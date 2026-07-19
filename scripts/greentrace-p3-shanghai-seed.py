#!/usr/bin/env python3
"""Seed Shanghai approved routes so /city/上海 renders full P3 page."""
import json
import sqlite3
import uuid
from datetime import datetime

db = sqlite3.connect("/opt/greentrace/greentrace.db")
db.row_factory = sqlite3.Row

# Find a Shanghai guide (or any approved guide)
g = db.execute(
    "select id, nickname, city, cities, status from guides "
    "where (city='上海' or cities like '%上海%') and status='已通过' limit 3"
).fetchall()
print("shanghai guides", [dict(x) for x in g])
if not g:
    g = db.execute(
        "select id, nickname, city, status from guides where status='已通过' limit 1"
    ).fetchall()
    print("fallback guide", [dict(x) for x in g])

guide_id = g[0]["id"] if g else None
existing = db.execute("select count(*) c from hidden_routes where city='上海'").fetchone()["c"]
print("existing shanghai routes", existing)

if existing == 0 and guide_id:
    routes = [
        {
            "title": "法租界梧桐 Citywalk",
            "description": "从交通大学出发，沿武康路、安福路、永福路步行，穿过法租界梧桐与老洋房。避开外滩人潮，用脚步感受上海的日常优雅。",
            "duration": "半天",
            "highlights": "Citywalk,建筑,咖啡",
            "difficulty": "轻松",
            "best_season": "3-11月",
            "itinerary": [
                {"time": "09:30", "title": "武康路起点", "desc": "地铁交通大学站集合，咖啡热身"},
                {"time": "11:00", "title": "安福路 → 永福路", "desc": "梧桐与老洋房，支巷更安静"},
                {"time": "13:00", "title": "小馆午餐", "desc": "支巷本帮/点心，避开网红排队"},
                {"time": "15:00", "title": "张园 / 陕西南路", "desc": "室内综合体可躲雨，收尾散走"},
            ],
            "tips": ["穿舒适步行鞋", "周末安福路人流翻倍，建议工作日", "共享单车注意非机动车道"],
            "transport": "地铁 10/11/1 号线",
            "price_range": "¥99-299",
        },
        {
            "title": "徐汇滨江慢骑",
            "description": "从龙华附近骑入徐汇滨江绿道，江风与工业遗存并存。适合黄昏，比外滩骑行更疏朗。",
            "duration": "半天",
            "highlights": "骑行,江景,低碳",
            "difficulty": "轻松",
            "best_season": "四季",
            "itinerary": [
                {"time": "16:00", "title": "取共享单车", "desc": "龙华路附近取车"},
                {"time": "16:30", "title": "滨江绿道南段", "desc": "慢骑观江，停靠工业风雕塑"},
                {"time": "18:00", "title": "西岸艺术区歇脚", "desc": "可选美术馆或江边简餐"},
            ],
            "tips": ["戴头盔更安全", "逆风时缩短行程", "夜骑注意照明"],
            "transport": "共享单车 + 地铁 7/11 号线",
            "price_range": "¥0-99",
        },
        {
            "title": "文庙旧书 · 老城厢半日",
            "description": "周日文庙旧书市场与老城厢街巷，适合喜欢翻书与市井气的旅行者。非周日可改豫园外围支巷。",
            "duration": "半天",
            "highlights": "市井,旧物,步行",
            "difficulty": "轻松",
            "best_season": "春秋",
            "itinerary": [
                {"time": "10:00", "title": "文庙旧书（周日）", "desc": "翻书淘旧，不必成交"},
                {"time": "12:00", "title": "老城厢支巷午餐", "desc": "避开豫园正门人流"},
                {"time": "14:00", "title": "小东门一带散步", "desc": "感受老上海街廓"},
            ],
            "tips": ["周日早到人少", "带现金更方便", "注意保管随身物品"],
            "transport": "地铁 9/10 号线",
            "price_range": "¥0-99",
        },
        {
            "title": "71 路看梧桐 · 公交探索",
            "description": "坐 71 路中运量公交沿延安路看梧桐树影，再换短驳到安福路。用公交窗框理解上海尺度。",
            "duration": "半天",
            "highlights": "公交,城市观察,低碳",
            "difficulty": "轻松",
            "best_season": "四季",
            "itinerary": [
                {"time": "10:00", "title": "上 71 路", "desc": "选靠窗座位"},
                {"time": "11:00", "title": "延安路梧桐段", "desc": "观察街道节奏"},
                {"time": "12:30", "title": "安福路下车漫步", "desc": "短驳+步行收尾"},
            ],
            "tips": ["避开早晚高峰", "准备交通卡或手机支付", "雨天窗景也美"],
            "transport": "71 路 + 地铁",
            "price_range": "¥0-50",
        },
    ]
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    for r in routes:
        rid = uuid.uuid4().hex[:20]
        db.execute(
            "insert into hidden_routes (id, guide_id, city, title, description, duration, highlights, "
            "photos, status, votes, created_at, difficulty, best_season, itinerary, tips, transport, price_range) "
            "values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                rid,
                guide_id,
                "上海",
                r["title"],
                r["description"],
                r["duration"],
                r["highlights"],
                "[]",
                "approved",
                120,
                now,
                r["difficulty"],
                r["best_season"],
                json.dumps(r["itinerary"], ensure_ascii=False),
                json.dumps(r["tips"], ensure_ascii=False),
                r["transport"],
                r["price_range"],
            ),
        )
        print("inserted", rid, r["title"])
    db.commit()
    print("seeded", len(routes), "shanghai routes")
else:
    print("skip seed")

# verify
print("count now", db.execute("select count(*) c from hidden_routes where city='上海' and status='approved'").fetchone()["c"])
db.close()
