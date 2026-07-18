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
            <p>© LyRead AI 智能小说创作平台 · <a href="{site_base}/">首页</a></p>
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
            "logo": {"@type": "ImageObject", "url": f"{SITE_BASE}/images/logo-icon.webp"},
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
                "SELECT id, title, category, word_count, heat, score, created_at "
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
                json_ld = _json_ld_article(
                    safe_title, description, url,
                    genre=safe_category, word_count=int(row.get('word_count') or 0),
                )
                body_html = f"""
                <div class="info-grid">
                    <div class="info-item"><strong>分类</strong><br>{safe_category}</div>
                    <div class="info-item"><strong>字数</strong><br>{row['word_count']:,}</div>
                    <div class="info-item"><strong>热度</strong><br>{row['heat']}</div>
                    <div class="info-item"><strong>评分</strong><br>{row.get('score', 'N/A')}</div>
                </div>
                <div class="seo-cta">
                    <a href="{SITE_BASE}/?utm_source=baidu&utm_medium=seo">前往 LyRead 阅读完整作品 →</a>
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
    """生成搜索引擎站点地图"""
    urls = [
        (f"{SITE_BASE}/", "weekly", "1.0"),
        (f"{SITE_BASE}/pricing", "weekly", "0.9"),
        (f"{SITE_BASE}/trending", "weekly", "0.8"),
        (f"{SITE_BASE}/login", "monthly", "0.5"),
        (f"{SITE_BASE}/story", "weekly", "0.7"),
        (f"{SITE_BASE}/reader", "weekly", "0.7"),
        (f"{SITE_BASE}/ep", "weekly", "0.7"),
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
                updated = row['updated_at'].strftime('%Y-%m-%d') if row.get('updated_at') else datetime.now().strftime('%Y-%m-%d')
                urls.append((f"{SITE_BASE}/ep/{row['id']}", "weekly", "0.6"))
            cursor.close()
            db.close()
    except Exception as e:
        print(f"[SEO Page] Error generating sitemap: {e}")

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for loc, freq, priority in urls:
        xml += "  <url>\n"
        xml += f"    <loc>{loc}</loc>\n"
        xml += f"    <changefreq>{freq}</changefreq>\n"
        xml += f"    <priority>{priority}</priority>\n"
        xml += "  </url>\n"
    xml += "</urlset>"
    return xml


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    """爬虫规则"""
    return f"""User-agent: *
Allow: /
Sitemap: {SITE_BASE}/sitemap.xml

User-agent: Baiduspider
Allow: /

User-agent: Googlebot
Allow: /
"""


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
