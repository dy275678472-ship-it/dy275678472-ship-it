#!/usr/bin/env python3
"""Esylink.cn health & SEO audit — run locally or in CI."""

from __future__ import annotations

import argparse
import re
import ssl
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Iterable

BASE = "https://esylink.cn"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

KEY_PAGES = [
    "/",
    "/dialer/",
    "/cs/",
    "/pricing",
    "/free-trial.html",
    "/contact.html",
    "/about",
    "/cases/",
    "/400.html",
]


@dataclass
class Issue:
    level: str  # error | warn | info
    category: str
    message: str


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)

    def add(self, level: str, category: str, message: str) -> None:
        self.issues.append(Issue(level, category, message))

    @property
    def ok(self) -> bool:
        return not any(i.level == "error" for i in self.issues)


def fetch(url: str, method: str = "GET", timeout: int = 20) -> tuple[int, str, dict]:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": "EsylinkHealthCheck/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body, dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body, dict(e.headers) if e.headers else {}


def check_http(report: Report, path: str) -> None:
    url = f"{BASE}{path}"
    status, body, headers = fetch(url)
    if status != 200:
        report.add("error", "http", f"{path} returned HTTP {status}")
        return
    if len(body) < 500:
        report.add("warn", "http", f"{path} body suspiciously small ({len(body)} bytes)")
    if "text/html" not in headers.get("Content-Type", ""):
        report.add("warn", "http", f"{path} Content-Type: {headers.get('Content-Type')}")
    if "strict-transport-security" not in headers:
        report.add("warn", "security", f"{path} missing HSTS header")


def check_seo_meta(report: Report, path: str, body: str) -> None:
    title = re.search(r"<title>([^<]+)</title>", body)
    desc = re.search(r'name="description"\s+content="([^"]*)"', body)
    h1s = re.findall(r"<h1[^>]*>", body)
    canonical = re.search(r'rel="canonical"\s+href="([^"]+)"', body)

    if not title:
        report.add("error", "seo", f"{path} missing <title>")
    elif len(title.group(1)) > 70:
        report.add("warn", "seo", f"{path} title too long ({len(title.group(1))} chars)")

    if not desc:
        report.add("warn", "seo", f"{path} missing meta description")
    elif len(desc.group(1)) < 50:
        report.add("warn", "seo", f"{path} meta description short ({len(desc.group(1))} chars)")

    if len(h1s) == 0:
        report.add("warn", "seo", f"{path} missing H1")
    elif len(h1s) > 1:
        report.add("info", "seo", f"{path} has {len(h1s)} H1 tags")

    if not canonical and path not in ("/",):
        report.add("info", "seo", f"{path} no canonical tag")


def check_scripts(report: Report, path: str, body: str) -> None:
    has_conv = "esylink-conversion.js" in body
    has_track = "page-track.js" in body
    has_chat = "esylink-chat.js" in body

    if has_conv and not has_track:
        report.add("warn", "conversion", f"{path} has conversion.js but missing page-track.js")
    if has_conv and not has_chat:
        report.add("warn", "conversion", f"{path} has conversion.js but missing esylink-chat.js")


def check_sitemaps(report: Report) -> None:
    status, body, _ = fetch(f"{BASE}/sitemap-index.xml")
    if status != 200:
        report.add("error", "sitemap", f"sitemap-index.xml HTTP {status}")
        return

    root = ET.fromstring(body)
    sitemaps = [el.find("sm:loc", NS).text for el in root.findall("sm:sitemap", NS)]
    report.add("info", "sitemap", f"found {len(sitemaps)} sub-sitemaps")

    stale = []
    for sm_url in sitemaps:
        sm_status, sm_body, _ = fetch(sm_url)
        if sm_status != 200:
            report.add("error", "sitemap", f"{sm_url} HTTP {sm_status}")
            continue
        sm_root = ET.fromstring(sm_body)
        urls = sm_root.findall("sm:url", NS)
        lastmods = [u.find("sm:lastmod", NS) for u in urls if u.find("sm:lastmod", NS) is not None]
        if lastmods:
            latest = max(lm.text for lm in lastmods if lm is not None and lm.text)
            if latest < "2026-07-01":
                stale.append((sm_url, latest, len(urls)))
    for url, lastmod, count in stale:
        report.add("warn", "sitemap", f"{url}: {count} URLs, latest lastmod {lastmod}")


def check_apis(report: Report) -> None:
    for path in ["/api/analytics/tracker.js", "/js/page-track.js", "/js/esylink-chat.js"]:
        status, _, _ = fetch(f"{BASE}{path}")
        if status != 200:
            report.add("error", "assets", f"{path} HTTP {status}")


def run_audit(pages: Iterable[str] | None = None) -> Report:
    report = Report()
    targets = list(pages or KEY_PAGES)

    for path in targets:
        status, body, _ = fetch(f"{BASE}{path}")
        if status == 200:
            check_seo_meta(report, path, body)
            check_scripts(report, path, body)
        check_http(report, path)

    check_sitemaps(report)
    check_apis(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Esylink.cn health check")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--page", action="append", help="Extra page to check")
    args = parser.parse_args()

    pages = KEY_PAGES + (args.page or [])
    report = run_audit(pages)

    if args.json:
        import json

        print(json.dumps([i.__dict__ for i in report.issues], ensure_ascii=False, indent=2))
    else:
        icons = {"error": "✗", "warn": "⚠", "info": "·"}
        for i in report.issues:
            print(f"{icons[i.level]} [{i.category}] {i.message}")
        errors = sum(1 for i in report.issues if i.level == "error")
        warns = sum(1 for i in report.issues if i.level == "warn")
        print(f"\nDone: {errors} errors, {warns} warnings, {len(report.issues)} total")

    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
