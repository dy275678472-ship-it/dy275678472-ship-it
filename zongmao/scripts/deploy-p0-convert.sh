#!/bin/bash
set -euo pipefail
sudo mkdir -p /opt/zongmao/scripts /var/log/zongmao
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
sudo cp "$SCRIPT_DIR/p0-convert-patch.py" /opt/zongmao/scripts/p0-convert-patch.py
sudo python3 /opt/zongmao/scripts/p0-convert-patch.py
sudo python3 -m py_compile /opt/zongmao/app.py
sudo systemctl restart zongmao.service
sleep 2
echo ">>> Smoke tests"
curl -sf -o /dev/null -w "sparkline: %{http_code}\n" "https://zongmao.cn/api/symbol/RB/sparkline"
curl -sf "https://zongmao.cn/api/symbol/RB/sparkline" | python3 -c "import sys,json; d=json.load(sys.stdin); print('points:', len(d.get('data',[])))"
curl -sf -o /dev/null -w "register: %{http_code}\n" https://zongmao.cn/register
curl -sf -o /dev/null -w "signals: %{http_code}\n" https://zongmao.cn/signals
grep -q "logged_in" /opt/zongmao/templates/signals.html && echo "signals gating: OK"
grep -q "user_id" /opt/zongmao/app.py && echo "user_id cookie: OK"
echo "✅ Convert P0 deploy done"
