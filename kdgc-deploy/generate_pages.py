#!/usr/bin/env python3
"""Generate KDGC static pages — news/knowledge detail pages, EN market, accurate contact info."""

from pathlib import Path

DIST = Path(__file__).parent / "frontend" / "dist"

FOOTER_ZH = """<footer><div class="footer-grid container" style="padding:0">
<div><h4>中科国瓷</h4><p style="font-size:14px;margin-top:8px">高导热陶瓷基板与电子陶瓷材料方案商</p></div>
<div><h4>产品</h4><a href="/products/aln-substrate.html">氮化铝基板</a><a href="/products/dbc-amb.html">DBC/AMB基板</a><a href="/products/alumina.html">氧化铝陶瓷</a></div>
<div><h4>公司</h4><a href="/about/">关于我们</a><a href="/news/">新闻</a><a href="/knowledge/">知识库</a><a href="/contact/">联系</a></div>
<div><h4>联系</h4><a href="mailto:guanwn@kdgc.cc">guanwn@kdgc.cc</a><br><a href="tel:15385884309">153-8588-4309</a></div>
</div>
<div class="footer-bottom">© 2026 安徽中科国瓷新型元器件有限公司 · <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">皖ICP备2021010166号-1</a> · <a href="/en/">English</a></div></footer>
<script src="/assets/js/main.js"></script>"""

NAV_ZH = """<nav class="nav"><div class="nav-inner">
<a href="/" class="nav-logo">中科<span>国瓷</span><span class="nav-tagline">半导体级陶瓷基板</span></a>
<div class="nav-links">
<a href="/products/">产品</a><a href="/technology/">技术</a><a href="/applications/">应用</a>
<a href="/cases/">案例</a><a href="/about/">关于</a><a href="/news/">新闻</a><a href="/knowledge/">知识库</a>
<a href="/en/" style="opacity:.8">EN</a>
<a href="/contact/" class="nav-cta">获取方案</a>
</div>
<button class="menu-toggle" aria-label="菜单">☰</button>
</div></nav>"""

NAV_EN = """<nav class="nav"><div class="nav-inner">
<a href="/en/" class="nav-logo">ZK <span>Guoci</span><span class="nav-tagline">Ceramic Substrates</span></a>
<div class="nav-links">
<a href="/en/products.html">Products</a><a href="/en/technology.html">Technology</a><a href="/en/applications.html">Applications</a>
<a href="/en/cases.html">Cases</a><a href="/en/about.html">About</a><a href="/en/news.html">News</a>
<a href="/" style="opacity:.8">中文</a>
<a href="/contact/" class="nav-cta">Contact</a>
</div>
<button class="menu-toggle" aria-label="Menu">☰</button>
</div></nav>"""

FOOTER_EN = """<footer><div class="footer-grid container" style="padding:0">
<div><h4>ZK Guoci</h4><p style="font-size:14px;margin-top:8px">Advanced ceramic substrates for power electronics</p></div>
<div><h4>Products</h4><a href="/en/products.html">AlN Substrates</a><a href="/en/technology.html">Technology</a></div>
<div><h4>Company</h4><a href="/en/about.html">About</a><a href="/en/news.html">News</a><a href="/contact/">Contact</a></div>
<div><h4>Contact</h4><a href="mailto:guanwn@kdgc.cc">guanwn@kdgc.cc</a></div>
</div>
<div class="footer-bottom">© 2026 Anhui ZK Guoci New Components Co., Ltd. · <a href="/">中文站</a></div></footer>
<script src="/assets/js/main.js"></script>"""


def page_zh(title, desc, body, canonical=""):
    canon = f'<link rel="canonical" href="https://kdgc.cc{canonical}">' if canonical else ""
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
{canon}<link rel="stylesheet" href="/assets/css/style.css">
</head><body>{NAV_ZH}<main>{body}</main>{FOOTER_ZH}</body></html>"""


def page_en(title, desc, body, canonical=""):
    canon = f'<link rel="canonical" href="https://kdgc.cc{canonical}">' if canonical else ""
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
{canon}<link rel="alternate" hreflang="zh-CN" href="https://kdgc.cc/">
<link rel="alternate" hreflang="en" href="https://kdgc.cc/en/">
<link rel="stylesheet" href="/assets/css/style.css">
</head><body>{NAV_EN}<main>{body}</main>{FOOTER_EN}</body></html>"""


NEWS = [
    {"slug": "ceramic-summit-2025", "date": "2025-06-15", "title": "参加2025中国先进陶瓷材料产业峰会",
     "summary": "展示最新高导热氮化铝基板产品，获行业专家与客户广泛关注。",
     "body": "<p>2025年6月，中科国瓷参加中国先进陶瓷材料产业峰会，展示氮化铝陶瓷基板系列产品。公司产品导热率、可靠性指标获得与会专家关注，并与多家功率半导体企业达成初步合作意向。</p>"},
    {"slug": "iso9001-certification", "date": "2025-03-20", "title": "通过 ISO 9001 质量管理体系认证",
     "summary": "质量管理体系覆盖陶瓷材料全生产流程。",
     "body": "<p>经权威机构审核，中科国瓷质量管理体系符合 ISO 9001 标准，覆盖原料检验、成型烧结、金属化、检测出货全流程。</p>"},
    {"slug": "alumina-mass-production", "date": "2025-01-08", "title": "新一代氧化铝陶瓷基板量产",
     "summary": "高纯度氧化铝基板通过多家客户验证，进入规模化量产。",
     "body": "<p>公司高纯度氧化铝陶瓷基板完成多家客户验证，正式进入规模化量产阶段，可满足电子封装与高温绝缘应用需求。</p>"},
    {"slug": "aln-thermal-test", "date": "2025-08-01", "title": "氮化铝基板通过第三方导热率检测",
     "summary": "导热率实测达 195 W/m·K。",
     "body": "<p>第三方检测机构对氮化铝陶瓷基板进行导热率测试，实测值达 195 W/m·K，满足 IGBT 功率模块散热需求。完整检测报告可向销售索取。</p>"},
    {"slug": "ev-partnership", "date": "2025-10-12", "title": "与某头部新能源车企达成战略合作",
     "summary": "为电控系统提供高导热陶瓷基板解决方案。",
     "body": "<p>中科国瓷为某头部新能源车企电控系统提供高导热陶瓷基板定制方案，产品通过车规级可靠性测试，进入小批量供货阶段。（客户名称脱敏）</p>"},
]

KNOWLEDGE = [
    {"slug": "aln-vs-alumina", "title": "氮化铝 vs 氧化铝：如何选择陶瓷基板？",
     "summary": "功率密度决定材料选择，AlN 适用于高散热场景。",
     "body": """<p>氧化铝（Al₂O₃）成本低、工艺成熟，适用于中低功率场景；氮化铝（AlN）导热率可达 150–200 W/m·K，是 IGBT、激光器等高热流密度应用的首选。</p>
<p>选型时需综合考虑：热流密度、CTE 匹配、绝缘要求、成本预算。欢迎联系技术团队获取选型表。</p>"""},
    {"slug": "dbc-vs-amb", "title": "DBC 与 AMB 工艺对比",
     "summary": "DBC 适合大功率平面封装，AMB 适合复杂结构与高可靠性场景。",
     "body": """<p><strong>DBC（直接覆铜）</strong>：工艺成熟、成本较低，适合平面大功率模块。</p>
<p><strong>AMB（活性钎焊）</strong>：铜层结合力更强，适合复杂结构和车规级高可靠性要求。</p>"""},
    {"slug": "igbt-substrate-guide", "title": "IGBT 模块陶瓷基板选型指南",
     "summary": "导热率、热膨胀匹配、铜层厚度是关键参数。",
     "body": """<p>IGBT 模块选型陶瓷基板时，重点关注：导热率 ≥150 W/m·K、与硅/铜 CTE 匹配、介电强度、铜层厚度与键合工艺兼容性。</p>
<a href="/contact/?intent=pdf" class="btn btn-primary" style="margin-top:16px">获取完整选型 PDF</a>"""},
]

NEWS_LIST_HTML = "".join(
    f'<div class="content-block"><span class="tag">{n["date"]}</span>'
    f'<h3><a href="/news/{n["slug"]}.html">{n["title"]}</a></h3><p>{n["summary"]}</p></div>'
    for n in NEWS
)

KNOWLEDGE_LIST_HTML = "".join(
    f'<a href="/knowledge/{k["slug"]}.html" class="card" style="text-decoration:none;color:inherit">'
    f'<div class="card-body"><h3>{k["title"]}</h3><p>{k["summary"]}</p></div></a>'
    for k in KNOWLEDGE
)

PAGES_ZH = {
    "contact/index.html": page_zh("联系我们 — 中科国瓷", "获取陶瓷基板技术方案与样品申请",
        """<section class="page-hero"><div class="container"><h1>联系我们</h1><p>技术团队 24 小时内回复</p></div></section>
<section><div class="container"><div class="grid-3" style="margin-bottom:40px">
<div class="content-block"><h3>📍 地址</h3><p>安徽省合肥市高新区科大先研院-智源楼</p></div>
<div class="content-block"><h3>📞 电话</h3><p><a href="tel:15385884309">153-8588-4309</a></p></div>
<div class="content-block"><h3>✉️ 邮箱</h3><p><a href="mailto:guanwn@kdgc.cc">guanwn@kdgc.cc</a></p></div>
</div>
<form id="lead-form" class="form-box"><div class="form-hp"><input name="website" tabindex="-1"></div>
<div class="form-group"><label>公司名称 *</label><input name="company" required></div>
<div class="form-group"><label>联系人 *</label><input name="contact_name" required></div>
<div class="form-group"><label>手机 *</label><input name="phone" required></div>
<div class="form-group"><label>邮箱</label><input name="email" type="email"></div>
<div class="form-group"><label>产品兴趣</label><select name="product_interest"><option>氮化铝陶瓷基板</option><option>DBC/AMB陶瓷基板</option><option>氧化铝陶瓷</option></select></div>
<div class="form-group"><label>需求描述</label><textarea name="requirement"></textarea></div>
<button type="submit" class="btn btn-primary" style="width:100%">提交咨询</button><div class="form-msg"></div></form></div></section>""", "/contact/"),

    "about/index.html": page_zh("关于我们 — 中科国瓷", "安徽中科国瓷，高导热陶瓷基板与电子陶瓷材料方案商",
        """<section class="page-hero"><div class="container"><h1>关于中科国瓷</h1><p>中科大技术转化 · 产学研合作</p></div></section>
<section><div class="container content-block"><h2>公司简介</h2>
<p>安徽中科国瓷新型元器件有限公司专注于高导热陶瓷基板与电子陶瓷材料的研发与生产，为半导体封装、电力电子、新能源汽车等领域提供高可靠材料解决方案。</p>
<h3 style="margin-top:28px">核心团队</h3>
<div class="grid-3" style="margin-top:16px">
<div class="content-block"><h4>陈初升 · 首席科学家</h4><p>中国科学技术大学教授、博士生导师，国家杰出青年基金获得者，长期从事无机非金属材料和固体化学研究。</p></div>
<div class="content-block"><h4>李超 · 总经理</h4><p>中国科学技术大学近代物理系本科、硕士，曾任多家科技企业研发管理岗位。</p></div>
<div class="content-block"><h4>李彤 · 总工程师</h4><p>中国科学技术大学计算机系本科、博士，高级工程师，长期从事军工产品研制和项目管理。</p></div>
</div>
<h3 style="margin-top:28px">企业理念</h3><ul><li><strong>诚信至上</strong> — 产品承诺质保 5 年</li><li><strong>坚持创新</strong> — 产学研合作持续迭代</li><li><strong>快速响应</strong> — 7×24 小时全天候服务</li></ul>
<p style="margin-top:16px;font-size:13px;color:var(--muted)">以上内容整理自公司官网公开信息（www.kdgc.cc）</p></div></section>""", "/about/"),

    "technology/index.html": page_zh("技术能力 — 中科国瓷", "陶瓷材料技术参数、工艺流程与检测能力",
        """<section class="page-hero"><div class="container"><h1>技术能力</h1><p>材料 · 工艺 · 检测一体化</p></div></section>
<section><div class="container">
<div class="content-block"><h2>核心工艺能力</h2><ul>
<li>氮化铝陶瓷成型与烧结</li><li>DBC 直接覆铜金属化</li><li>AMB 活性钎焊金属化</li><li>高纯度氧化铝精密加工</li></ul></div>
<div class="content-block" style="margin-top:24px"><h2>材料参数对比</h2>
<table><tr><th>参数</th><th>Al₂O₃</th><th>AlN</th><th>DBC</th><th>AMB</th></tr>
<tr><td>导热率 W/m·K</td><td>20–30</td><td>150–200</td><td>24–28</td><td>90–170</td></tr>
<tr><td>热膨胀系数</td><td>7.2×10⁻⁶</td><td>4.5×10⁻⁶</td><td>7.4</td><td>7.1</td></tr>
<tr><td>介电强度 kV/mm</td><td>≥15</td><td>≥14</td><td>≥15</td><td>≥15</td></tr>
<tr><td>最高工作温度</td><td>1600°C</td><td>1800°C</td><td>350°C</td><td>350°C</td></tr></table>
<p style="font-size:13px;color:var(--muted);margin-top:12px">* 详细第三方检测报告可向销售索取</p>
<a href="/contact/?intent=pdf" class="btn btn-primary" style="margin-top:20px">下载技术参数 PDF</a></div>
<div class="content-block" style="margin-top:24px"><h2>相关阅读</h2>
<p><a href="/knowledge/aln-vs-alumina.html">氮化铝 vs 氧化铝选型</a> · <a href="/knowledge/dbc-vs-amb.html">DBC vs AMB 工艺对比</a></p></div>
</div></section>""", "/technology/"),

    "applications/index.html": page_zh("应用场景 — 中科国瓷", "IGBT、新能源电控、半导体封装陶瓷基板应用",
        """<section class="page-hero"><div class="container"><h1>应用场景</h1><p>功率电子 · 新能源车 · 半导体 · 航空航天</p></div></section>
<section><div class="container grid-3">
<a href="/cases/semiconductor-packaging.html" class="card"><div class="card-body"><span class="tag">半导体</span><h3>IGBT 功率模块</h3><p>氮化铝基板提供优异散热，延长器件寿命。查看半导体封装案例 →</p></div></a>
<a href="/cases/ev-power-module.html" class="card"><div class="card-body"><span class="tag">新能源</span><h3>新能源汽车电控</h3><p>DBC 基板满足高功率密度电控系统需求。查看电控案例 →</p></div></a>
<div class="content-block"><span class="tag">电力电子</span><h3>逆变器与轨道交通</h3><p>DBC/AMB 基板用于大功率逆变模块，耐温 350°C。</p></div>
<div class="content-block"><span class="tag">航空航天</span><h3>航空航天电子</h3><p>高可靠陶瓷材料用于极端环境电子系统。（案例脱敏）</p></div>
</div></section>""", "/applications/"),

    "news/index.html": page_zh("新闻动态 — 中科国瓷", "中科国瓷最新新闻与行业动态",
        f"""<section class="page-hero"><div class="container"><h1>新闻动态</h1></div></section>
<section><div class="container" id="news-list">{NEWS_LIST_HTML}</div></section>""", "/news/"),

    "knowledge/index.html": page_zh("技术知识库 — 中科国瓷", "陶瓷基板选型、氮化铝、DBC技术文章",
        f"""<section class="page-hero"><div class="container"><h1>技术知识库</h1><p>选型指南 · 工艺对比 · 行业实践</p></div></section>
<section><div class="container grid-3">{KNOWLEDGE_LIST_HTML}</div></section>""", "/knowledge/"),

    "cases/index.html": page_zh("客户案例 — 中科国瓷", "半导体封装、新能源电控陶瓷基板成功案例",
        """<section class="page-hero"><div class="container"><h1>客户案例</h1></div></section>
<section><div class="container grid-3" id="cases-list">
<a href="/cases/semiconductor-packaging.html" class="card"><div class="card-body"><span class="tag">semiconductor</span><h3>半导体 IGBT 模块散热方案</h3><p>热阻降低 35%，通过 1000 小时老化测试。</p></div></a>
<a href="/cases/ev-power-module.html" class="card"><div class="card-body"><span class="tag">ev</span><h3>新能源汽车电控 Tier1</h3><p>通过车规级测试，进入小批量供货。</p></div></a>
</div></section>
<script>fetch('/api/cases').then(r=>r.json()).then(items=>{if(!items.length)return;document.getElementById('cases-list').innerHTML=items.map(c=>`<a href="/cases/${c.slug}.html" class="card"><div class="card-body"><span class="tag">${c.industry}</span><h3>${c.title}</h3><p>${c.challenge}</p></div></a>`).join('')}).catch(()=>{});</script>""", "/cases/"),

    "products/index.html": page_zh("产品中心 — 中科国瓷", "氮化铝陶瓷基板、DBC/AMB基板、氧化铝陶瓷",
        """<section class="page-hero"><div class="container"><h1>产品中心</h1></div></section>
<section><div class="container grid-3">
<a href="/products/aln-substrate.html" class="card"><img src="/assets/images/old/product-aln.png" alt="氮化铝" class="card-img" loading="lazy"><div class="card-body"><h3>氮化铝陶瓷基板</h3><p>导热 200W/m·K</p></div></a>
<a href="/products/dbc-amb.html" class="card"><img src="/assets/images/old/product-dbc.png" alt="DBC" class="card-img" loading="lazy"><div class="card-body"><h3>DBC/AMB 陶瓷基板</h3><p>电力电子封装</p></div></a>
<a href="/products/alumina.html" class="card"><img src="/assets/images/old/product-alumina.png" alt="氧化铝" class="card-img" loading="lazy"><div class="card-body"><h3>氧化铝陶瓷</h3><p>纯度 99.7%</p></div></a>
</div></section>""", "/products/"),

    "privacy.html": page_zh("隐私政策 — 中科国瓷", "中科国瓷网站隐私政策",
        """<section class="page-hero"><div class="container"><h1>隐私政策</h1></div></section>
<section><div class="container content-block"><p>我们收集您通过联系表单提交的信息，仅用于回复咨询，不会向第三方出售。</p></div></section>""", "/privacy.html"),

    "404.html": page_zh("页面未找到 — 中科国瓷", "",
        """<section class="page-hero"><div class="container"><h1>404</h1><p>页面未找到</p><a href="/" class="btn btn-primary" style="margin-top:20px">返回首页</a></div></section>""", ""),
}

CASES = [
    {"slug": "semiconductor-packaging", "title": "某半导体封装企业 IGBT 模块散热方案", "industry": "半导体",
     "challenge": "IGBT 模块工作温度高，传统基板散热不足导致器件寿命缩短。",
     "solution": "采用氮化铝陶瓷基板（导热率 195 W/m·K），优化铜层厚度与键合工艺。",
     "result": "模块热阻降低 35%，通过 1000 小时高温老化测试。"},
    {"slug": "ev-power-module", "title": "某新能源汽车电控 Tier1 供应商", "industry": "新能源",
     "challenge": "电控系统功率密度提升，需要更高导热率的基板材料。",
     "solution": "提供 DBC 陶瓷基板定制方案，匹配客户封装工艺。",
     "result": "通过车规级可靠性测试，进入小批量供货阶段。"},
]

PRODUCTS = [
    ("products/aln-substrate.html", "氮化铝陶瓷基板", "aln-substrate", "导热 200W/m·K，IGBT 封装首选"),
    ("products/dbc-amb.html", "DBC/AMB 陶瓷基板", "dbc-amb", "电力电子封装核心材料"),
    ("products/alumina.html", "氧化铝陶瓷", "alumina", "纯度 92%–99.7%，耐温 1600°C"),
]

# EN pages for US market
PAGES_EN = {
    "en/index.html": page_en("ZK Guoci — Advanced Ceramic Substrates", "AlN and DBC/AMB ceramic substrates for power electronics",
        """<section class="hero"><div class="hero-bg"></div><div class="hero-content">
<h1>Advanced Ceramic Substrate Solutions</h1>
<p>AlN · DBC/AMB · High reliability for IGBT, EV inverters &amp; power modules</p>
<div class="hero-actions"><a href="/contact/" class="btn btn-primary">Request Datasheet</a><a href="/contact/?intent=sample" class="btn btn-ghost">Free Sample</a></div>
</div></section>
<section><div class="container grid-3" style="margin-top:40px">
<a href="/en/products.html" class="card"><div class="card-body"><h3>AlN Substrates</h3><p>200 W/m·K thermal conductivity</p></div></a>
<a href="/en/technology.html" class="card"><div class="card-body"><h3>Technology</h3><p>Material specs &amp; processes</p></div></a>
<a href="/en/applications.html" class="card"><div class="card-body"><h3>Applications</h3><p>IGBT · EV · Semiconductor</p></div></a>
</div></section>""", "/en/"),
    "en/products.html": page_en("Products — ZK Guoci", "AlN, DBC/AMB and alumina ceramic substrates",
        """<section class="page-hero"><div class="container"><h1>Products</h1></div></section>
<section><div class="container grid-3">
<a href="/products/aln-substrate.html" class="card"><div class="card-body"><h3>AlN Ceramic Substrates</h3><p>150–200 W/m·K, ideal for IGBT modules</p></div></a>
<a href="/products/dbc-amb.html" class="card"><div class="card-body"><h3>DBC/AMB Substrates</h3><p>Power electronics packaging</p></div></a>
<a href="/products/alumina.html" class="card"><div class="card-body"><h3>Alumina Ceramics</h3><p>92%–99.7% purity, up to 1600°C</p></div></a>
</div></section>""", "/en/products.html"),
    "en/technology.html": page_en("Technology — ZK Guoci", "Ceramic material specifications and processes",
        """<section class="page-hero"><div class="container"><h1>Technology</h1></div></section>
<section><div class="container content-block"><h2>Material Comparison</h2>
<table><tr><th>Property</th><th>Al₂O₃</th><th>AlN</th><th>DBC</th><th>AMB</th></tr>
<tr><td>Thermal conductivity</td><td>20–30</td><td>150–200</td><td>24–28</td><td>90–170</td></tr>
<tr><td>CTE (×10⁻⁶/°C)</td><td>7.2</td><td>4.5</td><td>7.4</td><td>7.1</td></tr></table>
<a href="/contact/?intent=pdf" class="btn btn-primary" style="margin-top:20px">Download Full Spec Sheet</a></div></section>""", "/en/technology.html"),
    "en/applications.html": page_en("Applications — ZK Guoci", "IGBT, EV power modules, semiconductor packaging",
        """<section class="page-hero"><div class="container"><h1>Applications</h1></div></section>
<section><div class="container grid-3">
<div class="content-block"><h3>IGBT Power Modules</h3><p>AlN substrates for superior heat dissipation.</p></div>
<div class="content-block"><h3>EV Traction Inverters</h3><p>DBC boards for high power density EV systems.</p></div>
<div class="content-block"><h3>Semiconductor Packaging</h3><p>High-reliability ceramics for advanced packaging.</p></div>
</div></section>""", "/en/applications.html"),
    "en/cases.html": page_en("Case Studies — ZK Guoci", "Semiconductor and EV ceramic substrate success stories",
        """<section class="page-hero"><div class="container"><h1>Case Studies</h1></div></section>
<section><div class="container grid-3">
<a href="/cases/semiconductor-packaging.html" class="card"><div class="card-body"><h3>IGBT Thermal Solution</h3><p>35% thermal resistance reduction</p></div></a>
<a href="/cases/ev-power-module.html" class="card"><div class="card-body"><h3>EV Tier-1 Supplier</h3><p>Automotive qualification passed</p></div></a>
</div></section>""", "/en/cases.html"),
    "en/about.html": page_en("About — ZK Guoci", "Anhui ZK Guoci advanced ceramic components",
        """<section class="page-hero"><div class="container"><h1>About ZK Guoci</h1></div></section>
<section><div class="container content-block"><p>Anhui ZK Guoci New Components Co., Ltd. develops and manufactures high thermal conductivity ceramic substrates for semiconductor packaging, power electronics, and new energy vehicles.</p>
<p>Our team includes researchers from the University of Science and Technology of China (USTC) with deep expertise in materials science and power electronics.</p></div></section>""", "/en/about.html"),
    "en/news.html": page_en("News — ZK Guoci", "Latest news from ZK Guoci",
        f"""<section class="page-hero"><div class="container"><h1>News</h1></div></section>
<section><div class="container">{"".join(f'<div class="content-block"><span class="tag">{n["date"]}</span><h3><a href="/news/{n["slug"]}.html">{n["title"]}</a></h3><p>{n["summary"]}</p></div>' for n in NEWS)}</div></section>""", "/en/news.html"),
}


def main():
    pages = dict(PAGES_ZH)
    pages.update(PAGES_EN)

    for path, title, slug, tagline in PRODUCTS:
        pages[path] = page_zh(f"{title} — 中科国瓷", f"{tagline} | 中科国瓷",
            f"""<section class="page-hero"><div class="container"><h1>{title}</h1><p>{tagline}</p></div></section>
<section><div class="container"><div class="content-block" id="product-detail"><p>加载中...</p></div>
<a href="/contact/?product={slug}" class="btn btn-primary">咨询此产品</a></div></section>
<script>fetch('/api/products/{slug}').then(r=>r.json()).then(p=>{{document.getElementById('product-detail').innerHTML=`<h2>${{p.name}}</h2><p>${{p.content}}</p>`}}).catch(()=>{{document.getElementById('product-detail').innerHTML='<p>{tagline}</p>'}});</script>""",
            f"/products/{slug}.html")

    for c in CASES:
        path = f"cases/{c['slug']}.html"
        pages[path] = page_zh(f"{c['title']} — 中科国瓷", "陶瓷基板客户成功案例",
            f"""<section class="page-hero"><div class="container"><h1>客户案例</h1><span class="tag">{c['industry']}</span></div></section>
<section><div class="container content-block"><h2>{c['title']}</h2>
<p><strong>挑战：</strong>{c['challenge']}</p><p><strong>方案：</strong>{c['solution']}</p><p><strong>结果：</strong>{c['result']}</p>
<p style="margin-top:24px"><a href="/cases/">← 返回案例列表</a></p></div></section>""", f"/cases/{c['slug']}.html")

    for rel, html in pages.items():
        out = DIST / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print("wrote", rel)

    for n in NEWS:
        rel = f"news/{n['slug']}.html"
        html = page_zh(f"{n['title']} — 中科国瓷", n["summary"],
            f"""<section class="page-hero"><div class="container"><h1>{n['title']}</h1><span class="tag">{n['date']}</span></div></section>
<section><div class="container content-block">{n['body']}
<p style="margin-top:24px"><a href="/news/">← 返回新闻列表</a></p></div></section>""", f"/news/{n['slug']}.html")
        (DIST / rel).write_text(html, encoding="utf-8")
        print("wrote", rel)

    for k in KNOWLEDGE:
        rel = f"knowledge/{k['slug']}.html"
        html = page_zh(f"{k['title']} — 中科国瓷", k["summary"],
            f"""<section class="page-hero"><div class="container"><h1>{k['title']}</h1></div></section>
<section><div class="container content-block">{k['body']}
<p style="margin-top:24px"><a href="/knowledge/">← 返回知识库</a></p></div></section>""", f"/knowledge/{k['slug']}.html")
        (DIST / rel).write_text(html, encoding="utf-8")
        print("wrote", rel)

    urls = ["/", "/products/", "/technology/", "/applications/", "/cases/", "/about/", "/news/", "/knowledge/", "/contact/"]
    urls += [f"/news/{n['slug']}.html" for n in NEWS]
    urls += [f"/knowledge/{k['slug']}.html" for k in KNOWLEDGE]
    urls += [f"/products/{s}.html" for _, _, s, _ in PRODUCTS]
    urls += [f"/cases/{c['slug']}.html" for c in CASES]
    urls += ["/en/", "/en/products.html", "/en/technology.html", "/en/applications.html", "/en/cases.html", "/en/about.html", "/en/news.html"]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        sitemap += f"  <url><loc>https://kdgc.cc{u}</loc><changefreq>weekly</changefreq></url>\n"
    sitemap += "</urlset>"
    (DIST / "sitemap.xml").write_text(sitemap)
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://kdgc.cc/sitemap.xml\n")
    print("done", len(urls), "urls in sitemap")


if __name__ == "__main__":
    main()
