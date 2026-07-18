"""小说大脑：人物、设定、伏笔、摘要的加载与 LLM 更新。"""

import json
import re
from typing import List, Optional


def load_brain(cursor, story_id: int) -> dict:
    brain = {"summaries": [], "characters": [], "settings": [], "foreshadowings": []}
    try:
        cursor.execute(
            "SELECT chapter_idx, summary FROM chapter_summaries WHERE story_id=%s ORDER BY chapter_idx",
            (story_id,),
        )
        brain["summaries"] = [{"chapter_idx": r[0] if not isinstance(r, dict) else r["chapter_idx"],
                              "summary": r[1] if not isinstance(r, dict) else r["summary"]}
                             for r in cursor.fetchall()]
    except Exception:
        pass
    try:
        cursor.execute("SELECT id, name, profile FROM characters WHERE story_id=%s", (story_id,))
        for r in cursor.fetchall():
            brain["characters"].append({
                "id": r["id"] if isinstance(r, dict) else r[0],
                "name": r["name"] if isinstance(r, dict) else r[1],
                "profile": r["profile"] if isinstance(r, dict) else r[2],
            })
    except Exception:
        pass
    try:
        cursor.execute(
            "SELECT category, name, detail FROM world_settings WHERE story_id=%s", (story_id,)
        )
        for r in cursor.fetchall():
            brain["settings"].append({
                "category": r[0] if not isinstance(r, dict) else r["category"],
                "name": r[1] if not isinstance(r, dict) else r["name"],
                "detail": r[2] if not isinstance(r, dict) else r["detail"],
            })
    except Exception:
        pass
    try:
        cursor.execute(
            "SELECT id, content, planted_chapter, status FROM foreshadowings WHERE story_id=%s ORDER BY id",
            (story_id,),
        )
        for r in cursor.fetchall():
            if isinstance(r, dict):
                brain["foreshadowings"].append(r)
            else:
                brain["foreshadowings"].append({
                    "id": r[0], "content": r[1], "planted_chapter": r[2], "status": r[3],
                })
    except Exception:
        pass
    return brain


def build_memory_context(
    title: str, intro: str, outline: str, characters_text: str,
    chapters: list, brain: Optional[dict] = None, max_chars: int = 8000,
) -> str:
    parts = [f"书名：{title}"]
    if intro:
        parts.append(f"简介：{intro[:800]}")
    if outline:
        parts.append(f"大纲：{outline[:1500]}")

    if brain:
        if brain.get("characters"):
            lines = [f"- {c['name']}：{(c.get('profile') or '')[:200]}" for c in brain["characters"][:12]]
            parts.append("人物档案：\n" + "\n".join(lines))
        if brain.get("settings"):
            lines = [f"- [{s.get('category','设定')}] {s.get('name','')}：{(s.get('detail') or '')[:150]}" for s in brain["settings"][:10]]
            parts.append("世界设定：\n" + "\n".join(lines))
        open_fs = [f for f in brain.get("foreshadowings", []) if f.get("status") == "open"]
        if open_fs:
            parts.append("未回收伏笔：\n" + "\n".join(f"- 第{f.get('planted_chapter','?')}章埋：{f.get('content','')[:120]}" for f in open_fs[:8]))
        if brain.get("summaries"):
            parts.append("章节摘要：\n" + "\n".join(
                f"第{s['chapter_idx']}章：{s['summary']}" for s in brain["summaries"][-10:] if s.get("summary")
            ))
    elif characters_text:
        parts.append(f"人物设定：{characters_text[:1000]}")

    tail = ""
    for ch in chapters[-2:]:
        if isinstance(ch, dict):
            c = ch.get("content") or ""
            if c:
                tail += f"\n【{ch.get('title', '章节')}】\n{c[-2500:]}\n"
    if tail:
        parts.append("最近正文：" + tail[-max_chars:])
    return "\n\n".join(parts)[:max_chars]


def extract_summary_prompt(chapter_title: str, content: str) -> str:
    text = (content or "")[:3000]
    return f"""用80字内概括本章核心剧情与人物变化：
章节：{chapter_title}
{text}
只输出摘要。"""


def extract_brain_update_prompt(chapter_idx: int, content: str, existing_names: List[str]) -> str:
    names = "、".join(existing_names[:8]) if existing_names else "无"
    text = (content or "")[:3500]
    return f"""分析下面章节，提取小说记忆更新。已有角色：{names}

章节序号：{chapter_idx}
正文：
{text}

输出 JSON（不要其他文字）：
{{
  "summary": "本章80字摘要",
  "characters": [{{"name":"角色名","profile":"关系/状态/目标变化"}}],
  "foreshadowings_new": [{{"content":"新伏笔描述"}}],
  "foreshadowings_recovered": ["已回收的伏笔简述"],
  "settings": [{{"category":"势力/地点/规则","name":"名称","detail":"设定"}}]
}}"""


def apply_brain_update(cursor, story_id: int, chapter_idx: int, data: dict) -> None:
    summary = (data.get("summary") or "").strip()
    if summary:
        cursor.execute(
            "INSERT INTO chapter_summaries (story_id, chapter_idx, summary) VALUES (%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE summary=VALUES(summary)",
            (story_id, chapter_idx, summary[:500]),
        )
    for ch in data.get("characters") or []:
        name = (ch.get("name") or "").strip()
        if not name:
            continue
        profile = (ch.get("profile") or "").strip()
        cursor.execute("SELECT id FROM characters WHERE story_id=%s AND name=%s LIMIT 1", (story_id, name))
        row = cursor.fetchone()
        if row:
            cid = row[0] if not isinstance(row, dict) else row["id"]
            cursor.execute("UPDATE characters SET profile=%s WHERE id=%s", (profile[:2000], cid))
            cursor.execute(
                "INSERT INTO character_states (character_id, after_chapter, state) VALUES (%s,%s,%s)",
                (cid, chapter_idx, profile[:1000]),
            )
        else:
            cursor.execute(
                "INSERT INTO characters (story_id, name, profile) VALUES (%s,%s,%s)",
                (story_id, name, profile[:2000]),
            )
    for fs in data.get("foreshadowings_new") or []:
        content = (fs.get("content") or fs if isinstance(fs, str) else "").strip()
        if content:
            cursor.execute(
                "INSERT INTO foreshadowings (story_id, content, planted_chapter, status) VALUES (%s,%s,%s,'open')",
                (story_id, content[:500], chapter_idx),
            )
    for hint in data.get("foreshadowings_recovered") or []:
        hint = (hint or "").strip()
        if not hint:
            continue
        cursor.execute(
            "UPDATE foreshadowings SET status='recovered', recovered_chapter=%s "
            "WHERE story_id=%s AND status='open' AND content LIKE %s LIMIT 1",
            (chapter_idx, story_id, f"%{hint[:40]}%"),
        )
    for st in data.get("settings") or []:
        if st.get("name"):
            cursor.execute(
                "INSERT INTO world_settings (story_id, category, name, detail) VALUES (%s,%s,%s,%s)",
                (story_id, st.get("category"), st.get("name"), (st.get("detail") or "")[:1000]),
            )


def parse_brain_json(llm_output: str) -> dict:
    m = re.search(r"\{.*\}", llm_output, re.DOTALL)
    if not m:
        return {"summary": llm_output[:200]}
    try:
        return json.loads(m.group())
    except Exception:
        return {"summary": llm_output[:200]}
