#!/bin/bash
set -euo pipefail
OPT="/opt/zongmao"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ">>> Deploy P0 patch files"
sudo cp "$SCRIPT_DIR/p0-patch.py" "$OPT/scripts/p0-patch.py" 2>/dev/null || {
  sudo mkdir -p "$OPT/scripts"
  sudo cp "$SCRIPT_DIR/p0-patch.py" "$OPT/scripts/p0-patch.py"
}

echo ">>> Run P0 patch"
sudo python3 "$OPT/scripts/p0-patch.py"

echo ">>> Test nginx"
sudo nginx -t

echo ">>> Reload services"
sudo systemctl reload nginx
sudo systemctl restart zongmao.service

echo ">>> Smoke tests"
curl -sf -o /dev/null -w "homepage: %{http_code}\n" https://zongmao.cn/
curl -sf -o /dev/null -w "pricing→premium: %{http_code}\n" -L https://zongmao.cn/pricing
curl -sfI -o /dev/null -w "HEAD homepage: %{http_code}\n" https://zongmao.cn/
curl -sf https://zongmao.cn/ | grep -c "kpi-total" && echo "KPI element found"
curl -sf https://zongmao.cn/ | grep -c 'kpi-total">-' && echo "WARNING: still has dash KPI" || echo "OK: no dash KPI"
curl -sf https://zongmao.cn/sitemap.xml | grep -c '<url>' | xargs -I{} echo "sitemap URLs: {}"

echo "✅ P0 deploy complete"
