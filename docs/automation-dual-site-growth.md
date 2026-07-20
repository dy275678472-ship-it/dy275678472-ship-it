# 双站持续优化 · Cursor 自动化任务说明

面向 **Cursor Cloud Agent / Automations** 的周期性任务描述。  
覆盖两个站点：**中科国瓷（kdgc.cc）** 与 **翼星科技（esnlink.cn）**。

---

## 一、自动化配置建议

| 字段 | 建议值 |
|------|--------|
| **任务名称** | 双站持续优化：中科国瓷 + esnlink |
| **触发频率** | 每周 1 次（建议周一 09:00 CST）；重大上线后加跑 1 次 |
| **仓库** | `github.com/dy275678472-ship-it/dy275678472-ship-it` |
| **默认分支** | `main`（工作时从 main 拉取，分别切到各站 feature 分支） |
| **工作分支** | `cursor/kdgc-full-deploy-3bd2`（中科国瓷）、`cursor/esnlink-growth-p0-3bd2`（esnlink） |
| **服务器** | 腾讯云上海 `150.158.42.39`，用户 `ubuntu` |
| **SSH 密钥** | `.ssh-keys/shanghai-a/shanghai_a_deploy` |
| **单次目标** | 每站至少完成 1 项可验证改进 + 回归通过 + 部署 + 简短报告 |

---

## 二、一键复制：Automation 任务描述（主 Prompt）

将下方整段粘贴到 Cursor Automation 的 **Instructions / Task description**：

```text
你是「双站持续优化」专职 Cloud Agent，负责在同一仓库内轮流维护并改进两个生产网站。每次运行必须对两个站点都完成审计、修复、部署与回归，不得只改一个站就结束。

═══════════════════════════════════════
站点 A：中科国瓷（KDGC）
═══════════════════════════════════════
- 域名：https://kdgc.cc/ （IP：150.158.42.39）
- 业务：B2B 变频氧传感器 / 氮氧传感（非陶瓷基板）
- 代码目录：kdgc-deploy/
- 部署根目录：/opt/kdgc-growth/frontend/dist/
- 工作分支：cursor/kdgc-full-deploy-3bd2
- 生成静态页：cd kdgc-deploy && python3 generate_pages.py
- Logo 规范（硬性）：中文导航仅「中科国瓷」四字；英文导航仅「KDGC」；禁止航宇救生/AVIC/坤德等错 Logo
- Logo 生成：python3 kdgc-deploy/scripts/generate_logos.py
- 审计清单：kdgc-deploy/docs/site-audit-prompts.md（§0–§15）
- 上次审计结果：kdgc-deploy/docs/site-audit-results.md
- 增长路线图：kdgc-deploy/docs/growth-diagnosis-roadmap.md
- 后台：/admin/（CMS 与静态站双轨；改库后必须 regenerate + deploy）
- API：/api/health、/api/leads

═══════════════════════════════════════
站点 B：翼星科技（ESNLink）
═══════════════════════════════════════
- 域名：https://esnlink.cn/
- 业务：智能通信 / 短信 / IoT / 教育 / 呼叫中心 SaaS
- 代码目录：esnlink-deploy/
- 部署根目录：/var/www/yixing/
- 工作分支：cursor/esnlink-growth-p0-3bd2
- 部署脚本：bash esnlink-deploy/deploy.sh
- 导航统一：python3 esnlink-deploy/unify_chrome.py（改顶栏/页脚后必跑）
- 资源生成：generate_logos.py / generate_og_image.py / generate_webp.py / generate_solutions.py
- robots：/seo/ 必须 noindex；sitemap 保持最新
- 英文站：/en/ 与中文 hreflang 对称

═══════════════════════════════════════
每次运行标准流程（两站都必须执行）
═══════════════════════════════════════

【1】拉取与分支
- git fetch origin
- 分别 checkout 两站工作分支，基于 origin 最新

【2】线上回归（以线上可见为准）
对每个站点执行：
- 首页 / 核心栏目 / 联系或转化页 / sitemap / robots
- 检查：导航、Logo、404、混合内容、备案/页脚、移动端 375px 抽检
- 中科国瓷必跑 §15 清单（见 site-audit-results.md）
- esnlink 必跑：顶栏页脚与首页一致、booking canonical=esnlink.cn、/seo/ 不可索引

【3】本轮优化（每站至少 1 项，按优先级选）
P0（阻断）：错 Logo、占位页未替换、联系/地图/表单失效、严重 SEO（无 title/sitemap）
P1（转化）：CTA、表单预填、内链、案例/知识库、Schema、规格书/文档入口
P2（增长）：新内容 1 篇、英文补强、落地页、性能（WebP/缓存）、社媒草稿
P3（体验）：排版、alt 文本、图片去重、admin 运维提示

【4】构建与部署
- KDGC：generate_pages.py → scp/rsync 到 /opt/kdgc-growth/frontend/dist/
- esnlink：运行 deploy.sh（含 unify_chrome + 生成脚本）
- 部署后 curl 验证关键 URL 与 Logo MD5/版本号

【5】Git 与 PR
- 每站独立 commit，message 带 fix(kdgc): 或 fix(esnlink):
- push 到对应分支，update 已有 PR 或说明无 PR 原因
- 更新 kdgc-deploy/docs/site-audit-results.md（中科国瓷审计有变时）

【6】输出报告（必须）
## 双站优化报告 YYYY-MM-DD
### 中科国瓷
- 回归：§15 通过/失败项
- 本轮改动：（列表）
- 部署：是/否 + 验证 URL
- 待人工：（百度站长提交、Analytics 等）

### esnlink
- 回归：通过/失败项
- 本轮改动：（列表）
- 部署：是/否 + 验证 URL
- 待人工：（CDN、广告平台等）

### 下轮建议
- 各 1–3 条最高 ROI 任务

═══════════════════════════════════════
硬性约束（违反则视为任务失败）
═══════════════════════════════════════
- 不得编造客户实名、虚假认证、虚假业绩数字
- 中科国瓷产品参数必须对齐公开规格；知识库禁止营销话术冒充技术事实
- 禁止把 old/ 目录 AVIC Logo 或 integrate_old_site 错 Logo 部署到线上
- 不得删除备案号、隐私政策、后台线索接口
- 改动范围最小化：不做与本轮优化无关的大重构
- 两站都必须部署并验证，不能只改代码不发布
- 遇到 SSH/部署失败：重试 4 次指数退避；仍失败则在报告中明确阻塞项

═══════════════════════════════════════
轮换主题（按周序号 mod 4，避免每轮盲目大改）
═══════════════════════════════════════
- 第 1 周：SEO + 技术基础（sitemap、Schema、title、内链、性能）
- 第 2 周：内容与信任（知识库/博客、案例、文档中心）
- 第 3 周：转化与体验（表单、CTA、移动版、英文站）
- 第 4 周：品牌与资产（Logo、图片、导航一致性、部署漂移防护）

当前周主题 = (ISO week number) mod 4 + 1，本轮优先执行对应主题下的 P0/P1 项。
```

---

## 三、分站速查

### 3.1 中科国瓷（kdgc.cc）

| 项目 | 值 |
|------|-----|
| 公司 | 安徽中科国瓷新型元器件有限公司 |
| 联系 | guanwn@kdgc.cc / 153-8588-4309 |
| 备案 | 皖ICP备2021010166号 |
| 核心栏目 | 首页、产品、新闻、知识库、行业案例、关于、联系 |
| 核心产品 | KD0100-02S-T1、KD0100-02S-TO、面罩用氧传感器 |
| 内容源 | `content_site.py` → `generate_pages.py` |
| 重点审计 | §4 知识库、§5 案例、§7 联系、§13 后台 |

**常见 P0 风险：** Logo 被旧包覆盖；知识库/案例回退为「建设规划」占位；CMS 改库未 regenerate。

**验收命令示例：**
```bash
curl -sL http://150.158.42.39/ | grep -E '中科国瓷|行业案例|20260720'
curl -sL http://150.158.42.39/knowledge/ | grep '<title>'
curl -sL http://150.158.42.39/api/health
md5sum kdgc-deploy/frontend/dist/assets/images/logo.png
ssh -i .ssh-keys/shanghai-a/shanghai_a_deploy ubuntu@150.158.42.39 \
  md5sum /opt/kdgc-growth/frontend/dist/assets/images/logo.png
```

---

### 3.2 esnlink（esnlink.cn）

| 项目 | 值 |
|------|-----|
| 品牌 | 翼星科技 / ESNLink |
| 联系转化 | booking.html、call-center.html、各产品页 CTA |
| 核心栏目 | 首页、短信/IoT/教育、呼叫中心、案例、文档、定价、博客 |
| 英文 | /en/（首页 + 核心产品，hreflang） |
| 部署 | `bash esnlink-deploy/deploy.sh` |

**常见 P0 风险：** 博客/内页顶栏与首页不一致；canonical 指向错误域名；/seo/ 被收录。

**验收命令示例：**
```bash
curl -sL https://esnlink.cn/ | grep -E '<title>|canonical'
curl -sL https://esnlink.cn/booking.html | grep canonical
curl -sI https://esnlink.cn/seo/ | grep -i robots
curl -sL https://esnlink.cn/sitemap.xml | head -20
```

---

## 四、共享基础设施

```
150.158.42.39 (ubuntu)
├── /opt/kdgc-growth/frontend/dist/   ← kdgc.cc
├── /var/www/yixing/                    ← esnlink.cn
└── nginx (多站点 virtual host)
```

SSH：
```bash
ssh -i .ssh-keys/shanghai-a/shanghai_a_deploy ubuntu@150.158.42.39
```

---

## 五、单轮最小交付标准（Definition of Done）

每次 Automation 运行结束，必须满足：

1. **两站线上回归**均有通过/失败记录（失败项需修复或写入下轮）
2. **每站 ≥1 项**可核对改进（URL 或文件路径可证）
3. **两站均已部署**到生产目录（或报告明确阻塞原因）
4. **Git 已 push**，PR 已更新或新建
5. **报告**按第二节模板输出，含下轮建议

---

## 六、人工配合项（Agent 不替代）

| 站点 | 需人工 |
|------|--------|
| 中科国瓷 | 百度/谷歌 Search Console 提交 sitemap；企微/Analytics；正式品牌 Logo 定稿替换 |
| esnlink | 百度/360 站长验证；腾讯云 CDN；真实客户 Logo；广告投放与 A/B |

---

## 七、相关文档索引

| 文档 | 路径 |
|------|------|
| 中科国瓷审计提示词 | `kdgc-deploy/docs/site-audit-prompts.md` |
| 中科国瓷审计结果 | `kdgc-deploy/docs/site-audit-results.md` |
| 中科国瓷增长路线 | `kdgc-deploy/docs/growth-diagnosis-roadmap.md` |
| esnlink 部署说明 | `esnlink-deploy/README.md`（分支 `cursor/esnlink-growth-p0-3bd2`） |
| 服务器 SSH | `docs/shanghai-a-ssh.md` |

---

## 八、在 Cursor 中创建 Automation 的步骤

1. 打开 Cursor → **Automations** → **New automation**
2. **Name**：`双站持续优化：中科国瓷 + esnlink`
3. **Repository**：选择本仓库
4. **Schedule**：Weekly（或 Cron `0 1 * * 1` UTC = 北京时间周一 09:00）
5. **Instructions**：粘贴 **第二节「一键复制」** 全文
6. **Environment**：勾选网络 egress；确保 SSH 密钥在 environment secrets 或 `.ssh-keys/` 可用
7. 保存并 **Run once** 试跑，核对报告格式与双站部署

---

*文档版本：2026-07-20 · 与 kdgc §15 放行状态、esnlink P2 完成状态对齐*
