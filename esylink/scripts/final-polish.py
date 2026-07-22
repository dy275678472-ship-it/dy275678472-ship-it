#!/usr/bin/env python3
"""Final polish: homepage, product images, webp expansion."""
from pathlib import Path

WEB = Path("/var/www/esylink")

# Homepage
idx = WEB / "index.html"
html = idx.read_text(encoding="utf-8")
html = html.replace(
    "AI智能外呼，<br>让每个电话<span class=\"text-indigo-300\">都是成交机会</span>",
    "AI外呼 + 云客服一体化平台<br>让企业<span class=\"text-indigo-300\">少招客服，多接线索</span>",
)
html = html.replace(
    "DeepSeek大模型语义理解 × 真人级语音合成<br class=\"hidden sm:block\"><span class=\"text-indigo-300\">外呼成本降低80% · 接通率提升3倍 · 7×24小时自动值守</span>",
    "支持智能外呼、来电接待、400热线、工单CRM、本地号码<br class=\"hidden sm:block\"><span class=\"text-indigo-300\">适合教育/口腔/保险/金融/电商 · 最快当天开通 · 7天免费试用</span>",
)
if "/trust/" not in html:
    html = html.replace(
        '<a href="/about" class="hover:text-indigo-300 transition">关于</a>',
        '<a href="/trust/" class="hover:text-indigo-300 transition">信任</a>\n                <a href="/about" class="hover:text-indigo-300 transition">关于</a>',
    )
idx.write_text(html, encoding="utf-8")
print("✓ homepage")

# Product images on dialer/cs
img = '<img src="/images/product-dashboard.webp" alt="易连云通信产品仪表盘" width="800" height="520" class="w-full rounded-xl shadow-lg my-8" loading="lazy">'
for rel in ["dialer/index.html", "cs/index.html", "cloud-cs.html", "400.html"]:
    p = WEB / rel
    if p.exists():
        t = p.read_text(encoding="utf-8")
        if "product-dashboard.webp" not in t and "</h1>" in t:
            t = t.replace("</h1>", "</h1>\n" + img, 1)
            p.write_text(t, encoding="utf-8")
            print(f"✓ image → {rel}")

# PNG → WebP
n = 0
for f in WEB.rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    if "product-dashboard.png" in t:
        f.write_text(t.replace("product-dashboard.png", "product-dashboard.webp"), encoding="utf-8")
        n += 1
print(f"✓ png→webp: {n} files")

# Nav: add compliance link to all pages with standard nav
for f in WEB.rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    if 'href="/cases/"' in t and 'href="/trust/"' not in t and 'href="/about"' in t:
        t = t.replace(
            '<a href="/about"',
            '<a href="/trust/" class="hover:text-indigo-300 transition">信任</a>\n                <a href="/about"',
            1,
        )
        f.write_text(t, encoding="utf-8")

print("✓ final polish done")
