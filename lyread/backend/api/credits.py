"""点数账户与计费服务。

设计要点：
- 余额分两部分：free_balance（每日免费额度，不累计）与 paid_balance（充值/赠送）。
- 生成任务走「预冻结 reserve → 成功结算 settle / 失败返还 refund」。
- 所有变更写不可变流水 credit_transactions；账户行用 SELECT ... FOR UPDATE 加锁，保证并发安全。
"""

import os
import mysql.connector
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.auth import get_current_user
from settings import database_config

router = APIRouter()

SIGNUP_BONUS = 30
DAILY_FREE = 5

# 各生成任务的点数价目（V2 首版）
PRICES = {
    "title": 1,
    "outline": 3,
    "chapters": 5,
    "chapter": 10,
    "continue": 10,
    "consistency": 2,
}


def _db():
    try:
        return mysql.connector.connect(**database_config())
    except Exception as exc:
        print(f"[Credits] DB 连接失败: {exc}")
        raise HTTPException(status_code=503, detail="数据库暂时不可用")


def estimate_points(job_type: str) -> int:
    return PRICES.get(job_type, 1)


def _ensure_account(cursor, uid: str):
    cursor.execute("INSERT IGNORE INTO credit_accounts (user_id) VALUES (%s)", (uid,))


def _fetch_account(cursor, uid: str) -> dict:
    cursor.execute(
        "SELECT free_balance, paid_balance, reserved FROM credit_accounts WHERE user_id=%s FOR UPDATE",
        (uid,),
    )
    row = cursor.fetchone()
    if not row:
        return {"free_balance": 0, "paid_balance": 0, "reserved": 0}
    if isinstance(row, dict):
        return row
    return {"free_balance": row[0], "paid_balance": row[1], "reserved": row[2]}


def _write_txn(cursor, uid, ttype, amount, free_delta, paid_delta, balance_after, ref_type=None, ref_id=None, note=None):
    cursor.execute(
        "INSERT INTO credit_transactions (user_id, type, amount, free_delta, paid_delta, balance_after, ref_type, ref_id, note) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (uid, ttype, amount, free_delta, paid_delta, balance_after, ref_type, ref_id, note),
    )


def grant_signup_bonus(conn, uid: str) -> None:
    """注册赠送点数（幂等：已有 signup_bonus 流水则跳过）。conn 由调用方管理事务。"""
    cursor = conn.cursor(dictionary=True)
    _ensure_account(cursor, uid)
    cursor.execute(
        "SELECT id FROM credit_transactions WHERE user_id=%s AND type='signup_bonus' LIMIT 1", (uid,)
    )
    if cursor.fetchone():
        return
    acc = _fetch_account(cursor, uid)
    new_paid = acc["paid_balance"] + SIGNUP_BONUS
    cursor.execute("UPDATE credit_accounts SET paid_balance=%s WHERE user_id=%s", (new_paid, uid))
    _write_txn(cursor, uid, "signup_bonus", SIGNUP_BONUS, 0, SIGNUP_BONUS,
               new_paid + acc["free_balance"], note="注册赠送")


def get_balance(uid: str) -> dict:
    conn = _db()
    try:
        cursor = conn.cursor(dictionary=True)
        _ensure_account(cursor, uid)
        conn.commit()
        cursor.execute(
            "SELECT free_balance, paid_balance, reserved FROM credit_accounts WHERE user_id=%s", (uid,)
        )
        row = cursor.fetchone() or {"free_balance": 0, "paid_balance": 0, "reserved": 0}
        cursor.execute(
            "SELECT 1 AS ok FROM daily_free_grants WHERE user_id=%s AND grant_date=%s LIMIT 1",
            (uid, date.today()),
        )
        claimed_today = cursor.fetchone() is not None
        return {
            "free": int(row["free_balance"]),
            "paid": int(row["paid_balance"]),
            "reserved": int(row["reserved"]),
            "total": int(row["free_balance"]) + int(row["paid_balance"]),
            "claimed_today": claimed_today,
        }
    finally:
        if conn.is_connected():
            conn.close()


def reserve(uid: str, points: int, job_type: str, story_id=None) -> dict:
    """预冻结点数并创建 generation_job。返回 {job_id, reserved}。余额不足抛 402。"""
    conn = _db()
    try:
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()
        _ensure_account(cursor, uid)
        max_jobs = int(os.getenv("MAX_CONCURRENT_JOBS", "2"))
        cursor.execute(
            "SELECT COUNT(*) AS n FROM generation_jobs WHERE user_id=%s AND status='running'", (uid,)
        )
        if int((cursor.fetchone() or {}).get("n") or 0) >= max_jobs:
            conn.rollback()
            raise HTTPException(status_code=429, detail="同时进行的生成任务过多，请稍后再试")
        acc = _fetch_account(cursor, uid)
        total = acc["free_balance"] + acc["paid_balance"]
        if total < points:
            conn.rollback()
            raise HTTPException(status_code=402, detail="点数不足，请充值或领取每日免费额度")
        # 先扣免费额度，再扣充值额度
        from_free = min(acc["free_balance"], points)
        from_paid = points - from_free
        new_free = acc["free_balance"] - from_free
        new_paid = acc["paid_balance"] - from_paid
        new_reserved = acc["reserved"] + points
        cursor.execute(
            "UPDATE credit_accounts SET free_balance=%s, paid_balance=%s, reserved=%s WHERE user_id=%s",
            (new_free, new_paid, new_reserved, uid),
        )
        cursor.execute(
            "INSERT INTO generation_jobs (user_id, story_id, job_type, reserved_credits, reserved_free, reserved_paid, status) "
            "VALUES (%s,%s,%s,%s,%s,%s,'running')",
            (uid, story_id, job_type, points, from_free, from_paid),
        )
        job_id = cursor.lastrowid
        _write_txn(cursor, uid, "reserve", -points, -from_free, -from_paid,
                   new_free + new_paid, ref_type="job", ref_id=str(job_id), note=f"{job_type} 预冻结")
        conn.commit()
        return {"job_id": job_id, "reserved": points, "from_free": from_free, "from_paid": from_paid}
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        print(f"[Credits.reserve] {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="计费失败")
    finally:
        if conn.is_connected():
            conn.close()


def settle(uid: str, job_id: int, actual_points: int) -> None:
    """结算：实际消耗 actual_points（<=预冻结），差额退回 paid。"""
    conn = _db()
    try:
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()
        cursor.execute(
            "SELECT reserved_credits, status FROM generation_jobs WHERE id=%s AND user_id=%s FOR UPDATE",
            (job_id, uid),
        )
        job = cursor.fetchone()
        if not job or job["status"] != "running":
            conn.rollback()
            return
        reserved = int(job["reserved_credits"])
        actual = max(0, min(actual_points, reserved))
        refund = reserved - actual
        acc = _fetch_account(cursor, uid)
        new_reserved = max(0, acc["reserved"] - reserved)
        new_paid = acc["paid_balance"] + refund
        cursor.execute(
            "UPDATE credit_accounts SET reserved=%s, paid_balance=%s WHERE user_id=%s",
            (new_reserved, new_paid, uid),
        )
        cursor.execute(
            "UPDATE generation_jobs SET status='succeeded', actual_credits=%s, finished_at=NOW() WHERE id=%s",
            (actual, job_id),
        )
        _write_txn(cursor, uid, "settle", -actual, 0, refund,
                   acc["free_balance"] + new_paid, ref_type="job", ref_id=str(job_id),
                   note=f"结算(实扣{actual}/冻结{reserved})")
        conn.commit()
    except Exception as exc:
        conn.rollback()
        print(f"[Credits.settle] {type(exc).__name__}: {exc}")
    finally:
        if conn.is_connected():
            conn.close()


def refund(uid: str, job_id: int, error_code: str = "generation_failed") -> None:
    """失败全额返还，按原始 free/paid 拆分归还。"""
    conn = _db()
    try:
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()
        cursor.execute(
            "SELECT reserved_credits, reserved_free, reserved_paid, status FROM generation_jobs WHERE id=%s AND user_id=%s FOR UPDATE",
            (job_id, uid),
        )
        job = cursor.fetchone()
        if not job or job["status"] != "running":
            conn.rollback()
            return
        reserved = int(job["reserved_credits"])
        rfree = int(job["reserved_free"])
        rpaid = int(job["reserved_paid"])
        acc = _fetch_account(cursor, uid)
        new_reserved = max(0, acc["reserved"] - reserved)
        new_free = acc["free_balance"] + rfree
        new_paid = acc["paid_balance"] + rpaid
        cursor.execute(
            "UPDATE credit_accounts SET reserved=%s, free_balance=%s, paid_balance=%s WHERE user_id=%s",
            (new_reserved, new_free, new_paid, uid),
        )
        cursor.execute(
            "UPDATE generation_jobs SET status='refunded', actual_credits=0, error_code=%s, finished_at=NOW() WHERE id=%s",
            (error_code, job_id),
        )
        _write_txn(cursor, uid, "refund", reserved, rfree, rpaid,
                   new_free + new_paid, ref_type="job", ref_id=str(job_id), note="生成失败返还")
        conn.commit()
    except Exception as exc:
        conn.rollback()
        print(f"[Credits.refund] {type(exc).__name__}: {exc}")
    finally:
        if conn.is_connected():
            conn.close()


# ==================== API ====================

@router.get("/balance")
def balance(user: dict = Depends(get_current_user)):
    return {"success": True, **get_balance(str(user["sub"]))}


@router.get("/prices")
def prices():
    return {"success": True, "prices": PRICES, "signup_bonus": SIGNUP_BONUS, "daily_free": DAILY_FREE}


class EstimateRequest(BaseModel):
    job_type: str


@router.post("/estimate")
def estimate(req: EstimateRequest, user: dict = Depends(get_current_user)):
    pts = estimate_points(req.job_type)
    bal = get_balance(str(user["sub"]))
    return {"success": True, "job_type": req.job_type, "points": pts, "enough": bal["total"] >= pts, "balance": bal}


@router.post("/daily-claim")
def daily_claim(user: dict = Depends(get_current_user)):
    """领取当日免费额度（每天一次，不累计：直接把 free_balance 置为 DAILY_FREE）。"""
    uid = str(user["sub"])
    today = date.today()
    conn = _db()
    try:
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()
        _ensure_account(cursor, uid)
        cursor.execute(
            "SELECT points FROM daily_free_grants WHERE user_id=%s AND grant_date=%s", (uid, today)
        )
        if cursor.fetchone():
            conn.rollback()
            bal = get_balance(uid)
            return {"success": True, "claimed": False, "message": "今日已领取", "balance": bal}
        acc = _fetch_account(cursor, uid)
        cursor.execute("UPDATE credit_accounts SET free_balance=%s WHERE user_id=%s", (DAILY_FREE, uid))
        cursor.execute(
            "INSERT INTO daily_free_grants (user_id, grant_date, points) VALUES (%s,%s,%s)",
            (uid, today, DAILY_FREE),
        )
        _write_txn(cursor, uid, "daily_grant", DAILY_FREE, DAILY_FREE - acc["free_balance"], 0,
                   DAILY_FREE + acc["paid_balance"], note="每日免费额度")
        conn.commit()
        return {"success": True, "claimed": True, "message": f"已领取 {DAILY_FREE} 点", "balance": get_balance(uid)}
    except Exception as exc:
        conn.rollback()
        print(f"[Credits.daily_claim] {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="领取失败")
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/transactions")
def transactions(limit: int = 30, user: dict = Depends(get_current_user)):
    uid = str(user["sub"])
    conn = _db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT type, amount, balance_after, note, created_at FROM credit_transactions "
            "WHERE user_id=%s ORDER BY id DESC LIMIT %s",
            (uid, max(1, min(limit, 100))),
        )
        rows = cursor.fetchall()
        return {
            "success": True,
            "transactions": [
                {"type": r["type"], "amount": int(r["amount"]), "balance_after": int(r["balance_after"]),
                 "note": r["note"], "created_at": str(r["created_at"])}
                for r in rows
            ],
        }
    finally:
        if conn.is_connected():
            conn.close()
