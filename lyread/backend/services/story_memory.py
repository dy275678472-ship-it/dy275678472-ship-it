"""小说大脑基础：章节摘要读写与续写上下文组装。"""

import json
from typing import List, Optional


def parse_chapters(chapters_raw: Optional[str]) -> list:
    if not chapters_raw:
        return []
    try:
        data = json.loads(chapters_raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def build_memory_context(
    title: str,
    intro: str,
    outline: str,
    characters: str,
    chapters: list,
    db_summaries: Optional[List[dict]] = None,
    max_chars: int = 6000,
) -> str:
    """组装续写用上下文：书名/简介/大纲/人物 + 最近章节摘要与正文尾部。"""
    parts = [f"书名：{title}"]
    if intro:
        parts.append(f"简介：{intro[:800]}")
    if outline:
        parts.append(f"大纲：{outline[:1500]}")
    if characters:
        parts.append(f"人物设定：{characters[:1000]}")

    if db_summaries:
        summ_lines = [f"第{s['chapter_idx']}章摘要：{s['summary']}" for s in db_summaries[-8:] if s.get("summary")]
        if summ_lines:
            parts.append("章节摘要记忆：\n" + "\n".join(summ_lines))

    # 最近 2 章正文尾部
    tail = ""
    for ch in chapters[-2:]:
        if isinstance(ch, dict):
            c = ch.get("content") or ch.get("summary") or ""
            if c:
                tail += f"\n【{ch.get('title', '章节')}】\n{c[-2000:]}\n"
    if tail:
        parts.append("最近章节正文：" + tail[-max_chars:])

    return "\n\n".join(parts)[:max_chars]


def extract_summary_prompt(chapter_title: str, content: str) -> str:
    text = (content or "")[:3000]
    return f"""请用 80 字以内概括下面章节的核心剧情、人物变化与未解伏笔，不要剧透后续：
章节：{chapter_title}
正文：
{text}

只输出摘要，不要其他内容。"""
