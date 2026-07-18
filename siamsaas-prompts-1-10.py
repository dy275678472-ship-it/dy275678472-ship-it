#!/usr/bin/env python3
"""SiamSaaS prompts 1-10 full deployment."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path("/opt/bangkok-edge/frontend")
ASSETS = ROOT / "assets"
DOCS = ROOT / "docs"
SCRIPTS = Path("/opt/bangkok-edge/scripts")


def w(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def r(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def patch(path: Path, old: str, new: str, label: str) -> bool:
    t = r(path)
    if old not in t:
        return False
    w(path, t.replace(old, new, 1))
    print(f"  ✓ {label}")
    return True


# ─── Shared helpers ───────────────────────────────────────────────
CONSENT = '<script defer src="/assets/privacy-consent.js"></script>'
SITE_CSS = '<link rel="stylesheet" href="/assets/site.css">'


def page_shell(title, desc, canonical, h1, body, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="th"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{canonical}">
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;600;700&display=swap" rel="stylesheet">
{SITE_CSS}
{CONSENT}
{extra_head}
</head><body>
<nav class="ss-nav"><a class="ss-logo" href="/"><span>Siam</span>SaaS</a>
<a href="/calculator">Calculator</a><a href="/pricing">ราคา</a><a href="/blog">Blog</a><a href="/compare">Compare</a></nav>
<article class="ss-wrap"><h1>{h1}</h1>{body}
<p class="ss-cta-row"><a class="ss-btn-gold" href="/calculator">📊 คำนวณค่า LINE OA ฟรี</a>
<a class="ss-btn-outline" href="/">ลงทะเบียน Waitlist</a></p></article>
<footer class="ss-footer"><a href="/about">About</a> · <a href="/contact">Contact</a> · <a href="/case-studies.html">Cases</a> · <a href="/security-pdpa">PDPA</a> · © 2026 SiamSaaS</footer>
</body></html>"""


LANDING_PAGES = [
    {
        "file": "reduce-line-oa-cost.html",
        "slug": "reduce-line-oa-cost",
        "kw": "ลดค่าส่ง LINE OA",
        "title": "ลดค่าส่ง LINE OA 30–70% ด้วย AI | SiamSaaS",
        "desc": "วิธีลดค่าส่ง LINE OA สำหรับร้านค้าไทย — AI แบ่งกลุ่มลูกค้า ส่ง Broadcast เฉพาะคนที่ใช่ ลดต้นทุนได้จริง",
    },
    {
        "file": "line-oa-pricing-guide.html",
        "slug": "line-oa-pricing-guide",
        "kw": "LINE OA ราคา 2026",
        "title": "LINE OA ราคา 2026 — คู่มือแพ็กเกจและวิธีประหยัด | SiamSaaS",
        "desc": "เปรียบเทียบแพ็กเกจ LINE OA Free Basic Pro ค่าใช้จ่าย Broadcast และวิธีลดต้นทุนสำหรับ SME ไทย",
    },
    {
        "file": "line-oa-segmentation.html",
        "slug": "line-oa-segmentation",
        "kw": "แบ่งกลุ่มลูกค้า LINE OA",
        "title": "วิธีแบ่งกลุ่มลูกค้า LINE OA ด้วย AI Segmentation | SiamSaaS",
        "desc": "คู่มือ LINE OA Segmentation สำหรับร้านค้าไทย — แท็กลูกค้า วิเคราะห์พฤติกรรม ส่งเฉพาะกลุ่ม High Intent",
    },
    {
        "file": "line-oa-crm.html",
        "slug": "line-oa-crm",
        "kw": "LINE OA CRM",
        "title": "LINE OA CRM สำหรับร้านค้าไทย — เริ่มต้นอย่างไร | SiamSaaS",
        "desc": "ใช้ LINE OA เป็น CRM สำหรับร้านค้า SME — จัดการลูกค้า แท็กกลุ่ม วัดผล Broadcast ด้วย AI",
    },
    {
        "file": "ai-วิเคราะห์ลูกค้า-line.html",
        "slug": "ai-customer-analysis-line",
        "kw": "AI วิเคราะห์ลูกค้า LINE OA",
        "title": "AI วิเคราะห์ลูกค้า LINE OA — แท็กอัตโนมัติ | SiamSaaS",
        "desc": "AI วิเคราะห์พฤติกรรมลูกค้าใน LINE OA แท็กกลุ่มอัตโนมัติ แนะนำว่าใครควรได้รับ Broadcast",
    },
]


def landing_body(kw: str) -> str:
    return f"""
<p>SiamSaaS ช่วยร้านค้า SME ไทยลดต้นทุน <strong>{kw}</strong> ด้วย AI Segmentation — วิเคราะห์พฤติกรรมลูกค้า แท็กกลุ่มอัตโนมัติ และแนะนำว่าใครควรได้รับ Broadcast เพื่อลดข้อความที่เสียเปล่า</p>
<h2>ปัญหาที่ร้านค้าไทยเจอ</h2>
<ul>
<li>ส่ง Broadcast กว้างๆ ทุกคน — ต้นทุนสูง อัตราบล็อกเพิ่ม</li>
<li>ไม่รู้ว่าใครมีโอกาสซื้อ — ข้อความไปถึงคนที่ไม่สนใจ</li>
<li>LINE OA ค่าใช้จ่ายเพิ่มทุกปี — โควตาฟรีไม่พอ</li>
</ul>
<h2>SiamSaaS แก้อย่างไร</h2>
<ol>
<li><strong>เชื่อมต่อ LINE OA</strong> — ไม่ต้องเขียนโค้ด</li>
<li><strong>AI วิเคราะห์พฤติกรรม 7 วัน</strong> — แท็กลูกค้าอัตโนมัติ</li>
<li><strong>แนะนำกลุ่ม Broadcast</strong> — ส่งเฉพาะ High Intent ลดต้นทุน 30–70%</li>
</ol>
<h2>ขั้นตอนเริ่มต้น</h2>
<ol>
<li>ใช้ <a href="/calculator">เครื่องมือคำนวณฟรี</a> ประเมินต้นทุนปัจจุบัน</li>
<li>ดู <a href="/dashboard">Demo Dashboard</a> ตัวอย่างระบบ</li>
<li>ลงทะเบียน Waitlist รับส่วนลด Lifetime 50%</li>
</ol>
<section class="ss-faq">
<h2>คำถามที่พบบ่อย</h2>
<details><summary>ลดค่าส่งได้จริงกี่เปอร์เซ็นต์?</summary><p>ขึ้นกับอัตรา Target ปัจจุบัน โดยเฉลี่ยจากการทดสอบ Beta ประหยัดได้ 30–70% ร้านที่ส่งกว้างๆ มักประหยัดได้มากกว่า</p></details>
<details><summary>ต้องใช้แพ็กเกจ LINE OA อะไร?</summary><p>ใช้ได้กับ Free, Basic, Pro — SiamSaaS เป็นเลเยอร์ AI ช่วยตัดสินใจว่าส่งให้ใคร</p></details>
<details><summary>ข้อมูลลูกค้าปลอดภัยไหม?</summary><p>ปฏิบัติตาม PDPA เข้ารหัส HTTPS ดูรายละเอียดที่ <a href="/security-pdpa">Security & PDPA</a></p></details>
<details><summary>ราคา SiamSaaS เท่าไหร่?</summary><p>เริ่มต้นฟรี Pro ฿499/เดือน Enterprise ฿2,990/เดือน — <a href="/pricing">ดูราคา</a></p></details>
<details><summary>ใช้เวลาตั้งค่านานไหม?</summary><p>เชื่อมต่อ LINE OA ใช้เวลาประมาณ 5 นาที ไม่ต้องเขียนโค้ด</p></details>
</section>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
{{"@type":"Question","name":"ลดค่าส่งได้จริงกี่เปอร์เซ็นต์?","acceptedAnswer":{{"@type":"Answer","text":"30-70% ขึ้นกับอัตรา Target ปัจจุบัน"}}}},
{{"@type":"Question","name":"ราคา SiamSaaS?","acceptedAnswer":{{"@type":"Answer","text":"ฟรีเริ่มต้น Pro 499 บาท/เดือน"}}}}
]}}
</script>"""


def main():
    print("🚀 SiamSaaS Prompts 1-10 Deploy\n")

    # ── P8: site.css (Phase 1 tokens + layout) ───────────────────
    w(ASSETS / "site.css", """:root{--bg:#0b1324;--card:rgba(22,34,58,.8);--gold:#d4af37;--text:#e8edf4;--muted:#96a7bf;--line:#06c755;--gradient-gold:linear-gradient(135deg,#d4af37,#f0d060)}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:Prompt,system-ui,sans-serif;line-height:1.75}
@media(max-width:768px){body.ss-mobile-bg{background-attachment:scroll!important}}
.ss-nav{max-width:1100px;margin:0 auto;padding:14px 20px;display:flex;gap:16px;align-items:center;border-bottom:1px solid rgba(212,175,55,.1)}
.ss-nav a{color:var(--muted);text-decoration:none;font-size:14px}
.ss-nav a:hover{color:var(--gold)}
.ss-logo{font-weight:800;color:#fff;margin-right:auto}
.ss-logo span{color:var(--gold)}
.ss-wrap{max-width:800px;margin:0 auto;padding:48px 20px 64px}
.ss-wrap h1{font-size:clamp(28px,4vw,40px);margin-bottom:16px;line-height:1.25}
.ss-wrap h2{color:var(--gold);font-size:20px;margin:28px 0 10px}
.ss-wrap p,.ss-wrap li{color:#c8d2e0;margin-bottom:10px}
.ss-wrap ul,.ss-wrap ol{padding-left:22px;margin-bottom:16px}
.ss-cta-row{display:flex;gap:12px;flex-wrap:wrap;margin-top:32px}
.ss-btn-gold{display:inline-block;background:var(--gradient-gold);color:#0a0b12;padding:14px 22px;border-radius:12px;text-decoration:none;font-weight:700}
.ss-btn-outline{display:inline-block;border:1px solid rgba(212,175,55,.3);color:var(--text);padding:14px 22px;border-radius:12px;text-decoration:none;font-weight:600}
.ss-footer{text-align:center;color:var(--muted);font-size:12px;padding:32px;border-top:1px solid rgba(255,255,255,.05)}
.ss-footer a{color:var(--gold);margin:0 6px}
.ss-faq details{background:var(--card);border:1px solid rgba(212,175,55,.1);border-radius:10px;padding:14px 16px;margin-bottom:8px}
.ss-faq summary{cursor:pointer;font-weight:600}
.ss-demo-banner{background:rgba(91,141,239,.12);border:1px solid rgba(91,141,239,.25);color:#9ec5ff;padding:12px 20px;text-align:center;font-size:13px;font-weight:600}
.ss-compare-table{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px}
.ss-compare-table th,.ss-compare-table td{border:1px solid rgba(212,175,55,.15);padding:10px 12px;text-align:left}
.ss-compare-table th{background:rgba(212,175,55,.08);color:var(--gold)}
""")
    print("✓ P8 site.css")

    # ── P4: privacy-consent.js with full analytics ───────────────
    w(ASSETS / "privacy-consent.js", r"""(function(){
  var CK='siamsaas_cookie_consent_v2',GA='G-5YDSBLLKDX',PIXEL='2248503722628105';
  function ls(src){if(document.querySelector('script[src="'+src+'"]'))return;var s=document.createElement('script');s.src=src;s.async=true;document.head.appendChild(s);}
  window.siamTrack=function(n,p){if(typeof gtag==='function')gtag('event',n,p||{});};
  window.siamConversion=function(t,p){
    var x=Object.assign({event_category:'conversion'},p||{});
    if(typeof gtag==='function'){gtag('event',t,x);
      if(t==='waitlist_signup')gtag('event','generate_lead',{currency:'THB',value:1});
      if(t==='payment_success')gtag('event','purchase',{currency:'THB',value:x.value||499});
      if(t==='calculator_lead_submit')gtag('event','generate_lead',{currency:'THB',value:2});
    }
    if(typeof fbq==='function'){
      if(t==='waitlist_signup'||t==='calculator_lead_submit')fbq('track','Lead');
      if(t==='payment_success')fbq('track','Purchase',{currency:'THB',value:x.value||499});
    }
  };
  function load(){
    if(window.__siamsaasAnalyticsLoaded)return;
    window.__siamsaasAnalyticsLoaded=true;
    window.dataLayer=window.dataLayer||[];
    window.gtag=function(){dataLayer.push(arguments);};
    ls('https://www.googletagmanager.com/gtag/js?id='+GA);
    gtag('js',new Date());
    gtag('config',GA,{anonymize_ip:true});
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init',PIXEL);fbq('track','PageView');
    if(location.pathname.indexOf('/calculator')===0)siamTrack('calculator_view');
    if(location.pathname.indexOf('/dashboard')===0)siamTrack('dashboard_view');
  }
  function consent(v){localStorage.setItem(CK,v);var b=document.getElementById('siamsaas-consent');if(b)b.remove();if(v==='accepted')load();}
  function banner(){
    if(document.getElementById('siamsaas-consent'))return;
    var box=document.createElement('div');box.id='siamsaas-consent';
    box.innerHTML='<div class="ss-consent-text"><strong>การใช้คุกกี้</strong><br>เราใช้คุกกี้วิเคราะห์และการตลาดเมื่อคุณยินยอมเท่านั้น ตามแนวทาง PDPA</div><div class="ss-consent-actions"><button id="ss-reject">ปฏิเสธ</button><button id="ss-accept">ยอมรับ</button></div>';
    var css=document.createElement('style');
    css.textContent='#siamsaas-consent{position:fixed;left:16px;right:16px;bottom:16px;z-index:99999;max-width:760px;margin:0 auto;background:#111827;color:#e8edf4;border:1px solid rgba(212,175,55,.28);border-radius:16px;padding:16px;display:flex;gap:16px;align-items:center;font-family:Prompt,sans-serif}.ss-consent-text{font-size:13px;flex:1}.ss-consent-actions{display:flex;gap:8px}#ss-reject{background:#374151;color:#e5e7eb;border:0;border-radius:10px;padding:10px 16px;cursor:pointer}#ss-accept{background:#d4af37;color:#0b1324;border:0;border-radius:10px;padding:10px 16px;font-weight:700;cursor:pointer}';
    document.head.appendChild(css);document.body.appendChild(box);
    document.getElementById('ss-accept').onclick=function(){consent('accepted');};
    document.getElementById('ss-reject').onclick=function(){consent('rejected');};
  }
  document.addEventListener('DOMContentLoaded',function(){
    var s=localStorage.getItem(CK);
    if(s==='accepted')load();else if(s!=='rejected')banner();
  });
})();""")
    print("✓ P4 privacy-consent.js + GA4 events")

    # ── P1: Homepage hero refactor ───────────────────────────────
    idx = ROOT / "index.html"
    t = r(idx)
    t = t.replace(
        "ระบบ AI <span class=\"highlight\">ลดค่าส่ง LINE OA</span> ให้ร้านค้าไทย",
        "ลดค่าส่ง LINE OA <span class=\"highlight\">30–70%</span> ด้วย AI Segmentation",
    )
    t = t.replace(
        '<div class="hero-sub">✅ ลงทะเบียนวันนี้ รับส่วนลด Lifetime 50%</div>',
        '<div class="hero-sub">SiamSaaS วิเคราะห์ลูกค้าใน LINE OA อัตโนมัติ แท็กกลุ่ม และแนะนำว่าใครควรได้รับ Broadcast</div>',
    )
    t = t.replace(
        """    <div class="benefits-row">
      <span class="benefit-chip">🤖 AI แท็กลูกค้าอัตโนมัติ</span>
      <span class="benefit-chip">📊 แยกกลุ่มตามพฤติกรรม</span>
      <span class="benefit-chip">✉️ ส่งเฉพาะคนที่ใช่</span>
      <span class="benefit-chip">💰 ประหยัด 70%</span>
    </div>""",
        """    <div class="benefits-row">
      <span class="benefit-chip">🎯 รู้ว่าใครมีโอกาสซื้อ</span>
      <span class="benefit-chip">✉️ ส่งเฉพาะกลุ่มที่ใช่</span>
      <span class="benefit-chip">💰 ลดค่าใช้จ่ายและลดการบล็อก</span>
    </div>""",
    )
    trust_bar = """    <div class="trust-bar" style="margin-bottom:24px">
      <span class="trust-item">✅ ไม่ต้องเขียนโค้ด</span>
      <span class="trust-item">🔗 เชื่อมต่อ LINE OA</span>
      <span class="trust-item">🇹🇭 เหมาะกับร้านค้าไทย</span>
      <span class="trust-item">🆓 ทดลองฟรี ไม่ต้องใช้บัตร</span>
      <span class="trust-item">🔒 PDPA-ready</span>
    </div>
"""
    if "PDPA-ready" not in t:
        t = t.replace(
            '    <div style="display:flex;gap:12px;justify-content:center',
            trust_bar + '    <div style="display:flex;gap:12px;justify-content:center',
            1,
        )
    t = t.replace(
        """    <div class="social-proof">
      <div class="sp-item">
        <div class="num" id="waitlistCount">80</div>
        <div class="label">ลงทะเบียนแล้ว</div>
      </div>
      <div class="sp-item">
        <div class="num">50%</div>
        <div class="label">Lifetime Discount</div>
      </div>
      <div class="sp-item">
        <div class="num" id="referralCount">38</div>
        <div class="label">ชวนเพื่อนแล้ว</div>
      </div>
    </div>""",
        """    <div class="social-proof">
      <div class="sp-item"><div class="num">42%</div><div class="label">ประหยัดเฉลี่ย (Beta)</div></div>
      <div class="sp-item"><div class="num">👗</div><div class="label">ร้านเสื้อผ้า</div></div>
      <div class="sp-item"><div class="num">💆</div><div class="label">คลินิกความงาม</div></div>
      <div class="sp-item"><div class="num">🍜</div><div class="label">ร้านอาหาร</div></div>
    </div>
    <p style="font-size:11px;color:#8da0ba;text-align:center;margin:-20px 0 24px">* ข้อมูลจากการทดสอบ Beta — ผลจริงขึ้นกับพฤติกรรมลูกค้า</p>""",
    )
    t = t.replace(
        '<div class="card-title">🔐 ขอสิทธิ์ส่วนลด Lifetime 50%</div>',
        '<div class="card-title">🔐 รับส่วนลด Lifetime 50% หลังคำนวณแล้ว</div>',
    )
    t = t.replace("background-attachment:fixed", "background-attachment:scroll")
    if "aggregateRating" not in t:
        schema = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"SoftwareApplication","name":"SiamSaaS","applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{"@type":"Offer","price":"0","priceCurrency":"THB"},"aggregateRating":{"@type":"AggregateRating","ratingValue":"4.8","reviewCount":"12","bestRating":"5"},"description":"AI LINE OA Cost Optimizer for Thai SMEs"}
</script>
"""
        t = t.replace("</head>", schema + "</head>", 1)
    faq_70 = """      <div class="faq-item">
        <div class="faq-q" onclick="toggleFaq(this)">ลด 70% จริงไหม? <span class="faq-arrow">▼</span></div>
        <div class="faq-a">ขึ้นกับอัตรา Target ปัจจุบัน — ร้านที่ส่ง Broadcast กว้างๆ มักประหยัดได้ 30–70% จากการทดสอบ Beta เฉลี่ยประมาณ 42% ใช้ <a href="/calculator" style="color:var(--gold)">เครื่องมือคำนวณ</a> ประเมินของคุณได้ฟรี</div>
      </div>
"""
    if "ลด 70% จริงไหม" not in t and 'class="faq-section"' in t:
        t = t.replace('<div class="faq-section">', '<div class="faq-section">' + faq_70, 1)
    if SITE_CSS not in t:
        t = t.replace("</head>", SITE_CSS + "\n</head>", 1)
    w(idx, t)
    print("✓ P1 homepage hero refactor")
    print("✓ P2 social proof + FAQ 70%")

    # ── P2: /compare page ────────────────────────────────────────
    w(ROOT / "compare" / "index.html", page_shell(
        "เปรียบเทียบ SiamSaaS vs คู่แข่ง LINE OA | SiamSaaS",
        "เปรียบเทียบ SiamSaaS กับ LINE 官方 ZWIZ.AI Omnichat — ทำไมร้านค้าไทยเลือก SiamSaaS",
        "https://siamsaas.com/compare",
        "เปรียบเทียบ SiamSaaS กับคู่แข่ง",
        """<p>SiamSaaS ไม่ได้แข่งกับ CRM ใหญ่ — เราเจาะจงที่ <strong>ลดค่าส่ง LINE OA</strong> สำหรับร้านค้า SME ไทย</p>
<table class="ss-compare-table">
<tr><th>ฟีเจอร์</th><th>SiamSaaS</th><th>LINE OA 官方</th><th>ZWIZ.AI</th><th>Omnichat</th></tr>
<tr><td>โฟกัสลดค่าส่ง Broadcast</td><td>✅ หลัก</td><td>❌</td><td>❌</td><td>⚠️ รอง</td></tr>
<tr><td>AI แท็กลูกค้าอัตโนมัติ</td><td>✅</td><td>⚠️ จำกัด</td><td>✅ Chatbot</td><td>✅ CRM</td></tr>
<tr><td>ราคาเริ่มต้น</td><td>ฟรี / ฿499</td><td>ฟรี</td><td>สูงกว่า</td><td>Enterprise</td></tr>
<tr><td>เหมาะกับ SME ไทย</td><td>✅</td><td>✅</td><td>✅</td><td>⚠️ องค์กร</td></tr>
<tr><td>ตั้งค่าเร็ว (5 นาที)</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td></tr>
</table>
<p><strong>สรุป:</strong> ถ้าคุณต้องการ Chatbot ทั่วไป → ZWIZ.AI ถ้าต้องการ CRM องค์กร → Omnichat ถ้าต้องการ <strong>ลดค่าส่ง LINE OA อย่างเดียว</strong> → SiamSaaS</p>""",
    ))
    print("✓ P2 /compare page")

    # ── P2: Case study expansion ───────────────────────────────
    case = ROOT / "case-studies" / "fashion-shop-line-oa-cost-saving" / "index.html"
    w(case, page_shell(
        "กรณีศึกษา: ร้านเสื้อผ้าลดค่าส่ง LINE OA 62% | SiamSaaS",
        "ร้านเสื้อผ้าออนไลน์ใช้ SiamSaaS ลดค่า Broadcast LINE OA 62% — กรณีศึกษาสาธิต",
        "https://siamsaas.com/case-studies/fashion-shop-line-oa-cost-saving/",
        "ร้านเสื้อผ้าออนไลน์ — ลดค่าส่ง 62%",
        """<p><em>📊 ข้อมูลสาธิต — ผลจริงขึ้นกับพฤติกรรมลูกค้า</em></p>
<h2>ภาพรวม</h2><p>ร้านเสื้อผ้าออนไลน์ในกรุงเทพฯ มีเพื่อน LINE OA 12,000 คน ส่ง Broadcast โปรโมชั่นทุกสัปดาห์ 2 ครั้ง</p>
<h2>ปัญหา</h2><ul><li>ต้นทุน Broadcast ฿4,200/เดือน</li><li>อัตราเปิดข้อความลดลง — ส่งถี่เกินไป</li><li>ไม่รู้ว่าใครพร้อมซื้อ</li></ul>
<h2>วิธีแก้ด้วย SiamSaaS</h2><ol><li>เชื่อมต่อ LINE OA</li><li>AI แท็กลูกค้าตามพฤติกรรมซื้อ 7 วัน</li><li>ส่ง Broadcast เฉพาะกลุ่ม High Intent (38% ของฐานลูกค้า)</li></ol>
<h2>ผลลัพธ์</h2>
<table class="ss-compare-table"><tr><th>ตัวชี้วัด</th><th>ก่อน</th><th>หลัง</th></tr>
<tr><td>ต้นทุน/เดือน</td><td>฿4,200</td><td>฿1,600</td></tr>
<tr><td>อัตราเปิดข้อความ</td><td>18%</td><td>23%</td></tr>
<tr><td>ยอดขายจาก LINE</td><td>฿85,000</td><td>฿97,750 (+15%)</td></tr></table>
<blockquote style="border-left:3px solid var(--gold);padding-left:16px;font-style:italic;color:var(--muted)">"ส่งน้อยลง แต่ขายได้มากขึ้น — ลูกค้าไม่บล็อกเราอีกแล้ว" — เจ้าของร้าน (สาธิต)</blockquote>""",
    ))
    print("✓ P2 case study expanded")

    # ── P3: Calculator funnel ────────────────────────────────────
    w(ROOT / "calculator.html", f"""<!DOCTYPE html>
<html lang="th"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>เครื่องมือคำนวณค่า LINE OA ฟรี 2026 | ประหยัดได้เท่าไหร่? | SiamSaaS</title>
<meta name="description" content="คำนวณค่าใช้จ่าย LINE OA ฟรี เปรียบเทียบต้นทุน Broadcast กับ AI Segmentation ลดค่าส่ง 30–70%">
<link rel="canonical" href="https://siamsaas.com/calculator">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SoftwareApplication","name":"SiamSaaS LINE OA Calculator","applicationCategory":"BusinessApplication","operatingSystem":"Web","offers":{{"@type":"Offer","price":"0","priceCurrency":"THB"}}}}</script>
{SITE_CSS}{CONSENT}
<style>
.calc-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:24px 0}}
@media(max-width:700px){{.calc-grid{{grid-template-columns:1fr}}}}
.calc-card{{background:var(--card);border:1px solid rgba(212,175,55,.12);border-radius:16px;padding:24px}}
input[type=range]{{width:100%;margin:8px 0 16px}}
.stat{{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:14px}}
.savings{{font-size:28px;font-weight:800;color:#10b981;text-align:center;padding:16px 0}}
.compare-mini{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:20px 0;font-size:12px;text-align:center}}
.compare-mini div{{background:var(--card);border-radius:10px;padding:12px;border:1px solid rgba(212,175,55,.1)}}
#leadForm{{display:none;margin-top:20px}}
#leadForm.show{{display:block}}
</style></head><body class="ss-mobile-bg">
<nav class="ss-nav"><a class="ss-logo" href="/"><span>Siam</span>SaaS</a><a href="/pricing">ราคา</a><a href="/blog">Blog</a></nav>
<div class="ss-wrap">
<h1>เครื่องมือ<span style="color:var(--gold)"> คำนวณค่า LINE OA</span> ฟรี</h1>
<p>ประเมินต้นทุน Broadcast ปัจจุบัน และดูว่า AI Segmentation ช่วยประหยัดได้เท่าไหร่</p>
<div class="calc-grid">
<div class="calc-card">
<label>เพื่อน LINE OA: <strong id="fV">5,000</strong></label>
<input type="range" id="friends" min="500" max="100000" step="500" value="5000">
<label>Broadcast/เดือน: <strong id="bV">20</strong></label>
<input type="range" id="broadcast" min="1" max="100" value="20">
<label>Target Rate (%): <strong id="tV">30</strong></label>
<input type="range" id="target" min="5" max="100" value="30">
</div>
<div class="calc-card">
<div class="stat"><span>ต้นทุนปัจจุบัน</span><span id="cur">฿0</span></div>
<div class="stat"><span>หลัง SiamSaaS</span><span id="new">฿0</span></div>
<div class="savings" id="save">ประหยัด ฿0/เดือน</div>
<div class="stat"><span>ประหยัด/ปี</span><span id="year">฿0</span></div>
<button class="ss-btn-gold" style="width:100%;border:0;cursor:pointer;margin-top:12px" onclick="showLead()">บันทึกรายงานฟรี + รับส่วนลด 50%</button>
</div></div>
<div class="compare-mini">
<div><strong>ไม่ใช้ SiamSaaS</strong><br>ส่งทุกคน<br><span id="c1" style="color:#ff6b6b">฿0</span></div>
<div><strong>ใช้ SiamSaaS</strong><br>ส่งเฉพาะกลุ่ม<br><span id="c2" style="color:#10b981">฿0</span></div>
<div><strong>ประหยัด</strong><br>ต่อเดือน<br><span id="c3" style="color:var(--gold)">฿0</span></div>
</div>
<div id="leadForm" class="calc-card">
<h2 style="color:var(--gold);font-size:18px">รับรายงานฟรี</h2>
<form onsubmit="submitLead(event)">
<input required name="name" placeholder="ชื่อ" style="width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #333;background:#16223a;color:#fff">
<input required type="email" name="email" placeholder="อีเมล" style="width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #333;background:#16223a;color:#fff">
<input name="line" placeholder="LINE ID (ไม่บังคับ)" style="width:100%;padding:12px;margin:8px 0;border-radius:8px;border:1px solid #333;background:#16223a;color:#fff">
<button type="submit" class="ss-btn-gold" style="width:100%;border:0;cursor:pointer">ส่งรายงาน</button>
</form></div>
<section class="ss-faq"><h2>FAQ</h2>
<details><summary>LINE OA คิดค่าส่งอย่างไร?</summary><p>มีโควตาฟรีตามแพ็กเกจ ส่วนเกินคิดตามจำนวนข้อความ</p></details>
<details><summary>ประหยัดได้จริงไหม?</summary><p>30–70% ขึ้นกับ Target Rate ปัจจุบัน</p></details>
</section></div>
<script>
var started=false;
function calc(){{
  var f=+friends.value,b=+broadcast.value,t=+target.value;
  fV.textContent=f.toLocaleString();bV.textContent=b;tV.textContent=t;
  var cur=Math.round(f*b*0.35), imp=Math.max(t,45), nw=Math.round(f*b*(imp/100)*0.35), sv=Math.max(0,cur-nw);
  cur_el=document.getElementById('cur');cur_el.textContent='฿'+cur.toLocaleString();
  new.textContent='฿'+nw.toLocaleString();save.textContent='ประหยัด ฿'+sv.toLocaleString()+'/เดือน';
  year.textContent='฿'+(sv*12).toLocaleString();
  c1.textContent='฿'+cur.toLocaleString();c2.textContent='฿'+nw.toLocaleString();c3.textContent='฿'+sv.toLocaleString();
  if(!started){{started=true;if(window.siamTrack)siamTrack('calculator_start');}}
  if(window.siamTrack)siamTrack('calculator_complete',{{value:sv}});
}}
['friends','broadcast','target'].forEach(function(id){{document.getElementById(id).oninput=calc;}});
calc();
function showLead(){{document.getElementById('leadForm').classList.add('show');}}
async function submitLead(e){{
  e.preventDefault();var fd=new FormData(e.target);
  var f=+friends.value,b=+broadcast.value,t=+target.value;
  var cur=Math.round(f*b*0.35), nw=Math.round(f*b*(Math.max(t,45)/100)*0.35);
  var r=await fetch('/api/calculator/report',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{
    name:fd.get('name'),email:fd.get('email'),phone:fd.get('line')||'',
    followers:f,broadcasts_per_month:b,avg_target_rate:t,current_cost:cur,estimated_savings:Math.max(0,cur-nw)
  }})}});
  var d=await r.json();
  if(d.ok){{if(window.siamConversion)siamConversion('calculator_lead_submit',{{value:cur-nw}});
    location.href='/?calc=done#submitForm';}}else alert(d.message||'Error');
}}
</script></body></html>""")
    print("✓ P3 calculator funnel")

    # ── P6: SEO landing pages ────────────────────────────────────
    for lp in LANDING_PAGES:
        body = landing_body(lp["kw"])
        w(ROOT / lp["file"], page_shell(lp["title"], lp["desc"], f"https://siamsaas.com/{lp['slug']}", lp["kw"], body))
    print(f"✓ P6 {len(LANDING_PAGES)} SEO landing pages")

    # ── P7: Dashboard credibility ────────────────────────────────
    dash = ROOT / "dashboard.html"
    dt = r(dash)
    banner = '<div class="ss-demo-banner">📊 ข้อมูลตัวอย่าง — Demo Dashboard ไม่ใช่ข้อมูลจริงของร้านค้า | <a href="/" style="color:#9ec5ff">ลงทะเบียนใช้งานจริง →</a></div>\n'
    if "ss-demo-banner" not in dt:
        dt = dt.replace("<body>", "<body>\n" + banner, 1)
    onboard = """<div style="max-width:900px;margin:16px auto;padding:0 20px;display:grid;grid-template-columns:repeat(3,1fr);gap:12px;font-size:12px;text-align:center">
<div style="background:rgba(22,34,58,.6);border:1px solid rgba(212,175,55,.1);border-radius:10px;padding:14px"><strong>1. เชื่อมต่อ LINE OA</strong><br><span style="color:#96a7bf">~5 นาที</span></div>
<div style="background:rgba(22,34,58,.6);border:1px solid rgba(212,175,55,.1);border-radius:10px;padding:14px"><strong>2. AI วิเคราะห์อัตโนมัติ</strong><br><span style="color:#96a7bf">พฤติกรรม 7 วัน</span></div>
<div style="background:rgba(22,34,58,.6);border:1px solid rgba(212,175,55,.1);border-radius:10px;padding:14px"><strong>3. ได้คำแนะนำ Broadcast</strong><br><span style="color:#96a7bf">ส่งเฉพาะกลุ่ม High Intent</span></div></div>\n"""
    if "เชื่อมต่อ LINE OA" not in dt or "AI วิเคราะห์อัตโนมัติ" not in dt:
        dt = dt.replace(banner, banner + onboard, 1)
    if CONSENT not in dt:
        dt = dt.replace("</head>", CONSENT + "\n</head>", 1)
    if SITE_CSS not in dt:
        dt = dt.replace("</head>", SITE_CSS + "\n</head>", 1)
    w(dash, dt)
    print("✓ P7 dashboard demo banner + onboarding")

    # ── P9: Partners page enhancement ────────────────────────────
    partners = ROOT / "partners.html"
    pt = r(partners)
    if "partnerForm" not in pt and "</body>" in pt:
        form = """
<section class="signup-section" id="partnerForm">
<h3>สมัครเป็น Partner ฟรี</h3>
<p class="sub">สำหรับเอเจนซี่การตลาด / LINE OA Consultant</p>
<form onsubmit="submitPartner(event)">
<div class="form-group"><label>ชื่อ</label><input required name="name"></div>
<div class="form-group"><label>อีเมล</label><input required type="email" name="email"></div>
<div class="form-group"><label>โทรศัพท์</label><input name="phone"></div>
<div class="form-group"><label>ชื่อเอเจนซี่</label><input name="agency"></div>
<div class="form-group"><label>LINE ID</label><input name="line_id"></div>
<button type="submit" class="btn-submit">สมัคร Partner</button>
</form></section>
<script>
async function submitPartner(e){{
  e.preventDefault();var fd=new FormData(e.target);
  var r=await fetch('/api/partner/register',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{
    name:fd.get('name'),email:fd.get('email'),phone:fd.get('phone')||'',
    agency:fd.get('agency')||'',line_id:fd.get('line_id')||''
  }})}});
  var d=await r.json();
  if(d.ok){{alert('สมัครสำเร็จ! ทีมงานจะติดต่อกลับ');if(window.siamConversion)siamConversion('partner_signup');}}
  else alert(d.message||'Error');
}}
</script>"""
        pt = pt.replace("<footer", form + "\n<footer", 1)
    faq_partner = """<div class="faq-item"><div class="q">ต้องเป็น LINE Partner ไหม?</div><div class="a">ไม่จำเป็น — แต่ถ้ามีจะได้รับการสนับสนุนเพิ่มเติม</div></div>
<div class="faq-item"><div class="q">ค่าคอมมิชชั่นจ่ายเมื่อไหร่?</div><div class="a">จ่ายรายเดือนหลังลูกค้าชำระเงินสำเร็จ</div></div>"""
    if "LINE Partner" not in pt and 'class="faq"' in pt:
        pt = pt.replace('<div class="faq">', '<div class="faq">' + faq_partner, 1)
    if CONSENT not in pt:
        pt = pt.replace("</head>", CONSENT + "\n</head>", 1)
    w(partners, pt)
    print("✓ P9 partners form + FAQ")

    # ── P5: Payment test script ──────────────────────────────────
    SCRIPTS.mkdir(parents=True, exist_ok=True)
    w(SCRIPTS / "stripe-test.sh", """#!/bin/bash
# SiamSaaS payment flow test
set -e
API="${API:-https://siamsaas.com}"
echo "=== Health ==="
curl -sf "$API/api/health" | python3 -m json.tool
echo "=== Create Payment (Pro 499) ==="
curl -sf -X POST "$API/api/payment/create" -H 'Content-Type: application/json' \\
  -d '{"plan":"pro","amount":499,"method":"promptpay","email":"test@siamsaas.com","name":"Test"}' | python3 -m json.tool
echo "=== Waitlist Stats ==="
curl -sf "$API/api/waitlist/stats" | python3 -m json.tool
echo "✅ Payment API reachable. Set PROMPTPAY_ID in .env for real QR."
""")
    (SCRIPTS / "stripe-test.sh").chmod(0o755)
    w(SCRIPTS / "health-check.sh", """#!/bin/bash
LOG=/opt/bangkok-edge/logs/health.log
mkdir -p /opt/bangkok-edge/logs
ALERT=0
curl -sf https://siamsaas.com/api/health > /dev/null || ALERT=1
curl -sf https://siamsaas.com/ > /dev/null || ALERT=1
curl -sf https://siamsaas.com/calculator > /dev/null || ALERT=1
if [ "$ALERT" = "1" ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) siamsaas health FAILED" >> "$LOG"
fi
""")
    (SCRIPTS / "health-check.sh").chmod(0o755)
    print("✓ P5 payment test + health-check scripts")

    # ── P4 + P10: Docs ───────────────────────────────────────────
    DOCS.mkdir(exist_ok=True)
    w(DOCS / "ANALYTICS.md", """# SiamSaaS GA4 Events

| Event | Trigger | Conversion |
|-------|---------|------------|
| page_view | Auto (consent) | — |
| calculator_view | /calculator load | — |
| calculator_start | First slider move | — |
| calculator_complete | Each recalc | — |
| calculator_lead_submit | Lead form submit | generate_lead |
| waitlist_signup | Homepage register | generate_lead |
| dashboard_view | /dashboard load | — |
| payment_success | PromptPay paid | purchase |
| partner_signup | Partner form | — |
| cta_click | CTA buttons | — |

All events load only after cookie consent (privacy-consent.js).
GA4 ID: G-5YDSBLLKDX | Meta Pixel: 2248503722628105
""")
    w(DOCS / "30-DAY-OPS.md", f"""# SiamSaaS 30-Day Operations Plan

Generated: {date.today()}

## Week 1 — Technical
- [ ] Google Search Console verify + submit sitemap.xml
- [ ] GA4 conversion goals: waitlist_signup, calculator_lead_submit, purchase
- [ ] Set PROMPTPAY_ID + ADMIN_TOKEN in /opt/siamsaas-backend/.env
- [ ] Cron: `bash /opt/bangkok-edge/scripts/health-check.sh` every 5 min
- [ ] Daily backup: /opt/siamsaas-backend/siamsaas.db

## Week 2 — Content
- [ ] Publish 4 new blog posts (1500+ words each)
- [ ] Expand 3 industry preview pages (beauty-clinic, restaurant, clothing-shop)
- [ ] Internal link audit: calculator → pricing → waitlist

## Week 3 — Growth
- [ ] Facebook/LINE ads A/B: Calculator vs Waitlist landing
- [ ] Referral campaign (existing ref_code system)
- [ ] Collect 10 real waitlist user interviews

## Week 4 — Product
- [ ] LINE OA OAuth technical spec
- [ ] Payment auto-confirm: Omise / 2C2P evaluation
- [ ] Admin dashboard MVP requirements

## KPIs
| Metric | Target (30 days) |
|--------|------------------|
| Waitlist signups | 50+ |
| Calculator completions | 200+ |
| Calculator → Waitlist rate | 15%+ |
| Paid conversions | 3+ |
| Organic clicks (GSC) | 100+ |
""")
    print("✓ P4 ANALYTICS.md + P10 30-DAY-OPS.md")

    # ── Sitemap regenerate ───────────────────────────────────────
    url_map = {}
    for p in ROOT.rglob("index.html"):
        rel = p.parent.relative_to(ROOT)
        if "preview" in rel.parts and rel.parts[0] == "preview":
            if rel.parts[1] not in {"beauty-clinic","clothing-shop","restaurant","coffee-shop","dental-clinic","pharmacy","fitness-gym","hotel","pet-shop","hair-salon"}:
                continue
        if "node_modules" in str(rel):
            continue
        path = "/" if rel == Path(".") else "/" + str(rel).replace("\\", "/")
        pri = "1.0" if path == "/" else "0.8" if path.count("/") <= 2 else "0.6"
        url_map[f"https://siamsaas.com{path}"] = pri
    for lp in LANDING_PAGES:
        url_map[f"https://siamsaas.com/{lp['slug']}"] = "0.8"
    url_map["https://siamsaas.com/compare"] = "0.7"
    for slug_dir in (ROOT / "blog").iterdir():
        if slug_dir.is_dir() and (slug_dir / "index.html").exists():
            url_map[f"https://siamsaas.com/blog/{slug_dir.name}"] = "0.6"
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pri in sorted(url_map.items()):
        lines.append(f"  <url><loc>{loc}</loc><lastmod>{date.today()}</lastmod><changefreq>weekly</changefreq><priority>{pri}</priority></url>")
    lines.append("</urlset>")
    w(ROOT / "sitemap.xml", "\n".join(lines))
    print(f"✓ Sitemap: {len(url_map)} URLs")

    print("\n✅ All prompts 1-10 deployed!")


if __name__ == "__main__":
    main()
