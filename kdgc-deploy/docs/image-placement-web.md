# 中科国瓷 · AI 生图挂载规划（Web 格式）

> 目标：每张图有固定路径、用途、尺寸与页面位置；入库后转 **WebP**（产品白底保留 PNG），页面用 `<picture>` / CSS `background-image` 显示。

## 投放总表

| 编号 | 建议文件名 | Web 路径 | 页面位置 | 尺寸建议 | 格式 |
|------|------------|----------|----------|----------|------|
| 01-01 | `hero-oxygen-sensor.jpg` | `/assets/images/home/hero-oxygen-sensor.webp` | 首页 Hero 背景（右侧重图、左留字） | 1920×1080 | WebP |
| 01-02 | `og-share.jpg` | `/og-image.webp` + `/og-image.png` | 全站 OG/分享 | 1200×630 | WebP+PNG |
| 02-01 | `banner-about.jpg` | `/assets/images/about/banner-about.webp` | 关于页顶 Banner | 1920×640 | WebP |
| 02-02~04 | `team-*-silhouette.jpg` | `/assets/images/about/team-*.webp` | 关于页核心团队旁视觉（可选） | 800×1000 | WebP |
| 02-05~06 | `lab-environment-*.jpg` | `/assets/images/about/lab-*.webp` | 关于页「研发环境」区块 | 1600×900 | WebP |
| 03-01 | `product-kd0100-02s-t1.png` | `/assets/images/products/kd0100-02s-t1.webp` | 产品列表+详情 T1 | 1200×1200 | WebP（白底） |
| 03-02 | `product-kd0100-02s-to.png` | `/assets/images/products/kd0100-02s-to.webp` | 产品列表+详情 TO | 1200×1200 | WebP |
| 03-03 | `product-mask-o2-sensor.png` | `/assets/images/products/mask-o2-sensor.webp` | 面罩传感器 | 1200×1200 | WebP |
| 03-04 | `product-exploded.png` | `/assets/images/products/exploded.webp` | 产品详情「结构示意」 | 1600×1200 | WebP |
| 03-05 | `product-controller-kd0100-03.png` | `/assets/images/products/controller-kd0100-03.webp` | 控制器配套图 | 1200×1200 | WebP |
| 03-06 | `scene-automotive.jpg` | `/assets/images/scenes/automotive.webp` | 首页/应用·车用 | 1600×900 | WebP |
| 03-07 | `scene-aviation-mask.jpg` | `/assets/images/scenes/aviation-mask.webp` | 应用·航空面罩 | 1600×900 | WebP |
| 03-08 | `scene-industrial-gas.jpg` | `/assets/images/scenes/industrial-gas.webp` | 应用·工业气体 | 1600×900 | WebP |
| 03-09 | `products-banner.jpg` | `/assets/images/products/banner.webp` | 产品中心页头 | 1920×640 | WebP |
| 04-01 | `cover-team-building.jpg` | `/assets/images/news/team-building-2022.webp` | 新闻封面·团建 | 1200×675 | WebP |
| 04-02 | `cover-nox-market.jpg` | `/assets/images/news/nox-sensor-market.webp` | 新闻封面·氮氧市场 | 1200×675 | WebP |
| 04-03 | `cover-o2-explain.jpg` | `/assets/images/news/understand-o2-sensor.webp` | 新闻封面·一文读懂 | 1200×675 | WebP |
| 04-04 | `news-banner.jpg` | `/assets/images/news/banner.webp` | 新闻列表页头 | 1920×640 | WebP |
| 05-* | `cover-*.jpg` / `knowledge-banner.jpg` | `/assets/images/knowledge/*` | 知识库封面（正式文上线后） | 1200×675 | WebP |
| 06-* | `case-*.jpg` | `/assets/images/cases/*` | 案例封面（有真实案例后） | 1400×788 | WebP |
| 07-01 | `contact-campus.jpg` | `/assets/images/contact/campus.webp` | 联系页园区实景 | 16:9 | WebP |
| 07-02 | `contact-banner.jpg` | `/assets/images/contact/banner.webp` | 联系页顶 Banner | 1920×640 | WebP |
| 07-03 | `icon-response.png` | `/assets/images/contact/icon-response.webp` | 联系页·快速响应 | 512×512 | WebP/PNG |
| 07-04 | `icon-24h.png` | `/assets/images/contact/icon-24h.webp` | 联系页·7×24 | 512×512 | WebP/PNG |
| 07-05 | `icon-location.png` | `/assets/images/contact/icon-location.webp` | 联系页·地址 | 512×512 | WebP/PNG |
| 07-06 | `wechat-placeholder.png` | 仅占位；正式用现有 `wechat-qr.png` | 微信二维码 | 512×512 | PNG |

## 页面信息架构（先上这些）

1. **首页**：Hero 背景 + 三产品主图 + 三场景缩略（车用/航空/工业）+ 新闻三封面  
2. **产品中心**：Banner + 三 SKU 主图；详情页可加爆炸图/控制器  
3. **新闻**：Banner + 三封面（替换现有小图）  
4. **关于**：Banner + 实验室 1～2 张；团队剪影可选  
5. **联系**：Banner + 园区图 + 三个服务图标 + 真实微信码  

## 入库方式

1. 把原图（JPG/PNG）按上表「建议文件名」放进：  
   `kdgc-deploy/assets-incoming/`  
2. 运行：  
   `python3 kdgc-deploy/ingest_ai_images.py`  
3. 脚本会：压缩 → WebP → 拷到 `frontend/dist/assets/images/...` → 再跑 `generate_pages.py` 刷新引用  

## 当前状态（已上线能力）

- 现有产品 / 新闻 / 荣誉 / 合作伙伴图已转 **WebP**，页面优先引用 `.webp`。  
- 微信二维码固定用 **PNG**（保证可扫）。  
- Hero / 场景 / Banner / 联系图标等槽位已写好：文件放入 `assets-incoming/` 并跑 `ingest_ai_images.py` 即显示。  
- 聊天贴图**不会**落盘，请发 **zip** 或直接拷进 `assets-incoming/`。

## 注意

- **不要用** `07-06 wechat-placeholder` 替换真实可扫码二维码。  
- 产品白底图优先 WebP；若透明底需要再保留 PNG。  
