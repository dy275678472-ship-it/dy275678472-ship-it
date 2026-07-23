#!/usr/bin/env bash
# LyRead 端到端冒烟验收（主链路 + 权限 + 计费基础）
set -euo pipefail

BASE_URL="${BASE_URL:-https://lyread.cn}"
PASS=0
FAIL=0

log() { echo "[smoke] $*"; }
ok() { log "✓ $1"; PASS=$((PASS + 1)); }
bad() { log "✗ $1"; FAIL=$((FAIL + 1)); }

json_field() {
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d$1)" 2>/dev/null || echo ""
}

# --- 健康检查 ---
if curl -sf "$BASE_URL/health/live" | grep -q '"status":"ok"'; then
  ok "health/live"
else
  bad "health/live"
fi

# --- 公开 API ---
if curl -sf "$BASE_URL/api/credits/prices" | grep -q '"success":true'; then
  ok "credits/prices"
else
  bad "credits/prices"
fi

if curl -sf "$BASE_URL/api/cases" | grep -q '"success":true'; then
  ok "cases list"
else
  bad "cases list"
fi

# --- 注册 + 登录 ---
USER="smoke_$(date +%s)"
PASSWD="SmokeTest123!"
REG=$(curl -sf -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USER\",\"password\":\"$PASSWD\",\"email\":\"${USER}@example.com\"}" || echo '{}')
TOKEN=$(echo "$REG" | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null || echo "")
if [[ -n "$TOKEN" ]]; then
  ok "register ($USER)"
else
  bad "register"
  echo "$REG"
fi

AUTH="Authorization: Bearer $TOKEN"

# --- 余额 ---
BAL=$(curl -sf "$BASE_URL/api/credits/balance" -H "$AUTH" || echo '{}')
if echo "$BAL" | grep -q '"success":true'; then
  ok "credits balance"
else
  bad "credits balance"
fi

# --- 创建作品 ---
CREATE=$(curl -sf -X POST "$BASE_URL/api/story/create" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"title":"冒烟测试作品","genre":"都市","intro":"测试简介"}' || echo '{}')
STORY_ID=$(echo "$CREATE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('story_id',''))" 2>/dev/null || echo "")
if [[ -n "$STORY_ID" ]]; then
  ok "create story ($STORY_ID)"
else
  bad "create story"
fi

# --- 越权：未登录创作接口 ---
CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/story/generate-outline" \
  -H "Content-Type: application/json" \
  -d '{"title":"x","intro":"y","hot_points":["a"]}')
if [[ "$CODE" == "401" || "$CODE" == "403" ]]; then
  ok "generate-outline requires auth ($CODE)"
else
  bad "generate-outline auth expected 401, got $CODE"
fi

# --- 内容安全：敏感词拦截 ---
MOD_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/story/generate-title" \
  -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"prompt":"制毒教程","genre":"都市"}')
if [[ "$MOD_CODE" == "422" ]]; then
  ok "content moderation blocks input"
else
  bad "content moderation expected 422, got $MOD_CODE"
fi

# --- 管理员接口拒绝普通用户 ---
ADMIN_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/admin/stats" -H "$AUTH")
if [[ "$ADMIN_CODE" == "403" ]]; then
  ok "admin forbidden for normal user"
else
  bad "admin expected 403, got $ADMIN_CODE"
fi

# --- 找回密码 ---
FORGOT=$(curl -sf -X POST "$BASE_URL/api/auth/forgot" -H "Content-Type: application/json" \
  -d "{\"username\":\"$USER\",\"email\":\"${USER}@example.com\"}" || echo '{}')
if echo "$FORGOT" | grep -q '"success":true'; then
  ok "forgot password"
else
  bad "forgot password"
fi

# --- 汇总 ---
log "----------------------------------------"
log "通过: $PASS  失败: $FAIL"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
