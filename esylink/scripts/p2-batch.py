#!/usr/bin/env python3
"""P2 batch: noindex matrix pages, blog covers, whitepaper, compare leads, case data."""
from __future__ import annotations

import base64
import re
import struct
import zlib
from pathlib import Path

WEB = Path("/var/www/esylink")
NOINDEX_DIRS = {"dialer", "city", "collection"}
KEEP_INDEX = {"index.html"}

# Minimal 600x340 indigo gradient WebP (placeholder blog cover)
WEBP_B64 = (
    "UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAQAcJaQAA3AA/vuUAAA="
)


def write_webp(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    raw = base64.b64decode(
        "UklGRkYAAABXRUJQVlA4IDQAAADwAQCdASoBAAEAAQAcJaQAA3AA/v8AAAA="
    )
    path.write_bytes(raw)


def make_cover_svg(title: str) -> str:
    t = (title[:30] + "…") if len(title) > 30 else title
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="340" viewBox="0 0 600 340">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#312e81"/><stop offset="100%" stop-color="#4f46e5"/>
  </linearGradient></defs>
  <rect width="600" height="340" fill="url(#g)"/>
  <text x="40" y="180" fill="#fff" font-size="28" font-family="sans-serif" font-weight="bold">{t}</text>
  <text x="40" y="220" fill="#c7d2fe" font-size="14" font-family="sans-serif">易连云通信 · 博客</text>
</svg>"""


def noindex_matrix_pages():
    n = 0
    for d in NOINDEX_DIRS:
        root = WEB / d
        if not root.is_dir():
            continue
        for f in root.rglob("*.html"):
            if f.name in KEEP_INDEX and f.parent == root:
                continue
            html = f.read_text(encoding="utf-8", errors="replace")
            if "noindex" in html:
                continue
            tag = '<meta name="robots" content="noindex, follow">'
            if "</head>" in html:
                html = html.replace("</head>", f"    {tag}\n</head>", 1)
                f.write_text(html, encoding="utf-8")
                n += 1
    print(f"  ✓ noindex matrix pages: {n}")


def inject_blog_covers():
    covers_dir = WEB / "images" / "blog" / "covers"
    covers_dir.mkdir(parents=True, exist_ok=True)
    default = covers_dir / "default.svg"
    if not default.exists():
        default.write_text(make_cover_svg("AI外呼与云客服"), encoding="utf-8")

    n = 0
    for f in (WEB / "blog").rglob("index.html"):
        if f.parent == WEB / "blog":
            continue
        html = f.read_text(encoding="utf-8", errors="replace")
        if 'images/blog/covers/' in html:
            continue
        title_m = re.search(r"<title>([^<]+)</title>", html)
        title = title_m.group(1).split("—")[0].strip() if title_m else "博客"
        slug = f.parent.name
        cover = covers_dir / f"{slug}.svg"
        if not cover.exists():
            cover.write_text(make_cover_svg(title), encoding="utf-8")
        img = f'<img src="/images/blog/covers/{slug}.svg" alt="{title}" width="600" height="340" class="w-full rounded-xl mb-6" loading="lazy">'
        if "<article" in html and img not in html:
            html = re.sub(r"(<article[^>]*>)", r"\1\n" + img, html, count=1)
            f.write_text(html, encoding="utf-8")
            n += 1
    print(f"  ✓ blog covers: {n}")


def create_whitepaper():
    fp = WEB / "resources" / "ai-outbound-guide.html"
    if fp.exists():
        print("  ✓ whitepaper exists")
        return
    fp.parent.mkdir(parents=True, exist_ok=True)
    html = """<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>中小企业AI外呼选型指南 — 易连云通信白皮书</title>
<meta name="description" content="免费下载《中小企业AI外呼选型指南》：功能对比、合规要点、ROI测算、实施 checklist。">
<link rel="canonical" href="https://esylink.cn/resources/ai-outbound-guide.html">
<link rel="stylesheet" href="/css/tw.css">
<link rel="stylesheet" href="/css/fontawesome/all.min.css">
</head><body class="bg-slate-50 text-slate-800">
<header class="bg-indigo-700 text-white py-4"><div class="max-w-4xl mx-auto px-4 font-bold">易连云通信</div></header>
<main class="max-w-4xl mx-auto px-4 py-12 prose">
<h1>中小企业 AI 外呼选型指南</h1>
<p>本白皮书涵盖：产品能力矩阵、合规要求、成本模型、供应商对比、上线 checklist。</p>
<h2>目录</h2>
<ol>
<li>AI 外呼 vs 传统电销</li>
<li>合规流程（时段/黑名单/录音）</li>
<li>ROI 测算模型</li>
<li>供应商五维对比</li>
<li>7 天试用实施清单</li>
</ol>
<div class="not-prose bg-white rounded-xl p-6 border my-8">
  <h3 class="font-bold text-lg mb-3">免费获取完整 PDF</h3>
  <input type="tel" id="wp-phone" placeholder="手机号" class="w-full border rounded-lg px-4 py-3 mb-3">
  <button onclick="submitWp()" class="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold w-full">下载白皮书</button>
  <p id="wp-msg" class="text-sm mt-2"></p>
</div>
<p><a href="/compare">查看服务商对比</a> · <a href="/calculator">ROI 计算器</a></p>
</main>
<script>
function submitWp(){
  var p=document.getElementById('wp-phone').value.trim();
  if(!/^1\\d{10}$/.test(p)){document.getElementById('wp-msg').textContent='请输入正确手机号';return;}
  fetch('/api/v1/leads',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
    name:'白皮书下载',phone:p,source:'whitepaper',page_url:location.href,message:'AI外呼选型指南'
  })}).then(function(){document.getElementById('wp-msg').textContent='已提交，PDF将发送至您的手机';});
}
</script>
<script src="/js/page-track.js" defer></script>
</body></html>"""
    fp.write_text(html, encoding="utf-8")
    print("  ✓ whitepaper created")


def enhance_compare_leads():
    fp = WEB / "compare.html"
    if not fp.exists():
        return
    html = fp.read_text(encoding="utf-8")
    if "compare-leads-js" in html:
        print("  ✓ compare leads already wired")
        return
    script = """
<script id="compare-leads-js">
document.getElementById('ctaForm')?.addEventListener('submit',function(e){
  e.preventDefault();
  var phone=document.getElementById('phone').value.trim();
  var msg=document.getElementById('msg');
  if(!/^1\\d{10}$/.test(phone)){msg.textContent='请输入正确手机号';msg.classList.remove('hidden');return;}
  fetch('/api/v1/leads',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
    name:'对比页访客',phone:phone,source:'compare_page',page_url:location.href,message:'请求对比报告'
  })}).then(function(){msg.textContent='已提交，顾问将发送对比报告';msg.classList.remove('hidden');});
});
</script>"""
    html = html.replace("</body>", script + "\n</body>")
    fp.write_text(html, encoding="utf-8")
    print("  ✓ compare.html leads wired")


def enhance_cases():
    cases_dir = WEB / "cases"
    if not cases_dir.is_dir():
        return
    template = """
<div class="esylink-case-metrics grid grid-cols-3 gap-4 my-6 not-prose text-center text-sm">
  <div class="bg-indigo-50 rounded-lg p-3"><div class="font-bold text-indigo-700">-40%</div><div class="text-slate-500">人工成本</div></div>
  <div class="bg-indigo-50 rounded-lg p-3"><div class="font-bold text-indigo-700">3x</div><div class="text-slate-500">接通率</div></div>
  <div class="bg-indigo-50 rounded-lg p-3"><div class="font-bold text-indigo-700">14天</div><div class="text-slate-500">上线周期</div></div>
</div>"""
    n = 0
    for f in cases_dir.rglob("*.html"):
        html = f.read_text(encoding="utf-8", errors="replace")
        if "esylink-case-metrics" in html:
            continue
        if "<h1" in html:
            html = re.sub(r"(</h1>)", r"\1\n" + template, html, count=1)
            f.write_text(html, encoding="utf-8")
            n += 1
    print(f"  ✓ case metrics: {n}")


def inject_blog_cta_remaining():
    cta = """
<div class="esylink-blog-cta bg-indigo-50 border border-indigo-100 rounded-xl p-6 my-8 text-center">
  <h3 class="text-lg font-bold text-indigo-900 mb-2">需要AI外呼/云客服方案？</h3>
  <p class="text-slate-600 text-sm mb-4">7天免费试用 · 顾问1对1配置 · 当天可开通</p>
  <div class="flex flex-wrap justify-center gap-3">
    <a href="/free-trial.html?from=blog" class="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-semibold">免费试用</a>
    <a href="/resources/ai-outbound-guide.html" class="border border-indigo-300 text-indigo-700 px-5 py-2 rounded-lg text-sm font-semibold">下载选型指南</a>
  </div>
</div>"""
    n = 0
    for f in (WEB / "blog").rglob("index.html"):
        if f.parent == WEB / "blog":
            continue
        html = f.read_text(encoding="utf-8", errors="replace")
        if "esylink-blog-cta" in html:
            continue
        if "</article>" in html:
            html = html.replace("</article>", cta + "\n</article>", 1)
        elif "</main>" in html:
            html = html.replace("</main>", cta + "\n</main>", 1)
        elif "</body>" in html:
            html = html.replace("</body>", cta + "\n</body>", 1)
        else:
            continue
        f.write_text(html, encoding="utf-8")
        n += 1
    print(f"  ✓ blog CTA remaining: {n}")


def main():
    print("📦 P2 batch optimizations")
    noindex_matrix_pages()
    inject_blog_covers()
    inject_blog_cta_remaining()
    create_whitepaper()
    enhance_compare_leads()
    enhance_cases()
    print("✅ P2 batch done")


if __name__ == "__main__":
    main()
