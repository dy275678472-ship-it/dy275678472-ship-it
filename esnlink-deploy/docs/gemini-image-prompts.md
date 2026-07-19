# esnlink.cn 图片制作需求 + Gemini 网页版提示词

> 品牌：esnlink · 翼星科技  
> Slogan：链接创造价值  
> 视觉主色：深蓝 `#0f172a` / 品牌蓝 `#2563eb` / 青色 `#0891b2` / 试用橙 `#f59e0b`  
> 风格关键词：clean enterprise SaaS, soft blue light, modern product UI, no clutter, no watermarks, no fake logos of Alibaba/Tencent  
> Gemini 网页版每次最多 **8 张**：下面按 Batch 分组，一次复制一个 Batch。

---

## 一、现状检查（图片缺口）

| 位置 | 现状 | 问题 |
|------|------|------|
| 全站栏目顶栏 | 已统一为首页风格导航（本次修复） | 无 logo 图标文件，纯文字 |
| 首页 Hero | 渐变背景 + 文案 | **缺主视觉大图** |
| 产品页（外呼/短信/物联网） | 基本无配图 | 缺产品场景图 |
| 行业方案（教育/电商/金融） | 文字为主 | 缺封面图 |
| 案例中心 | 列表文字 | 缺案例封面 |
| 英文版 | 极简卡片 | 缺 EN Hero / 产品图 |
| 信任墙 | 8 个 SVG 占位 logo | 需换成更精致行业徽章（非真实客户商标） |
| OG 分享图 | 有 `og-image.png` | 可升级为更清晰品牌构图 |
| Landing `/landing/sms.html` | 纯色渐变 | 可选补一张短信触达插画 |

**结论：** 站点几乎没有摄影级/插画级产品图，优先补 **Hero + 3 产品 + 4 行业封面**（Batch 1），再补案例/OG/英文（Batch 2–3）。

---

## 二、输出规格（生成后请按此导出）

| 用途 | 文件名建议 | 尺寸 | 格式 |
|------|------------|------|------|
| 首页 Hero | `hero-home.webp` | 1600×1000 | WebP/JPG，主体偏右留白给文案 |
| 产品场景 | `product-call.webp` 等 | 1200×800 | WebP |
| 行业封面 | `solution-education.webp` 等 | 1400×788（16:9） | WebP |
| 案例封面 | `case-01.webp` 等 | 1200×675 | WebP |
| OG | `og-image.png` | **1200×630**（固定） | PNG |
| Logo 图标 | `logo-mark.png` | 512×512 透明底 | PNG |
| 信任徽章 | `badge-*.svg/png` | 280×64 | PNG 透明 |

放置目录建议：`/assets/images/`（Hero/产品/方案）、`/assets/images/cases/`、根目录保留 `og-image.png`。

---

## 三、通用前缀（每个提示词都带上）

把下面这段复制到每条 prompt 开头（或作为 Gemini 对话系统设定）：

```text
Brand visual system for esnlink (翼星科技), an enterprise communication cloud company in China.
Style: modern B2B SaaS, clean, premium, soft daylight + cool blue accents (#2563eb, #0891b2), slate navy (#0f172a).
No text in the image unless explicitly requested. No watermarks, no stock-photo watermarks, no real third-party brand logos.
Photoreal or high-end 3D product visualization. Wide composition with negative space for website copy.
```

---

## Batch 1（8 张）— 首页 + 三产品 + 四行业封面（优先做）

### 1) 首页 Hero 主视觉 — `hero-home.webp`
```text
[Use brand visual system above]
Wide hero visual for an enterprise communication cloud homepage.
A modern glass-and-steel office desk scene from a slightly elevated angle: a laptop showing an abstract AI call-center dashboard (waveform, green call buttons, soft charts), a smartphone receiving a clean SMS notification bubble, and a small IoT gateway device with a subtle cyan LED.
Soft blue ambient light, shallow depth of field, lots of empty space on the LEFT for headline text overlay.
No readable real text, no logos, photoreal, 16:10, premium SaaS marketing look.
```

### 2) 智能外呼产品图 — `product-call.webp`
```text
[Use brand visual system above]
Product scene for AI outbound calling / intelligent call center.
Headset silhouette next to a floating translucent UI panel showing call progress rings, AI voice waveform, and agent assist cards.
Cool blue-cyan lighting, dark navy desk, clean and techy, no readable Chinese/English words, cinematic product photography style, 3:2.
```

### 3) 短信平台产品图 — `product-sms.webp`
```text
[Use brand visual system above]
Product scene for enterprise SMS platform.
A smartphone in the foreground with a clean SMS thread of abstract message bubbles (no real brand names), behind it a soft-focus server room / cloud network light trails suggesting high delivery rate.
Bright, trustworthy, blue accents, generous negative space, photoreal, 3:2.
```

### 4) 物联网产品图 — `product-iot.webp`
```text
[Use brand visual system above]
Product scene for IoT connectivity platform.
A compact industrial IoT module / 4G-5G gateway on a clean bench, subtle holographic network mesh connecting tiny sensors (campus, meter, camera) in the background blur.
Cyan LED glow, navy and white palette, photoreal tech product shot, 3:2.
```

### 5) 教育行业方案封面 — `solution-education.webp`
```text
[Use brand visual system above]
16:9 cover image for education industry communication solution.
Modern vocational campus corridor with soft daylight; overlay a translucent dashboard motif suggesting student outreach calls and class notifications — abstract, not readable.
Optimistic blue tones, no school logos, no faces sharply identifiable, cinematic, spacious.
```

### 6) 电商行业方案封面 — `solution-ecommerce.webp`
```text
[Use brand visual system above]
16:9 cover for ecommerce messaging & outreach solution.
Bright fulfillment / packing desk with parcels and a tablet showing abstract order-notification UI; warm accent of orange (#f59e0b) only as small highlight against blue brand colors.
No marketplace logos (no Taobao/Amazon marks), clean commercial photography.
```

### 7) 金融行业方案封面 — `solution-finance.webp`
```text
[Use brand visual system above]
16:9 cover for finance SMS & secure notification solution.
Minimalist bank-operations desk: laptop with abstract compliance dashboard, soft vault-blue lighting, feeling of security and trust.
No real bank logos, no card numbers readable, premium corporate look.
```

### 8) 医疗/社区医院方案封面 — `solution-healthcare.webp`
```text
[Use brand visual system above]
16:9 cover for community hospital patient-communication solution.
Clean clinic reception with soft daylight; smartphone showing abstract appointment reminder bubbles; calm teal-blue palette communicating care and reliability.
No hospital logos, no patient faces in focus, respectful documentary style.
```

---

## Batch 2（8 张）— 案例封面 + Logo + OG + Landing

### 1–4) 案例封面 `case-01` … `case-04`
```text
[Use brand visual system above]
16:9 case-study cover #{N}: {THEME}.
Show a tasteful before/after energy of digital transformation with abstract UI glass panels and a real-world environment.
No readable client names, no logos. Soft blue grade, premium editorial photo.
Themes:
1) vocational education enrollment outbound calling
2) training institution SMS reminders
3) adult education night-class outreach
4) smart campus IoT connectivity
```
（生成时把 `{N}` / `{THEME}` 换成上面 4 条，各跑一张；若 Gemini 一次可出多图，可把 4 条拆成 4 个完整 prompt。）

**展开版（可直接分 4 次粘贴）：**

**case-01**
```text
[Use brand visual system above]
16:9 case-study cover: vocational education enrollment powered by AI outbound calling.
Counselor desk + soft overlay of call waveform UI, hopeful daylight, blue accents, no logos, no readable text.
```

**case-02**
```text
[Use brand visual system above]
16:9 case-study cover: training institution using SMS reminders for class attendance.
Classroom corridor + phone with abstract reminder bubbles, clean and bright, no logos.
```

**case-03**
```text
[Use brand visual system above]
16:9 case-study cover: adult education night-class outreach via intelligent calling.
Evening campus lights, warm windows, cool blue UI overlay, cinematic, no logos.
```

**case-04**
```text
[Use brand visual system above]
16:9 case-study cover: smart campus IoT connectivity.
IoT gateway + campus network mesh light points at dusk, cyan LEDs, premium tech photo, no logos.
```

### 5) 品牌 Logo 图标 — `logo-mark.png`
```text
[Use brand visual system above]
Simple geometric app icon / brand mark for "esnlink": abstract link-node or twin-star connection symbol.
Flat vector style, blue gradient (#2563eb to #0891b2), transparent background, centered, no text, suitable at 32px and 512px.
```

### 6) OG 分享图 — `og-image.png`（必须 1200×630）
```text
[Use brand visual system above]
Open Graph social share image, exactly 1200x630 composition.
Left side: bold empty space for later text overlay "esnlink · 翼星科技".
Right side: collage of AI headset waveform + SMS phone + IoT module in soft 3D.
Navy-to-blue gradient background, premium, no small unreadable text, no watermarks.
```

### 7) 短信落地页插画 — `landing-sms-hero.webp`
```text
[Use brand visual system above]
Full-bleed illustration for SMS pricing landing page.
Dark navy gradient background, glowing message bubbles flying upward like a delivery network, one large price-tag glow in amber (#f59e0b) without any numbers/text.
High contrast, conversion-focused, modern fintech aesthetic, 16:9.
```

### 8) 预约演示页配图 — `booking-hero.webp`
```text
[Use brand visual system above]
Friendly B2B booking/demo page visual.
Two professionals on a video call (faces slightly out of focus / not identifiable), laptop showing abstract product UI, bright office, trust-building blue accents, 3:2.
```

---

## Batch 3（8 张）— 英文版 + 信任徽章 + 文档插图

### 1) 英文首页 Hero — `hero-home-en.webp`
```text
[Use brand visual system above]
Homepage hero for ENGLISH site of the same brand.
Global enterprise SaaS look: laptop dashboard + smartphone SMS + IoT gateway, more neutral international office set, blue accents, LEFT side empty for English headline, photoreal 16:10, no text.
```

### 2) EN AI Calling — `product-call-en.webp`
```text
[Use brand visual system above]
English-market product image for AI calling: headset + translucent analytics panels, cool blue, clean desk, no text, 3:2.
```

### 3) EN SMS — `product-sms-en.webp`
```text
[Use brand visual system above]
English-market product image for SMS API: smartphone + abstract API node graph in background blur, bright trustworthy blue, no text, 3:2.
```

### 4–8) 信任墙行业徽章（5 张，非真实商标）
```text
[Use brand visual system above]
Minimal horizontal partner badge icon on transparent / white background, 280x64 feel, flat vector.
Abstract monogram only (NOT a real carrier or company logo):
4) telecom abstract signal bars + orbit ring (generic)
5) satellite constellation abstract hexagon
6) finance abstract column / shield
7) education abstract open-book geometry
8) healthcare abstract cross-in-circle (subtle, not red-cross official mark)
Blue-gray palette, clean, suitable for logo wall.
```
（说明：真实「电信/移动/联通/星网」商标勿让 AI 仿冒；官网信任墙请用几何徽章或客户授权真 Logo。）

---

## Batch 4（可选 6 张）— 文档/定价/博客配图

### 1) 文档中心头图 — `docs-hero.webp`
```text
[Use brand visual system above]
Developer docs hero: code editor bokeh + API key card abstract + soft network lines, blue theme, 16:9, no readable code text.
```

### 2) 定价页配图 — `pricing-hero.webp`
```text
[Use brand visual system above]
Pricing page visual: clean 3 soft glass pricing cards floating above a desk (no numbers/text), amber highlight on the middle card, blue ambient light, 16:9.
```

### 3) 博客默认封面 — `blog-cover-default.webp`
```text
[Use brand visual system above]
Default blog cover: abstract communication nodes linked by light, navy background, blue-cyan glow, 16:9, no text.
```

### 4) FAQ / 帮助中心 — `faq-hero.webp`
```text
[Use brand visual system above]
Help center illustration: soft 3D chat bubbles and a headset icon, friendly light blue, spacious, 16:9, no text.
```

### 5) 关于我们 — `about-team.webp`
```text
[Use brand visual system above]
About-us office atmosphere: modern Chinese tech office collaboration area, natural light, no identifiable faces, blue accent glass walls, photoreal 16:9.
```

### 6) 物联网校园专题 — `iot-campus.webp`
```text
[Use brand visual system above]
Smart campus IoT aerial-style dusk scene with subtle connected light points on buildings, cyan network overlay, cinematic, no logos, 16:9.
```

---

## 四、生成后怎么交给我上线

1. 按文件名导出（优先 WebP，OG 用 PNG 1200×630）。  
2. 发我文件夹或压缩包路径。  
3. 我会把图挂到对应页面（首页 Hero、产品、方案、案例、EN、og-image）。  

## 五、本次与导航修复的关系

- 栏目顶栏已与首页统一（含英文版结构对齐）。  
- **图片不会自动出现在顶栏**；Logo 图标（Batch2-#5）做好后可替换文字 Logo 左侧的 mark。  
