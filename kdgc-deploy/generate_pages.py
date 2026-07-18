#!/usr/bin/env python3
"""Generate KDGC static pages."""
import os
from pathlib import Path

DIST = Path(__file__).parent / "frontend" / "dist"

NAV = """<nav class="nav"><div class="nav-inner">
<a href="/" class="nav-logo">中科<span>国瓷</span></a>
<div class="nav-links">
<a href="/products/">产品</a><a href="/technology/">技术</a><a href="/applications/">应用</a>
<a href="/cases/">案例</a><a href="/about/">关于</a><a href="/news/">新闻</a><a href="/knowledge/">知识库</a>
<a href="/contact/" class="nav-cta">获取方案</a>
</div>
<button class="menu-toggle" aria-label="菜单">☰</button>
</div></nav>"""

FOOTER = """<footer><div class="footer-grid container" style="padding:0">
<div><h4>中科国瓷</h4><p style="font-size:14px;margin-top:8px">高导热陶瓷基板与电子陶瓷材料方案商</p></div>
<div><h4>产品</h4><a href="/products/aln-substrate.html">氮化铝基板</a><a href="/products/dbc-amb.html">DBC/AMB基板</a></div>
<div><h4>公司</h4><a href="/about/">关于我们</a><a href="/news/">新闻</a><a href="/contact/">联系</a></div>
<div><h4>联系</h4><a href="mailto:info@kdgc.cc">info@kdgc.cc</a></div>
</div>
<div class="footer-bottom">© 2026 安徽中科国瓷新型元器件有限公司 · 皖ICP备XXXXXXXX号 [待公司提供]</div></footer>
<script src="/assets/js/main.js"></script>"""


def page(title, desc, body, canonical=""):
    canon = f'<link rel="canonical" href="https://kdgc.cc{canonical}">' if canonical else ""
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
{canon}<link rel="stylesheet" href="/assets/css/style.css">
</head><body>{NAV}<main>{body}</main>{FOOTER}</body></html>"""


PAGES = {
    "contact/index.html": (
        "联系我们 — 中科国瓷",
        "获取陶瓷基板技术方案与样品申请",
        """<section class="page-hero"><div class="container"><h1>联系我们</h1><p>技术团队 24 小时内回复</p></div></section>
<section><div class="container"><div class="grid-3" style="margin-bottom:40px">
<div class="content-block"><h3>📍 地址</h3><p>安徽省合肥市高新区 [详细地址待补充]</p></div>
<div class="content-block"><h3>📞 电话</h3><p>[待公司提供]</p></div>
<div class="content-block"><h3>✉️ 邮箱</h3><p><a href="mailto:info@kdgc.cc">info@kdgc.cc</a></p></div>
</div>
<form id="lead-form" class="form-box"><div class="form-hp"><input name="website" tabindex="-1"></div>
<div class="form-group"><label>公司名称 *</label><input name="company" required></div>
<div class="form-group"><label>联系人 *</label><input name="contact_name" required></div>
<div class="form-group"><label>手机 *</label><input name="phone" required></div>
<div class="form-group"><label>邮箱</label><input name="email" type="email"></div>
<div class="form-group"><label>产品兴趣</label><select name="product_interest"><option>氮化铝陶瓷基板</option><option>DBC/AMB陶瓷基板</option><option>氧化铝陶瓷</option></select></div>
<div class="form-group"><label>需求描述</label><textarea name="requirement"></textarea></div>
<button type="submit" class="btn btn-primary" style="width:100%">提交咨询</button><div class="form-msg"></div></form></div></section>""",
        "/contact/",
    ),
    "about/index.html": (
        "关于我们 — 中科国瓷",
        "安徽中科国瓷，高导热陶瓷基板与电子陶瓷材料方案商",
        """<section class="page-hero"><div class="container"><h1>关于中科国瓷</h1><p>中科大技术转化 · 产学研合作</p></div></section>
<section><div class="container content-block"><h2>公司简介</h2>
<p>安徽中科国瓷新型元器件有限公司专注于高导热陶瓷基板与电子陶瓷材料的研发与生产。公司与中科大先进陶瓷实验室保持产学研合作，为半导体封装、电力电子、新能源汽车等领域提供高可靠材料解决方案。</p>
<p>公司核心产品包括氮化铝陶瓷基板（导热率 200W/m·K）、DBC/AMB 覆铜陶瓷基板、高纯度氧化铝陶瓷等。</p>
<h3 style="margin-top:24px">资质荣誉</h3><ul><li>ISO 9001 质量管理体系认证 [证书待上传]</li><li>产学研合作单位 [证明材料待上传]</li></ul>
<h3 style="margin-top:24px">专家团队</h3><p>核心团队具有材料学、电力电子领域深厚背景。[专家详细信息待公司提供]</p></div></section>""",
        "/about/",
    ),
    "technology/index.html": (
        "技术能力 — 中科国瓷",
        "陶瓷材料技术参数与能力对比",
        """<section class="page-hero"><div class="container"><h1>技术能力</h1></div></section>
<section><div class="container"><div class="content-block"><h2>材料参数对比</h2>
<table><tr><th>参数</th><th>Al₂O₃</th><th>AlN</th><th>DBC</th><th>AMB</th></tr>
<tr><td>导热率</td><td>20–30</td><td>150–200</td><td>24–28</td><td>90–170</td></tr>
<tr><td>介电强度</td><td>≥15</td><td>≥14</td><td>≥15</td><td>≥15</td></tr></table>
<p style="margin-top:16px;font-size:13px;color:var(--muted)">* 详细检测报告 [待公司提供]</p>
<a href="/contact/?intent=pdf" class="btn btn-primary" style="margin-top:20px">下载完整参数表</a></div></div></section>""",
        "/technology/",
    ),
    "applications/index.html": (
        "应用场景 — 中科国瓷",
        "IGBT、新能源电控、半导体封装陶瓷基板应用",
        """<section class="page-hero"><div class="container"><h1>应用场景</h1></div></section>
<section><div class="container grid-3">
<div class="content-block"><h3>IGBT 功率模块</h3><p>氮化铝基板提供优异散热，延长器件寿命。</p></div>
<div class="content-block"><h3>新能源汽车电控</h3><p>DBC 基板满足高功率密度电控系统需求。</p></div>
<div class="content-block"><h3>半导体封装</h3><p>高可靠陶瓷基板用于先进封装工艺。</p></div>
<div class="content-block"><h3>航空航天电子</h3><p>高可靠陶瓷材料用于极端环境。[脱敏案例]</p></div>
</div></section>""",
        "/applications/",
    ),
    "products/index.html": (
        "产品中心 — 中科国瓷",
        "氮化铝陶瓷基板、DBC/AMB基板、氧化铝陶瓷",
        """<section class="page-hero"><div class="container"><h1>产品中心</h1></div></section>
<section><div class="container grid-3">
<a href="/products/aln-substrate.html" class="card"><div class="card-body"><h3>氮化铝陶瓷基板</h3><p>导热 200W/m·K</p></div></a>
<a href="/products/dbc-amb.html" class="card"><div class="card-body"><h3>DBC/AMB 陶瓷基板</h3><p>电力电子封装</p></div></a>
<a href="/products/alumina.html" class="card"><div class="card-body"><h3>氧化铝陶瓷</h3><p>纯度 99.7%</p></div></a>
</div></section>""",
        "/products/",
    ),
    "cases/index.html": (
        "客户案例 — 中科国瓷",
        "半导体封装、新能源电控陶瓷基板成功案例",
        """<section class="page-hero"><div class="container"><h1>客户案例</h1></div></section>
<section><div class="container grid-3" id="cases-list"><p>加载中...</p></div></section>
<script>fetch('/api/cases').then(r=>r.json()).then(items=>{document.getElementById('cases-list').innerHTML=items.map(c=>`<a href="/cases/${c.slug}.html" class="card"><div class="card-body"><span class="tag">${c.industry}</span><h3>${c.title}</h3><p>${c.challenge}</p></div></a>`).join('')}).catch(()=>{});</script>""",
        "/cases/",
    ),
    "news/index.html": (
        "新闻动态 — 中科国瓷",
        "中科国瓷最新新闻与行业动态",
        """<section class="page-hero"><div class="container"><h1>新闻动态</h1></div></section>
<section><div class="container" id="news-list"><p>加载中...</p></div></section>
<script>fetch('/api/news').then(r=>r.json()).then(items=>{document.getElementById('news-list').innerHTML=items.map(n=>`<div class="content-block"><span class="tag">${(n.published_at||'').slice(0,10)}</span><h3><a href="/news/${n.slug}.html">${n.title}</a></h3><p>${n.summary}</p></div>`).join('')}).catch(()=>{});</script>""",
        "/news/",
    ),
    "knowledge/index.html": (
        "技术知识库 — 中科国瓷",
        "陶瓷基板选型、氮化铝、DBC技术文章",
        """<section class="page-hero"><div class="container"><h1>技术知识库</h1></div></section>
<section><div class="container">
<div class="content-block"><h3>氮化铝 vs 氧化铝：如何选择陶瓷基板？</h3><p>功率密度决定材料选择，AlN 适用于高散热场景。</p></div>
<div class="content-block"><h3>DBC 与 AMB 工艺对比</h3><p>DBC 适合大功率，AMB 适合复杂结构。</p></div>
<div class="content-block"><h3>IGBT 模块陶瓷基板选型指南</h3><p>导热率、热膨胀匹配、铜层厚度是关键参数。</p></div>
</div></section>""",
        "/knowledge/",
    ),
    "privacy.html": (
        "隐私政策 — 中科国瓷",
        "中科国瓷网站隐私政策",
        """<section class="page-hero"><div class="container"><h1>隐私政策</h1></div></section>
<section><div class="container content-block"><p>我们收集您通过联系表单提交的信息（公司名、联系人、电话、邮箱），仅用于回复您的咨询。我们不会向第三方出售您的个人信息。</p></div></section>""",
        "/privacy.html",
    ),
    "404.html": (
        "页面未找到 — 中科国瓷",
        "",
        """<section class="page-hero"><div class="container"><h1>404</h1><p>页面未找到</p><a href="/" class="btn btn-primary" style="margin-top:20px">返回首页</a></div></section>""",
        "",
    ),
    "admin/index.html": (
        "管理后台 — 中科国瓷",
        "",
        """<section class="page-hero"><div class="container"><h1>线索管理</h1></div></section>
<section><div class="container"><div class="form-group"><label>Admin Token</label><input id="token" type="password"><button class="btn btn-primary" onclick="loadLeads()">加载线索</button></div>
<div id="leads" class="content-block" style="margin-top:20px"></div></div></section>
<script>async function loadLeads(){const t=document.getElementById('token').value;const r=await fetch('/api/leads',{headers:{'X-Admin-Token':t}});const d=await r.json();document.getElementById('leads').innerHTML='<pre>'+JSON.stringify(d,null,2)+'</pre>'}</script>""",
        "/admin/",
    ),
    "en/index.html": (
        "ZK Guoci — Advanced Ceramic Substrates",
        "High thermal conductivity ceramic substrates for semiconductor packaging",
        """<section class="hero"><div class="hero-bg"></div><div class="hero-content">
<h1>ZK Guoci — Ceramic Substrate Solutions</h1>
<p>AlN substrates · DBC/AMB boards · High reliability for power electronics</p>
<a href="/contact/" class="btn btn-primary">Contact Us</a>
</div></section>
<section><div class="container content-block"><h2>Products</h2>
<p>Aluminum Nitride (AlN) substrates with 200 W/m·K thermal conductivity.</p>
<p>DBC/AMB copper-bonded ceramic substrates for power modules.</p>
</div></section>""",
        "/en/",
    ),
}

PRODUCTS = {
    "products/aln-substrate.html": ("氮化铝陶瓷基板", "aln-substrate", "导热 200W/m·K，IGBT 封装首选"),
    "products/dbc-amb.html": ("DBC/AMB 陶瓷基板", "dbc-amb", "电力电子封装核心材料"),
    "products/alumina.html": ("氧化铝陶瓷", "alumina", "纯度 92%–99.7%，耐温 1600°C"),
}

for path, (title, slug, tagline) in PRODUCTS.items():
    PAGES[path] = (
        f"{title} — 中科国瓷",
        f"{tagline} | 中科国瓷",
        f"""<section class="page-hero"><div class="container"><h1>{title}</h1><p>{tagline}</p></div></section>
<section><div class="container"><div class="content-block" id="product-detail"><p>加载中...</p></div>
<a href="/contact/?product={slug}" class="btn btn-primary">咨询此产品</a></div></section>
<script>fetch('/api/products/{slug}').then(r=>r.json()).then(p=>{{document.getElementById('product-detail').innerHTML=`<h2>${{p.name}}</h2><p>${{p.content}}</p><h3>规格参数</h3><pre>${{JSON.stringify(p.specs,null,2)}}</pre>`}}).catch(()=>{{}});</script>""",
        f"/products/{slug}.html",
    )

CASES = {
    "cases/semiconductor-packaging.html": "semiconductor-packaging",
    "cases/ev-power-module.html": "ev-power-module",
}

for path, slug in CASES.items():
    PAGES[path] = (
        "客户案例 — 中科国瓷",
        "陶瓷基板客户成功案例",
        f"""<section class="page-hero"><div class="container"><h1>客户案例</h1></div></section>
<section><div class="container content-block" id="case-detail"><p>加载中...</p></div></section>
<script>fetch('/api/cases').then(r=>r.json()).then(items=>{{const c=items.find(x=>x.slug==='{slug}');if(c)document.getElementById('case-detail').innerHTML=`<h2>${{c.title}}</h2><p><strong>挑战：</strong>${{c.challenge}}</p><p><strong>方案：</strong>${{c.solution}}</p><p><strong>结果：</strong>${{c.result}}</p>`}});</script>""",
        f"/cases/{slug}.html",
    )

for rel, (title, desc, body, canon) in PAGES.items():
    out = DIST / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(title, desc, body, canon), encoding="utf-8")
    print("wrote", rel)

# robots + sitemap
(DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://kdgc.cc/sitemap.xml\n")
urls = ["/", "/products/", "/technology/", "/applications/", "/cases/", "/about/", "/news/", "/knowledge/", "/contact/", "/en/"]
urls += [f"/products/{s}.html" for s in ["aln-substrate", "dbc-amb", "alumina"]]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls:
    sitemap += f"  <url><loc>https://kdgc.cc{u}</loc><changefreq>weekly</changefreq></url>\n"
sitemap += "</urlset>"
(DIST / "sitemap.xml").write_text(sitemap)
print("done")
