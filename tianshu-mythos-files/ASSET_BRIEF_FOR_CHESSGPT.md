# TianShu MythOS (tianshu.online) — Image Asset Brief for ChessGPT

**Site:** https://tianshu.online  
**Product:** TianShu MythOS — English-only, dark fantasy living universe. Readers join the Genesis Registry, vote on Twelve Thrones, receive weekly Chronicle.  
**Strategy:** Conversion-first (registration → paid Founding Citizen). **Do NOT** produce Chinese text or 200+ character portraits.

---

## Global Style Guide (apply to EVERY image)

| Property | Value |
|----------|--------|
| Mood | Dark fantasy, solemn, epic — not cartoon, not anime chibi |
| Background | Near-black `#08080c` or deep void `#0e0e16` |
| Primary accent | Throne gold `#c9a84c` |
| Secondary text | Warm parchment `#e8e0d0`, muted `#8a8578` |
| Typography feel | Elegant serif / engraved / celestial archive |
| Lighting | Rim light in gold; subtle particle/stars OK; avoid flat clipart |
| References | Dark Souls tone + Stripe/Linear cleanliness (not busy) |
| Text in images | English only, minimal, high contrast |
| Export | PNG or WebP, sRGB, no watermark |

---

## PART A — Existing assets (download & optional upgrade)

These already exist on the server. ChessGPT may **redesign/upgrade** them or use as style reference.

| ID | URL | Size | Notes |
|----|-----|------|-------|
| A1 | https://tianshu.online/og-image.png | 1200×630 | Social share card — **upgrade recommended** |
| A2 | https://tianshu.online/favicon.svg | vector | Star sigil on dark square |
| A3–A14 | https://tianshu.online/img/characters/{slug}.svg | vector | 12 flagship heroes (see list below) |
| A15–A26 | https://tianshu.online/portraits/{slug}.svg | vector | Duplicate portrait set for same 12 |

**12 flagship character slugs:**  
`selene`, `raven`, `nyra`, `aurel`, `orion`, `astra`, `kade`, `mira`, `vex`, `lior`, `zeph`, `moreth`

**Example direct links:**
- https://tianshu.online/img/characters/selene.svg
- https://tianshu.online/img/characters/orion.svg
- https://tianshu.online/og-image.png

**Note:** ~94 other characters have **no** image file. Per roadmap we are **NOT** requesting bulk portraits for those.

---

## PART B — P0 Conversion images (CREATE FIRST)

### B1 — Homepage Hero Background
| Field | Spec |
|-------|------|
| **Filename** | `homepage-hero.webp` |
| **Dimensions** | 1920 × 1080 px (16:9), also export 1280×720 |
| **Placement** | Homepage hero behind headline "A living fantasy universe shaped by its first citizens" |
| **Prompt** | Cinematic wide dark fantasy vista: shattered celestial archive, twelve distant throne-shaped monoliths in a ring, stolen book of fate dissolving into golden particles, deep black sky `#08080c`, gold rim light `#c9a84c`, no characters in foreground, atmospheric fog, epic scale, photoreal painterly |
| **Alt text** | TianShu MythOS — Twelve Thrones and the stolen Book of Fate |
| **Goal** | First impression + trust in 3 seconds |

### B2 — Open Graph / Social Share (replace og-image.png)
| Field | Spec |
|-------|------|
| **Filename** | `og-image.png` |
| **Dimensions** | 1200 × 630 px (exact) |
| **Placement** | Twitter, Reddit, Discord link previews |
| **Prompt** | Dark banner: centered golden sigil (star in circle), title "TIANSHU MYTHOS" in serif caps, subtitle "Your vote becomes canon", subtle throne silhouettes, `#08080c` background, gold `#c9a84c` typography, clean margins (safe zone 40px) |
| **Alt text** | TianShu MythOS — AI Living Fantasy Universe |
| **Goal** | Click-through from social posts |

### B3 — How It Works Infographic (3 steps)
| Field | Spec |
|-------|------|
| **Filename** | `how-it-works-steps.webp` |
| **Dimensions** | 1600 × 900 px (horizontal) |
| **Placement** | `/how-it-works` page below intro |
| **Content** | Three panels left-to-right: **01 Join Registry** (scroll + number), **02 Back a Throne** (hand casting vote / golden beam), **03 Receive Chronicle** (sealed weekly dispatch). Thin gold borders between panels. |
| **Prompt** | Minimal dark fantasy infographic, three equal columns, iconographic not photoreal, gold line art on `#0e0e16`, English labels as above |
| **Goal** | Explain product without video |

### B4 — Chronicle Sample Cover (Issue #1)
| Field | Spec |
|-------|------|
| **Filename** | `chronicle-issue-01-cover.webp` |
| **Dimensions** | 800 × 1200 px (portrait, newsletter cover) |
| **Placement** | `/chronicle/sample` (planned) + email header |
| **Prompt** | Weekly canon dispatch cover: "THE CHRONICLE — Issue I", wax seal with star sigil, headline "The Theft of Fate: Week One", torn parchment texture on dark background, gold serif typography, fantasy gazette style |
| **Goal** | Email signup conversion — show what subscribers get |

### B5 — Founding Citizen Badge
| Field | Spec |
|-------|------|
| **Filename** | `founding-citizen-badge.png` |
| **Dimensions** | 512 × 512 px, transparent PNG |
| **Placement** | `/pricing`, `/founding-citizen`, future member profiles |
| **Prompt** | Circular enamel badge: gold ring, inner void black, embossed star and roman numeral I, text arc "FOUNDING CITIZEN", premium membership feel, no photo |
| **Goal** | Paid tier visual identity |

---

## PART C — P1 Twelve Thrones emblems

One emblem per Throne. Used on `/thrones/{slug}` and voting UI.

| ID | Filename | Throne | Color | Sigil | Prompt keyword |
|----|----------|--------|-------|-------|----------------|
| C1 | `throne-fate.webp` | Fate | `#c9a84c` | ✦ | Golden causality wheel, broken thread of prophecy |
| C2 | `throne-dreams.webp` | Dreams | `#7b5ea7` | ☽ | Violet moon over sleeping city, mist |
| C3 | `throne-flame.webp` | Flame | `#d4532a` | ♨ | Ember crown, rebellion fire |
| C4 | `throne-oceans.webp` | Oceans | `#4a90d9` | ≋ | Drowned archive under deep blue water |
| C5 | `throne-nature.webp` | Nature | `#5a8a3c` | ✣ | Ancient roots gripping stone throne |
| C6 | `throne-chaos.webp` | Chaos | `#2a9d8f` | ☿ | Shattered door, probability shards |
| C7 | `throne-death.webp` | Death | `#6b6b6b` | ⟡ | Empty throne, witness ledger |
| C8 | `throne-stars.webp` | Stars | `#8b9dc3` | ✧ | Navigation map with wounded constellations |
| C9 | `throne-storms.webp` | Storms | `#6366f1` | ϟ | Lightning splitting dark sky over throne |
| C10 | `throne-beasts.webp` | Beasts | `#8b6914` | ◈ | Claw marks on ancient stone seat |
| C11 | `throne-heaven.webp` | Heaven | `#f0e68c` | ☉ | Radiant bureaucratic seal, blinding light edge |
| C12 | `throne-war.webp` | War | `#b22222` | ⚔ | Crossed blades behind iron throne |

**Each emblem:** 512 × 512 px WebP + 128 × 128 PNG favicon-size version (`throne-{slug}-icon.png`)  
**Style:** Iconic, centered, dark background, throne color as accent glow  
**Alt pattern:** `{Throne} Throne emblem — TianShu MythOS`

---

## PART D — P1 Hero character portraits (upgrade 12 only)

Replace placeholder SVGs with illustrated bust portraits. **Square, same style across set.**

| ID | Filename | Character | Throne | Visual direction |
|----|----------|-----------|--------|------------------|
| D1 | `selene.webp` | Selene Moonshadow | Dreams | Pale woman, silver eyes, half-asleep, violet accents |
| D2 | `raven.webp` | Raven Nightshade | Chaos | Trickster, sharp smile, shadow cloak, teal-gold |
| D3 | `nyra.webp` | Nyra | Nature | Green-brown, leaf motifs, calm lethal |
| D4 | `aurel.webp` | Aurel | War | Scarred soldier, red-gold armor fragments |
| D5 | `orion.webp` | Orion Starborn | Fate | Stargazer, constellation marks on skin |
| D6 | `astra.webp` | Astra | Stars | Cold distance, navigational tattoos |
| D7 | `kade.webp` | Kade | Flame | Ash on face, ember eyes |
| D8 | `mira.webp` | Mira | Oceans | Deep blue, grief, drowned ink tears |
| D9 | `vex.webp` | Vex | Beasts | Feral elegance, gold-brown |
| D10 | `lior.webp` | Lior | Heaven | Austere, white-gold divine bureaucracy |
| D11 | `zeph.webp` | Zeph | Storms | Electric hair hints, indigo storm |
| D12 | `moreth.webp` | Moreth | Death | Gray pallor, witness eyes, stillness |

**Dimensions:** 512 × 512 px WebP (display at 80–160px in UI)  
**Style:** Painted bust, 3/4 view, dark `#08080c` background, gold rim light, consistent series  
**Alt pattern:** `{Name} — Heir of the {Throne} Throne`  
**Deliver path:** `/img/characters/{slug}.webp` (we will convert/deploy)

---

## PART E — P1 Social & community assets

| ID | Filename | Dimensions | Use | Prompt summary |
|----|----------|------------|-----|----------------|
| E1 | `discord-banner.png` | 960 × 540 | Discord server banner | "TIANSHU MYTHOS" + "Genesis Registry Open" + twelve throne ring |
| E2 | `reddit-banner.png` | 1920 × 384 | Reddit profile | Wide crop of hero art, readable at small size |
| E3 | `x-header.png` | 1500 × 500 | X/Twitter header | Same universe, leave center clear for avatar |
| E4 | `reddit-post-template.png` | 1200 × 1200 | Weekly vote results | Template: "THRONE VOTE RESULTS" + empty bar chart area |
| E5 | `pin-chronicle.png` | 1000 × 1500 | Pinterest / vertical share | Chronicle cover variant vertical |

---

## PART F — P2 Optional (only if time)

| ID | Asset | Notes |
|----|-------|-------|
| F1 | `logo-wordmark.svg` | "TIANSHU MYTHOS" vector wordmark |
| F2 | `logo-icon.svg` | Star sigil only (upgrade favicon) |
| F3 | `pricing-tier-icons/` | 3 icons: Citizen (free), Founding (star), Patron (crown) — 128px each |
| F4 | `event-the-theft-of-fate.webp` | 1200×630 for flagship event page |
| F5 | 15s hero loop | **GIF or MP4** 1280×720: particles + throne ring slow rotate (for homepage) |

**Explicitly out of scope:** 94 missing character images, Chinese graphics, generic stock fantasy art.

---

## Delivery checklist for ChessGPT

When sending files back, please include:

```
/assets/
  homepage-hero.webp
  og-image.png
  how-it-works-steps.webp
  chronicle-issue-01-cover.webp
  founding-citizen-badge.png
  /thrones/
    fate.webp … war.webp (+ icon variants)
  /characters/
    selene.webp … moreth.webp
  /social/
    discord-banner.png
    reddit-banner.png
    x-header.png
    reddit-post-template.png
    pin-chronicle.png
```

**Naming:** lowercase, hyphenated, match filenames exactly.  
**Format priority:** WebP for photos/illustrations, PNG for OG/badge/transparency, SVG only for logos/icons.

---

## Copy-paste master prompt for ChessGPT

```
You are creating a cohesive dark fantasy visual kit for TianShu MythOS (tianshu.online).

Style: near-black background #08080c, gold accent #c9a84c, serif epic tone, English only, dark fantasy (not anime). Consistent rim lighting across all assets.

Create these assets per attached brief:
1. homepage-hero.webp 1920x1080
2. og-image.png 1200x630
3. how-it-works-steps.webp 1600x900 (3-step infographic)
4. chronicle-issue-01-cover.webp 800x1200
5. founding-citizen-badge.png 512x512 transparent
6. Twelve throne emblems 512x512 (fate, dreams, flame, oceans, nature, chaos, death, stars, storms, beasts, heaven, war) — colors in brief
7. Twelve character portraits 512x512 (selene, raven, nyra, aurel, orion, astra, kade, mira, vex, lior, zeph, moreth)
8. Social: discord-banner 960x540, reddit-banner 1920x384, x-header 1500x500, reddit-post-template 1200x1200

Reference existing style: https://tianshu.online/og-image.png and https://tianshu.online/img/characters/selene.svg

Do NOT create Chinese text or hundreds of character images.
```

---

## After delivery

Send files to the dev agent (or upload to server `/data/www/mythos/public/img/`). We will wire paths, rebuild Next.js, and run IndexNow.
