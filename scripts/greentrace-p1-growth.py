#!/usr/bin/env python3
"""P1 growth for greentrace.com.cn — Article schema, subscribe, Klook, brand unify."""
import glob
import os
import re
import subprocess
import textwrap

LOG = []
BASE = "/opt/greentrace"
SERVER = f"{BASE}/server.py"
KLOOK_AID = "125965"


def run(cmd, check=True):
    LOG.append(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if out.strip():
        LOG.append(out.strip()[:3500])
    if check and r.returncode != 0:
        raise RuntimeError(f"Failed: {cmd}\n{out}")
    return r


def write(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    LOG.append(f"Wrote {path}")


SUBSCRIBE_FORM = """
<div class="gt-subscribe" style="margin:36px 0;padding:24px;border-radius:16px;background:linear-gradient(135deg,#d8f3dc,#f0f7f4);border:1px solid #b7e4c7;">
  <h3 style="margin:0 0 8px;color:#1b4332;font-size:1.15rem;">把低碳路线发到邮箱</h3>
  <p style="margin:0 0 14px;color:#3d405b;font-size:.92rem;">订阅后不定期收到 Citywalk / 骑行精选，无垃圾邮件。</p>
  <form id="gtSubscribeForm" style="display:flex;flex-wrap:wrap;gap:10px;">
    <input type="email" name="email" required placeholder="your@email.com"
      style="flex:1;min-width:200px;padding:10px 14px;border:1px solid #74c69d;border-radius:10px;font-size:.95rem;">
    <button type="submit" style="padding:10px 20px;background:#2d6a4f;color:#fff;border:none;border-radius:10px;font-weight:600;cursor:pointer;">免费订阅</button>
  </form>
  <p id="gtSubscribeMsg" style="margin:10px 0 0;font-size:.88rem;"></p>
</div>
<script>
(function(){
  var form=document.getElementById('gtSubscribeForm');
  if(!form||form.dataset.bound) return;
  form.dataset.bound='1';
  form.addEventListener('submit', async function(e){
    e.preventDefault();
    var msg=document.getElementById('gtSubscribeMsg');
    var btn=form.querySelector('button');
    btn.disabled=true;
    try{
      var email=new FormData(form).get('email');
      var res=await fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,source:location.pathname})});
      var j=await res.json();
      if(!res.ok) throw new Error(j.error||'订阅失败');
      msg.style.color='#2d6a4f'; msg.textContent=j.message||'订阅成功';
      form.reset();
      if(window.umami) umami.track('subscribe_complete',{source:location.pathname});
    }catch(err){
      msg.style.color='#b91c1c'; msg.textContent=err.message||'订阅失败';
    }finally{ btn.disabled=false; }
  });
})();
</script>
"""

KLOOK_WIDGET = """
<section id="stay" style="margin-top:28px;">
<h2>🏨 出行住宿（同价支持绿迹）</h2>
<div style="background:linear-gradient(135deg,#d8f3dc,#fefae0);border:1px solid #b7e4c7;border-radius:16px;padding:20px;">
<p style="color:var(--muted);font-size:.92rem;margin-bottom:14px;">通过 Klook 预订{city_slug}酒店与活动，价格不变，联盟佣金支持绿迹持续更新路线。</p>
<div style="display:flex;flex-wrap:wrap;gap:10px;">
<a href="https://www.klook.com/zh-CN/hotels/?aid={aid}&query={city_q}" target="_blank" rel="noopener noreferrer sponsored" style="display:inline-block;padding:10px 18px;background:var(--green-mid);color:#fff;border-radius:12px;text-decoration:none;font-weight:600;font-size:.9rem;">搜索{city_slug}酒店 →</a>
<a href="https://www.klook.com/zh-CN/activities/?aid={aid}" target="_blank" rel="noopener noreferrer sponsored" style="display:inline-block;padding:10px 18px;background:#fff;color:var(--green-dark);border:1px solid var(--green-mid);border-radius:12px;text-decoration:none;font-weight:600;font-size:.9rem;">景点门票</a>
</div>
</div>
</section>
""".replace("{aid}", KLOOK_AID)


def patch_blog_articles():
    files = sorted(glob.glob(f"{BASE}/blog/*.html"))
    n_schema = n_sub = 0
    for fp in files:
        name = os.path.basename(fp)
        if name == "index.html":
            continue
        with open(fp, encoding="utf-8") as f:
            html = f.read()
        slug = name[:-5]
        title_m = re.search(r"<title>([^|<]+)", html)
        desc_m = re.search(r'name="description" content="([^"]*)"', html)
        h1_m = re.search(r"<h1>([^<]+)</h1>", html)
        title = (h1_m or title_m).group(1).strip() if (h1_m or title_m) else slug
        desc = desc_m.group(1) if desc_m else title
        if "application/ld+json" not in html or '"@type": "Article"' not in html:
            schema = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":{json_str(title)},"description":{json_str(desc)},"url":"https://greentrace.com.cn/blog/{slug}","image":"https://greentrace.com.cn/og-image.png","author":{{"@type":"Organization","name":"绿迹"}},"publisher":{{"@type":"Organization","name":"绿迹","logo":{{"@type":"ImageObject","url":"https://greentrace.com.cn/og-image.png"}}}},"mainEntityOfPage":"https://greentrace.com.cn/blog/{slug}"}}
</script>
"""
            html = html.replace("</head>", schema + "</head>", 1)
            n_schema += 1
        if "gtSubscribeForm" not in html:
            if "</div>\n<footer>" in html:
                html = html.replace("</div>\n<footer>", SUBSCRIBE_FORM + "</div>\n<footer>", 1)
            elif '<a href="/blog/" class="back">' in html:
                # append before last closing container
                html = html.replace(
                    '<a href="/blog/" class="back">← 返回博客</a>',
                    '<a href="/blog/" class="back">← 返回博客</a>',
                    1,
                )
                if "</div>\n</body>" in html:
                    html = html.replace("</div>\n</body>", SUBSCRIBE_FORM + "</div>\n</body>", 1)
                elif "</body>" in html:
                    html = html.replace("</body>", SUBSCRIBE_FORM + "</body>", 1)
            elif "</body>" in html:
                html = html.replace("</body>", SUBSCRIBE_FORM + "</body>", 1)
            n_sub += 1
        # Soft CTA to booking city hub
        if "探索城市路线" not in html and "</body>" in html:
            cta = (
                '<p style="margin-top:28px;padding:16px;background:#fff;border-radius:12px;border:1px solid #b7e4c7;">'
                '读完想出发？<a href="/city/" style="color:#2d6a4f;font-weight:600;">浏览城市隐藏路线 →</a>'
                '　<a href="/guide.html" style="color:#40916c;">成为向导 →</a></p>\n'
            )
            html = html.replace(SUBSCRIBE_FORM, cta + SUBSCRIBE_FORM, 1) if SUBSCRIBE_FORM in html else html
        write(fp, html)
    LOG.append(f"Blog articles: schema+={n_schema}, subscribe+={n_sub}")


def json_str(s):
    import json

    return json.dumps(s, ensure_ascii=False)


def patch_blog_index():
    fp = f"{BASE}/blog/index.html"
    if not os.path.exists(fp):
        return
    with open(fp, encoding="utf-8") as f:
        html = f.read()
    if "gtSubscribeForm" not in html:
        if "</body>" in html:
            html = html.replace("</body>", SUBSCRIBE_FORM + "</body>", 1)
            write(fp, html)
            LOG.append("Blog index subscribe added")


def patch_subscribe_api():
    with open(SERVER, encoding="utf-8") as f:
        content = f.read()

    if "CREATE TABLE IF NOT EXISTS subscribers" not in content:
        # Insert after tour_requests create or near other CREATE TABLE
        marker = "CREATE TABLE IF NOT EXISTS tour_requests"
        idx = content.find(marker)
        if idx < 0:
            LOG.append("WARNING: tour_requests table marker not found")
        else:
            # find end of that create block
            end = content.find(")", idx)
            end = content.find("\n", end)
            insert = textwrap.dedent("""

        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            source TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
""")
            # Better: find a spot after init creates - look for city_ambassadors or similar end
            amb = content.find("CREATE TABLE IF NOT EXISTS city_ambassadors")
            if amb > 0:
                end = content.find(")", amb)
                end = content.find("\n", end)
                content = content[: end + 1] + insert + content[end + 1 :]
                LOG.append("Added subscribers table DDL")
            else:
                content = content[: end + 1] + insert + content[end + 1 :]
                LOG.append("Added subscribers table DDL (fallback)")

    if 'path == "/api/subscribe"' not in content:
        api = '''
        if path == "/api/subscribe":
            if self.command != "POST":
                return self.send_json({"error": "请使用POST"}, 405)
            data = self.read_body() or {}
            email = (data.get("email") or "").strip().lower()
            source = (data.get("source") or "blog")[:120]
            if not email or "@" not in email or "." not in email.split("@")[-1]:
                return self.send_json({"error": "请输入有效邮箱"}, 400)
            db = get_db()
            existing = db.execute("SELECT id FROM subscribers WHERE email=?", (email,)).fetchone()
            if existing:
                db.execute("UPDATE subscribers SET source=? WHERE email=?", (source, email))
            else:
                db.execute("INSERT INTO subscribers (email, source) VALUES (?, ?)", (email, source))
            db.commit()
            db.close()
            if not existing:
                try:
                    cfg = _get_email_config()
                    if cfg:
                        from email.mime.text import MIMEText as _MIMEText
                        _html = (
                            "<div style='font-family:sans-serif;max-width:520px;margin:0 auto;padding:24px;line-height:1.7;color:#1a1a2e'>"
                            "<h2 style='color:#2d6a4f'>欢迎订阅绿迹</h2>"
                            "<p>我们会不定期分享 Citywalk、骑行与公交探索精选。</p>"
                            "<p style='text-align:center;margin:24px 0'><a href='https://greentrace.com.cn/citywalk/' "
                            "style='display:inline-block;padding:12px 24px;background:#2d6a4f;color:#fff;text-decoration:none;border-radius:10px'>浏览 Citywalk</a></p>"
                            "<p style='font-size:12px;color:#6b705c'>如需退订，回复本邮件即可。</p></div>"
                        )
                        _msg = _MIMEText(_html, "html", "utf-8")
                        _msg["Subject"] = "【绿迹】订阅成功 — 低碳城市路线精选"
                        _msg["From"] = cfg[2]
                        _msg["To"] = email
                        with smtplib.SMTP(cfg[0], cfg[1]) as _s:
                            _s.starttls()
                            _s.login(cfg[2], cfg[3])
                            _s.send_message(_msg)
                except Exception:
                    logger.exception("subscribe welcome email failed")
            return self.send_json({"ok": True, "message": "订阅成功，精选路线会发到你的邮箱"})

'''
        needle = '        # ----- Booking API -----\n        if path == "/api/book":'
        if needle in content:
            content = content.replace(needle, api + needle, 1)
            LOG.append("Added /api/subscribe")
        else:
            needle2 = '        if path == "/api/book":'
            content = content.replace(needle2, api + needle2, 1)
            LOG.append("Added /api/subscribe (alt)")

    write(SERVER, content)


def patch_city_klook_and_trust():
    with open(SERVER, encoding="utf-8") as f:
        content = f.read()

    # Soften trust copy on city hero
    old_hero = (
        '<p class="hero-desc">{route_count}条隐藏路线 · {guide_count}位本地向导 · {review_count}条真实评价</p>'
    )
    new_hero = (
        '<p class="hero-desc">{route_count}条隐藏路线 · {guide_count}位本地向导</p>'
    )
    if old_hero in content:
        content = content.replace(old_hero, new_hero, 1)
        LOG.append("Softened city hero trust copy")

    old_stat = (
        '<div class="city-stat"><span class="cs-num">{review_count}</span><span class="cs-label">真实评价</span></div>'
    )
    new_stat = (
        '<div class="city-stat"><span class="cs-num">{review_count}</span><span class="cs-label">用户评价</span></div>'
    )
    if old_stat in content:
        content = content.replace(old_stat, new_stat, 1)

    reviews_h = "<section id=\"reviews\"><h2>💬 真实评价</h2>"
    if reviews_h in content:
        content = content.replace(reviews_h, '<section id="reviews"><h2>💬 用户评价</h2>', 1)

    # Insert Klook widget before booking CTA
    cta_marker = '<div class="cta" id="cta">'
    klook = KLOOK_WIDGET.replace("{city_q}", "{urllib.parse.quote(city_slug)}")
    # In f-string template, need city_slug for display and quote for URL
    klook_f = (
        "\n<section id=\"stay\" style=\"margin-top:28px;\">\n"
        "<h2>🏨 出行住宿（同价支持绿迹）</h2>\n"
        "<div style=\"background:linear-gradient(135deg,#d8f3dc,#fefae0);border:1px solid #b7e4c7;border-radius:16px;padding:20px;\">\n"
        "<p style=\"color:var(--muted);font-size:.92rem;margin-bottom:14px;\">"
        "通过 Klook 预订{city_slug}酒店与活动，价格不变，联盟佣金支持绿迹持续更新路线。</p>\n"
        "<div style=\"display:flex;flex-wrap:wrap;gap:10px;\">\n"
        f'<a href="https://www.klook.com/zh-CN/hotels/?aid={KLOOK_AID}&query={{urllib.parse.quote(city_slug)}}" '
        'target="_blank" rel="noopener noreferrer sponsored" '
        'style="display:inline-block;padding:10px 18px;background:var(--green-mid);color:#fff;'
        'border-radius:12px;text-decoration:none;font-weight:600;font-size:.9rem;">'
        "搜索{city_slug}酒店 →</a>\n"
        f'<a href="https://www.klook.com/zh-CN/activities/?aid={KLOOK_AID}" '
        'target="_blank" rel="noopener noreferrer sponsored" '
        'style="display:inline-block;padding:10px 18px;background:#fff;color:var(--green-dark);'
        "border:1px solid var(--green-mid);border-radius:12px;text-decoration:none;font-weight:600;font-size:.9rem;\">"
        "景点门票</a>\n"
        "</div></div></section>\n"
    )
    if 'id="stay"' not in content and cta_marker in content:
        # Only first city-page occurrence: before city booking form CTA that has 准备探索
        city_cta = '<div class="cta" id="cta">\n<h2>准备探索{city_slug}？</h2>'
        if city_cta in content:
            content = content.replace(city_cta, klook_f + city_cta, 1)
            LOG.append("Added Klook widget to city pages")
        else:
            # try single-line variant
            city_cta2 = '<div class="cta" id="cta"><h2>准备探索{city_slug}？</h2>'
            if city_cta2 in content:
                content = content.replace(city_cta2, klook_f + city_cta2, 1)
                LOG.append("Added Klook widget (compact CTA)")

    write(SERVER, content)


def unify_greenyoo_promo():
    targets = [
        f"{BASE}/PROMO_COPY.md",
        f"{BASE}/绿迹_寻找合伙人方案.md",
    ]
    for fp in targets:
        if not os.path.exists(fp):
            continue
        with open(fp, encoding="utf-8") as f:
            text = f.read()
        new = text.replace("greenyoo.cn/guide/register.html", "greentrace.com.cn/guide.html")
        new = new.replace("greenyoo.cn", "greentrace.com.cn")
        if new != text:
            write(fp, new)
            LOG.append(f"Unified greenyoo → greentrace in {os.path.basename(fp)}")


def compress_og():
    path = f"{BASE}/og-image.png"
    run(
        f"convert {path} -strip -quality 82 -resize '1200x630>' {path}.tmp && mv {path}.tmp {path}",
        check=False,
    )
    run(f"wc -c {path}", check=False)


def ensure_subscribers_table():
    run(
        f'cd {BASE} && python3 -c "'
        "import sqlite3; "
        "c=sqlite3.connect('greentrace.db'); "
        "c.execute('CREATE TABLE IF NOT EXISTS subscribers (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, source TEXT, created_at TEXT DEFAULT (datetime(\\'now\\',\\'localtime\\')))'); "
        "c.commit(); print('subscribers ok')"
        '"',
        check=False,
    )


def restart():
    run("sudo systemctl restart greentrace")
    run("sleep 2 && systemctl is-active greentrace")


def verify():
    run("curl -s https://greentrace.com.cn/blog/citywalk-guide-beginner | grep -c '\"@type\": \"Article\"'", check=False)
    run("curl -s https://greentrace.com.cn/blog/citywalk-guide-beginner | grep -c gtSubscribeForm", check=False)
    run("curl -s https://greentrace.com.cn/city/%E6%88%90%E9%83%BD | grep -c 'klook.com'", check=False)
    run("curl -s https://greentrace.com.cn/city/%E6%88%90%E9%83%BD | grep -c '真实评价' || true", check=False)
    run(
        "curl -s -X POST https://greentrace.com.cn/api/subscribe -H 'Content-Type: application/json' "
        "-d '{\"email\":\"p1-verify@example.com\",\"source\":\"p1-verify\"}'",
        check=False,
    )
    run("grep -c greenyoo.cn /opt/greentrace/PROMO_COPY.md || true", check=False)


def main():
    run(f"cp {SERVER} {SERVER}.bak.p1-$(date +%Y%m%d%H%M)")
    patch_blog_articles()
    patch_blog_index()
    patch_subscribe_api()
    patch_city_klook_and_trust()
    unify_greenyoo_promo()
    compress_og()
    ensure_subscribers_table()
    restart()
    verify()
    report = "\n".join(LOG)
    with open("/tmp/greentrace-p1.log", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
