# Google Search Console & Bing Webmaster Setup

## Google Search Console

1. Go to https://search.google.com/search-console
2. Add property: **URL prefix** `https://attyflow.com`
3. Choose verification method:

### Option A — HTML file (recommended)
1. Download verification file from GSC (e.g. `google123abc.html`)
2. Upload to server:
   ```bash
   sudo cp google123abc.html /var/www/attyflow/
   ```
3. Verify: `curl https://attyflow.com/google123abc.html`
4. Click **Verify** in GSC

### Option B — DNS TXT record (DNSPod)
1. Copy TXT record from GSC
2. DNSPod → attyflow.com → 添加记录 → TXT
3. Wait 5–30 min, verify in GSC

## Submit sitemaps

After verification, submit in GSC → Sitemaps:
- `https://attyflow.com/sitemap.xml`
- `https://attyflow.com/sitemap-index.xml`
- `https://attyflow.com/news-sitemap.xml`

## Bing Webmaster Tools

1. https://www.bing.com/webmasters
2. Import from GSC (fastest) or add site manually
3. Submit same sitemaps
4. IndexNow key already at: `https://attyflow.com/indexnow-key.txt` (value: `attyflow-com`)

## Bulk IndexNow (on server)

```bash
sudo python3 /var/www/attyflow/tools/attyflow_indexnow.py
```

## Key pages to inspect after setup

- Coverage report for `/compare/*`, `/case-studies/*`, `/tools/*`
- Core Web Vitals for `/` and `/taskpane.html`
- Manual URL inspection for new pages after each deploy
