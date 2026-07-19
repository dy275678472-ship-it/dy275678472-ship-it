#!/usr/bin/env python3
"""Generate professional SVG logo marks for esnlink.cn trust wall."""

from pathlib import Path

OUT = Path(__file__).parent / "site" / "assets" / "logos"
OUT.mkdir(parents=True, exist_ok=True)

# (filename, title, subtitle/monogram, primary color)
LOGOS = [
    ("telecom-ct.svg", "中国电信", "CT", "#0066b3"),
    ("telecom-cm.svg", "中国移动", "CM", "#00a0e9"),
    ("telecom-cu.svg", "中国联通", "CU", "#e60012"),
    ("satellite.svg", "中国星网", "GW", "#1e3a5f"),
    ("finance.svg", "城商行联盟", "CB", "#b45309"),
    ("education.svg", "职教集团", "VE", "#7c3aed"),
    ("ecommerce.svg", "头部电商", "EC", "#ea580c"),
    ("healthcare.svg", "社区医院", "CH", "#0891b2"),
]

TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 48" role="img" aria-label="{title}">
  <rect width="160" height="48" rx="8" fill="#f8fafc"/>
  <circle cx="24" cy="24" r="16" fill="{color}" opacity="0.12"/>
  <text x="24" y="28" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" font-weight="700" fill="{color}">{mono}</text>
  <text x="88" y="28" text-anchor="middle" font-family="system-ui,sans-serif" font-size="13" font-weight="600" fill="#334155">{title}</text>
</svg>'''

for fname, title, mono, color in LOGOS:
    (OUT / fname).write_text(TEMPLATE.format(title=title, mono=mono, color=color), encoding="utf-8")
    print(f"Created {fname}")

print(f"Done: {len(LOGOS)} logos in {OUT}")
