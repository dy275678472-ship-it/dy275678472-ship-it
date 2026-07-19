#!/usr/bin/env python3
"""Generate og-image.png (1200x630) for esnlink.cn social sharing."""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
img = Image.new("RGB", (W, H), "#0f172a")
draw = ImageDraw.Draw(img)

# gradient background bars
for i in range(W):
    r = int(15 + (37 - 15) * i / W)
    g = int(23 + (99 - 23) * i / W)
    b = int(42 + (235 - 42) * i / W)
    draw.line([(i, 0), (i, H)], fill=(r, g, b))

# decorative circles
draw.ellipse([800, -100, 1200, 300], fill=(37, 99, 235, 30))
draw.ellipse([-50, 400, 350, 700], fill=(8, 145, 178, 40))

# text
try:
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
    sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    tag_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
except OSError:
    title_font = ImageFont.load_default()
    sub_font = ImageFont.load_default()
    tag_font = ImageFont.load_default()

draw.text((80, 180), "esnlink · 翼星科技", fill="#60a5fa", font=title_font)
draw.text((80, 270), "让企业通信更智能、更省钱", fill="#ffffff", font=sub_font)
draw.text((80, 340), "AI 外呼 · 短信平台 · 物联网 · 一站式接入", fill="#94a3b8", font=tag_font)
draw.text((80, 420), "短信 0.03元/条起  |  外呼 0.08元/分钟起  |  免费试用14天", fill="#f59e0b", font=tag_font)

# mockup panel
draw.rounded_rectangle([720, 120, 1120, 520], radius=16, fill="#1e293b", outline="#334155")
draw.text((750, 150), "控制台实时数据", fill="#64748b", font=tag_font)
for idx, (val, lbl) in enumerate([("12,847", "今日外呼"), ("99.2%", "接通率"), ("3.2M", "短信发送")]):
    x = 750 + idx * 115
    draw.rounded_rectangle([x, 200, x + 100, 270], radius=8, fill="#0f172a")
    draw.text((x + 10, 210), val, fill="#60a5fa", font=tag_font)
    draw.text((x + 10, 240), lbl, fill="#64748b", font=tag_font)

out = "/workspace/esnlink-deploy/site/og-image.png"
img.save(out, "PNG", optimize=True)
print(f"Generated {out} ({W}x{H})")
