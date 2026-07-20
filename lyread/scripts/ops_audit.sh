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
for p in / /login /pricing /wallet /workspace /trending /admin; do
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

# ?ssr=1 预览开关（人类 UA）
SSR_HOME=$(curl -sf "$BASE_URL/?ssr=1" || true)
if echo "$SSR_HOME" | grep -q "注册领取" && ! echo "$SSR_HOME" | grep -q 'id="app"'; then
  ok "ssr=1 homepage preview"
else
  bad "ssr=1 homepage preview"
fi

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
