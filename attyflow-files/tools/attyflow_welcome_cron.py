import json
import os
import time
from pathlib import Path

import httpx

DATA_DIR = Path(os.getenv("ATTYFLOW_DATA_DIR", "/var/www/attyflow"))
SEQUENCE_FILE = Path(__file__).resolve().parent.parent / "emails" / "welcome-sequence.json"
WELCOME_QUEUE = DATA_DIR / "welcome_queue.jsonl"
WELCOME_SENT = DATA_DIR / "welcome_sent.jsonl"
LEADS_FILE = DATA_DIR / "leads.json"
RESEND_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("ATTYFLOW_FROM_EMAIL", "onboarding@attyflow.com")


def load_sequence() -> list[dict]:
    if SEQUENCE_FILE.exists():
        return json.loads(SEQUENCE_FILE.read_text(encoding="utf-8"))
    return []


def send_email(to: str, subject: str, body: str) -> bool:
    if not RESEND_KEY:
        return False
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
                json={"from": FROM_EMAIL, "to": [to], "subject": subject, "text": body},
            )
        return r.status_code in (200, 201)
    except Exception:
        return False


def already_sent(email: str, day: int) -> bool:
    if not WELCOME_SENT.exists():
        return False
    for line in WELCOME_SENT.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
            if rec.get("email") == email and rec.get("day") == day:
                return True
        except Exception:
            pass
    return False


def mark_sent(email: str, day: int, ok: bool) -> None:
    with WELCOME_SENT.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"email": email, "day": day, "ok": ok, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}) + "\n")


def main() -> None:
    seq = {item["day"]: item for item in load_sequence()}
    if not seq:
        print("no welcome sequence")
        return
    leads = []
    if LEADS_FILE.exists():
        leads = json.loads(LEADS_FILE.read_text(encoding="utf-8"))
    now = time.time()
    sent = 0
    for lead in leads:
        email = lead.get("email")
        created = lead.get("created_at", "")
        if not email:
            continue
        try:
            # rough age in days from ISO timestamp
            import datetime
            t0 = datetime.datetime.strptime(created[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()
        except Exception:
            t0 = now
        age_days = int((now - t0) / 86400)
        for day in sorted(seq.keys()):
            if age_days < day:
                continue
            if already_sent(email, day):
                continue
            item = seq[day]
            ok = send_email(email, item["subject"], item["body"])
            mark_sent(email, day, ok)
            sent += 1
            print(f"day {day} -> {email} ({'sent' if ok else 'queued/logged'})")
    if not RESEND_KEY:
        print("RESEND_API_KEY not set — logged only, no emails sent")
    print(f"processed {sent} welcome emails")


if __name__ == "__main__":
    main()
