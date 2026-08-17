"""公开案例质量过滤：排除测试/占位标题，避免污染 SEO 与案例区。"""

import re

_TEST_PATTERN = re.compile(
    r"测试|test|demo|样例|占位|未命名|untitled|xxx|aaa",
    re.IGNORECASE,
)

# 旧 seed 尾声堆字：跨案重复「故事，仍在前方」垫行（读感差；seed 入库前先读时剥离）
_PAD_TAIL_LINE_RE = re.compile(
    r"^(故事，?\s*仍在前方。?|故事仍在前方。?)\s*$"
)
_EXCERPT_END_RE = re.compile(r"^（节选完[^）]*）\s*$")


def is_public_case_title(title: str | None) -> bool:
    t = (title or "").strip()
    if len(t) < 4:
        return False
    if _TEST_PATTERN.search(t):
        return False
    return True


def clean_preview_body(text: str | None) -> str:
    """公开节选清洗：去提示块 + 剥离尾声堆字垫行，保留真实正文。"""
    if not text:
        return ""
    out = str(text)
    if "【阅读提示】" in out:
        out = out.split("【阅读提示】")[0]
    if "【节选说明】" in out:
        out = out.split("【节选说明】")[0]
    lines = out.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    while lines:
        stripped = lines[-1].strip()
        if not stripped or _EXCERPT_END_RE.match(stripped) or _PAD_TAIL_LINE_RE.match(stripped):
            lines.pop()
            continue
        break
    return "\n".join(lines).strip()


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
