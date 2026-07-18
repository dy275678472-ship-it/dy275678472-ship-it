#!/bin/bash
set -euo pipefail

KEY="${SSH_KEY:-/workspace/.ssh-keys/shanghai-a/shanghai_a_deploy}"
HOST="ubuntu@150.158.42.39"
REMOTE="/var/www/yixing"
LOCAL="/workspace/esnlink-deploy/site"
ROOT="/workspace/esnlink-deploy"

echo "==> Deploying esnlink.cn..."

# Generate assets if missing
if [ ! -f "$LOCAL/og-image.png" ]; then
    python3 "$ROOT/generate_og_image.py"
fi
python3 "$ROOT/generate_solutions.py" 2>/dev/null || true
python3 "$ROOT/apply_p1_patches.py" 2>/dev/null || true

# Prepare remote dirs
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" "mkdir -p /tmp/esnlink-deploy/docs /tmp/esnlink-deploy/solutions"

# Upload all site files
scp -i "$KEY" -o StrictHostKeyChecking=no \
    "$LOCAL/index.html" \
    "$LOCAL/call-center.html" \
    "$LOCAL/booking.html" \
    "$LOCAL/sms.html" \
    "$LOCAL/iot.html" \
    "$LOCAL/edu.html" \
    "$LOCAL/og-image.png" \
    "$LOCAL/sitemap.xml" \
    "$HOST:/tmp/esnlink-deploy/"

scp -i "$KEY" -o StrictHostKeyChecking=no \
    "$LOCAL/docs/"*.html \
    "$HOST:/tmp/esnlink-deploy/docs/"

scp -i "$KEY" -o StrictHostKeyChecking=no \
    "$LOCAL/solutions/"*.html \
    "$HOST:/tmp/esnlink-deploy/solutions/"

# Move to production
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" "
    sudo mv /tmp/esnlink-deploy/index.html /tmp/esnlink-deploy/call-center.html \
        /tmp/esnlink-deploy/booking.html /tmp/esnlink-deploy/sms.html \
        /tmp/esnlink-deploy/iot.html /tmp/esnlink-deploy/edu.html \
        /tmp/esnlink-deploy/og-image.png /tmp/esnlink-deploy/sitemap.xml $REMOTE/
    sudo mkdir -p $REMOTE/docs $REMOTE/solutions
    sudo mv /tmp/esnlink-deploy/docs/* $REMOTE/docs/
    sudo mv /tmp/esnlink-deploy/solutions/* $REMOTE/solutions/
    sudo chown -R www-data:www-data $REMOTE/index.html $REMOTE/call-center.html \
        $REMOTE/booking.html $REMOTE/sms.html $REMOTE/iot.html $REMOTE/edu.html \
        $REMOTE/og-image.png $REMOTE/sitemap.xml $REMOTE/docs $REMOTE/solutions
"

# Shared CSS
if [ -f "$ROOT/css/header-footer.css" ]; then
    scp -i "$KEY" -o StrictHostKeyChecking=no "$ROOT/css/header-footer.css" "$HOST:/tmp/header-footer.css"
    ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" \
        "sudo mv /tmp/header-footer.css $REMOTE/css/header-footer.css && sudo chown www-data:www-data $REMOTE/css/header-footer.css"
fi

echo "==> Deploy complete. Verifying..."
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" "
    curl -sI https://esnlink.cn/docs/sms-api.html | head -2
    curl -sI https://esnlink.cn/solutions/education.html | head -2
    curl -s https://esnlink.cn/booking.html | grep -o 'canonical.*esnlink' | head -1
"
