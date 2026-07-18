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

### 文件结构

```
esnlink-deploy/
├── site/
│   ├── index.html          # 首页（首屏+导航+页脚）
│   ├── call-center.html    # 智能外呼产品页
│   ├── og-image.png        # 社交分享图
│   └── sitemap.xml         # 站点地图
├── css/
│   └── header-footer.css   # 共享导航/页脚样式
├── deploy.sh               # 一键部署脚本
├── generate_og_image.py    # 生成 og-image
└── patch_blog_cta.py       # 博客 CTA 批量注入
```

## 部署

```bash
bash esnlink-deploy/deploy.sh
```

服务器：`150.158.42.39` → `/var/www/yixing/`

## 下一步（P2，90 天内）

1. 客户 Logo 墙（需客户提供授权 Logo）
2. 百度/360 站长平台提交 sitemap
3. `/seo/` 2800 页质量审核
4. CDN 接入 + 图片 WebP 优化
5. 英文版 `/en/` 页面

## 增长诊断报告

完整 10 维度商业增长诊断见 PR 描述。
