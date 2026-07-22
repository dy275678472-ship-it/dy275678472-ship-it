"""公开案例质量过滤：排除测试/占位标题，避免污染 SEO 与案例区。"""

import re

_TEST_PATTERN = re.compile(
    r"测试|test|demo|样例|占位|未命名|untitled|xxx|aaa",
    re.IGNORECASE,
)


def is_public_case_title(title: str | None) -> bool:
    t = (title or "").strip()
    if len(t) < 4:
        return False
    if _TEST_PATTERN.search(t):
        return False
    return True


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
