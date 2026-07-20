#!/usr/bin/env python3
"""Attyflow P5 — expand remaining 86 blogs, Product Hunt launch page, full IndexNow."""
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
EXP_MARKERS = ("P1 expansion", "P2 expansion", "P3 expansion", "P4 expansion", "P5 expansion")

CONTRACT_KW = ("contract", "nda", "clause", "msa", "indemn", "liabil", "playbook", "redlin", "vendor", "saas", "negotiat", "termination", "warrant", "force-majeure", "delaware", "cross-border", "rfp-response")
FIRM_KW = ("law-firm", "legal-ops", "legal-operations", "paralegal", "outside-counsel", "matter-management", "billing", "invoice", "spend", "revenue", "fee", "succession", "merger", "knowledge", "client-portal", "client-retention", "tech-stack", "kpi", "diversity", "financial", "cloud-migration", "cybersecurity", "digital-transformation", "practice-automation", "legal-tech-roi", "legal-tech-forecast", "legal-tech-startup", "legal-design", "legal-innovation", "alternative-fee", "legal-process-outsourcing", "project-management", "entity-management", "solo-practitioners", "legal-department", "legal-chatbots", "elevating-client", "your-roadmap")
COMPLIANCE_KW = ("compliance", "privacy", "regulatory", "esg", "whistleblower", "governance", "records-retention", "data-privacy")
LITIGATION_KW = ("e-discovery", "litigation", "court-filing", "deposition", "subpoena", "class-action", "legal-hold", "evidence", "predictive-coding", "litigation-funding", "litigation-analytics", "legal-analytics", "legal-research", "dispute-resolution", "redaction", "smarter-e-discovery", "streamlining-digital")


def p5_block(filename: str) -> str:
    slug = filename.replace(".html", "")
    title = slug.replace("-", " ").title()
    if any(k in slug for k in CONTRACT_KW):
        return f"""<!-- P5 expansion -->
<h2>Apply this to contract review</h2>
<p>This guide connects to practical contract workflows. After reading, paste a live clause into <a href="/taskpane.html">Attyflow's sandbox</a> or the relevant <a href="/tools/nda-clause-review/">free checker</a> to validate risk scoring against your playbook.</p>
<p>For firm-wide rollout, see our <a href="/case-studies/">pilot case studies</a> and <a href="/roi-calculator/">ROI calculator</a>.</p>"""
    if any(k in slug for k in FIRM_KW):
        return f"""<!-- P5 expansion -->
<h2>Operational next steps</h2>
<p>Legal operations and firm technology decisions should tie to measurable outcomes — cycle time, counsel hours, and error rates. Start with your highest-volume agreement type (usually NDAs or vendor MSAs) and run a 30-day pilot using <a href="/taskpane.html">Attyflow</a>.</p>
<p>Compare pilot metrics against the anonymized workflows in our <a href="/case-studies/">case studies</a>.</p>"""
    if any(k in slug for k in COMPLIANCE_KW):
        return f"""<!-- P5 expansion -->
<h2>Compliance and contract review</h2>
<p>Regulatory compliance often surfaces in contract language — data processing, breach notification, audit rights, and subprocessors. Use AI triage to flag clauses that need specialist review, not to replace compliance sign-off.</p>
<p>Pair policy review with clause-level checks via <a href="/tools/limitation-of-liability-checker/">Attyflow's free tools</a>.</p>"""
    if any(k in slug for k in LITIGATION_KW):
        return f"""<!-- P5 expansion -->
<h2>From litigation to prevention</h2>
<p>Many litigation workflows benefit from stronger upfront contract language. Transactional teams using <a href="/product">Attyflow</a> for first-pass review reduce ambiguous obligations before they become disputes.</p>
<p>This article's litigation focus complements — not replaces — contract review at the drafting stage.</p>"""
    if "blockchain" in slug or "smart-contract" in slug:
        return f"""<!-- P5 expansion -->
<h2>Note on terminology</h2>
<p>Attyflow reviews traditional commercial contracts (NDAs, MSAs, SaaS agreements) for US common-law workflows — not blockchain smart contract code. For legal agreement review in Word, try the <a href="/taskpane.html">free sandbox</a>.</p>"""
    if any(k in slug for k in ("ip", "patent", "trademark", "intellectual-property")):
        return f"""<!-- P5 expansion -->
<h2>IP clauses in commercial agreements</h2>
<p>IP assignment, license scope, and work-for-hire language appear across vendor and customer contracts. Flag overbroad assignments with AI triage before specialist IP review.</p>
<p>Test assignment clauses in the <a href="/taskpane.html">Attyflow sandbox</a> with seller or buyer position set.</p>"""
    return f"""<!-- P5 expansion -->
<h2>Put this guide into practice</h2>
<p>Legal technology guidance is most valuable when connected to a live workflow. Validate concepts from "{title}" by running a representative clause through <a href="/taskpane.html">Attyflow</a> — three free audits, no credit card.</p>
<p>See also: <a href="/best-ai-contract-review-2026/">Best AI contract review tools 2026</a> · <a href="/editorial-standards">Editorial standards</a></p>"""


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


def expand_all_remaining() -> int:
    n = 0
    for path in sorted((ROOT / "blog").glob("*.html")):
        if path.name == "index.html":
            continue
        text = path.read_text(encoding="utf-8")
        if any(m in text for m in EXP_MARKERS):
            continue
        if MARKER not in text:
            continue
        block = p5_block(path.name)
        text = text.replace(MARKER, block + "\n" + MARKER, 1)
        path.write_text(text, encoding="utf-8")
        n += 1
    print(f"  expanded {n} blogs (P5 — all remaining)")
    return n


def generate_ph_gallery() -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "pillow", "-q"], check=True)
        from PIL import Image, ImageDraw, ImageFont

    specs = [
        ("ph-gallery-1.png", "Risk Score 84 · HIGH", "Uncapped indemnity flagged"),
        ("ph-gallery-2.png", "Redline Ready", "Negotiation language drafted"),
        ("ph-gallery-3.png", "Word-native", "Review inside Microsoft Word"),
    ]
    try:
        font_l = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except OSError:
        font_l = ImageFont.load_default()
        font_s = ImageFont.load_default()

    for name, title, sub in specs:
        img = Image.new("RGB", (1200, 750), "#0f172a")
        draw = ImageDraw.Draw(img)
        draw.rectangle([(40, 40), (1160, 710)], outline="#334155", width=2)
        draw.rectangle([(40, 40), (1160, 100)], fill="#1e293b")
        draw.text((60, 52), "ATTYFLOW", fill="#f59e0b", font=font_s)
        draw.text((60, 200), title, fill="#f8fafc", font=font_l)
        draw.text((60, 280), sub, fill="#94a3b8", font=font_s)
        if "Risk" in title:
            draw.rectangle([(60, 360), (500, 420)], fill="#991b1b")
            draw.text((80, 375), "HIGH RISK · Score 84", fill="#fff", font=font_s)
        elif "Redline" in title:
            draw.rectangle([(60, 360), (1100, 480)], fill="#1e293b")
            draw.text((80, 380), "Replace with: Each party's indemnity shall be limited to...", fill="#e2e8f0", font=font_s)
        else:
            draw.rectangle([(60, 360), (700, 650)], fill="#fff")
            draw.rectangle([(720, 360), (1100, 650)], fill="#f8fafc")
            draw.text((80, 380), "Word document", fill="#64748b", font=font_s)
            draw.text((740, 380), "Taskpane", fill="#0f172a", font=font_s)
        out = ROOT / "assets" / name
        img.save(out, "PNG", optimize=True)
        print(f"  gallery: {name} ({out.stat().st_size} bytes)")


def patch_homepage_launch() -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    banner = '<div style="background:#f59e0b;color:#0f172a;text-align:center;padding:10px 22px;font-size:14px;font-weight:700"><a href="/launch/" style="color:inherit;text-decoration:none">🚀 Attyflow is live — try 3 free clause audits →</a></div>\n'
    if "Attyflow is live" not in text:
        text = text.replace("<body>", "<body>\n" + banner, 1)
        path.write_text(text, encoding="utf-8")
        print("  added launch banner to homepage")


def update_sitemap() -> None:
    text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    if "https://attyflow.com/launch/" not in text:
        text = text.replace(
            "</urlset>",
            f'  <url><loc>https://attyflow.com/launch/</loc><lastmod>{TODAY}</lastmod><priority>0.9</priority></url>\n</urlset>',
        )
        (ROOT / "sitemap.xml").write_text(text, encoding="utf-8")
        print("  added /launch/ to sitemap")


def update_llms() -> None:
    llms = ROOT / "llms.txt"
    if llms.exists():
        text = llms.read_text(encoding="utf-8")
        if "/launch/" not in text:
            text = text.replace("- /editorial-standards", "- /launch/\n- /editorial-standards")
            llms.write_text(text, encoding="utf-8")
            print("  updated llms.txt")


def indexnow_all() -> None:
    idx = ROOT / "tools/attyflow_indexnow.py"
    if idx.exists():
        subprocess.run([sys.executable, str(idx)], check=False)


def main() -> None:
    print("Attyflow P5 deploy")
    copy_src("launch/index.html")
    generate_ph_gallery()
    patch_homepage_launch()
    n = expand_all_remaining()
    update_sitemap()
    update_llms()
    indexnow_all()
    print(f"P5 complete — {n} blogs expanded, launch page live")


if __name__ == "__main__":
    main()
