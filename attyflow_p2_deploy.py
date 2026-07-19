#!/usr/bin/env python3
"""Attyflow P2 growth — content clusters, E-E-A-T, launch assets, blog depth."""
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path("/var/www/attyflow")
SRC = Path(__file__).resolve().parent / "attyflow-files"
TODAY = date.today().isoformat()
MARKER = '<section class="attyflow-eat"'

BLOG_P2 = {
  "ai-contract-review-2026.html": """
<h2>2026 adoption checklist for managing partners</h2>
<p>Before firm-wide rollout, require a 30-day pilot on live NDAs and MSAs with tracked metrics: minutes to first markup, partner revision rate, and client escalation count. Attyflow fits the pilot model with a no-credit-card sandbox and published Solo pricing.</p>
<h2>Vendor evaluation scorecard</h2>
<p>Score each tool 1–5 on: trial access, Word integration, position-aware review, redline quality, pricing transparency, and security documentation. Weight trial access and redline quality highest for transactional teams.</p>
""",
  "transactional-law-ai-adoption.html": """
<h2>Phased rollout for transactional practices</h2>
<p>Phase 1: NDA and mutual confidentiality agreements. Phase 2: vendor MSAs and SaaS orders. Phase 3: customer paper and non-standard indemnities. Each phase should have playbook thresholds and a defined partner escalation path for scores above 75.</p>
""",
  "limitation-liability-tech-contracts.html": """
<h2>Tech contract liability caps: market norms</h2>
<p>B2B SaaS agreements often cap direct damages at 12 months of fees paid, with negotiated super-caps for data breach and IP indemnity claims. Flag uncapped liability, consequential damages exposure, and carveouts that swallow the cap. Use the <a href="/tools/limitation-of-liability-checker/">free liability checker</a> for instant triage.</p>
""",
  "audit-nda-against-playbook-word.html": """
<h2>Playbook alignment in Word</h2>
<p>Export your firm's NDA positions as a one-page checklist: definition scope, term, residuals, injunctive relief, governing law. Run each counterparty clause through risk scoring and map HIGH items to specific playbook fallbacks before partner review.</p>
""",
  "playbook-driven-contract-review-partners.html": """
<h2>Partner sign-off on playbook deviations</h2>
<p>Document three fallback tiers per clause type: preferred, acceptable, and walk-away. AI triage should label which tier a counterparty draft triggers — not replace partner judgment on walk-away calls.</p>
""",
  "midsize-firms-compete-biglaw-ai.html": """
<h2>Competitive leverage for midsize firms</h2>
<p>Midsize transactional teams win on responsiveness. AI-assisted first-pass review lets boutiques return marked NDAs same-day while maintaining partner quality control on flagged clauses only.</p>
""",
  "contract-review-roi-billable-hours.html": """
<h2>Measuring billable hour impact</h2>
<p>Track pre- and post-adoption hours per contract type for 60 days. Firms typically see 25–45% reduction in associate first-pass time on standard NDAs and vendor MSAs. Use the <a href="/roi-calculator/">ROI calculator</a> to model your practice.</p>
""",
  "small-law-firm-technology.html": """
<h2>Tech stack priority for solos</h2>
<p>For solos reviewing 15+ contracts monthly, contract AI ROI often exceeds practice management upgrades. Start with a sandbox trial on your highest-volume agreement type before annual software commitments.</p>
""",
  "legal-playbook-automation-guide.html": """
<h2>Automating playbook checks</h2>
<p>Convert playbook rules into machine-checkable patterns: maximum liability multiples, required mutual indemnity, prohibited governing law. Attyflow risk scores surface deviations for attorney validation — automation assists, never replaces, legal judgment.</p>
""",
}

GLOSSARY_TERMS = [
  ("AI contract review", "Software that analyzes contract clauses for risk, often producing scores, issue summaries, and suggested redlines."),
  ("Contract redlining", "The process of marking proposed edits in a contract draft during negotiation."),
  ("Contract risk scoring", "A structured method for ranking clause risk by severity and negotiation exposure."),
  ("Redline-ready language", "Suggested replacement text that can be inserted into a draft after attorney review."),
  ("Contract playbook", "A set of preferred positions, fallbacks, and escalation rules for contract review."),
  ("CLM", "Contract Lifecycle Management — software for intake, approval, storage, and obligation tracking."),
  ("Limitation of liability", "A clause capping or excluding categories of damages between parties."),
  ("Indemnification", "A promise to compensate the other party for specified third-party claims or losses."),
  ("Mutual NDA", "A confidentiality agreement binding both parties to protect shared information."),
  ("Residual knowledge", "Information retained in unaided memory after exposure, often carved out of NDAs."),
  ("MSA", "Master Services Agreement governing an ongoing commercial relationship."),
  ("SaaS agreement", "Contract for cloud software subscription including data, SLA, and liability terms."),
  ("Termination for convenience", "A party's right to end a contract without cause, subject to notice and fees."),
  ("Legal ops", "The function managing legal department processes, technology, and outside counsel."),
  ("Word add-in", "A software extension that runs inside Microsoft Word."),
  ("E-E-A-T", "Experience, Expertise, Authoritativeness, Trust — quality signals for published content."),
  ("Common law", "Legal system based on case precedent; primary framework for US commercial contracts."),
  ("Injunctive relief", "Court order requiring or prohibiting specific conduct, often sought for confidentiality breaches."),
  ("Super-cap", "A liability limit higher than the standard cap for specified high-risk claims."),
  ("Triage", "Prioritizing items by urgency or risk for efficient review."),
  ("First-pass review", "Initial attorney or paralegal review before senior or partner approval."),
  ("Fallback position", "A secondary negotiating position when preferred language is rejected."),
  ("Data processing agreement", "Contract governing how a vendor processes personal or confidential data."),
  ("SOC 2", "Audit framework for service organization security controls."),
  ("No-training policy", "A vendor commitment not to use customer data to train AI models."),
]

NEW_SITEMAP_URLS = [
  ("https://attyflow.com/compare/ironclad-alternative/", "0.8"),
  ("https://attyflow.com/roi-calculator/", "0.8"),
  ("https://attyflow.com/use-cases/nda-review/", "0.8"),
  ("https://attyflow.com/use-cases/saas-vendor-contracts/", "0.8"),
  ("https://attyflow.com/clauses/nda-red-flags/", "0.7"),
  ("https://attyflow.com/clauses/termination-for-convenience-red-flags/", "0.7"),
  ("https://attyflow.com/editorial-standards", "0.6"),
  ("https://attyflow.com/product-hunt/", "0.5"),
]


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


def glossary_html() -> str:
    items = "\n".join(
        f'<div class="glossary-item"><dt>{t}</dt><dd>{d}</dd></div>' for t, d in GLOSSARY_TERMS
    )
    schema = '<script type="application/ld+json">{"@context":"https://schema.org","@type":"DefinedTermSet","name":"Legal AI Glossary"}</script>'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow">
<title>Legal AI Glossary (25 Terms) | Attyflow</title>
<meta name="description" content="Legal AI glossary: contract review, redlining, CLM, indemnity, liability caps, and 20 more terms for legal ops teams.">
<link rel="canonical" href="https://attyflow.com/legal-ai-glossary">
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/site-p2.css">
<meta property="og:image" content="https://attyflow.com/og-image.png">
{schema}
</head>
<body>
<header class="nav-wrap"><nav class="nav"><a class="logo" href="/">ATTYFLOW</a><div class="nav-links"><a href="/blog/">Blog</a><a href="/editorial-standards">Editorial</a><a href="/pricing" class="nav-cta">Pricing</a></div></nav></header>
<main class="article">
<h1>Legal AI glossary</h1>
<p class="lead">25 definitions for legal AI buyers, contract reviewers, and legal ops teams. <a href="/editorial-standards">Editorial standards</a>.</p>
<div class="glossary-grid">{items}</div>
<div class="cta-box"><h2 style="color:#fff">Apply terms in practice</h2><a class="btn btn-gold" href="/taskpane.html">Open Sandbox</a></div>
</main>
<footer class="site-footer"><p class="copyright">© 2026 Attyflow.</p></footer>
<script src="/tracker.js" defer></script>
</body>
</html>'''


def expand_blogs_p2() -> int:
    count = 0
    for filename, block in BLOG_P2.items():
        path = ROOT / "blog" / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "P2 expansion" in text or MARKER not in text:
            continue
        wrapped = f"<!-- P2 expansion -->\n{block}\n"
        text = text.replace(MARKER, wrapped + MARKER, 1)
        path.write_text(text, encoding="utf-8")
        count += 1
    print(f"  expanded {count} blog posts (P2)")
    return count


def update_clauses_index() -> None:
    path = ROOT / "clauses/index.html"
    text = path.read_text(encoding="utf-8")
    cards = [
        ('/clauses/nda-red-flags/', 'NDA red flags', 'Confidentiality scope, residuals, term.'),
        ('/clauses/termination-for-convenience-red-flags/', 'Termination for convenience', 'Notice, fees, data return.'),
    ]
    for href, title, desc in cards:
        slug = href.strip('/').split('/')[-1]
        if slug not in text:
            card = f'<a class="card" href="{href}"><h3>{title}</h3><p>{desc}</p></a>'
            text = text.replace("</div></main>", card + "</div></main>")
    use = '<p><a href="/use-cases/nda-review/">NDA use case</a> · <a href="/use-cases/saas-vendor-contracts/">SaaS vendor use case</a></p>'
    if "use-cases" not in text:
        text = text.replace('<div class="grid-2">', use + '<div class="grid-2">')
    path.write_text(text, encoding="utf-8")
    print("  updated clauses/index.html")


def update_sitemap() -> None:
    text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for url, pri in NEW_SITEMAP_URLS:
        if url not in text:
            text = text.replace(
                "</urlset>",
                f'  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod><priority>{pri}</priority></url>\n</urlset>',
            )
    (ROOT / "sitemap.xml").write_text(text, encoding="utf-8")
    print("  updated sitemap.xml")


def update_llms_txt() -> None:
    content = """# Attyflow
Attyflow is AI contract risk review and redline workflow software for US common-law legal teams.

Core pages:
- /product
- /pricing
- /tools/nda-clause-review/
- /sample-redline-report
- /security
- /best-ai-contract-review-2026/
- /roi-calculator/
- /compare/ironclad-alternative/
- /use-cases/nda-review/
- /editorial-standards

Important disclaimer: Attyflow is not a law firm and does not provide legal advice.
"""
    write("llms.txt", content)


def enhance_newsletter() -> None:
    path = ROOT / "newsletter.html"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if "What subscribers get" in text:
        return
    extra = """<h2>What subscribers get</h2><ul><li>One real clause risk example per week</li><li>Safer drafting pattern you can adapt</li><li>Legal AI workflow tip for Word users</li></ul><p>No spam. Unsubscribe anytime. See <a href="/editorial-standards">editorial standards</a>.</p>"""
    text = text.replace('<form class="form"', extra + '<form class="form"')
    path.write_text(text, encoding="utf-8")
    print("  enhanced newsletter.html")


def enhance_about() -> None:
    path = ROOT / "about.html"
    text = path.read_text(encoding="utf-8")
    if "editorial-standards" in text:
        return
    link = '<p><a href="/editorial-standards">Editorial standards</a> · <a href="/product-hunt/">Product Hunt kit</a> · <a href="/roi-calculator/">ROI calculator</a></p>'
    text = text.replace("</main>", link + "</main>")
    path.write_text(text, encoding="utf-8")
    print("  enhanced about.html")


def enhance_partners() -> None:
    path = ROOT / "partners.html"
    text = path.read_text(encoding="utf-8")
    if "Partner tiers" in text:
        return
    block = """<h2>Partner tiers</h2><div class="grid-2"><div class="card"><h3>Affiliate</h3><p>Legal tech newsletters and bloggers. Refer trial signups.</p></div><div class="card"><h3>Implementation</h3><p>Consultants deploying contract playbooks with Attyflow.</p></div></div><p>Apply: <a href="/contact?plan=partner">Contact partnerships</a></p>"""
    text = text.replace("</main>", block + "</main>")
    path.write_text(text, encoding="utf-8")
    print("  enhanced partners.html")


def submit_indexnow(urls: list[str]) -> None:
    key = (ROOT / "indexnow-key.txt").read_text().strip()
    payload = json.dumps({"host": "attyflow.com", "key": key, "urlList": urls}).encode()
    for ep in ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow"]:
        try:
            req = urllib.request.Request(ep, data=payload, method="POST", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                print(f"  IndexNow {len(urls)} urls: {r.status}")
        except Exception as e:
            print(f"  IndexNow failed: {e}")


def main() -> None:
    print("Attyflow P2 deploy")
    for rel in [
        "assets/site-p2.css", "assets/roi-calculator.js",
        "compare/ironclad-alternative/index.html",
        "roi-calculator/index.html",
        "use-cases/nda-review/index.html",
        "use-cases/saas-vendor-contracts/index.html",
        "clauses/nda-red-flags/index.html",
        "clauses/termination-for-convenience-red-flags/index.html",
        "product-hunt/index.html",
        "compare/index.html",
        "emails/welcome-sequence.json",
    ]:
        copy_src(rel)
    copy_src("editorial-standards.html")
    glossary_content = glossary_html()
    write("legal-ai-glossary.html", glossary_content)
    write("legal-ai-glossary/index.html", glossary_content)
    editorial = (SRC / "editorial-standards.html").read_text(encoding="utf-8")
    write("editorial-standards/index.html", editorial)
    update_clauses_index()
    expand_blogs_p2()
    enhance_newsletter()
    enhance_about()
    enhance_partners()
    update_sitemap()
    update_llms_txt()
    new_urls = [u for u, _ in NEW_SITEMAP_URLS]
    submit_indexnow(new_urls)
    idx = ROOT / "tools/attyflow_indexnow.py"
    if idx.exists():
        subprocess.run([sys.executable, str(idx), "50"], check=False)
    print("P2 deploy complete")


if __name__ == "__main__":
    main()
