#!/usr/bin/env bash
# Deploy Esylink static assets to production server.
# Requires: SSH key at ~/.ssh/esylink_id, public key on server.
set -euo pipefail

HOST="${ESYLINK_HOST:-101.34.64.67}"
USER="${ESYLINK_USER:-ubuntu}"
KEY="${ESYLINK_SSH_KEY:-$HOME/.ssh/esylink_id}"
REMOTE_ROOT="${ESYLINK_REMOTE_ROOT:-/var/www/esylink}"
BRANCH="${ESYLINK_BRANCH:-cursor/esylink-optimize-7cb2}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOCAL_WWW="$REPO_ROOT/esylink/www"

SSH_OPTS=(-i "$KEY" -o StrictHostKeyChecking=accept-new -o BatchMode=yes)

echo "==> Esylink deploy → ${USER}@${HOST}:${REMOTE_ROOT}"

# 1. Sync JS assets (always safe to push)
echo "==> Syncing JS + manifest..."
rsync -avz -e "ssh ${SSH_OPTS[*]}" \
  "$LOCAL_WWW/js/" "${USER}@${HOST}:${REMOTE_ROOT}/js/"
rsync -avz -e "ssh ${SSH_OPTS[*]}" \
  "$LOCAL_WWW/manifest.json" "${USER}@${HOST}:${REMOTE_ROOT}/manifest.json"

# 2. Run optimize-pages on server (inject tracking scripts site-wide)
echo "==> Running optimize-pages on server..."
ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" bash -s <<REMOTE
set -euo pipefail
cd /tmp
if [ ! -d esylink-deploy ]; then
  git clone https://github.com/dy275678472-ship-it/dy275678472-ship-it.git esylink-deploy
fi
cd esylink-deploy
git fetch origin ${BRANCH}
git checkout ${BRANCH}
python3 esylink/scripts/optimize-pages.py ${REMOTE_ROOT}
REMOTE

# 3. Reload nginx
echo "==> Reloading nginx..."
ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" "sudo nginx -t && sudo systemctl reload nginx"

# 4. Smoke test
echo "==> Smoke test..."
curl -sf -o /dev/null -w "homepage: %{http_code}\n" https://esylink.cn/
curl -sf -o /dev/null -w "page-track.js: %{http_code}\n" https://esylink.cn/js/page-track.js
curl -sf -o /dev/null -w "chat.js: %{http_code}\n" https://esylink.cn/js/esylink-chat.js

echo "==> Deploy complete."
