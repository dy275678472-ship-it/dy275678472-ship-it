#!/usr/bin/env python3
import json
import urllib.request
from xml.etree import ElementTree as ET

HOST = "tianshu.online"
KEY = "tianshu-online"
SITEMAP = f"https://{HOST}/sitemap.xml"

with urllib.request.urlopen(SITEMAP, timeout=60) as r:
    xml = r.read()

urls = [
    el.text
    for el in ET.fromstring(xml).iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    if el.text
]

for i in range(0, len(urls), 100):
    batch = urls[i : i + 100]
    payload = json.dumps({"host": HOST, "key": KEY, "urlList": batch}).encode()
    for endpoint in ["https://www.bing.com/indexnow", "https://api.indexnow.org/indexnow"]:
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                print(f"batch {i // 100 + 1} -> {endpoint}: {resp.status} ({len(batch)} urls)")
        except Exception as e:
            print(f"batch {i // 100 + 1} -> {endpoint}: {e}")

print(f"total {len(urls)} urls")
