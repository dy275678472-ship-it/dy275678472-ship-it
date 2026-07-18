# TianShu MythOS — Growth & Deployment

**Strategy:** English-only · Conversion-first (registration → retention → revenue)

See **[ROADMAP.md](./ROADMAP.md)** for the current plan.

## Live (Production)

### Conversion & trust
- `/pricing`, `/faq`, `/compare/mythos-vs-*`
- Homepage Citizens counter + post-signup vote CTA
- Amazon affiliate removed

### SEO (supporting conversion, not primary goal)
- Per-page OG meta + Schema
- IndexNow submission
- 50 thinnest character pages expanded (one-time quality floor)
- 12 throne lore pages expanded

## Removed from roadmap

- Chinese `/zh` and hreflang (301 → `/`)
- Bulk expansion of remaining ~198 character pages
- Chinese guide clusters

## Deploy

```bash
# English-only pivot (removes zh, hreflang, deprecates bulk char expand)
python3 tianshu_en_only.py

cd /data/www/mythos && npm run build && pm2 restart mythos
python3 tools/tianshu_indexnow.py
```

## Tools

| Script | Status |
|--------|--------|
| `tianshu_p0_deploy.py` | Active |
| `tianshu_p1_deploy.py` | Active |
| `tianshu_en_only.py` | Active — English-only pivot |
| `tianshu_expand_thrones.py` | On-demand only (campaign content) |
| `tianshu_expand_chars.py` | **Deprecated** — do not run |
