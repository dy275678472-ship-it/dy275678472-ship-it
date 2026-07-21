# 宗贸网 (zongmao.cn) 运维工具

## P0 增长修复

```bash
# 在服务器上
sudo python3 /opt/zongmao/scripts/p0-patch.py
sudo systemctl restart zongmao.service
sudo nginx -t && sudo systemctl reload nginx
```

### P0 包含项

1. 首页 KPI 服务端渲染（不再显示 `-`）
2. 去除「历史胜率40%」硬编码，改为「历史战绩公开可查」
3. `/pricing` → `/premium` 301 重定向
4. HEAD 请求 405 修复
5. Sitemap 信号页从 330 个低质 URL 精简为 102 个（34 品种 × 3 方向）
6. 信号 AI 文案修复（动力煤不再写 OPEC+）+ 同日去重
