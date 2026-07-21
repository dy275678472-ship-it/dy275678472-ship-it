# esylink.cn 完整架构分析与优化指令

> 版本：2026-07-18 | 综合：服务器 SSH 实测 + 27 份审计报告 + GPT 增长诊断 + 本次部署验证  
> 综合评分：**68/100** | 可增长潜力：**8/10**

---

## 0. 执行摘要

**esylink.cn** 是合肥科讯通信技术有限公司旗下的 B2B 云通信获客站，定位为「AI外呼 + 云客服 + 400电话」一体化平台，面向中小企业。

| 维度 | 现状 | 评级 |
|------|------|------|
| SEO 页面规模 | 2,180 HTML 页 | A |
| 技术 SEO（canonical） | 73% 页面缺失 | D |
| 转化闭环 | AI客服→企微扫码断点 | C |
| 后端能力 | 8 个 FastAPI 微服务 | B |
| 前端工程化 | 纯静态 HTML，无构建链 | C |
| 视觉资产 | 极少真实图片，大量内联 SVG/Emoji | D |
| 服务器资源 | 3.6GB 内存跑 10+ 服务，Swap 2.3GB | C- |

**一句话方向：** 从「批量 SEO 工厂站」升级为「可信赖的企业云通信品牌站」，先修技术与信任，再放大行业转化。

---

## 1. 服务器架构

### 1.1 硬件与系统

| 项目 | 值 |
|------|-----|
| 云厂商 | 腾讯云轻量服务器 |
| IP | `101.34.64.67` |
| 主机名 | VM-0-4-ubuntu |
| 系统 | Ubuntu 24.04, Linux 6.8 |
| CPU | 4 核 |
| 内存 | 3.6 GB（已用 1.8GB，Swap 使用 2.3GB ⚠️） |
| 磁盘 | 59GB（已用 35GB，61%） |
| SSH 用户 | `ubuntu` |

### 1.2 域名体系（7 域名同机）

| 域名 | 用途 | 根目录 |
|------|------|--------|
| **esylink.cn** / www | 主产品站（2,180 页） | `/var/www/esylink` |
| esylink.kexun.ltd | SEO 历史别名 → 301 | 同 esylink |
| kexun.ltd | 科讯软件母公司官网 | `/var/www/kexun` |
| token.kexun.ltd | Token 平台 / 用户登录 | `/var/www/token` |
| crm.kexun.ltd | CRM 管理后台 | `/var/www/kexun` |
| global.kexun.ltd | 多语言官网（10 语种） | `/var/www/global` |
| zongmao.cn | 宗贸网（独立站） | 独立配置 |

### 1.3 服务拓扑

```
                    腾讯云安全组 (22/80/443)
                              │
                    Nginx 1.24.0 (SSL + Gzip + 限流 + CSP)
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
  /var/www/esylink      /var/www/kexun       /var/www/token
  静态 HTML 59MB        母公司官网            登录/支付
        │                     │                     │
        └──────────┬──────────┴──────────┬──────────┘
                   ▼                     ▼
         ┌─────────────────────────────────────────┐
         │     后端微服务层 (127.0.0.1)              │
         │  :8080 agent_server   AI客服 + 12 Agent  │
         │  :8081 freecomm_esl   FreeSWITCH 软电话  │
         │  :8082 crm_service    CRM v3.0          │
         │  :8083 zongmao        宗贸网             │
         │  :8100 kexun_main     Token + Leads API  │
         │  :8889 analytics      自建埋点            │
         │  :9528 wechatsync     企微同步桥接        │
         └─────────────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
    SQLite × 7          cron 定时任务
    (token/crm/         · 百度推送 06:30
     analytics/v9)      · 招投标抓取 08:00/18:00
```

### 1.4 Nginx API 路由（esylink.cn）

| 路径 | 后端 | 功能 |
|------|------|------|
| `/api/v1/leads` | :8100 | 留资入库（限流 5 burst） |
| `/api/chat` | :8080 | V9 AI 客服对话 |
| `/api/v1/track/intent` | :8080 | 意向评分追踪 |
| `/api/v1/funnel` | :8100 | 转化漏斗 |
| `/api/analytics/*` | :8889 | 页面 PV/会话追踪 |
| `/ws/sip` | :8081 | WebSocket 软电话信令 |
| `/analytics` | :8889 | Analytics Dashboard |

### 1.5 已知服务器风险

| # | 风险 | 严重度 | 修复 |
|---|------|--------|------|
| 1 | 内存 3.6GB 跑 10+ Python 服务，Swap 2.3GB | 高 | 合并服务或升配至 8GB |
| 2 | 端口 9528 绑定 0.0.0.0（wechatsync） | 中 | 改 127.0.0.1 |
| 3 | 8889 Analytics 曾全网暴露 | 中 | 确认仅 127.0.0.1 |
| 4 | 7 个 SQLite 无自动备份 | 高 | cron dump + 异地备份 |
| 5 | crm.kexun.ltd SSL 私钥权限 | 低 | chmod 修复 |
| 6 | DEEPSEEK_API_KEY 未固化 | 中 | 写入 systemd env |

---

## 2. 前端架构

### 2.1 技术栈

| 层 | 技术 | 评估 |
|----|------|------|
| 页面 | 2,180 个独立 HTML 文件 | 无模板引擎，维护成本高 |
| CSS | Tailwind (`/css/tw.css`) + CDN Font Awesome | 现代但 CDN 依赖 |
| JS | 原生 JS 6 文件 | 无 React/Vue，无构建链 |
| 生成器 | `seo-engine/generate.py` | 批量生成城市/行业页 |
| 文章工厂 | `essay_factory/factory.py` | 自动生成博客/SEO 文章 |
| PWA | manifest.json + icon-192/512 | 已配置 |

### 2.2 页面资产分布

| 类别 | 数量 | 生成方式 | SEO 质量 |
|------|------|----------|----------|
| 核心产品页 | 5 | 手工 | B+ |
| 行业方案页 | 8 | 手工 | B |
| 城市页 cities/ | 54 | 模板 | C（缺 canonical） |
| dialer/ 矩阵 | 508 | generate.py | C（大量重复） |
| city/ 矩阵 | 584 | generate.py | C（大量重复） |
| 博客 blog/ | 374+ | essay_factory | B |
| SEO 文章 | 258 | 批量（5-6 批重复） | C- |
| 案例 cases/ | 8 | 手工 | B- |
| 云客服 cs/ | 系列 | 手工+模板 | B |

### 2.3 前端 JS 组件（转化核心）

| 文件 | 功能 | 部署状态 |
|------|------|----------|
| `page-track.js` | PV/滚动/CTA 埋点 → :8889 | ✅ 2026-07-18 已优化部署 |
| `esylink-chat.js` | V8-lite AI 客服 + 企微转化 | ✅ 已部署 |
| `esylink-conversion.js` | 退出弹窗 + 悬浮按钮 + 信任条 | ✅ 已部署 |
| `conversion_trigger.js` | 行为触发器（旧版） | ⚠️ 与 conversion.js 部分重叠 |
| `wechat-login.js` | 微信登录 | ❌ 已开发未启用 |

### 2.4 CDN 依赖

```
cdnjs.cloudflare.com  → Font Awesome 6.5.0 (~3MB CSS)
cdn.jsdelivr.net        → 备用 CDN
zz.bdstatic.com         → 百度统计
clarity.ms              → Microsoft Clarity 行为录屏
```

⚠️ 国内用户可能因 CDN 延迟导致首屏慢。建议 Font Awesome 子集化到本地。

---

## 3. 后端架构

### 3.1 微服务清单

| 端口 | 服务 | 框架 | 数据库 | 核心 API |
|------|------|------|--------|----------|
| 8080 | agent_server | FastAPI | v9_sessions.db | POST /api/chat, /api/agent |
| 8081 | freecomm_esl | FastAPI+WS | — | POST /call, WS /ws/sip |
| 8082 | crm_service | FastAPI | crm.db | 客户/工单/话术 CRUD |
| 8083 | zongmao | Uvicorn | — | 宗贸网业务 |
| 8100 | kexun_main | FastAPI | token.db | /api/v1/leads, /api/v1/funnel |
| 8889 | analytics_tracker | Python | analytics.db | /api/analytics/ping |
| 9528 | wechatsync | Python | — | 企微消息桥接 |

### 3.2 数据库（全部 SQLite）

| 库 | 路径 | 关键表 | 记录数 |
|----|------|--------|--------|
| token.db | /opt/kexun-token/ | leads, users, payment_orders | leads: 33 |
| crm.db | /opt/kexun-crm/ | customers, tickets | — |
| analytics.db | — | pageviews, sessions | — |
| v9_sessions.db | — | v9_sessions (AI对话) | — |

⚠️ **Leads 仅 33 条** — 与 2,180 页面、21,537 次 CTA 曝光严重不匹配，转化漏斗存在重大泄漏。

### 3.3 SEO 内容生成管线

```
seo-engine/data/
  ├── industries.json    → 行业模板数据
  ├── cities.json        → 53 城市数据
  └── city-tiers.json    → S/A/B 城市分级

seo-engine/generate.py   → 生成 dialer/ + city/ 矩阵页
seo-engine/generate_blog.py → 生成博客
essay_factory/factory.py  → 自动写文章（cron/手动）
update_sitemap.py         → 更新 sitemap（cron 06:30 百度推送）
baidu_push_esylink.py     → 百度站长推送
```

---

## 4. B2B 业务闭环（前后端全链路）

这是整个系统最核心的架构——SEO 流量如何变成付费客户：

```
┌─────────────────────────────────────────────────────────────────┐
│                    流量获取层 (SEO + 投放)                        │
│  2,180 页面 → 6 sitemap → 百度推送 cron → 自然搜索/外链/直接访问   │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    落地页层 (静态 HTML)                           │
│  首页 / dialer/ / cs/ / pricing / free-trial / 城市页 / 博客     │
│  埋点: page-track.js → :8889 analytics.db                       │
│  录屏: Microsoft Clarity                                        │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    意向识别层 (前端 JS)                           │
│  触发条件: 停留>40s / 滚动>60% / 高意图页(pricing/dialer)         │
│  esylink-chat.js → 打开 AI 客服窗口                              │
│  esylink-conversion.js → 退出弹窗 + 悬浮按钮                     │
│  page-track.js → CTA 点击归因 (✅ 2026-07-18 已扩展)             │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI 对话层 (:8080 agent_server)                 │
│  V9-lite: POST /api/chat → DeepSeek 大模型                       │
│  行业识别 → 需求对话 → 意向评分(hot/warm)                         │
│  高意向 → POST /api/v1/leads (sendBeacon)                       │
│  意向追踪 → POST /api/v1/track/intent                           │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              ⚠️ 转化断点：企微二维码 (wecom-qr.png)                │
│  用户需手动扫码添加企微 → 无自动建联 → 估计泄漏 >70%              │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    留资入库层 (:8100 kexun_main)                  │
│  POST /api/v1/leads → token.db.leads (仅 33 条!)                │
│  字段: name, phone, company, industry, source, page_url           │
│  ⚠️ 无即时通知 → 销售不知道有新线索                               │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CRM 层 (:8082 crm_service)                    │
│  crm.db → customers, tickets                                     │
│  ⚠️ token.db.leads 与 crm.db 数据不互通（孤岛）                  │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    销售跟进层 (人工)                              │
│  企微私聊 → 需求确认 → 报价 → 试用开通 → 付费                     │
│  token.kexun.ltd → 用户注册/支付/套餐管理                         │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    产品交付层                                     │
│  :8081 FreeSWITCH → 实际外呼/客服通话                             │
│  :8100 Token平台 → 套餐开通/余额管理                              │
│  token.kexun.ltd/dashboard → 客户自助管理                         │
└─────────────────────────────────────────────────────────────────┘
```

### 4.1 闭环断裂点（按优先级）

| # | 断点 | 影响 | 修复方案 |
|---|------|------|----------|
| 1 | 企微扫码手动断点 | 70%+ 转化泄漏 | 表单留资 + 企微 API 自动建联 |
| 2 | Leads 无即时通知 | 热线索冷却 | 企微 Webhook 推送销售群 |
| 3 | token.db ↔ crm.db 不互通 | 数据孤岛 | API 集成或合并库 |
| 4 | 仅 33 条 leads / 2180 页 | 漏斗效率极低 | A/B 测试 CTA + 简化表单 |
| 5 | 微信登录未启用 | 失去微信生态流量 | 配置 AppID 启用 wechat-login.js |
| 6 | AI 客服 DEEPSEEK_API_KEY 不稳定 | 降级为静态规则 | systemd 固化环境变量 |

---

## 5. 视觉资产深度审计（图片/SVG 优化）

### 5.1 关键发现：不是「大量 SVG 文件」，而是「视觉模拟过度」

| 资产类型 | 数量 | 说明 |
|----------|------|------|
| 实际 .svg 文件 | **2 个**（mascot.svg 2KB + og-image.svg 4KB） | 文件级 SVG 很少 |
| 含内联 `<svg>` 的页面 | **1,355 页** | Font Awesome 图标 + HTML 模拟 UI |
| Font Awesome 引用 | **35,866 次** | 依赖 CDN，可本地化 |
| Emoji 使用 | **10,218 次** | 不专业，B2B 信任感弱 |
| `<img>` 标签总数 | **仅 29 个**（全站！） | 极度缺乏真实产品图 |
| WebP 引用 | **2 次** | 几乎未使用 WebP |
| PNG 引用 | **957 次** | 多数为路径引用或 CSS 背景 |
| /images/ 目录实际文件 | **5 个**（mascot.svg, og-default.png, product-dashboard.png/webp, wecom-qr.png） | 资源极度匮乏 |

### 5.2 当前视觉问题

| 问题 | 严重度 | 说明 |
|------|--------|------|
| 产品页用 HTML/CSS 模拟仪表盘 | 高 | 非真实截图，B2B 买家不信任 |
| 全站仅 1 张产品 WebP | 高 | product-dashboard.webp 仅在首页 |
| Emoji 做图标（🤖📞☁️） | 中 | 移动端菜单/博客大量使用 |
| Font Awesome CDN 3MB | 中 | 拖慢首屏，国内不稳定 |
| 无产品演示视频 | 高 | 0 条视频 |
| 无证书/资质实拍图 | 高 | 「等保三级」无证书扫描件 |
| 案例无可验证截图 | 中 | 「某保险公司」无数据 |

### 5.3 图片优化指令（分阶段）

#### Phase 1：止血（1-3 天）

```bash
# 1. Font Awesome 本地化（仅保留用到的图标子集）
# 当前用全量 CDN 6.5.0，改为本地 subset ~15KB
npx @fortawesome/fontawesome-subset --icons robot,phone,headset,check,shield,link,chart-line

# 2. 将 product-dashboard.png (35KB) 全面替换为 webp (9KB)
# 已在 /images/ 有 webp 版本，但仅首页引用
find /var/www/esylink -name '*.html' -exec sed -i 's/product-dashboard\.png/product-dashboard.webp/g' {} +

# 3. 移除移动端菜单 Emoji，替换为 Font Awesome 图标
# 🤖 → <i class="fas fa-robot">
# 📞 → <i class="fas fa-phone">
```

#### Phase 2：真实资产替换（1-2 周）

| 需制作的图片 | 规格 | 用途 | 数量 |
|-------------|------|------|------|
| 产品仪表盘截图 | WebP 800×520, <30KB | 首页/产品页 Hero | 1 |
| AI 外呼流程 GIF | WebP 动画, <200KB | /dialer/ 流程演示 | 1 |
| 云客服工作台截图 | WebP 800×520 | /cs/ 产品页 | 1 |
| 坐席监控界面 | WebP 600×400 | 价格页/案例页 | 1 |
| 等保/ISO 证书扫描 | WebP 400×300 | /trust/ 信任页 | 2-3 |
| 企微二维码 | WebP 200×200 | 客服弹窗（替换 PNG） | 1 |
| 行业场景插图 | WebP 400×300 | 8 个行业页 | 8 |
| 博客封面模板 | WebP 600×340 | 374 篇博客 | 1 模板 ×N |
| OG 社交分享图 | WebP 1200×630 | 全站 og:image | 5 变体 |

#### Phase 3：系统化（1 个月）

```
/images/
  ├── products/          # 产品截图 WebP
  │   ├── dialer-dashboard.webp
  │   ├── cs-workbench.webp
  │   └── analytics-panel.webp
  ├── industries/        # 8 行业场景图
  ├── trust/             # 证书、资质
  ├── cases/             # 案例数据卡片
  ├── blog/covers/       # 博客封面
  └── icons/             # 本地化 FA 子集
```

图片优化脚本规范：
- 全部输出 WebP（fallback PNG 仅 OG 图）
- 单图 <50KB，Hero 图 <80KB
- 统一 `loading="lazy"` + `width/height` 防 CLS
- 统一 `alt` 含关键词（已达标，保持）
- 响应式 `srcset` 为 1x/2x

---

## 6. 已完成的优化（2026-07-18）

| 项目 | 状态 |
|------|------|
| SSH 接入 101.34.64.67 | ✅ |
| page-track.js CTA 扩展（dialer/tel/企微） | ✅ 已部署 |
| esylink-chat.js 高意图页扩展 | ✅ 已部署 |
| 1,517 页注入埋点脚本 | ✅ 已部署 |
| /dialer/ /cs/ /400.html 完整三件套 | ✅ 已验证 |
| nginx reload | ✅ |
| 健康检查 0 errors | ✅ |
| 工具链入库（health_check/deploy/optimize-pages） | ✅ |
| GPT 增长方案整合 | ✅ docs/esylink-growth-plan.md |

---

## 7. 完整优化指令清单

### P0 — 立即处理（第 1 周）

| # | 任务 | 负责层 | 命令/方法 | 工时 |
|---|------|--------|-----------|------|
| 1 | 批量注入 canonical（1,495 页） | 前端/SEO | `seo-engine/generate.py` 加 canonical 模板 | 3h |
| 2 | 修 sitemap（去 www、去后台页、更新 lastmod） | SEO | `python3 update_sitemap.py` + cron | 2h |
| 3 | 修断链（/haoma.html, /cs.html） | Nginx | 301 重定向规则 | 0.5h |
| 4 | Leads 企微即时通知 | 后端 | Webhook → 销售群 | 2h |
| 5 | 闭合企微断点：表单留资替代纯扫码 | 前端+后端 | 聊天窗增加手机号表单 | 8h |
| 6 | token.db ↔ crm.db 线索同步 | 后端 | API hook on lead create | 4h |
| 7 | DEEPSEEK_API_KEY 固化 | 运维 | systemd EnvironmentFile | 0.5h |
| 8 | SQLite 自动备份 cron | 运维 | `sqlite3 .backup` daily | 1h |
| 9 | 端口 9528 改 127.0.0.1 | 运维 | 修改 bridge_v2.py bind | 0.5h |
| 10 | 合规表述修复（删除「100%合规」） | 内容 | 批量替换 | 1h |
| 11 | 补隐私协议/服务条款页 | 前端 | 新建 /legal/ | 2h |
| 12 | Font Awesome CDN → 本地子集 | 前端 | 减 3MB 首屏 | 2h |

### P1 — 30 天内

| # | 任务 | 说明 |
|---|------|------|
| 13 | 首页首屏重写 | 聚焦「AI外呼+云客服一体化」 |
| 14 | 重写 5 核心产品页 | dialer/cs/ai-voice/400/pricing |
| 15 | 制作 8 张产品 WebP 截图 | 替换 HTML 模拟仪表盘 |
| 16 | 建 /trust/ 信任中心 | 证书编号、案例、安全说明 |
| 17 | 建 /compliance/ 合规中心 | AI外呼合规、电销合规 |
| 18 | 建 8 个行业方案页 | 教育/口腔/保险/金融/电商/物流/SaaS/医疗 |
| 19 | ROI 计算器强化 | /calculator.html 对接 leads API |
| 20 | 简化表单（两步提交） | 先手机号，再补需求 |
| 21 | 启用微信登录 | wechat-login.js + AppID |
| 22 | 接入 Google Search Console | 搜索数据盲区 |
| 23 | 案例页真实数据化 | 背景-问题-方案-结果-周期 |
| 24 | 博客 CTA 强化 | 每篇加选型清单下载 |
| 25 | A/B 测试框架 | 启用 ab_test_log 表 |

### P2 — 90 天内

| # | 任务 | 说明 |
|---|------|------|
| 26 | 低质模板页 noindex/合并 | ~1,234 页相似内容 |
| 27 | CloudFlare CDN 接入 | 静态资源加速 |
| 28 | 4 条产品演示视频 | 60-90s，首页+产品页嵌入 |
| 29 | 白皮书体系 | 《中小企业AI外呼选型指南》 |
| 30 | 竞品对比矩阵 | 容联云/环信/腾讯企点 |
| 31 | 知乎/小红书/公众号矩阵 | 30天内容计划 |
| 32 | 外链建设 | B2B目录、SaaS评测站 |
| 33 | CRM 线索自动分配 | leads.owner 字段 + 规则 |
| 34 | 服务器升配至 8GB | 解决 Swap 压力 |
| 35 | 博客封面 WebP 模板 | 374 篇统一视觉 |

### P3 — 长期（6-12 个月）

- 前端框架化（Astro/Next.js SSG 替代 2180 独立 HTML）
- 私有化部署方案页
- 渠道代理体系
- 客户学院 + Newsletter
- 年度行业报告品牌资产
- 接入 nudex-seo-toolkit Profit Engine 多站监控

---

## 8. 运维命令速查

```bash
# SSH 连接
ssh -i ~/.ssh/esylink_id ubuntu@101.34.64.67

# 健康检查（本地）
python3 esylink/scripts/health_check.py

# 部署优化
bash esylink/scripts/deploy.sh

# 服务器上：重生成 SEO 页面
cd /var/www/esylink/seo-engine && python3 generate.py --sitemap

# 服务器上：查看 leads
sqlite3 /opt/kexun-token/token.db "SELECT id, name, phone, source, created_at FROM leads ORDER BY id DESC LIMIT 10;"

# 服务器上：查看服务状态
ss -tlnp | grep -E '808|810|888'
ps aux | grep uvicorn | grep -v grep

# 服务器上：nginx 配置检查
sudo nginx -t && sudo systemctl reload nginx

# 审计报告位置
ls ~/esylink-audit-delivery/reports/
```

---

## 9. 验收标准

| 阶段 | 指标 | 目标 |
|------|------|------|
| P0 完成 | canonical 覆盖率 | >95% |
| P0 完成 | 月 leads 入库 | >50 条 |
| P0 完成 | 断链数 | 0 |
| P1 完成 | 首页转化率 | >1.5% |
| P1 完成 | 产品页 WebP 覆盖 | 5 张真实截图 |
| P1 完成 | 有效线索成本 | <200 元 |
| P2 完成 | 自然搜索点击 | 2-4x |
| P2 完成 | 月付费客户 | 5-20 |

---

## 10. 相关文档索引

| 文档 | 路径 |
|------|------|
| 增长路线图 | `docs/esylink-growth-plan.md` |
| 运维审计 | `docs/esylink-ops-audit.md` |
| SSH 部署 | `docs/esylink-ssh.md` |
| 服务器审计包（27 份） | `~/esylink-audit-delivery/reports/`（服务器上） |
| 工具链 | `esylink/scripts/` |
| PR | [#6](https://github.com/dy275678472-ship-it/dy275678472-ship-it/pull/6) |
