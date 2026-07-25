"""LyRead 认证 API：bcrypt 密码、限时 JWT 和服务端鉴权。"""
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import mysql.connector
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field

from settings import database_config

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)
JWT_ALGORITHM = "HS256"


def get_db():
    try:
        return mysql.connector.connect(**database_config())
    except Exception:
        return None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, stored_hash: str) -> tuple[bool, bool]:
    """返回（是否匹配，是否为需要迁移的旧 SHA-256）。"""
    if stored_hash.startswith("$2"):
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")), False
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return secrets.compare_digest(legacy, stored_hash), True


def jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "")
    if len(secret) < 32:
        raise HTTPException(status_code=503, detail="认证服务未正确配置")
    return secret


def generate_token(user_id: str, username: str) -> str:
    now = datetime.now(timezone.utc)
    minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    return jwt.encode(
        {
            "sub": str(user_id), "username": username, "iat": now,
            "exp": now + timedelta(minutes=minutes), "jti": secrets.token_hex(16),
        },
        jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    try:
        payload = jwt.decode(credentials.credentials, jwt_secret(), algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已失效")
    if not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效登录凭证")
    return payload


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Optional[dict]:
    """宽松鉴权：有有效令牌时返回用户，否则返回 None（用于免费试用等公开接口）。"""
    if not credentials or credentials.scheme.lower() != "bearer":
        return None
    try:
        payload = jwt.decode(credentials.credentials, jwt_secret(), algorithms=[JWT_ALGORITHM])
    except (JWTError, HTTPException):
        return None
    if not payload.get("sub"):
        return None
    return payload


def _generate_user_id(cursor) -> str:
    """生成 12 位数字用户 ID，兼容 users.id varchar(12) 且避免碰撞。"""
    for _ in range(6):
        uid = str(secrets.randbelow(900_000_000_000) + 100_000_000_000)  # 恒为 12 位
        cursor.execute("SELECT 1 FROM users WHERE id = %s LIMIT 1", (uid,))
        if not cursor.fetchone():
            return uid
    raise HTTPException(status_code=500, detail="生成用户ID失败，请重试")


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[\w.@+-]+$")
    # 登录兼容旧系统曾允许的较短密码；成功后会迁移旧哈希。
    password: str = Field(min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[\w.@+-]+$")
    password: str = Field(min_length=8, max_length=128)
    email: Optional[EmailStr] = None


@router.post("/login")
async def login(req: LoginRequest):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=503, detail="服务暂时不可用")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, email, password_hash, vip_level, balance, role, created_at "
            "FROM users WHERE username = %s LIMIT 1",
            (req.username,),
        )
        user = cursor.fetchone()
        matched, legacy = verify_password(req.password, user["password_hash"]) if user else (False, False)
        if not matched:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        if legacy:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (hash_password(req.password), user["id"]),
            )
            conn.commit()
        return {
            "token": generate_token(user["id"], user["username"]),
            "token_type": "bearer",
            "user": {
                "id": user["id"], "username": user["username"], "email": user["email"],
                "vip_level": user["vip_level"], "balance": float(user["balance"]),
                "created_at": str(user["created_at"]),
                "role": user.get("role") or "user",
            },
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="登录失败")
    finally:
        if conn.is_connected():
            conn.close()


@router.post("/register", status_code=201)
async def register(req: RegisterRequest):
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=503, detail="服务暂时不可用")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username = %s LIMIT 1", (req.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="用户名已存在")
        user_id = _generate_user_id(cursor)
        cursor.execute(
            "INSERT INTO users (id, username, password_hash, email) VALUES (%s, %s, %s, %s)",
            (user_id, req.username, hash_password(req.password), str(req.email) if req.email else None),
        )
        conn.commit()
        # 注册赠送点数（失败不影响注册主流程）
        try:
            from api.credits import grant_signup_bonus
            grant_signup_bonus(conn, user_id)
            conn.commit()
        except Exception as bonus_exc:
            print(f"[Register] 赠送点数失败: {bonus_exc}")
        return {
            "success": True,
            "message": "注册成功",
            "token": generate_token(user_id, req.username),
            "token_type": "bearer",
            "user": {"id": user_id, "username": req.username, "email": str(req.email) if req.email else None, "vip_level": 0, "balance": 0.0},
        }
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        print(f"[Register] 失败: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="注册失败")
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    conn = get_db()
    role = "user"
    if conn:
        try:
            c = conn.cursor(dictionary=True)
            c.execute("SELECT role, username, email, vip_level FROM users WHERE id=%s LIMIT 1", (user["sub"],))
            row = c.fetchone()
            if row:
                role = row.get("role") or "user"
                return {"id": user["sub"], "username": row.get("username") or user.get("username"),
                        "email": row.get("email"), "vip_level": row.get("vip_level"), "role": role}
        finally:
            if conn.is_connected():
                conn.close()
    return {"id": user["sub"], "username": user.get("username"), "role": role}


class ForgotPasswordRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    password: str = Field(min_length=8, max_length=128)


@router.post("/forgot")
async def forgot_password(req: ForgotPasswordRequest):
    """申请重置密码（验证用户名+邮箱匹配）。

    delivery 字段供前端诚实展示（不泄露账号是否存在）：
    - opaque: 账号/邮箱未匹配（通用话术）
    - email: 已发邮件
    - inline: SMTP 未就绪且 EXPOSE_RESET_TOKEN=1，令牌随响应返回
    - unavailable: SMTP 未就绪且不允许回显令牌（避免假称「已发邮件」）
    """
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=503, detail="服务暂时不可用")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, email FROM users WHERE username=%s LIMIT 1", (req.username,)
        )
        user = cursor.fetchone()
        if not user or not user.get("email") or str(user["email"]).lower() != str(req.email).lower():
            return {
                "success": True,
                "delivery": "opaque",
                "message": "若账号与邮箱匹配，将按可用方式发送重置指引",
            }
        token = secrets.token_urlsafe(32)
        from datetime import datetime, timedelta
        expires = datetime.utcnow() + timedelta(hours=1)
        cursor.execute(
            "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (%s,%s,%s)",
            (user["id"], token, expires),
        )
        conn.commit()
        reset_path = f"/login?reset={token}"
        from services.email import send_password_reset_email, smtp_configured
        if smtp_configured():
            try:
                send_password_reset_email(str(req.email), reset_path, token)
                return {
                    "success": True,
                    "delivery": "email",
                    "message": "重置链接已发送至您的邮箱",
                }
            except Exception as mail_exc:
                print(f"[Forgot] 邮件发送失败: {mail_exc}")
        expose = os.getenv("EXPOSE_RESET_TOKEN", "0") == "1"
        if expose:
            return {
                "success": True,
                "delivery": "inline",
                "message": "邮件服务未配置：请在本页直接设置新密码（令牌已填入）",
                "reset_path": reset_path,
                "token": token,
            }
        # 生产常见：SMTP 未配且不允许回显 → 不可再假称「已发邮件」
        return {
            "success": True,
            "delivery": "unavailable",
            "message": "邮件服务暂未开通，暂时无法发送重置邮件。可注册新账号继续创作（点数独立），或联系客服协助找回。",
        }
    finally:
        if conn.is_connected():
            conn.close()


@router.post("/reset")
async def reset_password(req: ResetPasswordRequest):
    """使用令牌重置密码。"""
    conn = get_db()
    if not conn:
        raise HTTPException(status_code=503, detail="服务暂时不可用")
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, expires_at, used_at FROM password_reset_tokens WHERE token=%s LIMIT 1",
            (req.token,),
        )
        row = cursor.fetchone()
        if not row or row.get("used_at"):
            raise HTTPException(status_code=400, detail="无效或已使用的重置链接")
        from datetime import datetime
        if row["expires_at"] < datetime.utcnow():
            raise HTTPException(status_code=400, detail="重置链接已过期")
        cursor.execute(
            "UPDATE users SET password_hash=%s WHERE id=%s",
            (hash_password(req.password), row["user_id"]),
        )
        cursor.execute("UPDATE password_reset_tokens SET used_at=NOW() WHERE token=%s", (req.token,))
        conn.commit()
        return {"success": True, "message": "密码已重置，请登录"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="重置失败")
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/oauth/status")
async def oauth_status():
    """第三方登录可用状态（前端据此展示按钮）。"""
    return {
        "success": True,
        "wechat": bool(os.getenv("WECHAT_APP_ID")),
        "qq": bool(os.getenv("QQ_APP_ID")),
    }


@router.get("/wechat/login")
async def wechat_login():
    """微信 OAuth 登录入口（需配置 WECHAT_APP_ID）。"""
    app_id = os.getenv("WECHAT_APP_ID", "")
    if not app_id:
        raise HTTPException(
            status_code=503,
            detail="微信登录即将上线，请先使用邮箱注册/登录",
        )
    site = os.getenv("SITE_URL", "https://lyread.cn").rstrip("/")
    redirect_uri = os.getenv("WECHAT_REDIRECT_URI", f"{site}/api/auth/wechat/callback")
    from urllib.parse import quote
    from fastapi.responses import RedirectResponse
    url = (
        "https://open.weixin.qq.com/connect/qrconnect"
        f"?appid={app_id}&redirect_uri={quote(redirect_uri, safe='')}"
        "&response_type=code&scope=snsapi_login&state=lyread#wechat_redirect"
    )
    return RedirectResponse(url)
