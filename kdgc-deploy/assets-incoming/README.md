# AI 生图入库目录

把 Gemini / 设计稿原图（JPG/PNG）按下列文件名放入本目录，然后运行：

```bash
cd kdgc-deploy
python3 ingest_ai_images.py
```

脚本会转成 **WebP** 写入 `frontend/dist/assets/images/...`，并自动重新生成页面。

## 推荐文件名（与投放表一致）

| 文件名 | 挂载位置 |
|--------|----------|
| `hero-oxygen-sensor.jpg` | 首页 Hero 背景 |
| `products-banner.jpg` | 产品中心页头 |
| `product-kd0100-02s-t1.png` | T1 探头主图 |
| `product-kd0100-02s-to.png` | TO 插针主图 |
| `product-mask-o2-sensor.png` | 面罩传感器主图 |
| `product-exploded.png` | 产品详情结构图 |
| `product-controller-kd0100-03.png` | 控制器配套图 |
| `scene-automotive.jpg` | 应用·车用 |
| `scene-aviation-mask.jpg` | 应用·航空 |
| `scene-industrial-gas.jpg` | 应用·工业 |
| `cover-team-building.jpg` | 新闻·团建封面 |
| `cover-nox-market.jpg` | 新闻·氮氧市场封面 |
| `cover-o2-explain.jpg` | 新闻·一文读懂封面 |
| `news-banner.jpg` | 新闻列表页头 |
| `banner-about.jpg` | 关于页页头 |
| `lab-environment-1.jpg` / `lab-environment-2.jpg` | 关于·研发环境 |
| `contact-banner.jpg` | 联系页页头 |
| `contact-campus.jpg` | 联系页园区实景 |
| `icon-response.png` / `icon-24h.png` / `icon-location.png` | 联系页服务图标 |

也支持带批次前缀的名字，例如 `04-01-cover-team-building.jpg`、`07-01-contact-campus.jpg`。

完整对照见 `docs/image-placement-web.md`。

> 聊天里直接贴图不会落到服务器磁盘，请发 **zip** 或把文件拷进本目录。  
> **不要**用 `wechat-placeholder` 覆盖真实可扫码的 `wechat-qr.png`。
