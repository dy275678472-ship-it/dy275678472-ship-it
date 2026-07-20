# Cloudflare setup for attyflow.com

Current DNS: **DNSPod** → A record `43.172.29.127` (direct to origin, no CDN).

## Why enable Cloudflare

- Global CDN caching for static assets (CSS, JS, images, WebP)
- Free SSL edge + DDoS protection
- Faster TTFB for US/EU legal tech visitors
- Bot management (optional)

## Step 1 — Add site to Cloudflare

1. Create account at https://dash.cloudflare.com
2. Add site: `attyflow.com`
3. Cloudflare will scan existing DNS records
4. Verify A record points to `43.172.29.127`
5. Add CNAME `www` → `attyflow.com` (or A record as today)

## Step 2 — Change nameservers at DNSPod

Replace DNSPod nameservers with Cloudflare-assigned nameservers (e.g. `ada.ns.cloudflare.com`).

**DNSPod path:** 域名解析 → attyflow.com → 修改 DNS 服务器 → 填入 Cloudflare NS

Propagation: usually 5–30 minutes, up to 48 hours.

## Step 3 — Cloudflare SSL/TLS settings

| Setting | Value |
|---------|-------|
| SSL mode | **Full (strict)** |
| Always Use HTTPS | On |
| Automatic HTTPS Rewrites | On |
| Minimum TLS | 1.2 |

Origin already has Let's Encrypt cert at `/etc/letsencrypt/live/attyflow.com/`.

## Step 4 — Caching rules (recommended)

**Page Rules or Cache Rules (free tier):**

| URL pattern | Cache |
|-------------|-------|
| `attyflow.com/assets/*` | Cache Everything, Edge TTL 7 days |
| `attyflow.com/*.webp` | Cache Everything, Edge TTL 7 days |
| `attyflow.com/og-image.png` | Cache Everything, Edge TTL 1 day |
| `attyflow.com/api/*` | Bypass |
| `attyflow.com/taskpane.html` | Bypass (dynamic app) |

## Step 5 — Origin nginx (already deployed)

File: `/etc/nginx/conf.d/cloudflare-real-ip.conf`

Includes Cloudflare IP ranges + `real_ip_header CF-Connecting-IP`.

Included in attyflow server block via:
```
include /etc/nginx/conf.d/cloudflare-real-ip.conf;
```

Verify after DNS switch:
```bash
curl -sI https://attyflow.com/ | grep -i cf-ray
# Should show: cf-ray: ...
```

## Step 6 — Verify

```bash
# Cloudflare active
curl -sI https://attyflow.com/ | grep -iE 'cf-ray|server'

# Real IP logging works
sudo tail /var/log/nginx/access.log | head -5

# SSL grade
# https://www.ssllabs.com/ssltest/analyze.html?d=attyflow.com
```

## Rollback

Revert nameservers at DNSPod to `raspberry.dnspod.net` / `setting.dnspod.net`.

Origin nginx Cloudflare include is safe to leave — it only affects requests with CF-Connecting-IP header.
