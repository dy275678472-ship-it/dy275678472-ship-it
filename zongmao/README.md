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
