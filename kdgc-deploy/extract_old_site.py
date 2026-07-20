#!/usr/bin/env python3
"""Download live old site JS and merge with local archive into new site."""
import json
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

DIST = Path("/opt/kdgc-growth/frontend/dist")
OLD_HTML = Path("/opt/kdgc-growth/frontend/out/index.html")
OLD_ASSETS = Path("/opt/kdgc-growth/data/original/kdgc_full/assets")
IMG_OUT = DIST / "assets/images/old"
IMG_OUT.mkdir(parents=True, exist_ok=True)
EXTRACTED = Path("/opt/kdgc-growth/data/extracted")
EXTRACTED.mkdir(parents=True, exist_ok=True)

BODY_JS_URL = "https://img.wanwang.xin/pubsf/10247/10247201/cdn-static-pages/pages/pc/3807_zh-cn.html.Body.js?version=20250911081059"

NAME_MAP = {
    "56160517.png": "product-alumina.png",
    "56160518.png": "product-aln.png",
    "56160519.png": "product-dbc.png",
    "56160520.png": "product-components.png",
    "56160521.png": "about-factory.png",
    "56164209.png": "team-advisor.png",
    "56164220.png": "team-engineer.png",
    # Do NOT map 56164313.png — old CDN asset is AVIC「航宇救生」, not 中科国瓷
    "code.png": "wechat-qr.png",
    "favicon.ico": "favicon.ico",
}

for src_name, dst_name in NAME_MAP.items():
    for base in [OLD_ASSETS, Path("/opt/kdgc-growth/frontend/out")]:
        src = base / src_name
        if src.exists():
            shutil.copy2(src, IMG_OUT / dst_name)
            break

# Download live body JS
body_js_path = EXTRACTED / "body.js"
try:
    req = urllib.request.Request(BODY_JS_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body_js_path.write_bytes(resp.read())
    print(f"Downloaded Body.js: {body_js_path.stat().st_size} bytes")
except Exception as e:
    print(f"Body.js download failed: {e}")
    body_js_path = None

text_html = OLD_HTML.read_text(encoding="utf-8")
text_js = body_js_path.read_text(encoding="utf-8", errors="ignore") if body_js_path and body_js_path.exists() else ""
combined = text_html + "\n" + text_js


def strip(s):
    s = re.sub(r"\\u003c", "<", s)
    s = re.sub(r"\\u003e", ">", s)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def find_chunks(source, min_len=10):
    pattern = "[\u4e00-\u9fff][\u4e00-\u9fff0-9A-Za-z，。、；：""''（）·\\-\\s\\d]{%d,200}" % min_len
    chunks = re.findall(pattern, source)
    return list(dict.fromkeys(c.strip() for c in chunks if c.strip()))


# Contact from live JS
emails = re.findall(r"guanwn@kdgc\.cc|info@kdgc\.cc", combined)
phones = re.findall(r"1[3-9]\d{9}", combined)
phone = "15385884309" if "15385884309" in combined else (phones[0] if phones else "")
email = "guanwn@kdgc.cc"
address = "安徽省合肥市高新区科大先研院-智源楼"
if "科大先研院" in combined:
    m = re.search(r"安徽省[^\"'\\]{5,60}先研院[^\"'\\]{0,20}", combined)
    if m:
        address = m.group(0).replace("\\u002d", "-").replace("\\", "")

# Team from live JS + HTML
team = [
    {
        "role": "Chief Scientist",
        "title": "博士导师",
        "items": [
            "中国科学技术大学教授，博士生导师",
            "长期从事无机非金属材料和固体化学的教学和研究工作",
            "历任中国科学技术大学化学与材料学院院长，副校长",
            "亚洲固态离子学会理事，中国固态离子学会副理事长",
        ],
    },
    {
        "role": "Senior Engineer",
        "title": "高级工程师",
        "items": [
            "中国科学技术大学计算机系本科、博士，高级工程师",
            "曾任中国电科38所某重大航天项目副总设计师",
            "长期从事军工产品研制和项目管理工作",
            "拥有多项电子陶瓷相关发明专利",
        ],
    },
]

# Override from JS if found
for chunk in find_chunks(text_js, 15):
    if "博士生导师" in chunk and "科学技术大学" in chunk:
        team[0]["items"][0] = chunk
    if "38所" in chunk and "航天" in chunk:
        for i, item in enumerate(team[1]["items"]):
            if "38所" in item:
                team[1]["items"][i] = chunk

# Products from HTML
products = []
for m in re.finditer(r'<div class="prod-card">(.*?)</div>\s*</div>', text_html, re.S):
    block = m.group(1)
    img = re.search(r'src="([^"]+)"', block)
    h = re.search(r"<h3>(.*?)</h3>", block, re.S)
    p = re.search(r"<p>(.*?)</p>", block, re.S)
    tags = [strip(t) for t in re.findall(r'<span class="prod-tag">(.*?)</span>', block, re.S)]
    if h:
        img_name = img.group(1) if img else ""
        for old, new in NAME_MAP.items():
            img_name = img_name.replace(old, new)
        products.append({
            "name": strip(h.group(1)),
            "desc": strip(p.group(1)) if p else "",
            "img": f"/assets/images/old/{img_name}" if img_name else "",
            "tags": tags,
        })

# News from HTML (news-body structure)
news = []
for m in re.finditer(
    r'<div class="news-card">.*?<div class="day">(.*?)</div>.*?<div class="mon">(.*?)</div>.*?<h3>(.*?)</h3>.*?<p>(.*?)</p>',
    text_html,
    re.S,
):
    news.append({
        "date": f"{strip(m.group(2))} {strip(m.group(1))}",
        "title": strip(m.group(3)),
        "summary": strip(m.group(4)),
    })

# About
about_p = ""
m = re.search(r"<h3>从实验室到产业化</h3>\s*<p>(.*?)</p>", text_html, re.S)
if m:
    about_p = strip(m.group(1))
about_list = [strip(x) for x in re.findall(r"<li>(.*?)</li>", re.search(r'feature-list">(.*?)</ul>', text_html, re.S).group(1), re.S)] if re.search(r"feature-list", text_html) else []

warranty = ""
for c in find_chunks(text_js, 8):
    if "质保" in c or "诚信为本" in c:
        warranty = c
        break

content = {
    "email": email,
    "phone": phone,
    "address": address,
    "warranty": warranty,
    "products": products,
    "news": news,
    "team": team,
    "about_p": about_p,
    "about_list": about_list,
}
(EXTRACTED / "old_site_content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")

# Update pages
def patch_file(path: Path, replacements: list[tuple[str, str]]):
    if not path.exists():
        return
    html = path.read_text(encoding="utf-8")
    for old, new in replacements:
        if old in html and new:
            html = html.replace(old, new)
    path.write_text(html, encoding="utf-8")

common = [
    ("info@kdgc.cc", email),
    ("guanwn@kdgc.cc", email),
    ("安徽省合肥市高新区 [详细地址待补充]", address),
    ("安徽省合肥市高新区", address),
    ("[待公司提供]", ""),
    ("<p>[待公司提供]</p>", f"<p>{phone}</p>" if phone else ""),
]

for f in [DIST / "index.html", DIST / "about/index.html", DIST / "contact/index.html"]:
    patch_file(f, common)

# Homepage images
index = (DIST / "index.html").read_text(encoding="utf-8")
for old, new in [
    ("/assets/images/aln-substrate.webp", "/assets/images/old/product-aln.png"),
    ("/assets/images/dbc-amb.webp", "/assets/images/old/product-dbc.png"),
    ("/assets/images/alumina.webp", "/assets/images/old/product-alumina.png"),
]:
    index = index.replace(old, new)
if warranty and "质保" not in index:
    index = index.replace(
        '<div class="trust-bar">',
        f'<div class="trust-bar"><div class="container" style="text-align:center;padding:8px 0;font-size:13px;color:var(--muted)">{warranty}</div>',
        1,
    )
(DIST / "index.html").write_text(index, encoding="utf-8")

# About page team
about_path = DIST / "about/index.html"
if about_path.exists():
    about = about_path.read_text(encoding="utf-8")
    if about_p:
        about = re.sub(r"<p>安徽中科国瓷.*?</p>", f"<p>{about_p}</p>", about, count=1, flags=re.S)
    if about_list:
        about = about.replace(
            "<ul><li>ISO 9001 质量管理体系认证 [证书待上传]</li><li>产学研合作单位 [证明材料待上传]</li></ul>",
            "<ul class=\"feature-list\">" + "".join(f"<li>{x}</li>" for x in about_list) + "</ul>",
        )
    team_html = '<div class="grid-3">'
    imgs = ["team-advisor.png", "team-engineer.png"]
    for i, t in enumerate(team):
        img = f"/assets/images/old/{imgs[i] if i < len(imgs) else 'logo.png'}"
        items = "".join(f"<li>{x}</li>" for x in t["items"])
        team_html += f'<div class="content-block"><img src="{img}" alt="{t["title"]}" style="max-width:200px;border-radius:12px;margin-bottom:12px" loading="lazy"><div class="tag">{t["role"]}</div><h3>{t["title"]}</h3><ul>{items}</ul></div>'
    team_html += "</div>"
    about = re.sub(
        r"<h3 style=\"margin-top:24px\">专家团队</h3>.*?</section>",
        f"<h3 style=\"margin-top:24px\">专家团队</h3>{team_html}</div></section>",
        about,
        count=1,
        flags=re.S,
    )
    about_path.write_text(about, encoding="utf-8")

# Contact page
contact_path = DIST / "contact/index.html"
if contact_path.exists():
    c = contact_path.read_text(encoding="utf-8")
    c = c.replace("<h3>📞 电话</h3><p>09:00-21:00</p>", f"<h3>📞 电话</h3><p><a href=\"tel:{phone}\">{phone}</a></p>")
    c = c.replace("<h3>📞 电话</h3><p>[待公司提供]</p>", f"<h3>📞 电话</h3><p><a href=\"tel:{phone}\">{phone}</a></p>")
    if (IMG_OUT / "wechat-qr.png").exists() and "wechat-qr" not in c:
        c = c.replace(
            '<form id="lead-form"',
            '<div class="content-block" style="text-align:center;margin-bottom:24px"><h3>微信咨询</h3><img src="/assets/images/old/wechat-qr.png" alt="微信二维码" width="160" loading="lazy"><p>客服时间 09:00-21:00</p></div>\n<form id="lead-form"',
        )
    contact_path.write_text(c, encoding="utf-8")

# News page static
if news:
    news_path = DIST / "news/index.html"
    static = "".join(
        f'<div class="content-block"><span class="tag">{n["date"]}</span><h3>{n["title"]}</h3><p>{n["summary"]}</p></div>'
        for n in news
    )
    nhtml = news_path.read_text(encoding="utf-8")
    nhtml = re.sub(
        r'<div class="container" id="news-list">.*?</div>\s*</section>',
        f'<div class="container" id="news-list">{static}</div></section>',
        nhtml,
        count=1,
        flags=re.S,
    )
    news_path.write_text(nhtml, encoding="utf-8")

# Product pages
slug_map = [("aln-substrate.html", "product-aln.png", 1), ("dbc-amb.html", "product-dbc.png", 2), ("alumina.html", "product-alumina.png", 0)]
for slug, img, idx in slug_map:
    p = DIST / "products" / slug
    if p.exists() and idx < len(products):
        prod = products[idx]
        html = p.read_text(encoding="utf-8")
        if f"/assets/images/old/{img}" not in html:
            html = html.replace(
                '<section class="page-hero">',
                f'<section class="page-hero"><div class="container"><img src="/assets/images/old/{img}" alt="{prod["name"]}" style="max-width:440px;margin:20px auto 0;border-radius:16px;display:block" loading="lazy"></div>',
                1,
            )
        html = re.sub(r"<h1>.*?</h1>", f"<h1>{prod['name']}</h1>", html, count=1, flags=re.S)
        p.write_text(html, encoding="utf-8")

# favicon
if (IMG_OUT / "favicon.ico").exists():
    shutil.copy2(IMG_OUT / "favicon.ico", DIST / "assets/images/favicon.ico")

# Update PostgreSQL via seed script
print(json.dumps(content, ensure_ascii=False, indent=2))
print(f"\nDone. Images: {len(list(IMG_OUT.glob('*')))} files")
