#!/usr/bin/env python3
"""Attyflow P4 — blog batch 4, lead welcome queue, newsletter API, GSC guide."""
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path("/var/www/attyflow")
SRC = Path(__file__).resolve().parent / "attyflow-files"
TODAY = date.today().isoformat()
MARKER = '<section class="attyflow-eat"'
RELATED = """<aside class="attyflow-related" style="margin:24px 0;padding:18px;border:1px solid #e2e8f0;border-radius:12px;background:#fff"><h3 style="margin-top:0;color:#0f172a">Attyflow resources</h3><ul style="margin:0;padding-left:18px;color:#475569;font-size:14px"><li><a href="/tools/nda-clause-review/">Free NDA checker</a></li><li><a href="/case-studies/">Pilot case studies</a></li><li><a href="/roi-calculator/">ROI calculator</a></li><li><a href="/best-ai-contract-review-2026/">Best AI tools 2026</a></li></ul></aside>"""

BLOG_P4 = {
  "nda-enforceability.html": "<h2>Enforceability checklist</h2><p>Confirm consideration, mutual obligations where required, reasonable scope, and jurisdiction-specific formalities. AI triage flags overbroad language; local counsel confirms enforceability.</p>",
  "limitation-of-liability.html": "<h2>Cap mechanics</h2><p>Distinguish direct vs consequential damages, carveouts for confidentiality breach and IP claims, and whether the cap is a multiple of fees or a fixed dollar amount. Use the <a href='/tools/limitation-of-liability-checker/'>liability checker</a>.</p>",
  "legal-ai-contract-analysis.html": "<h2>Analysis vs advice</h2><p>AI contract analysis surfaces issues for attorney judgment. Document that outputs are drafts requiring review before client delivery or negotiation.</p>",
  "ma-transactional-ai-vs-traditional.html": "<h2>M&A triage workflow</h2><p>Batch material contracts by type, score indemnity and change-of-control clauses, present ranked issues list before partner diligence call. See <a href='/case-studies/ma-clause-prioritization/'>M&A case study</a>.</p>",
  "reasonable-efforts-dangerous-contract-phrase.html": "<h2>Efforts standards</h2><p>Compare reasonable vs best efforts vs commercially reasonable efforts. Flag undefined standards that create litigation risk over performance obligations.</p>",
  "playbook-version-control-git.html": "<h2>Playbook versioning</h2><p>Store playbook changes in git with matter-type tags. Align Attyflow risk thresholds when playbook fallback tiers change.</p>",
  "cross-border-contract-management.html": "<h2>Cross-border review</h2><p>AI review does not replace local counsel. Use scores to decide which agreements need jurisdiction-specific sign-off.</p>",
  "contract-lifecycle-management.html": "<h2>CLM intake point</h2><p>Run AI clause review at contract intake before CLM routing. Reduces low-risk agreements reaching senior counsel.</p>",
  "legal-vendor-risk-management.html": "<h2>Vendor risk tiers</h2><p>Map contract risk scores to vendor tiers: critical vendors get full counsel review; low-risk renewals use playbook fallbacks only.</p>",
  "paralegal-ai-toolkit.html": "<h2>Paralegal workflow</h2><p>Paralegals run first-pass AI triage; attorneys approve redlines. Define escalation rules by risk score in your playbook.</p>",
  "navigating-legal-ai-ethics-framework.html": "<h2>Ethics guardrails</h2><p>Disclose AI use to clients where required, maintain competence through training, and never outsource professional judgment to software output.</p>",
  "ai-powered-due-diligence-revolution.html": "<h2>Diligence acceleration</h2><p>Prioritize contracts by revenue impact × risk score. Start with top 20% of agreements by value for deep review.</p>",
  "cut-due-diligence-time-70.html": "<h2>Time reduction tactics</h2><p>Standardize clause extraction templates, batch AI scoring overnight, and reserve partner time for score-ranked exceptions only.</p>",
  "document-automation-for-legal-teams.html": "<h2>Automation stack</h2><p>Combine template automation for standard agreements with AI review for non-standard counterparty paper.</p>",
  "corporate-legal-department-ai.html": "<h2>In-house adoption</h2><p>Start with procurement NDAs and vendor MSAs. Measure cycle time and counsel hours before expanding to customer paper.</p>",
  "ai-ethics-in-legal-practice.html": "<h2>Client disclosure</h2><p>Consider engagement letter language on AI-assisted review. Maintain audit logs of AI-generated markup accepted or rejected.</p>",
  "ai-governance-law-firms.html": "<h2>Firm governance</h2><p>Establish an AI committee: approve tools, define prohibited uses, and review malpractice carrier guidance annually.</p>",
  "law-firm-digital-transformation-2026.html": "<h2>Transformation priorities</h2><p>For transactional groups, contract AI often delivers faster ROI than generic document automation. Pilot on NDAs before firm-wide rollout.</p>",
  "virtual-law-firm-operations.html": "<h2>Remote review</h2><p>Word-native AI review supports distributed teams without centralized document servers. Ensure security policy covers cloud API processing.</p>",
  "e-discovery-cost-reduction-strategies.html": "<h2>Adjacent workflows</h2><p>Contract AI complements e-discovery — use during drafting and negotiation to reduce problematic language before disputes arise.</p>",
}


def write(rel: str, content: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {rel}")


def copy_src(rel: str) -> None:
    dst = ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC / rel, dst)
    print(f"  copied {rel}")


def expand_blogs() -> int:
    n = 0
    for fn, block in BLOG_P4.items():
        path = ROOT / "blog" / fn
        if not path.exists() or MARKER not in path.read_text(encoding="utf-8"):
            continue
        text = path.read_text(encoding="utf-8")
        if "P4 expansion" in text:
            continue
        text = text.replace(MARKER, f"<!-- P4 expansion -->\n{block}\n" + MARKER, 1)
        path.write_text(text, encoding="utf-8")
        n += 1
    print(f"  expanded {n} blogs (P4)")
    return n


def inject_related_links() -> int:
    n = 0
    for path in (ROOT / "blog").glob("*.html"):
        text = path.read_text(encoding="utf-8")
        if "attyflow-related" in text or MARKER not in text:
            continue
        text = text.replace(MARKER, RELATED + MARKER, 1)
        path.write_text(text, encoding="utf-8")
        n += 1
    print(f"  injected related links in {n} blogs")
    return n


def patch_newsletter() -> None:
    js = '<script src="/assets/newsletter-form.js" defer></script>\n'
    for rel in ["newsletter.html", "newsletter/index.html"]:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "newsletter-form.js" in text:
            continue
        text = text.replace(
            '<form class="form" action="/subscribe.php" method="post">',
            '<form class="form" id="newsletter-form">',
        )
        if 'id="newsletter-form"' not in text:
            text = text.replace('<form class="form"', '<form class="form" id="newsletter-form"', 1)
        text = text.replace("</body>", js + "</body>")
        path.write_text(text, encoding="utf-8")
        print(f"  patched {rel}")


def update_news_sitemap() -> None:
    entries = [
        ("https://attyflow.com/case-studies/small-firm-nda-turnaround/", "Small firm NDA turnaround case study"),
        ("https://attyflow.com/best-ai-contract-review-2026/", "Best AI contract review software 2026"),
        ("https://attyflow.com/roi-calculator/", "Contract review ROI calculator"),
    ]
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">',
    ]
    for url, title in entries:
        lines.append(f"<url><loc>{url}</loc>")
        lines.append("<news:news><news:publication><news:name>Attyflow</news:name>")
        lines.append("<news:language>en</news:language></news:publication>")
        lines.append(f"<news:publication_date>{TODAY}</news:publication_date>")
        lines.append(f"<news:title>{title}</news:title></news:news></url>")
    lines.append("</urlset>")
    write("news-sitemap.xml", "\n".join(lines) + "\n")


def restart_api() -> None:
    try:
        subprocess.run(["pm2", "restart", "attyflow"], check=True, capture_output=True)
        print("  restarted api via pm2 attyflow")
        return
    except Exception:
        pass
    print("  WARN: run manually: pm2 restart attyflow")


def main() -> None:
    print("Attyflow P4 deploy")
    copy_src("index.html")
    copy_src("main.py")
    copy_src("assets/newsletter-form.js")
    copy_src("tools/attyflow_welcome_cron.py")
    for doc in ["GSC_SETUP.md", "CLOUDFLARE_SETUP.md"]:
        if (SRC / doc).exists():
            copy_src(doc)
    expand_blogs()
    inject_related_links()
    patch_newsletter()
    update_news_sitemap()
    restart_api()
    idx = ROOT / "tools/attyflow_indexnow.py"
    if idx.exists():
        subprocess.run([sys.executable, str(idx), "100"], check=False)
    print("P4 deploy complete")


if __name__ == "__main__":
    main()
