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

### ⚠️ 待优化（本次 PR 已修复）

| 问题 | 影响 | 修复 |
|------|------|------|
| `/dialer/`、`/cs/`、`/400.html` 缺 `page-track.js` | 高意图页转化数据丢失 | `optimize-pages.py` 批量注入 |
| `/dialer/`、`/cs/`、`/400.html` 缺 `esylink-chat.js` | 外呼页无法触发 AI 客服 | 同上 |
| `page-track.js` CTA 正则未覆盖 `/dialer/`、`tel:` | 点击归因不全 | 扩展正则 |
| `esylink-chat.js` 高意图判定未含 `/dialer/` | 自动弹窗阈值偏高 | 扩展 `isHighIntent` |
| 首页 `og:title` 与 `<title>` 不一致 | 社交分享文案偏差 | `optimize-pages.py` 修正 |
| sitemap-index `lastmod` 停留在 2026-06-26 | 爬虫新鲜度信号弱 | 需服务端重新生成 sitemap |

### 📋 后续优化路线图

| 优先级 | 任务 | 说明 |
|--------|------|------|
| P0 | SSH 接入 + 源码入库 | 将 `/var/www/esylink` 同步到 `esylink/www/` |
| P0 | 部署优化 JS | `bash esylink/scripts/deploy.sh` |
| P1 | sitemap 自动更新 cron | 每日刷新 lastmod，保持 GSC 活跃 |
| P1 | `/api/chat` 可用性监控 | V9 AI 客服降级率告警 |
| P1 | 图片 WebP 全覆盖 | 部分页面仍用 SVG/emoji 占位 |
| P2 | 接入 nudex-seo-toolkit Profit Engine | 多站健康监控 + 自动修复 |
| P2 | Core Web Vitals | Font Awesome CDN 改本地子集化 |

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
