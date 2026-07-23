#!/usr/bin/env bash
# 写入精选展示案例（通过 case_quality 过滤，供 /trending 与 /case/* 阅读区使用）
# 幂等：按 content_id 去重；每次运行会刷新 preview_body 节选正文
# 元数据来自 seed_data/showcase_catalog.json；正文来自已有 handcraft 节选文件（不自动覆盖）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER="${MYSQL_CONTAINER:-lyread-mysql}"
DB="${MYSQL_DATABASE:-lyread}"
CATALOG="$SCRIPT_DIR/seed_data/showcase_catalog.json"
ROOT_PW=$(docker exec "$CONTAINER" printenv MYSQL_ROOT_PASSWORD)

if [[ ! -f "$CATALOG" ]]; then
  echo "[seed_showcase] missing catalog: $CATALOG" >&2
  exit 1
fi

SQL_BODY=$(python3 - "$CATALOG" <<'PY'
import json, sys
cases = json.load(open(sys.argv[1], encoding="utf-8"))
rows = []
for c in cases:
    title = c["title"].replace("\\", "\\\\").replace("'", "''")
    cat = c["category"].replace("\\", "\\\\").replace("'", "''")
    rows.append(
        f"  ('{c['content_id']}', '{title}', '{cat}', "
        f"{int(c['word_count'])}, {int(c['heat'])}, {float(c['score'])}, 'active')"
    )
print("SET NAMES utf8mb4;")
print("INSERT INTO contents (content_id, title, category, word_count, heat, score, status) VALUES")
print(",\n".join(rows))
print("""ON DUPLICATE KEY UPDATE
  title=VALUES(title),
  category=VALUES(category),
  word_count=VALUES(word_count),
  heat=VALUES(heat),
  score=VALUES(score),
  status='active';

SELECT COUNT(*) AS active_showcase FROM contents WHERE content_id LIKE 'showcase_%' AND status='active';""")
PY
)

docker exec -i "$CONTAINER" mysql --default-character-set=utf8mb4 -uroot -p"$ROOT_PW" "$DB" <<<"$SQL_BODY"

python3 "$SCRIPT_DIR/seed_showcase_preview_sql.py" | docker exec -i "$CONTAINER" mysql --default-character-set=utf8mb4 -uroot -p"$ROOT_PW" "$DB"

CASE_COUNT=$(python3 -c "import json; print(len(json.load(open('$CATALOG', encoding='utf-8'))))")
echo "[seed_showcase] showcase cases + reading excerpts ready ($CASE_COUNT cases)"
