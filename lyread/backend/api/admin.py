"""运营后台 API — 用户/作品/订单/任务/审核/额度调整。"""

from typing import Optional

import mysql.connector
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.admin_auth import get_admin_user
from settings import database_config

router = APIRouter()


def _db():
    try:
        return mysql.connector.connect(**database_config())
    except Exception as exc:
        raise HTTPException(status_code=503, detail="数据库暂时不可用") from exc


@router.get("/stats")
def admin_stats(_: dict = Depends(get_admin_user)):
    conn = _db()
    try:
        c = conn.cursor(dictionary=True)
        stats = {}
        for sql, key in [
            ("SELECT COUNT(*) AS n FROM users", "users"),
            ("SELECT COUNT(*) AS n FROM stories", "stories"),
            ("SELECT COUNT(*) AS n FROM orders WHERE status='paid'", "paid_orders"),
            ("SELECT COALESCE(SUM(paid_balance+free_balance),0) AS n FROM credit_accounts", "total_credits"),
            ("SELECT COUNT(*) AS n FROM generation_jobs WHERE status='running'", "running_jobs"),
            ("SELECT COUNT(*) AS n FROM content_reviews WHERE result='pending'", "pending_reviews"),
        ]:
            try:
                c.execute(sql)
                stats[key] = int((c.fetchone() or {}).get("n") or 0)
            except Exception:
                stats[key] = 0
        return {"success": True, "stats": stats}
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/users")
def list_users(limit: int = 50, offset: int = 0, _: dict = Depends(get_admin_user)):
    conn = _db()
    try:
        c = conn.cursor(dictionary=True)
        lim, off = max(1, min(limit, 100)), max(0, offset)
        c.execute(
            "SELECT u.id, u.username, u.email, u.role, u.vip_level, u.created_at, "
            "COALESCE(a.free_balance,0) AS free_balance, COALESCE(a.paid_balance,0) AS paid_balance "
            "FROM users u LEFT JOIN credit_accounts a ON a.user_id=u.id "
            "ORDER BY u.created_at DESC LIMIT %s OFFSET %s",
            (lim, off),
        )
        rows = c.fetchall()
        return {"success": True, "users": [{**r, "created_at": str(r.get("created_at") or "")} for r in rows]}
    finally:
        if conn.is_connected():
            conn.close()


class CreditAdjustRequest(BaseModel):
    points: int = Field(..., ge=-100000, le=100000)
    note: str = Field(default="管理员调整", max_length=200)
    target: str = Field(default="paid", pattern="^(free|paid)$")


@router.post("/users/{user_id}/credits")
def adjust_credits(user_id: str, req: CreditAdjustRequest, admin: dict = Depends(get_admin_user)):
    conn = _db()
    try:
        conn.start_transaction()
        c = conn.cursor(dictionary=True)
        c.execute("INSERT IGNORE INTO credit_accounts (user_id) VALUES (%s)", (user_id,))
        c.execute(
            "SELECT free_balance, paid_balance FROM credit_accounts WHERE user_id=%s FOR UPDATE", (user_id,)
        )
        acc = c.fetchone() or {"free_balance": 0, "paid_balance": 0}
        free, paid = int(acc["free_balance"]), int(acc["paid_balance"])
        if req.target == "free":
            free = max(0, free + req.points)
            free_delta, paid_delta = req.points, 0
        else:
            paid = max(0, paid + req.points)
            free_delta, paid_delta = 0, req.points
        c.execute(
            "UPDATE credit_accounts SET free_balance=%s, paid_balance=%s WHERE user_id=%s",
            (free, paid, user_id),
        )
        bal = free + paid
        c.execute(
            "INSERT INTO credit_transactions (user_id, type, amount, free_delta, paid_delta, balance_after, ref_type, note) "
            "VALUES (%s,'admin_adjust',%s,%s,%s,%s,'admin',%s)",
            (user_id, req.points, free_delta, paid_delta, bal, req.note),
        )
        conn.commit()
        return {"success": True, "balance": {"free": free, "paid": paid, "total": bal}}
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail="调整失败") from exc
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/stories")
def list_all_stories(limit: int = 50, _: dict = Depends(get_admin_user)):
    conn = _db()
    try:
        c = conn.cursor(dictionary=True)
        c.execute(
            "SELECT id, user_id, title, genre, status, word_count, created_at, updated_at "
            "FROM stories ORDER BY updated_at DESC LIMIT %s",
            (max(1, min(limit, 100)),),
        )
        rows = c.fetchall()
        return {"success": True, "stories": rows}
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/orders")
def list_orders(limit: int = 50, _: dict = Depends(get_admin_user)):
    conn = _db()
    try:
        c = conn.cursor(dictionary=True)
        c.execute(
            "SELECT out_trade_no, user_id, points, amount_fen, status, trade_no, created_at, paid_at "
            "FROM orders ORDER BY id DESC LIMIT %s",
            (max(1, min(limit, 100)),),
        )
        return {"success": True, "orders": c.fetchall()}
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/jobs")
def list_jobs(status: Optional[str] = None, limit: int = 50, _: dict = Depends(get_admin_user)):
    conn = _db()
    try:
        c = conn.cursor(dictionary=True)
        lim = max(1, min(limit, 100))
        if status:
            c.execute(
                "SELECT id, user_id, story_id, job_type, reserved_credits, actual_credits, status, created_at, finished_at "
                "FROM generation_jobs WHERE status=%s ORDER BY id DESC LIMIT %s",
                (status, lim),
            )
        else:
            c.execute(
                "SELECT id, user_id, story_id, job_type, reserved_credits, actual_credits, status, created_at, finished_at "
                "FROM generation_jobs ORDER BY id DESC LIMIT %s",
                (lim,),
            )
        return {"success": True, "jobs": c.fetchall()}
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/reviews")
def list_reviews(result: str = "pending", limit: int = 50, _: dict = Depends(get_admin_user)):
    conn = _db()
    try:
        c = conn.cursor(dictionary=True)
        c.execute(
            "SELECT id, target_type, target_id, user_id, title, result, reason, reviewer, created_at, reviewed_at "
            "FROM content_reviews WHERE result=%s ORDER BY id DESC LIMIT %s",
            (result, max(1, min(limit, 100))),
        )
        return {"success": True, "reviews": c.fetchall()}
    finally:
        if conn.is_connected():
            conn.close()


class ReviewAction(BaseModel):
    reason: Optional[str] = None


@router.post("/reviews/{review_id}/approve")
def approve_review(review_id: int, admin: dict = Depends(get_admin_user)):
    conn = _db()
    try:
        conn.start_transaction()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM content_reviews WHERE id=%s FOR UPDATE", (review_id,))
        rev = c.fetchone()
        if not rev:
            raise HTTPException(status_code=404, detail="审核记录不存在")
        if rev["result"] != "pending":
            conn.commit()
            return {"success": True, "message": "已处理"}
        reviewer = admin.get("username") or str(admin["sub"])
        c.execute(
            "UPDATE content_reviews SET result='approved', reviewer=%s, reviewed_at=NOW() WHERE id=%s",
            (reviewer, review_id),
        )
        if rev["target_type"] == "story":
            c.execute("UPDATE stories SET status='published' WHERE id=%s", (rev["target_id"],))
            c.execute("SELECT title, genre, word_count FROM stories WHERE id=%s", (rev["target_id"],))
            story = c.fetchone()
            if story:
                cid = f"story_{rev['target_id']}"
                c.execute(
                    "INSERT INTO contents (content_id, title, category, word_count, heat, score, status) "
                    "VALUES (%s,%s,%s,%s,0,0,'active') "
                    "ON DUPLICATE KEY UPDATE title=VALUES(title), status='active'",
                    (cid, story["title"], story.get("genre") or "都市", story.get("word_count") or 0),
                )
        conn.commit()
        return {"success": True, "message": "已通过并发布"}
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail="审核失败") from exc
    finally:
        if conn.is_connected():
            conn.close()


@router.post("/reviews/{review_id}/reject")
def reject_review(review_id: int, req: ReviewAction, admin: dict = Depends(get_admin_user)):
    conn = _db()
    try:
        c = conn.cursor()
        reviewer = admin.get("username") or str(admin["sub"])
        c.execute(
            "UPDATE content_reviews SET result='rejected', reason=%s, reviewer=%s, reviewed_at=NOW() "
            "WHERE id=%s AND result='pending'",
            (req.reason or "不符合发布规范", reviewer, review_id),
        )
        conn.commit()
        return {"success": True, "message": "已驳回"}
    finally:
        if conn.is_connected():
            conn.close()
