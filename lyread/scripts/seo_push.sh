#!/usr/bin/env bash
# 向搜索引擎推送 sitemap 与关键 SEO 页面（部署后执行）
set -euo pipefail

BASE_URL="${BASE_URL:-https://lyread.cn}"
SITEMAP="${BASE_URL}/sitemap.xml"

echo "=== SEO Push: ${BASE_URL} ==="

echo "[1] Google sitemap ping"
if curl -sf "https://www.google.com/ping?sitemap=${SITEMAP}" >/dev/null; then
  echo "  ✓ Google ping OK"
else
  echo "  ! Google ping failed (may still crawl via robots)"
fi

echo "[2] Bing sitemap ping"
if curl -sf "https://www.bing.com/ping?sitemap=${SITEMAP}" >/dev/null; then
  echo "  ✓ Bing ping OK"
else
  echo "  ! Bing ping failed"
fi

echo "[3] Sitemap URL count"
COUNT=$(curl -sf "${SITEMAP}" | grep -c '<loc>' || echo 0)
echo "  URLs in sitemap: ${COUNT}"

echo "[4] Baidu push"
if [[ -n "${BAIDU_PUSH_TOKEN:-}" ]]; then
  URLS="${SITEMAP}
${BASE_URL}/compare
${BASE_URL}/compare/biling
${BASE_URL}/compare/waqupin
${BASE_URL}/compare/chatgpt
${BASE_URL}/guide
${BASE_URL}/guide/ai-novel-start
${BASE_URL}/guide/outline-chapters
${BASE_URL}/guide/daily-update"
  RESP=$(curl -sf -X POST \
    "http://data.zz.baidu.com/urls?site=${BASE_URL}&token=${BAIDU_PUSH_TOKEN}" \
    -H "Content-Type: text/plain" \
    --data-binary "$URLS" || echo "failed")
  echo "  Baidu: ${RESP}"
else
  echo "  ! BAIDU_PUSH_TOKEN not set — submit sitemap manually at https://ziyuan.baidu.com/linksubmit/index"
fi

echo "=== done ==="
