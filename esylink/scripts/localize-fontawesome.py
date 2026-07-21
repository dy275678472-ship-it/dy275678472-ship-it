#!/usr/bin/env python3
"""Replace Font Awesome CDN with self-hosted files (~150KB vs CDN latency)."""
from __future__ import annotations

import os
import re
import sys
import urllib.request
from pathlib import Path

WEB = Path(os.environ.get("ESYLINK_WEB", "/var/www/esylink"))

FA_VERSION = "6.5.0"
CDN_CSS = f"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{FA_VERSION}/css/all.min.css"
LOCAL_CSS = "/css/fontawesome/all.min.css"
CSS_DIR = WEB / "css" / "fontawesome"
WEBFONTS_DIR = WEB / "webfonts"

CDN_PATTERNS = [
    re.compile(r'<link[^>]*href=["\']https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/[^"\']+["\'][^>]*>', re.I),
    re.compile(r'<link[^>]*href=["\']https://cdn\.jsdelivr\.net/npm/@fortawesome/[^"\']+["\'][^>]*>', re.I),
]
LOCAL_LINK = f'<link rel="stylesheet" href="{LOCAL_CSS}">'


def download_assets():
    CSS_DIR.mkdir(parents=True, exist_ok=True)
    WEBFONTS_DIR.mkdir(parents=True, exist_ok=True)

    css_path = CSS_DIR / "all.min.css"
    if not css_path.exists() or css_path.stat().st_size < 1000:
        print(f"  Downloading FA CSS {FA_VERSION}...")
        urllib.request.urlretrieve(CDN_CSS, css_path)

    css = css_path.read_text(encoding="utf-8")
    fonts = set(re.findall(r"url\(\.\./webfonts/([^)]+)\)", css))
    base = f"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/{FA_VERSION}/webfonts/"
    for font in fonts:
        dest = WEBFONTS_DIR / font
        if not dest.exists():
            print(f"  Downloading {font}...")
            urllib.request.urlretrieve(base + font, dest)

    # Fix paths: ../webfonts/ → /webfonts/
    fixed = css.replace("../webfonts/", "/webfonts/")
    if fixed != css:
        css_path.write_text(fixed, encoding="utf-8")
    print(f"  ✓ Assets ready ({len(fonts)} font files)")


def replace_in_html():
    changed = 0
    for f in WEB.rglob("*.html"):
        text = f.read_text(encoding="utf-8", errors="replace")
        orig = text
        for pat in CDN_PATTERNS:
            text = pat.sub(LOCAL_LINK, text)
        if text != orig:
            f.write_text(text, encoding="utf-8")
            changed += 1
    print(f"  ✓ Updated {changed} HTML files")


def main():
    if not WEB.is_dir():
        print(f"ERROR: {WEB} not found")
        sys.exit(1)
    print("🔤 Font Awesome localization")
    download_assets()
    replace_in_html()
    print("✅ Done")


if __name__ == "__main__":
    main()
