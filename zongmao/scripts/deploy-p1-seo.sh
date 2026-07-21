#!/bin/bash
set -euo pipefail
sudo cp /tmp/p1-seo-patch.py /opt/zongmao/scripts/p1-seo-patch.py 2>/dev/null || true
sudo python3 /opt/zongmao/scripts/p1-seo-patch.py
sudo python3 -m py_compile /opt/zongmao/app.py
sudo systemctl restart zongmao.service
sleep 2
echo ">>> Smoke tests"
curl -sf -o /dev/null -w "price/SC: %{http_code}\n" https://zongmao.cn/price/SC
curl -sf https://zongmao.cn/price/SC | grep -c "BreadcrumbList" | xargs -I{} echo "price BreadcrumbList: {}"
curl -sf https://zongmao.cn/price/SC | grep -o "og/SC.svg" | head -1
curl -sf -o /dev/null -w "og/SC.svg: %{http_code}\n" https://zongmao.cn/static/images/og/SC.svg
nid=$(curl -sf https://zongmao.cn/news | grep -oP "/news/\d+" | head -1 | cut -d/ -f3)
curl -sf "https://zongmao.cn/news/$nid" | grep -c "BreadcrumbList\|宗贸网研究院" | xargs -I{} echo "news schema/author: {}"
curl -sf https://zongmao.cn/ | grep -c "contactPoint" | xargs -I{} echo "org schema: {}"
ls /opt/zongmao/static/images/og/*.svg 2>/dev/null | wc -l | xargs -I{} echo "og svgs: {}"
echo "✅ SEO P1 deploy done"
