"""内容安全：敏感词检测（生成前后）。"""
import os
import re
from functools import lru_cache


def _default_blocklist() -> list[str]:
    """内置最小拦截词表，可通过环境变量扩展。"""
    return [
        "制毒", "贩毒", "恐怖袭击", "自杀教程", "儿童色情",
        "赌博平台", "代开发票", "翻墙软件",
    ]


@lru_cache(maxsize=1)
def load_blocklist() -> tuple[str, ...]:
    words: list[str] = list(_default_blocklist())
    extra = os.getenv("CONTENT_BLOCKLIST", "")
    if extra:
        words.extend(w.strip() for w in extra.split(",") if w.strip())
    path = os.getenv("CONTENT_BLOCKLIST_FILE", "")
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    words.append(line)
    # 去重、按长度降序（优先匹配长词）
    unique = sorted({w.lower() for w in words if w}, key=len, reverse=True)
    return tuple(unique)


def check_text(text: str | None) -> dict:
    """检测文本是否命中敏感词。返回 {ok, hits}。"""
    if not text or not str(text).strip():
        return {"ok": True, "hits": []}
    lowered = str(text).lower()
    hits = [w for w in load_blocklist() if w in lowered]
    return {"ok": len(hits) == 0, "hits": hits}


def check_many(*texts: str | None) -> dict:
    all_hits: list[str] = []
    for t in texts:
        r = check_text(t)
        all_hits.extend(r["hits"])
    unique = list(dict.fromkeys(all_hits))
    return {"ok": len(unique) == 0, "hits": unique}


def moderation_detail(hits: list[str]) -> str:
    shown = ", ".join(hits[:3])
    if len(hits) > 3:
        shown += "…"
    return f"内容包含不当用语：{shown}"
