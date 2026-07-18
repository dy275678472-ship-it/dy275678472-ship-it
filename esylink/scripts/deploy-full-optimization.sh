#!/bin/bash
# Master deploy: run all esylink optimizations on production server
set -euo pipefail

OPT_DIR="/opt/esylink-optimize"
WEB="/var/www/esylink"

echo "=========================================="
echo " Esylink Full Optimization Deploy"
echo " $(date -Iseconds)"
echo "=========================================="

mkdir -p "$OPT_DIR"

# 1. Generate new pages (legal, trust, compliance, industry)
echo ">>> [1/12] Generating new pages..."
python3 "$OPT_DIR/generate-pages.py"

# 2. Font Awesome CDN → local
echo ">>> [2/12] Localizing Font Awesome..."
python3 "$OPT_DIR/localize-fontawesome.py"

# 3. Run full HTML optimization (canonical, noindex, compliance, blog CTA, etc.)
echo ">>> [3/12] Running full HTML optimization..."
python3 "$OPT_DIR/run-full-optimization.py"

# 4. Enhance product pages + calculator
echo ">>> [4/12] Enhancing product pages..."
python3 "$OPT_DIR/enhance-products.py"
python3 "$OPT_DIR/enhance-calculator.py"

# 5. P2 batch (noindex matrix, blog covers, whitepaper, compare)
echo ">>> [5/12] P2 batch optimizations..."
python3 "$OPT_DIR/p2-batch.py"

# 6. Final polish
echo ">>> [6/12] Final polish..."
python3 "$OPT_DIR/final-polish.py"

# 7. Patch backend (CRM sync + owner assign)
echo ">>> [7/12] Patching backend..."
python3 "$OPT_DIR/patch-backend.py"

# 8. Fix wechatsync bind to localhost
echo ">>> [8/12] Fixing wechatsync port bind..."
if grep -q "0.0.0.0', HTTP_PORT" /home/ubuntu/wechatsync/bridge_v2.py 2>/dev/null; then
  sed -i "s/'0.0.0.0', HTTP_PORT/'127.0.0.1', HTTP_PORT/" /home/ubuntu/wechatsync/bridge_v2.py
  echo "    bridge_v2.py patched to 127.0.0.1"
fi
# Restart wechatsync if still bound to 0.0.0.0
if ss -tlnp 2>/dev/null | grep -q "0.0.0.0:9528"; then
  pkill -f "bridge_v2.py" 2>/dev/null || true
  sleep 1
  cd /home/ubuntu/wechatsync && nohup python3 bridge_v2.py >> /home/ubuntu/wechatsync.log 2>&1 &
  echo "    wechatsync restarted on 127.0.0.1"
fi

# 9. Nginx additions (idempotent)
echo ">>> [9/12] Updating nginx config..."
NGINX_CONF="/etc/nginx/conf.d/esylink.conf"
for rule in \
  'location = /haoma.html { return 301 /pricing; }' \
  'location = /cs.html    { return 301 /cs/; }' \
  'location = /trust/       { try_files /trust/index.html =404; }' \
  'location = /compliance/  { try_files /compliance/index.html =404; }'
do
  if ! grep -qF "$(echo "$rule" | awk '{print $2}')" "$NGINX_CONF" 2>/dev/null; then
    # Insert before the closing brace of server block - use a marker
    echo "    $rule" | sudo tee -a /tmp/esylink-nginx-additions.txt > /dev/null
  fi
done
if [ -f /tmp/esylink-nginx-additions.txt ]; then
  # Insert before last closing brace of first server block
  sudo sed -i '/# esylink.cn/r /tmp/esylink-nginx-additions.txt' "$NGINX_CONF" 2>/dev/null || \
    cat /tmp/esylink-nginx-additions.txt | sudo tee -a "$NGINX_CONF" > /dev/null
  rm -f /tmp/esylink-nginx-additions.txt
fi
sudo nginx -t && sudo systemctl reload nginx

# 10. Setup cron jobs
echo ">>> [10/12] Setting up cron jobs..."
CRON_MARKER="# esylink-optimize"
(crontab -l 2>/dev/null | grep -v "$CRON_MARKER"; cat <<EOF
0 3 * * * bash $OPT_DIR/backup-sqlite.sh >> /home/ubuntu/backups/backup.log 2>&1 $CRON_MARKER
0 4 * * * cd $WEB/seo-engine && python3 generate.py --sitemap >> /home/ubuntu/sitemap-cron.log 2>&1 $CRON_MARKER
EOF
) | crontab -

# 11. Restart backend to pick up patches
echo ">>> [11/12] Restarting kexun-token service..."
sudo systemctl restart kexun-token.service 2>/dev/null || echo "    (manual restart may be needed)"

# 12. Health check
echo ">>> [12/12] Smoke test..."
curl -sf -o /dev/null -w "homepage: %{http_code}\n" https://esylink.cn/
curl -sf -o /dev/null -w "trust: %{http_code}\n" https://esylink.cn/trust/
curl -sf -o /dev/null -w "compliance: %{http_code}\n" https://esylink.cn/compliance/
curl -sf -o /dev/null -w "privacy: %{http_code}\n" https://esylink.cn/legal/privacy.html
curl -sf -o /dev/null -w "lead-form.js: %{http_code}\n" https://esylink.cn/js/esylink-lead-form.js
curl -sf -o /dev/null -w "whitepaper: %{http_code}\n" https://esylink.cn/resources/ai-outbound-guide.html
curl -sf -o /dev/null -w "fontawesome: %{http_code}\n" https://esylink.cn/css/fontawesome/all.min.css

echo ""
echo "=========================================="
echo " ✅ Full optimization deploy complete"
echo "=========================================="
