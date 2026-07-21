#!/usr/bin/env python3
"""宗贸网 P1 增长补丁 — SEO + 转化优化"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

BASE = Path("/opt/zongmao")
APP = BASE / "app.py"
TPL = BASE / "templates"


def backup(path: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, path.with_suffix(path.suffix + f".bak_{ts}"))


NAV_FOOT = """
<footer class="footer">© 2026 宗贸网 zongmao.cn · 大宗商品交易信号与行情平台 · 风险提示：本站信息仅供参考，不构成投资建议
<br><a href="/about" style="color:#fff;margin:0 8px;">关于我们</a> | <a href="/methodology" style="color:#fff;margin:0 8px;">信号方法论</a> | <a href="/compare" style="color:#fff;margin:0 8px;">平台对比</a> | <a href="/disclaimer" style="color:#fff;margin:0 8px;">免责声明</a>
<br><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener" style="color:#888;text-decoration:none;">皖ICP备2026016894号-1</a>
</footer>
<script src="/static/js/common.js"></script>
</body></html>"""

PAGE_SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://zongmao.cn{url}">
<link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
<nav class="navbar">
    <a href="/" class="nav-brand">宗贸网</a>
    <div class="nav-links">
        <a href="/market">行情</a><a href="/signals">信号</a><a href="/performance">战绩</a>
        <a href="/premium" style="color:#c0392b;font-weight:bold;">会员</a>
        <a href="/trading-contest">模拟赛</a>
    </div>
    <div class="nav-right"><a href="/login">登录</a><a href="/register">注册</a></div>
</nav>
<div class="container" style="max-width:900px;">
{body}
</div>
""" + NAV_FOOT


def write_templates():
  pages = {
    "methodology.html": PAGE_SHELL.format(
      title="AI交易信号方法论 — 宗贸网",
      desc="宗贸网AI交易信号生成逻辑：趋势过滤、品种基本面、风险区间计算，每笔信号可回溯验证。",
      url="/methodology",
      body="""
<div class="card" style="padding:2rem;line-height:1.9;">
<h1 style="margin-top:0;">AI 交易信号方法论</h1>
<p>宗贸网每日基于<strong>34种大宗商品</strong>实时行情，通过三层过滤生成多空交易信号。所有信号均公开追踪，历史战绩可在<a href="/performance">战绩看板</a>验证。</p>
<h2>三层信号生成框架</h2>
<ol>
<li><strong>趋势过滤</strong>：仅当日内涨跌幅 |Δ| &gt; 1.5% 时触发，过滤震荡噪音</li>
<li><strong>品种逻辑</strong>：能源看供需/OPEC，黑色看钢厂利润，有色看LME库存，农产品看天气/USDA</li>
<li><strong>风险区间</strong>：自动计算入场价、目标价（±2.5%~3%）、止损价（±2%），风险收益比约 1:1.25</li>
</ol>
<h2>信号字段说明</h2>
<table class="quote-table"><tr><th>字段</th><th>含义</th></tr>
<tr><td>方向</td><td>多/空，基于当日趋势顺势判断</td></tr>
<tr><td>入场价</td><td>信号发布时最新价</td></tr>
<tr><td>目标价/止损价</td><td>系统计算的止盈/止损位</td></tr>
<tr><td>战绩</td><td>平仓后记录实际盈亏百分比</td></tr></table>
<h2>合规声明</h2>
<p>本站信号由AI系统自动生成，<strong>仅供参考，不构成投资建议</strong>。期货交易有风险，请结合自身判断。详见<a href="/disclaimer">免责声明</a>。</p>
<div style="text-align:center;margin-top:2rem;">
<a href="/register" class="btn btn-primary" style="padding:0.8rem 2rem;">免费注册看今日信号</a>
<a href="/premium" class="btn" style="margin-left:1rem;padding:0.8rem 2rem;">升级会员 ¥10/月起</a>
</div>
</div>""",
    ),
    "compare.html": PAGE_SHELL.format(
      title="期货信号平台对比 — 宗贸网 vs 文华财经 vs 同花顺",
      desc="宗贸网与文华财经、同花顺期货、掘金量化在AI信号、价格、模拟交易方面的客观对比。",
      url="/compare",
      body="""
<div class="card" style="padding:1.5rem;">
<h1 style="margin-top:0;">期货信号平台对比</h1>
<p style="color:#666;">客观对比，助你选择适合的工具（2026年7月）</p>
<div style="overflow-x:auto;">
<table class="quote-table">
<tr><th>对比维度</th><th style="background:#e8f0fe;">宗贸网</th><th>文华财经</th><th>同花顺期货</th></tr>
<tr><td>AI自动信号</td><td style="background:#e8f0fe;font-weight:600;">✅ 每日自动生成</td><td>❌ 需人工分析</td><td>⚠️ 部分智能提醒</td></tr>
<tr><td>信号可回溯验证</td><td style="background:#e8f0fe;font-weight:600;">✅ 公开战绩看板</td><td>❌</td><td>❌</td></tr>
<tr><td>模拟跟单</td><td style="background:#e8f0fe;">✅ 免费模拟赛</td><td>⚠️ 部分支持</td><td>⚠️ 部分支持</td></tr>
<tr><td>会员价格</td><td style="background:#e8f0fe;font-weight:600;color:#c0392b;">¥10/月起</td><td>数百元/月</td><td>免费+高阶付费</td></tr>
<tr><td>覆盖品种</td><td style="background:#e8f0fe;">34种大宗商品</td><td>全市场</td><td>全市场</td></tr>
<tr><td>每日早报</td><td style="background:#e8f0fe;">✅ 五大板块</td><td>✅</td><td>✅</td></tr>
</table>
</div>
<p style="margin-top:1.5rem;"><strong>选型建议：</strong>追求<strong>低价AI信号+可验证战绩</strong>选宗贸网；需要全市场行情终端选文华/同花顺。</p>
<div style="text-align:center;margin-top:1.5rem;">
<a href="/free-trial" class="btn btn-primary" style="padding:0.8rem 2rem;">免费试用宗贸网</a>
</div>
</div>""".replace("/free-trial", "/register"),
    ),
    "welcome.html": PAGE_SHELL.format(
      title="欢迎加入宗贸网",
      desc="新用户引导：查看今日AI信号、参加模拟交易赛、订阅每日早报。",
      url="/welcome",
      body="""
<div class="card" style="padding:2rem;text-align:center;">
<h1 style="margin-top:0;">🎉 欢迎加入宗贸网！</h1>
<p style="color:#666;font-size:1.1rem;">3 步开始你的模拟交易之旅</p>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin:2rem 0;text-align:left;">
<div style="background:#e8f5e9;border-radius:12px;padding:1.2rem;"><div style="font-size:1.5rem;font-weight:700;color:#27ae60;">1</div><strong>看今日信号</strong><p style="font-size:0.9rem;color:#666;margin:0.5rem 0 0;">浏览 AI 生成的多空建议，含入场/目标/止损</p><a href="/signals" style="font-size:0.85rem;">去看信号 →</a></div>
<div style="background:#e3f2fd;border-radius:12px;padding:1.2rem;"><div style="font-size:1.5rem;font-weight:700;color:#1565c0;">2</div><strong>参加模拟赛</strong><p style="font-size:0.9rem;color:#666;margin:0.5rem 0 0;">100万虚拟资金，零风险验证信号效果</p><a href="/trading-contest" style="font-size:0.85rem;">进入模拟赛 →</a></div>
<div style="background:#fff3e0;border-radius:12px;padding:1.2rem;"><div style="font-size:1.5rem;font-weight:700;color:#e67e22;">3</div><strong>订阅早报</strong><p style="font-size:0.9rem;color:#666;margin:0.5rem 0 0;">每日盘前速递，五大板块行情速览</p><a href="/daily-brief" style="font-size:0.85rem;">查看早报 →</a></div>
</div>
<a href="/signals" class="btn btn-primary" style="padding:0.9rem 2.5rem;font-size:1.1rem;">开始看今日信号</a>
<p style="margin-top:1rem;font-size:0.85rem;color:#999;">升级会员解锁全部品种实时信号 · <a href="/premium">¥10/月起</a></p>
</div>""",
    ),
    "tutorial.html": PAGE_SHELL.format(
      title="期货新手入门教程 — 宗贸网",
      desc="期货新手入门：如何读懂行情、使用AI信号、参加模拟交易赛。",
      url="/tutorial",
      body="""
<div class="card" style="padding:2rem;line-height:1.8;">
<h1>期货新手入门</h1>
<h2>1. 了解大宗商品期货</h2>
<p>期货是以未来某时间交割的商品合约。宗贸网覆盖能源、黑色、有色、化工、农产品五大板块共34个品种。</p>
<h2>2. 如何看行情</h2>
<p>进入<a href="/market">行情中心</a>，点击品种名称查看价格走势、历史数据和AI信号。</p>
<h2>3. 如何使用AI信号</h2>
<p>信号包含<strong>方向（多/空）、入场价、目标价、止损价</strong>。建议先在<a href="/trading-contest">模拟赛</a>中验证，再考虑实盘。详见<a href="/methodology">信号方法论</a>。</p>
<h2>4. 常见问题</h2>
<p><strong>信号准确吗？</strong> 所有信号在<a href="/performance">战绩看板</a>公开追踪，可自行验证历史胜率。</p>
<p><strong>多少钱？</strong> 注册免费，会员¥10/月起。详见<a href="/premium">会员方案</a>。</p>
</div>""",
    ),
  }
  for name, html in pages.items():
    path = TPL / name
    if not path.exists() or "P1-GENERATED" not in path.read_text(encoding="utf-8", errors="replace"):
      path.write_text("<!-- P1-GENERATED -->\n" + html, encoding="utf-8")
      print(f"  ✓ template {name}")
    else:
      print(f"  · template {name} exists")


def patch_app():
  text = APP.read_text(encoding="utf-8")
  changed = False

  # New routes
  routes = '''
@app.get("/methodology")
async def page_methodology(request: Request):
    return render(request, "methodology.html")

@app.get("/compare")
async def page_compare(request: Request):
    kpi = get_performance_kpi()
    return render(request, "compare.html", kpi=kpi)

@app.get("/welcome")
async def page_welcome(request: Request):
    return render(request, "welcome.html")

@app.get("/tutorial")
async def page_tutorial(request: Request):
    return render(request, "tutorial.html")

'''
  if '@app.get("/methodology")' not in text:
    text = text.replace('@app.get("/pricing")', routes + '@app.get("/pricing")', 1)
    changed = True

  # Sitemap: new pages + limit cards
  if "zongmao.cn/methodology" not in text:
    text = text.replace(
      "('https://zongmao.cn/premium', now, '0.8', 'weekly'),",
      "('https://zongmao.cn/premium', now, '0.8', 'weekly'),\n"
      "        ('https://zongmao.cn/methodology', now, '0.7', 'monthly'),\n"
      "        ('https://zongmao.cn/compare', now, '0.7', 'monthly'),\n"
      "        ('https://zongmao.cn/tutorial', now, '0.6', 'monthly'),",
      1,
    )
    changed = True

  if "LIMIT 2000" in text:
    text = text.replace("ORDER BY c.publish_date DESC LIMIT 2000", "ORDER BY c.publish_date DESC LIMIT 300", 1)
    changed = True

  # News detail: related signals
  old_news = """    related = [dict(r) for r in conn.execute("SELECT id,title,category,created_at FROM news WHERE category=? AND id!=? ORDER BY id DESC LIMIT 5", (news["category"], news_id)).fetchall()]
    conn.close()
    return render(request, "news_detail.html", news=dict(news), related=related)"""
  new_news = """    related = [dict(r) for r in conn.execute("SELECT id,title,category,created_at FROM news WHERE category=? AND id!=? ORDER BY id DESC LIMIT 5", (news["category"], news_id)).fetchall()]
  # 同板块相关信号（P1内链）
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
    if not news_dict.get("author"):
        news_dict["author"] = "宗贸网研究院"
    conn.close()
    return render(request, "news_detail.html", news=news_dict, related=related, related_signals=related_signals)"""
  if "related_signals=related_signals" not in text:
    text = text.replace(old_news, new_news, 1)
    changed = True

  # Register redirect to welcome
  if '"redirect": "/welcome"' not in text:
    text = text.replace('"redirect": "/trading-contest"', '"redirect": "/welcome"', 1)
    changed = True

  # Premium page pass kpi
  old_prem = '    return render(request, "premium.html", tiers=tiers, stats=stats)'
  new_prem = '    kpi = get_performance_kpi()\n    return render(request, "premium.html", tiers=tiers, stats=stats, kpi=kpi)'
  if 'premium.html", tiers=tiers, stats=stats, kpi=kpi' not in text:
    text = text.replace(old_prem, new_prem, 1)
    changed = True

  # robots.txt add cards disallow
  old_robots_line = (
    'return Response(content="User-agent: *\\nAllow: /\\nDisallow: /admin/\\nDisallow: /api/\\n'
    'Sitemap: https://zongmao.cn/sitemap.xml\\nSitemap: https://zongmao.cn/feed.xml\\n'
    'Sitemap: https://zongmao.cn/rss.xml", media_type="text/plain")'
  )
  new_robots_line = (
    'return Response(content="User-agent: *\\nAllow: /\\nDisallow: /admin/\\nDisallow: /api/\\n'
    'Disallow: /cards/\\nSitemap: https://zongmao.cn/sitemap.xml\\nSitemap: https://zongmao.cn/feed.xml\\n'
    'Sitemap: https://zongmao.cn/rss.xml", media_type="text/plain")'
  )
  if "Disallow: /cards/" not in text and old_robots_line in text:
    text = text.replace(old_robots_line, new_robots_line, 1)
    changed = True

  if changed:
    backup(APP)
    APP.write_text(text, encoding="utf-8")
    print("✅ app.py patched")
  else:
    print("ℹ️  app.py already patched")


def patch_news_detail():
  path = TPL / "news_detail.html"
  text = path.read_text(encoding="utf-8")
  changed = False

  if "Article" not in text:
    schema = """
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"Article","headline":"{{ news.title | replace('"', '\\"') }}",
     "description":"{{ (news.summary or '') | replace('"', '\\"') }}",
     "author":{"@type":"Organization","name":"{{ news.author or '宗贸网研究院' }}"},
     "publisher":{"@type":"Organization","name":"宗贸网","url":"https://zongmao.cn"},
     "datePublished":"{{ news.created_at }}","url":"https://zongmao.cn/news/{{ news.id }}"}
    </script>"""
    text = text.replace("</head>", schema + "\n</head>", 1)
    changed = True

  if "related_signals" not in text:
    block = """
    {% if related_signals %}
    <div class="card">
        <div class="card-header"><span class="card-title">📡 相关品种 AI 信号</span><a href="/signals" style="font-size:0.85rem;">全部信号 →</a></div>
        {% for sig in related_signals %}
        <div style="padding:0.6rem 0;border-bottom:1px solid #eee;display:flex;justify-content:space-between;">
            <span><strong>{{ sig.name or sig.symbol }}</strong> <span style="color:{{ '#e74c3c' if sig.direction=='多' else '#27ae60' }};">{{ sig.direction }}</span> 入场{{ sig.entry_price }}</span>
            <a href="/price/{{ sig.symbol }}" style="font-size:0.85rem;">行情 →</a>
        </div>
        {% endfor %}
    </div>
    {% endif %}"""
    text = text.replace("<!-- CTA: 引导注册/订阅 -->", block + "\n    <!-- CTA: 引导注册/订阅 -->", 1)
    changed = True

  if changed:
    backup(path)
    path.write_text(text, encoding="utf-8")
    print("✅ news_detail.html patched")


def patch_register():
  path = TPL / "register.html"
  text = path.read_text(encoding="utf-8")
  if "免费注册，查看今日AI交易信号" in text:
    print("ℹ️  register.html already patched")
    return
  text = text.replace(
    "<title>注册 - 宗贸网</title>",
    '<title>免费注册 - 宗贸网 | 查看今日AI交易信号</title>\n'
    '    <meta name="description" content="免费注册宗贸网，查看34品种AI交易信号，参加模拟交易赛，7天体验全部功能。">',
    1,
  )
  text = text.replace(
    "<h2 style=\"text-align:center;margin-bottom:1.5rem;\">注册宗贸网</h2>",
    '<h2 style="text-align:center;margin-bottom:0.5rem;">注册宗贸网</h2>\n'
    '<p style="text-align:center;color:#666;font-size:0.9rem;margin-bottom:1.5rem;">免费查看今日AI信号 · 自动加入模拟赛</p>',
    1,
  )
  backup(path)
  path.write_text(text, encoding="utf-8")
  print("✅ register.html patched")


def patch_premium():
  path = TPL / "premium.html"
  text = path.read_text(encoding="utf-8")
  if "premium-trust-bar" in text:
    print("ℹ️  premium.html already patched")
    return
  bar = """
    <div class="premium-trust-bar" style="background:#f8f9fa;padding:1rem 2rem;text-align:center;border-bottom:1px solid #eee;">
        <span style="margin:0 1.5rem;">📊 已追踪 <strong>{{ kpi.total }}+</strong> 笔信号</span>
        <span style="margin:0 1.5rem;">🎯 历史胜率 <strong>{{ kpi.win_rate }}%</strong></span>
        <span style="margin:0 1.5rem;">📈 盈亏比 <strong>{{ kpi.profit_loss_ratio }}</strong></span>
        <a href="/performance" style="margin-left:1rem;font-size:0.9rem;">查看战绩 →</a>
    </div>"""
  text = text.replace("<body>", "<body>\n" + bar, 1)
  backup(path)
  path.write_text(text, encoding="utf-8")
  print("✅ premium.html patched")


def patch_price_cta():
  path = TPL / "price.html"
  text = path.read_text(encoding="utf-8")
  if "price-bottom-cta" in text:
    print("ℹ️  price.html CTA exists")
    return
  cta = """
    <!-- price-bottom-cta -->
    <div class="card" style="text-align:center;padding:2rem;background:linear-gradient(135deg,#1a5276,#2980b9);color:#fff;border:none;">
        <h3 style="margin:0 0 0.5rem;">获取 {{ quote.name }} AI 交易信号</h3>
        <p style="opacity:0.9;margin:0 0 1.2rem;font-size:0.95rem;">免费注册查看多空方向、目标价、止损价 · 模拟跟单零风险</p>
        <a href="/register" style="display:inline-block;background:#fff;color:#1a5276;padding:0.7rem 2rem;border-radius:50px;font-weight:600;text-decoration:none;margin-right:0.8rem;">免费注册</a>
        <a href="/signal/bullish/{{ quote.symbol }}" style="display:inline-block;border:2px solid #fff;color:#fff;padding:0.65rem 1.5rem;border-radius:50px;text-decoration:none;">查看信号 →</a>
    </div>"""
  text = text.replace("</div>\n\n<footer class=\"footer\">", cta + "\n</div>\n\n<footer class=\"footer\">", 1)
  backup(path)
  path.write_text(text, encoding="utf-8")
  print("✅ price.html CTA added")


def setup_cron():
  import subprocess
  marker = "# zongmao-p1"
  try:
    existing = subprocess.check_output(["crontab", "-l"], text=True, stderr=subprocess.DEVNULL)
  except subprocess.CalledProcessError:
    existing = ""
  if marker in existing:
    print("ℹ️  cron already configured")
    return
  lines = [
    f"0 7 * * 1-5 cd /opt/zongmao && /opt/zongmao/venv/bin/python3 baidu_push.py >> /var/log/zongmao/baidu_push.log 2>&1 {marker}",
    f"30 9 * * 1-5 cd /opt/zongmao && /opt/zongmao/venv/bin/python3 gen_news.py >> /var/log/zongmao/gen_news.log 2>&1 {marker}",
    f"0 9,15 * * 1-5 cd /opt/zongmao && /opt/zongmao/venv/bin/python3 gen_signals.py >> /var/log/zongmao/gen_signals.log 2>&1 {marker}",
  ]
  new_cron = existing.rstrip() + "\n" + "\n".join(lines) + "\n"
  subprocess.run(["crontab", "-"], input=new_cron, text=True, check=True)
  print("✅ cron jobs added")


def main():
  print("🚀 Zongmao P1 patch")
  write_templates()
  patch_app()
  patch_news_detail()
  patch_register()
  patch_premium()
  patch_price_cta()
  setup_cron()
  print("✅ P1 complete — restart zongmao.service")


if __name__ == "__main__":
  main()
