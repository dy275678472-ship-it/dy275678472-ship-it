#!/usr/bin/env python3
"""宗贸网 P2 增长补丁 — 爬取预算清理 + 薄页 noindex + 安全头 + 品类落地页"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BASE = Path("/opt/zongmao")
APP = BASE / "app.py"
TPL = BASE / "templates"
NGINX = Path("/etc/nginx/sites-enabled/zongmao")
NGINX_FALLBACK = Path("/etc/nginx/sites-available/zongmao")
CONFIG = BASE / "site_config.json"


def backup(path: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if "nginx" in str(path):
        dest = path.parent / "backups" / f"{path.name}.bak_{ts}"
        dest.parent.mkdir(parents=True, exist_ok=True)
    else:
        dest = path.with_suffix(path.suffix + f".bak_{ts}")
    shutil.copy2(path, dest)
    print(f"  backup: {dest}")


def patch_app():
    text = APP.read_text(encoding="utf-8")
    changed = False

    # ── resolve_quote helper ──
    helper = '''
def resolve_quote(conn, asset_name: str):
    """Map symbol or Chinese name to quotes row."""
    row = conn.execute(
        "SELECT * FROM quotes WHERE symbol=? OR name=? LIMIT 1", (asset_name, asset_name)
    ).fetchone()
    if row:
        return dict(row)
    row = conn.execute(
        "SELECT * FROM quotes WHERE name LIKE ? LIMIT 1", (f"%{asset_name}%",)
    ).fetchone()
    return dict(row) if row else None


SIGNAL_DIR_MAP = {
    "bullish": ("多", "long"),
    "bearish": ("空", "short"),
    "neutral": ("中性", "neutral"),
}

'''
    if "def resolve_quote" not in text:
        text = text.replace("CATEGORIES = ", helper + "CATEGORIES = ", 1)
        changed = True

    # ── sitemap: drop cards/assets, cap news, signals with active data only, add welcome+category ──
    old_sitemap_tail = """    # 卡片SEO页 (最新2000张)
    card_rows = conn.execute(\"\"\"
        SELECT c.id, c.publish_date, ca.asset_name FROM cards c
        JOIN card_assets ca ON c.id = ca.card_id
        ORDER BY c.publish_date DESC LIMIT 300
    \"\"\").fetchall()
    card_pages = [
        (f'https://zongmao.cn/cards/{r["id"]}', r["publish_date"] if r["publish_date"] else now, '0.7', 'weekly')
        for r in card_rows
    ]
    # 品种聚合SEO页
    asset_rows = conn.execute("SELECT DISTINCT asset_name FROM card_assets ORDER BY asset_name").fetchall()
    asset_pages = [
        (f'https://zongmao.cn/asset/{r["asset_name"]}', now, '0.8', 'daily')
        for r in asset_rows
    ]
    # 信号方向SEO页（仅34个标准品种，避免低质URL）
    signal_pages = []
    for direction in ('bullish', 'bearish', 'neutral'):
        for r in quote_rows:
            signal_pages.append(
                (f'https://zongmao.cn/signal/{direction}/{r["symbol"]}', now, '0.7', 'weekly')
            )
    conn.close()
    xml = '<?xml version="1.0" encoding="UTF-8"?>\\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n'
    all_pages = static_pages + news_pages + quote_pages + card_pages + asset_pages + signal_pages"""

    new_sitemap_tail = """    # P2: 卡片/资产聚合页移出 sitemap（robots 已屏蔽 cards）
    # 新闻页限最新 500 篇，控制爬取预算
    news_pages = news_pages[:500]
    # 品类落地页
    category_pages = [
        (f'https://zongmao.cn/category/{cat}', now, '0.8', 'daily') for cat in CATEGORIES
    ]
    # 信号方向页：仅有活跃 trade_signals 的品种才收录
    signal_pages = []
    for direction in ('bullish', 'bearish', 'neutral'):
        zh, alt = SIGNAL_DIR_MAP[direction]
        for r in quote_rows:
            has = conn.execute(
                "SELECT 1 FROM trade_signals WHERE symbol=? AND status='active' "
                "AND direction IN (?, ?) LIMIT 1",
                (r["symbol"], zh, alt),
            ).fetchone()
            if has:
                signal_pages.append(
                    (f'https://zongmao.cn/signal/{direction}/{r["symbol"]}', now, '0.7', 'weekly')
                )
    conn.close()
    xml = '<?xml version="1.0" encoding="UTF-8"?>\\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n'
    all_pages = static_pages + category_pages + news_pages + quote_pages + signal_pages"""

    if "card_pages + asset_pages" in text:
        text = text.replace(old_sitemap_tail, new_sitemap_tail, 1)
        changed = True

    if "zongmao.cn/welcome" not in text:
        text = text.replace(
            "('https://zongmao.cn/tutorial', now, '0.6', 'monthly'),",
            "('https://zongmao.cn/tutorial', now, '0.6', 'monthly'),\n"
            "        ('https://zongmao.cn/welcome', now, '0.6', 'monthly'),",
            1,
        )
        changed = True

    # ── asset → price 301 ──
    old_asset = '''@app.get("/asset/{asset_name}")
async def page_asset(request: Request, asset_name: str):
    """SEO品种聚合页"""
    conn = get_db()

    # 品种元数据
    meta = conn.execute("SELECT * FROM commodity_meta WHERE symbol=?", (asset_name,)).fetchone()'''
    new_asset = '''@app.get("/asset/{asset_name}")
async def page_asset(request: Request, asset_name: str):
    """SEO品种聚合页 — 标准品种 301 到 /price/{symbol}"""
    conn = get_db()
    quote_row = resolve_quote(conn, asset_name)
    if quote_row:
        conn.close()
        return RedirectResponse(url=f"/price/{quote_row['symbol']}", status_code=301)

    # 品种元数据（非标准 slug 保留兜底页，noindex）
    meta = conn.execute("SELECT * FROM commodity_meta WHERE symbol=?", (asset_name,)).fetchone()'''
    if "标准品种 301" not in text:
        text = text.replace(old_asset, new_asset, 1)
        changed = True

    old_asset_return = '''    return render(request, "asset.html",
                  asset_name=asset_name, cards=cards, stats=stat_dict,
                  signal_data=signal_data,
                  quote=dict(quote) if quote else None,
                  meta=dict(meta) if meta else None,
                  related_symbols=related_symbols, type_labels=TYPE_LABELS)'''
    new_asset_return = '''    return render(request, "asset.html",
                  asset_name=asset_name, cards=cards, stats=stat_dict,
                  signal_data=signal_data,
                  quote=dict(quote) if quote else None,
                  meta=dict(meta) if meta else None,
                  related_symbols=related_symbols, type_labels=TYPE_LABELS,
                  noindex=True)'''
    if 'type_labels=TYPE_LABELS)\n\n\n@app.get("/signal' in text:
        text = text.replace(old_asset_return, new_asset_return, 1)
        changed = True

    # ── signal page: resolve symbol + trade_signals + noindex ──
    old_signal_fn = '''@app.get("/signal/{direction}/{asset_name}")
async def page_signal_filter(request: Request, direction: str, asset_name: str):
    """SEO信号筛选页: /signal/bullish/沪铜"""
    if direction not in ("bullish", "bearish", "neutral"):
        raise HTTPException(404)

    conn = get_db()
    rows = conn.execute("""
        SELECT c.* FROM cards c
        JOIN card_assets ca ON c.id = ca.card_id
        WHERE ca.asset_name=? AND c.direction=? AND c.card_type IN ('trend','anomaly','insight')
        ORDER BY c.publish_date DESC LIMIT 30
    """, (asset_name, direction)).fetchall()
    cards = [_card_row_to_dict(r, conn) for r in rows]

    dir_labels = {"bullish": "看多", "bearish": "看空", "neutral": "震荡"}
    conn.close()

    return render(request, "signal.html",
                  cards=cards, asset_name=asset_name, direction=direction,
                  dir_label=dir_labels.get(direction, direction), type_labels=TYPE_LABELS)'''
    new_signal_fn = '''@app.get("/signal/{direction}/{asset_name}")
async def page_signal_filter(request: Request, direction: str, asset_name: str):
    """SEO信号筛选页: /signal/bullish/SC"""
    if direction not in ("bullish", "bearish", "neutral"):
        raise HTTPException(404)

    conn = get_db()
    quote = resolve_quote(conn, asset_name)
    sym = quote["symbol"] if quote else asset_name
    display_name = quote["name"] if quote else asset_name
    zh, alt = SIGNAL_DIR_MAP[direction]

    trade_signals = [dict(r) for r in conn.execute(
        "SELECT ts.*, q.name FROM trade_signals ts LEFT JOIN quotes q ON ts.symbol=q.symbol "
        "WHERE ts.symbol=? AND ts.status='active' AND ts.direction IN (?, ?) "
        "ORDER BY ts.created_at DESC LIMIT 10",
        (sym, zh, alt),
    ).fetchall()]

    card_name = display_name
    rows = conn.execute("""
        SELECT c.* FROM cards c
        JOIN card_assets ca ON c.id = ca.card_id
        WHERE ca.asset_name=? AND c.direction=? AND c.card_type IN ('trend','anomaly','insight')
        ORDER BY c.publish_date DESC LIMIT 30
    """, (card_name, direction)).fetchall()
    cards = [_card_row_to_dict(r, conn) for r in rows]

    dir_labels = {"bullish": "看多", "bearish": "看空", "neutral": "震荡"}
    noindex = not cards and not trade_signals
    conn.close()

    return render(request, "signal.html",
                  cards=cards, trade_signals=trade_signals, quote=quote,
                  asset_name=display_name, symbol=sym, direction=direction,
                  dir_label=dir_labels.get(direction, direction),
                  type_labels=TYPE_LABELS, noindex=noindex)'''
    if "trade_signals=trade_signals" not in text:
        text = text.replace(old_signal_fn, new_signal_fn, 1)
        changed = True

    # ── card detail noindex ──
    old_card_return = '''    return render(request, "card_detail.html",
                  card=card, article=article, related=related, type_labels=TYPE_LABELS,
                  seo_title=seo_title, og_desc=og_desc)'''
    new_card_return = '''    return render(request, "card_detail.html",
                  card=card, article=article, related=related, type_labels=TYPE_LABELS,
                  seo_title=seo_title, og_desc=og_desc, noindex=True)'''
    if "card_detail.html" in text and "og_desc=og_desc, noindex=True" not in text:
        text = text.replace(old_card_return, new_card_return, 1)
        changed = True

    # ── category landing pages ──
    cat_route = '''
@app.get("/category/{category}")
async def page_category(request: Request, category: str):
    """品类 SEO 落地页"""
    if category not in CATEGORIES:
        raise HTTPException(404)
    conn = get_db()
    quotes = [dict(r) for r in conn.execute(
        "SELECT * FROM quotes WHERE category=? ORDER BY symbol", (category,)
    ).fetchall()]
    latest_signals = [dict(r) for r in conn.execute(
        "SELECT ts.*, q.name FROM trade_signals ts LEFT JOIN quotes q ON ts.symbol=q.symbol "
        "WHERE q.category=? AND ts.status='active' ORDER BY ts.created_at DESC LIMIT 5",
        (category,),
    ).fetchall()]
    conn.close()
    return render(request, "category.html", category=category, quotes=quotes,
                  cat_icon=CAT_ICONS.get(category, "📊"), latest_signals=latest_signals,
                  categories=CATEGORIES, cat_icons=CAT_ICONS)

'''
    if '@app.get("/category/{category}")' not in text:
        text = text.replace('@app.get("/methodology")', cat_route + '@app.get("/methodology")', 1)
        changed = True

    if changed:
        backup(APP)
        APP.write_text(text, encoding="utf-8")
        print("✅ app.py patched")
    else:
        print("ℹ️  app.py already patched")


def write_category_template():
    path = TPL / "category.html"
    if path.exists() and "P2-GENERATED" in path.read_text(encoding="utf-8", errors="replace"):
        print("ℹ️  category.html exists")
        return
    html = """<!-- P2-GENERATED -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ category }}期货行情与AI信号 — 宗贸网</title>
<meta name="description" content="宗贸网{{ category }}板块期货行情：实时价格、AI多空信号、历史战绩。覆盖{% for q in quotes %}{{ q.name }}{% if not loop.last %}、{% endif %}{% endfor %}等品种。">
<link rel="canonical" href="https://zongmao.cn/category/{{ category }}">
<link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
<nav class="navbar">
    <a href="/" class="nav-brand">宗贸网</a>
    <div class="nav-links">
        <a href="/market">行情</a><a href="/signals">信号</a><a href="/performance">战绩</a>
        <a href="/premium" style="color:#c0392b;font-weight:bold;">会员</a>
    </div>
    <div class="nav-right"><a href="/login">登录</a><a href="/register">注册</a></div>
</nav>
<div class="container">
    <h1>{{ cat_icon }} {{ category }}期货行情</h1>
    <p style="color:#666;">{{ quotes|length }} 个品种 · 实时行情 + AI 交易信号</p>
    <div class="card" style="padding:0;overflow:hidden;">
        <table class="quote-table" style="margin:0;">
            <tr><th>品种</th><th>最新价</th><th>涨跌幅</th><th>信号</th></tr>
            {% for q in quotes %}
            <tr>
                <td><a href="/price/{{ q.symbol }}">{{ q.name }}</a></td>
                <td>{{ q.price }}</td>
                <td class="{{ 'positive' if q.change_pct and q.change_pct > 0 else 'negative' if q.change_pct and q.change_pct < 0 else '' }}">{{ '%+.2f'|format(q.change_pct) if q.change_pct is not none else '—' }}%</td>
                <td><a href="/signal/bullish/{{ q.symbol }}">看多</a> · <a href="/signal/bearish/{{ q.symbol }}">看空</a></td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% if latest_signals %}
    <div class="card" style="margin-top:1.5rem;">
        <div class="card-header"><span class="card-title">📡 今日 {{ category }} AI 信号</span><a href="/signals">全部 →</a></div>
        {% for s in latest_signals %}
        <div style="padding:0.5rem 0;border-bottom:1px solid #eee;display:flex;justify-content:space-between;">
            <span><strong>{{ s.name or s.symbol }}</strong> <span style="color:{{ '#e74c3c' if s.direction in ('多','long') else '#27ae60' }};">{{ s.direction }}</span></span>
            <a href="/price/{{ s.symbol }}">行情 →</a>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    <div style="text-align:center;margin:2rem 0;">
        <a href="/register" class="btn btn-primary" style="padding:0.8rem 2rem;">免费注册查看信号</a>
    </div>
</div>
<footer class="footer">© 2026 宗贸网 zongmao.cn · 大宗商品交易信号与行情平台
<br><a href="/about" style="color:#fff;margin:0 8px;">关于我们</a> | <a href="/methodology" style="color:#fff;margin:0 8px;">信号方法论</a>
<br><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener" style="color:#888;">皖ICP备2026016894号-1</a>
</footer>
<script src="/static/js/common.js"></script>
{% include "_tongji.html" %}
</body></html>"""
    path.write_text(html, encoding="utf-8")
    print("✅ category.html created")


def patch_signal_template():
    path = TPL / "signal.html"
    text = path.read_text(encoding="utf-8")
    changed = False

    if "noindex" not in text:
        text = text.replace(
            "<link rel=\"stylesheet\" href=\"/static/css/style.css\">",
            '<link rel="stylesheet" href="/static/css/style.css">\n'
            '    {% if noindex %}<meta name="robots" content="noindex, follow">{% endif %}',
            1,
        )
        changed = True

    if "trade_signals" not in text:
        block = """
    {% if trade_signals %}
    <div class="card" style="margin-bottom:1.5rem;">
        <div class="card-header"><span class="card-title">🎯 活跃 AI 交易信号</span>
            {% if quote %}<a href="/price/{{ quote.symbol }}" style="font-size:0.85rem;">{{ quote.name }} 行情 →</a>{% endif %}
        </div>
        {% for s in trade_signals %}
        <div style="padding:0.7rem 0;border-bottom:1px solid #eee;">
            <strong>{{ s.name or s.symbol }}</strong>
            <span style="color:{{ '#e74c3c' if s.direction in ('多','long') else '#27ae60' }};margin:0 0.5rem;">{{ s.direction }}</span>
            入场 {{ s.entry_price }} · 目标 {{ s.target_price }} · 止损 {{ s.stop_loss }}
            {% if s.rationale %}<p style="font-size:0.85rem;color:#666;margin:0.3rem 0 0;">{{ s.rationale[:80] }}</p>{% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}"""
        text = text.replace('<div class="card-feed">', block + '\n    <div class="card-feed">', 1)
        changed = True

    if 'href="/asset/{{ asset_name }}"' in text and "quote.symbol" not in text:
        text = text.replace(
            '<a href="/asset/{{ asset_name }}" class="cat-tab"',
            '<a href="{% if quote %}/price/{{ quote.symbol }}{% else %}/asset/{{ asset_name }}{% endif %}" class="cat-tab"',
            1,
        )
        changed = True

    if '{% if not cards %}' in text and 'trade_signals' not in text.split('{% if not cards %}')[0][-200:]:
        text = text.replace(
            '{% if not cards %}',
            '{% if not cards and not trade_signals %}',
            1,
        )
        changed = True

    if changed:
        backup(path)
        path.write_text(text, encoding="utf-8")
        print("✅ signal.html patched")
    else:
        print("ℹ️  signal.html already patched")


def patch_card_templates():
    for name in ("card_detail.html", "cards.html"):
        path = TPL / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "noindex" in text:
            print(f"ℹ️  {name} already has noindex")
            continue
        if "</head>" in text:
            text = text.replace(
                "</head>",
                '    <meta name="robots" content="noindex, follow">\n</head>',
                1,
            )
            backup(path)
            path.write_text(text, encoding="utf-8")
            print(f"✅ {name} noindex added")


def patch_asset_template():
    path = TPL / "asset.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if "noindex" in text:
        print("ℹ️  asset.html already has noindex")
        return
    text = text.replace(
        "</head>",
        '    <meta name="robots" content="noindex, follow">\n</head>',
        1,
    )
    backup(path)
    path.write_text(text, encoding="utf-8")
    print("✅ asset.html noindex added")


def patch_tongji():
    """Baidu Tongji: read HM ID from site_config.json"""
    hm_id = ""
    if CONFIG.exists():
        try:
            hm_id = json.loads(CONFIG.read_text(encoding="utf-8")).get("baidu_hm_id", "")
        except json.JSONDecodeError:
            pass

    path = TPL / "_tongji.html"
    if hm_id:
        content = f"""{{# 百度统计 — P2 自动注入 #}}
<script>
var _hmt = _hmt || [];
(function() {{
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?{hm_id}";
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(hm, s);
}})();
</script>"""
    else:
        content = """{# 百度统计 — 在 /opt/zongmao/site_config.json 设置 baidu_hm_id 后重启生效 #}
<script>
console.log("[Zongmao] Set baidu_hm_id in site_config.json to enable Baidu Tongji");
</script>"""
    path.write_text(content, encoding="utf-8")
    print(f"✅ _tongji.html updated ({'active' if hm_id else 'pending HM ID'})")


def write_site_config():
    if not CONFIG.exists():
        CONFIG.write_text(
            json.dumps({"baidu_hm_id": ""}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("✅ site_config.json created")
    else:
        print("ℹ️  site_config.json exists")


def patch_nginx():
    target = NGINX if NGINX.exists() else NGINX_FALLBACK
    if not target.exists():
        print("⚠️  nginx config not found")
        return
    text = target.read_text(encoding="utf-8")
    extra = [
        'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
        'add_header Referrer-Policy "strict-origin-when-cross-origin" always;',
        'add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;',
    ]
    loc_block = """    location / {
        proxy_pass http://127.0.0.1:8083;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }"""
    loc_with_headers = """    location / {
        proxy_pass http://127.0.0.1:8083;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
    }"""
    changed = False
    if "Strict-Transport-Security" not in text.split("location / {")[1][:600] if "location / {" in text else "":
        if loc_block in text:
            text = text.replace(loc_block, loc_with_headers, 1)
            changed = True
    for line in extra:
        if line.split('"')[0].strip() not in text:
            text = text.replace(
                'add_header X-XSS-Protection "1; mode=block" always;',
                'add_header X-XSS-Protection "1; mode=block" always;\n    ' + line,
                1,
            )
            changed = True
    if changed:
        backup(target)
        target.write_text(text, encoding="utf-8")
        subprocess.run(["nginx", "-t"], check=True)
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
        print("✅ nginx security headers added")
    else:
        print("ℹ️  nginx already patched")


def main():
    print("🚀 Zongmao P2 patch")
    write_site_config()
    patch_app()
    write_category_template()
    patch_signal_template()
    patch_card_templates()
    patch_asset_template()
    patch_tongji()
    patch_nginx()
    print("✅ P2 complete — restart zongmao.service")


if __name__ == "__main__":
    main()
