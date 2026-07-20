#!/usr/bin/env python3
"""Deploy PH launch ops: monitor script, social copy, Cloudflare guide, playbook page."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/var/www/attyflow")
SRC = Path(__file__).resolve().parent / "attyflow-files"

FILES = [
    "tools/attyflow_ph_monitor.py",
    "launch/SOCIAL_LAUNCH_COPY.md",
    "CLOUDFLARE_DNSPOD_GUIDE.md",
    "launch/playbook/index.html",
]


def copy(rel: str) -> None:
    dst = ROOT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC / rel, dst)
    if rel.endswith(".py"):
        dst.chmod(0o755)
    print(f"  copied {rel}")


def main() -> None:
    print("Attyflow launch ops deploy")
    (ROOT / "reports").mkdir(parents=True, exist_ok=True)
    print("  ensured reports/")
    for rel in FILES:
        copy(rel)
    monitor = ROOT / "tools/attyflow_ph_monitor.py"
    if monitor.exists():
        r = subprocess.run([sys.executable, str(monitor)], capture_output=True, text=True)
        print(r.stdout[:800] if r.stdout else "(monitor produced no stdout)")
        if r.returncode != 0:
            print("  monitor stderr:", r.stderr[:400])
    print("Launch ops deploy complete")


if __name__ == "__main__":
    main()
