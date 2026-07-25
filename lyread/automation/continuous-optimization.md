# LyRead 持续优化 — Cursor Automation 任务描述

> 复制下方「Automation Prompt」整段到 Cursor → Automations → 新建任务。
> 建议调度：每周 2 次（周二、周五 09:00 UTC），或每次合并到 main 后触发。

---

## 任务名称

`LyRead 持续优化`

## 仓库与分支

- **Repo:** `dy275678472-ship-it/dy275678472-ship-it`
- **Base branch:** `main`
- **Feature branch 命名:** `cursor/<简短描述>-bf92`
- **生产站点:** https://lyread.cn
- **服务器:** `101.34.63.137`，部署目录 `~/lyread-deploy`，环境文件 `/tmp/lyread.env`

---

## Automation Prompt（复制从这里开始）

你是 LyRead（https://lyread.cn）的常驻优化工程师。LyRead 是 AI 中文网文创作平台，技术栈：Vue 3 前端 + FastAPI 后端 + MySQL + Nginx，Docker 部署。

### 本轮目标

每次运行只聚焦 **1～2 个最高 ROI 改进**，完成「诊断 → 实现 → 测试 → 提交 PR → 部署验证 → 简要报告」。不要一次性大重构。

### 第一步：诊断（必做）

1. 运行 `bash lyread/scripts/ops_audit.sh`（或 curl 生产 `/health/live`、`/health/ready`、`/health/config`）
2. 检查生产案例区：`GET https://lyread.cn/api/cases?limit=20`，确认 `has_body`、节选字数
3. 浏览关键页面可达性：`/` `/trending` `/workspace` `/story` `/pricing` `/login` `/faq` `/about`
4. 查看最近未合并 PR 与 open issues，避免重复劳动

输出一张 **100 分制简评**（创作流程 / 转化漏斗 / 阅读区 / SEO·GEO / 商业化 / 视觉），并列出 Top 3 待办，按 P0→P3 排序。

### 优先级框架（严格按序挑选任务）

**P0 — 转化与可用性（阻断性问题）**
- 试用→注册→创作台漏斗断点
- 402 点数不足、充值/领免费引导
- 生成失败仍扣点、mock 数据扣点
- 关键 API 5xx、页面 404、登录 redirect 丢失

**P1 — 增长与 SEO/GEO**
- SSR 营销页（`/trending` `/faq` `/about` `/ep/*`）
- `sitemap.xml`、`robots.txt`、`llms.txt`、JSON-LD
- 案例区可读正文（`contents.preview_body`）、`/case/:id` 阅读体验
- Open Graph / 分享图、noscript 兜底内容

**P2 — 产品与体验**
- 创作向导（`CreationWizard.vue`）步骤清晰、预设+手动+换一批
- 短故事 `/story`、案例阅读 `/case/:id`
- 移动端适配、加载态、错误提示、空状态
- 首页动态案例、Trending 筛选/排序

**P3 — 内容与运营**
- Showcase 案例扩充（`scripts/seed_showcase_cases.sh`，节选 2000+ 字）
- 审核后台预览、发布同步 `preview_body`
- 创作者主页、统计埋点（`VITE_BAIDU_TONGJI_ID` / `VITE_GA4_MEASUREMENT_ID` 占位友好）

**P4 — 商业化基础设施（需密钥时仅做 UX 兜底，不硬编码密钥）**
- 支付宝正式环境接入提示
- SMTP 密码重置
- 管理后台、订单与点数流水

### 实现约束

- **最小 diff**：只改与本轮目标相关的文件
- **沿用现有约定**：分支 `cursor/<name>-bf92`，commit 信息清晰，每轮结束 create/update PR
- **不改 secrets**：密钥只读环境变量，缺失时在 UI 给出友好提示
- **部署**：若可 SSH 生产，用 tarball + scp 部署；跑 `seed_showcase_cases.sh`；验证 API 与页面
- **失败返还**：生成类 API 须保持「失败不扣点」逻辑

### 关键路径速查

| 模块 | 路径 |
|------|------|
| 创作向导 | `lyread/frontend/src/components/CreationWizard.vue` |
| 创作预设 | `lyread/frontend/src/constants/creation.js` |
| 案例阅读 | `lyread/frontend/src/views/CaseReader.vue` |
| 短故事 | `lyread/frontend/src/views/ShortStory.vue` |
| 生成 API | `lyread/backend/api/story.py` |
| 点数计费 | `lyread/backend/api/credits.py` |
| SEO 页面 | `lyread/backend/api/seo_page.py` |
| 案例 seed | `lyread/scripts/seed_showcase_cases.sh` |
| 运维巡检 | `lyread/scripts/ops_audit.sh` |
| 部署 | `lyread/scripts/deploy.sh` |

### 本轮交付物（必含）

1. **简评表**（100 分制 + 与上轮对比，若无历史则给基线）
2. **本轮完成项**（做了什么、为什么、影响哪条漏斗）
3. **PR 链接**（draft 即可）与分支名
4. **生产验证结果**（ops_audit 摘要或 curl 证据）
5. **下一轮建议**（1～3 条，标明 P0–P4）

### 禁止事项

- 不要一次改 10+  unrelated 文件
- 不要删除已有 SEO/转化能力
- 不要未经请求全站换肤
- 不要创建用户未要求的额外 markdown 文档（本 automation 说明除外）

若本轮诊断后无需改代码（一切健康），仍须输出简评 + 监控结论，并 propose 一条最小的 P2/P3 体验 polish 供用户确认。

---

## Automation Prompt（复制到这里结束）

---

## 建议调度

| 频率 | 场景 |
|------|------|
| 每周 2 次 | 常规持续优化 |
| 每次 push main | 回归巡检 + 小修复 |
| 手动 | 大版本发布前全面审计 |

## 环境变量（Cloud Agent Environment 可选）

生产 SSH 与 API 诊断需要网络 egress。Analytics / 支付 / SMTP 密钥由服务器 `/tmp/lyread.env` 管理，勿写入仓库。

## 成功指标（长期跟踪）

- 转化：注册率、试用→创作台到达率
- 阅读：案例页平均阅读时长、`has_body` 案例占比
- 稳定：`ops_audit` 通过率、API P95
- SEO：索引页数、核心词排名（手动或 Search Console）
- 商业：充值转化、点数消耗/生成成功率
