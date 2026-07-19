#!/usr/bin/env python3
"""P2 image fixes for greentrace.com.cn — city covers, no picsum, SVG route maps.

Run on Seoul server as root/ubuntu with write access to /opt/greentrace.
"""
import ast
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path

LOG = []
BASE = Path("/opt/greentrace")
SERVER = BASE / "server.py"
IMG = BASE / "images"
UA = "Mozilla/5.0 (compatible; GreenTraceBot/1.0; +https://greentrace.com.cn)"

# Verified location-tagged Unsplash short IDs / photo-* CDN IDs
VERIFIED = {
    "chengdu": "ItOVNVIrwAM",
    "hangzhou": "IvFtwmRcCQ0",
    "shanghai": "photo-1548919973-5cef591cdbc9",
    "beijing": "photo-1508804185872-d7badad00f7d",
    "xiamen": "XjHNLadzEjY",
    "xian": "PUCoYaHv_Ys",
}
# Wikimedia Special:FilePath for Kunming Stone Forest (CC)
WIKI = {
    "kunming": "Shilin_Yunnan_China_Shilin-Stone-Forest-12.jpg",
}

CITY_UNSPLASH_BODY = """{
                '成都':'/images/city-hero-chengdu.jpg',
                '重庆':'/images/city-hero-chongqing.jpg',
                '上海':'/images/city-hero-shanghai.jpg',
                '杭州':'/images/city-hero-hangzhou.jpg',
                '广州':'/images/city-hero-guangzhou.jpg',
                '深圳':'/images/city-hero-shenzhen.jpg',
                '合肥':'/images/city-hero-hefei.jpg',
                '南京':'/images/city-hero-nanjing.jpg',
                '武汉':'/images/city-hero-wuhan.jpg',
                '长沙':'/images/city-hero-changsha.jpg',
                '北京':'/images/city-hero-beijing.jpg',
                '西安':'/images/city-hero-xian.jpg',
                '昆明':'/images/city-hero-kunming.jpg',
                '厦门':'/images/city-hero-xiamen.jpg',
                '桂林':'/images/city-hero-guilin.jpg',
                '大理':'/images/city-hero-dali.jpg',
                '丽江':'/images/city-hero-lijiang.jpg',
                '苏州':'/images/city-hero-suzhou.jpg',
                '青岛':'/images/city-hero-qingdao.jpg',
                '天津':'/images/city-hero-tianjin.jpg',
                '三亚':'/images/city-hero-sanya.jpg',
                '拉萨':'/images/city-hero-lhasa.jpg',
                '哈尔滨':'/images/city-hero-haerbin.jpg',
                '贵阳':'/images/city-hero-guiyang.jpg',
                '南宁':'/images/city-hero-nanning.jpg',
                '大连':'/images/city-hero-dalian.jpg',
                '沈阳':'/images/city-hero-shenyang.jpg',
                '郑州':'/images/city-hero-zhengzhou.jpg',
                '福州':'/images/city-hero-fuzhou.jpg',
                '南昌':'/images/city-hero-nanchang.jpg',
                '珠海':'/images/city-hero-zhuhai.jpg',
                '兰州':'/images/city-hero-lanzhou.jpg',
                '西宁':'/images/city-hero-xining.jpg',
                '乌鲁木齐':'/images/city-hero-wulumuqi.jpg',
                '张家界':'/images/city-hero-zhangjiajie.jpg',
                '凤凰':'/images/city-hero-fenghuang.jpg',
                '敦煌':'/images/city-hero-dunhuang.jpg',
                '洛阳':'/images/city-hero-luoyang.jpg',
                '济南':'/images/city-hero-jinan.jpg',
                '北海':'/images/city-hero-beihai.jpg',
                '佛山':'/images/city-hero-foshan.jpg',
                '香港':'/images/city-hero-hongkong.jpg',
                '曼谷':'/images/city-hero-bangkok.jpg',
                '釜山':'/images/city-hero-busan.jpg',
            }"""

HELPER = r'''
            def _build_route_map_svg(itinerary, city_name, title):
                import math as _math
                stops = [s for s in itinerary if isinstance(s, dict)][:8]
                if not stops:
                    return ""
                n = len(stops)
                W, H = 840, 320
                pad_x, pad_y = 70, 70
                pts = []
                for i in range(n):
                    t = i / max(n - 1, 1)
                    x = pad_x + t * (W - 2 * pad_x)
                    y = pad_y + 70 + 65 * _math.sin(t * _math.pi * 1.15) + (18 if i % 2 else -12)
                    pts.append((x, y))
                path_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
                area = path_d + f" L {pts[-1][0]:.1f},{H-28} L {pts[0][0]:.1f},{H-28} Z"
                circles = labels = ""
                for i, (stop, (x, y)) in enumerate(zip(stops, pts)):
                    name = (stop.get("title") or stop.get("name") or f"站{i+1}")[:14]
                    time = stop.get("time") or ""
                    name = name.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')
                    time = time.replace("&","&amp;")
                    fill = "#2d6a4f" if i == 0 else ("#d4a843" if i == n - 1 else "#40916c")
                    circles += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="{fill}" stroke="#fff" stroke-width="3"/>'
                    circles += f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="central" fill="#fff" font-size="11" font-weight="700">{i+1}</text>'
                    ly = y - 26 if i % 2 == 0 else y + 30
                    labels += f'<text x="{x:.1f}" y="{ly:.1f}" text-anchor="middle" fill="#1b4332" font-size="11" font-weight="600">{name}</text>'
                    if time:
                        labels += f'<text x="{x:.1f}" y="{ly+13:.1f}" text-anchor="middle" fill="#6b705c" font-size="9">{time}</text>'
                grid_v = "".join(f'<line x1="{x}" y1="24" x2="{x}" y2="{H-24}" stroke="#b7e4c7" stroke-width="1" opacity=".4"/>' for x in range(100, W, 100))
                grid_h = "".join(f'<line x1="36" y1="{y}" x2="{W-36}" y2="{y}" stroke="#b7e4c7" stroke-width="1" opacity=".3"/>' for y in range(64, H, 48))
                cname = str(city_name).replace("&","&amp;").replace("<","&lt;")
                parts = [
                    '<section class="route-map"><h2>🗺️ 路线示意图</h2>',
                    '<div class="map-wrap"><svg viewBox="0 0 %d %d" role="img" aria-label="%s路线图" xmlns="http://www.w3.org/2000/svg">' % (W, H, cname),
                    '<defs>',
                    '<linearGradient id="mapBg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%%" stop-color="#e8f5e9"/><stop offset="100%%" stop-color="#f0f7f4"/></linearGradient>',
                    '<linearGradient id="pathGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0%%" stop-color="#74c69d"/><stop offset="100%%" stop-color="#2d6a4f"/></linearGradient>',
                    '<filter id="soft"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity=".14"/></filter>',
                    '</defs>',
                    '<rect width="%d" height="%d" rx="16" fill="url(#mapBg)"/>' % (W, H),
                    grid_v + grid_h,
                    '<path d="%s" fill="#74c69d" opacity=".12"/>' % area,
                    '<path d="%s" fill="none" stroke="url(#pathGrad)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" filter="url(#soft)"/>' % path_d,
                    '<path d="%s" fill="none" stroke="#fff" stroke-width="1.5" stroke-dasharray="6 8" opacity=".65"/>' % path_d,
                    circles + labels,
                    '<text x="22" y="26" fill="#1b4332" font-size="13" font-weight="700">📍 %s</text>' % cname,
                    '<text x="%d" y="26" text-anchor="end" fill="#6b705c" font-size="11">%d 个途经点 · 绿迹路线图</text>' % (W - 22, n),
                    '</svg></div>',
                    '<p class="map-note">示意图按行程顺序连线，实际步行/骑行路径以向导现场安排为准。</p>',
                    '</section>',
                ]
                return "".join(parts)

'''

GALLERY_ELSE = '''            else:
                # City-matched local gallery + SVG route map (no random placeholders)
                import os as _gal_os
                _gpy = pinyin_map_route.get(r['city'], '')
                _gall = []
                for _i in range(1, 4):
                    _gp = f'/opt/greentrace/images/city-gallery-{_gpy}-{_i}.jpg'
                    if _gpy and _gal_os.path.exists(_gp):
                        _gall.append(f'/images/city-gallery-{_gpy}-{_i}.jpg')
                if not _gall and _gpy:
                    for _cand in (f'/images/city-hero-{_gpy}.jpg', f'/images/city-{_gpy}.jpg'):
                        if _gal_os.path.exists('/opt/greentrace' + _cand):
                            _gall.append(_cand)
                fallback_imgs = "".join([
                    f'<div class="gallery-item"><img src="{p}" loading="lazy" alt="{r["title"]} · {r["city"]}"></div>'
                    for p in _gall
                ])
                map_html = _build_route_map_svg(itinerary, r['city'], r['title']) if itinerary else ""
                photo_html = (map_html or "") + (
                    f'<section class="gallery"><h2>📸 路线图览</h2><div class="gallery-grid">{fallback_imgs}</div></section>'
                    if fallback_imgs else map_html
                )
'''


def run(cmd, check=True):
    LOG.append(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.stdout.strip():
        LOG.append(r.stdout.strip()[:2000])
    if r.stderr.strip():
        LOG.append(r.stderr.strip()[:1000])
    if check and r.returncode != 0:
        raise RuntimeError(cmd)
    return r


def download(ref, dest):
    if ref.startswith("photo-"):
        url = f"https://images.unsplash.com/{ref}?w=1600&h=900&fit=crop&q=85"
    else:
        url = f"https://unsplash.com/photos/{ref}/download?force=true&w=1600"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=60).read()
    if len(data) < 8000 or data[:5].lstrip()[:1] == b"<":
        return False
    Path(dest).write_bytes(data)
    LOG.append(f"dl {ref} {len(data)}b")
    return True


def download_wiki(filename, dest):
    url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width=1600"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=60).read()
    if len(data) < 8000:
        return False
    Path(dest).write_bytes(data)
    LOG.append(f"wiki {filename} {len(data)}b")
    return True


def emit_variants(raw, pinyin):
    IMG.mkdir(parents=True, exist_ok=True)
    hero = IMG / f"city-hero-{pinyin}.jpg"
    card = IMG / f"city-{pinyin}.jpg"
    for p in (hero, card):
        bak = Path(str(p) + ".bak.p2")
        if p.exists() and not bak.exists():
            run(f"cp '{p}' '{bak}'", check=False)
    run(f"convert '{raw}' -auto-orient -strip -resize '1600x700^' -gravity center -extent 1200x500 -quality 88 '{hero}'")
    run(f"convert '{raw}' -auto-orient -strip -resize '800x600^' -gravity center -extent 600x450 -quality 88 '{card}'")
    run(f"cwebp -q 78 '{hero}' -o '{IMG}/city-hero-{pinyin}.webp'", check=False)
    run(f"cwebp -q 78 '{card}' -o '{IMG}/city-{pinyin}.webp'", check=False)
    for i, grav in enumerate(("center", "North", "South"), 1):
        out = IMG / f"city-gallery-{pinyin}-{i}.jpg"
        run(
            f"convert '{raw}' -auto-orient -strip -resize '1400x900^' "
            f"-gravity {grav} -extent 1200x800 -quality 85 '{out}'",
            check=False,
        )


def refresh_images():
    for py, ref in VERIFIED.items():
        raw = f"/tmp/gt-raw-{py}.jpg"
        if download(ref, raw):
            emit_variants(raw, py)
    for py, fn in WIKI.items():
        raw = f"/tmp/gt-wiki-{py}.jpg"
        if download_wiki(fn, raw):
            emit_variants(raw, py)
    # Tiny heroes → generate gallery from existing if possible
    for hero in IMG.glob("city-hero-*.jpg"):
        py = hero.name[len("city-hero-") : -4]
        gal = IMG / f"city-gallery-{py}-1.jpg"
        if not gal.exists() and hero.stat().st_size > 40000:
            emit_variants(str(hero), py)
    LOG.append("images refreshed")


def patch_server():
    content = SERVER.read_text(encoding="utf-8")
    m = re.search(r"city_unsplash = \{.*?\n            \}", content, re.S)
    if not m:
        raise RuntimeError("city_unsplash missing")
    content = content[: m.start()] + "city_unsplash = " + CITY_UNSPLASH_BODY + content[m.end() :]

    content, n = re.subn(
        r"thumb = photos\[0\] if photos else f['\"]https://picsum\.photos/seed/route\{r\[\"id\"\]\}/400/300['\"]",
        "thumb = photos[0] if photos else city_thumb_url",
        content,
        count=1,
    )
    LOG.append(f"thumb={n}")
    content = content.replace(
        "city_thumb_url = city_unsplash.get(city_slug, 'https://images.unsplash.com/photo-1506901429812-b3e4c1cba5e0?w=400&h=300&fit=crop')",
        "city_thumb_url = city_unsplash.get(city_slug, '/images/city-hero-beijing.jpg')",
    )

    if "_build_route_map_svg" not in content:
        marker = "            # Itinerary timeline HTML"
        content = content.replace(marker, HELPER + "\n" + marker, 1)

    old_gallery = (
        "            else:\n"
        "                # Generate 3 fallback images using picsum with route-id seeds\n"
        '                fallback_imgs = "".join([f\'<div class="gallery-item"><img src="https://picsum.photos/seed/route{r["id"]}g{i}/400/300" loading="lazy" alt="{r["title"]} 图{i+1}"></div>\' for i in range(3)])\n'
        '                photo_html = f\'<section class="gallery"><h2>📸 路线图览</h2><div class="gallery-grid">{fallback_imgs}</div></section>\'\n'
    )
    if old_gallery in content:
        content = content.replace(old_gallery, GALLERY_ELSE, 1)
        LOG.append("gallery replaced")

    real = 'photo_html = f\'<section class="gallery"><h2>📸 路线实拍</h2><div class="gallery-grid">{imgs}</div></section>\''
    if real in content and "photo_html = (map_html or \"\") + f'<section class=\"gallery\"><h2>📸 路线实拍" not in content:
        content = content.replace(
            real,
            "map_html = _build_route_map_svg(itinerary, r['city'], r['title']) if itinerary else \"\"\n"
            "                photo_html = (map_html or \"\") + f'<section class=\"gallery\"><h2>📸 路线实拍</h2><div class=\"gallery-grid\">{imgs}</div></section>'",
            1,
        )

    # CSS inside f-string → double braces
    if ".route-map{{" not in content and ".route-map{" not in content:
        content = content.replace(
            "/* ── Gallery ── */",
            "/* ── Route Map ── */\n"
            ".route-map{{margin-bottom:36px}}\n"
            ".map-wrap{{background:var(--w);border-radius:var(--r);padding:12px;box-shadow:0 2px 12px rgba(0,0,0,.04);overflow:hidden}}\n"
            ".map-wrap svg{{width:100%;height:auto;display:block}}\n"
            ".map-note{{font-size:.8rem;color:var(--m);margin-top:8px}}\n"
            "/* ── Gallery ── */",
            1,
        )
    elif ".route-map{margin-bottom" in content and ".route-map{{margin-bottom" not in content:
        content = content.replace(".route-map{margin-bottom:36px}", ".route-map{{margin-bottom:36px}}")
        content = content.replace(
            ".map-wrap{background:var(--w);border-radius:var(--r);padding:12px;box-shadow:0 2px 12px rgba(0,0,0,.04);overflow:hidden}",
            ".map-wrap{{background:var(--w);border-radius:var(--r);padding:12px;box-shadow:0 2px 12px rgba(0,0,0,.04);overflow:hidden}}",
        )
        content = content.replace(
            ".map-wrap svg{width:100%;height:auto;display:block}",
            ".map-wrap svg{{width:100%;height:auto;display:block}}",
        )
        content = content.replace(
            ".map-note{font-size:.8rem;color:var(--m);margin-top:8px}",
            ".map-note{{font-size:.8rem;color:var(--m);margin-top:8px}}",
        )

    content = re.sub(r"https://picsum\.photos/[^\"'\s]+", "/images/city-hero-beijing.jpg", content)
    ast.parse(content)
    SERVER.write_text(content, encoding="utf-8")
    LOG.append("server patched AST OK")


def main():
    run(f"cp {SERVER} {SERVER}.bak.p2-$(date +%Y%m%d%H%M)")
    refresh_images()
    patch_server()
    run("sudo systemctl restart greentrace")
    time.sleep(2)
    run("systemctl is-active greentrace")
    html = urllib.request.urlopen(
        "https://greentrace.com.cn/route/6e8bbc0cc3964531b4e0", timeout=30
    ).read().decode("utf-8", "ignore")
    LOG.append(
        f"verify picsum={html.count('picsum')} map={html.count('路线示意图')} "
        f"gal={html.count('city-gallery-chengdu')}"
    )
    report = "\n".join(LOG)
    Path("/tmp/greentrace-p2.log").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
