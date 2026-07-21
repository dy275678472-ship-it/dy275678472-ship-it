#!/usr/bin/env python3
"""Generate KDGC static site from migrated www.kdgc.cc content (oxygen sensors).

Source of truth: https://www.kdgc.cc (Wanwang site: /sy about, /xwzx products, /lxwm news, /ahzkgcxxyqjyxgs contact)
Note: santa6.kdjc.cc does not resolve; content mirrored from www.kdgc.cc.
"""

from pathlib import Path

import content_site
from content_site import CASES as INDUSTRY_CASES, KNOWLEDGE, MAP_ADDRESS, MAP_LAT, MAP_LNG, MAP_TITLE, product_name

ROOT = Path(__file__).parent
DIST = ROOT / "frontend" / "dist"
NEWS_CONTENT = ROOT / "content" / "news"
IMG = DIST / "assets" / "images"


def asset_url(rel: str, fallback: str | None = None) -> str:
    """Prefer WebP when present under frontend/dist/assets/images/."""
    rel = rel.lstrip("/")
    if rel.startswith("assets/images/"):
        rel = rel[len("assets/images/") :]
    webp = IMG / Path(rel).with_suffix(".webp")
    orig = IMG / rel
    if webp.exists():
        return f"/assets/images/{webp.relative_to(IMG).as_posix()}"
    if orig.exists():
        return f"/assets/images/{orig.relative_to(IMG).as_posix()}"
    if fallback:
        return asset_url(fallback) if not fallback.startswith("/") else fallback
    return f"/assets/images/{rel}"


def has_asset(rel: str) -> bool:
    rel = rel.lstrip("/")
    if rel.startswith("assets/images/"):
        rel = rel[len("assets/images/") :]
    return (IMG / rel).exists() or (IMG / Path(rel).with_suffix(".webp")).exists()


def page_hero(title: str, subtitle: str = "", banner: str | None = None) -> str:
    """Top banner; uses photo background when WebP/JPG asset exists."""
    cls = "page-hero"
    style = ""
    if banner and has_asset(banner):
        cls += " page-hero--photo"
        url = asset_url(banner)
        style = (
            f' style="background-image:linear-gradient(105deg,rgba(7,20,38,.92) 0%,'
            f"rgba(7,20,38,.75) 48%,rgba(7,20,38,.5) 100%),url('{url}');"
            f'background-size:cover;background-position:center"'
        )
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    return f'<section class="{cls}"{style}><div class="container"><h1>{title}</h1>{sub}</div></section>'


def contact_promises_html(lang: str = "zh") -> str:
    items = (
        [
            ("bolt", "快速响应", "技术与商务咨询优先处理"),
            ("clock", "7×24 响应", "客服时段 09:00–21:00，紧急需求全天候跟进"),
            ("pin", "合肥高新区", ADDRESS),
        ]
        if lang == "zh"
        else [
            ("bolt", "Fast response", "Technical & commercial inquiries prioritized"),
            ("clock", "7×24 follow-up", "Support 09:00–21:00; urgent requests tracked around the clock"),
            ("pin", "Hefei Hi-tech Zone", ADDRESS_EN),
        ]
    )
    icons = {
        "bolt": '<path d="M13 2 4.8 13.2h6.1L10 22l8.2-11.2h-6.1L13 2Z"/>',
        "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3.5 2"/>',
        "pin": '<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.4"/>',
    }
    cards = []
    for icon_name, title, desc in items:
        icon = (
            '<span class="contact-promise-icon" aria-hidden="true">'
            f'<svg viewBox="0 0 24 24">{icons[icon_name]}</svg></span>'
        )
        cards.append(
            f'<div class="contact-promise">{icon}<h3>{title}</h3><p>{desc}</p></div>'
        )
    return f'<div class="contact-promises">{"".join(cards)}</div>'


BEIAN_ICP = "皖ICP备2021010166号"
BEIAN_GA = "皖公网安备34019202001633号"
BEIAN_GA_URL = "http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=34019202001633"
EMAIL = "guanwn@kdgc.cc"
PHONE = "15385884309"
PHONE_DISPLAY = "153-8588-4309"
ADDRESS = "安徽省合肥市高新区望江西路5089号嵌入式研发楼103-C3（科大先研院-智源楼）"
ADDRESS_EN = "Room 103-C3, Embedded R&D Building, No. 5089 Wangjiang West Road, High-tech District, Hefei, Anhui, China"
HOURS = "客服工作时间：09:00–21:00（7×24 响应）"
HOURS_EN = "Support hours: 09:00–21:00 (7×24 response)"

SERVICE_WIDGET_ZH = """<div class="service-rail" aria-label="在线服务">
<button id="chat-open" class="service-rail-btn service-rail-primary" type="button" aria-label="在线客服">
<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 17.5 3.5 21l4.4-1.7c1.2.5 2.6.7 4.1.7 5 0 9-3.6 9-8s-4-8-9-8-9 3.6-9 8c0 2.1.8 4 2 5.5Z"/><path d="M8 12h.01M12 12h.01M16 12h.01"/></svg>
<span>在线客服</span></button>
<button id="wechat-open" class="service-rail-btn" type="button" aria-label="企业微信">
<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8.5 5C4.9 5 2 7.4 2 10.4c0 1.7.9 3.2 2.4 4.2L3.8 17l2.8-1.2c.6.1 1.2.2 1.9.2 3.6 0 6.5-2.4 6.5-5.6S12.1 5 8.5 5Z"/><path d="M14.5 9c4.1 0 7.5 2.7 7.5 6 0 1.8-1 3.4-2.7 4.5l.7 2.5-3.1-1.3c-.8.2-1.6.3-2.4.3-3.5 0-6.4-1.9-7.2-4.5"/></svg>
<span>企业微信</span></button>
</div>
<section id="chat-panel" class="support-panel" aria-hidden="true">
<header><div><strong>中科国瓷在线客服</strong><small>工程师在线 · 通常很快回复</small></div><button class="support-close" type="button" aria-label="关闭">×</button></header>
<div id="chat-messages" class="support-messages"><div class="support-bubble agent">您好，请问您想咨询产品选型、规格参数还是样品申请？</div></div>
<div class="support-contact"><input id="chat-name" maxlength="60" placeholder="称呼（选填）"><input id="chat-phone" maxlength="30" placeholder="手机/邮箱（选填）"></div>
<div class="support-compose"><textarea id="chat-input" maxlength="1000" rows="2" placeholder="请输入您的问题…"></textarea><button id="chat-send" type="button">发送</button></div>
<p id="chat-state" class="support-state">消息将由客服后台接收</p>
</section>
<section id="wechat-panel" class="wechat-panel" aria-hidden="true">
<button class="support-close" type="button" aria-label="关闭">×</button>
<div class="wechat-placeholder"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM15 14h2v2h-2zM18 14h2v5h-2zM14 18h3v2h-3z"/></svg></div>
<strong>企业微信</strong><p>二维码即将上线<br>您也可以先使用在线客服沟通</p>
</section>"""

SERVICE_WIDGET_EN = SERVICE_WIDGET_ZH.replace("在线服务", "Online service").replace("在线客服", "Online support").replace("企业微信", "WeCom").replace("中科国瓷Online support", "ZK Guoci Support").replace("工程师在线 · 通常很快回复", "Engineer support · Fast response").replace("您好，请问您想咨询产品选型、规格参数还是样品申请？", "Hello. How can we help with product selection, specifications, or samples?").replace("称呼（选填）", "Name (optional)").replace("手机/邮箱（选填）", "Phone/email (optional)").replace("请输入您的问题…", "Type your question…").replace("发送", "Send").replace("消息将由客服后台接收", "Your message will be received by our support team").replace("二维码即将上线<br>您也可以先使用Online support沟通", "QR code coming soon<br>Please use online support for now").replace("关闭", "Close")

FOOTER = f"""<footer><div class="footer-grid container" style="padding:0">
<div><h4>中科国瓷</h4><p style="font-size:14px;margin-top:8px">变频氧传感器与氮氧传感技术 · 中科大技术转化</p>
<p style="font-size:13px;margin-top:8px;opacity:.8">恪守诚信为本，产品承诺质保 5 年</p></div>
<div><h4>产品中心</h4>
<a href="/products/kd0100-02s-t1.html">KD0100-02S-T1 探头</a>
<a href="/products/kd0100-02s-to.html">KD0100-02S-TO 插针</a>
<a href="/products/mask-o2-sensor.html">面罩用氧传感器</a></div>
<div><h4>网站栏目</h4><a href="/news/">新闻资讯</a><a href="/knowledge/">知识库</a><a href="/cases/">行业案例</a><a href="/about/">关于中科国瓷</a></div>
<div><h4><a href="/contact/" style="color:inherit;font-size:inherit;font-weight:inherit;display:inline;margin:0">联系我们</a></h4><a href="mailto:{EMAIL}">{EMAIL}</a>
<a href="tel:{PHONE}">{PHONE_DISPLAY}</a>
<p style="font-size:13px;margin-top:8px">{ADDRESS}</p></div>
</div>
<div class="footer-bottom"><div class="footer-meta">
<span>© 2026 安徽中科国瓷新型元器件有限公司</span><span class="sep">·</span>
<a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">{BEIAN_ICP}</a><span class="sep">·</span>
<a href="{BEIAN_GA_URL}" target="_blank" rel="noopener"><img src="/assets/images/ga_icon.png" alt="" width="14" height="14">{BEIAN_GA}</a><span class="sep">·</span>
<a href="/en/">English</a><span class="sep">|</span><a href="/">中文</a><span class="sep">·</span><a href="/privacy.html">隐私政策</a>
</div></div></footer>
{SERVICE_WIDGET_ZH}
<script src="/assets/js/main.js"></script>"""

NAV = """<nav class="nav"><div class="nav-inner">
<a href="/" class="nav-logo nav-wordmark" aria-label="中科国瓷">
<span class="wordmark-cn">中科国瓷</span><span class="wordmark-divider"></span><span class="wordmark-en">KDGC<small>OXYGEN SENSING</small></span>
</a>
<div class="nav-links">
<a href="/">首页</a>
<a href="/products/">产品中心</a>
<a href="/news/">新闻资讯</a>
<a href="/knowledge/">知识库</a>
<a href="/cases/">行业案例</a>
<a href="/about/">关于中科国瓷</a>
<a href="/en/" style="opacity:.8">EN</a>
<a href="/contact/" class="nav-cta">联系我们</a>
</div>
<button class="menu-toggle" aria-label="菜单">☰</button>
</div></nav>"""

NAV_EN = """<nav class="nav"><div class="nav-inner">
<a href="/en/" class="nav-logo nav-wordmark" aria-label="KDGC">
<span class="wordmark-en wordmark-en-main">KDGC<small>OXYGEN SENSING</small></span><span class="wordmark-divider"></span><span class="wordmark-cn wordmark-cn-small">中科国瓷</span>
</a>
<div class="nav-links">
<a href="/en/">Home</a>
<a href="/en/products.html">Products</a>
<a href="/en/news.html">News</a>
<a href="/en/knowledge.html">Knowledge</a>
<a href="/en/cases.html">Industry Cases</a>
<a href="/en/about.html">About</a>
<a href="/" style="opacity:.8">中文</a>
<a href="/en/contact.html" class="nav-cta">Contact</a>
</div>
<button class="menu-toggle" aria-label="Menu">☰</button>
</div></nav>"""

FOOTER_EN = f"""<footer><div class="footer-grid container" style="padding:0">
<div><h4>ZK Guoci</h4><p style="font-size:14px;margin-top:8px">Variable-frequency oxygen sensors · USTC tech transfer</p>
<p style="font-size:13px;margin-top:8px;opacity:.8">Integrity first · 5-year product warranty</p></div>
<div><h4>Product Center</h4>
<a href="/en/products/kd0100-02s-t1.html">KD0100-02S-T1 Probe</a>
<a href="/en/products/kd0100-02s-to.html">KD0100-02S-TO Pin</a>
<a href="/en/products/mask-o2-sensor.html">Mask O₂ Sensor</a></div>
<div><h4>Site Sections</h4>
<a href="/en/news.html">News</a>
<a href="/en/knowledge.html">Knowledge</a>
<a href="/en/cases.html">Industry Cases</a>
<a href="/en/about.html">About</a></div>
<div><h4><a href="/en/contact.html" style="color:inherit;font-size:inherit;font-weight:inherit;display:inline;margin:0">Contact Us</a></h4><a href="mailto:{EMAIL}">{EMAIL}</a>
<a href="tel:{PHONE}">{PHONE_DISPLAY}</a>
<p style="font-size:13px;margin-top:8px">{ADDRESS_EN}</p></div>
</div>
<div class="footer-bottom"><div class="footer-meta">
<span>© 2026 Anhui ZK Guoci New Components Co., Ltd.</span><span class="sep">·</span>
<a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">{BEIAN_ICP}</a><span class="sep">·</span>
<a href="{BEIAN_GA_URL}" target="_blank" rel="noopener"><img src="/assets/images/ga_icon.png" alt="" width="14" height="14">{BEIAN_GA}</a><span class="sep">·</span>
<a href="/en/">English</a><span class="sep">|</span><a href="/">中文</a><span class="sep">·</span><a href="/privacy.html">Privacy</a>
</div></div></footer>
{SERVICE_WIDGET_EN}
<script src="/assets/js/main.js"></script>"""


ORG_SCHEMA = """{
  "@context":"https://schema.org",
  "@type":"Organization",
  "@id":"https://kdgc.cc/#org",
  "name":"安徽中科国瓷新型元器件有限公司",
  "alternateName":["中科国瓷","KDGC","ZK Guoci"],
  "url":"https://kdgc.cc/",
  "logo":"https://kdgc.cc/assets/images/logo.png",
  "contactPoint":{"@type":"ContactPoint","telephone":"+86-15385884309","contactType":"sales","email":"guanwn@kdgc.cc","availableLanguage":["Chinese","English"]},
  "address":{"@type":"PostalAddress","streetAddress":"望江西路5089号嵌入式研发楼103-C3","addressLocality":"合肥市","addressRegion":"安徽省","postalCode":"230088","addressCountry":"CN"},
  "sameAs":["https://kdgc.cc/en/"]
}"""

def product_schema(p, slug):
    return f"""{{
  "@context":"https://schema.org",
  "@type":"Product",
  "name":"{p['name']}",
  "description":"{p['summary']}",
  "url":"https://kdgc.cc/products/{slug}.html",
  "image":"https://kdgc.cc/assets/images/products/{slug}.png",
  "brand":{{"@type":"Brand","name":"中科国瓷"}},
  "manufacturer":{{"@id":"https://kdgc.cc/#org"}},
  "offers":{{"@type":"Offer","availability":"https://schema.org/InStock","url":"https://kdgc.cc/contact/"}}
}}"""

def breadcrumb_schema(items):
    elements = ",".join(
        f'{{"@type":"ListItem","position":{i+1},"name":"{name}","item":"https://kdgc.cc{url}"}}'
        for i,(name,url) in enumerate(items)
    )
    return f'{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{elements}]}}'

def page(title, desc, body, canonical="", lang="zh", schema_extra=""):
    nav = NAV if lang == "zh" else NAV_EN
    footer = FOOTER if lang == "zh" else FOOTER_EN
    lang_attr = "zh-CN" if lang == "zh" else "en"
    canon = f'<link rel="canonical" href="https://kdgc.cc{canonical}">' if canonical else ""
    schemas = [ORG_SCHEMA]
    if schema_extra:
        schemas.append(schema_extra)
    schema_tags = "\n".join(
        f'<script type="application/ld+json">{s}</script>' for s in schemas
    )
    return f"""<!DOCTYPE html>
<html lang="{lang_attr}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
{canon}<link rel="stylesheet" href="/assets/css/style.css">
<link rel="icon" href="/assets/images/favicon.ico?v=20260720e">
{schema_tags}
</head><body>{nav}<main>{body}</main>{footer}</body></html>"""


PRODUCTS = [
    {
        "slug": "kd0100-02s-t1",
        "name": "KD0100-02S-T1 氧气传感器-探头",
        "name_en": "KD0100-02S-T1 Oxygen Sensor — Probe",
        "tagline": "氧压范围 0.5–101 kPa · 线束探头型",
        "tagline_en": "O₂ partial pressure 0.5–101 kPa · Cable probe type",
        "summary": "氧压范围 0.5kPa–101kPa，与外部接口板配合工作，可测试空气、纯氧及氮氧混合气等气体的氧分压。",
        "summary_en": "Measures oxygen partial pressure from 0.5–101 kPa. Works with an external interface board / KD0100-03 controller for air, pure oxygen, and N₂/O₂ mixtures.",
        "image": "products/kd0100-02s-t1.png",
        "advantages": [
            "氧压范围：0.5kPa–101kPa",
            "与外部接口板 / 配套控制器 KD0100-03 配合工作",
            "可测试空气、纯氧及氮氧混合气等气体的氧分压",
            "线束探头结构，便于系统集成",
        ],
        "advantages_en": [
            "O₂ partial pressure range: 0.5–101 kPa",
            "Works with external interface board / KD0100-03 controller",
            "Measures air, pure O₂, and N₂/O₂ mixed gases",
            "Cable-harness probe design for easy system integration",
        ],
        "specs": [
            ("传感器型号", "KD0100-02S"),
            ("配套控制器", "KD0100-03"),
            ("加热电压", "~4.5V / 9V（可选）"),
            ("允许气体温度", "（-50 ~ 200）℃"),
            ("气流速率", "（0 ~ 10）m/s"),
            ("探头重量", "≦35g（不包括线束）"),
        ],
        "specs_en": [
            ("Sensor model", "KD0100-02S"),
            ("Controller", "KD0100-03"),
            ("Heater voltage", "~4.5V / 9V (optional)"),
            ("Gas temperature", "(-50 ~ 200) °C"),
            ("Gas flow rate", "(0 ~ 10) m/s"),
            ("Probe weight", "≦35 g (excl. harness)"),
        ],
        "wiring": [
            ("Vh-", "白线"),
            ("Vh+", "蓝线"),
            ("Sense", "红线"),
            ("Common", "灰线"),
            ("Pump", "绿线"),
        ],
        "wiring_en": [
            ("Vh-", "White"),
            ("Vh+", "Blue"),
            ("Sense", "Red"),
            ("Common", "Gray"),
            ("Pump", "Green"),
        ],
        "accuracy": [
            ("氧分压 1～10 kPa", "≤±0.5 kPa"),
            ("氧分压 10～30 kPa", "≤±1 kPa"),
            ("氧分压 30～50 kPa", "≤±1.5 kPa"),
            ("氧分压 50～70 kPa", "≤±2 kPa"),
            ("氧分压 70～100 kPa", "≤±2.5 kPa"),
        ],
        "accuracy_en": [
            ("1–10 kPa", "≤±0.5 kPa"),
            ("10–30 kPa", "≤±1 kPa"),
            ("30–50 kPa", "≤±1.5 kPa"),
            ("50–70 kPa", "≤±2 kPa"),
            ("70–100 kPa", "≤±2.5 kPa"),
        ],
        "notes": [
            "工作时传感器探头温度较高，注意防范误触探头导致烫伤",
            "须按控制器说明书进行操作使用，否则可能会造成传感器永久损坏失效",
        ],
        "notes_en": [
            "Probe tip is hot during operation — avoid burns from accidental contact",
            "Operate only per the controller manual; misuse may permanently damage the sensor",
        ],
    },
    {
        "slug": "kd0100-02s-to",
        "name": "KD0100-02S-TO 氧气传感器-插针",
        "name_en": "KD0100-02S-TO Oxygen Sensor — Pin Header",
        "tagline": "氧压范围 0.5–101 kPa · 插针型 · ≦5g",
        "tagline_en": "O₂ partial pressure 0.5–101 kPa · Pin type · ≦5 g",
        "summary": "氧压范围 0.5kPa–101kPa，插针电气连接，探头重量 ≦5g，与配套控制器 KD0100-03 配合工作。",
        "summary_en": "Pin-header electrical connection, probe weight ≦5 g, O₂ range 0.5–101 kPa, paired with KD0100-03 controller.",
        "image": "products/kd0100-02s-to.png",
        "advantages": [
            "氧压范围：0.5kPa–101kPa",
            "轻量化插针结构，探头重量 ≦5g",
            "可测试空气、纯氧及氮氧混合气等气体的氧分压",
            "尺寸公差 ≦0.5mm（单位 mm）",
        ],
        "advantages_en": [
            "O₂ partial pressure range: 0.5–101 kPa",
            "Lightweight pin design, probe ≦5 g",
            "Measures air, pure O₂, and N₂/O₂ mixed gases",
            "Dimensional tolerance ≦0.5 mm",
        ],
        "specs": [
            ("传感器型号", "KD0100-02S"),
            ("配套控制器", "KD0100-03"),
            ("加热电压", "~4.5V / 9V（可选）"),
            ("允许气体温度", "（-50 ~ 200）℃"),
            ("气流速率", "（0 ~ 10）m/s"),
            ("探头重量", "≦5g（不包括线束）"),
        ],
        "specs_en": [
            ("Sensor model", "KD0100-02S"),
            ("Controller", "KD0100-03"),
            ("Heater voltage", "~4.5V / 9V (optional)"),
            ("Gas temperature", "(-50 ~ 200) °C"),
            ("Gas flow rate", "(0 ~ 10) m/s"),
            ("Probe weight", "≦5 g (excl. harness)"),
        ],
        "wiring": [
            ("1", "Pump"),
            ("2", "Common"),
            ("3", "Sense"),
            ("7", "Vh-"),
            ("9", "Vh+"),
            ("其余", "NC，无连接"),
        ],
        "wiring_en": [
            ("1", "Pump"),
            ("2", "Common"),
            ("3", "Sense"),
            ("7", "Vh-"),
            ("9", "Vh+"),
            ("Others", "NC"),
        ],
        "accuracy": [
            ("氧分压 1～10 kPa", "≤±0.5 kPa"),
            ("氧分压 10～30 kPa", "≤±1 kPa"),
            ("氧分压 30～50 kPa", "≤±1.5 kPa"),
            ("氧分压 50～70 kPa", "≤±2 kPa"),
            ("氧分压 70～100 kPa", "≤±2.5 kPa"),
        ],
        "accuracy_en": [
            ("1–10 kPa", "≤±0.5 kPa"),
            ("10–30 kPa", "≤±1 kPa"),
            ("30–50 kPa", "≤±1.5 kPa"),
            ("50–70 kPa", "≤±2 kPa"),
            ("70–100 kPa", "≤±2.5 kPa"),
        ],
        "notes": [
            "工作时传感器探头温度较高，注意防范误触探头导致烫伤",
            "须按控制器说明书进行操作使用，否则可能会造成传感器永久损坏失效",
            "注：所有单位均为 mm，尺寸公差 ≦0.5mm",
        ],
        "notes_en": [
            "Probe tip is hot during operation — avoid burns",
            "Operate only per the controller manual",
            "All dimensions in mm; tolerance ≦0.5 mm",
        ],
    },
    {
        "slug": "mask-o2-sensor",
        "name": "面罩用氧传感器",
        "name_en": "Mask Oxygen Sensor",
        "tagline": "战机飞行员面罩用低温型变频式氧传感器",
        "tagline_en": "Low-temperature VF oxygen sensor for pilot oxygen masks",
        "summary": "公司开发的战机飞行员面罩用低温型变频式氧传感器已试制成功，产品各项性能指标优异。",
        "summary_en": "A low-temperature variable-frequency oxygen sensor for fighter-pilot oxygen masks has been successfully prototyped with excellent performance metrics.",
        "image": "products/mask-o2-sensor.png",
        "advantages": [
            "面向航空面罩应用的低温型变频式氧传感器",
            "氧分压测量范围 0.5 ~ 101 kPa",
            "响应时间 t90 ＜15 s，启动时间 65 s",
            "封装外壳温度 ＜60℃",
        ],
        "advantages_en": [
            "Low-temperature VF oxygen sensor for aviation masks",
            "O₂ partial pressure range 0.5–101 kPa",
            "Response time t90 <15 s; warm-up 65 s",
            "Package shell temperature <60 °C",
        ],
        "specs": [
            ("氧分压测量范围", "0.5 ~ 101 kPa"),
            ("工作电压", "3~4V / ≤1A"),
            ("工作温度", "-40 ~ +125 ℃"),
            ("允许气体温度", "-50 ~ +200 ℃"),
            ("启动时间", "65 s"),
            ("响应时间 (t90)", "＜15 s"),
            ("封装外壳温度", "＜60 ℃"),
        ],
        "specs_en": [
            ("O₂ range", "0.5 ~ 101 kPa"),
            ("Supply", "3–4 V / ≤1 A"),
            ("Operating temp.", "-40 ~ +125 °C"),
            ("Gas temperature", "-50 ~ +200 °C"),
            ("Warm-up time", "65 s"),
            ("Response t90", "<15 s"),
            ("Shell temperature", "<60 °C"),
        ],
        "wiring": [],
        "wiring_en": [],
        "accuracy": [
            ("1~10 kPa", "≤0.5 kPa"),
            ("10~30 kPa", "≤1 kPa"),
            ("30~70 kPa", "≤1.5 kPa"),
            ("70~101 kPa", "≤2 kPa"),
        ],
        "accuracy_en": [
            ("1–10 kPa", "≤0.5 kPa"),
            ("10–30 kPa", "≤1 kPa"),
            ("30–70 kPa", "≤1.5 kPa"),
            ("70–101 kPa", "≤2 kPa"),
        ],
        "notes": [],
        "notes_en": [],
    },
]

NEWS = [
    {
        "slug": "team-building-2022",
        "date": "2022-01-16",
        "cover": "news/team-building-2022.jpg",
        "title": "2022年1月国瓷团建户外活动！新年新气象！虎年虎虎生威！",
        "title_en": "ZK Guoci 2022 Outdoor Team Building — New Year, New Energy",
        "summary": "新年伊始，国瓷公司进行周末全员户外团建，增强部门协作与凝聚力。",
        "summary_en": "At the start of 2022, ZK Guoci held a full-company outdoor team-building day to strengthen cross-team collaboration.",
        "body": """<p>2022年1月16日新年伊始，国瓷公司进行了一次周末全员户外团建活动。此次活动围绕着“敞开胸怀，接纳、认同、相信、团队，目标一致、实现自我。”为主题进行开展，目的是“增强部门与部门间、同事与同事间的沟通、交流与合作，增强公司的凝聚力，提高大家的积极性和效率。”通过活动的开展，让新员工迅速融入到了团队中，找到集体归属感，收到了良好的效果。</p>
<p>户外拓展第一项就是带大家一起体验骑马活动，温顺的马儿载着初体验的伙伴绕着马场观光，有的慢行散步体会马背上风光，有的伙伴追求策马扬鞭的感觉，通过管理员的现场教学，体验了一把歌词里的策马奔腾，潇潇洒洒。骑马活动也正式开始了热场，让大家已经进入到了活跃的状态。</p>
<p>体验完了骑马活动，接下来的一场拓展也正式拉开比赛的序幕——射箭比赛！这次比赛的赛制规则为：所有人分为两组：一组、二组，先行热身，让大家熟悉下靶场、箭弓，每个人都参与试射，找准位置和感觉，大家跃跃欲试，各组内队员每射中一次靶子都会带来一阵欢呼，射中箭靶的队员也被称为“种子选手”！当然比赛有惩罚，最后经过两组协商，输的队男生俯卧撑、女生深蹲作为惩罚！正式比赛开始！三局制，最后得分最高的队伍胜利。比赛中大家为每一次的中靶跳跃欢呼，为每一次的脱靶鼓舞打劲，加深了团队配合，懂得如何发挥团队最大的力量，互相鼓励、不气不馁。</p>
<p>在如火如荼的射箭比赛后，大家兴致高昂，意犹未尽，这时候正是进行刺激战场——CS射击战的时候。比赛同样分为两组，第一局对战为“斩首行动”，第二局要求必须团灭一组分输赢。这次CS的比赛大家都明白了团队的力量，确定了一个目标，既要有部署又要有冲劲，并且坚定不移的执行。</p>
<p>在一系列的比赛结束后，大家中午调整休息，美餐一顿，下午又开展了一系列团队活动：一起划竹筏船、一起开卡丁车。这两项活动都让团队认知到任何一件事都要脚踏实地去做，纸上谈兵只是空谈，只有实际去做去学习去感受才能走好后面的路。</p>
<p>团建尾声，大家将自己喜欢的活动又体验了一遍，最后以“摔碗酒”作为句号，带着美好的祝福开始新一年的辉煌。2022年国瓷在全体伙伴的努力下，全力以赴，共同进步，必将展开更加恢弘的篇章！最后国瓷祝大家新年快乐！虎年虎虎生威！！</p>""",
    },
    {
        "slug": "nox-sensor-market",
        "date": "2021-06-01",
        "cover": "news/nox-sensor-market.png",
        "title": "国内车用氮氧传感器市场超百亿元",
        "title_en": "China Automotive NOx Sensor Market Exceeds RMB 10 Billion",
        "summary": "气体传感器是机动车尾气后处理系统关键零部件，国Ⅵ排放标准下国内氮氧传感器市场空间超百亿元。",
        "summary_en": "Gas sensors are critical to vehicle aftertreatment. Under China VI, the domestic NOx sensor market is projected above RMB 10 billion.",
        "body": """<p>气体传感器作为汽车电子控制系统的信息源，是机动车尾气后处理系统中的关键零部件，决定了汽车排放物的控制水平。车用气体传感器的应用，为汽车尾气处理带来了新的变革，成为机动车节能减排的重要推手。</p>
<p>据了解，目前，我国每年需要近千万个氮氧传感器。柴油机所产生的微粒（PM）和氮氧化物（NOx）是排放中两种最主要的污染物。</p>
<p>当前针对 PM 及 NOx 排放控制的柴油机排放后处理技术有两种方法：</p>
<p>一种是通过废气再循环（EGR）技术降低发动机缸内燃烧的 NOx 排放，然后用柴油机颗粒捕集器（DPF）控制 PM。</p>
<p>另一种是通过燃油高压喷射技术降低发动机缸内燃烧的 PM 排放，然后用选择催化还原技术（SCR，喷射车用尿素液，以中和 NOx）控制 NOx。SCR 技术因为具有更高的燃油经济性和良好的耐硫性能，被认为是最有优势的技术路线，在欧洲已经得到了广泛的应用，而 SCR 技术中必然会用到氮氧传感器。</p>
<p>氮氧传感器是一种由固体电解质陶瓷及氮氧化物敏感电极材料，利用半导体技术制备的传感器，通过精密控制检测氮氧化物的电极表面的纳米复合结构，实现了极高的氮氧化物分子选择性。通过适当电极显微结构，提高了传感器对氮氧气体敏感性。</p>
<p>氮氧传感器由传感器探头和电控单元组成，二者之间通过一个线束连接，可测量尾气中氮氧化物的浓度、氧气的浓度。它可用于柴油发动机的 SCR 系统中实现氮氧化物的闭环控制，或汽油和柴油发动机的车载诊断（OBD）中。</p>
<p>传感器的探头，是将氧敏陶瓷材料制成的陶瓷芯片装配在金属外壳中。实际应用时，探头被安装在汽车的尾气管道中，陶瓷芯片会将尾气中的浓度值以电压的形式反馈到电控单元中。电控单元控制传感器探头的加热温度，并经过一系列信号调理，最后确定泵中氮氧化物浓度。电控单元通过 CAN 总线通讯，将测量气体的数值实时发送给汽车总控制中心（ECU），为 SCR 喷射量提供依据，以减少氮氧化物的排放。</p>
<p>市场分析认为，目前，在新车车用氮氧传感器市场领域，我国将至少需要 320 万个氮氧传感器。在旧车改造售后市场，将需要约 560 万个氮氧传感器，我国每年需要近千万个氮氧传感器。我国将实施国Ⅵ排放标准，届时每辆柴油车将安装 2 个氮氧传感器，我国年均将至少需要 1700 万个氮氧传感器，这将是一个超百亿元的国内市场。</p>""",
    },
    {
        "slug": "understand-o2-sensor",
        "date": "2021-05-01",
        "cover": "news/understand-o2-sensor.jpg",
        "title": "一文读懂氧传感器",
        "title_en": "Oxygen Sensors Explained",
        "summary": "从发动机故障灯到氧化锆/氧化钛氧传感器原理、结构、分类、检测与行业应用的完整科普。",
        "summary_en": "Full primer on zirconia/titania oxygen sensors — principles, types, diagnostics, and industry applications.",
        "body": (NEWS_CONTENT / "understand-o2-sensor.body.html").read_text(encoding="utf-8"),
    },
]

TEAM = [
    {
        "name": "陈初升",
        "role": "首席科学家",
        "items": [
            "中国科学技术大学教授，博士生导师",
            "长期从事无机非金属材料和固体化学的教学和研究工作",
            "历任中国科学技术大学化学与材料学院院长，中国科学技术大学副校长；亚洲固态离子学会理事，中国固态离子学会副理事长",
            "国家杰出青年基金获得者",
            "国务院特殊津贴",
        ],
    },
    {
        "name": "李超",
        "role": "总经理",
        "items": [
            "中国科学技术大学近代物理系本科、硕士",
            "曾任 MXIC 研发经理，Creative Technology 研发经理，清华公共安全研究院（泽众安全科技有限公司）副总经理",
        ],
    },
    {
        "name": "李彤",
        "role": "总工程师",
        "items": [
            "中国科学技术大学计算机系本科、博士，高级工程师",
            "曾任中国电科 38 所某重大航天项目副总设计师，长期从事军工产品研制和项目管理工作",
        ],
    },
]

HONORS = [
    {"title": "2022年度合肥高新区深科技企业", "img": "honors/deep-tech-2022.png", "desc": "合肥高新技术产业开发区管理委员会 · 2022年12月"},
    {"title": "第十一届中国创新创业大赛安徽赛区合肥市赛三等奖", "img": "honors/innovation-2022.png", "desc": "初创企业组 · 合肥市科学技术局 · 2022年8月"},
    {"title": "ISO 9001:2015 质量管理体系认证", "img": "honors/iso9001.png", "desc": "证书号 50322Q4558R0S · 覆盖氮氧传感器研发和生产"},
    {"title": "发明专利：变频氧传感器", "img": "honors/patent-grant.png", "desc": "申请号 202110555297.8 · 国家知识产权局授予发明专利权通知书"},
    {"title": "专利权人变更为中科国瓷", "img": "honors/patent-transfer.png", "desc": "变频氧传感器专利由中科大先进技术研究院变更为本公司"},
]

PARTNERS = [
    {"name": "汇智新材料", "img": "partners/huizhi.png"},
    {"name": "AMPRON", "img": "partners/ampron.png"},
]


def product_detail_html(p):
    specs_rows = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in p["specs"])
    acc_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in p["accuracy"])
    wiring = ""
    if p["wiring"]:
        wiring = "<h3>电气连接</h3><table><tr><th>端口</th><th>说明</th></tr>" + "".join(
            f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in p["wiring"]
        ) + "</table>"
    notes = ""
    if p["notes"]:
        notes = "<h3>注意事项</h3><ul>" + "".join(f"<li>{n}</li>" for n in p["notes"]) + "</ul>"
    adv = "".join(f"<li>{a}</li>" for a in p["advantages"])
    img = asset_url(p["image"])
    # Download button (PDF placeholder — engineers can replace with real file)
    download_btn = (
        f'<a href="/contact/?product={p["slug"]}&req=spec" class="btn btn-ghost" '
        f'style="margin-left:8px;border-color:var(--blue);color:var(--blue)">'
        f'📄 要规格书</a>'
    )
    extras = []
    if has_asset("products/exploded.png") or has_asset("products/exploded.webp"):
        extras.append(
            f'<figure class="product-extra"><img src="{asset_url("products/exploded.png")}" alt="结构示意" loading="lazy">'
            f"<figcaption>结构示意</figcaption></figure>"
        )
    if has_asset("products/controller-kd0100-03.png") or has_asset("products/controller-kd0100-03.webp"):
        extras.append(
            f'<figure class="product-extra"><img src="{asset_url("products/controller-kd0100-03.png")}" alt="配套控制器 KD0100-03" loading="lazy">'
            f"<figcaption>配套控制器 KD0100-03</figcaption></figure>"
        )
    extras_html = (
        f'<div class="product-extras">{"".join(extras)}</div>' if extras else ""
    )
    return f"""{page_hero(p["name"], p["tagline"], "products/banner.jpg")}
<section><div class="container" style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start">
<div><img src="{img}" alt="{p['name']}" class="product-hero-img" loading="lazy">{extras_html}</div>
<div class="content-block" style="margin:0">
<p>{p['summary']}</p>
<h3>产品优势</h3><ul>{adv}</ul>
<p style="margin-top:20px"><a href="/contact/?product={p['slug']}" class="btn btn-primary">工程师咨询</a>
{download_btn}
<a href="/products/" class="btn btn-ghost" style="margin-left:8px;color:var(--navy);border-color:var(--border)">返回产品中心</a></p>
</div></div>
<div class="container" style="margin-top:32px">
<div class="content-block"><h2>规格参数</h2>
<p style="font-size:13px;color:var(--muted);margin-bottom:12px">如需完整规格书（PDF），请<a href="/contact/?product={p['slug']}&req=spec" style="color:var(--blue)">联系我们</a>索取。</p>
<table>{specs_rows}</table>
{wiring}
<h3 style="margin-top:24px">测量精度（标准大气条件下）</h3>
<table><tr><th>氧分压范围</th><th>精度</th></tr>{acc_rows}</table>
{notes}
</div></div></section>
<style>@media(max-width:800px){{section .container[style*="grid-template"]{{display:block!important}}}}</style>"""



def knowledge_related_html(slugs):
    links = []
    for s in slugs:
        links.append(f'<a href="/products/{s}.html" class="tag">{product_name(s)}</a>')
    return " ".join(links)


def baidu_map_html(lang="zh"):
    # Baidu URI API marker page — no AK required for basic marker view
    from urllib.parse import quote

    title = MAP_TITLE if lang == "zh" else "ZK Guoci"
    addr = MAP_ADDRESS if lang == "zh" else ADDRESS_EN
    src = (
        f"https://api.map.baidu.com/marker?location={MAP_LAT},{MAP_LNG}"
        f"&title={quote(title)}&content={quote(addr)}&output=html&coord_type=bd09ll&src=webapp.kdgc.site"
    )
    label = "打开百度地图导航" if lang == "zh" else "Open in Baidu Maps"
    coords = f"{MAP_LNG}, {MAP_LAT}"
    return f'''<div class="map-block">
<iframe class="baidu-map" title="Baidu Map" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
src="{src}"></iframe>
<div class="map-meta"><span>坐标（BD-09）：{coords}</span>
<a href="{src}" target="_blank" rel="noopener">{label}</a></div>
</div>'''


def main():
    pages = {}

    # Homepage
    prod_cards = "".join(
        f"""<a href="/products/{p['slug']}.html" class="card">
<img src="{asset_url(p['image'])}" alt="{p['name']}" class="card-img card-img--product" loading="lazy">
<div class="card-body"><h3>{p['name']}</h3><p>{p['tagline']}</p>
<span class="tag">氧传感器</span></div></a>"""
        for p in PRODUCTS
    )
    news_cards = "".join(
        f"""<a href="/news/{n['slug']}.html" class="card news-card">
<img src="{asset_url(n['cover'])}" alt="{n['title']}" class="card-img" loading="lazy">
<div class="card-body">
<span class="tag">{n['date']}</span><h3>{n['title']}</h3><p>{n['summary']}</p></div></a>"""
        for n in NEWS
    )
    hero_bg = ""
    if has_asset("home/hero-oxygen-sensor.jpg") or has_asset("home/hero-oxygen-sensor.webp"):
        hero_bg = f'style="background-image:linear-gradient(100deg,rgba(7,20,38,.88) 0%,rgba(7,20,38,.55) 45%,rgba(7,20,38,.35) 100%),url(\'{asset_url("home/hero-oxygen-sensor.jpg")}\');background-size:cover;background-position:center right"'

    pages["index.html"] = page(
        "中科国瓷 — 变频氧传感器与氮氧传感技术",
        "安徽中科国瓷新型元器件有限公司，专注变频氧传感器、氮氧传感器研发与生产。中科大技术转化，科技感知未来。",
        f"""<section class="hero"><div class="hero-bg" {hero_bg}></div><div class="hero-content">
<div class="hero-badge">中科大技术转化 · 科技感知未来</div>
<h1>安徽中科国瓷<br><em>变频氧传感器</em>方案商</h1>
<p>氧压范围 0.5–101 kPa · 车用 / 航空面罩 / 工业气体检测 · 产品承诺质保 5 年</p>
<div class="hero-actions">
<a href="/products/" class="btn btn-primary">进入产品中心</a>
<a href="/contact/" class="btn btn-ghost">联系我们</a>
</div></div></section>
{"".join([
'<div class="trust-bar"><div class="container trust-items">',
*[
    (
        f'<span class="trust-item"><img src="{asset_url(ic)}" alt="" class="trust-icon" width="28" height="28" loading="lazy">'
        f"<span><strong>{label}</strong> {desc}</span></span>"
        if has_asset(ic)
        else f"<span><strong>{label}</strong> {desc}</span>"
    )
    for ic, label, desc in [
        ("home/icon-iso.png", "ISO 9001", "氮氧传感器研发生产"),
        ("home/icon-patent.png", "发明专利", "变频氧传感器"),
        ("home/icon-deeptech.png", "深科技企业", "合肥高新区 2022"),
        ("home/icon-warranty.png", "质保 5 年", "诚信为本"),
    ]
],
"</div></div>",
])}
<section><div class="container">
<div class="section-header"><div class="section-label">Products</div><h2>产品中心</h2><p>探头型、插针型与面罩用氧传感器，完整规格与详情</p></div>
<div class="grid-3">{prod_cards}</div>
</div></section>
<section class="values-teaser"><div class="container">
<div class="section-header"><div class="section-label">Values</div><h2>我们的价值观</h2>
<p>诚信 · 创新 · 响应 — 支撑长期合作</p></div>
<div class="values-cards values-cards--home">
<a class="values-card" href="/about/#values"><span class="values-num">01</span><h3>诚信至上</h3><p>产品承诺质保 5 年</p></a>
<a class="values-card" href="/about/#values"><span class="values-num">02</span><h3>坚持创新</h3><p>产学研合作持续迭代</p></a>
<a class="values-card" href="/about/#values"><span class="values-num">03</span><h3>快速响应</h3><p>7×24 小时全天候服务</p></a>
</div>
<p class="values-more"><a href="/about/#values">查看完整价值观 →</a></p>
</div></section>
<section style="background:var(--white)"><div class="container">
<div class="section-header"><div class="section-label">News</div><h2>新闻资讯</h2></div>
<div class="grid-3">{news_cards}</div>
</div></section>
<section style="background:var(--gray)"><div class="container">
<div class="section-header">
<div class="section-label">Selection Tool</div>
<h2>在线选型</h2>
<p>不确定选哪款？60 秒对比三款传感器核心差异</p>
</div>
<div class="values-cards" style="max-width:960px;margin:0 auto 24px">
<a class="values-card" href="/knowledge/oxygen-sensor-selection-guide.html">
<span class="values-num" style="color:var(--blue)">探头型 T1</span>
<h3>KD0100-02S-T1</h3>
<p>气管路插入 · 线束 · ≦35g · 工业首选</p>
</a>
<a class="values-card" href="/knowledge/oxygen-sensor-selection-guide.html">
<span class="values-num" style="color:var(--blue)">插针型 TO</span>
<h3>KD0100-02S-TO</h3>
<p>PCB 直插 · ≦5g · OEM 内嵌首选</p>
</a>
<a class="values-card" href="/knowledge/oxygen-sensor-selection-guide.html">
<span class="values-num" style="color:var(--blue)">面罩型</span>
<h3>面罩用氧传感器</h3>
<p>低温优化 · 航空/呼吸场景专用</p>
</a>
</div>
<p style="text-align:center;margin-top:8px">
<a href="/knowledge/oxygen-sensor-selection-guide.html" class="btn btn-primary" style="margin-right:12px">查看完整选型指南</a>
<a href="/contact/" class="btn btn-ghost" style="color:var(--navy);border-color:var(--navy)">咨询工程师</a>
</p>
</div></section>
<section class="cta-section"><div class="container">
<h2>获取氧传感器技术方案</h2>
<p style="margin-bottom:24px;opacity:.9">填写需求，技术团队将尽快与您联系</p>
<a href="/contact/" class="btn btn-white">立即咨询</a>
</div></section>""",
        "/",
        schema_extra=breadcrumb_schema([("首页", "/")]),
    )

    # Products index + details
    pages["products/index.html"] = page(
        "产品中心 — 中科国瓷",
        "KD0100 系列氧气传感器探头/插针、面罩用氧传感器",
        f"""{page_hero("产品中心", "KD0100 系列探头 / 插针 · 面罩用氧传感器", "products/banner.jpg")}
<section><div class="container grid-3">{prod_cards}</div></section>""",
        "/products/",
    )
    for p in PRODUCTS:
        pages[f"products/{p['slug']}.html"] = page(
            f"{p['name']} — 中科国瓷", p["summary"], product_detail_html(p), f"/products/{p['slug']}.html",
            schema_extra="\n".join([
                product_schema(p, p["slug"]),
                breadcrumb_schema([("首页","/"),("产品中心","/products/"),
                                   (p["name"], f"/products/{p['slug']}.html")]),
            ])
        )

    # About — 核心团队不放图片，仅展示姓名、职务与履历
    team_html = ""
    for t in TEAM:
        items = "".join(f"<li>{i}</li>" for i in t["items"])
        team_html += f"""<div class="content-block team-card"><div><h3>{t['name']} <span class="tag">{t['role']}</span></h3><ul>{items}</ul></div></div>"""
    honor_html = "".join(
        f"""<a href="{asset_url(h['img'])}" target="_blank" class="card">
<img src="{asset_url(h['img'])}" alt="{h['title']}" class="card-img" style="object-fit:contain;background:#f8fafc;padding:12px;height:240px" loading="lazy">
<div class="card-body"><h3 style="font-size:15px">{h['title']}</h3><p>{h['desc']}</p></div></a>"""
        for h in HONORS
    )
    partner_html = "".join(
        f"""<div class="content-block" style="text-align:center;padding:24px">
<img src="{asset_url(p['img'])}" alt="{p['name']}" style="max-height:80px;margin:0 auto 12px;object-fit:contain" loading="lazy">
<p>{p['name']}</p></div>"""
        for p in PARTNERS
    )
    lab_block = ""
    lab_imgs = []
    for key, alt in [("about/lab-1.jpg", "研发环境"), ("about/lab-2.jpg", "实验室")]:
        if has_asset(key):
            lab_imgs.append(
                f'<img src="{asset_url(key)}" alt="{alt}" class="about-lab-img" loading="lazy">'
            )
    if lab_imgs:
        lab_block = (
            '<h2 style="margin:40px 0 16px">研发环境</h2>'
            f'<div class="about-lab-grid">{"".join(lab_imgs)}</div>'
        )
    values_cards = """
<div class="values-cards">
<div class="values-card"><span class="values-num">01</span><h3>诚信至上</h3><p>产品承诺质保 5 年</p></div>
<div class="values-card"><span class="values-num">02</span><h3>坚持创新</h3><p>产学研合作持续迭代</p></div>
<div class="values-card"><span class="values-num">03</span><h3>快速响应</h3><p>7×24 小时全天候服务</p></div>
</div>"""
    values_poster = ""
    if has_asset("about/values-poster.jpg") or has_asset("about/values-poster.webp"):
        values_poster = f"""
<figure class="values-poster">
<a href="{asset_url("about/values-poster.jpg")}" target="_blank" rel="noopener" aria-label="Open values poster">
<img src="{asset_url("about/values-poster.jpg")}" alt="中科国瓷价值观：诚信至上、坚持创新、快速响应" loading="lazy">
</a>
<figcaption>精益求精 · 瓷就未来</figcaption>
</figure>"""
    values_block = f"""
<section id="values" class="values-section"><div class="container">
<div class="section-header">
<div class="section-label">Values</div>
<h2>我们的价值观</h2>
<p>以价值创造未来 · 以信任成就合作</p>
</div>
{values_cards}
{values_poster}
</div></section>"""

    pages["about/index.html"] = page(
        "关于中科国瓷 — 中科国瓷",
        "安徽中科国瓷新型元器件有限公司：价值观、核心团队、荣誉资质与合作伙伴。",
        f"""{page_hero("关于中科国瓷", "科技感知未来 · 中科大技术转化平台", "about/banner-about.jpg")}
<section><div class="container">
<div class="content-block">
<p>安徽中科国瓷新型元器件有限公司聚焦变频氧传感器、氮氧传感器的研发与生产，统一社会信用代码 91340100MA8LLE5K9H。公司地址位于中国（安徽）自由贸易试验区合肥市高新区望江西路 5089 号嵌入式研发楼 103-C3。</p>
<p>公司秉承以人为本、追求超越的经营理念；恪守诚信为本，产品承诺质保 5 年。通过坚持不懈地开拓创新、与时俱进，不断开创新局面、实现新跨越。</p>
</div>
</div></section>
{values_block}
<section><div class="container">
<h2 style="margin:0 0 16px">核心团队</h2>
{team_html}
{lab_block}
<h2 style="margin:40px 0 16px">荣誉资质</h2>
<div class="grid-3">{honor_html}</div>
<h2 style="margin:40px 0 16px">合作伙伴</h2>
<div class="grid-3">{partner_html}</div>
<p style="margin-top:24px;font-size:13px;color:var(--muted)">以上信息来自公司公开资料（团队、证书与合作伙伴）</p>
</div></section>""",
        "/about/",
    )

    # News
    news_list = "".join(
        f"""<a href="/news/{n['slug']}.html" class="news-list-item">
<img src="{asset_url(n['cover'])}" alt="{n['title']}" class="news-list-cover" loading="lazy">
<div class="news-list-body">
<span class="tag">{n['date']}</span>
<h3>{n['title']}</h3>
<p>{n['summary']}</p>
<span class="news-read-more">阅读全文 →</span>
</div></a>"""
        for n in NEWS
    )
    pages["news/index.html"] = page(
        "新闻资讯 — 中科国瓷",
        "中科国瓷新闻资讯：团建活动、氮氧传感器市场、氧传感器科普",
        f"""{page_hero("新闻资讯", "公司动态 · 行业观察 · 技术科普", "news/banner.jpg")}
<section><div class="container news-list">{news_list}</div></section>""",
        "/news/",
    )
    for n in NEWS:
        pages[f"news/{n['slug']}.html"] = page(
            f"{n['title']} — 中科国瓷",
            n["summary"],
            f"""<article class="article">
<section class="page-hero article-hero"><div class="container">
<p class="article-meta"><span class="tag">{n['date']}</span><span class="tag">新闻资讯</span></p>
<h1>{n['title']}</h1>
<p class="article-deck">{n['summary']}</p>
</div></section>
<section class="article-section"><div class="container article-layout">
<figure class="article-cover"><img src="{asset_url(n['cover'])}" alt="{n['title']}"></figure>
<div class="article-body content-block">{n['body']}
<p class="article-back"><a href="/news/">← 返回新闻列表</a>
<a href="/contact/" class="btn btn-primary" style="margin-left:12px">咨询选型</a></p>
</div></div></section>
</article>""",
            f"/news/{n['slug']}.html",
        )

    # Contact
    campus_html = ""
    if has_asset("contact/campus.jpg") or has_asset("contact/campus.webp"):
        campus_html = (
            f'<figure class="contact-campus"><img src="{asset_url("contact/campus.jpg")}" '
            f'alt="中科国瓷园区" loading="lazy"><figcaption>合肥高新区 · 望江西路园区</figcaption></figure>'
        )
    map_zh = baidu_map_html("zh")
    map_en = baidu_map_html("en")
    pages["contact/index.html"] = page(
        "联系我们 — 中科国瓷",
        f"联系中科国瓷：{PHONE_DISPLAY} {EMAIL} {ADDRESS}",
        f"""{page_hero("联系我们", "24 小时内回复承诺 · 技术工程师直通", "contact/banner.jpg")}
<div style="background:#eff6ff;border-bottom:2px solid var(--blue);padding:14px 24px;text-align:center;font-size:15px;font-weight:600;color:var(--blue)">
  ✅ 提交咨询后，我们承诺在 24 小时内由工程师回复您（工作日当天内优先响应）
</div>
<section class="contact-promises-section"><div class="container">{contact_promises_html("zh")}</div></section>
<section class="contact-main"><div class="container contact-layout">
<div class="contact-info">
<div class="content-block contact-card">
<h2>联系方式</h2>
<dl class="contact-dl">
<dt>邮箱</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
<dt>电话</dt><dd><a href="tel:{PHONE}">{PHONE_DISPLAY}</a></dd>
<dt>地址</dt><dd>{ADDRESS}</dd>
<dt>服务时间</dt><dd>{HOURS}</dd>
</dl>
</div>
{campus_html}
{map_zh}
</div>
<form id="lead-form" class="form-box contact-form">
<h2 style="margin:0 0 16px;font-size:20px;color:var(--navy)">提交咨询</h2>
<div class="form-hp"><input name="website" tabindex="-1" autocomplete="off"></div>
<div class="form-group"><label>公司名称 *</label><input name="company" required></div>
<div class="form-group"><label>联系人 *</label><input name="contact_name" required></div>
<div class="form-row">
<div class="form-group"><label>手机 *</label><input name="phone" type="tel" required></div>
<div class="form-group"><label>邮箱</label><input name="email" type="email"></div>
</div>
<div class="form-group"><label>产品兴趣</label><select name="product_interest">
<option value="">请选择</option>
<option>KD0100-02S-T1 探头</option>
<option>KD0100-02S-TO 插针</option>
<option>面罩用氧传感器</option>
<option>其他</option></select></div>
<div class="form-group"><label>需求描述</label><textarea name="requirement" rows="4"></textarea></div>
<button type="submit" class="btn btn-primary" style="width:100%">提交咨询</button>
<div class="form-msg"></div>
</form>
</div></section>""",
        "/contact/",
    )

    pages["en/contact.html"] = page(
        "Contact — ZK Guoci",
        f"Contact ZK Guoci: {PHONE_DISPLAY} {EMAIL} {ADDRESS_EN}",
        f"""{page_hero("Contact Us", "24-hour response commitment · Direct to engineers", "contact/banner.jpg")}
<div style="background:#eff6ff;border-bottom:2px solid var(--blue);padding:14px 24px;text-align:center;font-size:15px;font-weight:600;color:var(--blue)">
  ✅ We respond within 24 hours (same business day when possible)
</div>
<section class="contact-promises-section"><div class="container">{contact_promises_html("en")}</div></section>
<section class="contact-main"><div class="container contact-layout">
<div class="contact-info">
<div class="content-block contact-card">
<h2>Contact details</h2>
<dl class="contact-dl">
<dt>Email</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
<dt>Phone</dt><dd><a href="tel:{PHONE}">{PHONE_DISPLAY}</a></dd>
<dt>Address</dt><dd>{ADDRESS_EN}</dd>
<dt>Hours</dt><dd>{HOURS_EN}</dd>
</dl>
</div>
{campus_html}
{map_en}
</div>
<form id="lead-form" class="form-box contact-form">
<h2 style="margin:0 0 16px;font-size:20px;color:var(--navy)">Inquiry form</h2>
<div class="form-hp"><input name="website" tabindex="-1" autocomplete="off"></div>
<div class="form-group"><label>Company *</label><input name="company" required></div>
<div class="form-group"><label>Contact name *</label><input name="contact_name" required></div>
<div class="form-row">
<div class="form-group"><label>Phone *</label><input name="phone" type="tel" required></div>
<div class="form-group"><label>Email</label><input name="email" type="email"></div>
</div>
<div class="form-group"><label>Product interest</label><select name="product_interest">
<option value="">Please select</option>
<option>KD0100-02S-T1 Probe</option>
<option>KD0100-02S-TO Pin</option>
<option>Mask O₂ Sensor</option>
<option>Other</option></select></div>
<div class="form-group"><label>Requirements</label><textarea name="requirement" rows="4"></textarea></div>
<button type="submit" class="btn btn-primary" style="width:100%">Submit inquiry</button>
<div class="form-msg"></div>
</form>
</div></section>""",
        "/en/contact.html",
        lang="en",
    )

    # Knowledge library (formal articles)
    cats = []
    for k in KNOWLEDGE:
        if k["category"] not in cats:
            cats.append(k["category"])
    cat_nav = "".join(f'<a href="#cat-{c}" class="kb-cat">{c}</a>' for c in cats)
    kb_list = ""
    for c in cats:
        items = [k for k in KNOWLEDGE if k["category"] == c]
        cards = "".join(
            f"""<a href="/knowledge/{k['slug']}.html" class="kb-item">
<span class="tag">{k['category']}</span><span class="kb-date">{k['date']}</span>
<h3>{k['title']}</h3><p>{k['summary']}</p>
<span class="news-read-more">阅读全文 &rarr;</span></a>"""
            for k in items
        )
        kb_list += f'<div class="kb-group" id="cat-{c}"><h2 class="kb-group-title">{c}</h2><div class="kb-list">{cards}</div></div>'
    pages["knowledge/index.html"] = page(
        "知识库 — 中科国瓷",
        "变频氧传感器与氮氧传感知识库：原理、选型、应用与维护",
        f"""{page_hero("知识库", "严谨技术内容 · 对齐公开产品规格 · 服务选型决策", "news/banner.jpg")}
<section class="kb-section"><div class="container">
<p class="kb-lead">以下文章参数均对齐公司公开规格（氧分压 0.5–101 kPa、KD0100-03 配套等），不编造未公开指标。文末提供相关产品与咨询入口。</p>
<nav class="kb-cats">{cat_nav}</nav>
{kb_list}
</div></section>""",
        "/knowledge/",
    )
    for k in KNOWLEDGE:
        related = knowledge_related_html(k.get("related_products", []))
        cover_html = (
            f'<figure class="article-cover"><img src="{asset_url(k["cover"])}" alt="{k["title"]}"></figure>'
            if k.get("cover")
            else ""
        )
        pages[f"knowledge/{k['slug']}.html"] = page(
            f"{k['title']} — 中科国瓷",
            k["summary"],
            f"""<article class="article">
<section class="page-hero article-hero"><div class="container">
<p class="article-meta"><span class="tag">{k['category']}</span><span class="tag">{k['date']}</span></p>
<h1>{k['title']}</h1>
<p class="article-deck">{k['summary']}</p>
</div></section>
<section class="article-section"><div class="container article-layout">
{cover_html}
<div class="article-body content-block">{k['body']}
<div class="related-products"><h3>相关产品</h3><p>{related}</p></div>
<p class="article-back"><a href="/knowledge/">&larr; 返回知识库</a>
<a href="/contact/" class="btn btn-primary" style="margin-left:12px">咨询选型</a></p>
</div></div></section>
</article>""",
            f"/knowledge/{k['slug']}.html",
            schema_extra=breadcrumb_schema([
                ("首页","/"),("知识库","/knowledge/"),(k["title"],f"/knowledge/{k['slug']}.html")
            ]),
        )

    # Industry cases
    case_cards = "".join(
        f"""<a href="/cases/{c['slug']}.html" class="case-card">
<img src="{asset_url(c['cover'])}" alt="{c['title']}" class="case-cover" loading="lazy">
<div class="case-body">
<span class="tag">{c['industry']}</span>{'<span class="tag tag-wip">评估中</span>' if '进行中' in c['title'] or 'In Progress' in c.get('title_en', '') else ''}
<h3>{c['title']}</h3>
<p class="case-customer">{c['customer']}</p>
<p>{c['summary']}</p>
<ul class="case-metrics">{"".join(f"<li>{r}</li>" for r in c["results"][:2])}</ul>
<span class="news-read-more">查看案例 &rarr;</span>
</div></a>"""
        for c in INDUSTRY_CASES
    )
    pages["cases/index.html"] = page(
        "行业案例 — 中科国瓷",
        "中科国瓷行业案例：航空生命保障、工业气体监测、仪器 OEM、后处理评估（客户名脱敏）",
        f"""{page_hero("行业案例", "基于真实行业需求编写 · 客户名称均以代名词脱敏", "products/banner.jpg")}
<section class="cases-section"><div class="container">
<p class="kb-lead">案例结构包含挑战、方案、实施节点与可核对结果。涉及客户主体一律使用代名词；量化结论限于公开规格与可披露的项目口径。</p>
<div class="case-grid">{case_cards}</div>
</div></section>""",
        "/cases/",
    )
    for c in INDUSTRY_CASES:
        milestones = "".join(f"<li>{m}</li>" for m in c["milestones"])
        results = "".join(f"<li>{r}</li>" for r in c["results"])
        prod_links = " ".join(
            f'<a href="/products/{s}.html" class="tag">{product_name(s)}</a>' for s in c["product_slugs"]
        )
        pages[f"cases/{c['slug']}.html"] = page(
            f"{c['title']} — 中科国瓷",
            c["summary"],
            f"""<article class="article">
<section class="page-hero article-hero"><div class="container">
<p class="article-meta"><span class="tag">{c['industry']}</span><span class="tag">{c['date']}</span></p>
<h1>{c['title']}</h1>
<p class="article-deck">{c['customer']} · {c['summary']}</p>
</div></section>
<section class="article-section"><div class="container article-layout">
<figure class="article-cover"><img src="{asset_url(c['cover'])}" alt="{c['title']}"></figure>
<div class="article-body content-block">
<div class="case-panel"><h2>挑战</h2><p>{c['challenge']}</p></div>
<div class="case-panel"><h2>方案</h2><p>{c['solution']}</p></div>
<div class="case-panel"><h2>实施节点</h2><ol>{milestones}</ol></div>
<div class="case-panel"><h2>结果</h2><ul>{results}</ul></div>
<p class="article-note">{c['body_note']}</p>
<div class="related-products"><h3>相关产品</h3><p>{prod_links}</p></div>
<p class="article-back"><a href="/cases/">&larr; 返回行业案例</a>
<a href="/contact/" class="btn btn-primary" style="margin-left:12px">咨询同款方案</a></p>
</div></div></section>
</article>""",
            f"/cases/{c['slug']}.html",
            schema_extra=breadcrumb_schema([
                ("首页","/"),("行业案例","/cases/"),(c["title"],f"/cases/{c['slug']}.html")
            ]),
        )

    pages["privacy.html"] = page(
        "隐私政策 — 中科国瓷",
        "中科国瓷官网隐私政策：信息收集范围、使用目的、Cookie 说明、数据安全措施与用户权利。",
        f"""<section class="page-hero"><div class="container"><h1>隐私政策</h1><p>生效日期：2026 年 7 月 · 适用范围：kdgc.cc 及其子页面</p></div></section>
<section><div class="container" style="max-width:860px">
<div class="content-block">
<p>安徽中科国瓷新型元器件有限公司（下称「我们」）尊重并保护您的个人信息。本政策说明我们在您访问本网站（kdgc.cc）时如何收集、使用、存储和保护您的信息。使用本网站即表示您同意本政策。</p>

<h2>一、我们收集的信息</h2>
<h3>1. 您主动提供的信息</h3>
<ul>
<li><strong>咨询表单</strong>：公司名称、联系人姓名、手机号、邮箱、感兴趣的产品与需求描述；</li>
<li><strong>在线客服</strong>：您在会话中填写的称呼、联系方式，以及会话消息内容；</li>
<li><strong>邮件与电话</strong>：您通过 {EMAIL} 或 {PHONE_DISPLAY} 与我们沟通时提供的信息。</li>
</ul>
<h3>2. 自动收集的信息</h3>
<ul>
<li>访问日志：IP 地址、访问时间、浏览页面、浏览器类型与操作系统（用于安全防护与访问统计）；</li>
<li>本地存储：用于记住您的在线客服会话，避免刷新页面后会话丢失。</li>
</ul>

<h2>二、信息的使用目的</h2>
<ul>
<li>响应您的产品咨询、样品申请与规格书索取，并由工程师与您对接；</li>
<li>履行合同与售后服务（包括质保期内的技术支持）；</li>
<li>改进网站内容与用户体验（基于匿名化的访问统计）；</li>
<li>防范网络攻击、恶意提交与滥用行为（如提交频率限制）。</li>
</ul>

<h2>三、信息的共享与披露</h2>
<p>我们<strong>不会出售</strong>您的个人信息。仅在以下情形共享必要信息：</p>
<ul>
<li>经您明确同意；</li>
<li>为完成您的委托事项（如物流寄送样品）而向必要的合作方提供最小范围信息；</li>
<li>依据法律法规、监管要求或司法程序必须提供。</li>
</ul>

<h2>四、Cookie 与本地存储</h2>
<p>本网站不使用第三方广告 Cookie。我们使用浏览器本地存储（localStorage）保存您的客服会话标识，仅用于恢复会话连续性；您可随时通过浏览器设置清除。</p>

<h2>五、数据安全</h2>
<ul>
<li>网站数据传输采用 HTTPS 加密；</li>
<li>咨询与会话数据存储于境内服务器，访问受管理凭证控制；</li>
<li>对提交接口实施频率限制与反垃圾校验，防止恶意采集。</li>
</ul>

<h2>六、信息保存期限</h2>
<p>咨询与会话信息在达成商务目的所需期间内保存；法律法规另有规定的，按规定期限执行。超过期限后我们将删除或匿名化处理。</p>

<h2>七、您的权利</h2>
<p>您有权查询、更正或要求删除我们持有的您的个人信息，也可要求我们停止向您发送商务信息。请通过以下方式联系我们行使上述权利：</p>
<ul>
<li>邮箱：<a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li>电话：<a href="tel:{PHONE}">{PHONE_DISPLAY}</a></li>
<li>地址：{ADDRESS}</li>
</ul>
<p>我们将在收到请求后 15 个工作日内予以答复。</p>

<h2>八、未成年人保护</h2>
<p>本网站面向企业用户（B2B），不面向未成年人提供服务，也不会有意收集未成年人的个人信息。</p>

<h2>九、政策更新</h2>
<p>我们可能根据业务与法规变化更新本政策，更新后将在本页面发布并标注生效日期。重大变更时，我们会在网站显著位置提示。</p>

<p style="margin-top:28px"><a href="/contact/" class="btn btn-primary">有疑问？联系我们</a></p>
</div>
</div></section>""",
        "/privacy.html",
    )
    pages["404.html"] = page(
        "页面未找到 — 中科国瓷",
        "",
        """<section class="page-hero"><div class="container"><h1>404</h1><p>页面未找到</p>
<a href="/" class="btn btn-primary" style="margin-top:20px">返回首页</a></div></section>""",
        "",
    )

    # —— English site (full content) ——
    en_prod_cards = "".join(
        f"""<a href="/en/products/{p['slug']}.html" class="card">
<img src="{asset_url(p['image'])}" alt="{p['name_en']}" class="card-img card-img--product" loading="lazy">
<div class="card-body"><h3>{p['name_en']}</h3><p>{p['tagline_en']}</p>
<span class="tag">Oxygen sensor</span></div></a>"""
        for p in PRODUCTS
    )
    en_news_cards = "".join(
        f"""<a href="/news/{n['slug']}.html" class="card news-card">
<img src="{asset_url(n['cover'])}" alt="{n['title_en']}" class="card-img" loading="lazy">
<div class="card-body">
<span class="tag">{n['date']}</span><h3>{n['title_en']}</h3><p>{n['summary_en']}</p>
<p style="font-size:13px;color:var(--muted);margin:0">Full article in Chinese →</p></div></a>"""
        for n in NEWS
    )
    pages["en/index.html"] = page(
        "ZK Guoci — Variable-Frequency Oxygen Sensors",
        "Anhui ZK Guoci New Components Co., Ltd. — variable-frequency oxygen sensors and NOx sensing technology. USTC tech transfer.",
        f"""<section class="hero"><div class="hero-bg" {hero_bg}></div><div class="hero-content">
<div class="hero-badge">USTC Tech Transfer · Sensing the Future</div>
<h1>Anhui ZK Guoci<br><em>Variable-Frequency Oxygen Sensors</em></h1>
<p>0.5–101 kPa · Automotive / Aviation mask / Industrial gas · 5-year warranty</p>
<div class="hero-actions">
<a href="/en/products.html" class="btn btn-primary">Product Center</a>
<a href="/en/contact.html" class="btn btn-ghost">Contact Us</a>
</div></div></section>
{"".join([
'<div class="trust-bar"><div class="container trust-items">',
*[
    (
        f'<span class="trust-item"><img src="{asset_url(ic)}" alt="" class="trust-icon" width="28" height="28" loading="lazy">'
        f"<span><strong>{label}</strong> {desc}</span></span>"
        if has_asset(ic)
        else f"<span><strong>{label}</strong> {desc}</span>"
    )
    for ic, label, desc in [
        ("home/icon-iso.png", "ISO 9001", "NOx sensor R&amp;D &amp; production"),
        ("home/icon-patent.png", "Patent", "Variable-frequency O₂ sensor"),
        ("home/icon-deeptech.png", "Deep Tech", "Hefei High-tech Zone 2022"),
        ("home/icon-warranty.png", "5-year", "product warranty"),
    ]
],
"</div></div>",
])}
<section><div class="container">
<div class="section-header"><div class="section-label">Products</div><h2>Product Center</h2>
<p>Probe, pin, and mask oxygen sensors with full specifications</p></div>
<div class="grid-3">{en_prod_cards}</div>
</div></section>
<section style="background:var(--white)"><div class="container">
<div class="section-header"><div class="section-label">News</div><h2>News &amp; Insights</h2></div>
<div class="grid-3">{en_news_cards}</div>
</div></section>
<section class="cta-section"><div class="container">
<h2>Request an Oxygen Sensor Solution</h2>
<p style="margin-bottom:24px;opacity:.9">Tell us your range, interface, and application — our team will reply soon.</p>
<a href="/en/contact.html" class="btn btn-white">Contact</a>
</div></section>""",
        "/en/",
        lang="en",
    )

    pages["en/products.html"] = page(
        "Products — ZK Guoci",
        "KD0100 probe/pin oxygen sensors and aviation mask oxygen sensors",
        f"""{page_hero("Product Center", "KD0100 probe / pin series · Aviation mask oxygen sensors", "products/banner.jpg")}
<section><div class="container grid-3">{en_prod_cards}</div></section>""",
        "/en/products.html",
        lang="en",
    )

    for p in PRODUCTS:
        specs_rows = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in p["specs_en"])
        acc_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in p["accuracy_en"])
        wiring = ""
        if p["wiring_en"]:
            wiring = "<h3>Electrical connections</h3><table><tr><th>Pin</th><th>Signal</th></tr>" + "".join(
                f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in p["wiring_en"]
            ) + "</table>"
        notes = ""
        if p["notes_en"]:
            notes = "<h3>Notes</h3><ul>" + "".join(f"<li>{n}</li>" for n in p["notes_en"]) + "</ul>"
        adv = "".join(f"<li>{a}</li>" for a in p["advantages_en"])
        pages[f"en/products/{p['slug']}.html"] = page(
            f"{p['name_en']} — ZK Guoci",
            p["summary_en"],
            f"""{page_hero(p["name_en"], p["tagline_en"], "products/banner.jpg")}
<section><div class="container" style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start">
<div><img src="{asset_url(p['image'])}" alt="{p['name_en']}" class="product-hero-img" loading="lazy"></div>
<div class="content-block" style="margin:0">
<p>{p['summary_en']}</p>
<h3>Advantages</h3><ul>{adv}</ul>
<p style="margin-top:20px"><a href="/en/contact.html?product={p['slug']}" class="btn btn-primary">Inquire</a>
<a href="/en/products.html" class="btn btn-ghost" style="margin-left:8px;color:var(--navy);border-color:var(--border)">Back to products</a></p>
</div></div>
<div class="container" style="margin-top:32px">
<div class="content-block"><h2>Specifications</h2><table>{specs_rows}</table>
{wiring}
<h3 style="margin-top:24px">Accuracy (standard atmosphere)</h3>
<table><tr><th>O₂ partial pressure</th><th>Accuracy</th></tr>{acc_rows}</table>
{notes}
</div></div></section>
<style>@media(max-width:800px){{section .container[style*="grid-template"]{{display:block!important}}}}</style>""",
            f"/en/products/{p['slug']}.html",
            lang="en",
        )

    team_en = [
        ("Chen Chusheng", "Chief Scientist", [
            "Professor & PhD supervisor, University of Science and Technology of China (USTC)",
            "Long-term research in inorganic non-metallic materials and solid-state chemistry",
            "Former Dean of Chemistry & Materials, USTC; former Vice President of USTC; council roles in solid-state ionics societies",
            "Recipient of the National Science Fund for Distinguished Young Scholars",
            "Special Government Allowance of the State Council",
        ]),
        ("Li Chao", "General Manager", [
            "B.S. & M.S., Department of Modern Physics, USTC",
            "Former R&D Manager at MXIC and Creative Technology; former Deputy GM at Tsinghua Public Safety Research Institute (Zezhong Security Tech)",
        ]),
        ("Li Tong", "Chief Engineer", [
            "B.S. & PhD, Computer Science, USTC; Senior Engineer",
            "Former Deputy Chief Designer on a major aerospace program at CETC 38th Institute; long experience in defense product R&D and program management",
        ]),
    ]
    team_en_html = ""
    for name, role, items in team_en:
        team_en_html += f"""<div class="content-block team-card"><div><h3>{name} <span class="tag">{role}</span></h3>
<ul>{''.join(f'<li>{i}</li>' for i in items)}</ul></div></div>"""
    honor_en = "".join(
        f"""<a href="{asset_url(h['img'])}" target="_blank" class="card">
<img src="{asset_url(h['img'])}" alt="{h['title']}" class="card-img" style="object-fit:contain;background:#f8fafc;padding:12px;height:240px" loading="lazy">
<div class="card-body"><h3 style="font-size:15px">{h['title']}</h3><p>{h['desc']}</p></div></a>"""
        for h in HONORS
    )
    partner_en = "".join(
        f"""<div class="content-block" style="text-align:center;padding:24px">
<img src="{asset_url(p['img'])}" alt="{p['name']}" style="max-height:80px;margin:0 auto 12px;object-fit:contain" loading="lazy">
<p>{p['name']}</p></div>"""
        for p in PARTNERS
    )
    pages["en/about.html"] = page(
        "About ZK Guoci — Oxygen Sensors",
        "Anhui ZK Guoci leadership, certifications, partners, and contact.",
        f"""{page_hero("About ZK Guoci", "Sensing the future · USTC technology transfer", "about/banner-about.jpg")}
<section><div class="container">
<div class="content-block">
<p>Anhui ZK Guoci New Components Co., Ltd. focuses on R&amp;D and production of variable-frequency oxygen sensors and NOx-related sensing technologies. Unified Social Credit Code: 91340100MA8LLE5K9H.</p>
<p>Address: Room 103-C3, Embedded R&amp;D Building, No. 5089 Wangjiang West Road, High-tech District, Hefei, Anhui (China (Anhui) Pilot Free Trade Zone).</p>
<p>We pursue excellence with integrity and offer a <strong>5-year product warranty</strong>.</p>
</div>
</div></section>
<section id="values" class="values-section"><div class="container">
<div class="section-header"><div class="section-label">Values</div>
<h2>Our Values</h2>
<p>Create the future with value · Build partnership with trust</p></div>
<div class="values-cards">
<div class="values-card"><span class="values-num">01</span><h3>Integrity First</h3><p>5-year product warranty</p></div>
<div class="values-card"><span class="values-num">02</span><h3>Persistent Innovation</h3><p>Industry–university–research iteration</p></div>
<div class="values-card"><span class="values-num">03</span><h3>Rapid Response</h3><p>7×24 follow-up support</p></div>
</div>
{values_poster}
</div></section>
<section><div class="container">
<h2 style="margin:0 0 16px">Leadership</h2>
{team_en_html}
{lab_block}
<h2 style="margin:40px 0 16px">Honors &amp; Certifications</h2>
<div class="grid-3">{honor_en}</div>
<h2 style="margin:40px 0 16px">Partners</h2>
<div class="grid-3">{partner_en}</div>
<p style="margin-top:24px;font-size:13px;color:var(--muted)">Based on publicly available company information</p>
</div></section>""",
        "/en/about.html",
        lang="en",
    )

    pages["en/news.html"] = page(
        "News — ZK Guoci",
        "ZK Guoci news: team building, NOx sensor market, oxygen sensor primer",
        f"""{page_hero("News &amp; Insights", "Company updates · Industry notes · Technical primers", "news/banner.jpg")}
<section><div class="container news-list">{"".join(
            f"""<a href="/news/{n['slug']}.html" class="news-list-item">
<img src="{asset_url(n['cover'])}" alt="{n['title_en']}" class="news-list-cover" loading="lazy">
<div class="news-list-body">
<span class="tag">{n['date']}</span>
<h3>{n['title_en']}</h3>
<p>{n['summary_en']}</p>
<p style="font-size:13px;color:var(--muted);margin:8px 0 0">Chinese title: {n['title']}</p>
<span class="news-read-more">Read full article (Chinese) →</span>
</div></a>"""
            for n in NEWS
        )}</div></section>""",
        "/en/news.html",
        lang="en",
    )

    # EN knowledge + industry cases (abstracts + link to ZH)
    en_kb = "".join(
        f"""<a href="/knowledge/{k['slug']}.html" class="kb-item">
<span class="tag">{k['category_en']}</span><span class="kb-date">{k['date']}</span>
<h3>{k['title_en']}</h3><p>{k['summary_en']}</p>
<p style="font-size:13px;color:var(--muted);margin:8px 0 0">Chinese title: {k['title']}</p>
<span class="news-read-more">Read full article (Chinese) &rarr;</span></a>"""
        for k in KNOWLEDGE
    )
    pages["en/knowledge.html"] = page(
        "Knowledge Base — ZK Guoci",
        "Technical knowledge base for variable-frequency oxygen sensors: principles, selection, applications, maintenance",
        f"""{page_hero("Knowledge Base", "Rigorous articles aligned to published specs · Chinese full text", "news/banner.jpg")}
<section class="kb-section"><div class="container">
<p class="kb-lead">English pages provide abstracts. Full technical articles are maintained in Chinese to keep parameters consistent with product datasheets.</p>
<div class="kb-list">{en_kb}</div>
</div></section>""",
        "/en/knowledge.html",
        lang="en",
    )
    en_cases = "".join(
        f"""<a href="/cases/{c['slug']}.html" class="case-card">
<img src="{asset_url(c['cover'])}" alt="{c['title_en']}" class="case-cover" loading="lazy">
<div class="case-body">
<span class="tag">{c['industry_en']}</span>{'<span class="tag tag-wip">In progress</span>' if 'In Progress' in c.get('title_en', '') else ''}
<h3>{c['title_en']}</h3>
<p class="case-customer">{c['customer_en']}</p>
<p>{c['summary_en']}</p>
<span class="news-read-more">View case (Chinese) &rarr;</span>
</div></a>"""
        for c in INDUSTRY_CASES
    )
    pages["en/cases.html"] = page(
        "Industry Cases — ZK Guoci",
        "Industry cases with anonymized customers: aviation life support, industrial gas monitoring, OEM, aftertreatment evaluation",
        f"""{page_hero("Industry Cases", "Based on real industry needs · Customer names anonymized", "products/banner.jpg")}
<section class="cases-section"><div class="container">
<p class="kb-lead">Challenge / Solution / Results are summarized in English titles; full write-ups are in Chinese with anonymized customers.</p>
<div class="case-grid">{en_cases}</div>
</div></section>""",
        "/en/cases.html",
        lang="en",
    )

    for rel, html in pages.items():
        out = DIST / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print("wrote", rel)

    # Remove obsolete ceramic product/news pages if present
    for obsolete in [
        "products/aln-substrate.html",
        "products/dbc-amb.html",
        "products/alumina.html",
        "news/ceramic-summit-2025.html",
        "news/iso9001-certification.html",
        "news/alumina-mass-production.html",
        "news/aln-thermal-test.html",
        "news/ev-partnership.html",
        "knowledge/aln-vs-alumina.html",
        "knowledge/dbc-vs-amb.html",
        "knowledge/igbt-substrate-guide.html",
        "cases/semiconductor-packaging.html",
        "cases/ev-power-module.html",
        "technology/index.html",
        "applications/index.html",
        "en/technology.html",
        "en/applications.html",
    ]:
        p = DIST / obsolete
        if p.exists():
            p.unlink()
            print("removed", obsolete)

    urls = [
        "/",
        "/products/",
        "/about/",
        "/news/",
        "/knowledge/",
        "/cases/",
        "/contact/",
        "/en/",
        "/en/products.html",
        "/en/news.html",
        "/en/knowledge.html",
        "/en/cases.html",
        "/en/about.html",
        "/en/contact.html",
    ]
    urls += [f"/products/{p['slug']}.html" for p in PRODUCTS]
    urls += [f"/en/products/{p['slug']}.html" for p in PRODUCTS]
    urls += [f"/news/{n['slug']}.html" for n in NEWS]
    urls += [f"/knowledge/{k['slug']}.html" for k in KNOWLEDGE]
    urls += [f"/cases/{c['slug']}.html" for c in INDUSTRY_CASES]
    urls += ["/privacy.html"]

    # EN sitemap
    en_urls = [
        "/en/", "/en/products.html", "/en/news.html", "/en/knowledge.html",
        "/en/cases.html", "/en/about.html", "/en/contact.html",
    ]
    en_urls += [f"/en/products/{p['slug']}.html" for p in PRODUCTS]

    def make_sm(url_list, domain="https://kdgc.cc"):
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for u in url_list:
            sm += f"  <url><loc>{domain}{u}</loc><changefreq>weekly</changefreq><lastmod>2026-07-20</lastmod></url>\n"
        sm += "</urlset>"
        return sm

    all_urls = urls + en_urls
    (DIST / "sitemap.xml").write_text(make_sm(all_urls))
    (DIST / "sitemap-en.xml").write_text(make_sm(en_urls))
    (DIST / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n"
        "Sitemap: https://kdgc.cc/sitemap.xml\n"
        "Sitemap: https://kdgc.cc/sitemap-en.xml\n"
    )
    print("done", len(all_urls), "urls")


if __name__ == "__main__":
    main()
