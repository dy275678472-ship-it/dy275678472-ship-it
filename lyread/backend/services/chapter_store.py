"""章节独立表读写：与 stories.chapters JSON 双向同步。"""

import json
from typing import List, Optional


def parse_chapters_json(chapters_raw: Optional[str]) -> list:
    if not chapters_raw:
        return []
    try:
        data = json.loads(chapters_raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def chapters_to_json(chapters: List[dict]) -> str:
    return json.dumps(chapters, ensure_ascii=False)


def sync_chapters_table(cursor, story_id: int, user_id: str, chapters: list) -> int:
    """将章节列表写入 chapters 表，返回总字数。"""
    cursor.execute("DELETE FROM chapters WHERE story_id=%s", (story_id,))
    total = 0
    for i, ch in enumerate(chapters, 1):
        if not isinstance(ch, dict):
            continue
        idx = int(ch.get("chapter") or ch.get("idx") or i)
        title = ch.get("title") or f"第{idx}章"
        content = ch.get("content") or ch.get("summary") or ""
        wc = len(content)
        total += wc
        cursor.execute(
            "INSERT INTO chapters (story_id, user_id, idx, title, content, word_count, status) "
            "VALUES (%s,%s,%s,%s,%s,%s,'draft')",
            (story_id, user_id, idx, title, content, wc),
        )
    return total


def load_chapters_from_table(cursor, story_id: int) -> list:
    cursor.execute(
        "SELECT idx, title, content, word_count FROM chapters WHERE story_id=%s ORDER BY idx",
        (story_id,),
    )
    rows = cursor.fetchall()
    if not rows:
        return []
    result = []
    for r in rows:
        if isinstance(r, dict):
            result.append({
                "chapter": r["idx"], "idx": r["idx"], "title": r["title"],
                "content": r.get("content") or "", "word_count": r.get("word_count") or 0,
            })
        else:
            result.append({"chapter": r[0], "idx": r[0], "title": r[1], "content": r[2] or "", "word_count": r[3] or 0})
    return result


def merge_chapters_for_story(cursor, story_id: int, chapters_json: Optional[str]) -> list:
    """优先读 chapters 表；表空则回退 JSON。"""
    from_table = load_chapters_from_table(cursor, story_id)
    if from_table:
        return from_table
    return parse_chapters_json(chapters_json)
