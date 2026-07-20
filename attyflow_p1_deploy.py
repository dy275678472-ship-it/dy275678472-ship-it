#!/usr/bin/env python3
"""Attyflow P1 growth fixes — SEO, content, conversion."""
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path("/var/www/attyflow")
SRC = Path(__file__).resolve().parent / "attyflow-files"
NGINX_SITE = Path("/etc/nginx/sites-enabled/traffic-override.conf")
TODAY = date.today().isoformat()

HOWTO_SCHEMA = {
  "nda-clause-review": {
    "name": "How to review an NDA clause with Attyflow",
    "steps": [
      "Open the NDA Clause Review tool or sandbox.",
      "Select your client position: buyer, seller, or mutual.",
      "Paste the confidentiality or NDA clause into the text area.",
      "Click Run to receive a risk score and issue summary.",
      "Open the full sandbox for a negotiation-ready redline.",
    ],
  },
  "limitation-of-liability-checker": {
    "name": "How to check a limitation of liability clause",
    "steps": [
      "Open the Limitation of Liability Checker.",
      "Paste the liability cap or exclusion clause.",
      "Review flagged issues: uncapped damages, carveouts, asymmetry.",
      "Run the full sandbox for redline language.",
    ],
  },
  "indemnification-clause-checker": {
    "name": "How to review an indemnification clause",
    "steps": [
      "Open the Indemnification Clause Checker.",
      "Select buyer or seller position.",
      "Paste the indemnity clause and run the quick check.",
      "Upgrade to sandbox for full redline output.",
    ],
  },
}

BLOG_EXPANSIONS = {
  "contract-risk-scoring-models.html": """
<h2>Implementing risk scores in your review workflow</h2>
<p>Legal teams that adopt contract risk scoring should define three tiers aligned to escalation policy: green clauses proceed with associate markup only, yellow clauses require senior review, and red clauses trigger partner involvement or renegotiation. Attyflow's numeric scores map cleanly to this model — scores above 75 typically indicate indemnity, liability, or confidentiality language that diverges from market standard for the selected client position.</p>
<p>Calibration matters. Run ten historical clauses your team already classified through the sandbox and compare AI risk levels to your internal labels. Adjust playbook thresholds until false negatives on high-risk indemnities approach zero. Document the calibration in your firm's contract playbook so junior attorneys apply scores consistently.</p>
<h2>Common scoring pitfalls</h2>
<ul><li>Treating all contract types with identical thresholds (NDA vs MSA vs employment)</li><li>Ignoring client position — buyer-side risk differs from seller-side risk on the same clause</li><li>Skipping human review on medium scores that involve non-standard carveouts</li></ul>
""",
  "build-firm-contract-playbook.html": """
<h2>From partner preferences to machine-checkable rules</h2>
<p>The most effective contract playbooks translate partner judgment into repeatable checks: maximum liability caps by deal size, required indemnity reciprocity, mandatory confidentiality carveouts, and prohibited governing-law combinations. Attyflow accelerates playbook enforcement by scoring pasted clauses against these standards before human review.</p>
<p>Start with your five highest-volume agreement types. For each, list the ten clauses partners most often revise. Encode those as checklist items, then validate whether AI-assisted triage catches the same issues on a sample set of fifty historical contracts.</p>
<h2>Playbook maintenance cadence</h2>
<p>Review playbook rules quarterly after major deals close. When negotiation outcomes shift market position — for example, your firm starts accepting broader data-processing terms — update both the written playbook and the risk thresholds your team applies during AI-assisted first-pass review.</p>
""",
  "saas-contract-review-5-clauses.html": """
<h2>Deep dive: the five clauses that drive SaaS deal risk</h2>
<p>SaaS vendor agreements concentrate risk in data processing, service levels, limitation of liability, indemnification, and termination. In-house teams and outside counsel should review these clauses as a bundle because vendors often trade concessions in one area for tightening in another.</p>
<p><strong>Data processing:</strong> Verify subprocessors, breach notification timelines, and audit rights. <strong>SLAs:</strong> Check whether credits are the exclusive remedy. <strong>Liability:</strong> Confirm caps cover data breaches if indemnities do not. <strong>Indemnity:</strong> Scope IP infringement and data claims separately. <strong>Termination:</strong> Ensure data export and deletion obligations survive exit.</p>
<p>Run each clause through Attyflow's free checkers or sandbox with vendor-side position selected to surface asymmetry before signature.</p>
""",
  "ai-contract-review-managing-partner-guide.html": """
<h2>Managing partner checklist for AI contract tools</h2>
<p>Before approving firm-wide AI contract review adoption, managing partners should require: (1) a written no-training data policy, (2) attorney-in-the-loop workflow documentation, (3) malpractice carrier notification if required, (4) client disclosure language for AI-assisted review, and (5) a pilot on twenty live matters with outcome tracking.</p>
<p>Measure success by time-to-first-markup, partner revision rate on AI-suggested redlines, and client escalation frequency — not by raw volume of AI-generated text.</p>
""",
  "ai-redlining-midsize-law-firms.html": """
<h2>Redlining workflow for midsize transactional teams</h2>
<p>Midsize firms often bottleneck on partner review capacity. AI redlining tools should slot between associate first-pass and partner final approval — never replacing partner sign-off. Assign associates to run clause batches through risk scoring overnight; partners receive a prioritized issues list ranked by score each morning.</p>
<p>Standardize redline format: issue summary, proposed language, fallback position, and business rationale. Attyflow's output maps to this structure, reducing partner time spent reformatting associate work product.</p>
""",
}


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


def inject_howto_schema(tool_slug: str) -> None:
    path = ROOT / "tools" / tool_slug / "index.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if "HowTo" in text:
        return
    meta = HOWTO_SCHEMA[tool_slug]
    steps_json = ",\n    ".join(
        f'{{"@type": "HowToStep", "position": {i+1}, "name": "{s}"}}'
        for i, s in enumerate(meta["steps"])
    )
    schema = f'''<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "{meta["name"]}",
  "step": [
    {steps_json}
  ]
}}</script>'''
    text = text.replace("</head>", schema + "\n</head>", 1)
    if "sticky-cta.js" not in text:
        sticky = '<div class="sticky-cta" id="sticky-cta" hidden><span>3 free clause audits</span><a class="btn btn-gold" href="/taskpane.html">Try Free</a></div>\n'
        text = text.replace("<footer", sticky + "<footer", 1)
        text = text.replace("</body>", '<script src="/assets/sticky-cta.js" defer></script>\n</body>')
    if "site-p1.css" not in text:
        text = text.replace('href="/assets/site.css">', 'href="/assets/site.css">\n<link rel="stylesheet" href="/assets/site-p1.css">')
    path.write_text(text, encoding="utf-8")
    print(f"  HowTo schema: tools/{tool_slug}")


def expand_blogs() -> int:
    marker = '<section class="attyflow-eat"'
    count = 0
    for filename, block in BLOG_EXPANSIONS.items():
        path = ROOT / "blog" / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "P1 expansion" in text:
            continue
        if marker not in text:
            continue
        wrapped = f'<!-- P1 expansion -->\n{block}\n'
        text = text.replace(marker, wrapped + marker, 1)
        if '"@type": "Article"' not in text:
            article_schema = '''<script type="application/ld+json">{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "''' + filename.replace(".html", "").replace("-", " ").title() + '''",
  "author": {"@type": "Organization", "name": "Attyflow"},
  "publisher": {"@type": "Organization", "name": "Attyflow", "logo": {"@type": "ImageObject", "url": "https://attyflow.com/og-image.png"}}
}</script>'''
            text = text.replace("</head>", article_schema + "\n</head>", 1)
        path.write_text(text, encoding="utf-8")
        count += 1
    print(f"  expanded {count} blog posts")
    return count


def update_sitemap() -> None:
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    entries = [
        ("https://attyflow.com/compare/legalon-alternative/", "0.8"),
        ("https://attyflow.com/best-ai-contract-review-2026/", "0.9"),
    ]
    for url, pri in entries:
        if url not in text:
            text = text.replace(
                "</urlset>",
                f'  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod><priority>{pri}</priority></url>\n</urlset>',
            )
    for slug in ["spellbook-alternative", "legalon-alternative"]:
        text = re.sub(
            rf"(<loc>https://attyflow.com/compare/{slug}/</loc><lastmod>)[^<]+",
            rf"\g<1>{TODAY}",
            text,
        )
    sitemap.write_text(text, encoding="utf-8")
    print("  updated sitemap.xml")


def update_compare_index() -> None:
    copy_src("compare/index.html") if (SRC / "compare/index.html").exists() else None
    path = ROOT / "compare/index.html"
    text = path.read_text(encoding="utf-8")
    cards = [
        ('harvey-alternative', 'Harvey AI Alternative', 'Enterprise AI vs focused contract review.'),
        ('legalon-alternative', 'LegalOn Alternative', 'In-house CLM vs small-firm contract review.'),
    ]
    for slug, title, desc in cards:
        card = f'<a class="card" href="/compare/{slug}/"><h3>{title}</h3><p>{desc}</p></a>'
        if slug not in text:
            text = text.replace("</div></main>", card + "</div></main>")
    best_card = '<a class="card" href="/best-ai-contract-review-2026/"><h3>Best AI Contract Review 2026</h3><p>Full tool comparison for small firms and legal ops.</p></a>'
    if "best-ai-contract-review" not in text:
        text = text.replace("</div></main>", best_card + "</div></main>")
    path.write_text(text, encoding="utf-8")
    print("  updated compare/index.html")


def generate_webp() -> None:
    try:
        from PIL import Image
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "pillow", "-q"], check=True)
        from PIL import Image

    for name in ["icon-32.png", "icon-80.png", "og-image.png"]:
        src = ROOT / "assets" / name if name != "og-image.png" else ROOT / name
        if not src.exists():
            src = ROOT / name
        if not src.exists():
            continue
        dst = src.with_suffix(".webp")
        Image.open(src).save(dst, "WEBP", quality=85)
        print(f"  webp: {dst.name} ({dst.stat().st_size} bytes)")


def nginx_cache_headers() -> None:
    marker = "# attyflow-static-cache"
    if marker in NGINX_SITE.read_text(encoding="utf-8"):
        print("  nginx cache headers already set")
        return
    block = f'''
    {marker}
    location ~* \\.(css|js|png|webp|svg|ico)$ {{
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }}
'''
    text = NGINX_SITE.read_text(encoding="utf-8")
    anchor = "# include /etc/nginx/affiliate-attyflow.conf; # disabled P0 growth"
    if anchor in text and marker not in text:
        text = text.replace(anchor, block + "        " + anchor)
        NGINX_SITE.write_text(text, encoding="utf-8")
        subprocess.run(["sudo", "nginx", "-t"], check=True)
        subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True)
        print("  added nginx static cache headers")
    else:
        print("  nginx cache: skipped or already configured")


def inject_sticky_on_pages() -> None:
    pages = ["product.html", "pricing.html", "sample-redline-report.html"]
    for rel in pages:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        changed = False
        if "sticky-cta.js" not in text:
            if 'id="sticky-cta"' not in text:
                text = text.replace("<footer", '<div class="sticky-cta" id="sticky-cta" hidden><span>3 free clause audits</span><a class="btn btn-gold" href="/taskpane.html">Try Free</a></div>\n<footer')
            text = text.replace("</body>", '<script src="/assets/sticky-cta.js" defer></script>\n</body>')
            changed = True
        if "site-p1.css" not in text:
            text = text.replace('href="/assets/site.css">', 'href="/assets/site.css">\n<link rel="stylesheet" href="/assets/site-p1.css">')
            changed = True
        if changed:
            path.write_text(text, encoding="utf-8")
            print(f"  sticky CTA: {rel}")


def main() -> None:
    print("Attyflow P1 deploy")
    copy_src("index.html")
    copy_src("assets/sticky-cta.js")
    copy_src("assets/site-p1.css")
    copy_src("compare/spellbook-alternative/index.html")
    copy_src("compare/legalon-alternative/index.html")
    copy_src("best-ai-contract-review-2026/index.html")
    copy_src("tools/attyflow_indexnow.py")
    for slug in HOWTO_SCHEMA:
        inject_howto_schema(slug)
    expand_blogs()
    update_compare_index()
    update_sitemap()
    inject_sticky_on_pages()
    generate_webp()
    nginx_cache_headers()  # no-op if already configured on server
    # IndexNow — new P1 URLs only
    import urllib.request, json
    key = (ROOT / "indexnow-key.txt").read_text().strip()
    urls = [
        "https://attyflow.com/",
        "https://attyflow.com/compare/spellbook-alternative/",
        "https://attyflow.com/compare/legalon-alternative/",
        "https://attyflow.com/best-ai-contract-review-2026/",
        "https://attyflow.com/tools/nda-clause-review/",
    ]
    payload = json.dumps({"host": "attyflow.com", "key": key, "urlList": urls}).encode()
    for ep in ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow"]:
        try:
            req = urllib.request.Request(ep, data=payload, method="POST", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                print(f"  IndexNow {ep}: {r.status}")
        except Exception as e:
            print(f"  IndexNow failed: {e}")
    print("P1 deploy complete")


if __name__ == "__main__":
    main()
