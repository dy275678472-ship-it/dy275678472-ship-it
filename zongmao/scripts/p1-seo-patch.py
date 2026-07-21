#!/usr/bin/env python3
"""宗贸网 SEO/GEO P1 补丁 — Schema、OG 图、作者统一、内链"""
from __future__ import annotations

import json
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

BASE = Path("/opt/zongmao")
APP = BASE / "app.py"
TPL = BASE / "templates"
DB = BASE / "zongmao.db"
OG_DIR = BASE / "static" / "images" / "og"
SITE = "https://zongmao.cn"

ORG_SCHEMA = """
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Organization","name":"宗贸网","url":"https://zongmao.cn",
 "logo":"https://zongmao.cn/static/images/og-default.jpg",
 "description":"大宗商品AI交易信号平台，覆盖34种期货品种实时行情与可验证战绩",
 "sameAs":["https://zongmao.cn/about"],
 "contactPoint":{"@type":"ContactPoint","contactType":"customer support","url":"https://zongmao.cn/about"}}
</script>"""


def backup(path: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = path.with_suffix(path.suffix + f".bak_{ts}")
    shutil.copy2(path, dest)
    print(f"  backup: {dest.name}")


def patch_app_news():
    text = APP.read_text(encoding="utf-8")
    old = """    related = [dict(r) for r in conn.execute("SELECT id,title,category,created_at FROM news WHERE category=? AND id!=? ORDER BY id DESC LIMIT 5", (news["category"], news_id)).fetchall()]
    conn.close()
    return render(request, "news_detail.html", news=dict(news), related=related)"""
    new = """    related = [dict(r) for r in conn.execute("SELECT id,title,category,created_at FROM news WHERE category=? AND id!=? ORDER BY id DESC LIMIT 5", (news["category"], news_id)).fetchall()]
    cat_symbols = [r["symbol"] for r in conn.execute("SELECT symbol FROM quotes WHERE category=?", (news["category"],)).fetchall()]
    related_signals = []
    if cat_symbols:
        ph = ",".join("?" * len(cat_symbols))
        related_signals = [dict(r) for r in conn.execute(
            f"SELECT ts.*, q.name FROM trade_signals ts LEFT JOIN quotes q ON ts.symbol=q.symbol "
            f"WHERE ts.symbol IN ({ph}) AND ts.status='active' ORDER BY ts.created_at DESC LIMIT 3",
            cat_symbols,
        ).fetchall()]
    news_dict = dict(news)
    if not news_dict.get("author") or news_dict.get("author") in ("AI分析师", "AI"):
        news_dict["author"] = "宗贸网研究院"
    conn.close()
    return render(request, "news_detail.html", news=news_dict, related=related, related_signals=related_signals)"""
    if "related_signals=related_signals" not in text.split("page_news_detail")[1][:1200]:
        backup(APP)
        text = text.replace(old, new, 1)
        APP.write_text(text, encoding="utf-8")
        print("✅ app.py news_detail + related_signals")
    else:
        print("ℹ️  app.py news_detail already patched")


def fix_news_authors():
    conn = sqlite3.connect(DB)
    n = conn.execute(
        "UPDATE news SET author='宗贸网研究院' WHERE author IS NULL OR author='' OR author IN ('AI分析师','AI','分析师')"
    ).rowcount
    conn.commit()
    conn.close()
    print(f"✅ normalized {n} news author rows")


def gen_og_images():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT symbol, name, category, price, change_pct FROM quotes").fetchall()
    conn.close()
    OG_DIR.mkdir(parents=True, exist_ok=True)
    colors = {"能源": "#e67e22", "黑色": "#34495e", "有色": "#f39c12", "化工": "#9b59b6", "农产品": "#27ae60"}
    n = 0
    for r in rows:
        sym, name, cat = r["symbol"], r["name"], r["category"]
        color = colors.get(cat, "#2980b9")
        pct = r["change_pct"] or 0
        arrow = "▲" if pct > 0 else "▼" if pct < 0 else "●"
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#1a5276"/><stop offset="100%" stop-color="{color}"/>
  </linearGradient></defs>
  <rect width="1200" height="630" fill="url(#g)"/>
  <text x="60" y="120" fill="#fff" font-size="28" font-family="sans-serif" opacity="0.9">宗贸网 · {cat}</text>
  <text x="60" y="280" fill="#fff" font-size="72" font-family="sans-serif" font-weight="bold">{name}</text>
  <text x="60" y="360" fill="#ecf0f1" font-size="36" font-family="sans-serif">{sym} · {r["price"]} {arrow} {pct:+.2f}%</text>
  <text x="60" y="560" fill="#bdc3c7" font-size="24" font-family="sans-serif">zongmao.cn · AI交易信号</text>
</svg>'''
        path = OG_DIR / f"{sym}.svg"
        if not path.exists() or path.stat().st_size < 100:
            path.write_text(svg, encoding="utf-8")
            n += 1
    print(f"✅ OG images: {n} new, {len(rows)} total in {OG_DIR}")


def inject_after_head(path: Path, marker: str, block: str):
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return False
    if "</head>" not in text:
        return False
    text = text.replace("</head>", block + "\n</head>", 1)
    backup(path)
    path.write_text(text, encoding="utf-8")
    return True


def patch_price():
    path = TPL / "price.html"
    text = path.read_text(encoding="utf-8")
    changed = False

    old_og = '<meta property="og:image" content="https://zongmao.cn/static/images/og-default.jpg">'
    new_og = '<meta property="og:image" content="https://zongmao.cn/static/images/og/{{ quote.symbol }}.svg">\n    <meta property="og:image:type" content="image/svg+xml">'
    if "og/{{ quote.symbol }}" not in text:
        text = text.replace(old_og, new_og, 1)
        text = text.replace(
            '<meta name="twitter:image" content="https://zongmao.cn/static/images/og-default.jpg">',
            '<meta name="twitter:image" content="https://zongmao.cn/static/images/og/{{ quote.symbol }}.svg">',
            1,
        )
        changed = True

    breadcrumb_schema = """
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"首页","item":"https://zongmao.cn"},
      {"@type":"ListItem","position":2,"name":"行情中心","item":"https://zongmao.cn/market"},
      {"@type":"ListItem","position":3,"name":"{{ quote.category }}","item":"https://zongmao.cn/category/{{ quote.category }}"},
      {"@type":"ListItem","position":4,"name":"{{ quote.name }}","item":"https://zongmao.cn/price/{{ quote.symbol }}"}
    ]}
    </script>"""
    if "BreadcrumbList" not in text:
        text = text.replace("</head>", breadcrumb_schema + "\n</head>", 1)
        changed = True

    # Breadcrumb link to category page
    if '/category/{{ quote.category }}' not in text and '/market?category={{ quote.category }}' in text:
        text = text.replace(
            '<a href="/market?category={{ quote.category }}">{{ quote.category }}</a>',
            '<a href="/category/{{ quote.category }}">{{ quote.category }}</a>',
            1,
        )
        changed = True

    if 'id="priceChart"' in text and "aria-label" not in text:
        text = text.replace(
            '<div id="priceChart"',
            '<div id="priceChart" role="img" aria-label="{{ quote.name }}价格走势图"',
            1,
        )
        changed = True

    if changed:
        backup(path)
        path.write_text(text, encoding="utf-8")
        print("✅ price.html OG + BreadcrumbList + chart alt")
    else:
        print("ℹ️  price.html already patched")


def patch_news_detail():
    path = TPL / "news_detail.html"
    text = path.read_text(encoding="utf-8")
    changed = False

    if "og/{{ news.id }}" not in text:
        text = text.replace(
            '<meta property="og:image" content="https://zongmao.cn/static/images/og-default.jpg">',
            '<meta property="og:image" content="https://zongmao.cn/static/images/og-default.jpg">\n    <meta property="og:type" content="article">',
            1,
        )
        changed = True

    old_article = '''    {"@context":"https://schema.org","@type":"Article","headline":"{{ news.title | replace('"', '\\"') }}",
     "description":"{{ (news.summary or '') | replace('"', '\\"') }}",
     "author":{"@type":"Organization","name":"{{ news.author or '宗贸网研究院' }}"},
     "publisher":{"@type":"Organization","name":"宗贸网","url":"https://zongmao.cn"},
     "datePublished":"{{ news.created_at }}","url":"https://zongmao.cn/news/{{ news.id }}"}'''
    new_article = '''    {"@context":"https://schema.org","@type":"Article","headline":"{{ news.title | replace('"', '\\"') }}",
     "description":"{{ (news.summary or '') | replace('"', '\\"') }}",
     "author":{"@type":"Organization","name":"宗贸网研究院"},
     "publisher":{"@type":"Organization","name":"宗贸网","url":"https://zongmao.cn",
       "logo":{"@type":"ImageObject","url":"https://zongmao.cn/static/images/og-default.jpg"}},
     "datePublished":"{{ news.created_at }}","dateModified":"{{ news.created_at }}",
     "mainEntityOfPage":"https://zongmao.cn/news/{{ news.id }}",
     "articleSection":"{{ news.category }}",
     "url":"https://zongmao.cn/news/{{ news.id }}"}'''
    if '"articleSection"' not in text:
        text = text.replace(old_article, new_article, 1)
        changed = True

    breadcrumb = """
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"首页","item":"https://zongmao.cn"},
      {"@type":"ListItem","position":2,"name":"资讯中心","item":"https://zongmao.cn/news"},
      {"@type":"ListItem","position":3,"name":"{{ news.category }}","item":"https://zongmao.cn/news?category={{ news.category }}"},
      {"@type":"ListItem","position":4,"name":"{{ news.title[:30] }}","item":"https://zongmao.cn/news/{{ news.id }}"}
    ]}
    </script>"""
    if "BreadcrumbList" not in text:
        text = text.replace("</head>", breadcrumb + "\n</head>", 1)
        changed = True

    old_meta = "{{ news.category }} · {{ news.source }} ·"
    new_meta = '{{ news.category }} · <a href="/category/{{ news.category }}">{{ news.category }}行情</a> · 宗贸网研究院 ·'
    if "宗贸网研究院 ·" not in text:
        text = text.replace(old_meta, new_meta, 1)
        changed = True

    if changed:
        backup(path)
        path.write_text(text, encoding="utf-8")
        print("✅ news_detail.html schema + breadcrumb")
    else:
        print("ℹ️  news_detail.html already patched")


def patch_signal():
    path = TPL / "signal.html"
    text = path.read_text(encoding="utf-8")
    if "BreadcrumbList" in text:
        print("ℹ️  signal.html already patched")
        return
    block = """
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"首页","item":"https://zongmao.cn"},
      {"@type":"ListItem","position":2,"name":"交易信号","item":"https://zongmao.cn/signals"},
      {"@type":"ListItem","position":3,"name":"{{ asset_name }} {{ dir_label }}","item":"https://zongmao.cn/signal/{{ direction }}/{{ symbol if quote else asset_name }}"}
    ]}
    </script>"""
    text = text.replace("</head>", block + "\n</head>", 1)
    backup(path)
    path.write_text(text, encoding="utf-8")
    print("✅ signal.html BreadcrumbList")


def patch_index_org():
    path = TPL / "index.html"
    text = path.read_text(encoding="utf-8")
    if '"@type":"Organization"' in text and "contactPoint" in text:
        print("ℹ️  index.html Organization already present")
        return
    if '"@type":"Organization"' in text:
        # upgrade existing shallow org
        text = re.sub(
            r'<script type="application/ld\+json">\s*\{[^<]*"@type":"Organization"[^<]*\}\s*</script>',
            ORG_SCHEMA.strip(),
            text,
            count=1,
        )
    else:
        text = text.replace("</head>", ORG_SCHEMA + "\n</head>", 1)
    backup(path)
    path.write_text(text, encoding="utf-8")
    print("✅ index.html Organization schema")


def patch_footers():
    """Add trust-page links to main template footers."""
    trust_links = (
        '<a href="/methodology" style="color:#fff;margin:0 8px;">信号方法论</a> | '
        '<a href="/compare" style="color:#fff;margin:0 8px;">平台对比</a> | '
        '<a href="/tutorial" style="color:#fff;margin:0 8px;">新手教程</a> | '
    )
    targets = ["price.html", "news_detail.html", "performance.html", "signals.html", "market.html"]
    for name in targets:
        path = TPL / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "/methodology" in text:
            continue
        if '<a href="/about"' in text:
            text = text.replace('<a href="/about"', trust_links + '<a href="/about"', 1)
            backup(path)
            path.write_text(text, encoding="utf-8")
            print(f"  ✓ footer links in {name}")


def patch_category():
    path = TPL / "category.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if "BreadcrumbList" in text:
        print("ℹ️  category.html already patched")
        return
    block = """
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"首页","item":"https://zongmao.cn"},
      {"@type":"ListItem","position":2,"name":"行情中心","item":"https://zongmao.cn/market"},
      {"@type":"ListItem","position":3,"name":"{{ category }}","item":"https://zongmao.cn/category/{{ category }}"}
    ]}
    </script>"""
    text = text.replace("</head>", block + "\n</head>", 1)
    backup(path)
    path.write_text(text, encoding="utf-8")
    print("✅ category.html BreadcrumbList")


def main():
    print("🚀 Zongmao SEO/GEO P1 patch")
    patch_app_news()
    fix_news_authors()
    gen_og_images()
    patch_price()
    patch_news_detail()
    patch_signal()
    patch_category()
    patch_index_org()
    patch_footers()
    print("✅ SEO P1 complete — restart zongmao.service")


if __name__ == "__main__":
    main()
