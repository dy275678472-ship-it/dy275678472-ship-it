#!/usr/bin/env python3
"""Product Hunt launch-day monitor for attyflow.com.

Usage:
  python3 attyflow_ph_monitor.py              # today's snapshot
  python3 attyflow_ph_monitor.py --date 2026-07-22
  python3 attyflow_ph_monitor.py --since 2026-07-22T08:00:00Z
  python3 attyflow_ph_monitor.py --watch 300  # poll every 5 min
  python3 attyflow_ph_monitor.py --save       # write report to reports/
"""
import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/var/www/attyflow")
LEADS = ROOT / "leads.json"
EVENTS = ROOT / "events.jsonl"
WELCOME = ROOT / "welcome_queue.jsonl"
REPORTS = ROOT / "reports"

LAUNCH_PATHS = {"/", "/launch/", "/launch", "/taskpane.html", "/tools/nda-clause-review/", "/pricing", "/product-hunt/"}


def parse_ts(s: str) -> datetime | None:
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s[:19], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def load_leads(since: datetime | None, until: datetime | None) -> list[dict]:
    if not LEADS.exists():
        return []
    try:
        rows = json.loads(LEADS.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []
    for row in rows:
        ts = parse_ts(row.get("created_at", ""))
        if since and ts and ts < since:
            continue
        if until and ts and ts > until:
            continue
        out.append(row)
    return out


def load_events(since: datetime | None, until: datetime | None) -> list[dict]:
    if not EVENTS.exists():
        return []
    out = []
    for line in EVENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        ts = parse_ts(row.get("ts", ""))
        if since and ts and ts < since:
            continue
        if until and ts and ts > until:
            continue
        out.append(row)
    return out


def render(since: datetime | None, until: datetime | None) -> str:
    leads = load_leads(since, until)
    events = load_events(since, until)
    lines = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    window = ""
    if since:
        window = f"since {since.isoformat()}"
    if until:
        window += f" until {until.isoformat()}"
    lines.append("=" * 56)
    lines.append(f"ATTYFLOW PH LAUNCH MONITOR — {now}")
    if window:
        lines.append(window)
    lines.append("=" * 56)

    lines.append(f"\n## Leads: {len(leads)}")
    by_source = Counter(l.get("source", "unknown") for l in leads)
    for src, n in by_source.most_common():
        lines.append(f"  - {src}: {n}")
    if leads:
        lines.append("\n  Latest leads:")
        for l in leads[-5:]:
            lines.append(f"    · {l.get('email','?')} ({l.get('source','?')}) @ {l.get('created_at','?')}")

    lines.append(f"\n## Page events: {len(events)}")
    by_path = Counter(e.get("url", "?") for e in events)
    for path, n in by_path.most_common(10):
        flag = " ★" if path in LAUNCH_PATHS or path.startswith("/launch") else ""
        lines.append(f"  - {path}: {n}{flag}")

    cta_events = [e for e in events if e.get("cta")]
    lines.append(f"\n## CTA clicks (beacon): {len(cta_events)}")
    launch_views = [e for e in events if e.get("url", "").startswith("/launch")]
    taskpane_views = [e for e in events if e.get("url") == "/taskpane.html"]
    lines.append(f"  - /launch views: {len(launch_views)}")
    lines.append(f"  - /taskpane.html views: {len(taskpane_views)}")

    refs = Counter((e.get("ref") or "direct")[:60] for e in events if e.get("ref"))
    if refs:
        lines.append("\n## Top referrers")
        for ref, n in refs.most_common(8):
            lines.append(f"  - {ref}: {n}")

    avg_time = 0
    if events:
        times = [int(e.get("time", 0)) for e in events if e.get("time")]
        if times:
            avg_time = sum(times) // len(times)
    lines.append(f"\n## Avg time on page: {avg_time}s")

    lines.append("\n## Quick health")
    try:
        import urllib.request
        r = urllib.request.urlopen("http://127.0.0.1:8001/api/health", timeout=5)
        h = json.loads(r.read().decode())
        lines.append(f"  - API: ok={h.get('ok')} version={h.get('version','?')}")
    except Exception as ex:
        lines.append(f"  - API: FAILED ({ex})")

    lines.append("\n## Targets (suggested PH day)")
    lines.append("  - Leads: 20+ (good) · 50+ (strong)")
    lines.append("  - /taskpane views: 100+ (good)")
    lines.append("  - CTA clicks: 30+ (good)")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Attyflow PH launch monitor")
    ap.add_argument("--date", help="Filter to UTC date YYYY-MM-DD")
    ap.add_argument("--since", help="ISO timestamp UTC start")
    ap.add_argument("--watch", type=int, default=0, help="Poll interval seconds")
    ap.add_argument("--save", action="store_true", help="Save report to reports/")
    args = ap.parse_args()

    since = until = None
    if args.date:
        since = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        until = since.replace(hour=23, minute=59, second=59)
    elif args.since:
        since = parse_ts(args.since)

    def run_once():
        report = render(since, until)
        print(report)
        if args.save:
            REPORTS.mkdir(parents=True, exist_ok=True)
            tag = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
            path = REPORTS / f"ph-launch-{tag}.txt"
            path.write_text(report, encoding="utf-8")
            print(f"Saved: {path}")

    if args.watch > 0:
        while True:
            run_once()
            print(f"\n--- next poll in {args.watch}s ---\n")
            time.sleep(args.watch)
    else:
        run_once()


if __name__ == "__main__":
    main()
