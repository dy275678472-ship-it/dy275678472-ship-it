#!/bin/bash
set -euo pipefail
sudo mkdir -p /opt/zongmao/scripts /var/log/zongmao
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
for f in validation-patch.py product-validation-report.py; do
  if [ "$SCRIPT_DIR/$f" != "/opt/zongmao/scripts/$f" ]; then
    sudo cp "$SCRIPT_DIR/$f" "/opt/zongmao/scripts/$f"
  fi
done
sudo python3 /opt/zongmao/scripts/validation-patch.py
sudo python3 -m py_compile /opt/zongmao/app.py
sudo systemctl restart zongmao.service
sleep 2
echo ">>> 验证报告"
sudo python3 /opt/zongmao/scripts/product-validation-report.py | tail -25
echo ">>> API smoke"
curl -sf -X POST https://zongmao.cn/api/validation/event \
  -H 'Content-Type: application/json' \
  -d '{"event":"deploy_test","page":"/"}' | head -c 80
echo ""
echo "✅ 产品验证体系部署完成"
