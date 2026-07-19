#!/usr/bin/env python3
"""P0 SEO + conversion fixes for greentrace.com.cn on Seoul server."""
import json
import os
import subprocess
import textwrap
import urllib.request

LOG = []
BASE = "/opt/greentrace"
SERVER = f"{BASE}/server.py"
INDEX = f"{BASE}/index.html"
NGINX = "/etc/nginx/sites-enabled/traffic-override.conf"
INDEXNOW_KEY = "eb4d11db55e649cbab345946e3fe8c84"


def run(cmd, check=True):
    LOG.append(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if out.strip():
        LOG.append(out.strip()[:4000])
    if check and r.returncode != 0:
        raise RuntimeError(f"Failed: {cmd}\n{out}")
    return r


def write(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    LOG.append(f"Wrote {path}")


BOOKING_FORM = textwrap.dedent("""\
<div class="cta" id="cta">
<h2>准备探索{city_slug}？</h2>
<p>填写预约表单，2小时内为你匹配最合适的本地向导</p>
<form id="bookingForm" style="max-width:420px;margin:0 auto;text-align:left;background:rgba(255,255,255,.12);padding:20px;border-radius:16px;">
<label style="display:block;font-size:.85rem;margin-bottom:4px;opacity:.9">姓名 *</label>
<input name="name" required placeholder="怎么称呼你" style="width:100%;padding:10px 12px;border:none;border-radius:10px;margin-bottom:12px;font-size:.95rem;">
<label style="display:block;font-size:.85rem;margin-bottom:4px;opacity:.9">微信 / 手机 *</label>
<input name="wechat" required placeholder="方便联系的微信号或手机" style="width:100%;padding:10px 12px;border:none;border-radius:10px;margin-bottom:12px;font-size:.95rem;">
<label style="display:block;font-size:.85rem;margin-bottom:4px;opacity:.9">出行日期</label>
<input name="travel_date" type="date" style="width:100%;padding:10px 12px;border:none;border-radius:10px;margin-bottom:12px;font-size:.95rem;">
<label style="display:block;font-size:.85rem;margin-bottom:4px;opacity:.9">人数</label>
<input name="people" type="number" min="1" max="20" value="2" style="width:100%;padding:10px 12px;border:none;border-radius:10px;margin-bottom:12px;font-size:.95rem;">
<label style="display:block;font-size:.85rem;margin-bottom:4px;opacity:.9">备注（可选）</label>
<textarea name="note" rows="2" placeholder="想走哪条路线、是否需要拍照等" style="width:100%;padding:10px 12px;border:none;border-radius:10px;margin-bottom:14px;font-size:.95rem;resize:vertical;"></textarea>
<input type="hidden" name="city" value="{city_slug}">
<button type="submit" class="btn" style="width:100%;border:none;cursor:pointer;">🚀 提交预约</button>
<p id="bookingMsg" style="margin-top:12px;font-size:.9rem;text-align:center;"></p>
</form>
<script>
(function(){{
  var form=document.getElementById('bookingForm');
  if(!form) return;
  form.addEventListener('submit', async function(e){{
    e.preventDefault();
    var msg=document.getElementById('bookingMsg');
    var btn=form.querySelector('button[type=submit]');
    btn.disabled=true; btn.textContent='提交中...';
    var data=Object.fromEntries(new FormData(form).entries());
    try {{
      var res=await fetch('/api/book', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(data)}});
      var j=await res.json();
      if(!res.ok) throw new Error(j.error||'提交失败');
      msg.style.color='#b7e4c7';
      msg.textContent=j.message||'预约已收到！';
      form.reset();
      if(window.umami) umami.track('booking_submit', {{city: data.city||''}});
    }} catch(err) {{
      msg.style.color='#fecaca';
      msg.textContent=err.message||'提交失败，请稍后再试';
    }} finally {{
      btn.disabled=false; btn.textContent='🚀 提交预约';
    }}
  }});
}})();
</script>
</div>""")

def patch_booking_forms():
    with open(SERVER) as f:
        content = f.read()

    city_old = (
        '<div class="cta" id="cta"><h2>准备探索{city_slug}？</h2>'
        "<p>填写预约表单，2小时内为你匹配最合适的本地向导</p>"
        '<a href="#cta" class="btn">🚀 立即预约</a></div>'
    )
    if city_old in content:
        content = content.replace(city_old, BOOKING_FORM, 1)
        LOG.append("Patched city page booking form")
    elif "id=\"bookingForm\"" in content and "准备探索{city_slug}" in content:
        LOG.append("City booking form already patched")
    else:
        LOG.append("WARNING: city CTA pattern not found")

    route_old = (
        '<div class="cta" id="cta"><h2>想走这条路线？</h2>'
        '<p>预约本地向导，不走冤枉路，深度体验{r["city"]}</p>'
        '<a href="#cta" class="btn">🚀 立即预约向导</a></div>'
    )
    if route_old in content:
        route_form = BOOKING_FORM.replace(
            "准备探索{city_slug}？",
            "想走这条路线？",
        ).replace(
            "填写预约表单，2小时内为你匹配最合适的本地向导",
            '预约本地向导，不走冤枉路，深度体验{r["city"]}',
        ).replace(
            'value="{city_slug}"',
            'value="{r[\'city\']}"',
        )
        content = content.replace(route_old, route_form, 1)
        LOG.append("Patched route page booking form")
    else:
        LOG.append("Route CTA pattern not found or already patched")

    # Fix footer year while touching templates
    content = content.replace("© 2025 绿迹", "© 2026 绿迹")

    write(SERVER, content)


def patch_sitemap():
    with open(SERVER) as f:
        content = f.read()

    if "https://www.greentrace.com.cn/" in content:
        content = content.replace("https://www.greentrace.com.cn", "https://greentrace.com.cn")
        LOG.append("Sitemap host → apex")

    blog_snip = 'for page, freq, pri in [("about.html"'
    blog_block = (
        "            # Blog articles\n"
        "            import glob as _sm_glob, os as _sm_os\n"
        '            for _bf in sorted(_sm_glob.glob(f"{WWW}/blog/*.html")):\n'
        "                _bn = _sm_os.path.basename(_bf)\n"
        '                if _bn == "index.html":\n'
        "                    urls.append('<url><loc>https://greentrace.com.cn/blog/</loc>"
        "<changefreq>weekly</changefreq><priority>0.7</priority></url>')\n"
        "                else:\n"
        "                    _slug = _bn[:-5]\n"
        "                    urls.append("
        "f'<url><loc>https://greentrace.com.cn/blog/{_slug}</loc>"
        "<changefreq>monthly</changefreq><priority>0.6</priority></url>')\n"
        "\n"
        '            for page, freq, pri in [("about.html"'
    )
    if "Blog articles" not in content and blog_snip in content:
        content = content.replace(blog_snip, blog_block, 1)
        LOG.append("Added blog URLs to sitemap")
    else:
        LOG.append("Blog sitemap already present or pattern missing")

    write(SERVER, content)


def patch_search_action():
    with open(INDEX) as f:
        content = f.read()
    if "SearchAction" not in content and "query-input" not in content:
        # Ensure head WebSite block is valid JSON
        LOG.append("SearchAction already absent")
        return
    import re

    fixed = """<script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "绿迹",
        "alternateName": "GreenTrace",
        "url": "https://greentrace.com.cn",
        "description": "绿迹是可持续城市旅行指南。提供Citywalk路线、骑行道地图、公交探索攻略。",
        "knowsAbout": ["Citywalk","城市骑行","公交探索","低碳出行","可持续旅行"]
    }
    </script>"""
    pat = re.compile(
        r'<script type="application/ld\+json">\s*\{\s*"@context": "https://schema\.org",\s*"@type": "WebSite",.*?</script>',
        re.S,
    )
    m = pat.search(content)
    if m:
        content = content[: m.start()] + fixed + content[m.end() :]
        content = content.replace("SearchAction", "")
        content = re.sub(r'"query-input"[^\n]*\n?', "", content)
        write(INDEX, content)
        LOG.append("Replaced WebSite JSON-LD without SearchAction")
    else:
        LOG.append("WARNING: WebSite JSON-LD block not found")


def fix_indexnow_key():
    write(f"{BASE}/{INDEXNOW_KEY}.txt", INDEXNOW_KEY + "\n")
    # Remove wrong cosgo key if present as greentrace verification file confusion
    wrong = f"{BASE}/908aa1b2-a138-4a3e-b44a-0f04ab9e4a70.txt"
    if os.path.exists(wrong):
        os.remove(wrong)
        LOG.append("Removed wrong IndexNow key file (cosgo)")


def patch_nginx():
    with open(NGINX) as f:
        content = f.read()

    marker = "# 3. greentrace.com.cn"
    start = content.find(marker)
    end = content.find("# 4. tianshu.online")
    if start < 0 or end < 0:
        raise RuntimeError("greentrace nginx block not found")

    block = content[start:end]

    # Ensure www → apex on HTTPS
    if "return 301 https://greentrace.com.cn$request_uri;" not in block.split("listen 443")[1][:800]:
        block = block.replace(
            "server {\n    listen 443 ssl http2;\n    server_name greentrace.com.cn www.greentrace.com.cn;",
            "server {\n    listen 443 ssl http2;\n    server_name www.greentrace.com.cn;\n"
            "    ssl_certificate /etc/letsencrypt/live/greentrace.com.cn-0001/fullchain.pem;\n"
            "    ssl_certificate_key /etc/letsencrypt/live/greentrace.com.cn-0001/privkey.pem;\n"
            "    return 301 https://greentrace.com.cn$request_uri;\n}\n"
            "server {\n    listen 443 ssl http2;\n    server_name greentrace.com.cn;",
            1,
        )
        LOG.append("Added www→apex HTTPS redirect server")

    # Point /api/ to greentrace backend (4003 is dead)
    if "proxy_pass http://127.0.0.1:4003;" in block:
        block = block.replace(
            "    location /api/ {\n        proxy_pass http://127.0.0.1:4003;",
            "    location /api/ {\n        proxy_pass http://127.0.0.1:8081;",
            1,
        )
        LOG.append("nginx /api/ → 8081")

    # IndexNow key location
    key_loc = f"""
    location = /{INDEXNOW_KEY}.txt {{
        root /opt/greentrace;
        try_files /{INDEXNOW_KEY}.txt =404;
        add_header Cache-Control "public, max-age=86400";
    }}
"""
    if INDEXNOW_KEY not in block:
        block = block.replace(
            "    # Greentrace API endpoints",
            key_loc + "\n    # Greentrace API endpoints",
            1,
        )
        LOG.append("Added IndexNow key nginx location")

    # Fix CSP connect-src (remove cosgo.cn leftover, allow self analytics)
    if "connect-src 'self' https://cosgo.cn" in block:
        block = block.replace(
            "connect-src 'self' https://cosgo.cn https://www.google-analytics.com https://analytics.google.com",
            "connect-src 'self' https://greentrace.com.cn https://www.google-analytics.com https://analytics.google.com https://analytics.after2am.online",
            1,
        )
        LOG.append("Fixed CSP connect-src")

    content = content[:start] + block + content[end:]
    write("/tmp/traffic-override.conf", content)
    run(f"sudo cp /tmp/traffic-override.conf {NGINX}")
    run("sudo nginx -t")
    run("sudo systemctl reload nginx")


def restart_greentrace():
    run("sudo systemctl restart greentrace")
    run("sleep 2 && systemctl is-active greentrace")


def run_indexnow():
    run("sudo bash /opt/indexnow-submit.sh", check=False)
    run("grep greentrace /var/log/indexnow.log | tail -3", check=False)


def verify():
    checks = [
        "curl -sI https://www.greentrace.com.cn/ | head -5",
        "curl -s https://greentrace.com.cn/sitemap.xml | grep -c 'https://greentrace.com.cn/'",
        "curl -s https://greentrace.com.cn/sitemap.xml | grep -c www.greentrace || true",
        "curl -s https://greentrace.com.cn/sitemap.xml | grep -c '/blog/'",
        f"curl -s -o /dev/null -w '%{{http_code}}' https://greentrace.com.cn/{INDEXNOW_KEY}.txt",
        "curl -s https://greentrace.com.cn/ | grep -c SearchAction || true",
        "curl -s https://greentrace.com.cn/city/%E6%88%90%E9%83%BD | grep -c bookingForm",
        "curl -s -X POST https://greentrace.com.cn/api/book -H 'Content-Type: application/json' "
        "-d '{\"name\":\"P0验证\",\"wechat\":\"p0_verify_wx\",\"city\":\"成都\",\"people\":\"1\",\"note\":\"p0\"}'",
    ]
    for c in checks:
        run(c, check=False)


def main():
    # Backup
    run(f"cp {SERVER} {SERVER}.bak.p0-$(date +%Y%m%d%H%M)")
    run(f"cp {INDEX} {INDEX}.bak.p0-$(date +%Y%m%d%H%M)")
    patch_booking_forms()
    patch_sitemap()
    patch_search_action()
    fix_indexnow_key()
    patch_nginx()
    restart_greentrace()
    run_indexnow()
    verify()
    report = "\n".join(LOG)
    with open("/tmp/greentrace-p0.log", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
