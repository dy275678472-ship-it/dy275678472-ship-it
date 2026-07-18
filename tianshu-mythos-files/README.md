# TianShu MythOS P0 Growth Fixes

Deployed to production server `43.172.29.127` on 2026-07-18.

## Changes Applied (Live)

| Fix | Status |
|-----|--------|
| Remove Amazon affiliate footer injection (nginx) | ✅ Verified — 0 amazon.com links |
| Per-page OG Meta (`buildPageMetadata` helper) | ✅ founding-citizen og:url fixed |
| Organization Schema `sameAs` social profiles | ✅ X, Reddit, GitHub |
| `/pricing` page (3-tier membership) | ✅ HTTP 200 |
| `/faq` page (FAQPage schema, 10 Q&A) | ✅ HTTP 200 |
| Homepage registry counter | ✅ Shows live DB count |
| Post-registration vote CTA | ✅ "Cast your first vote" → `/#vote` |
| Footer links (Pricing, FAQ) | ✅ |
| IndexNow batch submit | ✅ 572 URLs → Bing + IndexNow 200 |
| `llms.txt` updated | ✅ |

## Not Applied (Requires Manual Setup)

- **Cloudflare CDN** — needs domain DNS moved to Cloudflare account

## Deploy Commands

```bash
ssh ubuntu@43.172.29.127
python3 /tmp/tianshu_p0_deploy.py
cd /data/www/mythos && npm run build && pm2 restart mythos
python3 /data/www/mythos/tools/tianshu_indexnow.py
```

## Files in This Repo

- `tianshu_p0_deploy.py` — core patch script (metadata, layout, footer, homepage)
- `tianshu-mythos-files/` — new pages (`pricing`, `faq`, `api/stats`) and IndexNow tool
