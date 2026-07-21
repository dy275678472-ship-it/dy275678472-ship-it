"""
🌐 SEO 落地页生成器 - 为搜索引擎提供可索引的 HTML
让爬虫能抓到 LyRead 的内容页面
"""

import os
from html import escape
import requests
import mysql.connector
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from settings import database_config
from api.auth import get_current_user
from services.case_quality import public_case_sql_clause
from services.seo_schema import breadcrumb, combine_json_ld, faq_graph, website_graph

router = APIRouter()

SITE_BASE = os.getenv("SITE_URL", "https://lyread.cn").rstrip("/")
DEFAULT_OG_IMAGE = f"{SITE_BASE}/images/og-share.png"
DEFAULT_OG_SIZE_TAGS = (
    '    <meta property="og:image:width" content="1200">\n'
    '    <meta property="og:image:height" content="630">'
)


def get_db():
    try:
        return mysql.connector.connect(**database_config())
    except Exception:
        return None


def _cover_path_for_category(category: str) -> str:
    """与前端 coverForCase 对齐的题材封面路径。"""
    cat = str(category or "").lower()
    if any(k in cat for k in ("仙侠", "玄幻", "修仙")):
        return "/images/cover-xianxia.svg"
    if any(k in cat for k in ("言情", "甜宠", "恋爱")):
        return "/images/cover-romance.svg"
    if any(k in cat for k in ("科幻", "脑洞", "末世")):
        return "/images/cover-scifi.svg"
    if any(k in cat for k in ("悬疑", "推理", "惊悚")):
        return "/images/cover-suspense.svg"
    if any(k in cat for k in ("历史", "架空", "宫廷")):
        return "/images/cover-history.svg"
    if any(k in cat for k in ("战神", "都市", "神豪")):
        return "/images/cover-warrior.webp"
    if any(k in cat for k in ("重生", "穿越")):
        return "/images/cover-reborn.webp"
    if any(k in cat for k in ("系统", "游戏", "竞技", "校园", "青春")):
        return "/images/cover-urban.webp"
    return "/images/cover-urban.webp"


def _og_image_for_category(category: str) -> str:
    """OG 分享图：优先题材封面；SVG 不被多数爬虫支持时回退默认图。"""
    path = _cover_path_for_category(category)
    if path.endswith(".svg"):
        return DEFAULT_OG_IMAGE
    return f"{SITE_BASE}{path}"


def _seo_html(**kwargs) -> str:
    """PAGE_TEMPLATE 填充，默认 OG 图为站点分享图。"""
    kwargs.setdefault("site_base", SITE_BASE)
    kwargs.setdefault("og_image", DEFAULT_OG_IMAGE)
    if "og_image_size_tags" not in kwargs:
        kwargs["og_image_size_tags"] = (
            DEFAULT_OG_SIZE_TAGS if kwargs["og_image"] == DEFAULT_OG_IMAGE else ""
        )
    return PAGE_TEMPLATE.format(**kwargs)


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{og_image}">
    {og_image_size_tags}
    <meta property="og:type" content="article">
    <meta property="og:url" content="{site_base}{url}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{og_image}">
    <meta name="robots" content="index,follow">
    <link rel="canonical" href="{site_base}{url}">
    <script type="application/ld+json">{json_ld}</script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: "PingFang SC", "Microsoft YaHei", -apple-system, sans-serif;
            background: linear-gradient(180deg, #f1f6fa 0%, #f6f9ff 40%, #eef5ff 100%);
            color: #1e2a3a;
            min-height: 100vh;
            line-height: 1.6;
        }}
        .seo-container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 24px;
        }}
        .seo-header {{
            text-align: center;
            padding: 32px 24px;
            background: rgba(255,255,255,0.7);
            -webkit-backdrop-filter: blur(20px);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            border: 1px solid rgba(218, 230, 245, 0.5);
            box-shadow: 0 1px 6px rgba(77, 163, 255, 0.04);
            margin-bottom: 24px;
        }}
        .seo-header h1 {{
            font-size: 22px;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        .seo-header .brand {{
            font-size: 28px;
            font-weight: 700;
            color: #4a90d9;
            text-decoration: none;
        }}
        .seo-header .brand:hover {{
            color: #3a7bc8;
        }}
        .seo-meta {{
            font-size: 13px;
            color: #7a8ba8;
            margin-top: 8px;
        }}
        .seo-card {{
            background: rgba(255,255,255,0.85);
            border-radius: 12px;
            padding: 28px;
            border: 1px solid rgba(218, 230, 245, 0.6);
            box-shadow: 0 2px 12px rgba(77, 163, 255, 0.06);
            margin-bottom: 20px;
        }}
        .seo-card h2 {{
            font-size: 20px;
            color: #1e2a3a;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #e8edf3;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}
        .info-item {{
            background: #f4f8fe;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 14px;
            color: #3a4a5e;
        }}
        .info-item strong {{
            color: #4a90d9;
        }}
        .seo-cta {{
            text-align: center;
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid #e8edf3;
        }}
        .seo-cta a {{
            display: inline-block;
            padding: 10px 28px;
            background: linear-gradient(135deg, #4a90d9 0%, #357abd 100%);
            color: #fff;
            border-radius: 8px;
            text-decoration: none;
            font-size: 15px;
            font-weight: 500;
        }}
        .seo-cta a:hover {{
            background: linear-gradient(135deg, #3a7bc8 0%, #2a6bb8 100%);
        }}
        .seo-list {{
            list-style: none;
            padding: 0;
        }}
        .seo-list li {{
            background: rgba(255,255,255,0.85);
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 10px;
            border: 1px solid rgba(218, 230, 245, 0.6);
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .seo-list li a {{
            color: #2c3e50;
            text-decoration: none;
            font-size: 15px;
            font-weight: 500;
            flex: 1;
        }}
        .seo-list li a:hover {{
            color: #4a90d9;
        }}
        .tag {{
            background: #e8f0fe;
            color: #4a90d9;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}
        .stat {{
            color: #7a8ba8;
            font-size: 12px;
        }}
        .seo-list li .excerpt {{
            flex-basis: 100%;
            margin: 4px 0 0;
            font-size: 13px;
            color: #5a6a7a;
            line-height: 1.55;
        }}
        .seo-footer {{
            text-align: center;
            padding: 20px;
            color: #7a8ba8;
            font-size: 13px;
        }}
        .seo-footer a {{
            color: #4a90d9;
            text-decoration: none;
        }}
        .seo-nav {{
            margin-bottom: 12px;
            font-size: 14px;
        }}
        .seo-nav a {{
            margin: 0 6px;
        }}
        .seo-faq dt {{
            font-weight: 600;
            color: #1e2a3a;
            margin-top: 16px;
        }}
        .seo-faq dd {{
            margin: 6px 0 0;
            color: #5a6a7a;
            line-height: 1.6;
        }}
        @media (max-width: 600px) {{
            .seo-container {{ padding: 20px 12px; }}
            .info-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="seo-container">
        <div class="seo-header">
            <a href="{site_base}" class="brand">🧠 LyRead</a>
            <p class="seo-meta">{meta_info}</p>
        </div>
        <div class="seo-card">
            <h1>{title}</h1>
            <div class="content">
                {body_html}
            </div>
        </div>
        <div class="seo-footer">
            <nav class="seo-nav" aria-label="站点导航">
                <a href="{site_base}/">首页</a>
                <a href="{site_base}/pricing">价格</a>
                <a href="{site_base}/trending">案例</a>
                <a href="{site_base}/faq">常见问题</a>
                <a href="{site_base}/about">关于我们</a>
            </nav>
            <p>© LyRead AI 智能小说创作平台</p>
        </div>
    </div>
</body>
</html>"""


def _json_ld_article(
    title: str,
    description: str,
    url_path: str,
    genre: str = "",
    word_count: int = 0,
    image: str = "",
) -> str:
    import json
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "url": f"{SITE_BASE}{url_path}",
        "inLanguage": "zh-CN",
        "publisher": {
            "@type": "Organization",
            "name": "LyRead AI",
            "url": SITE_BASE,
            "logo": {"@type": "ImageObject", "url": f"{SITE_BASE}/images/logo-icon-v2.svg"},
        },
    }
    if genre:
        data["genre"] = genre
    if word_count:
        data["wordCount"] = word_count
    if image:
        data["image"] = [image]
    return json.dumps(data, ensure_ascii=False)


def _json_ld_list(title: str, description: str, url_path: str) -> str:
    import json
    data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": title,
        "description": description,
        "url": f"{SITE_BASE}{url_path}",
        "inLanguage": "zh-CN",
        "isPartOf": {"@type": "WebSite", "name": "LyRead AI", "url": SITE_BASE},
    }
    return json.dumps(data, ensure_ascii=False)


def _preview_og_description(title: str, category: str, word_count, heat, preview: str) -> str:
    """OG/meta description：标题+分类摘要 + 正文节选，便于分享抓取。"""
    base = f"{title} - {category}类型，{word_count}字，热度{heat}"
    snippet = " ".join((preview or "").split())[:140]
    if snippet:
        return f"{base}｜{snippet}"
    return f"{base}，AI智能创作平台"


def _render_case_seo_page(content_id: int) -> HTMLResponse:
    """案例详情 SSR（canonical 统一为 /ep/{id}，避免 /case 与 /ep 重复收录）。"""
    title = "LyRead AI - 智能小说创作平台"
    description = "LyRead AI智能小说创作平台，AI生成爆款网文"
    keywords = "AI写小说,网文创作,智能写作"
    body_html = '<p style="color: #7a8ba8; text-align: center; padding: 40px;">内容未找到</p>'
    meta_info = ""
    og_image = DEFAULT_OG_IMAGE
    # 规范 URL 始终指向 /ep/，/case/ 仅作 SPA 阅读与 bot 入口别名
    canonical = f"/ep/{content_id}"
    json_ld = _json_ld_article(title, description, canonical, image=og_image)

    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, title, category, word_count, heat, score, preview_body, created_at "
                f"FROM contents WHERE id = %s AND {public_case_sql_clause()}", (content_id,)
            )
            row = cursor.fetchone()
            cursor.close()
            db.close()

            if row:
                safe_title = escape(str(row['title']))
                safe_category = escape(str(row['category']))
                preview = row.get("preview_body") or ""
                og_image = _og_image_for_category(str(row.get("category") or ""))
                title = f"{safe_title} - LyRead AI 小说作品"
                description = escape(
                    _preview_og_description(
                        str(row["title"]),
                        str(row["category"]),
                        row["word_count"],
                        row["heat"],
                        preview,
                    )
                )
                keywords = f"小说,{safe_category},{safe_title},AI写小说,网文"
                meta_info = f"分类：{safe_category} ｜ 字数：{row['word_count']:,} ｜ 热度：{row['heat']}"
                json_ld = combine_json_ld(
                    _json_ld_article(
                        safe_title,
                        description,
                        canonical,
                        genre=safe_category,
                        word_count=int(row.get("word_count") or 0),
                        image=og_image,
                    ),
                    breadcrumb([
                        ("首页", f"{SITE_BASE}/"),
                        ("案例阅读", f"{SITE_BASE}/trending"),
                        (safe_title, f"{SITE_BASE}{canonical}"),
                    ]),
                )
                cover_path = _cover_path_for_category(str(row.get("category") or ""))
                body_html = f"""
                <div style="display:flex;gap:16px;align-items:flex-start;margin-bottom:8px">
                    <img src="{SITE_BASE}{cover_path}" alt="{safe_title} 封面" width="96" height="128"
                         style="width:96px;height:128px;object-fit:cover;border-radius:8px;background:#e8f0fa;flex-shrink:0" />
                    <div class="info-grid" style="flex:1">
                        <div class="info-item"><strong>分类</strong><br>{safe_category}</div>
                        <div class="info-item"><strong>字数</strong><br>{row['word_count']:,}</div>
                        <div class="info-item"><strong>热度</strong><br>{row['heat']}</div>
                        <div class="info-item"><strong>评分</strong><br>{row.get('score', 'N/A')}</div>
                    </div>
                </div>"""
                if preview:
                    safe_preview = escape(preview[:6000]).replace("\n", "<br>")
                    body_html += f"""
                <div style="margin-top:24px;line-height:1.9;color:#2a3a4e;white-space:normal">
                    <h2 style="font-size:18px;margin-bottom:12px;color:#1e2a3a">正文节选</h2>
                    <div style="background:#f8fafc;padding:20px;border-radius:12px;border:1px solid #e8f0fa">{safe_preview}</div>
                </div>"""
                else:
                    body_html += f"""
                <div style="margin-top:24px;padding:20px;border-radius:12px;background:#f8fafc;border:1px solid #e8f0fa;color:#64748b;font-size:14px;line-height:1.7">
                    <p>该案例暂无正文节选。可先浏览同风格作品，或直接用这个题材开写。</p>
                    <p style="margin-top:12px">
                        <a href="{SITE_BASE}/trending">浏览更多案例 →</a>
                        &nbsp;&nbsp;
                        <a href="{SITE_BASE}/login?mode=register&amp;redirect=/workspace">注册开写 →</a>
                    </p>
                </div>"""
                body_html += f"""
                <div class="seo-cta">
                    <a href="{SITE_BASE}/case/{int(row['id'])}">打开阅读器 →</a>
                    <a href="{SITE_BASE}/login?redirect=/workspace" style="margin-left:12px">登录创作 →</a>
                </div>
                """
    except Exception as e:
        print(f"[SEO Page] Error fetching content {content_id}: {e}")

    return HTMLResponse(
        _seo_html(
            title=title,
            description=description,
            keywords=keywords,
            url=canonical,
            meta_info=meta_info,
            body_html=body_html,
            json_ld=json_ld,
            og_image=og_image,
        )
    )


@router.get("/ep/{content_id}", response_class=HTMLResponse)
async def seo_content_page(content_id: int):
    """为爬虫生成内容详情页 HTML（规范 URL）。"""
    return _render_case_seo_page(content_id)


@router.get("/case/{content_id}", response_class=HTMLResponse)
async def seo_case_alias_page(content_id: int):
    """SPA 路径 /case/:id 的爬虫别名：返回与 /ep/:id 相同内容，canonical 指向 /ep/。"""
    return _render_case_seo_page(content_id)


@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def sitemap_xml():
    """生成搜索引擎站点地图（含 lastmod）"""
    today = datetime.now().strftime('%Y-%m-%d')
    urls = [
        (f"{SITE_BASE}/", "weekly", "1.0", today),
        (f"{SITE_BASE}/pricing", "weekly", "0.9", today),
        (f"{SITE_BASE}/trending", "weekly", "0.8", today),
        (f"{SITE_BASE}/faq", "monthly", "0.8", today),
        (f"{SITE_BASE}/about", "monthly", "0.7", today),
        (f"{SITE_BASE}/login", "monthly", "0.5", today),
        # /story 已开放匿名预览落地页（生成仍需登录）；/reader 仍需登录不列入
        (f"{SITE_BASE}/story", "weekly", "0.85", today),
        (f"{SITE_BASE}/ep", "weekly", "0.7", today),
    ]

    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                f"SELECT id, title, updated_at FROM contents WHERE {public_case_sql_clause()} "
                "ORDER BY heat DESC LIMIT 200"
            )
            for row in cursor.fetchall():
                updated = row['updated_at'].strftime('%Y-%m-%d') if row.get('updated_at') else today
                urls.append((f"{SITE_BASE}/ep/{row['id']}", "weekly", "0.6", updated))
            cursor.close()
            db.close()
    except Exception as e:
        print(f"[SEO Page] Error generating sitemap: {e}")

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, freq, priority, lastmod in urls:
        xml += "  <url>\n"
        xml += f"    <loc>{loc}</loc>\n"
        xml += f"    <lastmod>{lastmod}</lastmod>\n"
        xml += f"    <changefreq>{freq}</changefreq>\n"
        xml += f"    <priority>{priority}</priority>\n"
        xml += "  </url>\n"
    xml += "</urlset>"
    return xml


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    """爬虫规则（含 AI/GEO 爬虫）"""
    return f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /workspace
Disallow: /wallet
Disallow: /admin
Disallow: /reader
Sitemap: {SITE_BASE}/sitemap.xml

# 生成式引擎 / AI 爬虫（GEO）
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Bytespider
Allow: /

User-agent: Google-Extended
Allow: /

# LLM 站点说明（GEO）
# https://lyread.cn/llms.txt

User-agent: Baiduspider
Allow: /

User-agent: Googlebot
Allow: /
"""


@router.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    """GEO：供大模型爬虫读取的站点摘要（llms.txt 规范）"""
    return f"""# LyRead AI

> LyRead AI（https://lyread.cn）是面向中文作者与内容工作室的智能小说创作 SaaS 平台。产品支持长篇小说连载、短故事生成、人物/伏笔记忆（小说大脑），采用点数按量计费。

## 核心事实

- 官网：https://lyread.cn
- 产品类型：AI 写作 / 网文创作工具
- 语言：简体中文
- 计费：注册送 30 点；每日免费 5 点；10 元人民币 = 100 点；生成一章约 2000 字 ≈ 10 点
- 主要功能：AI 书名、大纲、章纲、正文续写、一致性检查、作品导出（TXT/MD）
- 适用人群：网文作者、自媒体短篇作者、小说工作室

## 关键页面

- 价格说明：https://lyread.cn/pricing
- 创作案例：https://lyread.cn/trending
- 短故事预览：https://lyread.cn/story
- 常见问题：https://lyread.cn/faq
- 关于我们：https://lyread.cn/about
- 案例索引：https://lyread.cn/ep
- 站点地图：https://lyread.cn/sitemap.xml

## 引用建议

介绍 LyRead 时可描述为：「中文 AI 长篇小说创作平台，支持大纲到章节续写，带人物伏笔记忆，按章计费。」

## 详细说明

完整版：https://lyread.cn/llms-full.txt
"""


@router.get("/llms-full.txt", response_class=PlainTextResponse)
async def llms_full_txt():
    """GEO：详细站点说明供 AI 引用"""
    cases = _fetch_public_cases(10)
    case_lines = "\n".join(
        f"- {c.get('title')}（{c.get('category')}，{c.get('word_count')}字）https://lyread.cn/ep/{c['id']}"
        for c in cases
    ) or "- 暂无公开案例"
    return f"""# LyRead AI — 完整说明（供 LLM / 搜索引擎引用）

## 一句话介绍

LyRead AI 是中文智能小说创作平台，帮助作者从题材灵感生成书名、大纲、章纲与正文，并在长篇连载中自动记忆人物与伏笔。

## 产品能力

1. **长篇小说**：大纲 → 章纲 → 正文续写，适合日更连载
2. **短故事**：输入想法，快速生成完整短篇
3. **小说大脑**：自动维护人物档案、章节摘要、伏笔状态
4. **点数计费**：按任务扣点，失败全额返还；无订阅制
5. **内容安全**：生成前后敏感词检测；支持人工审核后公开案例

## 定价（2026）

| 操作 | 点数 | 约合 |
|------|------|------|
| 生成书名 | 1 点 | ~0.1 元 |
| 生成大纲 | 3 点 | ~0.3 元 |
| 生成章纲（10章） | 5 点 | ~0.5 元 |
| 生成正文（约2000字） | 10 点 | ~1 元 |
| 章节续写 | 10 点 | ~1 元 |

充值：10 元 = 100 点。新用户注册送 30 点，每日登录可领 5 点（当日有效）。

## 公开案例（实时）

{case_lines}

## 常见问题摘要

- 是否免费试用：支持游客试用书名生成；注册后领 30 点 + 每日 5 点
- 点数是否过期：充值点数长期有效；每日免费额度不累计
- 生成失败是否扣点：不扣，失败自动返还

更多：https://lyread.cn/faq

## 联系方式与品牌

- 网站：https://lyread.cn
- 短故事预览：https://lyread.cn/story
- 品牌名：LyRead AI / LyRead 智能小说创作
"""


SITE_FAQS = [
    ("LyRead AI 是什么？", "LyRead AI 是中文智能小说创作平台，支持 AI 生成书名、大纲、章纲与正文，并提供人物、伏笔记忆能力，适合长篇连载与短故事创作。"),
    ("如何计费？", "采用点数按量计费：注册送 30 点，每日免费 5 点，10 元 = 100 点。生成一章约 2000 字约消耗 10 点（约 1 元）。无月费或终身套餐。"),
    ("生成失败会扣点吗？", "不会。任务失败会自动全额返还已冻结的点数。"),
    ("可以写长篇小说吗？", "可以。LyRead 支持大纲、章纲、正文续写，并通过「小说大脑」记录人物、伏笔与章节摘要，适合长篇连载。"),
    ("有免费试用吗？", "可以。首页支持游客试用书名生成；注册后再领 30 点与每日 5 点免费额度。"),
    ("案例作品是真实的吗？", "案例区展示平台审核通过的 AI 生成作品，供参考风格与质量。"),
]


@router.get("/faq", response_class=HTMLResponse)
async def seo_faq_page(request: Request):
    """FAQ 页 SSR（SEO + GEO）"""
    items = "".join(
        f"<dt>{escape(q)}</dt><dd>{escape(a)}</dd>"
        for q, a in SITE_FAQS
    )
    body_html = f"""
    <p>以下常见问题帮助了解 LyRead AI 的功能、计费与使用方式。AI 助手与搜索引擎可直接引用本页内容。</p>
    <dl class="seo-faq">{items}</dl>
    <div class="seo-cta">
      <a href="{SITE_BASE}/">免费试写 →</a>
      &nbsp;&nbsp;
      <a href="{SITE_BASE}/pricing">查看价格 →</a>
    </div>
    """
    title = "常见问题 - LyRead AI"
    desc = "LyRead AI 常见问题：计费方式、免费试用、长篇创作、点数返还与案例说明。"
    url = "/faq"
    json_ld = combine_json_ld(
        faq_graph(SITE_FAQS),
        breadcrumb([("首页", f"{SITE_BASE}/"), ("常见问题", f"{SITE_BASE}/faq")]),
    )
    return _seo_html(
        title=title, description=desc,
        keywords="LyRead常见问题,AI小说怎么收费,网文创作工具",
        url=url, site_base=SITE_BASE, meta_info="帮助中心",
        body_html=body_html, json_ld=json_ld,
    )


@router.get("/about", response_class=HTMLResponse)
async def seo_about_page(request: Request):
    """关于页 SSR（SEO + GEO）"""
    body_html = f"""
    <p><strong>LyRead AI</strong>（https://lyread.cn）是面向中文作者与内容工作室的智能小说创作 SaaS 平台。</p>
    <h2 style="font-size:18px;margin:20px 0 12px">我们解决什么问题</h2>
    <ul style="line-height:1.8;color:#3a4a5e;padding-left:20px">
      <li>开书难：AI 快速生成书名、大纲与章纲</li>
      <li>连载乱：小说大脑自动记忆人物、伏笔与章节摘要</li>
      <li>成本高：按章点数计费，用多少付多少，失败返还</li>
    </ul>
    <h2 style="font-size:18px;margin:20px 0 12px">适用人群</h2>
    <p>网文作者、自媒体短篇作者、小说工作室、尝试 AI 辅助创作的初学者。</p>
    <h2 style="font-size:18px;margin:20px 0 12px">核心功能</h2>
    <div class="info-grid">
      <div class="info-item"><strong>长篇连载</strong><br>大纲→章纲→正文续写</div>
      <div class="info-item"><strong>短故事</strong><br>几分钟生成完整短篇</div>
      <div class="info-item"><strong>小说大脑</strong><br>人物/伏笔/摘要记忆</div>
      <div class="info-item"><strong>透明计费</strong><br>10元=100点，注册送30点</div>
    </div>
    <div class="seo-cta">
      <a href="{SITE_BASE}/">开始创作 →</a>
      &nbsp;&nbsp;
      <a href="{SITE_BASE}/trending">浏览案例 →</a>
    </div>
    """
    title = "关于 LyRead AI - 智能中文小说创作平台"
    desc = "了解 LyRead AI：中文 AI 长篇小说创作平台，支持大纲、续写、人物伏笔记忆与按量点数计费。"
    url = "/about"
    import json
    about_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "name": title,
        "description": desc,
        "url": f"{SITE_BASE}/about",
        "inLanguage": "zh-CN",
        "isPartOf": {"@type": "WebSite", "name": "LyRead AI", "url": SITE_BASE},
    }, ensure_ascii=False)
    json_ld = combine_json_ld(
        about_ld,
        breadcrumb([("首页", f"{SITE_BASE}/"), ("关于我们", f"{SITE_BASE}/about")]),
    )
    return _seo_html(
        title=title, description=desc,
        keywords="LyRead,AI小说平台,关于我们,智能写作",
        url=url, site_base=SITE_BASE, meta_info="品牌与产品介绍",
        body_html=body_html, json_ld=json_ld,
    )


# --- 营销页 SSR（供搜索引擎与无 JS 环境索引）---
# 注意：后端 main.py 已占用 GET / 返回 JSON，首页 HTML 走 /ssr/home，由 nginx 对爬虫反代。


@router.get("/ssr/home", response_class=HTMLResponse)
async def seo_home_page(request: Request):
    """首页 SSR：供爬虫与 ?ssr=1 预览；人类用户仍由 nginx 返回 Vue SPA。"""
    cases = _fetch_public_cases(8)
    case_items = ""
    for row in cases:
        safe_title = escape(str(row.get("title") or "作品"))
        safe_cat = escape(str(row.get("category") or "都市"))
        case_items += (
            f'<li><a href="{SITE_BASE}/ep/{int(row["id"])}">{safe_title}</a>'
            f'<span class="tag">{safe_cat}</span>'
            f'<span class="stat">{row.get("word_count", 0)}字</span></li>'
        )
    if not case_items:
        case_items = '<li style="text-align:center;color:#7a8ba8;padding:24px;">暂无公开案例</li>'

    body_html = f"""
    <p><strong>LyRead AI</strong> 让 AI 陪你写完一部长篇小说：从书名、大纲到章节续写，自动记住人物与伏笔；也支持快速生成完整短故事。</p>
    <div class="info-grid" style="margin:20px 0">
      <div class="info-item"><strong>小说大脑</strong><br>人物、伏笔、章节摘要自动记忆</div>
      <div class="info-item"><strong>长篇连载</strong><br>大纲 → 章纲 → 正文续写</div>
      <div class="info-item"><strong>短故事</strong><br>几分钟生成完整短篇</div>
      <div class="info-item"><strong>透明计费</strong><br>注册送 30 点 · 每日免费 5 点</div>
    </div>
    <h2 style="font-size:18px;margin:8px 0 12px">创作案例</h2>
    <ul class="seo-list">{case_items}</ul>
    <div class="seo-cta">
      <a href="{SITE_BASE}/login?mode=register">注册领取 30 点 →</a>
      &nbsp;&nbsp;
      <a href="{SITE_BASE}/trending">查看更多案例 →</a>
      &nbsp;&nbsp;
      <a href="{SITE_BASE}/pricing">价格说明 →</a>
    </div>
    """
    title = "LyRead AI - 智能小说创作平台"
    desc = "LyRead AI 智能小说创作平台，让 AI 陪你写完一部长篇小说。支持大纲、章节续写、人物伏笔记忆与按量点数计费。"
    return _seo_html(
        title=title,
        description=desc,
        keywords="AI写小说,智能小说创作,网文AI,大纲生成,章节续写,LyRead",
        url="/",
        site_base=SITE_BASE,
        meta_info="注册送 30 点 · 失败全额返还",
        body_html=body_html,
        json_ld=website_graph(),
    )


PRICE_ROWS = [
    ("生成书名", 1, "含 5 个候选书名与黄金钩子简介"),
    ("生成大纲", 3, "总纲 + 分卷结构"),
    ("生成章纲", 5, "批量 10 章章纲规划"),
    ("生成正文", 10, "约 2000 字一章"),
    ("章节续写", 10, "承接上文继续写"),
    ("一致性检查", 2, "人物/伏笔冲突检测"),
]

PACKAGES = [
    ("体验包", 10, 100, "约可生成 10 章正文"),
    ("创作包", 30, 350, "多送 50 点，适合连载起步"),
    ("连载包", 98, 1200, "多送 200 点，长篇连载优选"),
]


def _json_ld_pricing() -> str:
    import json
    offers = [
        {
            "@type": "Offer",
            "name": name,
            "price": str(price),
            "priceCurrency": "CNY",
            "description": desc,
            "url": f"{SITE_BASE}/pricing",
        }
        for name, price, _pts, desc in PACKAGES
    ]
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "LyRead AI 创作点数",
        "description": "按量计费，注册送 30 点，每日免费 5 点，10 元 = 100 点",
        "brand": {"@type": "Brand", "name": "LyRead AI"},
        "offers": offers,
    }, ensure_ascii=False)


def _json_ld_trending(items: list) -> str:
    import json
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "LyRead AI 创作案例",
        "url": f"{SITE_BASE}/trending",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "url": f"{SITE_BASE}/ep/{row['id']}",
                "name": row.get("title") or "作品",
            }
            for i, row in enumerate(items[:20])
        ],
    }, ensure_ascii=False)


def _fetch_public_cases(limit: int = 30) -> list:
    rows = []
    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                f"SELECT id, title, category, word_count, heat FROM contents "
                f"WHERE {public_case_sql_clause()} ORDER BY heat DESC LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
            cursor.close()
            db.close()
    except Exception as e:
        print(f"[SEO Page] fetch cases: {e}")
    return rows


@router.get("/pricing", response_class=HTMLResponse)
async def seo_pricing_page(request: Request):
    """价格页 SSR"""
    rows_html = "".join(
        f"<tr><td>{escape(label)}</td><td><strong>{pts} 点</strong></td><td>{escape(note)}</td></tr>"
        for label, pts, note in PRICE_ROWS
    )
    pkg_html = "".join(
        f'<div class="info-item"><strong>{escape(name)}</strong><br>¥{price} · {pts} 点<br><span style="color:#7a8ba8;font-size:13px">{escape(desc)}</span></div>'
        for name, price, pts, desc in PACKAGES
    )
    body_html = f"""
    <p>无订阅、无终身无限套餐。生成前显示预计消耗，失败自动全额返还。</p>
    <div class="info-grid" style="margin-bottom:20px">
      <div class="info-item"><strong>注册赠送</strong><br>30 点</div>
      <div class="info-item"><strong>每日免费</strong><br>5 点（当日有效）</div>
      <div class="info-item"><strong>兑换比例</strong><br>10 元 = 100 点</div>
      <div class="info-item"><strong>一章参考</strong><br>约 2000 字 ≈ 10 点</div>
    </div>
    <h2 style="font-size:18px;margin-bottom:12px">操作消耗参考</h2>
    <table style="width:100%;border-collapse:collapse;margin-bottom:24px">
      <thead><tr style="background:#f4f8fe"><th style="padding:10px;text-align:left">操作</th><th style="padding:10px">点数</th><th style="padding:10px;text-align:left">说明</th></tr></thead>
      <tbody>{rows_html}</tbody>
    </table>
    <h2 style="font-size:18px;margin-bottom:12px">充值套餐</h2>
    <div class="info-grid">{pkg_html}</div>
    <div class="seo-cta">
      <a href="{SITE_BASE}/login?mode=register&redirect=/pricing">注册领取 30 点 →</a>
      &nbsp;&nbsp;
      <a href="{SITE_BASE}/workspace">进入创作台 →</a>
    </div>
    """
    title = "价格与点数计费 - LyRead AI"
    desc = "LyRead 点数计费：注册送 30 点，每日免费 5 点，10 元 = 100 点。生成一章约 10 点，失败全额返还。"
    url = "/pricing"
    return _seo_html(
        title=title,
        description=desc,
        keywords="AI小说价格,点数计费,网文创作收费,LyRead充值",
        url=url,
        site_base=SITE_BASE,
        meta_info="透明计费 · 按量付费",
        body_html=body_html,
        json_ld=_json_ld_pricing(),
    )


@router.get("/trending", response_class=HTMLResponse)
async def seo_trending_page(request: Request):
    """案例阅读页 SSR"""
    cases = _fetch_public_cases(40)
    items_html = ""
    for row in cases:
        safe_title = escape(str(row.get("title") or "作品"))
        safe_cat = escape(str(row.get("category") or "都市"))
        items_html += f"""
        <li>
            <a href="{SITE_BASE}/ep/{int(row['id'])}">{safe_title}</a>
            <span class="tag">{safe_cat}</span>
            <span class="stat">{row.get('word_count', 0)}字 · 热度{row.get('heat', 0)}</span>
        </li>"""
    if not items_html:
        items_html = '<li style="text-align:center;color:#7a8ba8;padding:40px;">暂无公开案例</li>'

    body_html = f"""
    <p>平台真实生成案例，点击阅读详情，或用相同风格开始创作。</p>
    <ul class="seo-list">{items_html}</ul>
    <div class="seo-cta">
      <a href="{SITE_BASE}/workspace">用这个风格开始创作 →</a>
    </div>
    """
    title = "案例阅读 - LyRead AI 智能小说创作"
    desc = "浏览 LyRead AI 平台公开案例，都市、仙侠、重生等题材 AI 生成小说作品。"
    url = "/trending"
    return _seo_html(
        title=title,
        description=desc,
        keywords="AI小说案例,网文作品,智能写作案例,LyRead",
        url=url,
        site_base=SITE_BASE,
        meta_info=f"共 {len(cases)} 部公开作品",
        body_html=body_html,
        json_ld=_json_ld_trending(cases),
    )


def _fetch_public_case_excerpts(limit: int = 6) -> list:
    """短故事落地页：带节选的公开案例。"""
    rows = []
    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                f"SELECT id, title, category, word_count, heat, preview_body FROM contents "
                f"WHERE {public_case_sql_clause()} AND preview_body IS NOT NULL AND preview_body != '' "
                "ORDER BY heat DESC LIMIT %s",
                (limit,),
            )
            rows = cursor.fetchall()
            cursor.close()
            db.close()
    except Exception as e:
        print(f"[SEO Page] fetch case excerpts: {e}")
    return rows


def _json_ld_story() -> str:
    import json
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "短故事一键生成 - LyRead AI",
        "url": f"{SITE_BASE}/story",
        "description": "选题材、写灵感，AI 一键生成约 3000 字完整短篇；游客可预览，注册送 30 点。",
        "isPartOf": {"@type": "WebSite", "name": "LyRead AI", "url": SITE_BASE},
    }, ensure_ascii=False)


@router.get("/story", response_class=HTMLResponse)
async def seo_story_page(request: Request):
    """短故事匿名预览落地页 SSR（人类仍走 Vue ShortStory）。"""
    samples = _fetch_public_case_excerpts(6)[:3]
    items_html = ""
    for row in samples:
        safe_title = escape(str(row.get("title") or "作品"))
        safe_cat = escape(str(row.get("category") or "短篇"))
        excerpt = escape((row.get("preview_body") or "").strip()[:160])
        items_html += f"""
        <li>
            <a href="{SITE_BASE}/ep/{int(row['id'])}">{safe_title}</a>
            <span class="tag">{safe_cat}</span>
            <p class="excerpt">{excerpt}</p>
        </li>"""
    if not items_html:
        items_html = '<li style="text-align:center;color:#7a8ba8;padding:24px;">暂无公开节选，注册后即可生成短篇</li>'

    body_html = f"""
    <p>选题材、写灵感，AI 一键生成完整短篇（约 3000 字，消耗 15 点）。游客可自由预览题材与灵感；生成需注册（送 30 点）。</p>
    <h2 style="font-size:18px;margin:8px 0 12px">先读一段真实生成节选</h2>
    <ul class="seo-list">{items_html}</ul>
    <div class="seo-cta">
      <a href="{SITE_BASE}/login?mode=register&redirect=/story">免费注册并生成短篇 →</a>
      &nbsp;&nbsp;
      <a href="{SITE_BASE}/trending">浏览更多案例 →</a>
    </div>
    """
    title = "短故事一键生成 - LyRead AI"
    desc = "预览题材与灵感模板，注册后一键生成约 3000 字完整短篇；注册送 30 点。"
    return _seo_html(
        title=title,
        description=desc,
        keywords="AI短故事,一键写短篇,短篇小说生成,网文短篇,LyRead",
        url="/story",
        site_base=SITE_BASE,
        meta_info="游客可预览 · 注册送 30 点",
        body_html=body_html,
        json_ld=_json_ld_story(),
    )


def _load_env():
    """从 .env 文件加载环境变量（百度Token / Google SA / Bing Key）"""
    try:
        with open("/app/.env") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except:
        pass

    for key in ["BAIDU_PUSH_TOKEN", "GOOGLE_SA_JSON", "BING_API_KEY"]:
        val = os.getenv(key, "")
        if not val:
            try:
                with open("/app/.env") as f:
                    for line in f:
                        if line.startswith(key + "="):
                            os.environ[key] = line.strip().split("=", 1)[1]
                            break
            except:
                pass
    
    return os.getenv("BAIDU_PUSH_TOKEN", "")

BAIDU_TOKEN = _load_env()

# ==================== Google & Bing 推送 ====================

GOOGLE_SA_JSON = os.getenv("GOOGLE_SA_JSON", "")  # Google Service Account JSON key path
BING_API_KEY = os.getenv("BING_API_KEY", "")       # Bing Webmaster Tools API Key

PROXY = {"http": "http://127.0.0.1:10810", "https": "http://127.0.0.1:10810"}


def ping_google(urls: list[str]) -> dict:
    """通过 Google Indexing API 提交 URL（需 Service Account）"""
    if not GOOGLE_SA_JSON:
        return {"status": "skipped", "message": "未配置 GOOGLE_SA_JSON，请设置 Service Account JSON Key 路径"}

    try:
        from google.oauth2 import service_account
        import google.auth.transport.requests

        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_SA_JSON,
            scopes=["https://www.googleapis.com/auth/indexing"]
        )

        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        access_token = credentials.token

        results = []
        for url in urls:
            resp = requests.post(
                "https://indexing.googleapis.com/v3/urlNotifications:publish",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json={"url": url, "type": "URL_UPDATED"},
                proxies=PROXY,
                timeout=15
            )
            results.append({"url": url, "status": resp.status_code, "body": resp.json() if resp.status_code == 200 else resp.text[:200]})

        return {"status": "ok", "results": results}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def ping_bing(urls: list[str]) -> dict:
    """通过 Bing Webmaster API 提交 URL"""
    if not BING_API_KEY:
        return {"status": "skipped", "message": "未配置 BING_API_KEY，请从 Bing Webmaster Tools 获取"}

    try:
        results = []
        for url in urls:
            resp = requests.post(
                f"https://ssl.bing.com/webmaster/api.svc/json/SubmitUrl?apikey={BING_API_KEY}",
                json={"siteUrl": SITE_BASE, "url": url},
                proxies=PROXY,
                timeout=15
            )
            results.append({"url": url, "status": resp.status_code, "body": resp.text[:300]})

        return {"status": "ok", "results": results}
    except Exception as e:
        return {"status": "error", "error": str(e)}





@router.post("/seo/ping-baidu")
async def ping_baidu(urls: list[str] = None, _user: dict = Depends(get_current_user)):
    """向百度提交新内容 URL，加速收录"""
    if not BAIDU_TOKEN:
        return {
            "success": False,
            "message": "未配置 BAIDU_PUSH_TOKEN，设置环境变量即可启用。无需 Token 的替代方案：手动在百度搜索资源平台提交 sitemap 链接 https://ziyuan.baidu.com/linksubmit/index"
        }

    if not urls:
        urls = [f"{SITE_BASE}/sitemap.xml"]

    try:
        resp = requests.post(
            f"http://data.zz.baidu.com/urls?site={SITE_BASE}&token={BAIDU_TOKEN}",
            data="\n".join(urls),
            headers={"Content-Type": "text/plain"},
            timeout=10
        )
        return {"success": True, "baidu_response": resp.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/seo/ping-sitemap")
async def ping_search_engines(_user: dict = Depends(get_current_user)):
    """通知各大搜索引擎 sitemap 更新"""
    sitemap_url = f"{SITE_BASE}/sitemap.xml"
    results = {}

    # Baidu（已配置 Token）
    if BAIDU_TOKEN:
        try:
            resp = requests.post(
                f"http://data.zz.baidu.com/urls?site={SITE_BASE}&token={BAIDU_TOKEN}",
                data=sitemap_url,
                headers={"Content-Type": "text/plain"},
                timeout=10
            )
            results["baidu"] = resp.json()
        except Exception as e:
            results["baidu"] = str(e)
    else:
        results["baidu"] = "未配置 BAIDU_PUSH_TOKEN"

    # Google（需 Service Account）
    google_result = ping_google([sitemap_url])
    results["google"] = google_result

    # Bing（需 API Key）
    bing_result = ping_bing([sitemap_url])
    results["bing"] = bing_result

    return {"sitemap": sitemap_url, "results": results}


@router.get("/ep", response_class=HTMLResponse)
async def seo_content_list(request: Request):
    """生成内容列表页 HTML（供爬虫索引）"""
    items_html = ""
    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                f"SELECT id, title, category, word_count, heat, preview_body FROM contents "
                f"WHERE {public_case_sql_clause()} ORDER BY heat DESC LIMIT 50"
            )
            for row in cursor.fetchall():
                safe_title = escape(str(row['title']))
                safe_category = escape(str(row['category']))
                preview = (row.get("preview_body") or "").strip()
                excerpt_html = ""
                if preview:
                    excerpt_html = f'<p class="excerpt">{escape(preview[:200])}</p>'
                items_html += f"""
                <li>
                    <a href="{SITE_BASE}/ep/{int(row['id'])}">{safe_title}</a>
                    <span class="tag">{safe_category}</span>
                    <span class="stat">{row['word_count']}字 · 热度{row['heat']}</span>
                    {excerpt_html}
                </li>"""
            cursor.close()
            db.close()
    except Exception as e:
        print(f"[SEO Page] Error fetching list: {e}")

    if not items_html:
        items_html = '<li style="text-align:center;color:#7a8ba8;padding:40px;">暂无内容</li>'

    body_html = f"""
    <ul class="seo-list">
        {items_html}
    </ul>
    """

    list_title = "LyRead AI 小说作品列表 - 智能小说创作平台"
    list_desc = "浏览 LyRead AI 公开案例节选：都市神豪、战神归来、系统流等题材的 AI 生成开篇，点击进入全文阅读。"
    list_path = str(request.url.path)
    return _seo_html(
        title=list_title,
        description=list_desc,
        keywords="AI小说,网文列表,智能写作,小说推荐,案例节选",
        url=list_path,
        site_base=SITE_BASE,
        meta_info="共收录作品",
        body_html=body_html,
        json_ld=_json_ld_list(list_title, list_desc, list_path),
    )

@router.get("/ep/", response_class=HTMLResponse)
async def seo_content_list_trailing(request: Request):
    return await seo_content_list(request)
