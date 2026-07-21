#!/usr/bin/env python3
"""Ingest AI-generated images into KDGC web assets (WebP) and wire known slots."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
INCOMING = ROOT / "assets-incoming"
DIST_IMG = ROOT / "frontend" / "dist" / "assets" / "images"

# incoming filename (stem match, any suffix) -> relative path under assets/images (without ext)
MAP = {
    "hero-oxygen-sensor": "home/hero-oxygen-sensor",
    "hero-oxygen-sensor-alt": "home/hero-oxygen-sensor-alt",
    "og-share": "og-share",
    "icon-iso": "home/icon-iso",
    "icon-patent": "home/icon-patent",
    "icon-deeptech": "home/icon-deeptech",
    "icon-warranty": "home/icon-warranty",
    "tech-illustration": "home/tech-illustration",
    "banner-about": "about/banner-about",
    "team-scientist-silhouette": "about/team-scientist",
    "team-gm-silhouette": "about/team-gm",
    "team-cto-silhouette": "about/team-cto",
    "lab-environment-1": "about/lab-1",
    "lab-environment-2": "about/lab-2",
    "honors-gallery-bg": "about/honors-gallery-bg",
    "partners-wall-bg": "about/partners-wall-bg",
    "product-kd0100-02s-t1": "products/kd0100-02s-t1",
    "product-kd0100-02s-to": "products/kd0100-02s-to",
    "product-mask-o2-sensor": "products/mask-o2-sensor",
    "product-probe-alt": "products/probe-alt",
    "product-exploded": "products/exploded",
    "product-controller-kd0100-03": "products/controller-kd0100-03",
    "product-controller-pcb": "products/controller-pcb",
    "scene-automotive": "scenes/automotive",
    "scene-aviation-mask": "scenes/aviation-mask",
    "scene-industrial-gas": "scenes/industrial-gas",
    "scene-industrial-steam": "scenes/industrial-steam",
    "products-banner": "products/banner",
    "cover-team-building": "news/team-building-2022",
    "cover-team-building-sheet": "news/team-building-sheet",
    "cover-nox-market": "news/nox-sensor-market",
    "cover-o2-explain": "news/understand-o2-sensor",
    "news-banner": "news/banner",
    "contact-campus": "contact/campus",
    "contact-banner": "contact/banner",
    "icon-response": "contact/icon-response",
    "icon-24h": "contact/icon-24h",
    "icon-location": "contact/icon-location",
    # alternate labels from contact sheet
    "07-01-contact-campus": "contact/campus",
    "07-02-contact-banner": "contact/banner",
    "07-03-icon-response": "contact/icon-response",
    "07-04-icon-24h": "contact/icon-24h",
    "07-05-icon-location": "contact/icon-location",
    # knowledge covers + banner
    "cover-vf-vs-traditional": "knowledge/cover-vf-vs-traditional",
    "cover-t1-vs-to": "knowledge/cover-t1-vs-to",
    "cover-pressure-range": "knowledge/cover-pressure-range",
    "cover-controller-wiring": "knowledge/cover-controller-wiring",
    "cover-scr-obd": "knowledge/cover-scr-obd",
    "cover-aviation-metrics": "knowledge/cover-aviation-metrics",
    "cover-accuracy-curve": "knowledge/cover-accuracy-curve",
    "cover-safety-maintenance": "knowledge/cover-safety-maintenance",
    "knowledge-banner": "knowledge/banner",
    # industry cases
    "case-aviation-mask": "cases/case-aviation-mask",
    "case-aviation-mask-process": "cases/case-aviation-mask-process",
    "case-industrial-monitoring": "cases/case-industrial-monitoring",
    "case-industrial-monitoring-process": "cases/case-industrial-monitoring-process",
    "case-pin-integration": "cases/case-pin-integration",
    "case-pin-integration-process": "cases/case-pin-integration-process",
    "case-scr-obd": "cases/case-scr-obd",
    "cases-banner": "cases/banner",
    # EN / decorative
    "hero-en": "home/hero-en",
    "footer-texture": "footer-texture",
}


def find_cwebp() -> str | None:
    return shutil.which("cwebp") or shutil.which("magick")


def _open_resized(src: Path, max_w: int = 1600):
    from PIL import Image

    im = Image.open(src)
    if src.suffix.lower() == ".png" and "icon" in src.stem.lower():
        im = im.convert("RGBA")
    else:
        im = im.convert("RGB")
    if im.width > max_w:
        h = int(im.height * (max_w / im.width))
        im = im.resize((max_w, h), Image.Resampling.LANCZOS)
    return im


def to_webp(src: Path, dst: Path, quality: int = 82) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    max_w = 1920 if "banner" in src.stem.lower() or "hero" in src.stem.lower() else 1600
    try:
        im = _open_resized(src, max_w=max_w)
        im.save(dst, "WEBP", quality=quality, method=6)
        return dst.exists()
    except Exception as e:
        print("webp fail", src.name, e)
        cwebp = shutil.which("cwebp")
        if cwebp:
            r = subprocess.run(
                [cwebp, "-q", str(quality), str(src), "-o", str(dst)],
                capture_output=True,
            )
            return r.returncode == 0 and dst.exists()
        return False


def write_compressed_orig(src: Path, dst: Path) -> None:
    """Write a resized JPEG/PNG sibling so dist stays lean."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    suffix = src.suffix.lower().replace("jpeg", "jpg")
    max_w = 1920 if "banner" in src.stem.lower() or "hero" in src.stem.lower() else 1600
    try:
        im = _open_resized(src, max_w=max_w)
        if suffix == ".png" and im.mode == "RGBA":
            im.save(dst, "PNG", optimize=True)
        else:
            if dst.suffix.lower() != ".jpg":
                dst = dst.with_suffix(".jpg")
            im.convert("RGB").save(dst, "JPEG", quality=85, optimize=True)
    except Exception:
        shutil.copy2(src, dst)


def normalize_stem(name: str) -> str:
    s = Path(name).stem.lower()
    for ch in " ·_":
        s = s.replace(ch, "-")
    while "--" in s:
        s = s.replace("--", "-")
    # strip leading batch numbers like 04-01-
    import re

    s = re.sub(r"^\d{2}-\d{2}-", "", s)
    return s


def main():
    if not INCOMING.exists():
        INCOMING.mkdir(parents=True)
        print("created", INCOMING)
    files = [
        p
        for p in INCOMING.rglob("*")
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    ]
    if not files:
        print("No images in", INCOMING)
        print("Drop files then re-run. See assets-incoming/README.md")
        return

    done = 0
    for src in files:
        key = normalize_stem(src.name)
        # try direct and with product- prefix stripped variants
        rel = MAP.get(key)
        if not rel:
            # fuzzy: endswith known key
            for k, v in MAP.items():
                if key.endswith(k) or k in key:
                    rel = v
                    break
        if not rel:
            print("SKIP unknown name:", src.name, "→ stem", key)
            continue

        # also copy compressed original as .jpg/.png for <picture> fallback
        out_orig = DIST_IMG / f"{rel}{src.suffix.lower().replace('jpeg', 'jpg')}"
        write_compressed_orig(src, out_orig)
        # QR codes stay PNG for scan reliability
        if "wechat" in rel or "qr" in rel:
            shutil.copy2(src, out_orig)
            print("COPIED (png keep)", src.name, "→", rel)
            done += 1
            continue
        out_webp = DIST_IMG / f"{rel}.webp"
        ok = to_webp(src, out_webp)

        # special: og-share → site root og-image
        if rel == "og-share":
            root = ROOT / "frontend" / "dist"
            if out_webp.exists():
                shutil.copy2(out_webp, root / "og-image.webp")
            shutil.copy2(src, root / "og-image.png" if src.suffix.lower() == ".png" else root / "og-image.jpg")
            if (root / "og-image.jpg").exists() and not (root / "og-image.png").exists():
                # keep png name expected by meta if only jpg
                pass

        # product webp also update legacy .png references used by generate_pages
        if rel.startswith("products/") and out_webp.exists():
            # keep png/jpg sibling for current generator paths
            legacy = DIST_IMG / f"{rel}.png"
            if src.suffix.lower() == ".png":
                shutil.copy2(src, legacy)

        print(("OK" if ok else "COPIED"), src.name, "→", rel)
        done += 1

    print(f"done {done}/{len(files)}")
    # refresh HTML so new WebP paths are preferred
    gen = ROOT / "generate_pages.py"
    if gen.exists():
        subprocess.run(["python3", str(gen)], check=False)
        print("regenerated pages")
    else:
        print("Next: python3 generate_pages.py")


if __name__ == "__main__":
    main()
