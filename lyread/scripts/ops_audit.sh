#!/usr/bin/env bash
# LyRead 全站运维巡检：自动化组件、收款链、邮件、关键流程
set -euo pipefail

BASE_URL="${BASE_URL:-https://lyread.cn}"
PASS=0
FAIL=0
WARN=0

ok()   { echo "  ✓ $1"; PASS=$((PASS + 1)); }
bad()  { echo "  ✗ $1"; FAIL=$((FAIL + 1)); }
warn() { echo "  ! $1"; WARN=$((WARN + 1)); }

echo "=== LyRead Ops Audit ==="
echo "Target: $BASE_URL"
echo ""

# --- 1. 基础服务 ---
echo "[1] Core services"
if curl -sf "$BASE_URL/health/live" | grep -q '"status":"ok"'; then ok "API liveness"; else bad "API liveness"; fi
if curl -sf "$BASE_URL/health/ready" | grep -q '"status":"ready"'; then ok "API readiness (MySQL)"; else bad "API readiness"; fi

CFG=$(curl -sf "$BASE_URL/health/config" || echo '{}')
echo "$CFG" | python3 -c "
import sys,json
d=json.load(sys.stdin)
def b(k): print('true' if d.get(k) else 'false')
print('deepseek', d.get('deepseek'))
print('smtp_configured', d.get('smtp',{}).get('configured'))
print('alipay_configured', d.get('alipay',{}).get('configured'))
print('alipay_sandbox', d.get('alipay',{}).get('sandbox'))
print('auto_evolution', d.get('auto_evolution'))
print('expose_reset_token', d.get('expose_reset_token'))
" > /tmp/lyread_cfg_$$.txt 2>/dev/null || true

if grep -q "deepseek True" /tmp/lyread_cfg_$$.txt 2>/dev/null; then ok "DeepSeek API key set"; else bad "DeepSeek API key missing"; fi
if grep -q "smtp_configured True" /tmp/lyread_cfg_$$.txt 2>/dev/null; then ok "SMTP configured"; else warn "SMTP not configured (password reset uses token fallback)"; fi
if grep -q "alipay_configured True" /tmp/lyread_cfg_$$.txt 2>/dev/null; then ok "Alipay keys configured"; else
  if grep -q "alipay_sandbox True" /tmp/lyread_cfg_$$.txt 2>/dev/null; then warn "Alipay: sandbox mode only (no merchant keys)"; else bad "Alipay not configured"; fi
fi
if grep -q "auto_evolution True" /tmp/lyread_cfg_$$.txt 2>/dev/null; then ok "Auto evolution scheduler enabled"; else warn "Auto evolution disabled"; fi
rm -f /tmp/lyread_cfg_$$.txt

# --- 2. 前端页面 ---
echo ""
echo "[2] Frontend pages"
for p in / /login /pricing /wallet /workspace /trending /story /admin /faq /about; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$p")
  if [[ "$code" == "200" ]]; then ok "page $p"; else bad "page $p ($code)"; fi
done

# 爬虫 SSR：首页 / 价格 / 案例应返回可索引 HTML（非 SPA shell）
echo ""
echo "[2b] Bot SSR"
assert_bot_ssr() {
  local path="$1"
  local expect="$2"
  local html
  html=$(curl -sf -A "Googlebot" "$BASE_URL$path" || true)
  if echo "$html" | grep -q "$expect" && ! echo "$html" | grep -q 'id="app"'; then
    ok "bot SSR $path"
  else
    bad "bot SSR $path (expected content missing or still SPA)"
  fi
}
assert_bot_ssr "/" "LyRead AI"
assert_bot_ssr "/pricing" "点数"
assert_bot_ssr "/trending" "案例"
assert_bot_ssr "/story" "短故事"

# 案例 SPA 路径分享/爬虫：应返回正文 SSR（非首页 SPA shell）
CASE_ID=$(curl -sf "$BASE_URL/api/cases?limit=1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('cases',[{}])[0].get('id',''))" 2>/dev/null || echo "")
if [[ -n "$CASE_ID" ]]; then
  assert_bot_ssr "/case/$CASE_ID" "正文节选"
  CASE_SSR=$(curl -sf "$BASE_URL/case/$CASE_ID?ssr=1" || true)
  if echo "$CASE_SSR" | grep -q "正文节选" && echo "$CASE_SSR" | grep -q "rel=\"canonical\".*/ep/$CASE_ID" && ! echo "$CASE_SSR" | grep -q 'id="app"'; then
    ok "ssr=1 /case/$CASE_ID + canonical /ep"
  else
    bad "ssr=1 /case/$CASE_ID (missing body or canonical)"
  fi
else
  warn "no public case for /case bot SSR check"
fi

# ?ssr=1 预览开关（人类 UA）
SSR_HOME=$(curl -sf "$BASE_URL/?ssr=1" || true)
if echo "$SSR_HOME" | grep -q "注册领取" && ! echo "$SSR_HOME" | grep -q 'id="app"'; then
  ok "ssr=1 homepage preview"
else
  bad "ssr=1 homepage preview"
fi

# FAQ / About：始终 SSR，主 CTA 应对齐 register-first
echo ""
echo "[2c] FAQ/About conversion CTAs"
assert_seo_register_cta() {
  local path="$1"
  local html ctype
  ctype=$(curl -sf -D - -o /tmp/lyread_seo_$$.html "$BASE_URL$path" | tr -d '\r' | awk -F': ' 'tolower($1)=="content-type"{print tolower($2); exit}')
  html=$(cat /tmp/lyread_seo_$$.html 2>/dev/null || true)
  rm -f /tmp/lyread_seo_$$.html
  if echo "$ctype" | grep -q 'text/html' \
    && echo "$html" | grep -q 'login?mode=register' \
    && echo "$html" | grep -q '30 点' \
    && ! echo "$html" | grep -q 'id="app"'; then
    ok "SSR register CTA $path"
  else
    bad "SSR register CTA $path (need HTML + login?mode=register + 30 点)"
  fi
}
assert_seo_register_cta "/faq"
assert_seo_register_cta "/about"

# HEAD 可达性（tip 起 /faq /about 应 200，旧版 405）
echo ""
echo "[2d] FAQ/About HEAD"
for p in /faq /about; do
  code=$(curl -sS -o /dev/null -w "%{http_code}" -I "$BASE_URL$p" || echo "000")
  if [[ "$code" == "200" ]]; then ok "HEAD $p"; else bad "HEAD $p ($code, expect 200)"; fi
done

# --- 3. 收款链（沙箱/正式）---
echo ""
echo "[3] Payment chain"
if curl -sf "$BASE_URL/api/orders/packages" | grep -q '"success":true'; then ok "packages API"; else bad "packages API"; fi

USER="audit_$(date +%s)"
PASSWD="AuditTest123!"
REG=$(curl -sf -X POST "$BASE_URL/api/auth/register" -H "Content-Type: application/json" \
  -d "{\"username\":\"$USER\",\"password\":\"$PASSWD\",\"email\":\"${USER}@example.com\"}" || echo '{}')
TOKEN=$(echo "$REG" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "")
if [[ -n "$TOKEN" ]]; then
  ok "register for payment test"
  ORDER=$(curl -sf -X POST "$BASE_URL/api/orders/create" -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" -d "{\"package_id\":\"s\",\"idempotency_key\":\"audit$(date +%s)\"}" || echo '{}')
  OUT=$(echo "$ORDER" | python3 -c "import sys,json; print(json.load(sys.stdin).get('out_trade_no',''))" 2>/dev/null || echo "")
  SANDBOX=$(echo "$ORDER" | python3 -c "import sys,json; print(json.load(sys.stdin).get('sandbox',False))" 2>/dev/null || echo "False")
  if [[ -n "$OUT" ]]; then ok "create order ($OUT)"; else bad "create order"; fi
  if [[ "$SANDBOX" == "True" ]]; then
    PAID=$(curl -sf -X POST "$BASE_URL/api/orders/sandbox/confirm/$OUT" -H "Authorization: Bearer $TOKEN" || echo '{}')
    if echo "$PAID" | grep -q '"status":"paid"'; then ok "sandbox payment → credits credited"; else bad "sandbox confirm failed"; fi
  else
    PAY_URL=$(echo "$ORDER" | python3 -c "import sys,json; print(json.load(sys.stdin).get('pay_url') or '')" 2>/dev/null || echo "")
    if [[ -n "$PAY_URL" ]]; then ok "Alipay pay_url generated"; else warn "No pay_url (keys missing?)"; fi
  fi
else
  bad "register for payment test"
fi

# --- 4. 创作主链路 API ---
echo ""
echo "[4] Creation APIs"
if curl -sf "$BASE_URL/api/credits/prices" | grep -q signup_bonus; then ok "credits/prices"; else bad "credits/prices"; fi
if curl -sf "$BASE_URL/api/cases" | grep -q '"success":true'; then ok "public cases"; else bad "public cases"; fi

# 案例节选质量：列表 has_body + excerpt_chars（seed 后应全量 ≥2000）
CASES_AUDIT_FILE=$(mktemp)
if curl -sf "$BASE_URL/api/cases?limit=200" -o "$CASES_AUDIT_FILE" \
  && python3 - <<PY
import json
cases = json.load(open("$CASES_AUDIT_FILE")).get("cases") or []
if not cases:
    raise SystemExit(1)
no_body = sum(1 for c in cases if not c.get("has_body"))
short = sum(1 for c in cases if int(c.get("excerpt_chars") or 0) < 2000)
if no_body or short:
    print(f"  detail: total={len(cases)} no_body={no_body} short(<2000)={short}", flush=True)
    raise SystemExit(1)
PY
then
  ok "case excerpts ≥2000 (all)"
else
  warn "case excerpts short/missing (seed tip #118+)"
fi
rm -f "$CASES_AUDIT_FILE"

# sitemap Content-Type（text/plain 会被部分爬虫降权/忽略）；HEAD 需 200 且 CT 正确
echo ""
echo "[4a] Sitemap / SEO cluster"
SITEMAP_HEAD=$(curl -sI "$BASE_URL/sitemap.xml" | tr -d '\r')
SITEMAP_HEAD_CODE=$(printf '%s\n' "$SITEMAP_HEAD" | awk 'NR==1{print $2; exit}')
SITEMAP_CT=$(printf '%s\n' "$SITEMAP_HEAD" | awk -F': ' 'tolower($1)=="content-type"{print tolower($2); exit}')
# 若 HEAD 未通，回退 GET（避免旧后端 405 JSON 误报 CT）
if [[ "$SITEMAP_HEAD_CODE" != "200" || "$SITEMAP_CT" != application/xml* ]]; then
  SITEMAP_CT=$(curl -sD - -o /dev/null "$BASE_URL/sitemap.xml" | tr -d '\r' | awk -F': ' 'tolower($1)=="content-type"{print tolower($2); exit}')
fi
if [[ "$SITEMAP_HEAD_CODE" == "200" ]]; then ok "HEAD /sitemap.xml"; else bad "HEAD /sitemap.xml ($SITEMAP_HEAD_CODE, expect 200)"; fi
if [[ "$SITEMAP_CT" == application/xml* ]]; then ok "sitemap Content-Type ($SITEMAP_CT)"; else bad "sitemap Content-Type ($SITEMAP_CT, expect application/xml)"; fi
GUIDE_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/guide")
COMPARE_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/compare")
if [[ "$GUIDE_CODE" == "200" && "$COMPARE_CODE" == "200" ]]; then ok "SEO cluster /guide /compare"; else bad "SEO cluster guide=$GUIDE_CODE compare=$COMPARE_CODE"; fi
GUIDE_HEAD=$(curl -sI "$BASE_URL/guide" | tr -d '\r' | awk 'NR==1{print $2; exit}')
COMPARE_HEAD=$(curl -sI "$BASE_URL/compare" | tr -d '\r' | awk 'NR==1{print $2; exit}')
GENRE_HEAD=$(curl -sI "$BASE_URL/genre/xianxia" | tr -d '\r' | awk 'NR==1{print $2; exit}')
if [[ "$GUIDE_HEAD" == "200" && "$COMPARE_HEAD" == "200" && "$GENRE_HEAD" == "200" ]]; then
  ok "HEAD /guide /compare /genre"
else
  bad "HEAD SEO cluster guide=$GUIDE_HEAD compare=$COMPARE_HEAD genre=$GENRE_HEAD (expect 200)"
fi

# 题材 OG / 封面光栅资源（社交爬虫不吃 SVG；缺文件时 nginx SPA 也会 200 HTML，需验 Content-Type）
echo ""
echo "[4b] Genre OG assets"
OG_OK=0
for f in og-genre-xianxia.webp og-genre-romance.webp og-genre-scifi.webp og-genre-suspense.webp og-genre-history.webp cover-xianxia.webp cover-romance.webp; do
  ctype=$(curl -sI "$BASE_URL/images/$f" | tr -d '\r' | awk -F': ' 'tolower($1)=="content-type"{print tolower($2); exit}')
  if [[ "$ctype" == image/* ]]; then OG_OK=$((OG_OK + 1)); fi
done
if [[ "$OG_OK" -ge 7 ]]; then ok "genre OG/cover webp assets ($OG_OK/7)"; else bad "genre OG/cover webp assets ($OG_OK/7, need image/* not SPA HTML)"; fi

# --- 5. 安全 ---
echo ""
echo "[5] Security"
CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/admin/stats" -H "Authorization: Bearer $TOKEN")
[[ "$CODE" == "403" ]] && ok "admin blocked for normal user" || bad "admin auth ($CODE)"
MOD=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/story/generate-title" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"prompt":"制毒教程","genre":"都市"}')
[[ "$MOD" == "422" ]] && ok "content moderation active" || bad "content moderation ($MOD)"

# --- 汇总 ---
echo ""
echo "========================================"
echo "PASS: $PASS  WARN: $WARN  FAIL: $FAIL"
if [[ "$FAIL" -gt 0 ]]; then exit 1; fi
exit 0
