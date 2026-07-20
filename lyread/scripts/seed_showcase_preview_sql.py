#!/usr/bin/env python3
"""Output SQL to set preview_body for showcase cases (utf8mb4-safe escaping)."""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EXCERPT_DIR = SCRIPT_DIR / "seed_data" / "showcase_excerpts"

CASES = [
    ("showcase_urban_01.txt", "showcase_urban_01"),
    ("showcase_warrior_01.txt", "showcase_warrior_01"),
    ("showcase_reborn_01.txt", "showcase_reborn_01"),
    ("showcase_xianxia_01.txt", "showcase_xianxia_01"),
    ("showcase_romance_01.txt", "showcase_romance_01"),
    ("showcase_scifi_01.txt", "showcase_scifi_01"),
    ("showcase_suspense_01.txt", "showcase_suspense_01"),
    ("showcase_history_01.txt", "showcase_history_01"),
    ("showcase_system_01.txt", "showcase_system_01"),
    ("showcase_apocalypse_01.txt", "showcase_apocalypse_01"),
    ("showcase_campus_01.txt", "showcase_campus_01"),
    ("showcase_game_01.txt", "showcase_game_01"),
]


def sql_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "''")


def main() -> None:
    print("SET NAMES utf8mb4;")
    for filename, content_id in CASES:
        path = EXCERPT_DIR / filename
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
