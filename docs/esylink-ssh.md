# Esylink 服务器 SSH 部署指南

> 与 LyRead、上海A 使用**同一套模式**：Cloud Agent 生成密钥对 → 您把**公钥**写入服务器 → Agent 即可远程部署。

| 项目 | 值 |
|------|-----|
| 名称 | Esylink 生产机 |
| IP | `101.34.64.67` |
| 域名 | `esylink.cn` / `token.kexun.ltd` |
| 用户 | `ubuntu`（腾讯云惯例） |
| 密钥备注 | `cursor-cloud-agent-esylink` |
| 站点规模 | ~4,000 URL（6 个子 sitemap） |

## 公钥（添加到服务器）

将下面整行追加到服务器的 `~/.ssh/authorized_keys`：

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAyc3RUFZLrzB9amoxrZX6aXxCf8Sc+8bAB8VGeFF1NR cursor-cloud-agent-esylink
```

指纹：`SHA256:VW37/qE1LPhavvOleqJCB6KY4vwjbTWw6UycNQk2qYo`

## 方法一：腾讯云网页终端（推荐）

1. 打开 [腾讯云轻量服务器控制台](https://console.cloud.tencent.com/lighthouse/instance)
2. 找到 IP 为 `101.34.64.67` 的实例
3. 点击 **登录** → 使用网页终端
4. 执行：

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAyc3RUFZLrzB9amoxrZX6aXxCf8Sc+8bAB8VGeFF1NR cursor-cloud-agent-esylink' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## 验证（公钥写入后）

```bash
ssh -i ~/.ssh/esylink_id ubuntu@101.34.64.67 "hostname && whoami && nginx -v"
```

Cloud Agent 侧私钥路径：`/home/ubuntu/.ssh/esylink_id`

## 公钥写入后 — 一键部署

```bash
bash esylink/scripts/deploy.sh
```

或手动：

```bash
# 定位站点根目录
ssh -i ~/.ssh/esylink_id ubuntu@101.34.64.67 "sudo nginx -T 2>/dev/null | grep -A2 'server_name esylink'"

# 同步优化后的 JS
rsync -avz -e "ssh -i ~/.ssh/esylink_id" esylink/www/js/ ubuntu@101.34.64.67:/var/www/esylink/js/

# 全站注入埋点脚本
ssh -i ~/.ssh/esylink_id ubuntu@101.34.64.67 \
  "python3 /path/to/esylink/scripts/optimize-pages.py /var/www/esylink"

sudo systemctl reload nginx
```

## 与其他服务器的对比

| 服务器 | IP | 用户 | 公钥备注 |
|--------|-----|------|----------|
| 上海A | `150.158.42.39` | `ubuntu` | `shanghai-a-deploy-150.158.42.39` |
| LyRead | `101.34.63.137` | `ubuntu` | `cursor-cloud-agent-lyread` |
| **Esylink** | `101.34.64.67` | `ubuntu` | `cursor-cloud-agent-esylink` |

## 服务器架构（待 SSH 确认）

```
nginx (443) → /var/www/esylink  (静态 HTML + Tailwind)
           → /api/analytics/    (自研埋点)
           → /api/chat          (V9 AI 客服)
           → /api/v1/leads      (线索入库)
token.kexun.ltd → 同机或关联实例（登录后台）
```

详细运维见 `docs/esylink-ops-audit.md`。
