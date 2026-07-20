#!/usr/bin/env python3
"""Attyflow P0 growth fixes — deploy to /var/www/attyflow on production server."""
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path("/var/www/attyflow")
SRC = Path(__file__).resolve().parent / "attyflow-files"
NGINX_CONF = Path("/etc/nginx/sites-enabled/traffic-override.conf")
TODAY = date.today().isoformat()


def write(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {rel}")


def copy_src(rel: str) -> None:
    src = SRC / rel
    dst = ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  copied {rel}")


def disable_nginx_affiliate() -> None:
    text = NGINX_CONF.read_text(encoding="utf-8")
    needle = "include /etc/nginx/affiliate-attyflow.conf;"
    replacement = "# include /etc/nginx/affiliate-attyflow.conf; # disabled P0 growth"
    if needle in text:
        text = text.replace(needle, replacement)
        NGINX_CONF.write_text(text, encoding="utf-8")
        subprocess.run(["sudo", "nginx", "-t"], check=True)
        subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True)
        print("  disabled nginx affiliate-attyflow.conf")
    elif replacement in text:
        print("  nginx affiliate already disabled")
    else:
        print("  WARN: affiliate-attyflow include not found in nginx config")


def remove_blog_affiliate_ctas() -> int:
  patterns = [
    re.compile(
      r'<div style="margin:30px 0;padding:24px;background:linear-gradient\(135deg,#0f172a,#1e293b\).*?'
      r'/go/clio\.php.*?</div>\s*</div>',
      re.DOTALL,
    ),
    re.compile(
      r'<div class="cta-box" style="background:linear-gradient\(135deg,#0f172a,#1e293b\).*?'
      r'/go/clio\.php.*?</div>',
      re.DOTALL,
    ),
    re.compile(r'<div[^>]*>.*?/go/clio\.php.*?</div>', re.DOTALL),
  ]
  count = 0
  for path in (ROOT / "blog").glob("*.html"):
    text = path.read_text(encoding="utf-8")
    orig = text
    for pattern in patterns:
      text = pattern.sub("", text)
    if text != orig:
      path.write_text(text, encoding="utf-8")
      count += 1
  print(f"  removed Clio affiliate blocks from {count} blog posts")
  return count


def update_og_image_refs() -> int:
  count = 0
  for path in ROOT.rglob("*.html"):
    text = path.read_text(encoding="utf-8")
    if "og-image.svg" in text:
      text = text.replace("og-image.svg", "og-image.png")
      path.write_text(text, encoding="utf-8")
      count += 1
  print(f"  updated og-image refs in {count} html files")
  return count


def generate_og_png() -> None:
  try:
    from PIL import Image, ImageDraw, ImageFont
  except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "pillow", "-q"], check=True)
    from PIL import Image, ImageDraw, ImageFont

  w, h = 1200, 630
  img = Image.new("RGB", (w, h), "#0A0F1A")
  draw = ImageDraw.Draw(img)
  draw.rectangle([(0, 0), (w, 120)], fill="#0F172A")
  draw.rectangle([(80, 180), (1120, 182)], fill="#D4A853")
  try:
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 72)
    sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    tag_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
  except OSError:
    title_font = ImageFont.load_default()
    sub_font = ImageFont.load_default()
    tag_font = ImageFont.load_default()

  draw.text((80, 240), "ATTYFLOW", fill="#F8FAFC", font=title_font)
  draw.text((80, 340), "AI Contract Review & Redlines", fill="#94A3B8", font=sub_font)
  draw.text((80, 400), "Risk scores · Loophole analysis · Word-native workflow", fill="#64748B", font=tag_font)
  draw.rounded_rectangle([(80, 480), (420, 560)], radius=12, fill="#D4A853")
  draw.text((110, 505), "Try Free Clause Audit", fill="#0F172A", font=tag_font)
  out = ROOT / "og-image.png"
  img.save(out, "PNG", optimize=True)
  print(f"  generated {out} ({out.stat().st_size} bytes)")


def update_sitemap() -> None:
  sitemap = ROOT / "sitemap.xml"
  text = sitemap.read_text(encoding="utf-8")
  entry = f'  <url><loc>https://attyflow.com/compare/harvey-alternative/</loc><lastmod>{TODAY}</lastmod><priority>0.8</priority></url>\n'
  if "harvey-alternative" not in text:
    text = text.replace("</urlset>", entry + "</urlset>")
    sitemap.write_text(text, encoding="utf-8")
    print("  added harvey-alternative to sitemap")
  spellbook_marker = "spellbook-vs-attyflow"
  text = sitemap.read_text(encoding="utf-8")
  text = re.sub(
    rf'(<loc>https://attyflow.com/compare/{spellbook_marker}/</loc><lastmod>)[^<]+',
    rf"\g<1>{TODAY}",
    text,
  )
  sitemap.write_text(text, encoding="utf-8")


def update_compare_index() -> None:
  path = ROOT / "compare/index.html"
  text = path.read_text(encoding="utf-8")
  card = '''<a class="card" href="/compare/harvey-alternative/"><h3>Harvey AI Alternative</h3><p>Enterprise AI vs focused contract review for small firms and legal ops.</p></a>'''
  if "harvey-alternative" not in text:
    text = text.replace("</div></main>", card + "</div></main>")
    path.write_text(text, encoding="utf-8")
    print("  updated compare index")


def customers_page() -> None:
  content = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, follow">
<title>Attyflow Pilot Program | Early Access for Law Firms</title>
<meta name="description" content="Join the Attyflow pilot program for early access to AI contract review workflows.">
<link rel="canonical" href="https://attyflow.com/customers">
<link rel="icon" href="/assets/icon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/icon-80.png">
<meta property="og:title" content="Attyflow Pilot Program">
<meta property="og:description" content="Early access for law firms evaluating AI contract review.">
<meta property="og:image" content="https://attyflow.com/og-image.png">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<header class="nav-wrap">
  <nav class="nav">
    <a class="logo" href="/">ATTYFLOW</a>
    <button class="nav-toggle" aria-label="Toggle navigation" onclick="document.body.classList.toggle('nav-open')">☰</button>
    <div class="nav-links">
      <a href="/product">Product</a>
      <a href="/tools/nda-clause-review/">Free Tools</a>
      <a href="/sample-redline-report">Sample Report</a>
      <a href="/security">Security</a>
      <a href="/blog/">Blog</a>
      <a href="/pricing" class="nav-cta">Pricing</a>
    </div>
  </nav>
</header>
<main class="article">
  <h1>Attyflow pilot program</h1>
  <p class="lead">We are recruiting small law firms and legal ops teams for structured pilot partnerships. Real workflows, measurable time savings, and approved case studies — no fabricated testimonials.</p>
  <div class="grid-2">
    <div class="card"><h3>Who should apply</h3><ul><li>Solo attorneys and boutiques reviewing 10+ contracts/month</li><li>Legal ops teams triaging vendor NDAs and MSAs</li><li>Firms evaluating AI contract review before firm-wide rollout</li></ul></div>
    <div class="card"><h3>What pilots receive</h3><ul><li>Extended sandbox access during evaluation</li><li>Onboarding call and playbook setup guidance</li><li>Priority support and product feedback channel</li><li>Discounted Solo or Team pricing for 90 days</li></ul></div>
  </div>
  <h2>How it works</h2>
  <ol>
    <li>Run your first clause audit in the <a href="/taskpane.html">sandbox</a>.</li>
    <li>Apply via <a href="/contact?plan=pilot">contact form</a> with your firm size and contract types.</li>
    <li>Complete a 2-week workflow trial with 5–10 real clauses.</li>
    <li>Optional: approved case study published on this page.</li>
  </ol>
  <div class="cta-box">
    <h2 style="text-align:left;color:#fff">Apply for pilot access</h2>
    <p>Limited spots for Q3 2026. Tell us your contract volume and primary use case.</p>
    <a class="btn btn-gold" href="/contact?plan=pilot">Request Pilot Access</a>
  </div>
</main>
<footer class="site-footer">
  <div class="footer-grid">
    <div><strong>ATTYFLOW</strong><p>AI contract risk review and redline workflow for lawyers who live in Microsoft Word.</p></div>
    <div><h4>Product</h4><a href="/product">AI Contract Review</a><a href="/pricing">Pricing</a></div>
    <div><h4>Resources</h4><a href="/tools/nda-clause-review/">NDA Checker</a><a href="/blog/">Blog</a></div>
    <div><h4>Trust</h4><a href="/security">Security</a><a href="/contact">Contact</a></div>
  </div>
  <p class="copyright">© 2026 Attyflow. Built for US common-law contract workflows.</p>
</footer>
<script src="/tracker.js" defer></script>
</body>
</html>'''
  write("customers.html", content)
  customers_dir = ROOT / "customers"
  if customers_dir.is_dir():
    (customers_dir / "index.html").write_text(content, encoding="utf-8")
    print("  wrote customers/index.html")


def pricing_page() -> None:
  path = ROOT / "pricing.html"
  text = path.read_text(encoding="utf-8")
  text = text.replace(
    '<a class="btn btn-gold" href="/contact?plan=solo">Request Solo Access</a>',
    '<a class="btn btn-gold" id="solo-cta" href="/contact?plan=solo">Subscribe Solo — $69/mo</a>',
  )
  text = text.replace(
    '<a class="btn btn-primary" href="/contact?plan=team">Book Team Demo</a>',
    '<a class="btn btn-primary" id="team-cta" href="/contact?plan=team">Subscribe Team — $249/mo</a>',
  )
  faq_old = "<h3>Why no live Stripe link here?</h3><p>The previous package contained third-party branded checkout URLs. They were removed to avoid payment and trust problems. Add your own Attyflow Stripe Payment Links before launch.</p>"
  faq_new = "<h3>How do I subscribe?</h3><p>Solo and Team plans use Stripe checkout when configured. If checkout is unavailable, use the contact form and we will activate your account within one business day.</p>"
  text = text.replace(faq_old, faq_new)
  if "stripe-pricing.js" not in text:
    text = text.replace("</body>", '<script src="/assets/stripe-pricing.js" defer></script>\n</body>')
  path.write_text(text, encoding="utf-8")
  print("  updated pricing.html")


def stripe_assets() -> None:
  write(
    "assets/stripe-config.json",
    '{\n  "solo": "",\n  "team": ""\n}\n',
  )
  write(
    "assets/stripe-pricing.js",
    """(function () {
  fetch('/assets/stripe-config.json')
    .then(function (r) { return r.json(); })
    .then(function (cfg) {
      var solo = document.getElementById('solo-cta');
      var team = document.getElementById('team-cta');
      if (solo && cfg.solo) { solo.href = cfg.solo; solo.textContent = 'Subscribe Solo — $69/mo'; }
      if (team && cfg.team) { team.href = cfg.team; team.textContent = 'Subscribe Team — $249/mo'; }
    })
    .catch(function () {});
})();""",
  )


def submit_indexnow() -> None:
  key_path = ROOT / "indexnow-key.txt"
  if not key_path.exists():
    print("  skip IndexNow: no key file")
    return
  key = key_path.read_text(encoding="utf-8").strip()
  urls = [
    "https://attyflow.com/",
    "https://attyflow.com/pricing",
    "https://attyflow.com/compare/spellbook-vs-attyflow/",
    "https://attyflow.com/compare/harvey-alternative/",
    "https://attyflow.com/customers",
  ]
  import json
  import urllib.request

  payload = json.dumps({"host": "attyflow.com", "key": key, "urlList": urls}).encode()
  for endpoint in [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
  ]:
    try:
      req = urllib.request.Request(endpoint, data=payload, method="POST", headers={"Content-Type": "application/json"})
      with urllib.request.urlopen(req, timeout=15) as resp:
        print(f"  IndexNow {endpoint}: {resp.status}")
    except Exception as e:
      print(f"  IndexNow {endpoint} failed: {e}")


def main() -> None:
  print("Attyflow P0 deploy")
  disable_nginx_affiliate()
  copy_src("compare/spellbook-vs-attyflow/index.html")
  copy_src("compare/harvey-alternative/index.html")
  customers_page()
  pricing_page()
  stripe_assets()
  generate_og_png()
  update_og_image_refs()
  remove_blog_affiliate_ctas()
  update_compare_index()
  update_sitemap()
  submit_indexnow()
  print("P0 deploy complete")


if __name__ == "__main__":
  main()
