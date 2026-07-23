# LyRead 图片生成需求清单（交给 ChatGPT / DALL·E）

> 生成后请保存为 **PNG**，文件名与下表一致，发回给我后我会压缩为 WebP 并接入网站。
> 存放路径：`lyread/frontend/public/images/`

---

## 一、全局风格（每条 Prompt 前都加这段）

```
Global style for LyRead AI (Chinese web novel SaaS platform):
Modern flat vector illustration, clean professional SaaS aesthetic,
primary colors blue gradient #4DA1FF to #2563EB, accents white and soft ice-blue #F1F6FA,
soft subtle shadows, rounded friendly shapes, high clarity at small sizes.
NO readable text, NO letters, NO watermarks, NO logos with words.
```

---

## 二、当前已有图片（18 张，一般无需重做）

| 文件名 | 用途 | 备注 |
|--------|------|------|
| logo-icon.webp | 导航 Logo、favicon | 可升级更清晰版 |
| hero-banner.webp | 首页 Hero 背景 | 已有 |
| workspace-banner.webp | 创作台欢迎图 | 已有 |
| empty-create.webp | 空状态 | 已有，可共用 |
| icon-brain/novel/short/credits | 首页四大功能 | 已有 |
| icon-gift/daily/gem/point/fire | 价格/钱包/热度 | 已有 |
| cover-urban/warrior/reborn | 书封（都市/战神/重生） | 已有，需扩充题材 |
| avatar-author/studio | 用户评价头像 | 已有 |

---

## 三、仍偏「低」或未覆盖的位置

| 位置 | 现状 | 建议 |
|------|------|------|
| 创作台 AI 按钮 4 个 | **复用**功能图标，语义不对 | 生成 4 张专用动作图标 |
| 案例阅读封面 | 仅 3 张轮换，仙侠/言情等不匹配 | 再生成 4–5 张题材封面 |
| 登录页 | 仅小 Logo，大面积留白 | 左侧/背景插图 |
| 运营后台 | **纯文字**，无图 | 页头横幅 + 403 插图 |
| 移动端菜单 | `☰` `✕` 字符 | 菜单/关闭图标 |
| 社交登录（注释中） | emoji 💬 | 微信/QQ 图标（可选） |
| 微信分享预览 | 用 hero-banner | 专用 1200×630 og 图 |
| 作品列表缩略图 | 无封面 | 默认书封占位图 |
| 交易记录图标 | 多类型共用 gem/point | 5 张交易类型图标 |

---

## 四、待生成图片（完整 Prompt）

### P0 — 优先（语义错误 + 高频曝光）

#### 1. `icon-action-title.png` — 生成书名按钮
- **尺寸**：512×512，透明或白底
- **显示**：创作台「生成书名」，约 18×18px
- **Prompt**：
```
[Global style prefix]
App icon: open book with a golden nameplate tag floating above it,
symbolizing AI-generated novel titles, blue and gold accents,
square composition, centered, minimal detail for small-size clarity.
```

#### 2. `icon-action-outline.png` — 生成大纲按钮
- **尺寸**：512×512
- **Prompt**：
```
[Global style prefix]
App icon: hierarchical tree diagram or mind map with 4 connected nodes,
representing story outline structure, blue lines on white,
square, clean, readable at 24px.
```

#### 3. `icon-action-chapters.png` — 生成章纲按钮
- **尺寸**：512×512
- **Prompt**：
```
[Global style prefix]
App icon: vertical stack of 3 document pages with numbered chapter markers,
representing chapter planning, blue and white, square, flat design.
```

#### 4. `icon-action-continue.png` — AI 续写按钮
- **尺寸**：512×512
- **Prompt**：
```
[Global style prefix]
App icon: fountain pen writing a glowing text line on paper,
AI sparkle particles, blue ink, square, energetic but professional.
```

#### 5. `og-share.png` — 微信/社交媒体分享图
- **尺寸**：1200×630（必须）
- **用途**：`og:image`、链接预览
- **Prompt**：
```
[Global style prefix]
Wide social media banner 1200x630: abstract AI writing workspace scene,
floating book pages and character profile cards, blue gradient background,
modern Chinese SaaS marketing visual, cinematic but clean,
NO text NO words NO letters.
```

#### 6. `login-illustration.png` — 登录页插图
- **尺寸**：800×600 或 4:3
- **用途**：登录卡右侧或背景（桌面端）
- **Prompt**：
```
[Global style prefix]
Illustration: writer collaborating with friendly AI assistant hologram,
novel manuscripts and chapter outlines on desk, warm blue lighting,
hopeful creative mood, 4:3 landscape, no text.
```

---

### P1 — 案例封面扩充（按题材匹配）

统一规格：**600×800（3:4 竖版书封）**，无文字，无书名。

#### 7. `cover-xianxia.png` — 仙侠玄幻
```
[Global style prefix]
Chinese web novel book cover, xianxia cultivation theme,
misty mountains, sword and spiritual energy, cyan and gold palette,
vertical 3:4, dramatic, no text.
```

#### 8. `cover-romance.png` — 言情甜宠
```
[Global style prefix]
Chinese web novel book cover, modern romance theme,
soft pink and blue, city sunset, subtle couple silhouette,
vertical 3:4, warm, no text.
```

#### 9. `cover-scifi.png` — 科幻脑洞
```
[Global style prefix]
Chinese web novel book cover, sci-fi brainhole theme,
futuristic city, neural network hologram, purple and blue neon,
vertical 3:4, no text.
```

#### 10. `cover-suspense.png` — 悬疑推理
```
[Global style prefix]
Chinese web novel book cover, mystery suspense theme,
dark alley, single streetlight, rain, noir blue-gray tones,
vertical 3:4, tense atmosphere, no text.
```

#### 11. `cover-history.png` — 历史架空
```
[Global style prefix]
Chinese web novel book cover, historical fiction theme,
ancient palace and scrolls, red and gold imperial colors,
vertical 3:4, epic, no text.
```

---

### P1 — 钱包交易专用图标

统一规格：**512×512**，扁平图标。

#### 12. `icon-txn-recharge.png` — 充值到账
```
[Global style prefix]
Icon: wallet with upward arrow and coin, green and blue, square, flat.
```

#### 13. `icon-txn-consume.png` — 消费结算
```
[Global style prefix]
Icon: document with minus sign and small coins leaving, orange and blue, flat.
```

#### 14. `icon-txn-refund.png` — 失败返还
```
[Global style prefix]
Icon: circular arrow returning coins to wallet, teal and blue, flat.
```

#### 15. `icon-txn-reserve.png` — 预冻结
```
[Global style prefix]
Icon: snowflake or lock on coin stack, gray-blue, flat, square.
```

#### 16. `icon-txn-bonus.png` — 注册赠送
```
[Global style prefix]
Icon: gift box with star burst, coral and blue, flat, square.
```

---

### P2 — 运营后台 & UI 细节

#### 17. `admin-banner.png` — 后台页头
- **尺寸**：1200×200 宽横幅
```
[Global style prefix]
Wide admin dashboard header banner, abstract data charts and moderation queue,
blue gradient, minimal, 6:1 aspect ratio, no text.
```

#### 18. `admin-denied.png` — 403 无权限
- **尺寸**：400×300
```
[Global style prefix]
Illustration: friendly locked admin door with shield icon,
soft blue, not scary, empty state style, no text.
```

#### 19. `default-story-cover.png` — 作品列表默认封面
- **尺寸**：300×400（3:4）
```
[Global style prefix]
Generic default book cover placeholder, neutral blue gradient,
subtle book silhouette, minimal, vertical 3:4, no text.
```

#### 20. `icon-menu.png` — 移动端汉堡菜单
- **尺寸**：128×128，透明底
```
[Global style prefix]
Three horizontal lines hamburger menu icon, blue #2563EB,
minimal UI icon, transparent background, centered.
```

#### 21. `icon-close.png` — 移动端关闭
- **尺寸**：128×128，透明底
```
[Global style prefix]
X close icon, rounded line caps, blue #2563EB,
minimal UI icon, transparent background.
```

#### 22. `icon-wechat.png` — 微信登录（可选）
- **尺寸**：128×128
```
[Global style prefix]
WeChat-style green chat bubble icon, simplified flat,
recognizable but not official trademark exact copy, rounded square.
```

#### 23. `icon-qq.png` — QQ 登录（可选）
- **尺寸**：128×128
```
[Global style prefix]
QQ-style penguin mascot simplified flat icon,
cute minimal, blue and white, rounded.
```

---

### P2 — 品牌升级（可选替换现有）

#### 24. `logo-icon-v2.png` — 更清晰 Logo
- **尺寸**：512×512
```
[Global style prefix]
App logo mark: open book merged with neural network nodes,
blue gradient circle background, crisp edges for favicon use,
square, no text, professional SaaS brand.
```

#### 25. `pricing-hero.png` — 价格页顶部横幅
- **尺寸**：960×240
```
[Global style prefix]
Wide banner: transparent pricing concept, coins and gem credits,
fair pay-as-you-go, blue and gold, 4:1 ratio, no text.
```

---

## 五、交付规范

1. **格式**：PNG（24 位，图标可用透明底）
2. **命名**：与上表文件名完全一致（小写、连字符）
3. **不要**：水印、中文书名、英文单词、真实品牌 Logo（微信/QQ 做风格化即可）
4. **打包**：可 zip 发给 Cursor，或上传到仓库 `lyread/frontend/public/images/`

## 六、建议生成顺序

1. P0 的 1–6（创作按钮 + 分享图 + 登录图）— 立刻改善核心体验  
2. P1 的 7–11（书封）— 案例区更真实  
3. P1 的 12–16（交易图标）— 钱包页更专业  
4. P2 其余 — 锦上添花  

## 七、ChatGPT 使用提示

对 ChatGPT 说：

> 请按下面清单逐张生成图片。每张图前先加上「全局风格」段落，再写该图的 Prompt。尺寸按比例生成，导出 PNG，文件名用我给的名称。一次生成 1–2 张，我确认风格后再继续。

---

生成完成后把 PNG 发给我，我会：
1. 压缩为 WebP  
2. 更新 `src/assets/images.js`  
3. 接入对应页面并部署到 lyread.cn  
