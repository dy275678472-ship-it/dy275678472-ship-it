# esnlink.cn 增长优化部署

翼星科技官网（https://esnlink.cn）P0 增长优化实施包。

## 已部署改动（2026-07-18）

### P0（已完成）
- 首页首屏改版、导航/页脚修复、call-center.html、og-image、博客 CTA

### P1（已完成）
- [x] `booking.html` canonical/og 修正为 esnlink.cn
- [x] 新建 `/docs/` 文档中心 + `/docs/sms-api.html` 短信 API 文档
- [x] 新建行业方案页：教育 / 电商 / 金融
- [x] 产品页（sms/iot/edu）补充 og:image + Product/FAQ Schema + 统一导航
- [x] 产品页增加「相关资源」内链区块
- [x] sitemap 新增 6 个 URL

### P2（已完成）
- [x] `robots.txt` 屏蔽 `/seo/` + nginx `X-Robots-Tag: noindex`
- [x] nginx gzip + 静态资源缓存
- [x] `/cases/` 案例中心 + 首页案例可点击
- [x] Logo 信任墙升级（8 行业）
- [x] 英文版 `/en/`（首页 + SMS + Call Center，hreflang）
- [x] 广告落地页 `/landing/sms.html`
- [x] `og-image.webp` 生成

### 文件结构

```
esnlink-deploy/
├── site/
│   ├── index.html, call-center.html, ...
│   ├── docs/, solutions/, cases/, en/, landing/
│   ├── robots.txt, sitemap.xml, og-image.png/webp
├── nginx/                  # gzip + 缓存 + seo noindex
├── deploy.sh
└── generate_*.py
```

## 部署

```bash
bash esnlink-deploy/deploy.sh
```

服务器：`150.158.42.39` → `/var/www/yixing/`

## 下一步（P3，可选）

1. 真实客户 Logo 图片替换 emoji 占位
2. 百度/360 站长平台手动提交 sitemap
3. 落地页 A/B 测试
4. 腾讯云 CDN 域名接入

## 增长诊断报告

完整 10 维度商业增长诊断见 PR 描述。
