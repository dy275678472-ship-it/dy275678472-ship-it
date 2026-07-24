"""审核通过时将作品章节同步到 contents 公开案例。"""

from services.chapter_store import merge_chapters_for_story

PREVIEW_MAX_CHARS = 8000


def build_preview_body(chapters: list) -> str:
    """合并章节正文，首章完整 + 后续截断，供案例页与 SEO 展示。"""
    if not chapters:
        return ""
    parts = []
    total = 0
    for i, ch in enumerate(chapters):
        if not isinstance(ch, dict):
            continue
        title = ch.get("title") or f"第{ch.get('chapter') or ch.get('idx') or i + 1}章"
        content = (ch.get("content") or "").strip()
        if not content:
            continue
        block = f"{title}\n\n{content}"
        if i == 0:
            parts.append(block)
            total += len(block)
        else:
            remain = PREVIEW_MAX_CHARS - total
            if remain <= 0:
                break
            parts.append(block[:remain])
            total += min(len(block), remain)
        if total >= PREVIEW_MAX_CHARS:
            break
    body = "\n\n".join(parts)
    if len(body) > PREVIEW_MAX_CHARS:
        body = body[:PREVIEW_MAX_CHARS] + "\n\n…（节选）"
    return body


def sync_story_to_contents(cursor, story_id: int) -> dict:
    """从 stories + chapters 同步元数据与 preview_body 到 contents。"""
    cursor.execute(
        "SELECT id, title, genre, intro, outline, chapters, word_count FROM stories WHERE id=%s LIMIT 1",
        (story_id,),
    )
    story = cursor.fetchone()
    if not story:
        return {"synced": False, "reason": "story_not_found"}

    chapters = merge_chapters_for_story(cursor, story_id, story.get("chapters"))
    preview = build_preview_body(chapters)
    word_count = story.get("word_count") or sum(len((c.get("content") or "")) for c in chapters if isinstance(c, dict))
    if not word_count and preview:
        word_count = len(preview)

    cid = f"story_{story_id}"
    cursor.execute(
        "INSERT INTO contents (content_id, story_id, title, category, word_count, preview_body, heat, score, status) "
        "VALUES (%s,%s,%s,%s,%s,%s,0,0,'active') "
        "ON DUPLICATE KEY UPDATE "
        "story_id=VALUES(story_id), title=VALUES(title), category=VALUES(category), "
        "word_count=VALUES(word_count), preview_body=VALUES(preview_body), status='active'",
        (cid, story_id, story["title"], story.get("genre") or "都市", word_count, preview or None),
    )
    return {"synced": True, "content_id": cid, "preview_chars": len(preview or ""), "word_count": word_count}
