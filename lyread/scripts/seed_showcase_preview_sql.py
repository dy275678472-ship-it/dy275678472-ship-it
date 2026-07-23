#!/usr/bin/env python3
"""Output SQL to set preview_body for showcase cases (utf8mb4-safe escaping)."""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CATALOG = SCRIPT_DIR / "seed_data" / "showcase_catalog.json"
EXCERPT_DIR = SCRIPT_DIR / "seed_data" / "showcase_excerpts"


def sql_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "''")


def main() -> None:
    cases = json.loads(CATALOG.read_text(encoding="utf-8"))
    print("SET NAMES utf8mb4;")
    for case in cases:
        content_id = case["content_id"]
        path = EXCERPT_DIR / f"{content_id}.txt"
        if not path.is_file():
            raise SystemExit(f"missing excerpt file: {path}")
        body = path.read_text(encoding="utf-8").strip()
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
