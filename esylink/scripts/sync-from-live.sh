#!/usr/bin/env bash
# Pull latest static files from live esylink.cn into esylink/www/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$SCRIPT_DIR/../www"
TMP="/tmp/esylink-sync-$$"

mkdir -p "$DEST" "$TMP"
echo "==> Mirroring https://esylink.cn → $DEST"

wget -mk -np -nH --cut-dirs=0 -e robots=off \
  --reject-regex ".*\.(mp4|avi|mov)$" \
  -P "$TMP" https://esylink.cn/ 2>&1 | tail -5

# Merge: keep our optimized JS, update everything else
rsync -av --delete \
  --exclude 'js/' \
  "$TMP/" "$DEST/"

echo "==> Synced $(find "$DEST" -type f | wc -l) files (JS preserved from repo)"
rm -rf "$TMP"
