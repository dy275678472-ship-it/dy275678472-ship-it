#!/bin/bash
set -euo pipefail

echo "=== KDGC Full Deploy ==="
cd /opt/kdgc-growth

# Python venv
if [ ! -d venv ]; then
  python3 -m venv venv
fi
venv/bin/pip install -q -r backend/requirements.txt

# PostgreSQL user
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='kdgc'" | grep -q 1 || \
  sudo -u postgres psql -c "CREATE USER kdgc WITH PASSWORD 'kdgc_secure_2026';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE kdgc TO kdgc;" 2>/dev/null || true
sudo -u postgres psql -d kdgc -c "GRANT ALL ON SCHEMA public TO kdgc;" 2>/dev/null || true

# Seed database
export DATABASE_URL=postgresql+asyncpg://kdgc:kdgc_secure_2026@127.0.0.1:5432/kdgc
cd backend && ../venv/bin/python seed.py && cd ..

# Optimize images
mkdir -p frontend/dist/assets/images
shopt -s nullglob
for img in frontend/out/*.png; do
  base=$(basename "$img" .png)
  case "$base" in
    56160518) out=aln-substrate ;;
    56160519) out=dbc-amb ;;
    56160517) out=alumina ;;
    *) out="$base" ;;
  esac
  cwebp -q 80 "$img" -o "frontend/dist/assets/images/${out}.webp" 2>/dev/null || cp "$img" "frontend/dist/assets/images/${out}.png"
done
for ico in frontend/out/*.ico; do
  cp "$ico" frontend/dist/assets/images/favicon.ico
done
shopt -u nullglob
# fallback og image
[ -f frontend/dist/assets/images/aln-substrate.webp ] && cp frontend/dist/assets/images/aln-substrate.webp frontend/dist/assets/images/og-image.webp

# Nginx
sudo cp deploy/nginx-kdgc-growth.conf /etc/nginx/sites-available/kdgc-growth
sudo ln -sf /etc/nginx/sites-available/kdgc-growth /etc/nginx/sites-enabled/kdgc-growth
sudo nginx -t && sudo systemctl reload nginx

# Backend service
sudo cp deploy/kdgc-backend.service /etc/systemd/system/kdgc-backend.service
sudo systemctl daemon-reload
sudo systemctl enable kdgc-backend
sudo systemctl restart kdgc-backend

# Stop old http.server
sudo systemctl stop kdgc-frontend 2>/dev/null || true
sudo systemctl disable kdgc-frontend 2>/dev/null || true

# SSL (may fail if DNS not pointing here)
sudo certbot --nginx -d kdgc.cc -d www.kdgc.cc --non-interactive --agree-tos -m info@kdgc.cc --redirect 2>/dev/null || echo "SSL skipped - DNS may not point here yet"

echo "=== Deploy complete ==="
curl -s http://127.0.0.1/api/health
echo ""
curl -sI http://127.0.0.1/ | head -5
