#!/bin/bash
set -euo pipefail
sudo mkdir -p /var/log/zongmao
sudo cp /opt/zongmao/scripts/p1-patch.py /opt/zongmao/scripts/p1-patch.py 2>/dev/null || true
sudo python3 /opt/zongmao/scripts/p1-patch.py
sudo systemctl restart zongmao.service
sleep 2
echo ">>> Smoke tests"
curl -sf -o /dev/null -w "methodology: %{http_code}\n" https://zongmao.cn/methodology
curl -sf -o /dev/null -w "compare: %{http_code}\n" https://zongmao.cn/compare
curl -sf -o /dev/null -w "welcome: %{http_code}\n" https://zongmao.cn/welcome
curl -sf -o /dev/null -w "tutorial: %{http_code}\n" https://zongmao.cn/tutorial
curl -sf -o /dev/null -w "price/SC: %{http_code}\n" https://zongmao.cn/price/SC
curl -sf https://zongmao.cn/sitemap.xml | grep -c methodology | xargs -I{} echo "sitemap methodology: {}"
curl -sf https://zongmao.cn/robots.txt | grep cards
echo "✅ P1 deploy done"
