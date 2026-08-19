"""管理员鉴权：users.role=admin 或 ADMIN_USERNAMES 环境变量白名单。"""

import os
from typing import Optional

import mysql.connector
from fastapi import Depends, HTTPException

from api.auth import get_current_user
from settings import database_config


def _fetch_role(user_id: str) -> str:
    try:
        conn = mysql.connector.connect(**database_config())
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT role, username FROM users WHERE id=%s LIMIT 1", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return "user"
        if row.get("role") == "admin":
            return "admin"
        admins = {u.strip() for u in os.getenv("ADMIN_USERNAMES", "").split(",") if u.strip()}
        if row.get("username") in admins:
            return "admin"
        return row.get("role") or "user"
    except Exception:
        return "user"


def get_admin_user(user: dict = Depends(get_current_user)) -> dict:
    uid = str(user["sub"])
    role = _fetch_role(uid)
    if role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return {**user, "role": "admin"}
