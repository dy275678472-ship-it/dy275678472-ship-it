#!/bin/bash
set -euo pipefail

KEY="${SSH_KEY:-/workspace/.ssh-keys/shanghai-a/shanghai_a_deploy}"
HOST="ubuntu@150.158.42.39"
REMOTE="/var/www/yixing"
LOCAL="/workspace/esnlink-deploy/site"
ROOT="/workspace/esnlink-deploy"

echo "==> Deploying esnlink.cn..."

# Generate assets
python3 "$ROOT/generate_logos.py" 2>/dev/null || true
python3 "$ROOT/generate_og_image.py" 2>/dev/null || true
python3 "$ROOT/generate_webp.py" 2>/dev/null || true
python3 "$ROOT/generate_solutions.py" 2>/dev/null || true
python3 "$ROOT/apply_p1_patches.py" 2>/dev/null || true

# Prepare remote dirs
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" \
    "mkdir -p /tmp/esnlink-deploy/{docs,solutions,cases,en,landing}"

# Core pages
scp -i "$KEY" -o StrictHostKeyChecking=no \
    "$LOCAL/index.html" "$LOCAL/call-center.html" "$LOCAL/booking.html" \
    "$LOCAL/sms.html" "$LOCAL/iot.html" "$LOCAL/edu.html" \
    "$LOCAL/robots.txt" "$LOCAL/sitemap.xml" \
    "$LOCAL/og-image.png" "$LOCAL/og-image.webp" 2>/dev/null \
    "$HOST:/tmp/esnlink-deploy/" || \
scp -i "$KEY" -o StrictHostKeyChecking=no \
    "$LOCAL/index.html" "$LOCAL/call-center.html" "$LOCAL/booking.html" \
    "$LOCAL/sms.html" "$LOCAL/iot.html" "$LOCAL/edu.html" \
    "$LOCAL/robots.txt" "$LOCAL/sitemap.xml" "$LOCAL/og-image.png" \
    "$HOST:/tmp/esnlink-deploy/"

# Subdirectories
for dir in docs solutions cases en landing assets; do
    if [ -d "$LOCAL/$dir" ] && [ "$(ls -A "$LOCAL/$dir" 2>/dev/null)" ]; then
        scp -i "$KEY" -o StrictHostKeyChecking=no -r "$LOCAL/$dir" "$HOST:/tmp/esnlink-deploy/"
    fi
done

# CSS
scp -i "$KEY" -o StrictHostKeyChecking=no "$ROOT/css/header-footer.css" "$HOST:/tmp/header-footer.css" 2>/dev/null || true

# Nginx performance snippet
scp -i "$KEY" -o StrictHostKeyChecking=no "$ROOT/nginx/esnlink-performance.conf" "$HOST:/tmp/esnlink-performance.conf"
scp -i "$KEY" -o StrictHostKeyChecking=no "$ROOT/nginx/apply_nginx.sh" "$HOST:/tmp/apply_nginx.sh"

# Move to production
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" "
    sudo mv /tmp/esnlink-deploy/index.html /tmp/esnlink-deploy/call-center.html \
        /tmp/esnlink-deploy/booking.html /tmp/esnlink-deploy/sms.html \
        /tmp/esnlink-deploy/iot.html /tmp/esnlink-deploy/edu.html \
        /tmp/esnlink-deploy/robots.txt /tmp/esnlink-deploy/sitemap.xml \
        /tmp/esnlink-deploy/og-image.png $REMOTE/
    [ -f /tmp/esnlink-deploy/og-image.webp ] && sudo mv /tmp/esnlink-deploy/og-image.webp $REMOTE/
    for d in docs solutions cases en landing; do
        sudo mkdir -p $REMOTE/\$d
        sudo mv /tmp/esnlink-deploy/\$d/* $REMOTE/\$d/ 2>/dev/null || true
    done
    sudo mkdir -p $REMOTE/assets
    sudo cp -r /tmp/esnlink-deploy/assets/* $REMOTE/assets/ 2>/dev/null || true
    sudo mv /tmp/header-footer.css $REMOTE/css/header-footer.css 2>/dev/null || true
    sudo chown -R www-data:www-data $REMOTE/index.html $REMOTE/call-center.html \
        $REMOTE/booking.html $REMOTE/sms.html $REMOTE/iot.html $REMOTE/edu.html \
        $REMOTE/robots.txt $REMOTE/sitemap.xml $REMOTE/og-image.png $REMOTE/css \
        $REMOTE/docs $REMOTE/solutions $REMOTE/cases $REMOTE/en $REMOTE/landing $REMOTE/assets 2>/dev/null || true
    [ -f $REMOTE/og-image.webp ] && sudo chown www-data:www-data $REMOTE/og-image.webp
    chmod +x /tmp/apply_nginx.sh && sudo bash /tmp/apply_nginx.sh
"

echo "==> Deploy complete. Verifying..."
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" "
    echo 'robots.txt:' && curl -s https://esnlink.cn/robots.txt | grep -E 'Disallow|Sitemap'
    echo 'cases:' && curl -sI https://esnlink.cn/cases/ | head -2
    echo 'en:' && curl -sI https://esnlink.cn/en/ | head -2
    echo 'landing:' && curl -sI https://esnlink.cn/landing/sms.html | head -2
    echo 'seo noindex:' && curl -sI 'https://esnlink.cn/seo/cosgo/015c8c62.html' 2>/dev/null | grep -i robots || echo '(seo path may 404)'
"
