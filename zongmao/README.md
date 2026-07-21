# 宗贸网 (zongmao.cn) 运维工具

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
