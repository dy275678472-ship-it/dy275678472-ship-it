#!/bin/bash
set -euo pipefail

KEY="${SSH_KEY:-/workspace/.ssh-keys/shanghai-a/shanghai_a_deploy}"
HOST="ubuntu@150.158.42.39"
REMOTE="/var/www/yixing"
LOCAL="/workspace/esnlink-deploy/site"

echo "==> Deploying esnlink.cn growth optimizations..."

# Generate og-image if missing
if [ ! -f "$LOCAL/og-image.png" ]; then
    python3 /workspace/esnlink-deploy/generate_og_image.py
fi

# Sync changed files (upload to /tmp then move with sudo)
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" "mkdir -p /tmp/esnlink-deploy"
scp -i "$KEY" -o StrictHostKeyChecking=no \
    "$LOCAL/index.html" \
    "$LOCAL/call-center.html" \
    "$LOCAL/og-image.png" \
    "$LOCAL/sitemap.xml" \
    "$HOST:/tmp/esnlink-deploy/"

ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" "
    sudo mv /tmp/esnlink-deploy/index.html /tmp/esnlink-deploy/call-center.html /tmp/esnlink-deploy/og-image.png /tmp/esnlink-deploy/sitemap.xml $REMOTE/
    sudo chown www-data:www-data $REMOTE/index.html $REMOTE/call-center.html $REMOTE/og-image.png $REMOTE/sitemap.xml
"

# Update shared CSS
if [ -f /workspace/esnlink-deploy/css/header-footer.css ]; then
    scp -i "$KEY" -o StrictHostKeyChecking=no \
        /workspace/esnlink-deploy/css/header-footer.css \
        "$HOST:/tmp/header-footer.css"
    ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" \
        "sudo mv /tmp/header-footer.css $REMOTE/css/header-footer.css && sudo chown www-data:www-data $REMOTE/css/header-footer.css"
fi

# Fix ai-employees branding + noindex
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" << 'REMOTE_SCRIPT'
set -e
FILE="/var/www/yixing/ai-employees.html"
if [ -f "$FILE" ]; then
    sed -i 's/安禾科技/翼星科技/g' "$FILE"
    if ! grep -q 'name="robots"' "$FILE"; then
        sed -i 's/<head>/<head>\n    <meta name="robots" content="noindex, nofollow">/' "$FILE"
    else
        sed -i 's/content="index, follow"/content="noindex, nofollow"/g' "$FILE"
        sed -i 's/content="index,follow"/content="noindex, nofollow"/g' "$FILE"
    fi
    echo "Fixed ai-employees.html branding + noindex"
fi
REMOTE_SCRIPT

# Add blog CTA snippet to posts missing it
scp -i "$KEY" -o StrictHostKeyChecking=no \
    /workspace/esnlink-deploy/patch_blog_cta.py \
    "$HOST:/tmp/patch_blog_cta.py"
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" "sudo python3 /tmp/patch_blog_cta.py"

echo "==> Deploy complete. Verifying..."
ssh -i "$KEY" -o StrictHostKeyChecking=no "$HOST" "
    echo 'Pages:' && ls -la $REMOTE/index.html $REMOTE/call-center.html $REMOTE/og-image.png
    echo 'HTTP check:' && curl -sI https://esnlink.cn/call-center.html | head -3
    echo 'og-image:' && curl -sI https://esnlink.cn/og-image.png | head -3
"
