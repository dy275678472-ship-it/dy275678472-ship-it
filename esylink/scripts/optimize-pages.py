#!/usr/bin/env python3
"""Batch-apply Esylink page optimizations to a static site directory.

Fixes applied:
  1. Inject page-track.js + esylink-chat.js where only conversion.js exists
  2. Normalize script tags to use defer
  3. Fix homepage OG title/description mismatch
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SCRIPT_BLOCK = """
<script src="/js/page-track.js" defer></script>
<script src="/js/esylink-chat.js" defer></script>"""

OG_HOME_FIX = {
    'content="易连云通信 — 智能云客服·400全国热线·AI座席助手 | esylink.cn"': (
        'content="易连云通信 — AI智能外呼·云客服·400全国热线 | esylink.cn"'
    ),
    'content="易连云通信提供一站式云客服、400电话、AI座席助手解决方案，覆盖全国500+城市，为企业降本增效。"': (
        'content="易连云通信AI智能外呼系统：DeepSeek大模型驱动，10大行业场景模板，53城本地化覆盖。智能外呼+云客服+400热线，为企业降本80%通信成本。"'
    ),
}


def optimize_html(path: Path, dry_run: bool = False) -> list[str]:
    changes: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text

    has_conv = "esylink-conversion.js" in text
    has_track = "page-track.js" in text
    has_chat = "esylink-chat.js" in text

    if has_conv and (not has_track or not has_chat):
        # Insert before closing body or after conversion.js
        if "esylink-conversion.js" in text:
            anchor = re.search(r'(<script[^>]*esylink-conversion\.js[^>]*></script>)', text)
            if anchor:
                insert = ""
                if not has_track:
                    insert += '\n<script src="/js/page-track.js" defer></script>'
                if not has_chat:
                    insert += '\n<script src="/js/esylink-chat.js" defer></script>'
                text = text[: anchor.end()] + insert + text[anchor.end() :]
                changes.append("inject tracking scripts")

    # Normalize defer on our scripts
    for js in ("page-track.js", "esylink-chat.js", "esylink-conversion.js"):
        text = re.sub(
            rf'(<script\s+src="/js/{re.escape(js)}"(?![^>]*defer)[^>]*)(>)',
            r'\1 defer\2',
            text,
        )

    # Homepage OG fix
    if path.name in ("index.html",) or path.name == "index":
        for old, new in OG_HOME_FIX.items():
            if old in text:
                text = text.replace(old, new)
                changes.append("fix og meta")

    if text != original:
        rel = str(path)
        if not dry_run:
            path.write_text(text, encoding="utf-8")
        changes.insert(0, rel)
    return changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="Site root (e.g. /var/www/esylink)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root: Path = args.root
    if not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")

    total = 0
    for html in sorted(root.rglob("*")):
        if html.suffix in (".html", "") and html.is_file():
            if html.suffix == "" and html.name not in ("about", "pricing"):
                # extensionless pages like /about, /pricing
                pass
            elif html.suffix == "" and html.name in ("about", "pricing"):
                pass
            elif html.suffix != ".html" and html.name not in ("about", "pricing"):
                continue

            result = optimize_html(html, dry_run=args.dry_run)
            if result:
                print(" → ".join(result))
                total += 1

    print(f"\n{'Would update' if args.dry_run else 'Updated'} {total} files")


if __name__ == "__main__":
    main()
