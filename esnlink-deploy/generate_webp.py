#!/usr/bin/env python3
"""Generate WebP version of og-image.png."""

from pathlib import Path

try:
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "pillow", "-q"])
    from PIL import Image

src = Path(__file__).parent / "site" / "og-image.png"
dst = Path(__file__).parent / "site" / "og-image.webp"
if src.exists():
    img = Image.open(src).convert("RGB")
    img.save(dst, "WEBP", quality=85)
    print(f"Generated {dst} ({dst.stat().st_size} bytes)")
else:
    print("og-image.png not found, run generate_og_image.py first")
