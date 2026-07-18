"""统计模块 API：作品数、字数、发布数、热度等（读数据库，登录后按用户过滤）。"""

from fastapi import APIRouter, Depends
from typing import Optional

import mysql.connector

from api.auth import get_optional_user
from settings import database_config
from services.case_quality import public_case_sql_clause

router = APIRouter()


def _db():
    try:
        return mysql.connector.connect(**database_config())
    except Exception:
        return None


@router.get("/overview")
def overview(user: Optional[dict] = Depends(get_optional_user)):
    """作者概览：作品数、总字数、已发布数、草稿数。"""
    data = {"totalWorks": 0, "totalWords": 0, "published": 0, "drafts": 0}
    conn = _db()
    if not conn:
        return {"success": True, **data}
    try:
        cursor = conn.cursor(dictionary=True)
        if user and user.get("sub"):
            uid = str(user["sub"])
            cursor.execute(
                "SELECT COUNT(*) c, COALESCE(SUM(word_count),0) w, "
                "SUM(status='published') p, SUM(status='draft') d "
                "FROM stories WHERE user_id=%s",
                (uid,),
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) c, COALESCE(SUM(word_count),0) w, "
                "SUM(status='published') p, SUM(status='draft') d FROM stories"
            )
        row = cursor.fetchone() or {}
        data = {
            "totalWorks": int(row.get("c") or 0),
            "totalWords": int(row.get("w") or 0),
            "published": int(row.get("p") or 0),
            "drafts": int(row.get("d") or 0),
        }
        return {"success": True, **data}
    except Exception as exc:
        print(f"[Stats.overview] {type(exc).__name__}: {exc}")
        return {"success": True, **data}
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/stories")
def stories_stats(user: Optional[dict] = Depends(get_optional_user)):
    """作品维度统计：按题材聚合。"""
    conn = _db()
    if not conn:
        return {"success": True, "by_genre": []}
    try:
        cursor = conn.cursor(dictionary=True)
        if user and user.get("sub"):
            cursor.execute(
                "SELECT COALESCE(genre,'未分类') genre, COUNT(*) c, COALESCE(SUM(word_count),0) w "
                "FROM stories WHERE user_id=%s GROUP BY genre ORDER BY c DESC",
                (str(user["sub"]),),
            )
        else:
            cursor.execute(
                "SELECT COALESCE(genre,'未分类') genre, COUNT(*) c, COALESCE(SUM(word_count),0) w "
                "FROM stories GROUP BY genre ORDER BY c DESC"
            )
        rows = cursor.fetchall()
        return {
            "success": True,
            "by_genre": [
                {"genre": r["genre"], "count": int(r["c"]), "words": int(r["w"])}
                for r in rows
            ],
        }
    except Exception as exc:
        print(f"[Stats.stories] {type(exc).__name__}: {exc}")
        return {"success": True, "by_genre": []}
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/earnings")
def earnings(user: Optional[dict] = Depends(get_optional_user)):
    """收益概览（当前无交易系统，返回占位结构，便于前端渲染）。"""
    return {"success": True, "total": 0.0, "month": 0.0, "currency": "CNY", "items": []}


@router.get("/public")
def public_stats():
    """首页公开展示数据（真实数据库统计，禁止夸大）。"""
    data = {
        "users": 0,
        "works": 0,
        "cases": 0,
        "total_words": 0,
    }
    conn = _db()
    if not conn:
        return {"success": True, **data}
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS c FROM users")
        data["users"] = int((cursor.fetchone() or {}).get("c") or 0)
        cursor.execute("SELECT COUNT(*) AS c, COALESCE(SUM(word_count),0) AS w FROM stories")
        row = cursor.fetchone() or {}
        data["works"] = int(row.get("c") or 0)
        data["total_words"] = int(row.get("w") or 0)
        cursor.execute(f"SELECT COUNT(*) AS c FROM contents WHERE {public_case_sql_clause()}")
        data["cases"] = int((cursor.fetchone() or {}).get("c") or 0)
        return {"success": True, **data}
    except Exception as exc:
        print(f"[Stats.public] {type(exc).__name__}: {exc}")
        return {"success": True, **data}
    finally:
        if conn.is_connected():
            conn.close()
