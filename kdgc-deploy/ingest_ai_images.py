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
    "og-share": "og-share",
    "banner-about": "about/banner-about",
    "team-scientist-silhouette": "about/team-scientist",
    "team-gm-silhouette": "about/team-gm",
    "team-cto-silhouette": "about/team-cto",
    "lab-environment-1": "about/lab-1",
    "lab-environment-2": "about/lab-2",
    "product-kd0100-02s-t1": "products/kd0100-02s-t1",
    "product-kd0100-02s-to": "products/kd0100-02s-to",
    "product-mask-o2-sensor": "products/mask-o2-sensor",
    "product-exploded": "products/exploded",
    "product-controller-kd0100-03": "products/controller-kd0100-03",
    "scene-automotive": "scenes/automotive",
    "scene-aviation-mask": "scenes/aviation-mask",
    "scene-industrial-gas": "scenes/industrial-gas",
    "products-banner": "products/banner",
    "cover-team-building": "news/team-building-2022",
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
}


def find_cwebp() -> str | None:
    return shutil.which("cwebp") or shutil.which("magick")


def to_webp(src: Path, dst: Path, quality: int = 82) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cwebp = shutil.which("cwebp")
    if cwebp:
        r = subprocess.run(
            [cwebp, "-q", str(quality), str(src), "-o", str(dst)],
            capture_output=True,
        )
        return r.returncode == 0 and dst.exists()
    # Pillow fallback
    try:
        from PIL import Image

        im = Image.open(src).convert("RGBA" if src.suffix.lower() == ".png" else "RGB")
        if dst.suffix == ".webp":
            if im.mode == "RGBA":
                im.save(dst, "WEBP", quality=quality, method=6)
            else:
                im.save(dst, "WEBP", quality=quality, method=6)
        return dst.exists()
    except Exception as e:
        print("webp fail", src.name, e)
        # copy original as fallback with preferred name + original ext
        return False


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

        # also copy original as .jpg/.png for <picture> fallback
        out_orig = DIST_IMG / f"{rel}{src.suffix.lower().replace('jpeg', 'jpg')}"
        out_orig.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out_orig)
        # QR codes stay PNG for scan reliability
        if "wechat" in rel or "qr" in rel:
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
