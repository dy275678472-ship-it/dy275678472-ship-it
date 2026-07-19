#!/usr/bin/env python3
"""Attyflow P3 — Top 20 blog expansions, case studies, Cloudflare prep."""
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
NGINX_SITE = Path("/etc/nginx/sites-enabled/traffic-override.conf")
CF_CONF = Path("/etc/nginx/conf.d/cloudflare-real-ip.conf")
TODAY = date.today().isoformat()
MARKER = '<section class="attyflow-eat"'

BLOG_P3 = {
  "contract-ai-redlining-vs-human.html": "<h2>Hybrid workflow template</h2><p>Run AI redlining on indemnity and liability clauses first. Attorney reviews only sections scoring MEDIUM or HIGH. Document partner override rate monthly to calibrate trust in the tool.</p>",
  "contract-negotiation-strategies-ai.html": "<h2>AI-assisted negotiation prep</h2><p>Before a call, generate a ranked issues list from Attyflow scores. Lead with business-critical clauses (uncapped liability, IP assignment) and hold minor definitional edits for email markup.</p>",
  "contract-review-compliance-ai.html": "<h2>Compliance mapping</h2><p>Map AI-flagged clauses to your compliance register: data processing → privacy policy; export controls → trade compliance review. Risk scores help compliance teams prioritize without reading full agreements.</p>",
  "contract-risk-scoring-automated.html": "<h2>Automation boundaries</h2><p>Automate triage, not approval. Set hard rules: scores above 80 on indemnity always require partner eyes. Scores below 40 on standard NDAs may proceed with associate-only markup per playbook.</p>",
  "automating-contract-review-delaware.html": "<h2>Delaware-specific checks</h2><p>When governing law is Delaware, verify choice-of-forum, jury waiver, and indemnity scope against typical DE commercial norms. Cross-check with your <a href='/clauses/indemnification-red-flags'>indemnification red flags</a> guide.</p>",
  "collaborative-contract-playbooks.html": "<h2>Team playbook sharing</h2><p>Store approved fallback language per clause type in a shared playbook. Attyflow Team tier supports shared workflow — align scores with playbook tier labels (preferred / acceptable / escalate).</p>",
  "contract-lifecycle-management-best-practices.html": "<h2>CLM + AI review</h2><p>CLM handles repository and approvals; AI review handles clause-level risk at intake. Integrate Attyflow at the intake stage before contracts enter CLM workflow.</p>",
  "contract-metadata-extraction.html": "<h2>Metadata vs risk analysis</h2><p>Extraction tools pull dates and parties; risk tools evaluate clause substance. Use both: metadata for routing, risk scores for review depth assignment.</p>",
  "contract-negotiation-ai-platforms.html": "<h2>Platform selection</h2><p>Evaluate negotiation AI on redline acceptance rate by attorneys, not demo flashiness. Pilot on 20 live clauses and measure partner edit distance on suggested language.</p>",
  "indemnification-clause-7-red-flags.html": "<h2>Quick reference</h2><p>The seven flags: uncapped scope, third-party claims without procedure, IP carveouts, consequential damages inclusion, unilateral obligation, survival beyond term, and indemnity as exclusive remedy. Test each with the <a href='/tools/indemnification-clause-checker/'>indemnification checker</a>.</p>",
  "indemnification-traps.html": "<h2>Vendor paper traps</h2><p>Vendors often push indemnity covering your misuse of their platform while capping their liability. Flag asymmetry early and propose reciprocal third-party claim language.</p>",
  "data-privacy-vendor-contracts-ccpa-gdpr.html": "<h2>Privacy clause bundle</h2><p>Review DPA, SCCs, subprocessors, and breach notification together with limitation of liability. A weak liability cap can undermine privacy indemnities.</p>",
  "cross-border-contracts-ai.html": "<h2>Cross-border triage</h2><p>AI review does not replace local counsel on governing law and regulatory compliance. Use risk scoring to identify which cross-border agreements need jurisdiction-specific review.</p>",
  "choice-of-law-delaware-dominance.html": "<h2>When DE law is non-negotiable</h2><p>Many counterparties insist on Delaware governing law. Focus negotiation energy on liability and indemnity rather than re-litigating choice of law unless client policy prohibits DE.</p>",
  "ip-assignment-clauses-protection.html": "<h2>IP assignment red flags</h2><p>Work-for-hire scope, moral rights waivers, and background IP carveouts need human judgment. Use AI to flag overbroad assignment language for specialist review.</p>",
  "termination-for-convenience-30-days.html": "<h2>30-day TFC norms</h2><p>Thirty days is common in B2B SaaS but may be insufficient for data migration. Pair TFC review with data export and deletion clauses. See <a href='/clauses/termination-for-convenience-red-flags/'>TFC red flags</a>.</p>",
  "ma-due-diligence-automating-contract-review.html": "<h2>Diligence batching</h2><p>Process material contracts in batches by type: customer, supplier, IP license. Rank by revenue concentration × risk score for partner discussion order.</p>",
  "reps-and-warranties-audit-framework.html": "<h2>R&W triage</h2><p>AI clause review complements R&W insurance diligence. Flag uncapped indemnities and survival periods that affect R&W coverage eligibility.</p>",
  "third-party-risk-management.html": "<h2>TPRM integration</h2><p>Feed vendor contract risk scores into your third-party risk register. HIGH scores trigger enhanced due diligence before procurement approval.</p>",
  "contract-negotiation-platforms.html": "<h2>Negotiation stack</h2><p>Combine Word-native review (Attyflow) with CLM storage and e-signature. Avoid duplicating AI tools — one review layer at intake is sufficient for most firms.</p>",
}

CASE_URLS = [
  "https://attyflow.com/case-studies/",
  "https://attyflow.com/case-studies/small-firm-nda-turnaround/",
  "https://attyflow.com/case-studies/legal-ops-vendor-triage/",
  "https://attyflow.com/case-studies/ma-clause-prioritization/",
]


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
    for fn, block in BLOG_P3.items():
        path = ROOT / "blog" / fn
        if not path.exists() or MARKER not in path.read_text(encoding="utf-8"):
            continue
        text = path.read_text(encoding="utf-8")
        if "P3 expansion" in text:
            continue
        text = text.replace(MARKER, f"<!-- P3 expansion -->\n{block}\n" + MARKER, 1)
        path.write_text(text, encoding="utf-8")
        n += 1
    print(f"  expanded {n} blogs (P3)")
    return n


CF_IPV4_FALLBACK = [
    "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22",
    "141.101.64.0/18", "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20",
    "197.234.240.0/22", "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
    "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22",
]


def setup_cloudflare_nginx() -> None:
    try:
        req = urllib.request.Request(
            "https://www.cloudflare.com/ips-v4",
            headers={"User-Agent": "AttyflowDeploy/1.0"},
        )
        ips_v4 = urllib.request.urlopen(req, timeout=15).read().decode().strip().split("\n")
        ips_v4 = [ip.strip() for ip in ips_v4 if ip.strip()]
    except Exception as e:
        print(f"  WARN: fetch CF IPs failed ({e}), using fallback list")
        ips_v4 = CF_IPV4_FALLBACK
    lines = ["# Cloudflare real IP — auto-generated by attyflow_p3_deploy.py\n"]
    for ip in ips_v4:
        ip = ip.strip()
        if ip:
            lines.append(f"set_real_ip_from {ip};")
    lines.append("real_ip_header CF-Connecting-IP;")
    CF_CONF.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  wrote {CF_CONF} ({len(ips_v4)} IPv4 ranges)")

    text = NGINX_SITE.read_text(encoding="utf-8")
    inc = "include /etc/nginx/conf.d/cloudflare-real-ip.conf;"
    anchor = "server_name attyflow.com;"
    if inc not in text and anchor in text:
        text = text.replace(
            "    root /var/www/attyflow;\n    index index.html taskpane.html;",
            "    include /etc/nginx/conf.d/cloudflare-real-ip.conf;\n    root /var/www/attyflow;\n    index index.html taskpane.html;",
            1,
        )
        NGINX_SITE.write_text(text, encoding="utf-8")
        subprocess.run(["sudo", "nginx", "-t"], check=True)
        subprocess.run(["sudo", "systemctl", "reload", "nginx"], check=True)
        print("  included cloudflare-real-ip in attyflow server block")
    elif inc in text:
        print("  cloudflare include already present")
    shutil.copy2(SRC / "CLOUDFLARE_SETUP.md", ROOT / "CLOUDFLARE_SETUP.md")
    print("  copied CLOUDFLARE_SETUP.md")


def update_case_studies_html() -> None:
    hub = (SRC / "case-studies/index.html").read_text(encoding="utf-8")
    write("case-studies.html", hub)
    write("case-studies/index.html", hub)


def update_customers() -> None:
    path = ROOT / "customers.html"
    text = path.read_text(encoding="utf-8")
    if "case-studies" in text:
        return
    link = '<p>Read anonymized <a href="/case-studies/">pilot case studies</a> from teams in our evaluation program.</p>'
    text = text.replace("<h2>How it works</h2>", link + "<h2>How it works</h2>")
    path.write_text(text, encoding="utf-8")
    print("  linked case studies from customers page")


def update_sitemap() -> None:
    text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for url in CASE_URLS:
        if url not in text:
            text = text.replace(
                "</urlset>",
                f'  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod><priority>0.8</priority></url>\n</urlset>',
            )
    (ROOT / "sitemap.xml").write_text(text, encoding="utf-8")
    print("  updated sitemap")


def indexnow(urls: list[str]) -> None:
    key = (ROOT / "indexnow-key.txt").read_text().strip()
    payload = json.dumps({"host": "attyflow.com", "key": key, "urlList": urls}).encode()
    for ep in ["https://api.indexnow.org/indexnow", "https://www.bing.com/indexnow"]:
        try:
            req = urllib.request.Request(ep, data=payload, method="POST", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                print(f"  IndexNow {r.status} ({len(urls)} urls)")
        except Exception as e:
            print(f"  IndexNow failed: {e}")


def main() -> None:
    print("Attyflow P3 deploy")
    for rel in [
        "case-studies/index.html",
        "case-studies/small-firm-nda-turnaround/index.html",
        "case-studies/legal-ops-vendor-triage/index.html",
        "case-studies/ma-clause-prioritization/index.html",
    ]:
        copy_src(rel)
    update_case_studies_html()
    expand_blogs()
    update_customers()
    update_sitemap()
    setup_cloudflare_nginx()
    indexnow(CASE_URLS)
    idx = ROOT / "tools/attyflow_indexnow.py"
    if idx.exists():
        subprocess.run([sys.executable, str(idx)], check=False)
    print("P3 deploy complete")


if __name__ == "__main__":
    main()
