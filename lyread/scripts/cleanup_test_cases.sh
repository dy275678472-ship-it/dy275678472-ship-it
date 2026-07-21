#!/usr/bin/env bash
# 归档测试/占位案例（部署后执行）
set -euo pipefail

CONTAINER="${MYSQL_CONTAINER:-lyread-mysql}"
DB="${MYSQL_DATABASE:-lyread}"

ROOT_PW=$(docker exec "$CONTAINER" printenv MYSQL_ROOT_PASSWORD)

docker exec -i "$CONTAINER" mysql --default-character-set=utf8mb4 -uroot -p"$ROOT_PW" "$DB" <<'EOSQL'
UPDATE contents SET status='archived' WHERE status='active' AND (
  title LIKE '%测试%' OR LOWER(title) LIKE '%test%' OR LOWER(title) LIKE '%demo%'
  OR title LIKE '%未命名%' OR CHAR_LENGTH(TRIM(title)) < 4
);
SELECT ROW_COUNT() AS archived_rows;
EOSQL

echo "[cleanup] archived test/placeholder cases (status=archived)"
