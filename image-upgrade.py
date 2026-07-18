#!/usr/bin/env python3
"""Replace low-quality SVG/emoji placeholders with real images on momei.ink and siamsaas.com."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

MOMEI = Path("/opt/momei-v3/frontend")
SIAM = Path("/opt/bangkok-edge/frontend")
TMP = Path("/tmp")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def to_webp(src: Path, dst: Path, w: int, h: int) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x0b1324",
        "-q:v", "80", str(dst),
    ])


def to_png_icon(src: Path, dst: Path, size: int) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", f"scale={size}:{size}:force_original_aspect_ratio=decrease,pad={size}:{size}:(ow-iw)/2:(oh-ih)/2:color=0x0b1324",
        str(dst),
    ])


def prepare_assets() -> None:
    # Momei scenario images
    momei_img = MOMEI / "images"
    scenarios = momei_img / "scenarios"
    scenarios.mkdir(parents=True, exist_ok=True)
    mapping = {
        "momei-boi-scenario.png": "boi.webp",
        "momei-abnt-scenario.png": "abnt.webp",
        "momei-tci-scenario.png": "tci.webp",
    }
    for src_name, dst_name in mapping.items():
        src = TMP / src_name
        if not src.exists():
            src = momei_img / src_name
        if src.exists():
            to_webp(src, scenarios / dst_name, 640, 360)

    logo_src = TMP / "momei-logo-icon.png"
    if not logo_src.exists():
        logo_src = momei_img / "momei-logo-icon.png"
    if logo_src.exists():
        to_png_icon(logo_src, momei_img / "favicon.png", 64)
        to_png_icon(logo_src, momei_img / "logo-icon.png", 128)
        run(["cp", str(logo_src), str(momei_img / "momei-logo-icon.png")])

    # SiamSaaS favicon + step icons from existing photos
    siam_img = SIAM / "images"
    og = siam_img / "og-card.webp"
    if og.exists():
        to_png_icon(og, siam_img / "favicon.png", 64)

    icons = siam_img / "icons"
    icons.mkdir(exist_ok=True)
    pairs = [
        (siam_img / "line-mockup.webp", icons / "step-connect.webp", 96, 96),
        (siam_img / "dashboard-graph.webp", icons / "step-ai.webp", 96, 96),
        (siam_img / "thai-businessman.webp", icons / "step-broadcast.webp", 96, 96),
        (siam_img / "thai-shop-owner.webp", icons / "segment-fashion.webp", 96, 96),
        (siam_img / "thai-businessman.webp", icons / "segment-beauty.webp", 96, 96),
        (siam_img / "team-thai.webp", icons / "segment-restaurant.webp", 96, 96),
    ]
    for src, dst, w, h in pairs:
        if src.exists():
            to_webp(src, dst, w, h)

    print("✓ Assets prepared")


FAVICON_OLD = re.compile(
    r'<link rel="icon" href="data:image/svg\+xml[^"]*">',
    re.I,
)
FAVICON_NEW = (
    '<link rel="icon" href="/images/favicon.png" type="image/png" sizes="64x64">\n'
    '<link rel="apple-touch-icon" href="/images/og-card.webp">'
)


def patch_html_files(root: Path, patches: list[tuple[str, str]], label: str) -> int:
    count = 0
    for p in root.rglob("*.html"):
        if "node_modules" in str(p):
            continue
        t = p.read_text(encoding="utf-8")
        orig = t
        for old, new in patches:
            if old in t:
                t = t.replace(old, new)
        t = FAVICON_OLD.sub(FAVICON_NEW, t)
        if t != orig:
            p.write_text(t, encoding="utf-8")
            count += 1
    print(f"  ✓ {label}: {count} files")
    return count


def patch_momei() -> None:
    css_path = MOMEI / "assets" / "site.css"
    css = css_path.read_text(encoding="utf-8")
    extra = """
.logo{display:flex;align-items:center;gap:10px}
.logo-icon{width:28px;height:28px;border-radius:8px;object-fit:cover}
.scenario-thumb{width:100%;height:140px;object-fit:cover;border-radius:12px;margin-bottom:12px;display:block}
.sample-thumb{width:100%;height:120px;object-fit:cover;border-radius:10px;margin-bottom:12px;display:block;opacity:.92}
"""
    if ".scenario-thumb" not in css:
        css_path.write_text(css + extra, encoding="utf-8")

    patches = [
        (
            '<a class="logo" href="/">📄 <span>Momei</span></a>',
            '<a class="logo" href="/"><img src="/images/logo-icon.png" alt="" class="logo-icon" width="28" height="28"><span>Momei</span></a>',
        ),
        (
            '<div class="scenario-flag">🇹🇭</div>',
            '<img src="/images/scenarios/boi.webp" alt="Thailand BOI proposal" class="scenario-thumb" width="640" height="360" loading="lazy">',
        ),
        (
            '<div class="scenario-flag">🇧🇷</div>',
            '<img src="/images/scenarios/abnt.webp" alt="Brazil ABNT academic paper" class="scenario-thumb" width="640" height="360" loading="lazy">',
        ),
        (
            '<div class="scenario-flag">📚</div>',
            '<img src="/images/scenarios/tci.webp" alt="TCI journal article" class="scenario-thumb" width="640" height="360" loading="lazy">',
        ),
        (
            '<div class="doc-preview"><h3>BOI Investment Proposal</h3>',
            '<img src="/images/scenarios/boi.webp" alt="" class="sample-thumb" loading="lazy"><div class="doc-preview"><h3>BOI Investment Proposal</h3>',
        ),
        (
            '<div class="doc-preview"><h3>ABNT Academic Paper</h3>',
            '<img src="/images/scenarios/abnt.webp" alt="" class="sample-thumb" loading="lazy"><div class="doc-preview"><h3>ABNT Academic Paper</h3>',
        ),
        (
            '<div class="doc-preview"><h3>TCI Journal Article</h3>',
            '<img src="/images/scenarios/tci.webp" alt="" class="sample-thumb" loading="lazy"><div class="doc-preview"><h3>TCI Journal Article</h3>',
        ),
    ]
    patch_html_files(MOMEI, patches, "momei HTML")
    # index only: add hero visual if missing
    idx = MOMEI / "index.html"
    t = idx.read_text(encoding="utf-8")
    if "hero-visual" not in t and 'class="hero wrap"' in t:
        hero_img = (
            '<div class="hero-visual" style="max-width:920px;margin:0 auto 28px;padding:0 22px">'
            '<img src="/images/og-card.webp" alt="Momei AI document generator preview" '
            'width="1200" height="630" loading="eager" style="width:100%;border-radius:18px;border:1px solid rgba(129,140,248,.2);box-shadow:0 20px 60px rgba(0,0,0,.35)">'
            "</div>"
        )
        t = t.replace('<section class="hero wrap">', hero_img + '<section class="hero wrap">', 1)
        idx.write_text(t, encoding="utf-8")
        print("  ✓ momei hero visual added")


def rebuild_momei_frontend() -> None:
    """Frontend is baked into Docker; host file changes need image rebuild."""
    run([
        "docker", "compose", "-f", "/opt/momei-v3/docker-compose.yml",
        "build", "frontend",
    ])
    run([
        "docker", "compose", "-f", "/opt/momei-v3/docker-compose.yml",
        "up", "-d", "frontend",
    ])
    print("  ✓ momei frontend container rebuilt")


def patch_siamsaas() -> None:
    css_path = SIAM / "assets" / "site.css"
    css = css_path.read_text(encoding="utf-8")
    extra = """
.how-icon-img{width:56px;height:56px;border-radius:14px;object-fit:cover;margin:0 auto 10px;display:block;border:2px solid rgba(212,175,55,.2)}
.sp-icon-img{width:48px;height:48px;border-radius:50%;object-fit:cover;margin:0 auto 6px;display:block;border:2px solid rgba(212,175,55,.25)}
.preview-thumb{width:100%;height:100px;object-fit:cover;border-radius:10px;margin-bottom:10px;display:block}
"""
    if ".how-icon-img" not in css:
        css_path.write_text(css + extra, encoding="utf-8")

    idx = SIAM / "index.html"
    t = idx.read_text(encoding="utf-8")
    replacements = [
        (
            '<div class="how-icon">🔗</div>',
            '<img src="/images/icons/step-connect.webp" alt="เชื่อมต่อ LINE OA" class="how-icon-img" width="56" height="56" loading="lazy">',
        ),
        (
            '<div class="how-icon">🧠</div>',
            '<img src="/images/icons/step-ai.webp" alt="AI วิเคราะห์" class="how-icon-img" width="56" height="56" loading="lazy">',
        ),
        (
            '<div class="how-icon">✉️</div>',
            '<img src="/images/icons/step-broadcast.webp" alt="ส่ง Broadcast" class="how-icon-img" width="56" height="56" loading="lazy">',
        ),
        (
            '<div class="sp-item"><div class="num">42%</div><div class="label">ประหยัดเฉลี่ย (Beta)</div></div>',
            '<div class="sp-item"><img src="/images/dashboard-graph.webp" alt="" class="sp-icon-img" width="48" height="48" loading="lazy"><div class="num">42%</div><div class="label">ประหยัดเฉลี่ย (Beta)</div></div>',
        ),
        (
            '<div class="sp-item"><div class="num">👗</div><div class="label">ร้านเสื้อผ้า</div></div>',
            '<div class="sp-item"><img src="/images/icons/segment-fashion.webp" alt="ร้านเสื้อผ้า" class="sp-icon-img" width="48" height="48" loading="lazy"><div class="label">ร้านเสื้อผ้า</div></div>',
        ),
        (
            '<div class="sp-item"><div class="num">💆</div><div class="label">คลินิกความงาม</div></div>',
            '<div class="sp-item"><img src="/images/icons/segment-beauty.webp" alt="คลินิกความงาม" class="sp-icon-img" width="48" height="48" loading="lazy"><div class="label">คลินิกความงาม</div></div>',
        ),
        (
            '<div class="sp-item"><div class="num">🍜</div><div class="label">ร้านอาหาร</div></div>',
            '<div class="sp-item"><img src="/images/icons/segment-restaurant.webp" alt="ร้านอาหาร" class="sp-icon-img" width="48" height="48" loading="lazy"><div class="label">ร้านอาหาร</div></div>',
        ),
        (
            '<div class="preview-card-header">🏷️ AI แท็กลูกค้าอัตโนมัติ</div>',
            '<img src="/images/line-mockup.webp" alt="LINE OA tagging" class="preview-thumb" loading="lazy"><div class="preview-card-header">AI แท็กลูกค้าอัตโนมัติ</div>',
        ),
        (
            '<div class="preview-card-header">💰 เปรียบเทียบค่าส่ง LINE</div>',
            '<img src="/images/dashboard-graph.webp" alt="Cost comparison chart" class="preview-thumb" loading="lazy"><div class="preview-card-header">เปรียบเทียบค่าส่ง LINE</div>',
        ),
        (
            '<div class="preview-card-header">📊 ผลลัพธ์ร้านค้าจริง</div>',
            '<img src="/images/team-thai.webp" alt="ผลลัพธ์ร้านค้า" class="preview-thumb" loading="lazy"><div class="preview-card-header">ผลลัพธ์ร้านค้าจริง</div>',
        ),
        (
            '<span class="flag">🇹🇭</span>',
            '<img src="/images/favicon.png" alt="" width="22" height="22" style="border-radius:6px">',
        ),
    ]
    for old, new in replacements:
        t = t.replace(old, new)
    t = FAVICON_OLD.sub(FAVICON_NEW, t)
    idx.write_text(t, encoding="utf-8")
    print("  ✓ siamsaas index.html")

    logo_old = '<div class="logo"><a href="https://siamsaas.com">🇹🇭 <span>Siam</span>SaaS</a></div>'
    logo_new = (
        '<div class="logo"><a href="https://siamsaas.com">'
        '<img src="/images/favicon.png" alt="" width="22" height="22" style="border-radius:6px;vertical-align:middle;margin-right:6px">'
        '<span>Siam</span>SaaS</a></div>'
    )
    patch_html_files(SIAM, [(logo_old, logo_new)], "siamsaas logo HTML")

    partners = SIAM / "partners.html"
    if partners.exists():
        pt = partners.read_text(encoding="utf-8")
        partner_patches = [
            (
                '<div class="step">\n      <div class="icon">📝</div>',
                '<div class="step">\n      <img src="/images/icons/step-ai.webp" alt="" class="how-icon-img" width="56" height="56" loading="lazy">',
            ),
            (
                '<div class="step">\n      <div class="icon">🔗</div>',
                '<div class="step">\n      <img src="/images/icons/step-connect.webp" alt="" class="how-icon-img" width="56" height="56" loading="lazy">',
            ),
            (
                '<div class="step">\n      <div class="icon">💰</div>',
                '<div class="step">\n      <img src="/images/dashboard-graph.webp" alt="" class="how-icon-img" width="56" height="56" loading="lazy">',
            ),
            (
                '<div class="benefit"><div class="icon">📊</div>',
                '<div class="benefit"><img src="/images/dashboard-graph.webp" alt="" class="how-icon-img" width="48" height="48" loading="lazy">',
            ),
            (
                '<div class="benefit"><div class="icon">🏷️</div>',
                '<div class="benefit"><img src="/images/line-mockup.webp" alt="" class="how-icon-img" width="48" height="48" loading="lazy">',
            ),
            (
                '<div class="benefit"><div class="icon">🎓</div>',
                '<div class="benefit"><img src="/images/team-thai.webp" alt="" class="how-icon-img" width="48" height="48" loading="lazy">',
            ),
        ]
        for old, new in partner_patches:
            pt = pt.replace(old, new)
        partners.write_text(pt, encoding="utf-8")
        print("  ✓ siamsaas partners.html icons")

    # Dashboard sidebar phone mockup - ensure uses webp
    dash = SIAM / "dashboard.html"
    dt = dash.read_text(encoding="utf-8")
    if "line-mockup.webp" not in dt and "line-mockup.jpg" in dt:
        dt = dt.replace("/images/line-mockup.jpg", "/images/line-mockup.webp")
        dash.write_text(dt, encoding="utf-8")
        print("  ✓ dashboard line-mockup webp")


def main() -> None:
    print("🖼️ Image upgrade deploy\n")
    prepare_assets()
    patch_momei()
    patch_siamsaas()
    rebuild_momei_frontend()
    print("\n✅ Done")


if __name__ == "__main__":
    main()
