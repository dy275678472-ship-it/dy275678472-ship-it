#!/usr/bin/env bash
# 在 101.34.64.67 服务器上执行此脚本（腾讯云网页终端）
# 功能：1) 写入 Cursor Agent SSH 公钥  2) 运行全站审计  3) 打包交付物
set -euo pipefail

PUBKEY='ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAyc3RUFZLrzB9amoxrZX6aXxCf8Sc+8bAB8VGeFF1NR cursor-cloud-agent-esylink'
DELIVERY=~/esylink-audit-delivery
DATE=$(date +%Y%m%d)

echo "=========================================="
echo " Esylink 服务器引导 + 审计"
echo " 用户: $(whoami)  主机: $(hostname)"
echo "=========================================="

# ── Step 1: SSH 公钥 ──
echo ""
echo ">>> [1/4] 写入 Cursor Agent SSH 公钥..."
mkdir -p ~/.ssh && chmod 700 ~/.ssh
if grep -q 'cursor-cloud-agent-esylink' ~/.ssh/authorized_keys 2>/dev/null; then
  echo "    公钥已存在，跳过"
else
  echo "$PUBKEY" >> ~/.ssh/authorized_keys
  echo "    公钥已写入 ~/.ssh/authorized_keys"
fi
chmod 600 ~/.ssh/authorized_keys
echo "    权限: $(ls -la ~/.ssh/authorized_keys)"

# ── Step 2: 基础环境信息 ──
echo ""
echo ">>> [2/4] 采集服务器基础信息..."
mkdir -p "$DELIVERY/reports" "$DELIVERY/csv" "$DELIVERY/trees"

{
  echo "# SERVER_AUDIT.md"
  echo "生成时间: $(date -Iseconds)"
  echo ""
  echo "## 基础信息"
  echo "- 用户: $(whoami)"
  echo "- 主机: $(hostname)"
  echo "- 系统: $(uname -a)"
  echo ""
  echo "## 网络"
  ip addr 2>/dev/null | head -40 || ifconfig 2>/dev/null | head -20
  echo ""
  echo "## 磁盘"
  df -h
  echo ""
  echo "## Nginx"
  nginx -v 2>&1 || echo "nginx 未安装"
  nginx -t 2>&1 || true
  echo ""
  echo "## Docker"
  docker ps -a 2>/dev/null || echo "docker 未安装"
  echo ""
  echo "## 监听端口"
  ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || true
} > "$DELIVERY/reports/01_SERVER_AUDIT.md"

# ── Step 3: 定位站点目录 ──
echo ""
echo ">>> [3/4] 定位 esylink 项目目录..."
SITE_ROOT=""
for candidate in /var/www/esylink /var/www/html /usr/share/nginx/html /opt/esylink /srv/esylink; do
  if [ -f "$candidate/index.html" ] || [ -f "$candidate/index.html.bak" ]; then
    SITE_ROOT="$candidate"
    break
  fi
done

if [ -z "$SITE_ROOT" ]; then
  echo "    自动定位失败，搜索中..."
  SITE_ROOT=$(find /var/www /opt /srv /home -maxdepth 4 -name 'index.html' -path '*/esylink*' 2>/dev/null | head -1 | xargs dirname 2>/dev/null || true)
fi

if [ -z "$SITE_ROOT" ]; then
  # 尝试从 nginx 配置找 root
  SITE_ROOT=$(grep -r 'server_name.*esylink' /etc/nginx 2>/dev/null | head -1 | xargs -I{} sh -c "nginx -T 2>/dev/null | grep -A20 'server_name.*esylink' | grep 'root '" | awk '{print $2}' | tr -d ';' | head -1 || true)
fi

if [ -z "$SITE_ROOT" ] || [ ! -d "$SITE_ROOT" ]; then
  echo "    ⚠️  未找到站点目录，请手动指定: SITE_ROOT=/path bash $0"
  SITE_ROOT="${SITE_ROOT:-/var/www/html}"
fi

echo "    站点目录: $SITE_ROOT"
echo "$SITE_ROOT" > "$DELIVERY/reports/SITE_ROOT.txt"

# 项目树
find "$SITE_ROOT" -maxdepth 4 \
  -not -path '*/node_modules/*' \
  -not -path '*/.git/*' \
  -not -path '*/venv/*' \
  -not -path '*/__pycache__/*' \
  -print 2>/dev/null > "$DELIVERY/trees/PROJECT_TREE.txt" || true

HTML_COUNT=$(find "$SITE_ROOT" -name '*.html' 2>/dev/null | wc -l)
echo "    HTML 页面数: $HTML_COUNT"

# Nginx 配置
if [ -d /etc/nginx ]; then
  grep -R 'server_name.*esylink' -n /etc/nginx 2>/dev/null > "$DELIVERY/reports/NGINX_ESYLINK.conf" || true
  nginx -T 2>/dev/null > "$DELIVERY/reports/NGINX_FULL.conf" || true
fi

# Sitemap 统计
if [ -f "$SITE_ROOT/sitemap-index.xml" ]; then
  python3 - "$SITE_ROOT" << 'PY' > "$DELIVERY/reports/SITEMAP_AUDIT.md" 2>/dev/null || true
import sys, xml.etree.ElementTree as ET
from pathlib import Path
root = Path(sys.argv[1])
ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
idx = root / 'sitemap-index.xml'
if idx.exists():
    tree = ET.parse(idx)
    sitemaps = [e.find('sm:loc', ns).text for e in tree.findall('sm:sitemap', ns)]
    print(f"# Sitemap Audit\n\n子 sitemap 数: {len(sitemaps)}\n")
    for sm in sitemaps:
        print(f"- {sm}")
PY
fi

# ── Step 4: 打包源码（排除敏感文件）──
echo ""
echo ">>> [4/4] 打包源码..."
cd "$SITE_ROOT"
tar \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.env' \
  --exclude='.env.*' \
  --exclude='*.pem' \
  --exclude='*.key' \
  --exclude='*.log' \
  --exclude='logs' \
  --exclude='cache' \
  -czf "$DELIVERY/esylink-current-code-safe.tar.gz" . 2>/dev/null || true

cd ~
tar -czf "esylink-audit-delivery-${DATE}.tar.gz" -C "$(dirname "$DELIVERY")" "$(basename "$DELIVERY")" 2>/dev/null || true

echo ""
echo "=========================================="
echo " ✅ 完成！交付物："
echo "    $DELIVERY/reports/01_SERVER_AUDIT.md"
echo "    $DELIVERY/trees/PROJECT_TREE.txt"
echo "    $DELIVERY/esylink-current-code-safe.tar.gz"
echo "    ~/esylink-audit-delivery-${DATE}.tar.gz"
ls -lh ~/esylink-audit-delivery-${DATE}.tar.gz 2>/dev/null || ls -lh "$DELIVERY/"*.tar.gz 2>/dev/null || true
echo ""
echo " 下一步：回复 Agent「审计完成」，Agent 将 SSH 连接并部署优化"
echo "=========================================="
