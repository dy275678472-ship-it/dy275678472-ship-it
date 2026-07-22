"""创作者中心 API：等级 / 经验 / 资料。以登录用户为准，忽略前端传入的 user_id。"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

import mysql.connector

from api.auth import get_current_user
from settings import database_config

router = APIRouter()

# 等级阈值（经验值 -> 等级）
LEVELS = [0, 100, 300, 700, 1500, 3000, 6000, 12000]
TITLES = ["新手写手", "签约作者", "上架作者", "白银大神", "黄金大神", "白金大神", "殿堂大神", "至尊大神"]


def _db():
    try:
        return mysql.connector.connect(**database_config())
    except Exception:
        return None


def _level_for_xp(xp: int) -> dict:
    level = 1
    for i, threshold in enumerate(LEVELS):
        if xp >= threshold:
            level = i + 1
    level = min(level, len(TITLES))
    next_threshold = LEVELS[level] if level < len(LEVELS) else LEVELS[-1]
    return {
        "level": level,
        "title": TITLES[level - 1],
        "xp": xp,
        "next_level_xp": next_threshold,
    }


def _profile_from_db(uid: str) -> dict:
    """基于作品数据推导创作者画像，合并持久化资料。"""
    conn = _db()
    works, words, published = 0, 0, 0
    username = None
    nickname = None
    bio = None
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT COUNT(*) c, COALESCE(SUM(word_count),0) w, SUM(status='published') p "
                "FROM stories WHERE user_id=%s",
                (uid,),
            )
            row = cursor.fetchone() or {}
            works = int(row.get("c") or 0)
            words = int(row.get("w") or 0)
            published = int(row.get("p") or 0)
            cursor.execute("SELECT username FROM users WHERE id=%s LIMIT 1", (uid,))
            u = cursor.fetchone()
            username = u["username"] if u else None
            try:
                cursor.execute("SELECT nickname, bio FROM creator_profiles WHERE user_id=%s LIMIT 1", (uid,))
                prof = cursor.fetchone()
                if prof:
                    nickname = prof.get("nickname")
                    bio = prof.get("bio")
            except Exception:
                pass
        except Exception as exc:
            print(f"[Creator.profile] {type(exc).__name__}: {exc}")
        finally:
            if conn.is_connected():
                conn.close()
    # 经验：每千字 10 经验 + 每部发布 50 经验
    xp = (words // 1000) * 10 + published * 50
    info = _level_for_xp(xp)
    info.update({
        "user_id": uid,
        "username": username,
        "nickname": nickname or username,
        "bio": bio or "",
        "works": works,
        "words": words,
        "published": published,
    })
    return info


@router.get("/profile")
def get_profile(user: dict = Depends(get_current_user)):
    return {"success": True, "profile": _profile_from_db(str(user.get("sub", "0")))}


class XPRequest(BaseModel):
    amount: int = 10


@router.post("/gain_xp")
def gain_xp(req: XPRequest, user: dict = Depends(get_current_user)):
    # 经验按作品数据推导，这里仅回显最新画像
    return {"success": True, "profile": _profile_from_db(str(user.get("sub", "0")))}


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    bio: Optional[str] = None


@router.post("/update")
def update_profile(req: UpdateProfileRequest, user: dict = Depends(get_current_user)):
    uid = str(user.get("sub", "0"))
    conn = _db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO creator_profiles (user_id, nickname, bio) VALUES (%s,%s,%s) "
                "ON DUPLICATE KEY UPDATE nickname=VALUES(nickname), bio=VALUES(bio)",
                (uid, req.nickname or "", req.bio or ""),
            )
            conn.commit()
        except Exception as exc:
            print(f"[Creator.update] {exc}")
        finally:
            if conn.is_connected():
                conn.close()
    return {"success": True, "profile": _profile_from_db(uid)}
