# 宗贸网 (zongmao.cn) 运维工具

## 商业化 P0（注册转化）

```bash
sudo bash /opt/zongmao/scripts/deploy-p0-convert.sh
# 或
sudo python3 /opt/zongmao/scripts/p0-convert-patch.py
sudo systemctl restart zongmao.service
```

### 商业化 P0 包含项

1. 首页 sparkline API 修复（`/api/symbol/{sym}/sparkline` 404 → 200）
2. 登录/注册设置 `user_id` cookie（支付/激活码绑定）
3. 百度统计动态注入（`site_config.json` → `baidu_hm_id`，60s 热加载）
4. 注册页简化（仅手机号+密码，加载态，权益说明）
5. 信号页游客门控（前 3 条可见，其余模糊+注册 CTA）
6. 获客弹窗改为注册引导（20s，已登录跳过）
7. 首页底部 sticky 注册条（滚动后出现）
8. 会员页支付绑定真实 user_id（不再 guest_ 随机）
9. 管理后台 monetize API 鉴权修复

**接入百度统计：** 编辑 `/opt/zongmao/site_config.json` 填入 `baidu_hm_id`（在百度统计后台创建 zongmao.cn 站点后获取）

## 产品验证（当前阶段，P1 暂缓）

```bash
sudo bash /opt/zongmao/scripts/deploy-validation.sh
# 手动生成报告
sudo python3 /opt/zongmao/scripts/product-validation-report.py
# 报告路径: /var/log/zongmao/validation-latest.txt
# 管理后台 API: GET /api/admin/validation（需 admin 登录）
```

### 验证假设 & 成功标准（14 天）

| 假设 | 验证方式 | 成功标准 |
|------|----------|----------|
| H1 交易者愿意为 AI 信号注册 | UV→注册转化率 | ≥2%，周新增 ≥3 |
| H2 模拟赛是有效钩子 | 注册后访问 /trading-contest | 参与率 ≥40% |
| H3 SEO 带来目标流量 | 信号/新闻页入口占比 | 非首页流量 >30% |

### 埋点事件

- `register_view` / `register_submit` / `register_success`
- `cta_sticky` / `cta_signals_banner` / `cta_signals_gate`

## P0 增长修复

```bash
# 在服务器上
sudo python3 /opt/zongmao/scripts/p0-patch.py
sudo systemctl restart zongmao.service
sudo nginx -t && sudo systemctl reload nginx
```

### P1 包含项

1. 新增页面：`/methodology` `/compare` `/welcome` `/tutorial`
2. 资讯页 Article Schema + 相关品种信号内链
3. 34 品种页底部注册 CTA
4. 注册页 SEO + 注册后跳转 `/welcome` 引导
5. 会员页战绩信任条（SSR KPI）
6. Sitemap 卡片页 2000→300；robots 屏蔽 `/cards/`
7. Cron：百度推送 + 资讯生成 + 信号生成

## P2 爬取预算与性能

```bash
sudo python3 /opt/zongmao/scripts/p2-patch.py
sudo systemctl restart zongmao.service
sudo nginx -t && sudo systemctl reload nginx
```

### P2 包含项

1. Sitemap 瘦身：移除 `/cards/*` `/asset/*`；信号页仅收录有活跃信号的 URL；新闻限 500 篇
2. 薄页 noindex：`/cards/*`、非标准 `/asset/*`、无内容的 `/signal/*`
3. `/asset/{name}` → `/price/{symbol}` 301 重定向（标准品种）
4. 信号页展示活跃 `trade_signals`（修复 symbol/中文名不匹配）
5. 品类落地页 `/category/{能源|黑色|有色|化工|农产品}`
6. Nginx 安全头：HSTS、Referrer-Policy、Permissions-Policy
7. 百度统计配置：`/opt/zongmao/site_config.json` 设置 `baidu_hm_id`

## SEO/GEO P0

```bash
sudo python3 /opt/zongmao/scripts/p0-seo-patch.py
sudo systemctl restart zongmao.service
```

### SEO P0 包含项

1. 域名统一：`www.zongmao.cn` → `zongmao.cn` 301；百度推送改用裸域
2. `/performance` 战绩 KPI SSR + Dataset Schema（GEO 可引用）
3. `/llms.txt` AI 爬虫指引文件
4. 百度推送策略：改推 news/price/signal/信任页（不再推 cards/asset）

## SEO/GEO P1

```bash
sudo python3 /opt/zongmao/scripts/p1-seo-patch.py
sudo systemctl restart zongmao.service
```

### SEO P1 包含项

1. BreadcrumbList Schema：品种页、资讯页、信号页、品类页
2. Organization Schema 增强（首页含 contactPoint）
3. 34 品种独立 OG SVG 图（`/static/images/og/{symbol}.svg`）
4. 资讯作者统一为「宗贸网研究院」（DB + Schema）
5. Article Schema 增强：publisher logo、articleSection、dateModified
6. 全站 footer 内链：方法论 / 对比 / 教程
7. 品种页走势图 `aria-label` 无障碍

## SEO/GEO P2

```bash
sudo python3 /opt/zongmao/scripts/p2-seo-patch.py
sudo systemctl restart zongmao.service
```

### SEO P2 包含项

1. `/glossary` 期货术语词典（50 词 + FAQPage Schema）
2. `/stats/2026` 年度信号年报（SSR 战绩 + 板块/月度/品种分解）
3. `/compare` 留资表单（手机号 → lead_captures）
4. `gen_news.py` 资讯末尾结构化块（行情速览表 + AI 信号观点）
5. `llms.txt` / sitemap 更新
