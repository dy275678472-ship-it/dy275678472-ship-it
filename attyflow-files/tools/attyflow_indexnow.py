#!/usr/bin/env python3
"""Submit attyflow.com URLs to IndexNow (Bing, Yandex, etc.)."""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path("/var/www/attyflow")
KEY_FILE = ROOT / "indexnow-key.txt"
SITEMAP = ROOT / "sitemap.xml"
HOST = "attyflow.com"
ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
]


def load_urls(limit: int = 0) -> list[str]:
    if not SITEMAP.exists():
        return []
    text = SITEMAP.read_text(encoding="utf-8")
    import re
    urls = re.findall(r"<loc>(https://attyflow\.com[^<]+)</loc>", text)
    if limit:
        return urls[:limit]
    return urls


def submit(urls: list[str]) -> None:
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    payload = json.dumps({"host": HOST, "key": key, "urlList": urls}).encode()
    for endpoint in ENDPOINTS:
        req = urllib.request.Request(
            endpoint, data=payload, method="POST", headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                print(f"{endpoint}: {resp.status} ({len(urls)} urls)")
        except Exception as exc:
            print(f"{endpoint}: FAILED {exc}", file=sys.stderr)


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    urls = load_urls(limit)
    if not urls:
        print("No URLs found")
        sys.exit(1)
    # IndexNow accepts up to 10,000 URLs per request
    batch = 200
    for i in range(0, len(urls), batch):
        submit(urls[i : i + batch])


if __name__ == "__main__":
    main()
