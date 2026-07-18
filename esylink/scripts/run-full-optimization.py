#!/usr/bin/env python3
"""
Esylink.cn 全量优化脚本 — P0/P1/P2 批量执行
在服务器上运行: python3 /opt/esylink-optimize/run-full-optimization.py
"""
from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from pathlib import Path

WEB = Path(os.environ.get("ESYLINK_WEB", "/var/www/esylink"))
BASE = "https://esylink.cn"
TODAY = datetime.now().strftime("%Y-%m-%d")

# Extensionless canonical URLs (nginx 301 from .html)
EXTENSIONLESS = {
    "pricing.html", "about.html", "contact.html", "calculator.html",
    "free-trial.html", "faq.html", "cases.html", "compare.html",
}

# Pages that should be noindex
NOINDEX_FILES = {
    "seo-dashboard.html", "crm.html", "funnel.html", "case-template.html",
    "baidu_verify_codeva-g0tNnUajad.html", "baidu_verify_codeva-xxxxxxxx.html",
}

# Thin template dirs — noindex all subpages (keep dir index.html)
NOINDEX_DIRS = {"city", "dialer", "collection"}
NOINDEX_KEEP_INDEX = True
THIN_WORD_THRESHOLD = 400

COMPLIANCE_REPLACEMENTS = [
    ("100%合规", "合规流程辅助"),
    ("100% 合规", "合规流程辅助"),
    ("绝对合规", "合规流程管控"),
    ("科讯软件", "易连云通信"),
]

BLOG_CTA = """
<div class="esylink-blog-cta bg-indigo-50 border border-indigo-100 rounded-xl p-6 my-8 text-center">
  <h3 class="text-lg font-bold text-indigo-900 mb-2">需要AI外呼/云客服方案？</h3>
  <p class="text-slate-600 text-sm mb-4">7天免费试用 · 顾问1对1配置 · 当天可开通</p>
  <div class="flex flex-wrap justify-center gap-3">
    <a href="/free-trial.html?from=blog" class="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700">免费试用</a>
    <a href="/pricing" class="border border-indigo-300 text-indigo-700 px-5 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-50">查看报价</a>
    <a href="/contact" class="text-indigo-600 text-sm font-medium hover:underline">咨询顾问 →</a>
  </div>
</div>
"""

FOOTER_LEGAL = """<div class="text-xs text-slate-400 mt-4 flex flex-wrap gap-x-4 gap-y-1 justify-center">
  <a href="/legal/privacy.html" class="hover:text-slate-600">隐私政策</a>
  <a href="/legal/terms.html" class="hover:text-slate-600">服务条款</a>
  <a href="/compliance/" class="hover:text-slate-600">合规说明</a>
  <a href="/trust/" class="hover:text-slate-600">信任中心</a>
  <span>皖ICP备2026010967号-2</span>
</div>"""


def file_to_canonical(path: Path) -> str:
    rel = path.relative_to(WEB)
    parts = list(rel.parts)
    if parts[-1] == "index.html":
        parts = parts[:-1]
        url = "/" + "/".join(parts) + ("/" if parts else "")
    else:
        name = parts[-1]
        if name in EXTENSIONLESS:
            parts[-1] = name.replace(".html", "")
            url = "/" + "/".join(parts)
        else:
            url = "/" + "/".join(parts)
    url = re.sub(r"/+", "/", url)
    if url != "/" and url.endswith("/"):
        url = url.rstrip("/")
    return BASE + (url if url.startswith("/") else "/" + url)


def word_count(html: str) -> int:
    text = re.sub(r"<[^>]+>", " ", html)
    return len(re.sub(r"\s+", "", text))


def inject_canonical(html: str, url: str) -> tuple[str, bool]:
    tag = f'<link rel="canonical" href="{url}">'
    if "rel=\"canonical\"" in html or "rel='canonical'" in html:
        new = re.sub(
            r'<link[^>]*rel=["\']canonical["\'][^>]*>',
            tag,
            html,
            count=1,
        )
        return new, new != html
    if "</head>" in html:
        return html.replace("</head>", f"    {tag}\n</head>", 1), True
    return html, False


def inject_noindex(html: str) -> tuple[str, bool]:
    tag = '<meta name="robots" content="noindex, follow">'
    if "noindex" in html:
        return html, False
    if "</head>" in html:
        return html.replace("</head>", f"    {tag}\n</head>", 1), True
    return html, False


def fix_compliance(html: str) -> tuple[str, int]:
    n = 0
    for old, new in COMPLIANCE_REPLACEMENTS:
        if old in html:
            html = html.replace(old, new)
            n += 1
    return html, n


def fix_images(html: str) -> tuple[str, int]:
    n = 0
    if "product-dashboard.png" in html:
        html = html.replace("product-dashboard.png", "product-dashboard.webp")
        n += 1
    if "wecom-qr.png" in html and "wecom-qr.webp" not in html:
        # keep png for wecom if webp doesn't exist yet
        pass
    return html, n


def fix_emoji_nav(html: str) -> tuple[str, bool]:
    reps = [
        (">🤖 AI外呼<", '><i class="fas fa-robot mr-1"></i> AI外呼<'),
        (">☁️ 云客服<", '><i class="fas fa-cloud mr-1"></i> 云客服<'),
        (">📞 400电话<", '><i class="fas fa-phone mr-1"></i> 400电话<'),
        (">💰 报价<", '><i class="fas fa-tags mr-1"></i> 报价<'),
        (">📋 案例<", '><i class="fas fa-briefcase mr-1"></i> 案例<'),
    ]
    changed = False
    for old, new in reps:
        if old in html:
            html = html.replace(old, new)
            changed = True
    return html, changed


def inject_blog_cta(html: str, path: Path) -> tuple[str, bool]:
    if "esylink-blog-cta" in html:
        return html, False
    if "/blog/" not in str(path):
        return html, False
    if "</article>" in html:
        return html.replace("</article>", BLOG_CTA + "\n</article>", 1), True
    if "</main>" in html:
        return html.replace("</main>", BLOG_CTA + "\n</main>", 1), True
    return html, False


def inject_footer_legal(html: str) -> tuple[str, bool]:
    if "/legal/privacy" in html:
        return html, False
    if "<footer" in html and "隐私政策" not in html:
        html = re.sub(r"(</footer>)", FOOTER_LEGAL + r"\n\1", html, count=1)
        return html, True
    return html, False


def inject_scripts(html: str) -> tuple[str, bool]:
    scripts = []
    if "esylink-ab-test.js" not in html and "</body>" in html:
        scripts.append('<script src="/js/esylink-ab-test.js" defer></script>')
    if "esylink-lead-form.js" not in html and "esylink-chat.js" in html:
        scripts.append('<script src="/js/esylink-lead-form.js" defer></script>')
    if not scripts:
        return html, False
    block = "\n".join(scripts) + "\n"
    return html.replace("</body>", block + "</body>", 1), True


def fix_homepage_hero(html: str, path: Path) -> tuple[str, bool]:
    if path.name != "index.html" or path.parent != WEB:
        return html, False
    old_h1 = "AI智能外呼，<br>让每个电话<span class=\"text-indigo-300\">都是成交机会</span>"
    new_h1 = "AI外呼 + 云客服一体化平台<br>让企业<span class=\"text-indigo-300\">少招客服，多接线索</span>"
    old_p = "DeepSeek大模型语义理解 × 真人级语音合成<br class=\"hidden sm:block\"><span class=\"text-indigo-300\">外呼成本降低80% · 接通率提升3倍 · 7×24小时自动值守</span>"
    new_p = "支持智能外呼、来电接待、400热线、工单CRM、本地号码<br class=\"hidden sm:block\"><span class=\"text-indigo-300\">适合教育/口腔/保险/金融/电商 · 最快当天开通 · 7天免费试用</span>"
    changed = False
    if old_h1 in html:
        html = html.replace(old_h1, new_h1)
        changed = True
    if old_p in html:
        html = html.replace(old_p, new_p)
        changed = True
    # Fix free trial CTA link
    if 'href="/dialer/" class="bg-white text-indigo-700' in html:
        html = html.replace(
            'href="/dialer/" class="bg-white text-indigo-700',
            'href="/free-trial.html" class="bg-white text-indigo-700',
            1,
        )
        changed = True
    return html, changed


def process_file(path: Path, stats: dict) -> None:
    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return
    original = html
    rel = str(path.relative_to(WEB))

    # Canonical
    url = file_to_canonical(path)
    html, c = inject_canonical(html, url)
    if c:
        stats["canonical"] += 1

    # Noindex: admin pages + matrix subpages (dialer/city/collection)
    in_matrix = any(d in path.parts for d in NOINDEX_DIRS)
    is_matrix_index = (
        in_matrix
        and path.name == "index.html"
        and path.parent.name in NOINDEX_DIRS
    )
    should_noindex = path.name in NOINDEX_FILES or (
        in_matrix and not (NOINDEX_KEEP_INDEX and is_matrix_index)
    )
    if should_noindex:
        html, c = inject_noindex(html)
        if c:
            stats["noindex"] += 1

    # Compliance
    html, n = fix_compliance(html)
    stats["compliance"] += n

    # Images
    html, n = fix_images(html)
    stats["images"] += n

    # Emoji nav
    html, c = fix_emoji_nav(html)
    if c:
        stats["emoji_nav"] += 1

    # Blog CTA
    html, c = inject_blog_cta(html, path)
    if c:
        stats["blog_cta"] += 1

    # Footer legal
    html, c = inject_footer_legal(html)
    if c:
        stats["footer_legal"] += 1

    # Scripts
    html, c = inject_scripts(html)
    if c:
        stats["scripts"] += 1

    # Homepage hero
    html, c = fix_homepage_hero(html, path)
    if c:
        stats["homepage"] += 1

    if html != original:
        path.write_text(html, encoding="utf-8")
        stats["files_changed"] += 1


def update_robots():
    robots = WEB / "robots.txt"
    extra = """
# Block admin/template pages
Disallow: /seo-dashboard.html
Disallow: /crm.html
Disallow: /funnel.html
Disallow: /seo-engine/
Disallow: /api/
"""
    text = robots.read_text(encoding="utf-8")
    if "seo-dashboard" not in text:
        robots.write_text(text.rstrip() + "\n" + extra, encoding="utf-8")
        return True
    return False


def main():
    if not WEB.is_dir():
        print(f"ERROR: {WEB} not found")
        sys.exit(1)

    stats = {
        "files_changed": 0, "canonical": 0, "noindex": 0,
        "compliance": 0, "images": 0, "emoji_nav": 0,
        "blog_cta": 0, "footer_legal": 0, "scripts": 0, "homepage": 0,
    }

    print(f"🚀 Esylink full optimization — {WEB}")
    for f in sorted(WEB.rglob("*.html")):
        process_file(f, stats)

    robots_ok = update_robots()

    print(f"\n✅ Done:")
    for k, v in stats.items():
        print(f"   {k}: {v}")
    print(f"   robots.txt updated: {robots_ok}")

    # Regenerate sitemaps
    seo_engine = WEB / "seo-engine" / "generate.py"
    if seo_engine.exists():
        print("\n📄 Regenerating sitemaps...")
        os.system(f"cd {WEB / 'seo-engine'} && python3 generate.py --sitemap")


if __name__ == "__main__":
    main()
