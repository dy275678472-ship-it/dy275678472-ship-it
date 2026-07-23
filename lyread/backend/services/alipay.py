"""支付宝 RSA2 签名与下单（正式环境需配置密钥）。"""

import base64
import os
import urllib.parse
from datetime import datetime

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def _load_private_key():
    raw = os.getenv("ALIPAY_PRIVATE_KEY", "")
    if not raw:
        return None
    if "BEGIN" not in raw:
        raw = f"-----BEGIN RSA PRIVATE KEY-----\n{raw}\n-----END RSA PRIVATE KEY-----"
    return serialization.load_pem_private_key(raw.encode(), password=None)


def _load_public_key():
    raw = os.getenv("ALIPAY_PUBLIC_KEY", "")
    if not raw:
        return None
    if "BEGIN" not in raw:
        raw = f"-----BEGIN PUBLIC KEY-----\n{raw}\n-----END PUBLIC KEY-----"
    return serialization.load_pem_public_key(raw.encode())


def is_configured() -> bool:
    return bool(os.getenv("ALIPAY_APP_ID") and _load_private_key())


def sign_string(content: str) -> str:
    key = _load_private_key()
    if not key:
        raise ValueError("ALIPAY_PRIVATE_KEY 未配置")
    sig = key.sign(content.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
    return base64.b64encode(sig).decode()


def verify_string(content: str, signature_b64: str) -> bool:
    key = _load_public_key()
    if not key:
        return False
    try:
        key.verify(
            base64.b64decode(signature_b64),
            content.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


def build_page_pay_url(out_trade_no: str, amount_yuan: str, subject: str) -> str:
    """电脑网站支付 — 返回跳转 URL。"""
    app_id = os.getenv("ALIPAY_APP_ID")
    if not app_id:
        raise ValueError("ALIPAY_APP_ID 未配置")
    gateway = (
        "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
        if os.getenv("ALIPAY_SANDBOX", "0") == "1"
        else "https://openapi.alipay.com/gateway.do"
    )
    notify_url = os.getenv("ALIPAY_NOTIFY_URL", "https://lyread.cn/api/orders/alipay/notify")
    return_url = os.getenv("ALIPAY_RETURN_URL", "https://lyread.cn/wallet")
    biz = {
        "out_trade_no": out_trade_no,
        "product_code": "FAST_INSTANT_TRADE_PAY",
        "total_amount": amount_yuan,
        "subject": subject[:128],
    }
    import json
    params = {
        "app_id": app_id,
        "method": "alipay.trade.page.pay",
        "format": "JSON",
        "charset": "utf-8",
        "sign_type": "RSA2",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0",
        "notify_url": notify_url,
        "return_url": return_url,
        "biz_content": json.dumps(biz, ensure_ascii=False),
    }
    unsigned = "&".join(f"{k}={params[k]}" for k in sorted(params))
    params["sign"] = sign_string(unsigned)
    return gateway + "?" + urllib.parse.urlencode(params)

def verify_notify_params(params: dict) -> bool:
    """验证支付宝异步通知签名。"""
    sign = params.get("sign")
    if not sign:
        return False
    filtered = {k: v for k, v in params.items() if k not in ("sign", "sign_type") and v}
    content = "&".join(f"{k}={filtered[k]}" for k in sorted(filtered))
    return verify_string(content, sign)
