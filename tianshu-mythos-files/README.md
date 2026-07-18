# TianShu MythOS Growth Fixes

Deployed to production server `43.172.29.127`.

## P0 (Live)

- Remove Amazon affiliate injection
- Per-page OG Meta (`buildPageMetadata`)
- Organization `sameAs` social profiles
- `/pricing` and `/faq` pages
- Homepage registry counter + vote CTA
- IndexNow submission

## P1 (Live)

| Fix | Status |
|-----|--------|
| hreflang en/zh on homepage and `/zh` | ✅ |
| 3 competitor comparison pages | ✅ `/compare/mythos-vs-*` |
| 12 throne pages expanded (~5000 words each) | ✅ `throne-lore.ts` |
| Top 50 thinnest character bios expanded (1200–1700 words) | ✅ DB updated |
| Character Person JSON-LD enriched | ✅ |
| Event pages use `buildPageMetadata` + Event schema | ✅ |
| IndexNow resubmit | ✅ 573 URLs |

## Tools

```bash
# Code patches
python3 tianshu_p1_deploy.py

# Content expansion (requires DEEPSEEK_API_KEY on server)
python3 tools/tianshu_expand_thrones.py
python3 tools/tianshu_expand_chars.py 50

# Rebuild
cd /data/www/mythos && npm run build && pm2 restart mythos
python3 tools/tianshu_indexnow.py
```

## Not Included

- **Cloudflare CDN** — requires DNS migration to Cloudflare account
