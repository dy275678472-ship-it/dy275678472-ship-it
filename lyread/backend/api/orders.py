"""充值订单与支付宝回调（验签骨架 + 沙箱模式）。"""

import os
import secrets
from datetime import datetime

import mysql.connector
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from api.auth import get_current_user
from settings import database_config

router = APIRouter()

PACKAGES = {
    "s": {"name": "体验包", "price_yuan": 10, "points": 100},
    "m": {"name": "创作包", "price_yuan": 30, "points": 350},
    "l": {"name": "连载包", "price_yuan": 98, "points": 1200},
}


def _db():
    try:
        return mysql.connector.connect(**database_config())
    except Exception as exc:
        raise HTTPException(status_code=503, detail="数据库暂时不可用") from exc


class CreateOrderRequest(BaseModel):
    package_id: str = Field(pattern="^(s|m|l)$")
    idempotency_key: str = Field(min_length=8, max_length=80)


def _credit_recharge(conn, uid: str, points: int, out_trade_no: str, trade_no: str):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id FROM credit_transactions WHERE user_id=%s AND ref_type='order' AND ref_id=%s LIMIT 1",
        (uid, out_trade_no),
    )
    if cursor.fetchone():
        return
    cursor.execute("INSERT IGNORE INTO credit_accounts (user_id) VALUES (%s)", (uid,))
    cursor.execute("SELECT paid_balance, free_balance FROM credit_accounts WHERE user_id=%s FOR UPDATE", (uid,))
    acc = cursor.fetchone() or {"paid_balance": 0, "free_balance": 0}
    new_paid = int(acc["paid_balance"]) + points
    cursor.execute("UPDATE credit_accounts SET paid_balance=%s WHERE user_id=%s", (new_paid, uid))
    bal_after = new_paid + int(acc["free_balance"])
    cursor.execute(
        "INSERT INTO credit_transactions (user_id, type, amount, free_delta, paid_delta, balance_after, ref_type, ref_id, note) "
        "VALUES (%s,'recharge',%s,0,%s,%s,'order',%s,%s)",
        (uid, points, points, bal_after, out_trade_no, f"充值到账 {points} 点"),
    )


@router.get("/packages")
def packages():
    return {"success": True, "packages": [{"id": k, **v} for k, v in PACKAGES.items()]}


@router.post("/create")
def create_order(req: CreateOrderRequest, user: dict = Depends(get_current_user)):
    uid = str(user["sub"])
    pkg = PACKAGES.get(req.package_id)
    if not pkg:
        raise HTTPException(status_code=422, detail="无效套餐")
    out_trade_no = f"LR{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{secrets.token_hex(4).upper()}"
    amount_fen = pkg["price_yuan"] * 100
    conn = _db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM orders WHERE idempotency_key=%s LIMIT 1", (req.idempotency_key,)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="重复下单，请刷新后重试")
        cursor.execute(
            "INSERT INTO orders (out_trade_no, user_id, points, amount_fen, channel, status, idempotency_key) "
            "VALUES (%s,%s,%s,%s,'alipay','created',%s)",
            (out_trade_no, uid, pkg["points"], amount_fen, req.idempotency_key),
        )
        conn.commit()
    finally:
        if conn.is_connected():
            conn.close()

    alipay_configured = bool(os.getenv("ALIPAY_APP_ID") and os.getenv("ALIPAY_PRIVATE_KEY"))
    pay_url = None
    if alipay_configured:
        try:
            from services.alipay import build_page_pay_url
            pay_url = build_page_pay_url(out_trade_no, str(pkg["price_yuan"]), f"LyRead {pkg['name']} {pkg['points']}点")
        except Exception as exc:
            print(f"[Orders] 支付宝下单失败: {exc}")

    return {
        "success": True,
        "out_trade_no": out_trade_no,
        "points": pkg["points"],
        "amount_yuan": pkg["price_yuan"],
        "amount_fen": amount_fen,
        "alipay_ready": alipay_configured,
        "pay_url": pay_url,
        "sandbox": os.getenv("ALIPAY_SANDBOX", "0") == "1",
        "message": "请跳转支付宝完成支付" if pay_url else "支付宝参数未配置时，可使用沙箱确认接口完成测试充值",
    }


@router.get("/{out_trade_no}")
def get_order(out_trade_no: str, user: dict = Depends(get_current_user)):
    uid = str(user["sub"])
    conn = _db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT out_trade_no, points, amount_fen, status, trade_no, created_at, paid_at "
            "FROM orders WHERE out_trade_no=%s AND user_id=%s LIMIT 1",
            (out_trade_no, uid),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="订单不存在")
        return {"success": True, "order": {**row, "created_at": str(row.get("created_at") or ""), "paid_at": str(row.get("paid_at") or "")}}
    finally:
        if conn.is_connected():
            conn.close()


@router.post("/sandbox/confirm/{out_trade_no}")
def sandbox_confirm(out_trade_no: str, user: dict = Depends(get_current_user)):
    """沙箱模式：模拟支付成功（仅 ALIPAY_SANDBOX=1 或开发环境）。"""
    if os.getenv("ALIPAY_SANDBOX", "0") != "1" and os.getenv("APP_ENV", "production") == "production":
        raise HTTPException(status_code=403, detail="沙箱确认仅在测试环境可用")
    uid = str(user["sub"])
    conn = _db()
    try:
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, points, amount_fen, status FROM orders WHERE out_trade_no=%s FOR UPDATE",
            (out_trade_no,),
        )
        order = cursor.fetchone()
        if not order or str(order["user_id"]) != uid:
            conn.rollback()
            raise HTTPException(status_code=404, detail="订单不存在")
        if order["status"] == "paid":
            conn.commit()
            return {"success": True, "message": "订单已支付", "status": "paid"}
        trade_no = f"SANDBOX{secrets.token_hex(8)}"
        cursor.execute(
            "UPDATE orders SET status='paid', trade_no=%s, paid_amount_fen=%s, paid_at=NOW() WHERE out_trade_no=%s",
            (trade_no, order["amount_fen"], out_trade_no),
        )
        _credit_recharge(conn, uid, int(order["points"]), out_trade_no, trade_no)
        conn.commit()
        return {"success": True, "message": f"沙箱充值成功 +{order['points']} 点", "status": "paid"}
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        print(f"[Orders.sandbox] {exc}")
        raise HTTPException(status_code=500, detail="沙箱确认失败")
    finally:
        if conn.is_connected():
            conn.close()


@router.post("/alipay/notify")
async def alipay_notify(request: Request):
    """支付宝异步回调 — 必须验签后入账（生产环境）。"""
    body = await request.form()
    params = dict(body)

    from services.alipay import verify_notify_params
    if not verify_notify_params(params):
        print("[Alipay notify] 验签失败")
        return "fail"

    out_trade_no = params.get("out_trade_no")
    trade_no = params.get("trade_no")
    total_amount = params.get("total_amount")
    trade_status = params.get("trade_status")
    if trade_status not in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        return "success"

    conn = _db()
    try:
        conn.start_transaction()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, points, amount_fen, status, trade_no FROM orders WHERE out_trade_no=%s FOR UPDATE",
            (out_trade_no,),
        )
        order = cursor.fetchone()
        if not order:
            conn.rollback()
            return "fail"
        if order["status"] == "paid":
            conn.commit()
            return "success"
        expected_yuan = order["amount_fen"] / 100
        if abs(float(total_amount or 0) - expected_yuan) > 0.01:
            conn.rollback()
            print(f"[Alipay] 金额不符 {total_amount} vs {expected_yuan}")
            return "fail"
        if order.get("trade_no") and order["trade_no"] != trade_no:
            conn.rollback()
            return "fail"
        cursor.execute(
            "UPDATE orders SET status='paid', trade_no=%s, paid_amount_fen=%s, paid_at=NOW() WHERE out_trade_no=%s",
            (trade_no, int(float(total_amount) * 100), out_trade_no),
        )
        _credit_recharge(conn, str(order["user_id"]), int(order["points"]), out_trade_no, trade_no)
        conn.commit()
        return "success"
    except Exception as exc:
        conn.rollback()
        print(f"[Alipay notify] {exc}")
        return "fail"
    finally:
        if conn.is_connected():
            conn.close()
