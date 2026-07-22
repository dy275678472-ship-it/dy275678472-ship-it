#!/usr/bin/env bash
# 在服务器上配置 SMTP / 支付宝密钥（写入 /tmp/lyread.env 后重启后端）
# 用法: sudo bash setup_secrets.sh
set -euo pipefail

ENV_FILE="${ENV_FILE:-/tmp/lyread.env}"
BACKUP="${ENV_FILE}.bak.$(date +%Y%m%d%H%M%S)"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "错误: 找不到 $ENV_FILE"
  exit 1
fi

cp "$ENV_FILE" "$BACKUP"
echo "已备份: $BACKUP"

upsert() {
  local key="$1" val="$2"
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i "s|^${key}=.*|${key}=${val}|" "$ENV_FILE"
  else
    echo "${key}=${val}" >> "$ENV_FILE"
  fi
}

echo ""
echo "=== SMTP 邮件（腾讯企业邮 / QQ 邮箱示例）==="
echo "lyread.cn 当前无 MX 记录，需先在域名控制台开通企业邮并添加 MX。"
echo ""
read -rp "SMTP_HOST [smtp.exmail.qq.com]: " SMTP_HOST
SMTP_HOST=${SMTP_HOST:-smtp.exmail.qq.com}
read -rp "SMTP_PORT [465]: " SMTP_PORT
SMTP_PORT=${SMTP_PORT:-465}
read -rp "SMTP_SSL (1=SSL/465, 0=STARTTLS/587) [1]: " SMTP_SSL
SMTP_SSL=${SMTP_SSL:-1}
read -rp "SMTP_USER (发信账号): " SMTP_USER
read -rsp "SMTP_PASSWORD (授权码): " SMTP_PASSWORD; echo
read -rp "SMTP_FROM [noreply@lyread.cn]: " SMTP_FROM
SMTP_FROM=${SMTP_FROM:-noreply@lyread.cn}
read -rp "SITE_URL [https://lyread.cn]: " SITE_URL
SITE_URL=${SITE_URL:-https://lyread.cn}

if [[ -n "$SMTP_USER" && -n "$SMTP_PASSWORD" ]]; then
  upsert SMTP_HOST "$SMTP_HOST"
  upsert SMTP_PORT "$SMTP_PORT"
  upsert SMTP_SSL "$SMTP_SSL"
  upsert SMTP_USER "$SMTP_USER"
  upsert SMTP_PASSWORD "$SMTP_PASSWORD"
  upsert SMTP_FROM "$SMTP_FROM"
  upsert SMTP_TLS "0"
  upsert SITE_URL "$SITE_URL"
  echo "SMTP 已写入 $ENV_FILE"
else
  echo "跳过 SMTP（未填写账号/密码）"
fi

echo ""
echo "=== 支付宝收款 ==="
echo "沙箱: https://open.alipay.com/develop/sandbox/app"
echo "正式: https://open.alipay.com/"
echo ""
read -rp "ALIPAY_SANDBOX (1=沙箱, 0=正式) [1]: " ALIPAY_SANDBOX
ALIPAY_SANDBOX=${ALIPAY_SANDBOX:-1}
read -rp "ALIPAY_APP_ID: " ALIPAY_APP_ID
echo "ALIPAY_PRIVATE_KEY (粘贴 RSA2 私钥，单行或 PEM，输入 END 结束):"
PRIV=""
while IFS= read -r line; do
  [[ "$line" == "END" ]] && break
  PRIV+="${line}"
done
echo "ALIPAY_PUBLIC_KEY (支付宝公钥，输入 END 结束):"
PUB=""
while IFS= read -r line; do
  [[ "$line" == "END" ]] && break
  PUB+="${line}"
done

if [[ -n "$ALIPAY_APP_ID" && -n "$PRIV" ]]; then
  upsert ALIPAY_SANDBOX "$ALIPAY_SANDBOX"
  upsert ALIPAY_APP_ID "$ALIPAY_APP_ID"
  upsert ALIPAY_PRIVATE_KEY "$PRIV"
  [[ -n "$PUB" ]] && upsert ALIPAY_PUBLIC_KEY "$PUB"
  upsert ALIPAY_NOTIFY_URL "https://lyread.cn/api/orders/alipay/notify"
  upsert ALIPAY_RETURN_URL "https://lyread.cn/wallet"
  echo "支付宝已写入 $ENV_FILE"
else
  echo "跳过支付宝（未填写 APP_ID/私钥）"
fi

echo ""
echo "重启后端以生效:"
echo "  docker stop lyread-backend-fix && docker rm lyread-backend-fix"
echo "  docker run -d --name lyread-backend-fix --network lyread-net --restart unless-stopped \\"
echo "    -p 127.0.0.1:8004:8000 --env-file $ENV_FILE <image-tag>"
echo ""
echo "验证: curl -s https://lyread.cn/health/config | python3 -m json.tool"
