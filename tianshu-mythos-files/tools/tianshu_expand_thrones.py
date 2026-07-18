#!/usr/bin/env python3
"""Generate expanded throne lore for TianShu MythOS."""
import json
import os
import re
import time
import urllib.request

OUT = "/data/www/mythos/src/lib/throne-lore.ts"
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"

THRONES = [
    ("Fate", "fate", "Pattern, causality, broken prophecy."),
    ("Dreams", "dreams", "Sleep, prophecy, impossible memory."),
    ("Flame", "flame", "War heat, rebellion, purification."),
    ("Oceans", "oceans", "Depth, grief, drowned archives."),
    ("Nature", "nature", "Growth, decay, ancient law."),
    ("Chaos", "chaos", "Disruption, probability, unlicensed freedom."),
    ("Death", "death", "Ending, witness, final accounting."),
    ("Stars", "stars", "Distance, navigation, celestial error."),
    ("Storms", "storms", "Pressure, rupture, sudden verdict."),
    ("Beasts", "beasts", "Instinct, territory, old hunger."),
    ("Heaven", "heaven", "Authority, light, divine bureaucracy."),
    ("War", "war", "Conflict, discipline, irreversible choice."),
]


def load_key():
    for path in ("/home/ubuntu/.hermes/.env", "/tmp/nudex_apikey.txt"):
        if not os.path.isfile(path):
            continue
        for line in open(path):
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("DEEPSEEK_API_KEY not found")


def call_llm(key, name, promise):
    prompt = f"""Write expanded lore for the {name} Throne in TianShu MythOS (dark fantasy living universe).

Throne promise: {promise}
Context: The Book of Fate was stolen. Twelve Thrones compete. Readers vote weekly.

Return valid JSON only:
{{
  "origin": "2 paragraphs about how this Throne was established",
  "doctrine": "2 paragraphs about what its citizens believe",
  "currentConflict": "2 paragraphs about its role after the Theft of Fate",
  "notableHeirs": "2 paragraphs describing types of heirs and famous witnesses",
  "readerRole": "1 paragraph on why a new citizen might back this Throne"
}}

Total at least 1000 English words across all fields. Specific names and images. No markdown."""

    payload = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.75,
            "max_tokens": 3500,
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
    text = re.sub(r"^```json\s*|\s*```$", "", text, flags=re.S)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            return json.loads(m.group(0))
        raise


def main():
    key = load_key()
    lore = {}
    for name, slug, promise in THRONES:
        print(f"generating {slug}...")
        try:
            lore[slug] = call_llm(key, name, promise)
            print(f"  {slug} OK")
        except Exception as e:
            print(f"  {slug} ERROR: {e}")
            lore[slug] = {
                "origin": f"The {name} Throne rose when the first archive fractured.",
                "doctrine": promise,
                "currentConflict": "Its power is contested in the post-Theft era.",
                "notableHeirs": "Many heirs bear witness under this Throne.",
                "readerRole": f"Back {name} if this promise speaks to you.",
            }
        time.sleep(1.5)

    lines = [
        "export type ThroneLore = {",
        "  origin: string;",
        "  doctrine: string;",
        "  currentConflict: string;",
        "  notableHeirs: string;",
        "  readerRole: string;",
        "};",
        "",
        "export const throneLore: Record<string, ThroneLore> = " + json.dumps(lore, indent=2) + ";",
        "",
    ]
    open(OUT, "w", encoding="utf-8").write("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
