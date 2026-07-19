#!/usr/bin/env python3
"""P2b — fix ALL /city/ list page covers (city-*.jpg preferred by server)."""
import ast
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

LOG = []
BASE = Path("/opt/greentrace")
SERVER = BASE / "server.py"
IMG = BASE / "images"
UA = "Mozilla/5.0 (compatible; GreenTraceBot/1.0; +https://greentrace.com.cn)"
FONT = "WenQuanYi-Zen-Hei"

# pinyin used by /city/ list
PINYIN = {
    "成都": "chengdu", "杭州": "hangzhou", "厦门": "xiamen", "上海": "shanghai",
    "昆明": "kunming", "北京": "beijing", "丽江": "lijiang", "大理": "dali",
    "西安": "xian", "重庆": "chongqing", "深圳": "shenzhen", "香港": "hongkong",
    "桂林": "guilin", "天津": "tianjin", "兰州": "lanzhou", "郑州": "zhengzhou",
    "福州": "fuzhou", "武汉": "wuhan", "南宁": "nanning", "北海": "beihai",
    "苏州": "suzhou", "广州": "guangzhou", "南京": "nanjing", "青岛": "qingdao",
    "张家界": "zhangjiajie", "凤凰": "fenghuang", "香格里拉": "xianggelila",
    "贵阳": "guiyang", "拉萨": "lhasa", "三亚": "sanya", "合肥": "hefei",
    "长沙": "changsha", "大连": "dalian", "哈尔滨": "haerbin", "沈阳": "shenyang",
    "珠海": "zhuhai", "延边": "yanbian", "涠洲岛": "weizhoudao", "喀什": "kashi",
    "开封": "kaifeng", "西宁": "xining", "乌鲁木齐": "wulumuqi", "伊犁": "yili",
    "佛山": "foshan", "南昌": "nanchang", "呼和浩特": "huhehaote", "扬州": "yangzhou",
    "敦煌": "dunhuang", "洛阳": "luoyang", "济南": "jinan", "绍兴": "shaoxing",
    "腾冲": "tengchong", "西双版纳": "xishuangbanna", "曼谷": "bangkok", "釜山": "busan",
    # international (extend list page beyond gradient)
    "东京": "tokyo", "京都": "kyoto", "首尔": "seoul", "新加坡": "singapore",
    "纽约": "newyork", "旧金山": "sanfrancisco", "悉尼": "sydney", "迪拜": "dubai",
    "维也纳": "vienna", "布拉格": "prague", "布达佩斯": "budapest",
    "伊斯坦布尔": "istanbul", "开罗": "cairo", "加德满都": "kathmandu",
    "清迈": "chiangmai", "普吉岛": "phuket", "暹粒": "siemreap",
    "河内": "hanoi", "雅加达": "jakarta", "马尼拉": "manila",
    "槟城": "penang", "福冈": "fukuoka", "札幌": "sapporo", "慕尼黑": "munich",
}

# Verified sources: ('unsplash', id) | ('wiki', filename) | ('reuse', pinyin_of_good_local)
# Prefer landmark photos; never reuse wrong stock.
SOURCES = {
    "chengdu": ("unsplash", "ItOVNVIrwAM"),
    "hangzhou": ("unsplash", "IvFtwmRcCQ0"),
    "shanghai": ("wiki", "The_Bund_Shanghai.jpg"),
    "beijing": ("unsplash", "photo-1508804185872-d7badad00f7d"),
    "xiamen": ("unsplash", "XjHNLadzEjY"),
    "kunming": ("wiki", "Shilin_Yunnan_China_Shilin-Stone-Forest-12.jpg"),
    "xian": ("unsplash", "PUCoYaHv_Ys"),
    "guilin": ("wiki", "Guilin_Li_River.jpg"),
    "guangzhou": ("wiki", "Canton_Tower.jpg"),
    "suzhou": ("wiki", "Lingering_Garden.jpg"),
    "qingdao": ("wiki", "Qingdao_Pier.jpg"),
    "nanjing": ("wiki", "Sun_Yat-sen_Mausoleum.jpg"),
    "fenghuang": ("wiki", "Fenghuang_Ancient_Town.jpg"),
    "lhasa": ("wiki", "Potala_Palace.jpg"),
    "lijiang": ("wiki", "Old_Town_of_Lijiang.jpg"),
    "chongqing": ("wiki", "Chaotianmen_Bridge.jpg"),
    "wuhan": ("wiki", "Wuhan_Yangtze_River_Bridge.jpg"),
    "dali": ("wiki", "Dali,_Yunnan.jpg"),
    "shenzhen": ("wiki", "Shenzhen_Skyline.jpg"),
    "sanya": ("wiki", "Sanya_Bay.jpg"),
    "tianjin": ("wiki", "Tianjin_Eye.jpg"),
    "xishuangbanna": ("wiki", "Xishuangbanna.jpg"),
    "changsha": ("wiki", "Yuelu_Mountain.jpg"),
    "guiyang": ("wiki", "Guiyang.jpg"),
    "zhengzhou": ("wiki", "Zhengzhou.jpg"),
    "shenyang": ("wiki", "Shenyang.jpg"),
    "dalian": ("wiki", "Xinghai_Square.jpg"),
    "bangkok": ("wiki", "Wat_Arun.jpg"),
    "seoul": ("wiki", "Gyeongbokgung.jpg"),
    "tokyo": ("wiki", "Shibuya_Crossing.jpg"),
    "singapore": ("wiki", "Merlion_and_Marina_Bay_Sands.jpg"),
    "kyoto": ("wiki", "Kiyomizu-dera_in_Kyoto.jpg"),
    "newyork": ("wiki", "Statue_of_Liberty_7.jpg"),
    # alts
    "shanghai2": ("unsplash", "photo-1548919973-5cef591cdbc9"),
    "hangzhou2": ("wiki", "West_Lake,_Hangzhou.jpg"),
    "beijing2": ("unsplash", "photo-1547981609-4b6bfe67ca0b"),
    "guilin2": ("wiki", "Li_River,_Yongshuo,_Guilin,_China_(18751558398).jpg"),
    "suzhou2": ("wiki", "Garden_of_the_Master_of_the_Nets_(40106133194).jpg"),
}


def log(msg):
    LOG.append(str(msg))
    print(msg, flush=True)


def run(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd}\n{r.stderr}")
    return r


def fetch(url, dest, min_size=15000):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        data = urllib.request.urlopen(req, timeout=60).read()
    except Exception as e:
        log(f"fetch fail {url}: {e}")
        return False
    if len(data) < min_size or data[:3] not in (b"\xff\xd8\xff", b"\x89PN"):
        # allow jpeg only mostly
        if not (len(data) >= min_size and data[:2] == b"\xff\xd8"):
            log(f"bad bytes {len(data)} {url[:80]}")
            return False
    Path(dest).write_bytes(data)
    return True


def fetch_source(kind, ref, dest):
    if kind == "unsplash":
        if ref.startswith("photo-"):
            url = f"https://images.unsplash.com/{ref}?w=1400&h=900&fit=crop&q=85"
        else:
            url = f"https://unsplash.com/photos/{ref}/download?force=true&w=1400"
        return fetch(url, dest)
    if kind == "wiki":
        enc = urllib.parse.quote(ref, safe="(),_")
        url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width=1400"
        return fetch(url, dest, min_size=12000)
    return False


def branded(dest, title, subtitle="绿迹城市探索"):
    """Reliable Chinese-text cover when no landmark photo."""
    # Use convert with WenQuanYi Zen Hei
    run(
        f"convert -size 800x600 gradient:'#1b4332'-'#40916c' "
        f"-fill 'rgba(255,255,255,0.10)' -draw 'circle 120,100 220,200' "
        f"-draw 'circle 680,480 780,580' "
        f"-font '{FONT}' -gravity center -fill white -pointsize 72 "
        f"-annotate +0-24 '{title}' "
        f"-pointsize 26 -fill '#d8f3dc' -annotate +0+48 '{subtitle}' "
        f"'{dest}'"
    )


def emit(raw, pinyin):
    card = IMG / f"city-{pinyin}.jpg"
    hero = IMG / f"city-hero-{pinyin}.jpg"
    webp = IMG / f"city-{pinyin}.webp"
    for p in (card, hero):
        bak = Path(str(p) + ".bak.p2b")
        if p.exists() and not bak.exists():
            run(f"cp '{p}' '{bak}'", check=False)
    run(
        f"convert '{raw}' -auto-orient -strip -resize '900x675^' "
        f"-gravity center -extent 600x450 -quality 88 '{card}'"
    )
    run(
        f"convert '{raw}' -auto-orient -strip -resize '1600x700^' "
        f"-gravity center -extent 1200x500 -quality 88 '{hero}'"
    )
    run(f"cwebp -q 78 '{card}' -o '{webp}'", check=False)
    run(f"cwebp -q 78 '{hero}' -o '{IMG}/city-hero-{pinyin}.webp'", check=False)
    for i, grav in enumerate(("center", "North", "South"), 1):
        gal = IMG / f"city-gallery-{pinyin}-{i}.jpg"
        run(
            f"convert '{raw}' -auto-orient -strip -resize '1400x900^' "
            f"-gravity {grav} -extent 1200x800 -quality 85 '{gal}'",
            check=False,
        )


def refresh_all():
    IMG.mkdir(parents=True, exist_ok=True)
    # remove junk Chinese-filename stubs and 6057-byte stubs
    for fn in list(IMG.iterdir()):
        name = fn.name
        if not name.endswith(".jpg"):
            continue
        if re.search(r"city-[\u4e00-\u9fff]", name):
            fn.unlink(missing_ok=True)
            log(f"removed cn-name junk {name}")
        elif name.startswith("city-") and not name.startswith("city-hero") and not name.startswith("city-gallery"):
            if fn.stat().st_size < 12000:
                fn.unlink(missing_ok=True)
                log(f"removed tiny stub {name}")

    # Build unique pinyin set from PINYIN values
    city_by_py = {}
    for cn, py in PINYIN.items():
        city_by_py[py] = cn

    ok_photo = 0
    ok_brand = 0
    for py, cn in sorted(city_by_py.items(), key=lambda x: x[1]):
        raw = f"/tmp/gt-city-{py}.jpg"
        src = SOURCES.get(py)
        got = False
        if src:
            got = fetch_source(src[0], src[1], raw)
        # try alt keys
        if not got and f"{py}2" in SOURCES:
            s2 = SOURCES[f"{py}2"]
            got = fetch_source(s2[0], s2[1], raw)
        if got:
            emit(raw, py)
            ok_photo += 1
            log(f"PHOTO {cn}/{py}")
        else:
            branded(raw, cn)
            emit(raw, py)
            ok_brand += 1
            log(f"BRAND {cn}/{py}")
    log(f"done photo={ok_photo} brand={ok_brand}")


def patch_server_list_logic():
    """Prefer non-tiny images; expand pinyin_map for international cities."""
    content = SERVER.read_text(encoding="utf-8")

    # Expand all pinyin_map blocks with international cities
    intl_line = (
        "    '东京':'tokyo','京都':'kyoto','首尔':'seoul','新加坡':'singapore',"
        "'纽约':'newyork','旧金山':'sanfrancisco','悉尼':'sydney','迪拜':'dubai',"
        "'维也纳':'vienna','布拉格':'prague','布达佩斯':'budapest',"
        "'伊斯坦布尔':'istanbul','开罗':'cairo','加德满都':'kathmandu',"
        "'清迈':'chiangmai','普吉岛':'phuket','暹粒':'siemreap',"
        "'河内':'hanoi','雅加达':'jakarta','马尼拉':'manila',"
        "'槟城':'penang','福冈':'fukuoka','札幌':'sapporo','慕尼黑':'munich',\n"
    )
    needle = "'西双版纳':'xishuangbanna','曼谷':'bangkok','釜山':'busan',\n}"
    repl = "'西双版纳':'xishuangbanna','曼谷':'bangkok','釜山':'busan',\n" + intl_line + "}"
    if "'东京':'tokyo'" not in content and needle in content:
        n = content.count(needle)
        content = content.replace(needle, repl)
        log(f"intl pinyin injected into {n} pinyin_map blocks")
    elif "'东京':'tokyo'" in content:
        log("intl pinyin already present")
    else:
        log("WARN: pinyin_map needle not found")

    # Improve image selection: skip tiny city-*.jpg stubs
    old = """                    img_paths = [
                        f'/opt/greentrace/images/city-{pinyin}.jpg',
                        f'/opt/greentrace/images/city-hero-{pinyin}.jpg',
                    ]
                    found_img = next((p for p in img_paths if _os.path.exists(p)), None)"""
    new = """                    img_paths = [
                        f'/opt/greentrace/images/city-{pinyin}.jpg',
                        f'/opt/greentrace/images/city-hero-{pinyin}.jpg',
                    ]
                    found_img = None
                    for p in img_paths:
                        if _os.path.exists(p) and _os.path.getsize(p) >= 20000:
                            found_img = p
                            break"""
    if old in content:
        content = content.replace(old, new, 1)
        log("list image size gate added")
    else:
        log("WARN: img_paths block not exact match")

    ast.parse(content)
    SERVER.write_text(content, encoding="utf-8")
    log("server patched")


def verify():
    page = urllib.request.urlopen("https://greentrace.com.cn/city/", timeout=30).read().decode("utf-8", "ignore")
    blocks = re.findall(r'<a class="city-card"[^>]*>.*?</a>', page, re.S)
    grads = sum(1 for b in blocks if "<img" not in b)
    imgs = []
    for b in blocks:
        m = re.search(r'src="([^"]+)"', b)
        if m:
            imgs.append(m.group(1))
    # sample sizes via local filesystem
    tiny = 0
    for src in imgs:
        local = "/opt/greentrace" + src
        if os.path.exists(local) and os.path.getsize(local) < 20000:
            tiny += 1
    log(f"verify cards={len(blocks)} gradient={grads} imgs={len(imgs)} tiny={tiny}")
    # spot-check known good
    for py in ("chengdu", "suzhou", "guilin", "kunming", "tokyo"):
        p = IMG / f"city-{py}.jpg"
        log(f"  {py}: exists={p.exists()} size={p.stat().st_size if p.exists() else 0}")


def main():
    run(f"cp {SERVER} {SERVER}.bak.p2b-$(date +%Y%m%d%H%M)")
    refresh_all()
    patch_server_list_logic()
    run("sudo systemctl restart greentrace")
    time.sleep(2)
    run("systemctl is-active greentrace")
    verify()
    Path("/tmp/greentrace-p2b.log").write_text("\n".join(LOG))


if __name__ == "__main__":
    main()
