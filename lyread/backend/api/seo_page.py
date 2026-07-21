"""
🌐 SEO 落地页生成器 - 为搜索引擎提供可索引的 HTML
让爬虫能抓到 LyRead 的内容页面
"""

import os
from html import escape
from urllib.parse import quote
import requests
import mysql.connector
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from settings import database_config
from api.auth import get_current_user
from services.case_quality import public_case_sql_clause
from services.seo_schema import breadcrumb, combine_json_ld, faq_graph
from services.seo_content import (
    COMPARE_PAGES,
    GUIDE_PAGES,
    GENRE_PAGES,
    all_static_seo_paths,
)

router = APIRouter()

SITE_BASE = os.getenv("SITE_URL", "https://lyread.cn").rstrip("/")

def get_db():
    try:
        return mysql.connector.connect(**database_config())
    except Exception:
        return None


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
    <meta property="og:image" content="{site_base}/images/og-share.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{site_base}{url}">
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
                <a href="{site_base}/privacy">隐私政策</a>
                <a href="{site_base}/terms">用户协议</a>
            </nav>
            <p>© LyRead AI 智能小说创作平台</p>
        </div>
    </div>
</body>
</html>"""


def _json_ld_article(title: str, description: str, url_path: str, genre: str = "", word_count: int = 0) -> str:
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


@router.get("/ep/{content_id}", response_class=HTMLResponse)
async def seo_content_page(content_id: int, request: Request):
    """为爬虫生成内容详情页 HTML"""
    title = "LyRead AI - 智能小说创作平台"
    description = "LyRead AI智能小说创作平台，AI生成爆款网文"
    keywords = "AI写小说,网文创作,智能写作"
    body_html = '<p style="color: #7a8ba8; text-align: center; padding: 40px;">内容未找到</p>'
    meta_info = ""
    url = str(request.url.path)
    json_ld = _json_ld_article(title, description, url)

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
                title = f"{safe_title} - LyRead AI 小说作品"
                description = f"{safe_title} - {safe_category}类型，{row['word_count']}字，热度{row['heat']}，AI智能创作平台"
                keywords = f"小说,{safe_category},{safe_title},AI写小说,网文"
                meta_info = f"分类：{safe_category} ｜ 字数：{row['word_count']:,} ｜ 热度：{row['heat']}"
                json_ld = combine_json_ld(
                    _json_ld_article(safe_title, description, url, genre=safe_category, word_count=int(row.get('word_count') or 0)),
                    breadcrumb([
                        ("首页", f"{SITE_BASE}/"),
                        ("案例阅读", f"{SITE_BASE}/trending"),
                        (safe_title, f"{SITE_BASE}{url}"),
                    ]),
                )
                body_html = f"""
                <div class="info-grid">
                    <div class="info-item"><strong>分类</strong><br>{safe_category}</div>
                    <div class="info-item"><strong>字数</strong><br>{row['word_count']:,}</div>
                    <div class="info-item"><strong>热度</strong><br>{row['heat']}</div>
                    <div class="info-item"><strong>评分</strong><br>{row.get('score', 'N/A')}</div>
                </div>"""
                preview = row.get("preview_body") or ""
                if preview:
                    safe_preview = escape(preview[:6000]).replace("\n", "<br>")
                    body_html += f"""
                <div style="margin-top:24px;line-height:1.9;color:#2a3a4e;white-space:normal">
                    <h2 style="font-size:18px;margin-bottom:12px;color:#1e2a3a">正文节选</h2>
                    <div style="background:#f8fafc;padding:20px;border-radius:12px;border:1px solid #e8f0fa">{safe_preview}</div>
                </div>"""
                body_html += f"""
                <div class="seo-cta">
                    <a href="{SITE_BASE}/login?redirect=/workspace">登录 LyRead 创作你的作品 →</a>
                </div>
                """
    except Exception as e:
        print(f"[SEO Page] Error fetching content {content_id}: {e}")

    return PAGE_TEMPLATE.format(
        title=title,
        description=description,
        keywords=keywords,
        url=url,
        site_base=SITE_BASE,
        meta_info=meta_info,
        body_html=body_html,
        json_ld=json_ld,
    )


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
        (f"{SITE_BASE}/privacy", "yearly", "0.4", today),
        (f"{SITE_BASE}/terms", "yearly", "0.4", today),
        (f"{SITE_BASE}/login", "monthly", "0.5", today),
        (f"{SITE_BASE}/story", "weekly", "0.7", today),
        (f"{SITE_BASE}/reader", "weekly", "0.7", today),
        (f"{SITE_BASE}/ep", "weekly", "0.7", today),
    ]
    for path, freq, priority in all_static_seo_paths():
        urls.append((f"{SITE_BASE}{path}", freq, priority, today))

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
                urls.append((f"{SITE_BASE}/case/{row['id']}", "weekly", "0.55", updated))
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
- 常见问题：https://lyread.cn/faq
- 关于我们：https://lyread.cn/about
- 工具对比：https://lyread.cn/compare
- 创作教程：https://lyread.cn/guide
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
      <a href="{SITE_BASE}/">免费生成书名 →</a>
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
    return PAGE_TEMPLATE.format(
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
    return PAGE_TEMPLATE.format(
        title=title, description=desc,
        keywords="LyRead,AI小说平台,关于我们,智能写作",
        url=url, site_base=SITE_BASE, meta_info="品牌与产品介绍",
        body_html=body_html, json_ld=json_ld,
    )


@router.get("/privacy", response_class=HTMLResponse)
async def seo_privacy_page(request: Request):
    """隐私政策 SSR"""
    body_html = f"""
    <p>更新日期：2026-07-21。LyRead AI（https://lyread.cn）重视用户隐私保护。使用本平台即表示您同意本政策。</p>
    <h2 style="font-size:18px;margin:20px 0 12px">我们收集的信息</h2>
    <ul style="line-height:1.8;color:#3a4a5e;padding-left:20px">
      <li><strong>账号信息：</strong>注册邮箱、昵称（您主动提供）</li>
      <li><strong>创作内容：</strong>您输入的题材、大纲、章节正文等，用于提供 AI 生成服务</li>
      <li><strong>交易信息：</strong>充值订单、点数变动记录（支付由支付宝等第三方处理，我们不存储完整支付密码）</li>
      <li><strong>技术日志：</strong>IP、浏览器类型、访问时间，用于安全与故障排查</li>
    </ul>
    <h2 style="font-size:18px;margin:20px 0 12px">信息如何使用</h2>
    <ul style="line-height:1.8;color:#3a4a5e;padding-left:20px">
      <li>提供、维护与改进 AI 创作服务（含小说大脑记忆功能）</li>
      <li>处理充值、退款与客服请求</li>
      <li>经您同意后公开展示的案例作品（可在提交审核时选择）</li>
      <li>遵守法律法规要求</li>
    </ul>
    <h2 style="font-size:18px;margin:20px 0 12px">信息存储与安全</h2>
    <p>数据存储于中华人民共和国境内服务器，采用加密传输（HTTPS）与访问控制。我们不会向无关第三方出售您的个人信息。</p>
    <h2 style="font-size:18px;margin:20px 0 12px">您的权利</h2>
    <p>您可申请查阅、更正或删除账号与创作数据。注销账号请联系客服或通过设置页面操作（功能陆续开放）。</p>
    <h2 style="font-size:18px;margin:20px 0 12px">联系我们</h2>
    <p>隐私相关问题请通过网站「关于我们」页面所列方式联系。</p>
    <div class="seo-cta">
      <a href="{SITE_BASE}/terms">查看用户协议 →</a>
      &nbsp;&nbsp;
      <a href="{SITE_BASE}/">返回首页 →</a>
    </div>
    """
    title = "隐私政策 - LyRead AI"
    desc = "LyRead AI 隐私政策：说明我们如何收集、使用与保护您的账号、创作内容与交易信息。"
    url = "/privacy"
    json_ld = breadcrumb([("首页", f"{SITE_BASE}/"), ("隐私政策", f"{SITE_BASE}/privacy")])
    return PAGE_TEMPLATE.format(
        title=title, description=desc,
        keywords="LyRead隐私政策,用户数据保护",
        url=url, site_base=SITE_BASE, meta_info="法律与合规",
        body_html=body_html, json_ld=json_ld,
    )


@router.get("/terms", response_class=HTMLResponse)
async def seo_terms_page(request: Request):
    """用户协议 SSR"""
    body_html = f"""
    <p>更新日期：2026-07-21。欢迎使用 LyRead AI。请在使用前仔细阅读本协议。</p>
    <h2 style="font-size:18px;margin:20px 0 12px">服务说明</h2>
    <p>LyRead AI 提供 AI 辅助小说创作服务，包括书名生成、大纲、章纲、正文续写、短故事生成等。生成内容由 AI 模型产出，平台不对内容的文学质量、版权归属或商业结果作保证。</p>
    <h2 style="font-size:18px;margin:20px 0 12px">账号与点数</h2>
    <ul style="line-height:1.8;color:#3a4a5e;padding-left:20px">
      <li>注册即获赠体验点数；充值点数不可转让、不可兑换现金（法律另有规定除外）</li>
      <li>生成任务失败将全额返还已冻结点数</li>
      <li>禁止利用漏洞刷点、批量注册、恶意攻击系统</li>
    </ul>
    <h2 style="font-size:18px;margin:20px 0 12px">内容规范</h2>
    <p>您不得利用本平台生成、发布违反法律法规、侵犯他人权益、含有色情暴力政治敏感等内容。平台有权删除违规内容并暂停或终止账号。</p>
    <h2 style="font-size:18px;margin:20px 0 12px">知识产权</h2>
    <p>您对输入的原创设定与经人工实质性修改后的输出内容享有相应权利。平台服务界面、技术与品牌标识归 LyRead 所有。提交公开展示的案例，您授权平台在站内展示用于宣传与 SEO。</p>
    <h2 style="font-size:18px;margin:20px 0 12px">免责声明</h2>
    <p>AI 生成内容仅供参考，投稿前请自行审核合规性与原创性。因不可抗力、第三方服务中断导致的服务暂停，平台将尽力恢复但不承担间接损失。</p>
    <h2 style="font-size:18px;margin:20px 0 12px">协议变更</h2>
    <p>我们可能更新本协议，重大变更将在站内公告。继续使用即视为接受更新后的条款。</p>
    <div class="seo-cta">
      <a href="{SITE_BASE}/privacy">查看隐私政策 →</a>
      &nbsp;&nbsp;
      <a href="{SITE_BASE}/">返回首页 →</a>
    </div>
    """
    title = "用户协议 - LyRead AI"
    desc = "LyRead AI 用户服务协议：账号规则、点数计费、内容规范与知识产权说明。"
    url = "/terms"
    json_ld = breadcrumb([("首页", f"{SITE_BASE}/"), ("用户协议", f"{SITE_BASE}/terms")])
    return PAGE_TEMPLATE.format(
        title=title, description=desc,
        keywords="LyRead用户协议,服务条款",
        url=url, site_base=SITE_BASE, meta_info="法律与合规",
        body_html=body_html, json_ld=json_ld,
    )


def _sections_html(sections: list) -> str:
    parts = []
    for title, body in sections:
        if isinstance(body, str) and body.strip().startswith("<"):
            inner = body
        else:
            inner = f"<p>{escape(str(body))}</p>"
        parts.append(
            f'<h2 style="font-size:18px;margin:24px 0 12px;color:#1e2a3a">{escape(title)}</h2>{inner}'
        )
    return "".join(parts)


def _render_article_page(meta: dict, url: str, crumbs: list[tuple[str, str]]) -> str:
    h1 = meta.get("h1") or meta["title"]
    body_html = f"<h2 style='font-size:20px;margin-bottom:16px'>{escape(h1)}</h2>"
    body_html += _sections_html(meta["sections"])
    if meta.get("faqs"):
        body_html += '<h2 style="font-size:18px;margin:24px 0 12px">常见问题</h2><dl class="seo-faq">'
        for q, a in meta["faqs"]:
            body_html += f"<dt>{escape(q)}</dt><dd>{escape(a)}</dd>"
        body_html += "</dl>"
    body_html += f"""
    <div class="seo-cta">
      <a href="{SITE_BASE}/">免费生成书名 →</a>
      &nbsp;&nbsp;
      <a href="{SITE_BASE}/pricing">查看价格 →</a>
      &nbsp;&nbsp;
      <a href="{SITE_BASE}/trending">浏览案例 →</a>
    </div>
    """
    json_ld_parts = [breadcrumb(crumbs)]
    if meta.get("faqs"):
        json_ld_parts.append(faq_graph(meta["faqs"]))
    return PAGE_TEMPLATE.format(
        title=meta["title"],
        description=meta["description"],
        keywords=meta.get("keywords", "AI写小说,LyRead"),
        url=url,
        site_base=SITE_BASE,
        meta_info="LyRead AI 创作指南",
        body_html=body_html,
        json_ld=combine_json_ld(*json_ld_parts),
    )


@router.get("/compare", response_class=HTMLResponse)
async def seo_compare_index():
    items = "".join(
        f'<li><a href="{SITE_BASE}/compare/{slug}">{escape(p["title"])}</a></li>'
        for slug, p in COMPARE_PAGES.items()
    )
    body = f"""
    <p>客观对比 LyRead 与主流 AI 写小说工具，帮你按创作场景选型。</p>
    <ul class="seo-list">{items}</ul>
    <div class="seo-cta"><a href="{SITE_BASE}/">免费试用 LyRead →</a></div>
    """
    return PAGE_TEMPLATE.format(
        title="AI写小说工具对比 - LyRead AI",
        description="LyRead 与笔灵、蛙趣拼文、ChatGPT 等工具对比：长篇记忆、计费、工作流与适用人群。",
        keywords="AI写小说对比,笔灵,蛙蛙写作,ChatGPT写小说",
        url="/compare", site_base=SITE_BASE, meta_info="工具对比",
        body_html=body,
        json_ld=breadcrumb([("首页", f"{SITE_BASE}/"), ("工具对比", f"{SITE_BASE}/compare")]),
    )


@router.get("/compare/{slug}", response_class=HTMLResponse)
async def seo_compare_page(slug: str):
    meta = COMPARE_PAGES.get(slug)
    if not meta:
        raise HTTPException(status_code=404, detail="页面不存在")
    return _render_article_page(
        meta,
        f"/compare/{slug}",
        [("首页", f"{SITE_BASE}/"), ("工具对比", f"{SITE_BASE}/compare"), (meta["h1"], f"{SITE_BASE}/compare/{slug}")],
    )


@router.get("/guide", response_class=HTMLResponse)
async def seo_guide_index():
    items = "".join(
        f'<li><a href="{SITE_BASE}/guide/{slug}">{escape(p["title"])}</a></li>'
        for slug, p in GUIDE_PAGES.items()
    )
    body = f"""
    <p>AI 写小说教程：从入门、大纲章纲到日更续写实操。</p>
    <ul class="seo-list">{items}</ul>
    <div class="seo-cta"><a href="{SITE_BASE}/workspace">进入创作台 →</a></div>
    """
    return PAGE_TEMPLATE.format(
        title="AI写小说教程 - LyRead AI 创作指南",
        description="AI 小说创作教程：入门开书、大纲章纲、日更续写技巧与点数成本估算。",
        keywords="AI写小说教程,网文创作,章纲,日更",
        url="/guide", site_base=SITE_BASE, meta_info="创作教程",
        body_html=body,
        json_ld=breadcrumb([("首页", f"{SITE_BASE}/"), ("创作教程", f"{SITE_BASE}/guide")]),
    )


@router.get("/guide/{slug}", response_class=HTMLResponse)
async def seo_guide_page(slug: str):
    meta = GUIDE_PAGES.get(slug)
    if not meta:
        raise HTTPException(status_code=404, detail="页面不存在")
    return _render_article_page(
        meta,
        f"/guide/{slug}",
        [("首页", f"{SITE_BASE}/"), ("创作教程", f"{SITE_BASE}/guide"), (meta["h1"], f"{SITE_BASE}/guide/{slug}")],
    )


@router.get("/genre/{slug}", response_class=HTMLResponse)
async def seo_genre_page(slug: str):
    genre = GENRE_PAGES.get(slug)
    if not genre:
        raise HTTPException(status_code=404, detail="题材不存在")
    cases = []
    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                f"SELECT id, title, word_count, heat FROM contents WHERE {public_case_sql_clause()} "
                "AND category=%s ORDER BY heat DESC LIMIT 20",
                (genre["category"],),
            )
            cases = cursor.fetchall()
            cursor.close()
            db.close()
    except Exception as e:
        print(f"[SEO Page] genre cases: {e}")

    items = "".join(
        f'<li><a href="{SITE_BASE}/ep/{int(c["id"])}">{escape(str(c.get("title") or "作品"))}</a>'
        f'<span class="stat">{c.get("word_count", 0)}字 · 热度{c.get("heat", 0)}</span></li>'
        for c in cases
    ) or '<li style="color:#7a8ba8">暂无该题材公开案例，欢迎创作并提交审核。</li>'

    body_html = f"""
    <p>{escape(genre["intro"])}</p>
    <h2 style="font-size:18px;margin:20px 0 12px">相关案例</h2>
    <ul class="seo-list">{items}</ul>
    <div class="seo-cta">
      <a href="{SITE_BASE}/workspace?type={quote(genre['category'])}">用此题材开始创作 →</a>
    </div>
    """
    title = genre["title"]
    desc = genre["description"]
    url = f"/genre/{slug}"
    return PAGE_TEMPLATE.format(
        title=title,
        description=desc,
        keywords=f"{genre['category']},AI写小说,网文案例,LyRead",
        url=url,
        site_base=SITE_BASE,
        meta_info=genre["category"],
        body_html=body_html,
        json_ld=breadcrumb([
            ("首页", f"{SITE_BASE}/"),
            ("案例阅读", f"{SITE_BASE}/trending"),
            (genre["category"], f"{SITE_BASE}{url}"),
        ]),
    )


# --- 营销页 SSR（供搜索引擎与无 JS 环境索引）---

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
      <a href="{SITE_BASE}/login">注册领取 30 点 →</a>
      &nbsp;&nbsp;
      <a href="{SITE_BASE}/workspace">进入创作台 →</a>
    </div>
    """
    title = "价格与点数计费 - LyRead AI"
    desc = "LyRead 点数计费：注册送 30 点，每日免费 5 点，10 元 = 100 点。生成一章约 10 点，失败全额返还。"
    url = "/pricing"
    return PAGE_TEMPLATE.format(
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
    return PAGE_TEMPLATE.format(
        title=title,
        description=desc,
        keywords="AI小说案例,网文作品,智能写作案例,LyRead",
        url=url,
        site_base=SITE_BASE,
        meta_info=f"共 {len(cases)} 部公开作品",
        body_html=body_html,
        json_ld=_json_ld_trending(cases),
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
        for path, _freq, _pri in all_static_seo_paths():
            urls.append(f"{SITE_BASE}{path}")
        urls = urls[:20]

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
                f"SELECT id, title, category, word_count, heat FROM contents "
                f"WHERE {public_case_sql_clause()} ORDER BY heat DESC LIMIT 50"
            )
            for row in cursor.fetchall():
                safe_title = escape(str(row['title']))
                safe_category = escape(str(row['category']))
                items_html += f"""
                <li>
                    <a href="{SITE_BASE}/ep/{int(row['id'])}">{safe_title}</a>
                    <span class="tag">{safe_category}</span>
                    <span class="stat">{row['word_count']}字 · 热度{row['heat']}</span>
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
    list_desc = "LyRead AI智能小说创作平台作品列表，浏览各类热门的AI生成小说作品"
    list_path = str(request.url.path)
    return PAGE_TEMPLATE.format(
        title=list_title,
        description=list_desc,
        keywords="AI小说,网文列表,智能写作,小说推荐",
        url=list_path,
        site_base=SITE_BASE,
        meta_info="共收录作品",
        body_html=body_html,
        json_ld=_json_ld_list(list_title, list_desc, list_path),
    )

@router.get("/ep/", response_class=HTMLResponse)
async def seo_content_list_trailing(request: Request):
    return await seo_content_list(request)
