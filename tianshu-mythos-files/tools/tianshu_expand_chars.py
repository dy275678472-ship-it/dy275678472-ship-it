#!/usr/bin/env python3
"""Expand top N TianShu character descriptions to 1200+ words via DeepSeek."""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 50
TARGET_WORDS = 1200
MARKER = "<!-- tianshu-expanded -->"
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"


def load_key():
    for path in ("/home/ubuntu/.hermes/.env", "/tmp/nudex_apikey.txt"):
        if not os.path.isfile(path):
            continue
        for line in open(path):
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
            if path.endswith(".txt") and line and not line.startswith("#"):
                return line.strip()
    raise RuntimeError("DEEPSEEK_API_KEY not found")


def load_db_url():
    env = open("/data/www/mythos/.env").read()
    m = re.search(r"DATABASE_URL=(.+)", env)
    if not m:
        raise RuntimeError("DATABASE_URL missing")
    return m.group(1).strip()


def pg_query(url, sql, params=None):
    u = urllib.parse.urlparse(url)
    import subprocess

    env = os.environ.copy()
    env["PGPASSWORD"] = u.password or ""
    cmd = [
        "psql",
        "-h",
        u.hostname or "localhost",
        "-p",
        str(u.port or 5432),
        "-U",
        u.username or "mythos",
        "-d",
        (u.path or "/mythos").lstrip("/"),
        "-t",
        "-A",
        "-c",
        sql,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout


def pg_exec(url, sql):
    u = urllib.parse.urlparse(url)
    import subprocess

    env = os.environ.copy()
    env["PGPASSWORD"] = u.password or ""
    cmd = [
        "psql",
        "-h",
        u.hostname or "localhost",
        "-p",
        str(u.port or 5432),
        "-U",
        u.username or "mythos",
        "-d",
        (u.path or "/mythos").lstrip("/"),
        "-c",
        sql,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return proc.stdout


def word_count(text):
    return len(re.findall(r"\b\w+\b", text or ""))


def call_llm(key, char):
    prompt = f"""Write a unique, publication-quality fantasy character biography for TianShu MythOS.

Character: {char['name']}
Slug: {char['slug']}
Throne: {char['throne']}
Faction: {char.get('faction') or 'Unknown'}
Current bio: {char.get('description') or ''}
Goal: {char.get('goal') or ''}
Fear: {char.get('fear') or ''}
Desire: {char.get('desire') or ''}
Weakness: {char.get('weakness') or ''}
Secret: {char.get('secret') or ''}

World context: The Book of Fate was stolen from the Celestial Archive. Twelve Thrones compete for control. Citizens vote weekly to influence canon.

Requirements:
- At least {TARGET_WORDS} English words
- Dark fantasy tone, specific details, no generic filler
- 6-8 paragraphs separated by blank lines
- Include: origin, role in the Theft of Fate era, relationship to their Throne, a defining wound, and an unresolved tension
- Do NOT use bullet lists or markdown headers
- Start with: {MARKER}
- Write only the biography prose after the marker"""

    payload = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 4000,
        }
    ).encode()
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
    text = data["choices"][0]["message"]["content"].strip()
    if MARKER in text:
        text = text.split(MARKER, 1)[1].strip()
    return text


def fetch_chars(db_url, limit):
    sql = (
        "SELECT slug, name, throne, faction, description, goal, fear, desire, weakness, secret, abilities::text "
        "FROM characters "
        "WHERE description NOT LIKE '%tianshu-expanded%' "
        "ORDER BY length(description) ASC, id ASC "
        f"LIMIT {limit};"
    )
    raw = pg_query(db_url, sql)
    rows = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) < 11:
            continue
        rows.append(
            {
                "slug": parts[0],
                "name": parts[1],
                "throne": parts[2],
                "faction": parts[3],
                "description": parts[4],
                "goal": parts[5],
                "fear": parts[6],
                "desire": parts[7],
                "weakness": parts[8],
                "secret": parts[9],
                "abilities": parts[10],
            }
        )
    return rows


def esc(s):
    return (s or "").replace("'", "''")


def main():
    key = load_key()
    db_url = load_db_url()
    chars = fetch_chars(db_url, LIMIT)
    print(f"expanding {len(chars)} characters")
    done = 0
    for i, char in enumerate(chars, 1):
        try:
            bio = call_llm(key, char)
            wc = word_count(bio)
            if wc < 900:
                print(f"[{i}] {char['slug']}: too short ({wc} words), retrying once")
                bio = call_llm(key, char)
                wc = word_count(bio)
            full = f"{MARKER}\n\n{bio}"
            sql = (
                f"UPDATE characters SET description = '{esc(full)}' "
                f"WHERE slug = '{esc(char['slug'])}';"
            )
            pg_exec(db_url, sql)
            done += 1
            print(f"[{i}/{len(chars)}] {char['slug']}: {wc} words OK")
            time.sleep(1.5)
        except Exception as e:
            print(f"[{i}] {char['slug']}: ERROR {e}")
            time.sleep(3)
    print(f"finished {done}/{len(chars)}")


if __name__ == "__main__":
    main()
