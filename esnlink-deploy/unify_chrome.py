#!/usr/bin/env python3
"""Unify navbar + footer across all esnlink.cn pages to match homepage style."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent
SITE = ROOT / "site"
CSS_HREF = "/css/header-footer.css"

HAMBURGER_JS = """
<script>
(function(){
  var h = document.querySelector('.hamburger');
  var n = document.querySelector('.nav-links');
  if (h && n && !h.dataset.bound) {
    h.dataset.bound = '1';
    h.addEventListener('click', function(e){
      e.stopPropagation();
      n.classList.toggle('open');
    });
    n.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){ n.classList.remove('open'); });
    });
    document.addEventListener('click', function(e){
      if (!n.contains(e.target) && !h.contains(e.target)) { n.classList.remove('open'); }
    });
  }
})();
</script>
"""

NAV_ZH = """<!-- site-chrome-nav -->
<nav class="navbar">
    <div class="container nav-container">
        <a href="/" class="logo">
            <span>esnlink · 翼星科技</span>
            <span class="logo-slogan">链接创造价值</span>
        </a>
        <div class="nav-links">
            <a href="/">首页</a>
            <a href="/call-center.html">智能外呼</a>
            <a href="/sms.html">短信平台</a>
            <a href="/iot.html">物联网</a>
            <a href="/pricing.html">定价</a>
            <a href="/docs/">文档</a>
            <a href="/blog/">博客</a>
            <a href="/cases/">案例</a>
            <a href="/en/">EN</a>
            <a href="/booking.html" class="nav-btn btn-trial">免费试用</a>
            <a href="/#contact" class="nav-btn">咨询</a>
        </div>
        <button class="hamburger" aria-label="菜单">☰</button>
    </div>
</nav>
"""

NAV_EN = """<!-- site-chrome-nav -->
<nav class="navbar">
    <div class="container nav-container">
        <a href="/en/" class="logo">
            <span>esnlink</span>
            <span class="logo-slogan">Link Creates Value</span>
        </a>
        <div class="nav-links">
            <a href="/en/">Home</a>
            <a href="/en/call-center.html">AI Calling</a>
            <a href="/en/sms.html">SMS</a>
            <a href="/iot.html">IoT</a>
            <a href="/pricing.html">Pricing</a>
            <a href="/docs/">Docs</a>
            <a href="/cases/">Cases</a>
            <a href="/">中文</a>
            <a href="/booking.html" class="nav-btn btn-trial">Free Trial</a>
            <a href="/#contact" class="nav-btn">Contact</a>
        </div>
        <button class="hamburger" aria-label="Menu">☰</button>
    </div>
</nav>
"""

FOOTER_ZH = """<!-- site-chrome-footer -->
<footer class="footer">
    <div class="container">
        <div class="footer-grid">
            <div class="footer-brand">
                <a href="/" class="logo"><span>esnlink · 翼星科技</span></a>
                <p>智能通信与物联网解决方案提供商<br><strong style="color:#60a5fa;font-size:1.1rem;letter-spacing:0.08em;">链接创造价值</strong></p>
            </div>
            <div class="footer-col">
                <h5>产品</h5>
                <a href="/call-center.html">智能呼叫中心</a>
                <a href="/sms.html">短信平台</a>
                <a href="/iot.html">物联网模组</a>
                <a href="/edu.html">教育 AI</a>
            </div>
            <div class="footer-col">
                <h5>支持</h5>
                <a href="/faq.html">帮助中心</a>
                <a href="/pricing.html">定价方案</a>
                <a href="/booking.html">预约演示</a>
                <a href="/docs/">开发文档</a>
                <a href="/blog/">技术博客</a>
            </div>
            <div class="footer-col">
                <h5>关于</h5>
                <a href="/about.html">公司简介</a>
                <a href="/cases/">客户案例</a>
                <a href="/#contact">联系我们</a>
                <a href="/solutions/education.html">教育行业</a>
                <a href="/solutions/ecommerce.html">电商行业</a>
                <a href="/solutions/finance.html">金融行业</a>
                <a href="/en/">English</a>
            </div>
        </div>
        <div class="footer-bottom">
            <span>&copy; 2025 合肥翼星智能科技有限公司 All Rights Reserved.</span>
            <span style="margin-left:1rem"><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener" style="color:#94a3b8;text-decoration:none">皖ICP备2026012968号-1</a></span>
        </div>
    </div>
</footer>
"""

FOOTER_EN = """<!-- site-chrome-footer -->
<footer class="footer">
    <div class="container">
        <div class="footer-grid">
            <div class="footer-brand">
                <a href="/en/" class="logo"><span>esnlink</span></a>
                <p>Enterprise communication &amp; IoT cloud<br><strong style="color:#60a5fa;font-size:1.1rem;letter-spacing:0.08em;">Link Creates Value</strong></p>
            </div>
            <div class="footer-col">
                <h5>Products</h5>
                <a href="/en/call-center.html">AI Call Center</a>
                <a href="/en/sms.html">SMS Platform</a>
                <a href="/iot.html">IoT</a>
                <a href="/pricing.html">Pricing</a>
            </div>
            <div class="footer-col">
                <h5>Resources</h5>
                <a href="/docs/">Docs</a>
                <a href="/cases/">Cases</a>
                <a href="/booking.html">Book a demo</a>
                <a href="/faq.html">FAQ</a>
            </div>
            <div class="footer-col">
                <h5>Company</h5>
                <a href="/about.html">About</a>
                <a href="/#contact">Contact</a>
                <a href="/">中文</a>
            </div>
        </div>
        <div class="footer-bottom">
            <span>&copy; 2025 Hefei Yixing Intelligent Technology Co., Ltd.</span>
            <span style="margin-left:1rem"><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener" style="color:#94a3b8;text-decoration:none">皖ICP备2026012968号-1</a></span>
        </div>
    </div>
</footer>
"""

LANDING_TOP = """<!-- site-chrome-nav -->
<nav class="navbar" style="background:rgba(15,23,42,.85);border-bottom:1px solid rgba(255,255,255,.08)">
    <div class="container nav-container">
        <a href="/" class="logo" style="color:#fff;-webkit-text-fill-color:#fff;background:none">
            <span>esnlink · 翼星科技</span>
            <span class="logo-slogan" style="color:#93c5fd;border-left-color:rgba(147,197,253,.35)">链接创造价值</span>
        </a>
        <div class="nav-links">
            <a href="/" style="color:#e2e8f0">首页</a>
            <a href="/sms.html" style="color:#e2e8f0">短信平台</a>
            <a href="/pricing.html" style="color:#e2e8f0">定价</a>
            <a href="/booking.html" class="nav-btn btn-trial">免费试用</a>
        </div>
        <button class="hamburger" aria-label="菜单" style="color:#fff">☰</button>
    </div>
</nav>
"""


def ensure_css(html: str) -> str:
    if "header-footer.css" in html:
        # normalize to absolute path
        html = re.sub(
            r'href="[^"]*header-footer\.css"',
            f'href="{CSS_HREF}"',
            html,
        )
        return html
    if re.search(r"</head>", html, re.I):
        return re.sub(
            r"</head>",
            f'    <link rel="stylesheet" href="{CSS_HREF}">\n</head>',
            html,
            count=1,
            flags=re.I,
        )
    return html


def replace_nav(html: str, nav: str) -> str:
    # Remove floating lang-switch on EN pages (nav already has 中文)
    html = re.sub(
        r'<a href="/index\.html" class="lang-switch">.*?</a>\s*',
        "",
        html,
        flags=re.I | re.S,
    )
    patterns = [
        r"<!-- site-chrome-nav -->\s*<nav[\s\S]*?</nav>",
        r"<nav class=\"navbar\"[\s\S]*?</nav>",
        r"<nav class=\"nav[^\"]*\"[\s\S]*?</nav>",
    ]
    for pat in patterns:
        if re.search(pat, html, re.I):
            return re.sub(pat, nav.strip(), html, count=1, flags=re.I)
    # insert after <body...>
    return re.sub(r"(<body[^>]*>)", r"\1\n" + nav, html, count=1, flags=re.I)


def replace_footer(html: str, footer: str) -> str:
    patterns = [
        r"<!-- site-chrome-footer -->\s*<footer[\s\S]*?</footer>",
        r"<footer[\s\S]*?</footer>",
    ]
    for pat in patterns:
        if re.search(pat, html, re.I):
            return re.sub(pat, footer.strip(), html, count=1, flags=re.I)
    return re.sub(r"</body>", footer + "\n</body>", html, count=1, flags=re.I)


def ensure_hamburger(html: str) -> str:
    if "nav-links" in html and "hamburger" in html and "classList.toggle('open')" in html:
        # already has some toggle logic
        if "dataset.bound" in html or "classList.toggle(\"open\")" in html:
            return html
    if "site-chrome-hamburger" in html:
        return html
    snippet = "<!-- site-chrome-hamburger -->" + HAMBURGER_JS
    return re.sub(r"</body>", snippet + "\n</body>", html, count=1, flags=re.I)


def mark_active(html: str, path: Path) -> str:
    rel = "/" + str(path.relative_to(SITE)).replace("\\", "/")
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    elif rel.endswith("index.html"):
        rel = "/"
    candidates = {
        "/": ["/", "/index.html"],
        "/call-center.html": ["/call-center.html"],
        "/sms.html": ["/sms.html"],
        "/iot.html": ["/iot.html"],
        "/pricing.html": ["/pricing.html"],
        "/docs/": ["/docs/", "/docs/index.html", "/docs/sms-api.html"],
        "/blog/": ["/blog/"],
        "/cases/": ["/cases/", "/cases/index.html"],
        "/en/": ["/en/", "/en/index.html"],
        "/en/call-center.html": ["/en/call-center.html"],
        "/en/sms.html": ["/en/sms.html"],
        "/booking.html": ["/booking.html"],
        "/about.html": ["/about.html"],
        "/faq.html": ["/faq.html"],
        "/edu.html": ["/edu.html"],
    }
    active_href = None
    for href, matches in candidates.items():
        if rel in matches or any(rel.startswith(m.rstrip("/") + "/") for m in matches if m.endswith("/")):
            # prefer most specific
            if active_href is None or len(href) > len(active_href):
                active_href = href
    if not active_href:
        return html

    def add_active(m: re.Match) -> str:
        tag = m.group(0)
        if "nav-btn" in tag:
            return tag
        if re.search(r'\bactive\b', tag):
            return tag
        if "class=" in tag:
            return re.sub(r'class="([^"]*)"', r'class="\1 active"', tag, count=1)
        return tag.replace("<a ", '<a class="active" ', 1)

    def mark_in_nav_links(m: re.Match) -> str:
        block = m.group(0)
        block = re.sub(
            rf'<a href="{re.escape(active_href)}"[^>]*>',
            add_active,
            block,
            count=1,
        )
        return block

    return re.sub(
        r'<div class="nav-links">[\s\S]*?</div>\s*<button class="hamburger"',
        mark_in_nav_links,
        html,
        count=1,
    )


def strip_legacy_headers(html: str) -> str:
    """Remove leftover old top bars after the unified chrome nav."""
    # Keep only the first site-chrome navbar; drop subsequent navbar clones.
    parts = re.split(r"(<!-- site-chrome-nav -->\s*<nav class=\"navbar\"[\s\S]*?</nav>)", html, maxsplit=1)
    if len(parts) == 3:
        head, chrome, rest = parts
        rest = re.sub(r"<nav class=\"navbar\"[\s\S]*?</nav>\s*", "", rest, count=1)
        rest = re.sub(
            r"<!--\s*={0,5}\s*导航栏\s*={0,5}\s*-->\s*<div class=\"navbar\"[\s\S]*?</div>\s*",
            "",
            rest,
            count=1,
        )
        rest = re.sub(
            r"<!--\s*={0,5}\s*Navbar\s*={0,5}\s*-->\s*<header class=\"navbar\"[\s\S]*?</header>\s*",
            "",
            rest,
            count=1,
        )
        rest = re.sub(
            r"<header class=\"navbar\"[\s\S]*?</header>\s*",
            "",
            rest,
            count=1,
        )
        # orphan comment-only markers
        rest = re.sub(r"<!--\s*={0,5}\s*导航栏\s*={0,5}\s*-->\s*", "", rest)
        html = head + chrome + rest
    return html


def process(path: Path) -> bool:
    rel = path.relative_to(SITE).as_posix()
    html = path.read_text(encoding="utf-8")
    original = html

    is_en = rel.startswith("en/")
    is_landing = rel.startswith("landing/")

    html = ensure_css(html)

    if is_landing:
        html = replace_nav(html, LANDING_TOP)
        # keep landing footer minimal but branded
        html = replace_footer(
            html,
            """<!-- site-chrome-footer -->
<footer class="footer" style="padding:1.5rem 0;text-align:center">
    <div class="container">
        <p style="font-size:.85rem">&copy; 2025 合肥翼星智能科技有限公司 · <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener" style="color:#94a3b8;text-decoration:none">皖ICP备2026012968号-1</a> · <a href="/" style="color:#60a5fa">官网首页</a></p>
    </div>
</footer>
""",
        )
        # remove absolute logo-mini if present
        html = re.sub(r'<a href="/index\.html" class="logo-mini">.*?</a>\s*', "", html)
    elif is_en:
        html = replace_nav(html, NAV_EN)
        html = replace_footer(html, FOOTER_EN)
    else:
        html = replace_nav(html, NAV_ZH)
        # homepage contact can stay page-local; rewrite first consult link after inject is /#contact which is fine
        if rel == "index.html":
            html = html.replace('href="/#contact" class="nav-btn">咨询</a>', 'href="#contact" class="nav-btn">咨询</a>', 1)
        html = replace_footer(html, FOOTER_ZH)

    html = strip_legacy_headers(html)
    html = ensure_hamburger(html)
    html = mark_active(html, path)

    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main():
    # sync css into site/css
    src = ROOT / "css" / "header-footer.css"
    dst = SITE / "css" / "header-footer.css"
    dst.parent.mkdir(parents=True, exist_ok=True)
    css = src.read_text(encoding="utf-8")
    if ".nav-links a.active" not in css:
        css += """
.nav-links a.active { color: #2563eb; font-weight: 700; }
.logo { text-decoration: none; }
.footer-brand .logo { display: inline-flex; }
"""
    dst.write_text(css, encoding="utf-8")
    src.write_text(css, encoding="utf-8")

    changed = []
    for path in sorted(SITE.rglob("*.html")):
        if process(path):
            changed.append(path.relative_to(SITE).as_posix())
            print("updated", path.relative_to(SITE))
        else:
            print("unchanged", path.relative_to(SITE))
    print(f"done: {len(changed)} files changed")


if __name__ == "__main__":
    main()
