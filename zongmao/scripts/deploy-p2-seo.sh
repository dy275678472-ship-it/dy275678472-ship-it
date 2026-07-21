#!/bin/bash
set -euo pipefail
sudo cp /tmp/p2-seo-patch.py /opt/zongmao/scripts/p2-seo-patch.py 2>/dev/null || true
sudo python3 /opt/zongmao/scripts/p2-seo-patch.py
sudo python3 -m py_compile /opt/zongmao/app.py
sudo systemctl restart zongmao.service
sleep 2
echo ">>> Smoke tests"
curl -sf -o /dev/null -w "glossary: %{http_code}\n" https://zongmao.cn/glossary
curl -sf -o /dev/null -w "stats/2026: %{http_code}\n" https://zongmao.cn/stats/2026
curl -sf https://zongmao.cn/glossary | grep -c "FAQPage" | xargs -I{} echo "glossary FAQPage: {}"
curl -sf https://zongmao.cn/stats/2026 | grep -oE "[0-9]+\.[0-9]+%|累计信号" | head -4
curl -sf https://zongmao.cn/compare | grep -c "compare-lead-form" | xargs -I{} echo "compare lead: {}"
curl -sf https://zongmao.cn/sitemap.xml | grep -c "glossary\|stats/2026" | xargs -I{} echo "sitemap new pages: {}"
curl -sf https://zongmao.cn/llms.txt | grep -c glossary | xargs -I{} echo "llms glossary: {}"
echo "✅ SEO P2 deploy done"
