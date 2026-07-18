# esnlink.cn 增长优化部署

翼星科技官网（https://esnlink.cn）P0 增长优化实施包。

## 已部署改动（2026-07-18）

### P0 立即处理
- [x] 首页首屏改版：新价值主张 + 产品控制台视觉 + 双 CTA（免费试用 / 查看定价）
- [x] 导航栏重构：链接至真实产品页（call-center / sms / iot / pricing / blog）
- [x] 新增 `call-center.html` 智能外呼独立 SEO 页面
- [x] 补充全站 `og-image.png`（1200×630 社交分享图）
- [x] 页脚死链修复（`#` → 真实 URL）
- [x] 新增智能呼叫中心产品卡片（首页四大产品矩阵）
- [x] `ai-employees.html` 品牌修正 + noindex
- [x] 博客 21 篇文章文末 CTA 转化卡片
- [x] sitemap 新增 call-center.html

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

## 下一步（P1，30 天内）

1. 各产品页补充 `og:image` 和 Product Schema
2. 建立 `/docs/sms-api.html` API 文档页
3. 客户 Logo 墙（需客户提供授权 Logo）
4. 百度/360 站长平台提交更新后的 sitemap
5. `booking.html` canonical 从 yixing.tech 改为 esnlink.cn

## 增长诊断报告

完整 10 维度商业增长诊断见 PR 描述。
