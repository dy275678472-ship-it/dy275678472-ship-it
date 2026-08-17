"""公开案例质量过滤：排除测试/占位标题，避免污染 SEO 与案例区。"""

import re

_TEST_PATTERN = re.compile(
    r"测试|test|demo|样例|占位|未命名|untitled|xxx|aaa",
    re.IGNORECASE,
)

# 旧 seed 尾声堆字：跨案重复垫行（读感差；seed 入库前先读时剥离）
_PAD_TAIL_LINE_RE = re.compile(
    r"^(故事，?\s*仍在前方。?|故事仍在前方。?|风过处，故事暂歇，余韵仍在。?)\s*$"
)
_EXCERPT_END_RE = re.compile(r"^（节选完[^）]*）\s*$")


def is_public_case_title(title: str | None) -> bool:
    t = (title or "").strip()
    if len(t) < 4:
        return False
    if _TEST_PATTERN.search(t):
        return False
    return True


def _collapse_duplicate_paragraphs(text: str) -> str:
    """折叠垫文插入导致的连续重复段落，保留首次出现。"""
    parts = re.split(r"\n{2,}", text)
    out: list[str] = []
    prev = None
    for part in parts:
        norm = part.strip()
        if not norm:
            continue
        if norm == prev:
            continue
        out.append(norm)
        prev = norm
    return "\n\n".join(out)


def _shares_long_run(a: str, b: str, min_len: int = 20) -> bool:
    """两段是否共享 ≥min_len 的连续子串（用于近义/回声尾段）。

    阈值 20：覆盖 case84「苏灵儿擦净牌位…弟子等您，很久了。」(23 字) 一类回声，
    又高于常见短收束，降低误伤。
    """
    if len(a) < min_len or len(b) < min_len:
        return False
    # 用较短段扫子串，降低开销
    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    limit = len(shorter) - min_len
    for i in range(limit + 1):
        if shorter[i : i + min_len] in longer:
            return True
    return False


def _collapse_near_duplicate_trailing(text: str, min_len: int = 20) -> str:
    """从文末起丢弃与前段共享长连续子串的近义尾段，保留首次叙述。"""
    parts = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    if len(parts) < 2:
        return text
    while len(parts) >= 2:
        last = parts[-1]
        if any(_shares_long_run(last, prev, min_len) for prev in parts[:-1]):
            parts.pop()
            continue
        break
    return "\n\n".join(parts)


def clean_preview_body(text: str | None) -> str:
    """公开节选清洗：去提示块 + 剥离堆字垫行 + 折叠重复/近义尾段，保留真实正文。"""
    if not text:
        return ""
    out = str(text)
    if "【阅读提示】" in out:
        out = out.split("【阅读提示】")[0]
    if "【节选说明】" in out:
        out = out.split("【节选说明】")[0]
    lines = out.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    # 垫行可能夹在重复段中间，不只出现在文末
    lines = [ln for ln in lines if not _PAD_TAIL_LINE_RE.match(ln.strip())]
    while lines:
        stripped = lines[-1].strip()
        if not stripped or _EXCERPT_END_RE.match(stripped):
            lines.pop()
            continue
        break
    cleaned = "\n".join(lines).strip()
    cleaned = _collapse_duplicate_paragraphs(cleaned)
    return _collapse_near_duplicate_trailing(cleaned)

def public_case_sql_clause(alias: str = "") -> str:
    """返回可拼接到 WHERE 后的 SQL 片段（不含 leading AND）。"""
    prefix = f"{alias}." if alias else ""
    return (
        f"{prefix}status='active' "
        f"AND CHAR_LENGTH(TRIM({prefix}title)) >= 4 "
        f"AND {prefix}title NOT LIKE '%测试%' "
        f"AND LOWER({prefix}title) NOT LIKE '%test%' "
        f"AND LOWER({prefix}title) NOT LIKE '%demo%' "
        f"AND {prefix}title NOT LIKE '%未命名%'"
    )
