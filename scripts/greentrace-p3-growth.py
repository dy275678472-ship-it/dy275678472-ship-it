#!/usr/bin/env python3
"""P3 growth for greentrace — day plans, FAQ/schema, internal links, more city photos."""
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

# Core 8 cities
CORE = ["成都", "重庆", "杭州", "上海", "北京", "厦门", "苏州", "桂林"]

DAY_PLANS = {
    "成都": {
        "title": "成都可执行一日（Citywalk）",
        "summary": "地铁可达 · 步行约 1.2 万步 · 预算 ¥80–150（不含向导）",
        "slots": [
            ("09:00", "人民公园 · 鹤鸣茶社", "地铁 2 号线「人民公园」。点盖碗茶，观察本地晨间节奏。公厕在公园东门侧。"),
            ("11:00", "宽窄巷子外圈绕行", "不要主街打卡；走支巷到文殊院方向，人少、更像日常成都。"),
            ("12:30", "文殊院周边素斋 / 小面", "院外小馆更地道；雨天可改室内茶馆续坐。"),
            ("15:00", "玉林路 / 芳华街漫步", "地铁 3 号线「省体育馆」步行。咖啡馆与旧居民区交错，适合傍晚。"),
            ("18:30", "晚餐：串串或冒菜", "避开网红排队店；选有本地人的二楼小馆。"),
        ],
        "tips": ["夏季避开 13:00–15:00 暴晒", "雨天路线改茶馆+博物馆", "厕所优先商场/地铁站"],
        "metro": "2 号线 → 3 号线；共享单车适合玉林段",
    },
    "重庆": {
        "title": "重庆可执行一日（山城步道）",
        "summary": "轻轨 + 步行 · 爬坡多 · 预算 ¥100–180",
        "slots": [
            ("09:00", "山城巷 / 十八梯", "轨道交通 1 号线「较场口」。带防滑鞋，台阶多。"),
            ("11:30", "白象居 → 江景平台", "俯瞰长江；中午人少更好拍。"),
            ("13:00", "防空洞火锅或小面", "渝中半岛老店，避开洪崖洞正门排队。"),
            ("16:00", "下浩老街", "轨道交通「小什字」转公交；民国石板路，适合慢走。"),
            ("19:00", "南滨路夜景（可选）", "长江索道或南岸观景，夜景高峰 19:30–21:00。"),
        ],
        "tips": ["膝盖不好少选十八梯主线", "夏天备水和毛巾", "雾天夜景一般，改室内"],
        "metro": "1/2/环线组合；山城第三步道可看轻轨穿楼",
    },
    "杭州": {
        "title": "杭州可执行一日（西湖西线）",
        "summary": "公交 + 步行/骑行 · 预算 ¥60–120",
        "slots": [
            ("08:30", "北山街 → 断桥外圈", "地铁 1 号线「龙翔桥」或公交到北山。早去避开旅行团。"),
            ("10:30", "西泠印社 / 孤山", "人文密度高；公厕在孤山停车场附近。"),
            ("12:30", "龙井村简餐", "公交 Y2/Y3；茶农家常菜，避开茶市砍价陷阱。"),
            ("15:00", "九溪烟树徒步", "林荫线，夏季也相对凉快；约 1.5–2 小时。"),
            ("17:30", "回湖滨或河坊街外围", "河坊街主街可跳过，走支巷更舒服。"),
        ],
        "tips": ["桂花季满觉陇极挤，改九溪", "骑行选西山路非苏堤主道", "雨天改中国美院象山"],
        "metro": "1 号线 + 西湖观光巴士；共享单车适合西线",
    },
    "上海": {
        "title": "上海可执行一日（法租界梧桐线）",
        "summary": "地铁 + 步行 · 预算 ¥100–200",
        "slots": [
            ("09:30", "武康路起点", "地铁 10/11 号线「交通大学」。先咖啡再步行。"),
            ("11:00", "安福路 → 永福路", "梧桐树影与老洋房；避开周末中午拥堵。"),
            ("13:00", "午餐：小馆本帮/点心", "选支巷小店，勿跟风排队奶茶。"),
            ("15:00", "张园 / 南京西路外围", "地铁「陕西南路」；室内商业综合体可躲雨。"),
            ("18:00", "外滩可去可不去", "想看江景改十六铺或北外滩，人少。"),
        ],
        "tips": ["共享单车注意非机动车道", "雨天主攻室内美术馆", "周末安福路人流翻倍"],
        "metro": "10/11/1 号线；步行为主",
    },
    "北京": {
        "title": "北京可执行一日（胡同 B 面）",
        "summary": "地铁 + 步行 · 预算 ¥80–160",
        "slots": [
            ("09:00", "鼓楼 / 什刹海北沿", "地铁 8 号线「什刹海」或「鼓楼大街」。先北沿少游客。"),
            ("11:00", "烟袋斜街外围胡同", "钻支巷看四合院门墩；勿只逛主街。"),
            ("12:30", "午餐：炸酱面 / 铜锅", "选有本地人的馆子，避开鼓楼正门口。"),
            ("15:00", "南锣鼓巷外圈 → 国子监街", "国子监街更安静；成贤街书店可歇脚。"),
            ("17:30", "东四 / 朝阳门回程", "地铁 6/5 号线；傍晚光线适合胡同摄影。"),
        ],
        "tips": ["冬季早黑，压缩线路", "共享单车胡同内慎骑", "故宫当天票紧张可改景山远眺"],
        "metro": "6/8/5 号线；步行是核心",
    },
    "厦门": {
        "title": "厦门可执行一日（岛内慢线）",
        "summary": "公交 + 步行 · 预算 ¥70–140",
        "slots": [
            ("08:30", "八市早餐", "轮渡附近；沙茶面+海鲜粥。人多但周转快。"),
            ("10:00", "中山路支巷 → 沙坡尾", "沙坡尾艺术区，涂鸦与船坞；中午光线硬可进咖啡馆。"),
            ("13:00", "厦港 / 大学路一带", "适合慢走；公厕在社区广场。"),
            ("15:30", "环岛路片段骑行（可选）", "共享单车；只骑一段，勿硬骑全程。"),
            ("18:00", "晚餐回开禾路或百家村", "本地夜宵选择多。"),
        ],
        "tips": ["鼓浪屿可改天专访，勿塞进一日", "台风天改室内博物馆", "防晒必备"],
        "metro": "岛内公交为主；BRT 辅助",
    },
    "苏州": {
        "title": "苏州可执行一日（园林外的城）",
        "summary": "地铁 + 步行 · 预算 ¥90–160",
        "slots": [
            ("09:00", "平江路外圈水道", "地铁 1/4 号线「相门」或「临顿路」。走水道内侧少摊贩。"),
            ("11:00", "拙政园可去可留", "人多则改耦园/沧浪亭；提前预约。"),
            ("13:00", "午餐：苏式面", "观前外圈小店，避免观前主街。"),
            ("15:00", "山塘街尾段 / 虎丘方向（选一）", "虎丘需半日；时间紧只走山塘尾段。"),
            ("17:30", "回古城茶馆歇脚", "听一曲评弹更苏州。"),
        ],
        "tips": ["黄金周园林需预约", "骑行注意石板路", "雨天园林倒影反而好看"],
        "metro": "1/2/4 号线；古城内步行优先",
    },
    "桂林": {
        "title": "桂林可执行一日（漓江旁慢走）",
        "summary": "公交 + 步行/船 · 预算 ¥120–250",
        "slots": [
            ("08:00", "两江四湖外圈或象鼻山远眺", "早去光线好；象鼻山可只外拍省门票。"),
            ("10:30", "正阳步行街支巷早餐延展", "米粉店选有本地人排队但不网红打卡的。"),
            ("13:00", "前往阳朔方向（可选半日）", "高铁/大巴；或改市区叠彩山。"),
            ("16:00", "漓江边慢走 / 骑行", "避开游船码头高峰。"),
            ("18:30", "市区夜景或早歇", "体力型行程建议早睡。"),
        ],
        "tips": ["雨季路面湿滑", "游船选白天非夜游更值", "防晒与防蚊"],
        "metro": "公交 + 城际；阳朔可拆第二日",
    },
}

CITY_FAQS = {
    "成都": [
        ("成都一日怎么坐地铁最省事？", "人民公园（2 号线）→ 文殊院方向步行 → 省体育馆（3 号线）玉林路，基本覆盖慢生活主轴。"),
        ("雨天怎么改路线？", "茶馆 + 博物馆（四川博物院/宽窄室内）+ 商场连廊，少走开敞河堤。"),
        ("需要向导吗？", "第一次来、想进社区院落或夜市点餐，建议约半日向导；熟路可自走绿迹路线。"),
    ],
    "重庆": [
        ("重庆一日爬坡多吗？", "渝中半岛主线台阶多，选山城巷可控制强度；膝盖不好改南滨平路。"),
        ("怎么看轻轨穿楼？", "李子坝站旁观景平台，早晚人少；勿站轨行区。"),
        ("夏天怎么避暑？", "上午步道，下午防空洞火锅或商场，夜景放晚上。"),
    ],
    "杭州": [
        ("西湖一日怎么避开人潮？", "走西线（北山→龙井→九溪），少逛断桥主拍照点中午时段。"),
        ("能骑行吗？", "西山路、白堤外围适合；苏堤主道行人多，慎骑。"),
        ("茶村怎么不被坑？", "明码标价茶农家；不跟临时拉客进茶庄。"),
    ],
    "上海": [
        ("法租界一日怎么走？", "交大站上武康路，安福→永福，陕西南路收尾，约 4–5 小时含歇脚。"),
        ("外滩要不要去？", "想少人可改北外滩或十六铺；外滩夜景高峰极挤。"),
        ("雨天替代？", "美术馆（中华艺术宫/复星艺术中心）+ 商场连廊。"),
    ],
    "北京": [
        ("胡同一日怎么规划？", "什刹海北沿→鼓楼支巷→国子监街，比南锣主街舒服。"),
        ("故宫怎么搭配？", "故宫需单独预约半天；胡同线建议另日或只远眺景山。"),
        ("冬天注意什么？", "路面干冷风大，压缩户外段，多进茶馆暖场。"),
    ],
    "厦门": [
        ("鼓浪屿要塞进一日吗？", "不建议；岛内八市+沙坡尾已满，鼓浪屿留给第二天。"),
        ("怎么低碳出行？", "公交 + 步行 + 环岛路短骑，少打车。"),
        ("台风天怎么办？", "改博物馆与商场，观海点关闭时勿靠近防浪堤。"),
    ],
    "苏州": [
        ("园林和古城一日怎么选？", "时间紧：平江水道 + 一座中型园林（耦园/沧浪亭）；拙政园留给专日。"),
        ("需要预约吗？", "旺季拙政园/留园建议预约；平江路免费。"),
        ("适合带老人吗？", "平江水道平缓；虎丘与大园林台阶多，量力而行。"),
    ],
    "桂林": [
        ("市区和阳朔怎么排？", "一日够市区慢走；阳朔建议第二天早出发。"),
        ("游船值得吗？", "白天漓江精华段体验更好；纯打卡可改岸步。"),
        ("雨季注意？", "山路湿滑，改市区两江四湖外圈。"),
    ],
}

BLOG_BY_CITY = {
    "成都": "/blog/chengdu-food-walk",
    "重庆": "/blog/chongqing-mountain-trails",
    "杭州": "/blog/hangzhou-westlake-cycling",
    "上海": "/blog/shanghai-french-concession",
    "北京": "/blog/beijing-hutong-citywalk",
    "厦门": "/blog/xiamen-lowcarbon-travel",
    "苏州": "/blog/citywalk-guide-beginner",
    "桂林": "/blog/spring-citywalk-routes",
    "西安": "/blog/xian-citywall-cycling",
    "大理": "/blog/dali-erhai-cycling",
    "广州": "/blog/guangzhou-old-town",
    "南京": "/blog/nanjing-wutong-avenue",
}

RELATED_CITIES = {
    "成都": ["重庆", "西安", "昆明"],
    "重庆": ["成都", "贵阳", "张家界"],
    "杭州": ["苏州", "上海", "南京"],
    "上海": ["杭州", "苏州", "南京"],
    "北京": ["天津", "西安", "哈尔滨"],
    "厦门": ["福州", "广州", "深圳"],
    "苏州": ["杭州", "上海", "南京"],
    "桂林": ["凤凰", "南宁", "贵阳"],
}

WIKI_UPGRADE = {
    "luoyang": "Longmen_Grottoes.jpg",
    "sydney": "Sydney_Opera_House_Sails.jpg",
    "prague": "Charles_Bridge_Prague.jpg",
    "istanbul": "Hagia_Sophia_Mars_2013.jpg",
    "chiangmai": "Wat_Chedi_Luang.jpg",
    "hanoi": "Hoan_Kiem_Lake.jpg",
    "yangzhou": "Slender_West_Lake.jpg",
    "xianggelila": "Songzanlin_Monastery.jpg",
    "beihai": "Beihai_Silver_Beach.jpg",
    "xining": "Kumbum_Monastery.jpg",
    "yanbian": "Yanji.jpg",
    "sapporo": "Sapporo_TV_Tower.jpg",
    "fukuoka": "Fukuoka_Tower.jpg",
    "siemreap": "Angkor_Wat.jpg",
    "manila": "Intramuros_Manila.jpg",
    "cairo": "Giza_pyramid_complex.jpg",
    "kathmandu": "Boudhanath.jpg",
    "budapest": "Hungarian_Parliament_Building.jpg",
}


def log(m):
    LOG.append(str(m))
    print(m, flush=True)


def run(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd}\n{r.stderr[:500]}")
    return r


def esc(s):
    return (
        str(s)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace('"', '\\"')
    )


def build_dayplan_html(city):
    plan = DAY_PLANS[city]
    rows = ""
    for t, title, desc in plan["slots"]:
        rows += (
            f'<div class="dp-row"><div class="dp-time">{t}</div>'
            f'<div class="dp-body"><strong>{title}</strong><p>{desc}</p></div></div>'
        )
    tips = "".join(f"<li>{x}</li>" for x in plan["tips"])
    return (
        f'<section id="dayplan" class="dayplan">'
        f'<h2>🚶 {plan["title"]}</h2>'
        f'<p class="dp-sum">{plan["summary"]} · 交通：{plan["metro"]}</p>'
        f'<div class="dp-list">{rows}</div>'
        f'<div class="dp-tips"><strong>避雷与小贴士</strong><ul>{tips}</ul></div>'
        f"</section>"
    )


def build_faq_block(city):
    faqs = CITY_FAQS[city]
    items = "".join(
        f'<div class="faq-item"><h3>{q}</h3><p>{a}</p></div>' for q, a in faqs
    )
    # FAQPage schema entities
    ent = []
    for q, a in faqs:
        ent.append(
            '{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
            % (q.replace('"', '\\"'), a.replace('"', '\\"'))
        )
    schema = (
        '<script type="application/ld+json">'
        '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}'
        "</script>" % ",".join(ent)
    )
    return schema, f'<section id="faq"><h2>❓ 常见问题</h2>{items}</section>'


def build_explore_html(city):
    blog = BLOG_BY_CITY.get(city, "/blog/")
    related = RELATED_CITIES.get(city, ["成都", "杭州", "上海"])
    rel_links = "".join(
        f'<a href="/city/{urllib.parse.quote(c)}">{c}</a>' for c in related if c != city
    )
    return (
        f'<section id="explore" class="explore">'
        f"<h2>🧭 继续探索</h2>"
        f'<div class="explore-grid">'
        f'<a class="ex-card" href="/guide/{urllib.parse.quote(city)}">📖 {city}完整攻略</a>'
        f'<a class="ex-card" href="{blog}">✍️ 相关博客</a>'
        f'<a class="ex-card" href="/citywalk/">🚶 Citywalk 频道</a>'
        f'<a class="ex-card" href="/cycling/">🚲 骑行频道</a>'
        f'<a class="ex-card" href="/transit/">🚌 公交探索</a>'
        f'<a class="ex-card" href="/routes/">🗺️ 全部路线</a>'
        f"</div>"
        f'<p class="ex-related">相近城市：{rel_links}</p>'
        f"</section>"
    )


def patch_server_v2():
    """Safer patch: pre-render HTML maps as Python string dicts, inject into template."""
    content = SERVER.read_text(encoding="utf-8")
    if "P3_DAYPLAN_HTML" in content:
        log("P3 already patched")
        return

    # Prebuild HTML for each city (escaped for embedding in Python source as dict of strings)
    day_map = {}
    faq_html_map = {}
    faq_schema_map = {}
    explore_map = {}
    for city in CORE:
        day_map[city] = build_dayplan_html(city)
        sch, fh = build_faq_block(city)
        faq_schema_map[city] = sch
        faq_html_map[city] = fh
        explore_map[city] = build_explore_html(city)

    def to_py_dict(d):
        parts = []
        for k, v in d.items():
            parts.append(f"                {k!r}: {v!r},")
        return "{\n" + "\n".join(parts) + "\n            }"

    block = (
        "\n            # --- P3 content blocks ---\n"
        f"            P3_DAYPLAN_HTML = {to_py_dict(day_map)}\n"
        f"            P3_FAQ_HTML = {to_py_dict(faq_html_map)}\n"
        f"            P3_FAQ_SCHEMA = {to_py_dict(faq_schema_map)}\n"
        f"            P3_EXPLORE_HTML = {to_py_dict(explore_map)}\n"
        "            p3_day_html = P3_DAYPLAN_HTML.get(city_slug, '')\n"
        "            p3_faq_html = P3_FAQ_HTML.get(city_slug, '')\n"
        "            p3_faq_schema = P3_FAQ_SCHEMA.get(city_slug, '')\n"
        "            p3_explore_html = P3_EXPLORE_HTML.get(city_slug, '')\n"
    )

    marker = "            city_intro = city_intros.get(city_slug,"
    idx = content.find(marker)
    if idx < 0:
        raise RuntimeError("city_intro marker missing")
    # insert after the city_intro assignment line
    end = content.find("\n", content.find("\n", idx) + 1)
    # find full line end of city_intro =
    line_end = content.find("\n", idx)
    # city_intro may be one long line
    content = content[: line_end + 1] + block + content[line_end + 1 :]
    log("injected P3 dicts")

    # CSS (double braces for f-string template)
    css = (
        "/* P3 dayplan / faq / explore */\n"
        ".dayplan{{background:var(--card);border-radius:var(--radius);padding:24px;box-shadow:0 2px 10px rgba(0,0,0,.04);margin-bottom:36px}}\n"
        ".dp-sum{{color:var(--muted);font-size:.9rem;margin-bottom:16px}}\n"
        ".dp-row{{display:flex;gap:14px;padding:12px 0;border-bottom:1px solid var(--green-pale)}}\n"
        ".dp-row:last-child{{border-bottom:none}}\n"
        ".dp-time{{flex:0 0 64px;font-weight:700;color:var(--green-mid);font-size:.9rem}}\n"
        ".dp-body strong{{display:block;color:var(--green-dark);margin-bottom:4px}}\n"
        ".dp-body p{{font-size:.88rem;color:var(--muted);margin:0}}\n"
        ".dp-tips{{margin-top:14px;background:var(--bg);border-radius:12px;padding:14px 16px}}\n"
        ".dp-tips ul{{margin:8px 0 0 18px;color:var(--muted);font-size:.88rem}}\n"
        ".faq-item{{background:var(--card);border-radius:12px;padding:14px 18px;margin-bottom:10px;box-shadow:0 2px 6px rgba(0,0,0,.03)}}\n"
        ".faq-item h3{{font-size:.95rem;color:var(--green-dark);margin-bottom:6px}}\n"
        ".faq-item p{{font-size:.88rem;color:var(--muted);margin:0}}\n"
        ".explore-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin:12px 0}}\n"
        ".ex-card{{display:block;padding:14px 16px;background:var(--card);border-radius:12px;text-decoration:none;color:var(--green-dark);font-weight:600;font-size:.9rem;box-shadow:0 2px 6px rgba(0,0,0,.04);border:1px solid var(--green-pale)}}\n"
        ".ex-card:hover{{background:var(--green-mid);color:#fff}}\n"
        ".ex-related a{{margin-right:10px;color:var(--green-accent);text-decoration:none}}\n"
    )
    if ".dayplan{{" not in content:
        content = content.replace(
            "/* CTA */\n.cta{{",
            css + "/* CTA */\n.cta{{",
            1,
        )
        log("added P3 CSS")

    # Insert FAQ schema next to TouristDestination script
    if "{p3_faq_schema}" not in content:
        content = content.replace(
            '<script type="application/ld+json">{{"@context":"https://schema.org","@type":"TouristDestination"',
            "{p3_faq_schema}\n"
            '<script type="application/ld+json">{{"@context":"https://schema.org","@type":"TouristDestination"',
            1,
        )
        log("faq schema slot")

    # Insert sections in body: after city-intro, dayplan; before stay, faq+explore
    old_intro_close = (
        '<div class="city-intro"><p>{city_intro}</p><p style="margin-top:12px">'
        '<a href="/guide/{urllib.parse.quote(city_slug)}" '
    )
    # Simpler: after `<main>\n<section id="routes"` insert dayplan first
    if "{p3_day_html}" not in content:
        content = content.replace(
            "<main>\n<section id=\"routes\">",
            "<main>\n{p3_day_html}\n<section id=\"routes\">",
            1,
        )
        log("dayplan slot")
    if "{p3_faq_html}" not in content:
        content = content.replace(
            '<section id="stay"',
            "{p3_faq_html}\n{p3_explore_html}\n<section id=\"stay\"",
            1,
        )
        log("faq+explore slots")

    # Expand guide page FAQs for core cities missing rich FAQs
    # Add Suzhou/Xiamen/Guilin/Shanghai/Beijing if not in faqs dict on guide page
    guide_faq_extra = {
        "上海": [
            (
                "上海法租界一日怎么走？",
                "交通大学地铁站上武康路，经安福路、永福路到陕西南路，约 4–5 小时。",
            ),
            ("外滩一定要去吗？", "想少人可改北外滩；外滩夜景高峰很挤。"),
            ("雨天怎么办？", "美术馆 + 商场连廊，少走外滩江风段。"),
        ],
        "北京": [
            ("胡同一日怎么规划？", "什刹海北沿→鼓楼支巷→国子监街，比南锣主街舒服。"),
            ("和故宫怎么搭配？", "故宫单独半天；胡同线建议另排。"),
            ("冬天注意什么？", "压缩户外，多进茶馆暖场。"),
        ],
        "厦门": [
            ("鼓浪屿要塞进一日吗？", "不建议；八市+沙坡尾已满。"),
            ("怎么低碳玩？", "公交+步行+环岛路短骑。"),
            ("台风天怎么办？", "改室内，勿近防浪堤。"),
        ],
        "苏州": [
            ("园林怎么选？", "时间紧选耦园/沧浪亭；拙政园建议专日预约。"),
            ("平江路值得吗？", "值得走水道内侧，少逛主街摊贩。"),
            ("适合老人吗？", "平江平缓；虎丘台阶多。"),
        ],
        "桂林": [
            ("市区和阳朔怎么排？", "一日市区；阳朔第二天早出发。"),
            ("游船值得吗？", "白天精华段更好；可改岸步。"),
            ("雨季注意？", "山路湿滑，改两江四湖外圈。"),
        ],
    }
    # inject into guide faqs dict if keys missing
    for city, pairs in guide_faq_extra.items():
        key = f"'{city}':["
        if f"'{city}':[" not in content and f'"{city}":[' not in content:
            # insert before closing of faqs = {
            needle = "            faqs = {\n"
            if needle in content and f"'{city}'" not in content[content.find("faqs = {"):content.find("faqs = {")+800]:
                # find faqs block end `            }`
                pass
        # Use replace on known end of Chongqing faq entry
    # Append after Chongqing faq list if cities missing
    cq_end = (
        "('重庆哪个季节去？','3-5月和10-11月最舒适。夏天太热但防空洞火锅很有特色，冬天的雾气给山城加了一层滤镜。')],\n"
    )
    if cq_end in content and "'上海':[" not in content[content.find("faqs = {"): content.find("faqs = {") + 2500]:
        extra_src = ""
        for city, pairs in guide_faq_extra.items():
            pair_s = ",".join(f"('{q}','{a}')" for q, a in pairs)
            extra_src += f"                '{city}':[{pair_s}],\n"
        content = content.replace(cq_end, cq_end + extra_src, 1)
        log("expanded guide FAQs")

    # Deepen guide related links if simple
    old_rel = (
        "related = f'<div class=\"related\"><h3>探索更多</h3>"
        "<a href=\"/city/{urllib.parse.quote(guide_city)}\">🏙️ {guide_city}落地页</a>"
    )
    # leave as is if complex; add blog link via replace of related div builder
    if "相关博客" not in content[content.find("/guide/") : content.find("/guide/") + 5000] if "/guide/" in content else True:
        # patch related string
        old = (
            "related = f'<div class=\"related\"><h3>探索更多</h3>"
            "<a href=\"/city/{urllib.parse.quote(guide_city)}\">🏙️ {guide_city}落地页</a>"
            "<a href=\"/routes/\">🗺️ 全部路线</a>"
            "<a href=\"/city/\">🌍 全部城市</a>"
            "<a href=\"/ambassador.html\">✨ 城市主理人</a></div>'"
        )
        new = (
            "related = f'<div class=\"related\"><h3>探索更多</h3>"
            "<a href=\"/city/{urllib.parse.quote(guide_city)}\">🏙️ {guide_city}落地页</a>"
            "<a href=\"/blog/\">✍️ 博客</a>"
            "<a href=\"/citywalk/\">🚶 Citywalk</a>"
            "<a href=\"/routes/\">🗺️ 全部路线</a>"
            "<a href=\"/city/\">🌍 全部城市</a>"
            "<a href=\"/ambassador.html\">✨ 城市主理人</a></div>'"
        )
        if old in content:
            content = content.replace(old, new, 1)
            log("guide related links enriched")

    ast.parse(content)
    SERVER.write_text(content, encoding="utf-8")
    log("server P3 patched AST OK")


def fetch_wiki(name, dest):
    url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(name, safe='(),_')}?width=1400"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=60).read()
    if len(data) < 20000 or data[:2] != b"\xff\xd8":
        return False
    Path(dest).write_bytes(data)
    return True


def emit_city(raw, pinyin):
    card = IMG / f"city-{pinyin}.jpg"
    hero = IMG / f"city-hero-{pinyin}.jpg"
    run(
        f"convert '{raw}' -auto-orient -strip -resize '900x675^' -gravity center -extent 600x450 -quality 88 '{card}'"
    )
    run(
        f"convert '{raw}' -auto-orient -strip -resize '1600x700^' -gravity center -extent 1200x500 -quality 88 '{hero}'"
    )
    run(f"cwebp -q 78 '{card}' -o '{IMG}/city-{pinyin}.webp'", check=False)
    run(f"cwebp -q 78 '{hero}' -o '{IMG}/city-hero-{pinyin}.webp'", check=False)


def upgrade_photos():
    # Prefer downloading on this host with backoff, then convert
    ok = 0
    for py, fn in WIKI_UPGRADE.items():
        raw = f"/tmp/p3-{py}.jpg"
        got = False
        for attempt in range(1, 5):
            try:
                if fetch_wiki(fn, raw):
                    got = True
                    break
            except Exception as e:
                log(f"wiki {py} attempt {attempt}: {e}")
                time.sleep(attempt * 6)
        if got:
            emit_city(raw, py)
            ok += 1
            log(f"PHOTO {py}")
        else:
            log(f"SKIP {py}")
        time.sleep(2)
    log(f"photos upgraded {ok}/{len(WIKI_UPGRADE)}")


def verify():
    import urllib.request as u

    for city in CORE:
        url = "https://greentrace.com.cn/city/" + urllib.parse.quote(city)
        html = u.urlopen(url, timeout=30).read().decode("utf-8", "ignore")
        log(
            f"VERIFY {city}: dayplan={html.count('id=\"dayplan\"')} faq={html.count('id=\"faq\"')} "
            f"explore={html.count('id=\"explore\"')} FAQPage={html.count('FAQPage')} "
            f"citywalk={html.count('/citywalk/')} under_construction={'建设中' in html}"
        )
    html = u.urlopen(
        "https://greentrace.com.cn/guide/" + urllib.parse.quote("成都"), timeout=30
    ).read().decode()
    log(f"VERIFY guide: blog_link={html.count('/blog/')} citywalk={html.count('Citywalk')}")
    html = u.urlopen(
        "https://greentrace.com.cn/guide/" + urllib.parse.quote("上海"), timeout=30
    ).read().decode()
    log(f"VERIFY guide 上海: ok={len(html)>2000} blog={html.count('/blog/')}")

def seed_shanghai_if_needed():
    """Shanghai had zero approved routes → city page short-circuited to 建设中."""
    import json
    import sqlite3
    import uuid
    from datetime import datetime, timezone

    db = sqlite3.connect(str(BASE / "greentrace.db"))
    db.row_factory = sqlite3.Row
    n = db.execute(
        "select count(*) c from hidden_routes where city='上海' and status='approved'"
    ).fetchone()["c"]
    if n > 0:
        log(f"shanghai routes already {n}")
        db.close()
        return
    g = db.execute(
        "select id from guides where status='已通过' limit 1"
    ).fetchone()
    if not g:
        log("no guide for shanghai seed")
        db.close()
        return
    guide_id = g["id"]
    routes = [
        (
            "法租界梧桐 Citywalk",
            "从交通大学出发，沿武康路、安福路、永福路步行，穿过法租界梧桐与老洋房。",
            "半天",
            "Citywalk,建筑,咖啡",
            [
                {"time": "09:30", "title": "武康路起点", "desc": "地铁交通大学站集合"},
                {"time": "11:00", "title": "安福路 → 永福路", "desc": "梧桐与老洋房"},
                {"time": "15:00", "title": "张园 / 陕西南路", "desc": "室内可躲雨"},
            ],
            ["穿舒适步行鞋", "周末人流翻倍建议工作日"],
            "地铁 10/11/1 号线",
        ),
        (
            "徐汇滨江慢骑",
            "从龙华附近骑入徐汇滨江绿道，江风与工业遗存并存。",
            "半天",
            "骑行,江景,低碳",
            [
                {"time": "16:00", "title": "取共享单车", "desc": "龙华路附近"},
                {"time": "16:30", "title": "滨江绿道南段", "desc": "慢骑观江"},
                {"time": "18:00", "title": "西岸艺术区", "desc": "可选美术馆"},
            ],
            ["戴头盔", "逆风缩短行程"],
            "共享单车 + 地铁",
        ),
        (
            "文庙旧书 · 老城厢半日",
            "周日文庙旧书市场与老城厢街巷；非周日可改豫园外围支巷。",
            "半天",
            "市井,旧物,步行",
            [
                {"time": "10:00", "title": "文庙旧书（周日）", "desc": "翻书淘旧"},
                {"time": "12:00", "title": "老城厢支巷午餐", "desc": "避开豫园正门"},
            ],
            ["周日早到", "带现金"],
            "地铁 9/10 号线",
        ),
        (
            "71 路看梧桐 · 公交探索",
            "坐 71 路中运量公交沿延安路看梧桐，再短驳到安福路。",
            "半天",
            "公交,城市观察,低碳",
            [
                {"time": "10:00", "title": "上 71 路", "desc": "选靠窗"},
                {"time": "12:30", "title": "安福路漫步", "desc": "短驳+步行"},
            ],
            ["避开早晚高峰"],
            "71 路 + 地铁",
        ),
    ]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    for title, desc, dur, hi, itin, tips, transport in routes:
        rid = uuid.uuid4().hex[:20]
        db.execute(
            "insert into hidden_routes (id, guide_id, city, title, description, duration, highlights, "
            "photos, status, votes, created_at, difficulty, best_season, itinerary, tips, transport, price_range) "
            "values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                rid,
                guide_id,
                "上海",
                title,
                desc,
                dur,
                hi,
                "[]",
                "approved",
                120,
                now,
                "轻松",
                "春秋",
                json.dumps(itin, ensure_ascii=False),
                json.dumps(tips, ensure_ascii=False),
                transport,
                "¥0-299",
            ),
        )
        log(f"seeded shanghai route {title}")
    db.commit()
    db.close()


def main():
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("all", "patch", "seed"):
        seed_shanghai_if_needed()
    if mode in ("all", "patch"):
        run(f"cp {SERVER} {SERVER}.bak.p3-$(date +%Y%m%d%H%M)")
        patch_server_v2()
    if mode in ("all", "photos"):
        upgrade_photos()
    if mode in ("all", "patch", "photos", "restart", "seed"):
        run("sudo systemctl restart greentrace")
        time.sleep(2)
        run("systemctl is-active greentrace")
    if mode in ("all", "verify", "patch", "photos", "seed"):
        time.sleep(1)
        verify()
    Path("/tmp/greentrace-p3.log").write_text("\n".join(LOG), encoding="utf-8")
    print("\n".join(LOG))


if __name__ == "__main__":
    main()
