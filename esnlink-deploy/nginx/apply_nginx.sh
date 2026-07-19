# Patch esnlink.cn nginx: gzip, caching, noindex for /seo/ proxy pages
# Run on server with sudo

set -e
CONF="/etc/nginx/sites-enabled/esnlink.cn"
SNIP="/etc/nginx/snippets/esnlink-performance.conf"
BACKUP="/etc/nginx/sites-enabled/esnlink.cn.bak.$(date +%Y%m%d)"

if [ ! -f "$CONF" ]; then
    echo "Error: $CONF not found"
    exit 1
fi

sudo cp "$CONF" "$BACKUP"
sudo cp /tmp/esnlink-performance.conf "$SNIP"

# Add noindex header to /seo/ location
if ! grep -q 'X-Robots-Tag' "$CONF"; then
    sudo sed -i 's|add_header X-Seo-Page|add_header X-Robots-Tag "noindex, nofollow" always;\n        add_header X-Seo-Page|' "$CONF"
fi

# Include performance snippet after server_name line
if ! grep -q 'esnlink-performance' "$CONF"; then
    sudo sed -i '/server_name esnlink.cn/a\    include snippets/esnlink-performance.conf;' "$CONF"
fi

sudo nginx -t && sudo systemctl reload nginx
echo "Nginx patched OK. Backup: $BACKUP"
