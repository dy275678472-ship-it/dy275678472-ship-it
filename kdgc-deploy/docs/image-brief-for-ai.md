# 中科国瓷官网 · AI 生图需求规范（给 ChatGPT / 图像模型）

> 用途：让 AI 按栏目批量生成网站视觉素材  
> 品牌：安徽中科国瓷新型元器件有限公司（中科国瓷 / ZK Guoci）  
> 产品定位：变频氧传感器、氮氧传感相关技术（**不要**生成陶瓷基板/AlN/DBC 类错误题材）  
> 风格总则：工业科技、冷静专业、偏实验室/精密制造；避免卡通、赛博紫光、廉价库存感  

---

## 0. 全局视觉规范（所有图都遵守）

### 品牌气质
- 关键词：精密传感、中科大技术转化、可信赖、B2B 工业
- 主色建议：深蓝 `#071426`、科技蓝 `#1677FF`、白/浅灰背景；点缀可用冷青绿或金属银
- 避免：紫色霓虹、赛博朋克、过度发光、表情包式插画、文字堆满画面

### 技术输出要求
| 用途 | 推荐尺寸 (px) | 比例 | 格式 | 背景 |
|------|---------------|------|------|------|
| 首页 Hero 背景 | 1920×1080 | 16:9 | JPG/WebP | 可深色渐变+轻微纹理 |
| 栏目页头 Banner | 1920×640 | 约 3:1 | JPG/WebP | 深色或实验室氛围 |
| 产品主图 | 1200×1200 | 1:1 | PNG（透明底优先）或白底 JPG | 纯白/浅灰 |
| 产品列表缩略图 | 800×600 | 4:3 | JPG/WebP | 白底或浅灰 |
| 新闻封面 | 1200×675 | 16:9 | JPG/WebP | 写实或轻插画 |
| 知识库封面 | 1200×675 | 16:9 | JPG/WebP | 示意图风格可接受 |
| 案例封面 | 1400×788 | 16:9 | JPG/WebP | 应用场景写实 |
| 团队/人物占位 | 800×1000 | 4:5 | JPG | 中性背景，商务专业 |
| 荣誉/证书展示框 | 1000×1400 | 约 5:7 | PNG/JPG | 白底，仅作“展示位示意”时用 |
| 合作伙伴 Logo 位 | 600×240 | 2.5:1 | PNG 透明 | 透明底 |
| OG 分享图 | 1200×630 | 约 1.91:1 | JPG | 含品牌名空间 |
| 图标/小插图 | 512×512 | 1:1 | PNG 透明 | 透明底 |

### 画面文字规则
- **默认不要在图内写中文大段说明**（网站自己排版）
- 仅允许：极简英文型号（如 `KD0100`）、无字纯视觉
- 若必须出带字海报，另开任务，并单独标注「可含文字」

### 统一负面提示词（Negative，每次都可附上）
```
cartoon, anime, cute sticker, neon purple glow, cyberpunk city,
blurry, watermark, stock photo logo, fake brand logos,
ceramic substrate board, AlN wafer marketing collage,
messy text, Chinese characters filling the image, low quality
```

---

## 1. 首页（Home）

### 1.1 Hero 主视觉背景 ×1（必做）
- 文件名建议：`hero-oxygen-sensor.jpg`
- 尺寸：1920×1080
- 构图：左侧或中央留出大面积负空间给标题；右侧/下方可有传感器/实验室元素
- ChatGPT 提示词：
```
Photorealistic industrial technology hero background for a B2B oxygen sensor company.
Deep navy to dark blue gradient atmosphere, subtle laboratory cleanroom lighting.
A precise oxygen sensor probe and controller subtly visible on the right third,
metallic and ceramic sensing tip, shallow depth of field.
Left two-thirds mostly clean dark space for website headline overlay.
No text, no logos, no people faces. Cinematic, premium, trustworthy. 16:9.
```

### 1.2 信任条小图标 ×4（可选）
主题：ISO 认证、发明专利、深科技企业、5年质保  
- 尺寸：512×512，扁平线性图标，蓝白配色，透明底  
- 风格统一：2px 线宽、圆角矩形容器可选  

### 1.3 OG / 社交分享图 ×1
- 尺寸：1200×630  
- 提示词：同 Hero，但更居中，预留中部空白放品牌名（图内仍可不写字）

---

## 2. 关于中科国瓷（About）

### 2.1 栏目 Banner ×1
```
Wide banner 1920x640, modern Chinese deep-tech company atmosphere.
University research lab transferring to industry, clean architecture +
precision instruments silhouette, navy blue tones, no text.
```

### 2.2 团队人物图 ×3（若暂无实拍，用「商务写实占位」）
| 角色 | 文件名 | 气质 |
|------|--------|------|
| 首席科学家 陈初升 | `team-chief-scientist.jpg` | 资深学者、沉稳、实验室/书房背景虚化 |
| 总经理 李超 | `team-gm.jpg` | 科技企业高管、商务正装、自信专业 |
| 总工程师 李彤 | `team-cto.jpg` | 工程技术负责人、干练、偏研发场景 |

通用提示词模板：
```
Professional corporate portrait photo, Asian male, [ROLE VIBE],
soft studio or blurred lab background, navy suit or smart casual,
natural lighting, 4:5 vertical, photorealistic, no text, no watermark.
```
> 注意：AI 生成脸部不能冒充真人照片用于「实名介绍」。若用于上线，建议标注「示意」或改用实拍；更稳妥是只生成「剪影/背影/无脸部特写」的场景图。

**更推荐的合规方案（优先）：**
```
Abstract professional silhouette of a scientist / executive in a lab,
back view or side profile in shadow, no identifiable face,
navy color grade, premium B2B style, 4:5.
```

### 2.3 公司/研发环境图 ×2
1. 洁净实验室工作台 + 传感器测试设备  
2. 办公室/展厅「科技感知未来」氛围（无具体竞品 Logo）

### 2.4 荣誉资质「展示底板」×1（可选）
- 用于证书照片的统一衬底/画廊背景（证书本身用官网扫描件，不需 AI 伪造证书）
```
Clean light gray certificate gallery wall background, soft shadows,
museum-like display rail, 1920x1080, no fake seals, no text.
```

### 2.5 合作伙伴区装饰 ×1
```
Minimal partner logo wall background, soft grid, light gray,
plenty of empty slots, no brand logos, 1920x600.
```

---

## 3. 产品中心（Products）

### 3.1 产品主图 ×3（核心，尽量「电商级白底精拍」风格）

| 产品 | 文件名 | 要点 |
|------|--------|------|
| KD0100-02S-T1 探头 | `product-kd0100-02s-t1.png` | 线束探头型，金属/陶瓷探头 + 多色线束 |
| KD0100-02S-TO 插针 | `product-kd0100-02s-to.png` | 插针型，轻量化、针脚清晰 |
| 面罩用氧传感器 | `product-mask-o2-sensor.png` | 航空面罩相关传感模组感，精密小巧 |

通用提示词：
```
Studio product photography of an industrial oxygen sensor [PROBE WITH CABLE / PIN HEADER / AVIATION MASK MODULE],
centered on pure white background, softbox lighting, sharp detail,
metallic housing, sensing tip visible, high-end electronic component look,
square 1:1, no text, no brand logos, no people.
```

### 3.2 产品「爆炸/结构示意」×1（可选，用于详情页）
```
Technical exploded-view illustration of an oxygen sensor probe:
housing, ceramic sensing element, heater, pins/cable, clean white background,
blueprint-ish soft blue accents, no text labels (labels added on website).
```

### 3.3 应用场景配图 ×3（产品详情底部可用）
1. 汽车尾气/发动机舱精密传感（不出现可识别车标）  
2. 飞行员面罩/航空供氧监测（示意，非军徽）  
3. 工业炉窑/气体管道在线监测  

```
Photorealistic application scene: [SCENE], oxygen sensing context,
industrial documentary style, navy-blue color grade, 16:9, no logos, no text.
```

---

## 4. 新闻资讯（News）

官网现有 3 篇，建议每篇 1 张封面：

| 文章 | 封面方向 |
|------|----------|
| 团建户外活动 | 团队户外拓展氛围（可用实拍；AI 仅作补图时避免伪造「本公司合影」） |
| 车用氮氧传感器市场 | 卡车/柴油车尾气后处理系统示意、传感器与排气管道 |
| 一文读懂氧传感器 | 氧传感器剖面/原理示意图，干净科普风 |

提示词示例（市场篇）：
```
Editorial technology photo: diesel vehicle exhaust aftertreatment system context,
focus on gas sensor concept near exhaust pipe, realistic, 16:9,
no car brand logos, no text.
```

提示词示例（科普篇）：
```
Clean scientific illustration of zirconia oxygen sensor cross-section concept,
ceramic electrolyte, electrodes, heater, soft blue and white, 16:9, no text.
```

---

## 5. 知识库（Knowledge）

每篇文章 1 封面 + 可选 1 原理图。首批 P0 四篇建议：

| 选题 | 视觉 |
|------|------|
| 变频 vs 传统氧传感器 | 对比示意：两枚传感器并置，中间抽象波形 |
| T1 vs TO 选型 | 探头线束 vs 插针，左右对比白底 |
| 0.5–101 kPa 量程 | 简洁仪表/量程刻度抽象图（无具体假数据更好） |
| KD0100-03 控制器接线 | 控制器模块 + 线束分色示意（可用示意图） |

风格：科普插画 + 轻微 3D，白底或浅灰，信息图感，但**图内尽量无字**。

---

## 6. 产品案例（Cases）

每案例最少：
1. **封面** 1400×788 应用场景  
2. **过程图** 1–2 张（台架/安装/测试）  
3. **结果视觉** 1 张（可抽象：下降曲线、稳定波形——无伪造具体客户数据数字）

案例方向（与建设方案一致）：
- 航空面罩供氧监测  
- 工业气体氧分压在线监测  
- 紧凑设备插针集成  
- （规划）柴油机 SCR/OBD 配套  

```
Documentary-style industrial case study cover photo:
[APPLICATION], technicians optional with backs turned / no identifiable faces,
equipment and sensor installation emphasis, 16:9, no logos, no text.
```

---

## 7. 联系我们（Contact）

### 7.1 地图/区位氛围图 ×1（可选）
合肥高新区科创园区外景氛围（不要伪造具体门牌实景冒充）  
```
Modern high-tech industrial park exterior in Hefei style atmosphere,
daylight, clean architecture, 16:9, no readable signage text.
```

### 7.2 客服/响应图标 ×3
快速响应、7×24、定位/地址 —— 线性图标 512×512

---

## 8. 英文站 / 通用装饰

- EN Hero：同中文 Hero，更国际化工业风即可  
- 页脚细纹理：深海军蓝微网格 1920×200（可选）

---

## 9. 交付清单（请按此打包回传）

请按文件夹返回：

```
01-home/
  hero-oxygen-sensor.jpg
  og-share.jpg
  icon-iso.png
  icon-patent.png
  icon-deeptech.png
  icon-warranty.png
02-about/
  banner-about.jpg
  team-scientist-silhouette.jpg
  team-gm-silhouette.jpg
  team-cto-silhouette.jpg
  lab-environment-1.jpg
  lab-environment-2.jpg
03-products/
  product-kd0100-02s-t1.png
  product-kd0100-02s-to.png
  product-mask-o2-sensor.png
  product-exploded.png
  scene-automotive.jpg
  scene-aviation-mask.jpg
  scene-industrial-gas.jpg
04-news/
  cover-team-building.jpg
  cover-nox-market.jpg
  cover-o2-explain.jpg
05-knowledge/
  cover-vf-vs-traditional.jpg
  cover-t1-vs-to.jpg
  cover-pressure-range.jpg
  cover-controller-wiring.jpg
06-cases/
  case-aviation-mask.jpg
  case-industrial-monitoring.jpg
  case-pin-integration.jpg
07-contact/
  contact-campus.jpg
  icon-response.png
  icon-24h.png
  icon-location.png
```

### 命名与质量
- 英文小写 + 连字符  
- 单边长边 ≥ 1200px（图标除外）  
- 文件 < 2MB（大图可先出高清，我们再压 WebP）  
- 附一张「色板参考」：深蓝/科技蓝/白/灰四色块即可  

---

## 10. 一键总提示（可先丢给 ChatGPT 当系统设定）

```
你是工业 B2B 品牌视觉设计师。客户是「中科国瓷」，做变频氧传感器/气体传感，不是陶瓷基板厂。
请按我提供的文件名与尺寸，逐张给出可直接用于文生图的英文 prompt，并遵守：
- 深蓝科技风、干净专业
- 默认图内无文字、无真实品牌 Logo、无清晰可识别人脸
- 不要陶瓷电路基板题材
- 输出时按栏目分组，每张包含：文件名、尺寸、prompt、negative prompt
```

---

## 11. 不需要 AI 生成的（请用官网原图）

以下请继续使用 www.kdgc.cc 已有实物/证件扫描，**不要让 AI 伪造**：

- 荣誉证书、专利通知书、ISO 证书原件  
- 微信二维码  
- 公司 Logo（若已有矢量/PNG）  
- 产品若已有实拍，优先实拍，AI 仅作补缺或场景氛围  

---

*文档版本：2026-07-19 · 对应线上栏目：关于 / 产品 / 新闻 / 知识库 / 案例 / 联系*
