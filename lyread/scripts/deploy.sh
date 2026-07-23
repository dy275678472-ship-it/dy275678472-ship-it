#!/usr/bin/env bash
# LyRead 一键部署（在服务器 ~/lyread-deploy 目录执行）
set -euo pipefail

BRANCH="${BRANCH:-cursor/lyread-c65f}"
REPO_DIR="${REPO_DIR:-$HOME/lyread-deploy}"
ENV_FILE="${ENV_FILE:-/tmp/lyread.env}"
NETWORK="${DOCKER_NETWORK:-lyread-net}"
BACKEND_PORT="${BACKEND_PORT:-8004}"
NGINX_CONF_SRC="${NGINX_CONF_SRC:-$REPO_DIR/lyread/nginx/lyread.cn.conf}"
NGINX_CONF_DST="${NGINX_CONF_DST:-/etc/nginx/conf.d/default.conf}"

cd "$REPO_DIR"
echo "=== git pull ($BRANCH) ==="
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull origin "$BRANCH"

echo "=== backend image ==="
TAG="lyread-backend:fix-$(date +%Y%m%d-%H%M%S)"
docker build -t "$TAG" lyread/backend

echo "=== restart backend ==="
docker stop lyread-backend-fix 2>/dev/null || true
docker rm lyread-backend-fix 2>/dev/null || true
docker run -d \
  --name lyread-backend-fix \
  --restart unless-stopped \
  --network "$NETWORK" \
  -p "127.0.0.1:${BACKEND_PORT}:8000" \
  --env-file "$ENV_FILE" \
  "$TAG"

for i in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:${BACKEND_PORT}/health/live" | grep -q ok; then
    echo "Backend healthy"
    break
  fi
  sleep 2
done

echo "=== archive test cases ==="
bash "$REPO_DIR/lyread/scripts/cleanup_test_cases.sh" || true

echo "=== seed showcase cases ==="
bash "$REPO_DIR/lyread/scripts/seed_showcase_cases.sh" || true

echo "=== frontend build ==="
cd lyread/frontend
if [ -f "${FRONTEND_ENV_FILE:-/tmp/lyread-frontend.env}" ]; then
  cp "${FRONTEND_ENV_FILE:-/tmp/lyread-frontend.env}" .env.production
  echo "Using frontend analytics env from ${FRONTEND_ENV_FILE:-/tmp/lyread-frontend.env}"
fi
npm install --silent
npm run build
sudo cp -r dist/* /usr/share/nginx/html/

if [ -f "$NGINX_CONF_SRC" ]; then
  echo "=== nginx config ==="
  sudo cp "$NGINX_CONF_SRC" "$NGINX_CONF_DST"
  sudo nginx -t
  sudo systemctl reload nginx
fi

echo "=== cron (backup + monitor) ==="
(crontab -l 2>/dev/null | grep -v 'lyread/scripts/backup_db' | grep -v 'lyread/scripts/monitor_health' || true
 echo "0 3 * * * $REPO_DIR/lyread/scripts/backup_db.sh >> /var/log/lyread_backup.log 2>&1"
 echo "*/15 * * * * $REPO_DIR/lyread/scripts/monitor_health.sh") | crontab -

echo "=== smoke ==="
BASE_URL=https://lyread.cn bash "$REPO_DIR/lyread/scripts/smoke_test.sh" || true

echo "=== seo push ==="
BASE_URL=https://lyread.cn bash "$REPO_DIR/lyread/scripts/seo_push.sh" || true

echo "=== done ==="
