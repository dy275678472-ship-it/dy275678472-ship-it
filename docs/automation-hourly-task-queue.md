# 双站每小时自动化 · 任务清单（基于 2026-07-20 现状）

> 配合 `docs/automation-dual-site-growth.md` 使用。  
> **频率**：每小时 1 次（Cron `0 * * * *` UTC，即每小时整点）  
> **原则**：每小时 = **必做巡检（两站）** + **1 项主任务（按槽位轮换）**；无改动则只出巡检报告，不强行改代码。

---

## 一、现状摘要（任务编排依据）

### 中科国瓷 kdgc.cc — 已就绪 / 待做

| 状态 | 项 |
|------|-----|
| ✅ 已放行 | 导航、13 篇知识库、4 案例、联系地图、Logo 中科国瓷/KDGC、§15 通过 |
| ⚠️ 风险 | CMS↔静态双轨；Logo/占位页部署漂移；`/admin/` 无 nginx 限制 |
| 🔜 P1  backlog | 部署漂移校验脚本、选型落地页、downloads 中心、知识库扩写、转化事件追踪 |
| 🔜 P2  backlog | 英文全文、technology/applications 扩页、PDF 规格书、社媒发布 |

### esnlink.cn — 已就绪 / 待做

| 状态 | 项 |
|------|-----|
| ✅ P0–P2 完成 | 首页改版、docs/solutions/cases/en/landing、nginx 性能、/seo/ noindex |
| ⚠️ 风险 | 博客/内页顶栏偶发不一致；booking canonical；磁盘 75% |
| 🔜 P3  backlog | 真实客户 Logo、CDN、A/B 落地页、站长平台提交、博客持续更新 |

---

## 二、每小时必做巡检（两站，约 5–10 分钟）

每次运行**必须先做**，不通过则本小时主任务改为「修复 P0」：

```
[ ] KDGC 首页 HTTP 200，title 含「中科国瓷」，导航含「首页」「行业案例」
[ ] KDGC Logo：alt=中科国瓷，版本 query 与仓库一致，MD5 线上=本地
[ ] KDGC /knowledge/ title ≠「建设规划」；/cases/ ≠「建设方案」
[ ] KDGC /api/health status=ok；/contact/ 含地图坐标 117.12885,31.83560
[ ] esnlink 首页 HTTP 200，canonical 含 esnlink.cn
[ ] esnlink /booking.html canonical=esnlink.cn
[ ] esnlink /seo/ 返回 noindex（X-Robots-Tag 或 meta）
[ ] 服务器磁盘 df -h / 使用率 <85%（>85% 则报告告警，清理日志/旧包）
```

**巡检命令包**（Agent 可直接跑）：

```bash
BASE_K=http://150.158.42.39
curl -sf "$BASE_K/api/health" | grep -q '"status":"ok"' && echo KDGC-API:OK
curl -sfL "$BASE_K/" | grep -q 'alt="中科国瓷"' && echo KDGC-LOGO:OK
curl -sfL "$BASE_K/knowledge/" | grep -q '知识库 — 中科国瓷' && echo KDGC-KB:OK
curl -sfL https://esnlink.cn/ | grep -q 'esnlink.cn' && echo ESN-HOME:OK
curl -sfI https://esnlink.cn/seo/ | grep -qi noindex && echo ESN-SEO-BLOCK:OK
```

---

## 三、24 小时主任务槽位（循环队列）

**槽位号** = `当前 UTC 小时 (0–23)`。每轮只执行**当前槽位** 1 项；完成后在报告里标记，重复轮次时可做下一优先级或加深。

| 槽位 (UTC) | 北京时间 | 站点 | 主任务 | 验收标准 |
|:---:|:---:|:---|:---|:---|
| **0** | 08:00 | 双站 | 全量巡检 + 写 hourly-log | 报告含 8 项巡检 PASS/FAIL |
| **1** | 09:00 | KDGC | **部署漂移校验脚本** `scripts/verify_deploy.py` | 失败时 exit 1；检查 title/logo MD5 |
| **2** | 10:00 | KDGC | 扩写 1 篇知识库短文（<800字优先） | 单篇 +300 字以上，regenerate+deploy |
| **3** | 11:00 | KDGC | 产品页 title/description SEO 优化 1 款 | 含型号+场景+中科国瓷 |
| **4** | 12:00 | KDGC | 内链：1 篇知识库补「相关产品+案例」 | 文内 ≥2 内链 |
| **5** | 13:00 | esnlink | **unify_chrome 回归**：抽 3 页比对首页 nav | 不一致则 fix+deploy |
| **6** | 14:00 | esnlink | 博客列表 + 1 篇详情 CTA/canonical 检查 | booking 链接可达 |
| **7** | 15:00 | esnlink | sitemap.xml 与实页对齐 | 无 404 URL |
| **8** | 16:00 | esnlink | /en/ 1 页 hreflang/meta 检查或补全 | link rel=alternate 成对 |
| **9** | 17:00 | KDGC | **新建 `/solutions/selection.html` 或推进** | 页面可访问+进 sitemap |
| **10** | 18:00 | KDGC | FAQ 或 Product Schema 补 1 处 | 结构化数据 validator 无致命错 |
| **11** | 19:00 | 双站 | 全站图片引用扫描（HTML→文件存在） | missing=0 |
| **12** | 20:00 | KDGC | 首页/新闻：团建降权或补 1 条技术向摘要 | 首页新闻区检查 |
| **13** | 21:00 | KDGC | 联系页/表单：线索 API 试投 + 预填参数测 | POST /api/leads 成功 |
| **14** | 22:00 | KDGC | admin 后台：静态同步文档或 Case 字段对齐 | 文档或模型 1 处改进 |
| **15** | 23:00 | esnlink | /docs/ 补 1 段 API 说明或 FAQ | 新内容可索引 |
| **16** | 00:00 | esnlink | /cases/ 1 个案例摘要/封面优化 | 案例页可点击完整 |
| **17** | 01:00 | esnlink | /landing/sms.html CTA 与表单链检查 | 转化路径无断链 |
| **18** | 02:00 | esnlink | og-image/webp 生成脚本跑一遍 | 资源时间戳更新 |
| **19** | 03:00 | KDGC | 英文站 1 页（产品或知识摘要）补强 | /en/ 可访问 |
| **20** | 04:00 | KDGC | `/technology/` 或 `/applications/` 扩 1 段+内链 | 非薄页 |
| **21** | 05:00 | 双站 | 生成「站长提交包」：sitemap URL 列表 | markdown 报告，不自动提交 |
| **22** | 06:00 | KDGC | 社媒草稿→站内 1 条（知乎/公众号摘要链知识库） | 1 处内链新增 |
| **23** | 07:00 | 双站 | **队列复盘**：更新 backlog 优先级 + hourly-log | 下 24h 建议 3 条 |

---

## 四、P0 插队规则（任意小时优先）

巡检 FAIL 时，**取消原槽位**，改为：

| 故障 | 动作 |
|------|------|
| KDGC Logo 错/AVIC | 立即 `generate_logos.py` + 全站 cache-bust + deploy |
| KDGC 知识库/案例变占位页 | `generate_pages.py` + 全量 dist deploy |
| KDGC API down | 查 uvicorn/systemd，重启 kdgc-backend |
| esnlink nav 分裂 | `unify_chrome.py` + `deploy.sh` |
| esnlink canonical 错域 | 修正 booking/产品页 + deploy |
| 磁盘 >90% | 清理 /tmp、旧 tar、nginx log |

---

## 五、每小时交付标准（DoD）

1. 巡检 8 项有 PASS/FAIL 记录  
2. 执行了当前槽位主任务 **或** P0 修复 **或** 明确「槽位已完成，本轮跳过」  
3. 有代码改动 → commit + push + deploy + 验证 URL  
4. 追加一行到 `docs/automation-hourly-log.md`（见下节模板）  
5. 报告 ≤30 行，不堆砌废话  

---

## 六、运行日志模板

追加到 `docs/automation-hourly-log.md`：

```markdown
## 2026-07-20 15:00 UTC · 槽位 15 · esnlink
- 巡检：KDGC 8/8 PASS · esnlink 7/8 FAIL（booking canonical 缺）
- 主任务：docs 补 FAQ 段 — 跳过，先修 P0 canonical
- 部署：是 · commit abc1234
- 下轮：槽位 16 cases 优化
```

---

## 七、Cursor Automation 创建参数

| 字段 | 值 |
|------|-----|
| Name | `双站每小时巡检+优化（KDGC+esnlink）` |
| Schedule | Cron **`0 * * * *`**（每小时整点 UTC） |
| Repository | `dy275678472-ship-it` |
| Instructions | 见 `automation-dual-site-growth.md` **第二节「 hourly 版 Prompt」** |
| Environment | 网络 egress + SSH 密钥 |

---

## 八、Backlog 总量（按站点，供槽位完成后接棒）

### 中科国瓷 — 按 ROI 排序

1. `scripts/verify_deploy.py` 部署漂移校验（槽位 1）
2. `/solutions/selection.html` 选型页（槽位 9）
3. `/downloads/` 规格书中心（槽位 9 完成后）
4. 知识库 13→20 篇扩写（槽位 2 循环）
5. 生产 `ADMIN_TOKEN` + CORS + `/admin/` nginx 限制（槽位 14）
6. 转化事件 gtag/dataLayer（槽位 13 延伸）
7. 英文知识库全文（槽位 19 循环）
8. 百度/谷歌 sitemap 人工提交包（槽位 21，人工执行）

### esnlink — 按 ROI 排序

1. unify_chrome 每周全站回归（槽位 5 循环）
2. 博客 SEO + CTA 统一（槽位 6 循环）
3. 真实客户 Logo 替换 SVG 占位（需素材，Agent 仅准备占位规范）
4. 腾讯云 CDN 接入文档（人工）
5. 落地页 A/B 第二版（槽位 17 延伸）
6. 360/百度站长验证与提交（槽位 21，人工）

---

*队列版本：2026-07-20 · 与 site-audit-results 放行状态对齐*
