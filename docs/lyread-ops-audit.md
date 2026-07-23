# LyRead 运维审计报告

服务器 `101.34.63.137`，域名 `lyread.cn`。

## 是否全自动运行？

**部分自动，未完全无人值守。**

| 组件 | 状态 | 说明 |
|------|------|------|
| 后端容器 | ✅ 自动 | `restart=unless-stopped`，5 分钟健康看门狗自动 `docker restart` |
| MySQL / Redis | ✅ 自动 | `unless-stopped`，仅本机 127.0.0.1 |
| Nginx + HTTPS | ✅ 自动 | Let's Encrypt 证书，`certbot.timer` 自动续期（57 天有效） |
| 内容进化调度器 | ✅ 自动 | `AUTO_EVOLUTION=1`，每 900s 周期任务 |
| 代码部署 | ❌ 手动 | `git pull` + `docker build` + 前端 `npm run build` |
| 数据库备份 | ⚠️ 半自动 | 有备份文件，**无每日 cron**（建议添加） |
| SMTP 邮件 | ❌ 未配置 | 无 `SMTP_*` 环境变量；域名无 MX 记录 |
| 支付宝正式收款 | ❌ 未配置 | 仅 `ALIPAY_SANDBOX=1`，无商户密钥 |
| Redis 使用 | ❌ 未接入 | 容器运行但后端未使用 |
| CI/CD | ❌ 无 | 无 GitHub Actions 自动部署 |

## 收款链（支付）现状

```
用户 → /pricing 下单 → POST /api/orders/create
  ├─ 有 ALIPAY_APP_ID + 私钥 → 返回 pay_url → 支付宝 → POST /api/orders/alipay/notify（验签入账）
  └─ 仅沙箱模式 → 前端弹窗 → POST /api/orders/sandbox/confirm → 点数到账
```

**当前走沙箱确认路径**，正式支付宝跳转不可用（缺少商户密钥）。

## 邮件现状

- 代码已实现 `services/email.py`
- 服务器 **未配置** SMTP
- `lyread.cn` **无 MX  DNS 记录** → 需先开通企业邮/腾讯邮并配置 MX
- 临时方案：`EXPOSE_RESET_TOKEN=1`（找回密码返回令牌，不发邮件）

## 关键流程检查

| 流程 | 状态 |
|------|------|
| 注册 → 赠送 30 点 + 每日 5 点 | ✅ |
| 创作 → 计费预冻结 → 结算/返还 | ✅ |
| 续写 → 章节入库 + 大脑更新 | ✅ |
| 提交审核 → 后台通过 → 案例区 | ✅（需人工审核） |
| 充值 → 点数到账 | ✅ 沙箱 / ❌ 正式支付宝 |
| 找回密码邮件 | ❌ 需 SMTP |
| 内容安全敏感词 | ✅ |
| 冒烟测试 10/10 | ✅ |

## 仍缺失的关键组件（按优先级）

### P0 — 收费前必须

1. **支付宝商户密钥** — `ALIPAY_APP_ID`、RSA2 私钥、支付宝公钥
2. **SMTP 企业邮箱** — 域名 MX + `SMTP_*` 凭据
3. **数据库每日备份 cron** — 防止数据丢失

### P1 — 运营稳定性

4. **一键部署脚本** — 减少手工步骤
5. **监控告警** — 除看门狗外，磁盘/内存/DeepSeek 余额告警
6. **凭证轮换** — 安全清单要求轮换曾暴露的 MySQL/API Key

### P2 — 可延后

7. Redis 接入（会话/限流/任务队列）
8. `generation_jobs` token 成本写入
9. `story_projects` 表迁移

## 快速配置命令

```bash
# 服务器上交互配置 SMTP + 支付宝
bash ~/lyread-deploy/lyread/scripts/setup_secrets.sh

# 全站巡检
BASE_URL=https://lyread.cn bash ~/lyread-deploy/lyread/scripts/ops_audit.sh

# 查看配置状态（不含密钥）
curl -s https://lyread.cn/health/config | python3 -m json.tool
```

## 需要你提供的信息

| 项目 | 获取方式 |
|------|----------|
| 企业邮箱 | 腾讯云/腾讯企业邮开通 `noreply@lyread.cn`，获取 SMTP 授权码 |
| 支付宝沙箱/正式 | [支付宝开放平台](https://open.alipay.com/) 创建应用，下载 RSA2 密钥 |
| 域名 MX | 在域名 DNS 添加企业邮 MX 记录 |

配置完成后运行 `ops_audit.sh`，`smtp.configured` 和 `alipay.configured` 应为 `true`。
