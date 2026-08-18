#!/usr/bin/env bash
# LyRead MySQL 每日备份（cron: 0 3 * * *）
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/home/ubuntu/backups}"
CONTAINER="${MYSQL_CONTAINER:-lyread-mysql}"
DB="${MYSQL_DATABASE:-lyread}"
RETAIN_DAYS="${RETAIN_DAYS:-14}"

mkdir -p "$BACKUP_DIR"
STAMP=$(date +%Y%m%d-%H%M%S)
OUT="$BACKUP_DIR/lyread-db-${STAMP}.sql"

ROOT_PW=$(docker exec "$CONTAINER" printenv MYSQL_ROOT_PASSWORD)
docker exec "$CONTAINER" mysqldump -uroot -p"$ROOT_PW" --single-transaction --routines "$DB" > "$OUT"
gzip -f "$OUT"
echo "[$(date)] backup ok: ${OUT}.gz"

find "$BACKUP_DIR" -name 'lyread-db-*.sql.gz' -mtime +"$RETAIN_DAYS" -delete 2>/dev/null || true
