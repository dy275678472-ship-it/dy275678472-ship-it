#!/usr/bin/env bash
# 写入精选展示案例（通过 case_quality 过滤，供 /trending 与 /case/* 阅读区使用）
# 幂等：按 content_id 去重；每次运行会刷新 preview_body 节选正文
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER="${MYSQL_CONTAINER:-lyread-mysql}"
DB="${MYSQL_DATABASE:-lyread}"
ROOT_PW=$(docker exec "$CONTAINER" printenv MYSQL_ROOT_PASSWORD)

echo "[seed_showcase] generating excerpts from catalog..."
python3 "$SCRIPT_DIR/generate_showcase_excerpts.py"

SQL_BODY=$(python3 - "$SCRIPT_DIR/seed_data/showcase_catalog.json" <<'PY'
import json, sys
cases = json.load(open(sys.argv[1], encoding="utf-8"))
rows = []
for c in cases:
    title = c["title"].replace("'", "''")
    cat = c["category"].replace("'", "''")
    rows.append(
        f"  ('{c['content_id']}', '{title}', '{cat}', "
        f"{c['word_count']}, {c['heat']}, {c['score']}, 'active')"
    )
print("INSERT INTO contents (content_id, title, category, word_count, heat, score, status) VALUES")
print(",\n".join(rows))
print("""ON DUPLICATE KEY UPDATE
  title=VALUES(title),
  category=VALUES(category),
  word_count=VALUES(word_count),
  heat=VALUES(heat),
  score=VALUES(score),
  status='active';

SELECT COUNT(*) AS active_showcase FROM contents WHERE status='active';""")
PY
)

docker exec -i "$CONTAINER" mysql --default-character-set=utf8mb4 -uroot -p"$ROOT_PW" "$DB" <<<"$SQL_BODY"

python3 "$SCRIPT_DIR/seed_showcase_preview_sql.py" | docker exec -i "$CONTAINER" mysql --default-character-set=utf8mb4 -uroot -p"$ROOT_PW" "$DB"

CASE_COUNT=$(python3 -c "import json; print(len(json.load(open('$SCRIPT_DIR/seed_data/showcase_catalog.json'))))")
echo "[seed_showcase] showcase cases + reading excerpts ready ($CASE_COUNT cases)"
