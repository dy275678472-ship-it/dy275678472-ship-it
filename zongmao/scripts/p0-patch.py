#!/usr/bin/env python3
"""宗贸网 P0 增长修复补丁 — 在服务器 /opt/zongmao 上运行"""
from __future__ import annotations

import re
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path("/opt/zongmao")
APP = BASE / "app.py"
INDEX = BASE / "templates" / "index.html"
GEN = BASE / "gen_signals.py"
NGINX = Path("/etc/nginx/sites-available/zongmao")


def backup(path: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = path.with_suffix(path.suffix + f".bak_{ts}")
    shutil.copy2(path, dest)
    print(f"  backup: {dest.name}")


def patch_app():
    text = APP.read_text(encoding="utf-8")
    changed = False

    # 1. Helper: get_performance_kpi
    helper = '''
def get_performance_kpi():
    """KPI stats for SSR (homepage/performance)."""
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM trade_signals").fetchone()[0]
    closed = conn.execute("SELECT COUNT(*) FROM trade_signals WHERE status='closed'").fetchone()[0]
    wins = conn.execute("SELECT COUNT(*) FROM trade_signals WHERE status='closed' AND result_pct > 0").fetchone()[0]
    total_pnl = conn.execute("SELECT COALESCE(SUM(result_pct),0) FROM trade_signals WHERE status='closed'").fetchone()[0]
    avg_win = conn.execute("SELECT COALESCE(AVG(result_pct),0) FROM trade_signals WHERE status='closed' AND result_pct > 0").fetchone()[0]
    avg_loss = conn.execute("SELECT COALESCE(AVG(result_pct),0) FROM trade_signals WHERE status='closed' AND result_pct < 0").fetchone()[0]
    win_rate = round(wins / closed * 100, 1) if closed else 0
    profit_loss_ratio = round(avg_win / abs(avg_loss), 2) if avg_loss != 0 else 0
    conn.close()
    return {
        "total": total, "closed": closed, "wins": wins,
        "win_rate": win_rate, "total_pnl": round(total_pnl, 2),
        "profit_loss_ratio": profit_loss_ratio,
    }


def sanitize_signal_rationale(symbol: str, name: str, category: str, rationale: str) -> str:
    """Fix common AI rationale errors (e.g. OPEC+ on coal)."""
    r = rationale
    coal_syms = {"ZC", "JM", "J", "I", "RB", "HC", "SF", "SM"}
    if symbol in coal_syms or name in ("动力煤", "焦煤", "焦炭", "铁矿石", "螺纹钢", "热卷"):
        r = r.replace("OPEC+动态和地缘风险", "电厂库存和钢厂利润")
        r = r.replace("OPEC+减产", "供需格局")
    if symbol in ("CU", "AL", "ZN", "NI", "SN", "AO") or category == "有色":
        r = r.replace("OPEC+动态和地缘风险", "LME库存和美元走势")
    if category == "农产品":
        r = r.replace("OPEC+动态和地缘风险", "天气和USDA报告")
    return r

'''
    if "def get_performance_kpi" not in text:
        text = text.replace("# ─── 信号战绩看板 ───", helper + "# ─── 信号战绩看板 ───", 1)
        changed = True

    # 2. page_index pass kpi
    old_return = (
        '    return render(request, "index.html", quotes=quotes, headlines=headlines, '
        'categories=CATEGORIES, cat_icons=CAT_ICONS, cat_index=cat_index, gainers=gainers, '
        'losers=losers, latest_signals=latest_signals)'
    )
    new_return = (
        '    kpi = get_performance_kpi()\n'
        '    return render(request, "index.html", quotes=quotes, headlines=headlines, '
        'categories=CATEGORIES, cat_icons=CAT_ICONS, cat_index=cat_index, gainers=gainers, '
        'losers=losers, latest_signals=latest_signals, kpi=kpi)'
    )
    if "kpi=kpi)" not in text:
        text = text.replace(old_return, new_return, 1)
        changed = True

    # 3. Sitemap: use quotes not card_assets for signal pages
    old_signal = """    # 信号方向SEO页
    signal_pages = []
    for direction in ('bullish', 'bearish', 'neutral'):
        for r in asset_rows:
            signal_pages.append(
                (f'https://zongmao.cn/signal/{direction}/{r["asset_name"]}', now, '0.6', 'weekly')
            )"""
    new_signal = """    # 信号方向SEO页（仅34个标准品种，避免低质URL）
    signal_pages = []
    for direction in ('bullish', 'bearish', 'neutral'):
        for r in quote_rows:
            signal_pages.append(
                (f'https://zongmao.cn/signal/{direction}/{r["symbol"]}', now, '0.7', 'weekly')
            )"""
    if 'signal/{direction}/{r["asset_name"]}' in text:
        text = text.replace(old_signal, new_signal, 1)
        changed = True

    # 4. Add premium to static pages in sitemap
    if "zongmao.cn/premium" not in text:
        text = text.replace(
            "('https://zongmao.cn/privacy', now, '0.5', 'monthly'),",
            "('https://zongmao.cn/privacy', now, '0.5', 'monthly'),\n"
            "        ('https://zongmao.cn/premium', now, '0.8', 'weekly'),",
            1,
        )
        changed = True

    # 5. /pricing redirect
    if '@app.get("/pricing")' not in text:
        anchor = '@app.get("/premium")'
        redirect = '''
@app.get("/pricing")
async def page_pricing_redirect():
    return RedirectResponse(url="/premium", status_code=301)

'''
        text = text.replace(anchor, redirect + anchor, 1)
        changed = True

    # 6. HEAD middleware
    if "HeadMethodMiddleware" not in text:
        mw = '''
from starlette.middleware.base import BaseHTTPMiddleware

class HeadMethodMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method == "HEAD":
            request.scope["method"] = "GET"
            response = await call_next(request)
            return Response(status_code=response.status_code, headers=dict(response.headers))
        return await call_next(request)

'''
        text = text.replace('app = FastAPI(title="宗贸网"', mw + 'app = FastAPI(title="宗贸网"', 1)
        if "app.add_middleware(HeadMethodMiddleware)" not in text:
            text = text.replace(
                'app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")',
                'app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")\n'
                'app.add_middleware(HeadMethodMiddleware)',
                1,
            )
        changed = True

    # 7. Signal dedup + rationale sanitize on create
    old_insert = """    conn = get_db()
    conn.execute("INSERT INTO trade_signals (user_id,username,symbol,direction,entry_price,target_price,stop_loss,rationale) VALUES (?,?,?,?,?,?,?,?)",
        (user_id, username, symbol, direction, entry_price, target_price, stop_loss, rationale))
    conn.commit()
    conn.close()
    return JSONResponse({"status": "ok", "message": "信号发布成功"})"""
    new_insert = """    conn = get_db()
    # 同日同品种同方向去重
    dup = conn.execute(
        "SELECT id FROM trade_signals WHERE symbol=? AND direction=? AND status='active' "
        "AND date(created_at)=date('now','localtime') LIMIT 1",
        (symbol, direction),
    ).fetchone()
    if dup:
        conn.close()
        return JSONResponse({"status": "ok", "message": "今日该品种信号已存在"})
    q = conn.execute("SELECT name, category FROM quotes WHERE symbol=?", (symbol,)).fetchone()
    if q:
        rationale = sanitize_signal_rationale(symbol, q["name"], q["category"], rationale)
    conn.execute("INSERT INTO trade_signals (user_id,username,symbol,direction,entry_price,target_price,stop_loss,rationale) VALUES (?,?,?,?,?,?,?,?)",
        (user_id, username, symbol, direction, entry_price, target_price, stop_loss, rationale))
    conn.commit()
    conn.close()
    return JSONResponse({"status": "ok", "message": "信号发布成功"})"""
    if "同日同品种同方向去重" not in text:
        text = text.replace(old_insert, new_insert, 1)
        changed = True

    # 8. Use helper in api_performance_stats
    if "kpi_raw = get_performance_kpi()" not in text.split("api_performance_stats")[1][:800]:
        old_kpi = """    conn = get_db()
    # KPI 指标
    total = conn.execute("SELECT COUNT(*) FROM trade_signals").fetchone()[0]
    closed = conn.execute("SELECT COUNT(*) FROM trade_signals WHERE status='closed'").fetchone()[0]
    wins = conn.execute("SELECT COUNT(*) FROM trade_signals WHERE status='closed' AND result_pct > 0").fetchone()[0]
    losses = conn.execute("SELECT COUNT(*) FROM trade_signals WHERE status='closed' AND result_pct < 0").fetchone()[0]
    total_pnl = conn.execute("SELECT COALESCE(SUM(result_pct),0) FROM trade_signals WHERE status='closed'").fetchone()[0]
    avg_win = conn.execute("SELECT COALESCE(AVG(result_pct),0) FROM trade_signals WHERE status='closed' AND result_pct > 0").fetchone()[0]
    avg_loss = conn.execute("SELECT COALESCE(AVG(result_pct),0) FROM trade_signals WHERE status='closed' AND result_pct < 0").fetchone()[0]

    win_rate = round(wins / closed * 100, 1) if closed else 0
    profit_loss_ratio = round(avg_win / abs(avg_loss), 2) if avg_loss != 0 else 0"""
        new_kpi = """    kpi_raw = get_performance_kpi()
    losses = kpi_raw["closed"] - kpi_raw["wins"]
    conn = get_db()"""
        if old_kpi in text:
            text = text.replace(old_kpi, new_kpi, 1)
            changed = True

    old_return_kpi = '''            "total": total, "closed": closed,
            "win_rate": win_rate, "total_pnl": round(total_pnl, 2),
            "avg_win": round(avg_win, 2), "avg_loss": round(avg_loss, 2),
            "profit_loss_ratio": profit_loss_ratio,
            "wins": wins, "losses": losses'''
    new_return_kpi = '''            "total": kpi_raw["total"], "closed": kpi_raw["closed"],
            "win_rate": kpi_raw["win_rate"], "total_pnl": kpi_raw["total_pnl"],
            "avg_win": 0, "avg_loss": 0,
            "profit_loss_ratio": kpi_raw["profit_loss_ratio"],
            "wins": kpi_raw["wins"], "losses": losses'''
    if old_return_kpi in text:
        text = text.replace(old_return_kpi, new_return_kpi, 1)
        changed = True

    if changed:
        backup(APP)
        APP.write_text(text, encoding="utf-8")
        print("✅ app.py patched")
    else:
        print("ℹ️  app.py already patched")


def patch_index():
    text = INDEX.read_text(encoding="utf-8")
    changed = False

    if "历史胜率40%" in text:
        text = text.replace(
            "<span>历史胜率40%</span>",
            "<span>历史战绩公开可查</span>",
        )
        changed = True

    # SSR KPI values
    old_kpi = """            <div class="kpi-value" id="kpi-total">-</div>
            <div class="kpi-label">累计信号</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-value" id="kpi-winrate">-</div>
            <div class="kpi-label">胜率</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">📈</div>
            <div class="kpi-value" id="kpi-plratio">-</div>
            <div class="kpi-label">盈亏比</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🏆</div>
            <div class="kpi-value" id="kpi-pnl">-</div>"""

    new_kpi = """            <div class="kpi-value" id="kpi-total">{{ kpi.total }}条</div>
            <div class="kpi-label">累计信号</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-value" id="kpi-winrate">{% if kpi.closed %}{{ kpi.win_rate }}%{% else %}数据积累中{% endif %}</div>
            <div class="kpi-label">胜率</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">📈</div>
            <div class="kpi-value" id="kpi-plratio">{% if kpi.profit_loss_ratio %}{{ kpi.profit_loss_ratio }}{% else %}—{% endif %}</div>
            <div class="kpi-label">盈亏比</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🏆</div>
            <div class="kpi-value {% if kpi.total_pnl > 0 %}positive{% elif kpi.total_pnl < 0 %}negative{% endif %}" id="kpi-pnl">{% if kpi.closed %}{{ '%+.1f'|format(kpi.total_pnl) }}%{% else %}数据积累中{% endif %}</div>"""

    if 'id="kpi-total">-' in text:
        text = text.replace(old_kpi, new_kpi, 1)
        changed = True

    if changed:
        backup(INDEX)
        INDEX.write_text(text, encoding="utf-8")
        print("✅ index.html patched")
    else:
        print("ℹ️  index.html already patched")


def patch_gen_signals():
    text = GEN.read_text(encoding="utf-8")
    if "COMMODITY_LOGIC" in text:
        print("ℹ️  gen_signals.py already patched")
        return

    old_block = """        if cat == "能源":
            logic_parts.append("关注OPEC+动态和地缘风险")
        elif cat == "有色":
            logic_parts.append("关注LME库存和美元走势")
        elif cat == "黑色":
            logic_parts.append("关注钢厂利润和房地产政策")
        elif cat == "化工":
            logic_parts.append("关注原油成本和下游开工率")
        elif cat == "农产品":
            logic_parts.append("关注天气和USDA报告")"""

    new_block = """        # 品种级逻辑（避免动力煤写OPEC+）
        COMMODITY_LOGIC = {
            "ZC": "关注电厂库存和港口煤价", "JM": "关注钢厂补库和焦化利润",
            "J": "关注焦化利润和环保限产", "SC": "关注OPEC+动态和地缘风险",
            "FU": "关注原油走势和炼厂开工", "BU": "关注基建需求和炼厂利润",
            "LNG": "关注进口成本和采暖需求",
        }
        CAT_LOGIC = {
            "能源": "关注供需格局和库存变化",
            "有色": "关注LME库存和美元走势",
            "黑色": "关注钢厂利润和房地产政策",
            "化工": "关注原油成本和下游开工率",
            "农产品": "关注天气和USDA报告",
        }
        logic_parts.append(COMMODITY_LOGIC.get(sym, CAT_LOGIC.get(cat, "关注基本面变化")))"""

    backup(GEN)
    text = text.replace(old_block, new_block, 1)
    GEN.write_text(text, encoding="utf-8")
    print("✅ gen_signals.py patched")


def patch_nginx():
    if not NGINX.exists():
        print("⚠️  nginx config not found")
        return
    text = NGINX.read_text(encoding="utf-8")
    rules = [
        '    location = /pricing { return 301 /premium; }',
    ]
    changed = False
    for rule in rules:
        if "/pricing" not in text:
            text = text.replace("    location / {\n", f"    {rule}\n    location / {{\n", 1)
            changed = True
    if changed:
        backup(NGINX)
        NGINX.write_text(text, encoding="utf-8")
        print("✅ nginx patched")
    else:
        print("ℹ️  nginx already patched")


def fix_existing_rationales():
    import sqlite3
    db = BASE / "zongmao.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT ts.id, ts.symbol, ts.rationale, q.name, q.category "
        "FROM trade_signals ts LEFT JOIN quotes q ON ts.symbol=q.symbol "
        "WHERE ts.status='active'"
    ).fetchall()
    n = 0
    for r in rows:
        old = r["rationale"] or ""
        new = old.replace("OPEC+动态和地缘风险", "电厂库存和供需格局")
        if r["symbol"] in ("SC", "FU", "BU"):
            pass  # keep OPEC for oil products
        elif r["category"] == "能源" and r["symbol"] not in ("SC", "FU", "BU", "LNG"):
            new = old.replace("OPEC+动态和地缘风险", "电厂库存和港口煤价")
        if new != old:
            conn.execute("UPDATE trade_signals SET rationale=? WHERE id=?", (new, r["id"]))
            n += 1
    conn.commit()
    conn.close()
    print(f"✅ fixed {n} active signal rationales")


def main():
    print("🚀 Zongmao P0 patch")
    patch_app()
    patch_index()
    patch_gen_signals()
    patch_nginx()
    fix_existing_rationales()
    print("✅ P0 patch complete — restart zongmao.service and reload nginx")


if __name__ == "__main__":
    main()
