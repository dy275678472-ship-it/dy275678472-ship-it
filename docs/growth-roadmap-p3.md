# 增长路线图 P3 — zhenxi.hk.cn & cosgo.cn

> P0（SEO 基建）✅ · P1（安全 + 转化基建）✅ · P2（性能 + 内容计划）进行中
> 本文档定义 P3 阶段的中期增长与商业化路径。

---

## P3 总览

| 维度 | P3 目标 | 预期影响 |
|------|---------|----------|
| 流量 | 有机流量 +50%（90 天） | 搜索 + 社交复利 |
| 转化 | 测评 → 邮件 15% 转化 | 可触达用户池 |
| 收入 | 月均 ¥3,000+ 多元化 | 打赏 + 导流 + 合作 |
| 基建 | Cloudflare + 邮件 + 埋点 | 可度量、可扩展 |
| 服务器 | 内存升级或 Hermes 隔离 | Swap < 500MB |

---

## P3-A：基础设施（第 1–2 周）

### A1. Cloudflare CDN

**现状**：DNS 直解析首尔 `43.128.145.79`，无边缘缓存。

**动作**：
1. 将 `zhenxi.hk.cn`、`cosgo.cn` DNS 迁入 Cloudflare（橙云代理）
2. 开启 Brotli、Auto Minify、HTTP/3
3. Page Rules / Cache Rules：
   - `/_next/static/*` → Cache Everything, 1 year
   - `/*.png|jpg|webp` → Cache 7 days
   - HTML → Bypass 或 1h edge cache
4. 保留源站 nginx 作为 fallback（已配置 long-cache headers）

**验收**：`cf-cache-status: HIT` 在静态资源响应头出现；国内 TTFB 下降 30%+

### A2. 邮件收集系统

**现状**：测评完成无留资；contact 表单无人工回复。

**动作**：
1. 接入 Resend 或 SendGrid（测评结果页 + 博客文末）
2. 字段：邮箱 + 可选昵称；双 opt-in
3. 自动发送「你的疗愈报告」PDF/邮件摘要
4. 存储：现有 PostgreSQL 或新增 `subscribers` 表

**验收**：测评完成 → 邮件送达率 > 95%

### A3. 分析埋点完善

**动作**：
1. Umami 自定义事件：`assessment_complete`、`cta_click`、`blog_read_50pct`
2. GSC + Umami 周报自动化（cron + 邮件摘要）
3. 转化漏斗看板：首页 → 测评 → 邮件 → 打赏

---

## P3-B：内容 & SEO 深化（第 3–6 周）

### B1. 博客体系统一

- 博客列表 14 篇 ↔ slug 页 22 篇对齐
- 每篇文末统一 CTA 组件（测评 + 相关指南）
- 内链矩阵：指南 ↔ 博客 ↔ 城市 ↔ 测评

### B2. 结构化数据扩展

- 博客文章 `Article` schema（author, datePublished, image）
- 测评 `Quiz` / `HowTo` schema
- FAQ schema 加到 assessment、services 页

### B3. 多语言评估（可选）

- 若海外流量 > 5%：恢复 `/en` 并真正落地英文首页
- 否则保持单语言，避免 hreflang 陷阱

### B4. 执行 [30 天内容计划](./zhenxi-content-plan-30d.md)

- 按周 SOP 推进，D14 / D28 复盘

---

## P3-C：商业化（第 4–8 周）

### C1. 收入流矩阵

| 流 | 现状 | P3 目标 |
|----|------|---------|
| 爱发电打赏 | 有入口 | 优化文案 + 测评后引导 |
| 疗愈空间导流 | partners 页空 | 签约 3–5 家，CPS 分成 |
| 数字产品 | 无 | 睡眠/正念 PDF 指南 ¥19–49 |
| 企业合作 | 无 | 女性健康/HR wellness 内容授权 |

### C2. cosgo.cn 协同

- 漫展季流量 → zhenxi 女性用户交叉（banner 互推）
- 共享 IndexNow / CDN 配置
- 统一 tracker 与 Umami 项目

### C3. 付费测评增值（轻量）

- 免费：基础报告
- 付费（¥9.9）：详细报告 + 7 天邮件陪伴系列

---

## P3-D：服务器 & 运维（并行）

### D1. 内存 / Swap 根治

**现状**：3.6G RAM，Swap 2.1G/3.9G；Hermes agent ~500MB swap，MySQL ~380MB swap。

**选项**（按成本排序）：
1. **腾讯云升配** → 8G RAM（推荐，~¥50–80/月增量）
2. **Hermes 迁出** → 独立轻量实例或上海节点
3. **MySQL 调优** → `innodb_buffer_pool_size` 降至 256M（当前机器）
4. **swappiness=10** → ✅ P2 已执行，缓解但不根治

### D2. 多区域 CDN 替代自建边缘

- 评估是否仍需曼谷/弗吉尼亚 nginx 边缘代理
- Cloudflare 全球 PoP 可能简化 `www.zhenxi.hk.cn` 分流

### D3. 备份 & 监控

- 每日 `pg_dump` + `mysqldump` 到对象存储
- Uptime Kuma 或腾讯云监控告警
- 磁盘 > 80% 自动告警

---

## P3 优先级排序

```
P3-1  Cloudflare CDN          ← 最大性能/成本比，需 DNS 权限
P3-2  测评邮件收集            ← 最大转化杠杆
P3-3  博客 CTA + 列表对齐     ← SEO + 转化
P3-4  服务器升配 8G           ← 稳定性
P3-5  结构化数据扩展
P3-6  数字产品 / 付费报告
P3-7  Hermes 迁出
P3-8  英文版评估
```

---

## 里程碑验收（90 天）

| 里程碑 | 日期 | 验收标准 |
|--------|------|----------|
| M1 CDN 上线 | +2 周 | cf-cache-status HIT，TTFB < 200ms（国内主要城市） |
| M2 邮件系统 | +3 周 | 100+ 订阅，送达率 > 95% |
| M3 内容 30 天 | +4 周 | 8 篇新/翻新文，GSC 点击 +30% |
| M4 首笔导流收入 | +8 周 | partners 导流或数字产品首单 |
| M5 服务器稳定 | +6 周 | Swap < 500MB，无 OOM |

---

## 需要你的决策

1. **DNS 权限**：是否可将 zhenxi.hk.cn / cosgo.cn 迁入 Cloudflare？
2. **邮件服务商**：Resend / SendGrid / 腾讯企业邮？
3. **服务器升配**：是否批准 3.6G → 8G 升配？
4. **Hermes**：是否可迁出首尔节点或限制运行时段？
5. **付费测评**：是否接受 ¥9.9 轻付费模式？

确认后即可按 P3-1 → P3-2 顺序执行。
