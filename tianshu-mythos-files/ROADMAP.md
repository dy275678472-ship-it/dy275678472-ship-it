# TianShu MythOS — English-Only, Conversion-First Roadmap

**Strategy:** Global English audience · Registration & revenue over page count  
**Last updated:** 2026-07-18  
**Explicitly removed:** Chinese localization (`/zh`, hreflang, CN guide clusters) · Bulk character bio expansion (198+ pages)

---

## North Star Metrics

| Metric | Current (est.) | 90-day target | 12-month target |
|--------|----------------|---------------|-----------------|
| Genesis Registry signups | ~1 | 500 | 5,000 |
| Chronicle email subscribers | ~1 | 400 | 3,000 |
| Paid Founding Citizens | 0 | 25 | 250 |
| Monthly revenue (Founding Citizen @ $5) | $0 | $125 | $1,250+ |

**We do not optimize for:** total URL count, Chinese SERP coverage, or expanding every character page.

---

## What We Keep (Already Live)

| Item | Why it helps conversion |
|------|-------------------------|
| `/pricing` + `/faq` | Reduces friction; answers objections before signup |
| `/compare/mythos-vs-*` | Captures high-intent traffic; positions vs AI Dungeon / World Anvil |
| Amazon affiliate removed | Trust on a premium fantasy brand |
| Per-page OG meta + Schema | Better social shares → more qualified clicks |
| Homepage Citizens counter + vote CTA | Social proof + immediate post-signup action |
| 50 thinnest character pages expanded | SEO quality floor (done; no further bulk expansion) |
| 12 throne lore pages expanded | Anchor content for campaigns and Reddit posts |
| IndexNow | Faster indexing of new conversion pages |

---

## What We Removed

| Removed | Reason |
|---------|--------|
| `/zh` Chinese homepage | Not part of product strategy; splits focus |
| hreflang en/zh | Implies bilingual product we don't support |
| Bulk expansion of remaining ~198 characters | Low conversion ROI; high API cost |
| Chinese `/zh/guides` cluster | Never planned; dropped permanently |

`/zh` now **301 redirects to `/`**.

---

## Phase 1 — Conversion Foundation (Weeks 1–2)

**Goal:** Every visitor can understand, trust, and register in under 60 seconds.

| # | Task | Impact | Owner |
|---|------|--------|-------|
| 1.1 | **Chronicle sample page** — publish 1 full issue publicly at `/chronicle/sample` | Shows product value before email commit | Content |
| 1.2 | **Homepage hero rewrite** — lead with “Your vote becomes canon” + single primary CTA | Clarity → signup rate | Copy |
| 1.3 | **Sticky mobile CTA** — “Join Registry” bar on scroll | Mobile conversion | Dev |
| 1.4 | **Post-register email** — welcome + “cast your first vote” deep link | Activation | Dev |
| 1.5 | **Founding Citizen waitlist** — collect email + plan interest on `/pricing` | Revenue pipeline | Dev |

**Success:** Registry completion rate +25% vs baseline.

---

## Phase 2 — Trust & Activation (Weeks 3–4)

**Goal:** Turn signups into weekly returners.

| # | Task | Impact | Owner |
|---|------|--------|-------|
| 2.1 | **Launch Discord** — one `#throne-voting` + `#chronicle` channel | Retention + feedback loop | Community |
| 2.2 | **Reddit launch post** — r/worldbuilding or r/AIDungeon (follow sub rules) | First 50–200 signups | Marketing |
| 2.3 | **3 founder quotes** — even short testimonials on homepage | Trust | Community |
| 2.4 | **Weekly Chronicle send** — fixed schedule (e.g. Sunday UTC) | Habit | Content |
| 2.5 | **Vote results email** — “Your Throne rose/fell this week” | Re-engagement | Dev |

**Success:** Week-2 retention ≥ 20% of new signups.

---

## Phase 3 — Monetization (Weeks 5–8)

**Goal:** First paying customers without hurting free funnel.

| # | Task | Impact | Owner |
|---|------|--------|-------|
| 3.1 | **Stripe Checkout** — Founding Citizen $5/mo (or $49/yr) | Revenue | Dev |
| 3.2 | **Upgrade prompt** — after 2nd vote or 2nd Chronicle open | Natural upsell moment | Dev |
| 3.3 | **Member benefits page** — what paid unlocks vs free | Conversion clarity | Copy |
| 3.4 | **Limited seats** — “First 500 Founding Citizens” counter | Urgency | Product |
| 3.5 | **Refund policy** — 7-day no-questions on first month | Risk reversal | Legal |

**Success:** 25 paid members · $125 MRR by end of Week 8.

---

## Phase 4 — Scalable Acquisition (Weeks 9–12)

**Goal:** Repeatable channels that cost less than LTV.

| # | Task | Impact | Budget |
|---|------|--------|--------|
| 4.1 | **Cloudflare CDN** | Speed → lower bounce | $0 |
| 4.2 | **X + Reddit organic** — 3 posts/week (lore snippets, vote results) | Free signups | $0 |
| 4.3 | **One comparison blog post** — “MythOS vs AI Dungeon: which is for you?” (long-form on `/compare` hub) | SEO + conversion | $0 |
| 4.4 | **Reddit Ads test** — $300 to r/worldbuilding | CAC benchmark | $300 |
| 4.5 | **Newsletter referral** — invite 3 friends → badge | Viral coefficient | Dev |

**Success:** 500 total Registry · CAC < $15 on paid test.

---

## Content Policy (English-Only)

| Do | Don't |
|----|-------|
| Write for Reddit, X, Discord in English | Add `/zh` or Chinese guides |
| Expand **hero characters** only when tied to a campaign (max 2/month) | Bulk-expand all 198 remaining characters |
| Fix thin **guides** only if they get impressions in GSC | Generate 250 more programmatic pages |
| Chronicle + vote results as weekly “product” | Treat SEO page count as a goal |

---

## 12-Month Vision (Conversion-Led)

```
Q1  Foundation     → 500 signups · Stripe live · Discord active
Q2  Retention      → 2,000 signups · 100 paid · Chronicle habit
Q3  Scale          → Paid ads with proven CAC · KOL on Reddit/YouTube
Q4  Brand          → 5,000 signups · 250 paid · $1,250+ MRR
```

---

## Priority Stack (When in Doubt)

1. Does it increase **signup rate**?
2. Does it increase **Week-2 retention**?
3. Does it enable **first dollar of revenue**?
4. Only then: SEO depth, new page types, or technical polish.

---

## PR / Repo References

- P0 fixes: PR #14  
- P1 SEO/content: PR #17  
- English-only pivot: this roadmap + `tianshu_en_only.py`
