#!/usr/bin/env python3
"""P1 patches: og:image, unified nav, related links for product pages."""

import re
from pathlib import Path

SITE = Path(__file__).parent / "site"
OG_IMAGE = """    <meta property="og:image" content="https://www.esnlink.cn/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta name="twitter:image" content="https://www.esnlink.cn/og-image.png">"""

UNIFIED_NAV = """        <div class="nav-links">
            <a href="index.html">首页</a>
            <a href="call-center.html">智能外呼</a>
            <a href="sms.html">短信平台</a>
            <a href="iot.html">物联网</a>
            <a href="pricing.html">定价</a>
            <a href="docs/">文档</a>
            <a href="blog/">博客</a>
            <a href="booking.html" class="nav-btn btn-trial">免费试用</a>
        </div>"""

RELATED_LINKS_SMS = """
<!-- related-links -->
<section style="background:#f8fafc;padding:3rem 0">
    <div class="container" style="max-width:900px;margin:0 auto;padding:0 1.5rem">
        <h2 style="text-align:center;font-size:1.4rem;margin-bottom:1.5rem">相关资源</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem">
            <a href="docs/sms-api.html" style="background:#fff;padding:1.2rem;border-radius:12px;border:1px solid #e2e8f0;text-decoration:none;color:#1e293b"><strong>📄 短信 API 文档</strong><br><span style="font-size:0.85rem;color:#64748b">5 分钟完成接入</span></a>
            <a href="solutions/ecommerce.html" style="background:#fff;padding:1.2rem;border-radius:12px;border:1px solid #e2e8f0;text-decoration:none;color:#1e293b"><strong>🛒 电商短信方案</strong><br><span style="font-size:0.85rem;color:#64748b">大促触达最佳实践</span></a>
            <a href="solutions/finance.html" style="background:#fff;padding:1.2rem;border-radius:12px;border:1px solid #e2e8f0;text-decoration:none;color:#1e293b"><strong>🏦 金融短信方案</strong><br><span style="font-size:0.85rem;color:#64748b">验证码安全合规</span></a>
            <a href="pricing.html" style="background:#fff;padding:1.2rem;border-radius:12px;border:1px solid #e2e8f0;text-decoration:none;color:#1e293b"><strong>💰 定价方案</strong><br><span style="font-size:0.85rem;color:#64748b">0.03 元/条起</span></a>
        </div>
    </div>
</section>"""

RELATED_LINKS_IOT = RELATED_LINKS_SMS.replace("sms-api.html", "docs/").replace("短信 API 文档", "开发文档").replace("5 分钟完成接入", "物联网 API 指南")

PRODUCT_FAQ_SMS = """
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
{"@type":"Question","name":"翼星短信平台到达率多少？","acceptedAnswer":{"@type":"Answer","text":"国内三网综合到达率 99%+，验证码短信通常 5 秒内送达。"}},
{"@type":"Question","name":"短信 API 如何接入？","acceptedAnswer":{"@type":"Answer","text":"注册账号获取 AppID 和 AppSecret，参考 docs/sms-api.html 文档，5 分钟即可完成集成。"}},
{"@type":"Question","name":"短信价格是多少？","acceptedAnswer":{"@type":"Answer","text":"国内短信 0.03 元/条起，无最低消费，比阿里云/腾讯云便宜约 30%。"}}
]}
</script>"""

PRODUCT_SCHEMA_SMS = """
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Product","name":"翼星科技短信平台","description":"三网合一企业短信平台，支持验证码、通知、营销短信","brand":{"@type":"Brand","name":"翼星科技"},"offers":{"@type":"Offer","price":"0.03","priceCurrency":"CNY","priceSpecification":{"@type":"UnitPriceSpecification","unitText":"条"}}}
</script>"""


def patch_og_image(content: str) -> str:
    if "og:image" in content:
        return content
    return content.replace(
        '<meta property="og:locale" content="zh_CN">',
        '<meta property="og:locale" content="zh_CN">\n' + OG_IMAGE,
        1,
    )


def patch_nav(content: str) -> str:
    return re.sub(
        r'<div class="nav-links">.*?</div>\s*<button class="hamburger">',
        UNIFIED_NAV + '\n        <button class="hamburger">',
        content,
        count=1,
        flags=re.DOTALL,
    )


def patch_file(path: Path, extra_before_footer: str = "", extra_head: str = ""):
    if not path.exists():
        print(f"Skip {path} (not found)")
        return
    content = path.read_text(encoding="utf-8")
    content = patch_og_image(content)
    if '<div class="nav-links">' in content and "docs/" not in content:
        content = patch_nav(content)
    if extra_head and extra_head not in content:
        content = content.replace("</head>", extra_head + "\n</head>")
    if extra_before_footer and "related-links" not in content:
        content = content.replace("<!-- Footer -->", extra_before_footer + "\n<!-- Footer -->")
    path.write_text(content, encoding="utf-8")
    print(f"Patched {path.name}")


def main():
    patch_file(SITE / "sms.html", RELATED_LINKS_SMS, PRODUCT_FAQ_SMS + PRODUCT_SCHEMA_SMS)
    patch_file(SITE / "iot.html", RELATED_LINKS_IOT)
    patch_file(SITE / "edu.html", RELATED_LINKS_SMS.replace("sms-api", "docs").replace("短信 API", "开发文档"))
    # booking og:image
    booking = SITE / "booking.html"
    if booking.exists():
        c = booking.read_text(encoding="utf-8")
        if "og:image" not in c:
            c = c.replace(
                '<meta property="og:site_name"',
                '<meta property="og:image" content="https://www.esnlink.cn/og-image.png">\n    <meta property="og:site_name"',
            )
            booking.write_text(c, encoding="utf-8")
            print("Patched booking.html og:image")


if __name__ == "__main__":
    main()
