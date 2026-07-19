#!/bin/bash
set -euo pipefail

KEY="${SSH_KEY:-/workspace/.ssh-keys/shanghai-a/shanghai_a_deploy}"
HOST="ubuntu@150.158.42.39"
REMOTE="/var/www/yixing"
LOCAL="/workspace/esnlink-deploy/site"
ROOT="/workspace/esnlink-deploy"

echo "==> Deploying esnlink.cn..."

# Generate assets + unify chrome
python3 "$ROOT/generate_logos.py" 2>/dev/null || true
python3 "$ROOT/generate_og_image.py" 2>/dev/null || true
python3 "$ROOT/generate_webp.py" 2>/dev/null || true
python3 "$ROOT/generate_solutions.py" 2>/dev/null || true
python3 "$ROOT/apply_p1_patches.py" 2>/dev/null || true
python3 "$ROOT/unify_chrome.py"

# Prepare remote dirs
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" \
    "mkdir -p /tmp/esnlink-deploy/{docs,solutions,cases,en,landing,blog,assets,css}"

# Core pages (include pricing/about/faq for nav consistency)
scp -i "$KEY" -o StrictHostKeyChecking=no \
    "$LOCAL/index.html" "$LOCAL/call-center.html" "$LOCAL/booking.html" \
    "$LOCAL/sms.html" "$LOCAL/iot.html" "$LOCAL/edu.html" \
    "$LOCAL/pricing.html" "$LOCAL/about.html" "$LOCAL/faq.html" \
    "$LOCAL/robots.txt" "$LOCAL/sitemap.xml" \
    "$LOCAL/og-image.png" "$LOCAL/og-image.webp" 2>/dev/null \
    "$HOST:/tmp/esnlink-deploy/" || \
scp -i "$KEY" -o StrictHostKeyChecking=no \
    "$LOCAL/index.html" "$LOCAL/call-center.html" "$LOCAL/booking.html" \
    "$LOCAL/sms.html" "$LOCAL/iot.html" "$LOCAL/edu.html" \
    "$LOCAL/pricing.html" "$LOCAL/about.html" "$LOCAL/faq.html" \
    "$LOCAL/robots.txt" "$LOCAL/sitemap.xml" "$LOCAL/og-image.png" \
    "$HOST:/tmp/esnlink-deploy/"

# Subdirectories
for dir in docs solutions cases en landing blog assets css; do
    if [ -d "$LOCAL/$dir" ] && [ "$(ls -A "$LOCAL/$dir" 2>/dev/null)" ]; then
        scp -i "$KEY" -o StrictHostKeyChecking=no -r "$LOCAL/$dir" "$HOST:/tmp/esnlink-deploy/"
    fi
done

# CSS fallback from repo root
scp -i "$KEY" -o StrictHostKeyChecking=no "$ROOT/css/header-footer.css" "$HOST:/tmp/header-footer.css" 2>/dev/null || true

# Nginx performance snippet
scp -i "$KEY" -o StrictHostKeyChecking=no "$ROOT/nginx/esnlink-performance.conf" "$HOST:/tmp/esnlink-performance.conf"
scp -i "$KEY" -o StrictHostKeyChecking=no "$ROOT/nginx/apply_nginx.sh" "$HOST:/tmp/apply_nginx.sh"

# Move to production
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" "
    sudo mv /tmp/esnlink-deploy/index.html /tmp/esnlink-deploy/call-center.html \
        /tmp/esnlink-deploy/booking.html /tmp/esnlink-deploy/sms.html \
        /tmp/esnlink-deploy/iot.html /tmp/esnlink-deploy/edu.html \
        /tmp/esnlink-deploy/pricing.html /tmp/esnlink-deploy/about.html \
        /tmp/esnlink-deploy/faq.html \
        /tmp/esnlink-deploy/robots.txt /tmp/esnlink-deploy/sitemap.xml \
        /tmp/esnlink-deploy/og-image.png $REMOTE/ 2>/dev/null || true
    [ -f /tmp/esnlink-deploy/og-image.webp ] && sudo mv /tmp/esnlink-deploy/og-image.webp $REMOTE/
    for d in docs solutions cases en landing blog assets css; do
        sudo mkdir -p $REMOTE/\$d
        sudo cp -r /tmp/esnlink-deploy/\$d/* $REMOTE/\$d/ 2>/dev/null || true
    done
    [ -f /tmp/header-footer.css ] && sudo mv /tmp/header-footer.css $REMOTE/css/header-footer.css
    sudo chown -R www-data:www-data $REMOTE
    chmod +x /tmp/apply_nginx.sh && sudo bash /tmp/apply_nginx.sh
"

echo "==> Deploy complete. Verifying..."
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" "
    python3 - <<'PY'
import urllib.request, re
pages=['/','/sms.html','/pricing.html','/iot.html','/about.html','/en/','/cases/']
for p in pages:
    t=urllib.request.urlopen('http://127.0.0.1'+p).read().decode('utf-8','ignore')
    m=re.search(r'<nav class=\"navbar\"[\\s\\S]*?</nav>', t)
    links=re.findall(r'href=\"([^\"]+)\"', m.group(0)) if m else []
    print(p, 'OK' if '智能外呼' in (m.group(0) if m else '') or 'AI Calling' in (m.group(0) if m else '') else 'BAD', links[:8])
PY
"
