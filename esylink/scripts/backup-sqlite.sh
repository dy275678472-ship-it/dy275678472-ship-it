#!/bin/bash
# SQLite 自动备份 — 每日凌晨 3:00
set -euo pipefail
BACKUP_DIR="/home/ubuntu/backups/sqlite"
DATE=$(date +%Y%m%d)
mkdir -p "$BACKUP_DIR"

DATABASES=(
  "/opt/kexun-token/token.db"
  "/opt/kexun-crm/crm.db"
  "/opt/kexun-token/analytics.db"
)

for db in "${DATABASES[@]}"; do
  if [ -f "$db" ]; then
    name=$(basename "$db" .db)
    sqlite3 "$db" ".backup '$BACKUP_DIR/${name}-${DATE}.db'"
    echo "$(date -Iseconds) backed up $db"
  fi
done

# Keep last 14 days
find "$BACKUP_DIR" -name "*.db" -mtime +14 -delete
echo "Backup complete: $BACKUP_DIR"
