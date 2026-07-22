#!/usr/bin/env python3
"""Output SQL to set preview_body for showcase cases (utf8mb4-safe escaping).

Auto-discovers `seed_data/showcase_excerpts/*.txt` → content_id = stem.
"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EXCERPT_DIR = SCRIPT_DIR / "seed_data" / "showcase_excerpts"


def sql_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "''")


def main() -> None:
    files = sorted(EXCERPT_DIR.glob("showcase_*.txt"))
    if not files:
        raise SystemExit(f"no excerpt files in {EXCERPT_DIR}")

    print("SET NAMES utf8mb4;")
    for path in files:
        content_id = path.stem
        body = path.read_text(encoding="utf-8").strip()
        if len(body) < 2000:
            raise SystemExit(f"excerpt too short (<2000): {path.name} len={len(body)}")
        escaped = sql_escape(body)
        print(
            f"UPDATE contents SET preview_body='{escaped}' "
            f"WHERE content_id='{content_id}';"
        )
    print(
        "SELECT content_id, "
        "CHAR_LENGTH(preview_body) AS preview_chars, "
        "preview_body IS NOT NULL AS has_body "
        "FROM contents WHERE content_id LIKE 'showcase_%' ORDER BY content_id;"
    )


if __name__ == "__main__":
    main()
