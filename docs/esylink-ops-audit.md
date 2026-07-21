# Esylink 运维审计报告

> 审计时间：2026-07-18 | 站点：https://esylink.cn | 服务器：101.34.64.67

## 站点概况

| 指标 | 值 |
|------|-----|
| 品牌 | 易连云通信（合肥科讯通信技术有限公司） |
| 核心产品 | AI智能外呼 / 云客服 / 400全国热线 |
| 技术栈 | nginx + 静态 HTML + Tailwind (`/css/tw.css`) |
| 转化组件 | V8-lite 聊天 (`esylink-chat.js`) + 退出弹窗 (`esylink-conversion.js`) |
| 埋点 | 自研 `page-track.js` + Clarity + `/api/analytics/` |
| SEO 规模 | 6 个子 sitemap，主 sitemap ~2,176 URL |
| 后台 | https://token.kexun.ltd/login.html |

## 本次审计发现

### ✅ 已达标

- HTTPS + HSTS + CSP 安全头完整
- 首页 title/description/H1 结构正确
- 关键页面无死链（抽样 42 条内链全部 200）
- 博客/城市页已嵌入完整转化脚本三件套
- robots.txt 正确指向 6 个 sitemap
- PWA manifest.json 已配置

### ✅ 已部署（2026-07-18）

| 问题 | 状态 |
|------|------|
| `/dialer/`、`/cs/`、`/400.html` 缺 `page-track.js` | ✅ 已注入（1,517 页） |
| `/dialer/`、`/cs/`、`/400.html` 缺 `esylink-chat.js` | ✅ 已注入 |
| `page-track.js` CTA 正则未覆盖 `/dialer/`、`tel:` | ✅ 已部署新版 JS |
| `esylink-chat.js` 高意图判定未含 `/dialer/` | ✅ 已部署新版 JS |
| 首页 `og:title` 与 `<title>` 不一致 | ✅ optimize-pages 已修正 |
| SSH 接入 | ✅ `ubuntu@101.34.64.67` 已验证 |

### ⚠️ 待优化（下一步 P0）

| 问题 | 影响 | 修复 |
|------|------|------|
| 1,495 页缺 canonical（73%） | 重复收录风险 | 批量 canonical 脚本 |
| sitemap-index `lastmod` 停留在 2026-06-26 | 爬虫新鲜度信号弱 | cron 自动更新 |
| Leads 无即时通知 | 热线索冷却 | 企微 Webhook |
| 8889/9528 端口全网暴露 | 安全风险 | 改 127.0.0.1 绑定 |
| 内存压力（3.6GB 跑 8 服务） | 服务不稳定 | 合并服务/升配 |

### 📋 后续优化路线图

| 优先级 | 任务 | 说明 |
|--------|------|------|
| P0 | 批量 canonical 修复 | 1,495 页缺标签（服务器审计确认） |
| P0 | sitemap 自动更新 cron | 每日刷新 lastmod |
| P0 | Leads 企微即时通知 | 留资后销售 10 分钟内触达 |
| P1 | 源码同步入库 | `sync-from-live.sh` 拉取 `/var/www/esylink` |
| P1 | `/api/chat` 可用性监控 | V9 AI 客服降级率告警 |
| P1 | 首页首屏重写 | 聚焦 AI外呼+云客服一体化 |
| P2 | CDN 接入 | CloudFlare 免费加速 |
| P2 | 接入 nudex-seo-toolkit Profit Engine | 多站健康监控 |

## 服务器架构（SSH 已确认）

| 项目 | 值 |
|------|-----|
| 主机 | VM-0-4-ubuntu（腾讯云 4核 3.6GB Ubuntu 24.04） |
| 站点根目录 | `/var/www/esylink`（2,180 HTML 页） |
| Web 服务器 | Nginx 1.24.0（7 域名 SSL） |
| 后端 | Python FastAPI × 8 服务 |
| 数据库 | SQLite × 7 |
| 审计包 | `~/esylink-audit-delivery/`（27 份报告） |

## 健康检查

```bash
# 本地运行
python3 esylink/scripts/health_check.py

# 仅检查外呼页
python3 esylink/scripts/health_check.py --page /dialer/
```

## 持续优化工作流

```
1. sync-from-live.sh  → 从线上拉取最新静态文件
2. 在 esylink/www/ 修改 + 本地验证
3. health_check.py    → 部署前审计
4. deploy.sh          → rsync 到生产 + optimize-pages + nginx reload
5. health_check.py    → 部署后验证
```

## 仓库结构

```
esylink/
├── www/js/              # 优化后的 JS（版本管理）
│   ├── page-track.js    # 埋点 v2（扩展 CTA 覆盖）
│   ├── esylink-chat.js  # V8-lite AI 客服
│   └── esylink-conversion.js
└── scripts/
    ├── health_check.py  # 健康/SEO 审计
    ├── optimize-pages.py # 批量页面优化
    ├── deploy.sh        # 一键部署
    └── sync-from-live.sh
```
