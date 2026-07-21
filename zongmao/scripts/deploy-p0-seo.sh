#!/bin/bash
set -euo pipefail
sudo mkdir -p /opt/zongmao/scripts /var/log/zongmao
sudo cp /tmp/p0-seo-patch.py /opt/zongmao/scripts/p0-seo-patch.py 2>/dev/null || true
sudo python3 /opt/zongmao/scripts/p0-seo-patch.py
sudo python3 -m py_compile /opt/zongmao/app.py
sudo systemctl restart zongmao.service
sleep 2
echo ">>> Smoke tests"
curl -sf -o /dev/null -w "llms.txt: %{http_code}\n" https://zongmao.cn/llms.txt
curl -sf https://zongmao.cn/llms.txt | head -3
curl -sf https://zongmao.cn/performance | grep -oE "[0-9]+\.[0-9]+%|[0-9]+</div><div class=\"kpi-label\">总信号" | head -5
curl -sI https://www.zongmao.cn/ | grep -i "^location:"
grep "site=" /opt/zongmao/baidu_push.py | head -1
echo "✅ SEO P0 deploy done"
