#!/usr/bin/env python3
"""Generate KDGC brand logos: ZH「中科国瓷」, EN「KDGC」 — text-only wordmarks."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend/dist/assets/images"

WHITE = (255, 255, 255)
BLUE = (24, 144, 255)

FONT_ZH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
FONT_EN = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def make_wordmark(text: str, font_path: str, font_size: int, *, tracking: int = 0) -> Image.Image:
    font = ImageFont.truetype(font_path, font_size)
    probe = Image.new("RGBA", (1, 1))
    draw_probe = ImageDraw.Draw(probe)
    tw, th = text_size(draw_probe, text, font)
    if tracking:
        tw += tracking * max(len(text) - 1, 0)

    pad_x, pad_y = 4, 6
    width = tw + pad_x * 2
    height = th + pad_y * 2
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    x = pad_x
    y = pad_y - 1
    if tracking:
        for i, ch in enumerate(text):
            draw.text((x, y), ch, font=font, fill=WHITE)
            cw, _ = text_size(draw, ch, font)
            x += cw + tracking
    else:
        draw.text((x, y), text, font=font, fill=WHITE)

    return img


def save_assets(img: Image.Image, stem: str) -> None:
    png = OUT / f"{stem}.png"
    webp = OUT / f"{stem}.webp"
    img.save(png, "PNG", optimize=True)
    img.save(webp, "WEBP", quality=95, method=6)
    print(f"wrote {png} ({img.size[0]}x{img.size[1]})")


def write_svg(text: str, path: Path, *, en: bool = False) -> None:
    if en:
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 48" role="img" aria-label="KDGC">
  <text x="0" y="36" fill="#ffffff" font-family="DejaVu Sans, Arial, sans-serif" font-size="36" font-weight="700" letter-spacing="3">KDGC</text>
</svg>"""
    else:
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 48" role="img" aria-label="中科国瓷">
  <text x="0" y="36" fill="#ffffff" font-family="WenQuanYi Micro Hei, Noto Sans SC, sans-serif" font-size="34" font-weight="700">中科国瓷</text>
</svg>"""
    path.write_text(svg, encoding="utf-8")
    print(f"wrote {path}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    zh = make_wordmark("中科国瓷", FONT_ZH, 44)
    en = make_wordmark("KDGC", FONT_EN, 48, tracking=4)

    save_assets(zh, "logo")
    save_assets(en, "logo-en")
    save_assets(zh, "logo-full")
    write_svg("中科国瓷", OUT / "logo.svg")
    write_svg("KDGC", OUT / "logo-en.svg", en=True)


if __name__ == "__main__":
    main()
