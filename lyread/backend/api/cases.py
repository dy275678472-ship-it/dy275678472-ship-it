"""平台案例阅读 API — 从 contents 表读取已发布内容。"""

import mysql.connector
from fastapi import APIRouter, HTTPException
from settings import database_config
from services.case_quality import public_case_sql_clause

router = APIRouter()


def _db():
    try:
        return mysql.connector.connect(**database_config())
    except Exception as exc:
        raise HTTPException(status_code=503, detail="数据库暂时不可用") from exc


@router.get("")
def list_cases(limit: int = 20, category: str = None):
    """公开案例列表（无需登录）。"""
    conn = _db()
    try:
        cursor = conn.cursor(dictionary=True)
        lim = max(1, min(limit, 50))
        if category:
            cursor.execute(
                f"SELECT id, content_id, title, category, word_count, heat, score, preview_body, created_at "
                f"FROM contents WHERE {public_case_sql_clause()} AND category=%s "
                f"ORDER BY heat DESC, id DESC LIMIT %s",
                (category, lim),
            )
        else:
            cursor.execute(
                f"SELECT id, content_id, title, category, word_count, heat, score, preview_body, created_at "
                f"FROM contents WHERE {public_case_sql_clause()} "
                f"ORDER BY heat DESC, id DESC LIMIT %s",
                (lim,),
            )
        rows = cursor.fetchall()
        return {
            "success": True,
            "cases": [
                {
                    "id": r["id"],
                    "content_id": r.get("content_id"),
                    "title": r.get("title") or "未命名",
                    "category": r.get("category") or "都市",
                    "word_count": int(r.get("word_count") or 0),
                    "heat": int(r.get("heat") or 0),
                    "score": float(r.get("score") or 0),
                    "url": f"/case/{r['id']}",
                    "excerpt": (r.get("preview_body") or "")[:200],
                    "has_body": bool(r.get("preview_body")),
                    "created_at": str(r.get("created_at") or ""),
                }
                for r in rows
            ],
            "total": len(rows),
        }
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/{case_id}")
def get_case(case_id: int):
    """案例详情（公开）。"""
    conn = _db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT id, content_id, title, category, word_count, heat, score, status, preview_body, created_at "
            f"FROM contents WHERE id=%s AND {public_case_sql_clause()} LIMIT 1",
            (case_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="案例不存在")
        preview = row.get("preview_body") or ""
        return {
            "success": True,
            "case": {
                **row,
                "preview_excerpt": preview[:1500] if preview else "",
                "has_body": bool(preview),
                "url": f"/ep/{row['id']}",
                "created_at": str(row.get("created_at") or ""),
            },
        }
    finally:
        if conn.is_connected():
            conn.close()
