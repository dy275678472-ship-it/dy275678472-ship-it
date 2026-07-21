"""Admin auth: multi-token roles (admin / editor / ops)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from fastapi import HTTPException, Request

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "kdgc-admin-change-me")
EDITOR_TOKEN = os.getenv("EDITOR_TOKEN", "")
OPS_TOKEN = os.getenv("OPS_TOKEN", "")

# Optional CSV: role:token:name,role:token:name
# Example: admin:secret1:管理员,editor:secret2:编辑小王,ops:secret3:运营小李
ADMIN_USERS_RAW = os.getenv("ADMIN_USERS", "")

ROLE_PERMS = {
    "admin": {
        "content_read",
        "content_write",
        "content_delete",
        "leads_read",
        "leads_write",
        "leads_export",
        "chat_read",
        "chat_write",
        "tickets",
        "publish",
        "backup",
        "logs",
        "stats",
    },
    "editor": {
        "content_read",
        "content_write",
        "leads_read",
        "chat_read",
        "tickets",
        "publish",
        "stats",
    },
    "ops": {
        "leads_read",
        "leads_write",
        "leads_export",
        "chat_read",
        "chat_write",
        "tickets",
        "stats",
        "logs",
    },
}


@dataclass
class AdminPrincipal:
    name: str
    role: str
    token: str

    def can(self, perm: str) -> bool:
        return perm in ROLE_PERMS.get(self.role, set())


def _parse_users() -> dict[str, AdminPrincipal]:
    users: dict[str, AdminPrincipal] = {}
    if ADMIN_TOKEN:
        users[ADMIN_TOKEN] = AdminPrincipal(name="管理员", role="admin", token=ADMIN_TOKEN)
    if EDITOR_TOKEN:
        users[EDITOR_TOKEN] = AdminPrincipal(name="编辑", role="editor", token=EDITOR_TOKEN)
    if OPS_TOKEN:
        users[OPS_TOKEN] = AdminPrincipal(name="运营", role="ops", token=OPS_TOKEN)
    for part in ADMIN_USERS_RAW.split(","):
        part = part.strip()
        if not part:
            continue
        bits = part.split(":")
        if len(bits) < 2:
            continue
        if len(bits) == 2:
            role, token = bits[0].strip(), bits[1].strip()
            name = role
        else:
            role, token, name = bits[0].strip(), bits[1].strip(), bits[2].strip()
        if role not in ROLE_PERMS or not token:
            continue
        users[token] = AdminPrincipal(name=name or role, role=role, token=token)
    return users


USERS = _parse_users()


def resolve_admin(request: Request) -> AdminPrincipal:
    token = request.headers.get("X-Admin-Token") or ""
    user = USERS.get(token)
    if not user:
        raise HTTPException(401, "未授权：请提供正确的 Admin Token")
    return user


def require_perm(request: Request, perm: str) -> AdminPrincipal:
    user = resolve_admin(request)
    if not user.can(perm):
        raise HTTPException(403, f"权限不足：需要 {perm}（当前角色 {user.role}）")
    return user
