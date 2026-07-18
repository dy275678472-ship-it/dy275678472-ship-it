#!/usr/bin/env python3
"""SiamSaaS growth optimization deploy — based on ChatGPT diagnosis report."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path("/opt/bangkok-edge/frontend")
ASSETS = ROOT / "assets"

INDEXED_PREVIEWS = {
    "beauty-clinic",
    "clothing-shop",
    "restaurant",
    "coffee-shop",
    "dental-clinic",
    "pharmacy",
    "fitness-gym",
    "hotel",
    "pet-shop",
    "hair-salon",
}

NEW_BLOG_POSTS = [
    {
        "slug": "line-oa-pricing-guide-2026",
        "title": "LINE OA ราคา 2026 — คู่มือแพ็กเกจและวิธีประหยัด",
        "desc": "เปรียบเทียบแพ็กเกจ LINE OA Free, Basic, Pro และวิธีลดค่าใช้จ่ายสำหรับร้านค้าไทย",
        "cat": "LINE OA Pricing",
    },
    {
        "slug": "line-oa-segmentation-guide",
        "title": "วิธีแบ่งกลุ่มลูกค้า LINE OA ด้วย AI Segmentation",
        "desc": "แนวทางแบ่งกลุ่มลูกค้า LINE OA เพื่อส่ง Broadcast เฉพาะกลุ่มที่มีโอกาสซื้อ",
        "cat": "AI Segmentation",
    },
    {
        "slug": "broadcast-line-oa-roi",
        "title": "Broadcast LINE OA ยังไงให้คุ้ม — คำนวณ ROI",
        "desc": "วิธีวัดผล Broadcast LINE OA และคำนวณ ROI สำหรับร้านค้า SME ไทย",
        "cat": "Broadcast ROI",
    },
    {
        "slug": "line-oa-crm-for-thai-sme",
        "title": "LINE OA CRM สำหรับร้านค้าไทย — เริ่มต้นอย่างไร",
        "desc": "คู่มือใช้ LINE OA เป็น CRM สำหรับร้านค้าไทย พร้อมเครื่องมือ AI ลดต้นทุน",
        "cat": "LINE OA CRM",
    },
]


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def set_meta_robots(s: str, content: str) -> str:
    if re.search(r'<meta\s+name=["\']robots["\']', s, re.I):
        return re.sub(
            r'<meta\s+name=["\']robots["\'][^>]*>',
            f'<meta name="robots" content="{content}">',
            s,
            count=1,
            flags=re.I,
        )
    return s.replace("</head>", f'<meta name="robots" content="{content}">\n</head>', 1)


def set_canonical(s: str, url: str) -> str:
    tag = f'<link rel="canonical" href="{url}">'
    if re.search(r'<link\s+rel=["\']canonical["\']', s, re.I):
        return re.sub(r'<link\s+rel=["\']canonical["\'][^>]*>', tag, s, count=1, flags=re.I)
    return s.replace("</head>", tag + "\n</head>", 1)


def inject_consent(s: str) -> str:
    snippet = '<script defer src="/assets/privacy-consent.js"></script>'
    if snippet in s:
        return s
    if "</head>" in s:
        return s.replace("</head>", snippet + "\n</head>", 1)
    return s + snippet


def strip_analytics(s: str) -> str:
    s = re.sub(
        r"<!--\s*Meta Pixel Code\s*-->.*?<!--\s*End Meta Pixel Code\s*-->",
        "",
        s,
        flags=re.S | re.I,
    )
    s = re.sub(
        r"<!--\s*Google tag.*?-->(?:\s*<script[^>]*googletagmanager[^>]*></script>)?\s*<script>\s*window\.dataLayer.*?</script>",
        "",
        s,
        flags=re.S | re.I,
    )
    s = re.sub(
        r'<script\s+async\s+src="https://www\.googletagmanager\.com/gtag/js\?id=[^"]+"></script>\s*<script>\s*window\.dataLayer.*?</script>',
        "",
        s,
        flags=re.S | re.I,
    )
    s = re.sub(
        r"<script>\s*!function\(f,b,e,v,n,t,s\).*?fbq\(\s*['\"]track['\"]\s*,\s*['\"]PageView['\"]\s*\);\s*</script>",
        "",
        s,
        flags=re.S,
    )
    s = re.sub(
        r"<noscript>\s*<img[^>]+facebook\.com/tr\?id=[^>]+>\s*</noscript>",
        "",
        s,
        flags=re.S | re.I,
    )
    s = re.sub(r'<script[^>]*src="/assets/analytics\.js"[^>]*></script>\s*', "", s)
    return s


def redirect_page(title: str, target: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="th"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="https://siamsaas.com{target}">
<meta http-equiv="refresh" content="0;url={target}">
<script>location.replace("{target}");</script>
<script defer src="/assets/privacy-consent.js"></script>
</head><body><p><a href="{target}">ไปยังหน้าหลัก</a></p></body></html>"""


def trust_shell(title: str, desc: str, canonical: str, h1: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="th"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;600;700&display=swap" rel="stylesheet">
<script defer src="/assets/privacy-consent.js"></script>
<style>
:root{{--bg:#0b1324;--text:#e8edf4;--muted:#96a7bf;--gold:#d4af37}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:Prompt,sans-serif;line-height:1.75}}
nav{{max-width:1000px;margin:0 auto;padding:14px 20px;display:flex;gap:16px;border-bottom:1px solid rgba(212,175,55,.1)}}
nav a{{color:var(--muted);text-decoration:none;font-size:14px}}
nav a:hover{{color:var(--gold)}}
.logo{{font-weight:800;color:#fff;margin-right:auto}}
.logo span{{color:var(--gold)}}
.wrap{{max-width:760px;margin:0 auto;padding:48px 20px 64px}}
h1{{font-size:clamp(28px,4vw,40px);margin-bottom:12px}}
h2{{font-size:20px;color:var(--gold);margin:28px 0 10px}}
p,li{{color:#c8d2e0;margin-bottom:12px}}
ul{{padding-left:20px}}
footer{{text-align:center;color:var(--muted);font-size:12px;padding:32px;border-top:1px solid rgba(255,255,255,.05)}}
footer a{{color:var(--gold)}}
</style>
</head><body>
<nav><a class="logo" href="/"><span>Siam</span>SaaS</a>
<a href="/calculator">Calculator</a><a href="/pricing">ราคา</a><a href="/blog">Blog</a><a href="/contact">ติดต่อ</a></nav>
<section class="wrap"><h1>{h1}</h1>{body_html}</section>
<footer><a href="/privacy">Privacy</a> · <a href="/terms">Terms</a> · <a href="/security-pdpa">PDPA</a> · © 2026 SiamSaaS</footer>
</body></html>"""


def blog_post_html(post: dict) -> str:
    slug = post["slug"]
    return f"""<!DOCTYPE html>
<html lang="th"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{post["title"]} | SiamSaaS Blog</title>
<meta name="description" content="{post["desc"]}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://siamsaas.com/blog/{slug}">
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;600;700&display=swap" rel="stylesheet">
<script defer src="/assets/privacy-consent.js"></script>
<style>
body{{background:#0b1324;color:#e8edf4;font-family:Prompt,sans-serif;line-height:1.8;margin:0}}
nav{{max-width:1000px;margin:0 auto;padding:14px 20px;display:flex;gap:16px;border-bottom:1px solid rgba(212,175,55,.1)}}
nav a{{color:#96a7bf;text-decoration:none;font-size:14px}}
article{{max-width:760px;margin:0 auto;padding:48px 20px}}
.cat{{color:#d4af37;font-size:12px;font-weight:700}}
h1{{font-size:clamp(26px,4vw,36px);margin:8px 0 16px}}
h2{{color:#d4af37;font-size:20px;margin:28px 0 10px}}
p,li{{color:#c8d2e0}}
.cta{{display:inline-block;background:#06c755;color:#fff;padding:12px 20px;border-radius:10px;text-decoration:none;font-weight:700;margin-top:20px}}
</style>
</head><body>
<nav><a href="/">SiamSaaS</a><a href="/blog">Blog</a><a href="/calculator">Calculator</a></nav>
<article>
<div class="cat">{post["cat"]}</div>
<h1>{post["title"]}</h1>
<p>{post["desc"]}</p>
<h2>ทำไมร้านค้าไทยต้องสนใจเรื่องนี้</h2>
<p>LINE OA เป็นแพลตฟอร์มหลักของร้านค้าไทย แต่การส่ง Broadcast แบบกว้างๆ ทำให้ต้นทุนสูงและอัตราบล็อกเพิ่ม SiamSaaS ช่วยวิเคราะห์ลูกค้า แบ่งกลุ่ม และแนะนำว่าควรส่งข้อความให้ใครเพื่อลดค่าใช้จ่าย 30–70%</p>
<h2>วิธีเริ่มต้น</h2>
<ul>
<li>ใช้ <a href="/calculator" style="color:#d4af37">เครื่องมือคำนวณค่า LINE OA ฟรี</a> เพื่อประเมินต้นทุนปัจจุบัน</li>
<li>ดู <a href="/pricing" style="color:#d4af37">แพ็กเกจราคา</a> — เริ่มต้นฟรี Pro ฿499/เดือน</li>
<li>ลงทะเบียน Waitlist เพื่อรับส่วนลด Lifetime 50%</li>
</ul>
<a class="cta" href="/calculator">คำนวณค่า LINE OA ฟรี</a>
<p style="margin-top:32px;font-size:13px;color:#96a7bf"><a href="/blog" style="color:#d4af37">← กลับไป Blog</a></p>
</article>
</body></html>"""


def main() -> None:
    stats: dict[str, int] = {}

    # 1) privacy-consent.js
    consent_js = r"""(function(){
  var CONSENT_KEY='siamsaas_cookie_consent_v2';
  var GA_ID='G-5YDSBLLKDX';
  var META_PIXEL_ID='2248503722628105';
  function loadScript(src){if(document.querySelector('script[src="'+src+'"]'))return;var s=document.createElement('script');s.src=src;s.async=true;document.head.appendChild(s);}
  function loadAnalytics(){
    if(window.__siamsaasAnalyticsLoaded)return;
    window.__siamsaasAnalyticsLoaded=true;
    window.dataLayer=window.dataLayer||[];
    window.gtag=function(){dataLayer.push(arguments);};
    loadScript('https://www.googletagmanager.com/gtag/js?id='+GA_ID);
    gtag('js',new Date());
    gtag('config',GA_ID,{anonymize_ip:true});
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    if(window.fbq){fbq('init',META_PIXEL_ID);fbq('track','PageView');}
    window.siamTrack=function(name,params){if(typeof gtag==='function')gtag('event',name,params||{});};
    window.siamConversion=function(type,params){
      var payload=Object.assign({event_category:'conversion'},params||{});
      if(typeof gtag==='function'){gtag('event',type,payload);if(type==='waitlist_signup')gtag('event','generate_lead',{currency:'THB',value:1});}
      if(typeof fbq==='function'&&type==='waitlist_signup')fbq('track','Lead');
    };
  }
  function setConsent(v){localStorage.setItem(CONSENT_KEY,v);var b=document.getElementById('siamsaas-consent');if(b)b.remove();if(v==='accepted')loadAnalytics();}
  function showBanner(){
    if(document.getElementById('siamsaas-consent'))return;
    var box=document.createElement('div');box.id='siamsaas-consent';
    box.innerHTML='<div class="ss-consent-text"><strong>การใช้คุกกี้</strong><br>เราใช้คุกกี้วิเคราะห์และการตลาดเมื่อคุณยินยอมเท่านั้น ตามแนวทาง PDPA</div><div class="ss-consent-actions"><button id="ss-reject">ปฏิเสธ</button><button id="ss-accept">ยอมรับ</button></div>';
    var css=document.createElement('style');
    css.textContent='#siamsaas-consent{position:fixed;left:16px;right:16px;bottom:16px;z-index:99999;max-width:760px;margin:0 auto;background:#111827;color:#e8edf4;border:1px solid rgba(212,175,55,.28);box-shadow:0 18px 60px rgba(0,0,0,.35);border-radius:16px;padding:16px;display:flex;gap:16px;align-items:center;font-family:Prompt,Sarabun,system-ui,sans-serif}.ss-consent-text{font-size:13px;line-height:1.6;flex:1}.ss-consent-actions{display:flex;gap:8px}.ss-consent-actions button{border:0;border-radius:10px;padding:10px 16px;font-weight:700;cursor:pointer}#ss-reject{background:#374151;color:#e5e7eb}#ss-accept{background:#d4af37;color:#0b1324}@media(max-width:640px){#siamsaas-consent{flex-direction:column}}';
    document.head.appendChild(css);document.body.appendChild(box);
    document.getElementById('ss-accept').onclick=function(){setConsent('accepted');};
    document.getElementById('ss-reject').onclick=function(){setConsent('rejected');};
  }
  document.addEventListener('DOMContentLoaded',function(){
    var state=localStorage.getItem(CONSENT_KEY);
    if(state==='accepted')loadAnalytics();
    else if(state!=='rejected')showBanner();
  });
})();"""
    ASSETS.mkdir(exist_ok=True)
    write(ASSETS / "privacy-consent.js", consent_js.strip())
    stats["consent_js"] = 1

    # Strip analytics + inject consent on all HTML
    html_count = 0
    for p in ROOT.rglob("*.html"):
        if "node_modules" in str(p):
            continue
        s = strip_analytics(read(p))
        s = inject_consent(s)
        write(p, s)
        html_count += 1
    stats["html_cleaned"] = html_count

    # 2) payment.html pricing fix
    payment = ROOT / "payment.html"
    s = read(payment)
    s = set_meta_robots(s, "noindex, nofollow")
    s = set_canonical(s, "https://siamsaas.com/payment")
    s = s.replace('data-plan="pro" data-price="2500"', 'data-plan="pro" data-price="499"')
    s = s.replace("💎 Pro<br><small>฿2,500/เดือน</small>", "💎 Pro<br><small>฿499/เดือน</small>")
    s = s.replace('data-plan="business" data-price="7500"', 'data-plan="enterprise" data-price="2990"')
    s = s.replace("🏢 Business<br><small>฿7,500/เดือน</small>", "🏢 Enterprise<br><small>฿2,990/เดือน</small>")
    s = s.replace(
        "pro:'💎 Pro — ฿2,500/เดือน',business:'🏢 Business — ฿7,500/เดือน'",
        "pro:'💎 Pro — ฿499/เดือน',enterprise:'🏢 Enterprise — ฿2,990/เดือน'",
    )
    s = s.replace("selectedPlan==='pro'?'Pro':'Business'", "selectedPlan==='pro'?'Pro':'Enterprise'")
    s = s.replace("business:'🏢 Business", "enterprise:'🏢 Enterprise")
    write(payment, s)
    stats["payment_fixed"] = 1

    # 3) Homepage CTA
    idx = ROOT / "index.html"
    s = read(idx)
    cta_block = """<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-bottom:28px;max-width:480px;width:100%">
      <a href="/calculator" style="flex:1;min-width:200px;padding:15px 20px;background:linear-gradient(135deg,#d4af37,#f0d060);color:#0a0b12;font-size:15px;font-weight:700;border-radius:12px;text-decoration:none;text-align:center;box-shadow:0 6px 20px rgba(212,175,55,0.15)">📊 คำนวณค่า LINE OA ฟรี</a>
      <a href="/dashboard" style="flex:1;min-width:200px;padding:15px 20px;background:rgba(255,255,255,0.05);border:1px solid rgba(212,175,55,0.2);color:#e8edf4;font-size:15px;font-weight:600;border-radius:12px;text-decoration:none;text-align:center">ดู Demo Dashboard</a>
    </div>"""
    if "คำนวณค่า LINE OA ฟรี" not in s and 'class="pain-point"' in s:
        s = s.replace('<div class="pain-point">', cta_block + '\n    <div class="pain-point">', 1)
        write(idx, s)
        stats["homepage_cta"] = 1

    # 4) Calculator SEO upgrade
    calc = ROOT / "calculator.html"
    calc_content = f"""<!DOCTYPE html>
<html lang="th"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>เครื่องมือคำนวณค่า LINE OA ฟรี — ประหยัดได้เท่าไหร่? | SiamSaaS</title>
<meta name="description" content="คำนวณค่าใช้จ่าย LINE OA ฟรี เปรียบเทียบต้นทุน Broadcast ปัจจุบันกับการใช้ AI Segmentation ลดค่าส่งได้ 30–70% สำหรับร้านค้าไทย">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://siamsaas.com/calculator">
<meta property="og:title" content="เครื่องมือคำนวณค่า LINE OA ฟรี | SiamSaaS">
<meta property="og:description" content="คำนวณว่าคุณประหยัดค่า Broadcast LINE OA ได้เท่าไหร่ด้วย AI Segmentation">
<meta property="og:url" content="https://siamsaas.com/calculator">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"SoftwareApplication","name":"SiamSaaS LINE OA Cost Calculator","applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{{"@type":"Offer","price":"0","priceCurrency":"THB"}},"description":"เครื่องมือคำนวณค่า LINE OA สำหรับร้านค้าไทย"}}
</script>
<script defer src="/assets/privacy-consent.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0b1324;color:#e8edf4;font-family:Prompt,sans-serif;line-height:1.7}}
nav{{max-width:1000px;margin:0 auto;padding:14px 20px;display:flex;gap:16px;border-bottom:1px solid rgba(212,175,55,.1)}}
nav a{{color:#96a7bf;text-decoration:none;font-size:14px}}
.wrap{{max-width:900px;margin:0 auto;padding:40px 20px}}
h1{{font-size:clamp(26px,4vw,38px);margin-bottom:8px}}
h1 span{{color:#d4af37}}
.sub{{color:#96a7bf;margin-bottom:28px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}
@media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}
.calc-card{{background:rgba(22,34,58,.8);border:1px solid rgba(212,175,55,.12);border-radius:16px;padding:28px}}
label{{display:block;font-size:13px;color:#96a7bf;margin:12px 0 6px}}
input[type=range]{{width:100%}}
.stat{{display:flex;justify-content:space-between;padding:8px 0;font-size:14px;border-bottom:1px solid rgba(255,255,255,.05)}}
.savings{{font-size:32px;font-weight:800;color:#10b981;text-align:center;padding:16px 0}}
.faq{{margin-top:40px}}
.faq h2{{color:#d4af37;font-size:20px;margin-bottom:16px}}
.faq details{{background:rgba(22,34,58,.5);border:1px solid rgba(212,175,55,.1);border-radius:10px;padding:14px 16px;margin-bottom:8px}}
.faq summary{{cursor:pointer;font-weight:600}}
</style>
</head><body>
<nav><a href="/">SiamSaaS</a><a href="/pricing">ราคา</a><a href="/blog">Blog</a></nav>
<div class="wrap">
<h1>เครื่องมือ<span>คำนวณค่า LINE OA</span> ฟรี</h1>
<p class="sub">ประเมินต้นทุน Broadcast ปัจจุบัน และดูว่า AI Segmentation ช่วยประหยัดได้เท่าไหร่</p>
<div class="grid">
<div class="calc-card">
<label>จำนวนเพื่อน LINE OA: <strong id="friendsVal">5,000</strong></label>
<input type="range" id="friends" min="500" max="100000" step="500" value="5000" oninput="calc()">
<label>จำนวน Broadcast ต่อเดือน: <strong id="broadcastVal">20</strong></label>
<input type="range" id="broadcast" min="1" max="100" value="20" oninput="calc()">
<label>อัตรา Target ปัจจุบัน (%): <strong id="targetVal">30</strong></label>
<input type="range" id="target" min="5" max="100" value="30" oninput="calc()">
</div>
<div class="calc-card">
<div class="stat"><span>ต้นทุนปัจจุบัน/เดือน</span><span id="currentCost">฿0</span></div>
<div class="stat"><span>ต้นทุนหลังใช้ SiamSaaS</span><span id="newCost">฿0</span></div>
<div class="savings" id="savings">ประหยัด ฿0/เดือน</div>
<p style="text-align:center;font-size:13px;color:#96a7bf">ประมาณการ — ผลจริงขึ้นกับพฤติกรรมลูกค้า</p>
<a href="/" style="display:block;text-align:center;background:#06c755;color:#fff;padding:14px;border-radius:12px;text-decoration:none;font-weight:700;margin-top:16px">ลงทะเบียน Waitlist ฟรี</a>
</div>
</div>
<section class="faq">
<h2>คำถามที่พบบ่อย</h2>
<details><summary>LINE OA คิดค่าส่ง Broadcast อย่างไร?</summary><p>LINE OA มีโควตาฟรีตามแพ็กเกจ ส่วนเกินจะคิดตามจำนวนข้อความที่ส่ง SiamSaaS ช่วยลดการส่งไม่จำเป็น</p></details>
<details><summary>ประหยัดได้จริง 30–70% หรือไม่?</summary><p>ขึ้นกับอัตรา Target ปัจจุบัน ร้านที่ส่งกว้างๆ มักประหยัดได้มากกว่า</p></details>
<details><summary>ต้องเขียนโค้ดหรือไม่?</summary><p>ไม่ต้อง เชื่อมต่อ LINE OA และใช้ AI แบ่งกลุ่มอัตโนมัติ</p></details>
</section>
</div>
<script>
function calc(){{
  var f=+document.getElementById('friends').value;
  var b=+document.getElementById('broadcast').value;
  var t=+document.getElementById('target').value;
  document.getElementById('friendsVal').textContent=f.toLocaleString();
  document.getElementById('broadcastVal').textContent=b;
  document.getElementById('targetVal').textContent=t;
  var msgs=Math.round(f*b);
  var costPerMsg=0.35;
  var current=Math.round(msgs*costPerMsg);
  var improvedTarget=Math.min(100,Math.max(t,45));
  var newMsgs=Math.round(f*b*(improvedTarget/100));
  var newer=Math.round(newMsgs*costPerMsg);
  var save=Math.max(0,current-newer);
  document.getElementById('currentCost').textContent='฿'+current.toLocaleString();
  document.getElementById('newCost').textContent='฿'+newer.toLocaleString();
  document.getElementById('savings').textContent='ประหยัด ฿'+save.toLocaleString()+'/เดือน';
}}
calc();
</script>
</body></html>"""
    write(calc, calc_content)
    stats["calculator_seo"] = 1

    # 5) cloud-deals redirect
    write(ROOT / "cloud-deals.html", redirect_page("Redirecting...", "/"))
    stats["cloud_deals"] = 1

    # 6) Thai duplicate redirect
    thai_dup = ROOT / "ลดค่าส่ง-line-oa.html"
    if thai_dup.exists():
        write(thai_dup, redirect_page("Redirect", "/reduce-line-oa-cost"))
        stats["thai_dup"] = 1

    # 7) Preview pages noindex/index
    indexed = noindexed = 0
    preview_dir = ROOT / "preview"
    if preview_dir.exists():
        for d in preview_dir.iterdir():
            if not d.is_dir():
                continue
            idx_p = d / "index.html"
            if not idx_p.exists():
                continue
            s = read(idx_p)
            if d.name in INDEXED_PREVIEWS:
                s = set_meta_robots(s, "index, follow")
                indexed += 1
            else:
                s = set_meta_robots(s, "noindex, follow")
                noindexed += 1
            s = strip_analytics(s)
            s = inject_consent(s)
            write(idx_p, s)
    stats["preview_indexed"] = indexed
    stats["preview_noindex"] = noindexed

    # 8) Trust pages
    write(
        ROOT / "about.html",
        trust_shell(
            "เกี่ยวกับ SiamSaaS — AI LINE OA Cost Optimizer",
            "SiamSaaS คือระบบ AI ช่วยร้านค้าไทยลดค่าส่ง LINE OA ด้วยการแบ่งกลุ่มลูกค้าอัตโนมัติ",
            "https://siamsaas.com/about",
            "เกี่ยวกับ SiamSaaS",
            """<p>SiamSaaS ก่อตั้งขึ้นเพื่อช่วยร้านค้า SME ไทยลดต้นทุน LINE Official Account โดยใช้ AI วิเคราะห์พฤติกรรมลูกค้า แท็กกลุ่ม และแนะนำว่าควรส่ง Broadcast ให้ใคร</p>
<h2>พันธกิจ</h2><p>ทำให้ร้านค้าไทยส่ง LINE น้อยลง แต่ขายได้มากขึ้น</p>
<h2>ทีม</h2><p>ทีมผู้เชี่ยวชาญด้าน LINE Marketing และ AI ที่ Bangkok ประเทศไทย</p>""",
        ),
    )
    write(
        ROOT / "security-pdpa.html",
        trust_shell(
            "ความปลอดภัยและ PDPA | SiamSaaS",
            "นโยบายความปลอดภัยข้อมูลและการปฏิบัติตาม PDPA ของ SiamSaaS",
            "https://siamsaas.com/security-pdpa",
            "ความปลอดภัยและ PDPA",
            """<p>SiamSaaS ปฏิบัติตามพระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล (PDPA) ของประเทศไทย</p>
<h2>การเก็บข้อมูล</h2><ul><li>เก็บเฉพาะข้อมูลที่จำเป็นสำหรับบริการ</li><li>ไม่ขายข้อมูลให้บุคคลที่สาม</li><li>เข้ารหัสการส่งข้อมูลด้วย HTTPS</li></ul>
<h2>คุกกี้</h2><p>ใช้คุกกี้วิเคราะห์และการตลาดเมื่อผู้ใช้ยินยอมเท่านั้น</p>""",
        ),
    )
    write(
        ROOT / "contact.html",
        trust_shell(
            "ติดต่อ SiamSaaS",
            "ติดต่อทีม SiamSaaS สำหรับคำถาม การสาธิต หรือความร่วมมือ",
            "https://siamsaas.com/contact",
            "ติดต่อเรา",
            """<p>อีเมล: hello@siamsaas.com</p>
<p>LINE OA: @siamsaas</p>
<h2>แบบฟอร์มติดต่อ</h2>
<form id="contactForm" onsubmit="return submitContact(event)">
<label>ชื่อ</label><input required name="name" style="width:100%;padding:12px;border-radius:8px;border:1px solid #333;background:#16223a;color:#fff;margin-bottom:12px">
<label>อีเมล</label><input required type="email" name="email" style="width:100%;padding:12px;border-radius:8px;border:1px solid #333;background:#16223a;color:#fff;margin-bottom:12px">
<label>ข้อความ</label><textarea required name="message" rows="4" style="width:100%;padding:12px;border-radius:8px;border:1px solid #333;background:#16223a;color:#fff;margin-bottom:12px"></textarea>
<button type="submit" style="background:#d4af37;color:#0b1324;border:0;padding:12px 24px;border-radius:10px;font-weight:700;cursor:pointer">ส่งข้อความ</button>
</form>
<script>
async function submitContact(e){{
  e.preventDefault();
  var fd=new FormData(e.target);
  var r=await fetch('/api/contact',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{name:fd.get('name'),email:fd.get('email'),message:fd.get('message')}})}});
  var d=await r.json();
  alert(d.ok?'ส่งข้อความสำเร็จ!':'เกิดข้อผิดพลาด: '+(d.message||''));
  return false;
}}
</script>""",
        ),
    )
    write(
        ROOT / "case-studies.html",
        trust_shell(
            "กรณีศึกษา SiamSaaS — ลดค่าส่ง LINE OA",
            "กรณีศึกษาการลดต้นทุน LINE OA ของร้านค้าไทยด้วย SiamSaaS",
            "https://siamsaas.com/case-studies",
            "กรณีศึกษา",
            """<p>ตัวอย่างผลลัพธ์จากร้านค้าที่ใช้ AI Segmentation (ข้อมูลสาธิต)</p>
<ul>
<li><a href="/case-studies/fashion-shop-line-oa-cost-saving/" style="color:#d4af37">ร้านเสื้อผ้าออนไลน์ — ลดค่าส่ง 62%</a></li>
</ul>""",
        ),
    )
    case_dir = ROOT / "case-studies" / "fashion-shop-line-oa-cost-saving"
    write(
        case_dir / "index.html",
        trust_shell(
            "กรณีศึกษา: ร้านเสื้อผ้าลดค่าส่ง LINE OA 62%",
            "ร้านเสื้อผ้าออนไลน์ใช้ SiamSaaS ลดค่า Broadcast LINE OA 62%",
            "https://siamsaas.com/case-studies/fashion-shop-line-oa-cost-saving/",
            "ร้านเสื้อผ้าออนไลน์ — ลดค่าส่ง 62%",
            """<p><em>ข้อมูลสาธิต — ผลลัพธ์จริงขึ้นกับพฤติกรรมลูกค้า</em></p>
<h2>สถานการณ์</h2><p>ร้านเสื้อผ้าออนไลน์มีเพื่อน LINE OA 12,000 คน ส่ง Broadcast ทุกสัปดาห์ ต้นทุน ฿4,200/เดือน</p>
<h2>วิธีแก้</h2><p>ใช้ SiamSaaS แบ่งกลุ่มลูกค้าตามพฤติกรรมซื้อ ส่งเฉพาะกลุ่ม High Intent</p>
<h2>ผลลัพธ์</h2><ul><li>ลดค่าส่ง 62% (เหลือ ฿1,600/เดือน)</li><li>อัตราเปิดข้อความเพิ่ม 28%</li><li>ยอดขายจาก LINE เพิ่ม 15%</li></ul>
<a href="/calculator" style="display:inline-block;background:#06c755;color:#fff;padding:12px 20px;border-radius:10px;text-decoration:none;font-weight:700">คำนวณประหยัดของคุณ</a>""",
        ),
    )
    stats["trust_pages"] = 5

    # 9) Blog posts + static index
    blog_json_path = ROOT / "data" / "blog.json"
    posts = json.loads(read(blog_json_path)) if blog_json_path.exists() else []
    existing_slugs = {p.get("slug", "") for p in posts}
    for post in NEW_BLOG_POSTS:
        if post["slug"] not in existing_slugs:
            posts.append(
                {
                    "slug": post["slug"],
                    "title": post["title"],
                    "excerpt": post["desc"],
                    "category": post["cat"],
                    "date": str(date.today()),
                    "author": "SiamSaaS Team",
                }
            )
        blog_dir = ROOT / "blog" / post["slug"]
        write(blog_dir / "index.html", blog_post_html(post))
    write(blog_json_path, json.dumps(posts, ensure_ascii=False, indent=2))

    # Static blog.html cards from blog.json
    cards = ""
    for p in posts:
        slug = p.get("slug", "")
        title = p.get("title", slug)
        excerpt = p.get("excerpt", p.get("desc", ""))
        cat = p.get("category", "LINE OA")
        cards += f'<a class="post-card" href="/blog/{slug}"><div class="cat">{cat}</div><h3>{title}</h3><p>{excerpt}</p></a>\n'

    blog_html = read(ROOT / "blog.html")
    if "กำลังโหลด" in blog_html:
        blog_html = re.sub(
            r'<div style="text-align:center;padding:60px 20px;color:#96a7bf;">.*?</div>',
            f'<div class="blog-grid">{cards}</div>',
            blog_html,
            flags=re.S,
        )
        write(ROOT / "blog.html", blog_html)

    # blog/index.html
    blog_index_cards = "\n".join(
        f'<li><a href="/blog/{p.get("slug","")}">{p.get("title","")}</a></li>' for p in posts
    )
    write(
        ROOT / "blog" / "index.html",
        f"""<!DOCTYPE html><html lang="th"><head>
<meta charset="UTF-8"><title>SiamSaaS Blog</title>
<meta name="description" content="บทความ LINE OA สำหรับร้านค้าไทย">
<link rel="canonical" href="https://siamsaas.com/blog/">
<script defer src="/assets/privacy-consent.js"></script>
</head><body style="background:#0b1324;color:#e8edf4;font-family:Prompt,sans-serif;padding:40px">
<h1>SiamSaaS Blog</h1><ul>{blog_index_cards}</ul>
<p><a href="/blog" style="color:#d4af37">ดู Blog แบบเต็ม →</a></p>
</body></html>""",
    )
    stats["blog_posts"] = len(posts)

    # 10) Sitemap + robots.txt
    url_map: dict[str, str] = {}
    for p in ROOT.rglob("index.html"):
        rel = p.parent.relative_to(ROOT)
        if "node_modules" in str(rel) or "preview" in str(rel.parts[:1]):
            continue
        path = "/" if rel == Path(".") else "/" + str(rel).replace("\\", "/")
        if "/preview/" in path:
            continue
        pri = "1.0" if path == "/" else "0.8" if path.count("/") <= 2 else "0.6"
        url_map[f"https://siamsaas.com{path}"] = pri

    for p in ROOT.glob("*.html"):
        path = "/" + p.stem if p.stem != "index" else "/"
        if p.stem in ("cloud-deals", "payment"):
            continue
        url_map[f"https://siamsaas.com/{p.stem}"] = "0.7"

    for slug_dir in (ROOT / "blog").iterdir():
        if slug_dir.is_dir() and (slug_dir / "index.html").exists():
            url_map[f"https://siamsaas.com/blog/{slug_dir.name}"] = "0.6"

    for name in INDEXED_PREVIEWS:
        url_map[f"https://siamsaas.com/preview/{name}/"] = "0.5"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, pri in sorted(url_map.items()):
        lines.append(
            f"  <url><loc>{loc}</loc><lastmod>{date.today()}</lastmod>"
            f"<changefreq>weekly</changefreq><priority>{pri}</priority></url>"
        )
    lines.append("</urlset>")
    write(ROOT / "sitemap.xml", "\n".join(lines))
    stats["sitemap_urls"] = len(url_map)

    robots = read(ROOT / "robots.txt") if (ROOT / "robots.txt").exists() else ""
    if "cloud-deals" not in robots:
        robots += "\nDisallow: /cloud-deals\nDisallow: /payment\n"
        write(ROOT / "robots.txt", robots.strip() + "\n")

    # Footer links on index
    idx = read(ROOT / "index.html")
    if "/about" not in idx and "<footer" in idx:
        idx = idx.replace(
            '<footer',
            '<div style="text-align:center;padding:16px;font-size:12px;color:#8da0ba"><a href="/about" style="color:#d4af37;margin:0 8px">About</a><a href="/contact" style="color:#d4af37;margin:0 8px">Contact</a><a href="/case-studies" style="color:#d4af37;margin:0 8px">Case Studies</a><a href="/security-pdpa" style="color:#d4af37;margin:0 8px">PDPA</a></div>\n<footer',
            1,
        )
        write(ROOT / "index.html", idx)

    print("✅ SiamSaaS growth deploy complete")
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
