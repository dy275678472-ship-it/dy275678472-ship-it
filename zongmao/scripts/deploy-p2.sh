#!/bin/bash
set -euo pipefail
sudo mkdir -p /var/log/zongmao
sudo cp /opt/zongmao/scripts/p2-patch.py /opt/zongmao/scripts/p2-patch.py 2>/dev/null || sudo cp /tmp/p2-patch.py /opt/zongmao/scripts/p2-patch.py
sudo python3 /opt/zongmao/scripts/p2-patch.py
sudo python3 -m py_compile /opt/zongmao/app.py
sudo systemctl restart zongmao.service
sleep 2
echo ">>> Smoke tests"
curl -sf -o /dev/null -w "category/能源: %{http_code}\n" "https://zongmao.cn/category/%E8%83%BD%E6%BA%90"
curl -sf -o /dev/null -w "asset/SC原油 redirect: %{http_code}\n" -L -o /dev/null -w "%{url_effective} %{http_code}\n" "https://zongmao.cn/asset/SC%E5%8E%9F%E6%B2%B9" 2>/dev/null || curl -sI "https://zongmao.cn/asset/SC%E5%8E%9F%E6%B2%B9" | head -3
REDIR=$(curl -sI "https://zongmao.cn/asset/SC%E5%8E%9F%E6%B2%B9" | grep -i "^location:" | awk '{print $2}' | tr -d '\r')
echo "asset redirect location: ${REDIR:-none}"
curl -sf -o /dev/null -w "signal/bullish/SC: %{http_code}\n" https://zongmao.cn/signal/bullish/SC
TOTAL=$(curl -sf https://zongmao.cn/sitemap.xml | grep -c "<loc>" || echo 0)
CARDS=$(curl -sf https://zongmao.cn/sitemap.xml | grep -c "/cards/" || echo 0)
ASSETS=$(curl -sf https://zongmao.cn/sitemap.xml | grep -c "/asset/" || echo 0)
SIGNALS=$(curl -sf https://zongmao.cn/sitemap.xml | grep -c "/signal/" || echo 0)
echo "sitemap: total=$TOTAL cards=$CARDS assets=$ASSETS signals=$SIGNALS"
curl -sf https://zongmao.cn/sitemap.xml | grep -c "category" | xargs -I{} echo "sitemap categories: {}"
curl -sI https://zongmao.cn/ | grep -i "strict-transport-security" | head -1
NOIDX=$(curl -sf https://zongmao.cn/cards/8ec1209c62a9 2>/dev/null | grep -c noindex || echo 0)
echo "card noindex: $NOIDX"
echo "✅ P2 deploy done"
