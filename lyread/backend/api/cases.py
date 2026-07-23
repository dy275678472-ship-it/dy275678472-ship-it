"""平台案例阅读 API — 从 contents 表读取已发布内容。"""

import re

import mysql.connector
from fastapi import APIRouter, HTTPException
from settings import database_config
from services.case_quality import public_case_sql_clause

router = APIRouter()

_CHAPTER_RE = re.compile(r"^第[一二三四五六七八九十百千0-9]+章", re.M)


def _clean_preview(text: str) -> str:
    if not text:
        return ""
    if "【阅读提示】" in text:
        text = text.split("【阅读提示】")[0]
    if "【节选说明】" in text:
        text = text.split("【节选说明】")[0]
    return text.strip()


def _excerpt_meta(text: str) -> dict:
    clean = _clean_preview(text)
    return {
        "excerpt_chars": len(clean),
        "excerpt_chapters": len(_CHAPTER_RE.findall(clean)),
    }


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
        lim = max(1, min(limit, 140))
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
        if category:
            cursor.execute(
                f"SELECT COUNT(*) AS c FROM contents WHERE {public_case_sql_clause()} AND category=%s",
                (category,),
            )
        else:
            cursor.execute(f"SELECT COUNT(*) AS c FROM contents WHERE {public_case_sql_clause()}")
        total = int((cursor.fetchone() or {}).get("c") or 0)
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
                    "excerpt": _clean_preview(r.get("preview_body") or "")[:120],
                    "has_body": bool(r.get("preview_body")),
                    "created_at": str(r.get("created_at") or ""),
                    **_excerpt_meta(r.get("preview_body") or ""),
                }
                for r in rows
            ],
            "total": total,
        }
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/categories/list")
def list_categories():
    """公开案例题材分类（供筛选）。"""
    conn = _db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT category, COUNT(*) AS count FROM contents WHERE {public_case_sql_clause()} "
            "GROUP BY category ORDER BY count DESC, category ASC"
        )
        rows = cursor.fetchall()
        return {
            "success": True,
            "categories": [
                {"name": r["category"] or "其他", "count": int(r["count"] or 0)}
                for r in rows
            ],
        }
    finally:
        if conn.is_connected():
            conn.close()


@router.get("/{case_id}/neighbors")
def case_neighbors(case_id: int):
    """同题材上下篇（按热度排序，与列表页一致）。"""
    conn = _db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT id, title, category, heat FROM contents "
            f"WHERE id=%s AND {public_case_sql_clause()} LIMIT 1",
            (case_id,),
        )
        cur = cursor.fetchone()
        if not cur:
            raise HTTPException(status_code=404, detail="案例不存在")
        cat = cur["category"] or "都市"
        heat = int(cur.get("heat") or 0)
        cid = int(cur["id"])

        cursor.execute(
            f"SELECT id, title FROM contents WHERE {public_case_sql_clause()} AND category=%s "
            f"AND (heat > %s OR (heat = %s AND id > %s)) "
            f"ORDER BY heat ASC, id ASC LIMIT 1",
            (cat, heat, heat, cid),
        )
        prev_row = cursor.fetchone()

        cursor.execute(
            f"SELECT id, title FROM contents WHERE {public_case_sql_clause()} AND category=%s "
            f"AND (heat < %s OR (heat = %s AND id < %s)) "
            f"ORDER BY heat DESC, id DESC LIMIT 1",
            (cat, heat, heat, cid),
        )
        next_row = cursor.fetchone()

        def _pack(row):
            if not row:
                return None
            return {"id": row["id"], "title": row.get("title") or "未命名", "url": f"/case/{row['id']}"}

        return {
            "success": True,
            "category": cat,
            "prev": _pack(prev_row),
            "next": _pack(next_row),
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
        preview = _clean_preview(row.get("preview_body") or "")
        meta = _excerpt_meta(preview)
        return {
            "success": True,
            "case": {
                **row,
                "preview_body": preview,
                "preview_excerpt": preview,
                "has_body": bool(preview),
                "url": f"/ep/{row['id']}",
                "created_at": str(row.get("created_at") or ""),
                **meta,
            },
        }
    finally:
        if conn.is_connected():
            conn.close()
