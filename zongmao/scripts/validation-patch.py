#!/usr/bin/env python3
"""宗贸网产品验证补丁 — 轻量埋点 + 验证报告 cron"""
from __future__ import annotations

import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BASE = Path("/opt/zongmao")
APP = BASE / "app.py"
COMMON = BASE / "static" / "js" / "common.js"
REPORT = BASE / "scripts" / "product-validation-report.py"
CRON = Path("/etc/cron.d/zongmao-validation")


def backup(path: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = path.with_suffix(path.suffix + f".bak_{ts}")
    shutil.copy2(path, dest)
    print(f"  backup: {dest.name}")


def patch_app():
    text = APP.read_text(encoding="utf-8")
    changed = False

    # product_events table in init_db
    if "product_events" not in text:
        old = '        CREATE TABLE IF NOT EXISTS lead_captures ('
        new = '''        CREATE TABLE IF NOT EXISTS product_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            page TEXT DEFAULT '',
            meta TEXT DEFAULT '',
            ip TEXT DEFAULT '',
            created_at TEXT DEFAULT(datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS lead_captures ('''
        if old in text:
            text = text.replace(old, new, 1)
            changed = True
        else:
            # fallback: ensure table exists at runtime
            ensure = '''
def ensure_product_events():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS product_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, page TEXT DEFAULT '',
        meta TEXT DEFAULT '', ip TEXT DEFAULT '',
        created_at TEXT DEFAULT(datetime('now','localtime')))""")
    conn.commit()
    conn.close()

'''
            text = text.replace("def get_db():", ensure + "def get_db():", 1)
            changed = True

    # validation event endpoint
    if "/api/validation/event" not in text:
        route = '''
@app.post("/api/validation/event")
async def api_validation_event(request: Request):
    """产品验证轻量埋点（无登录）"""
    try:
        body = await request.json()
    except Exception:
        body = {}
    event = str(body.get("event", ""))[:64]
    if not event:
        return JSONResponse({"status": "ok"})
    page = str(body.get("page", ""))[:200]
    meta = str(body.get("meta", ""))[:200]
    ip = request.client.host if request.client else ""
    conn = get_db()
    conn.execute(
        "INSERT INTO product_events(event,page,meta,ip) VALUES(?,?,?,?)",
        (event, page, meta, ip),
    )
    conn.commit()
    conn.close()
    return JSONResponse({"status": "ok"})

'''
        anchor = "# ─── 数据 API ───"
        text = text.replace(anchor, route + anchor, 1)
        changed = True

    # admin validation report endpoint
    if "/api/admin/validation" not in text:
        admin_route = '''
@app.get("/api/admin/validation")
async def api_admin_validation(request: Request):
    verify_admin(request)
    report_path = "/var/log/zongmao/validation-latest.txt"
    if os.path.exists(report_path):
        with open(report_path, encoding="utf-8") as f:
            content = f.read()
    else:
        content = "报告尚未生成，请运行 product-validation-report.py"
    return JSONResponse({"status": "ok", "report": content})

'''
        anchor = "# ─── 管理 API ───"
        text = text.replace(anchor, admin_route + anchor, 1)
        changed = True

    if changed:
        backup(APP)
        APP.write_text(text, encoding="utf-8")
        print("✅ app.py validation endpoints")
    else:
        print("ℹ️  app.py already has validation endpoints")

    # ensure table on existing DB
    import sqlite3
    conn = sqlite3.connect("/opt/zongmao/zongmao.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS product_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, page TEXT DEFAULT '',
        meta TEXT DEFAULT '', ip TEXT DEFAULT '',
        created_at TEXT DEFAULT(datetime('now','localtime')))""")
    conn.commit()
    conn.close()
    print("✅ product_events table ready")


def patch_common_js():
    text = COMMON.read_text(encoding="utf-8")
    if "function trackValidation" in text:
        print("ℹ️  common.js already has trackValidation")
        return

    tracker = '''
// 产品验证埋点（轻量，sendBeacon）
function trackValidation(event, meta) {
    try {
        var payload = JSON.stringify({event: event, page: location.pathname, meta: meta || ''});
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/api/validation/event', new Blob([payload], {type: 'application/json'}));
        } else {
            fetch('/api/validation/event', {method:'POST', headers:{'Content-Type':'application/json'}, body: payload, keepalive:true});
        }
    } catch(e) {}
}

'''
    text = tracker + text

    # Track register page view
    if "trackValidation('register_view')" not in text:
        text = text.replace(
            "// ===== 获客弹窗",
            "if (location.pathname === '/register') trackValidation('register_view');\n\n// ===== 获客弹窗",
            1,
        )

    backup(COMMON)
    COMMON.write_text(text, encoding="utf-8")
    print("✅ common.js trackValidation added")


def patch_register_js():
    reg = BASE / "templates" / "register.html"
    text = reg.read_text(encoding="utf-8")
    if "trackValidation('register_submit')" in text:
        print("ℹ️  register.html already tracks submit")
        return
    text = text.replace(
        "btn.disabled = true; btn.textContent = '注册中...';",
        "trackValidation('register_submit');\n    btn.disabled = true; btn.textContent = '注册中...';",
        1,
    )
    if "trackValidation('register_success')" not in text:
        text = text.replace(
            "if (res.status === 'ok') {",
            "if (res.status === 'ok') {\n        trackValidation('register_success');",
            1,
        )
    backup(reg)
    reg.write_text(text, encoding="utf-8")
    print("✅ register.html submit tracking")


def patch_index_sticky():
    idx = BASE / "templates" / "index.html"
    text = idx.read_text(encoding="utf-8")
    if "trackValidation('cta_sticky'" in text:
        print("ℹ️  index sticky tracking done")
        return
    text = text.replace(
        'href="/register" style="background:#c0392b',
        'href="/register" onclick="trackValidation(\'cta_sticky\')" style="background:#c0392b',
        1,
    )
    backup(idx)
    idx.write_text(text, encoding="utf-8")
    print("✅ index.html sticky CTA tracking")


def patch_signals_gate():
    sig = BASE / "templates" / "signals.html"
    text = sig.read_text(encoding="utf-8")
    if "trackValidation('cta_signals_banner'" in text:
        print("ℹ️  signals tracking done")
        return
    text = text.replace(
        'href="/register" class="btn btn-primary" style="font-size:0.85rem;padding:0.5rem 1.2rem;">30秒免费注册</a>',
        'href="/register" onclick="trackValidation(\'cta_signals_banner\')" class="btn btn-primary" style="font-size:0.85rem;padding:0.5rem 1.2rem;">30秒免费注册</a>',
        1,
    )
    text = text.replace(
        '<a href="/register" class="btn btn-primary" style="font-size:0.85rem;">免费注册</a>',
        '<a href="/register" onclick="trackValidation(\'cta_signals_gate\')" class="btn btn-primary" style="font-size:0.85rem;">免费注册</a>',
        1,
    )
    backup(sig)
    sig.write_text(text, encoding="utf-8")
    print("✅ signals.html CTA tracking")


def setup_cron():
    cron_line = "0 8 * * * root python3 /opt/zongmao/scripts/product-validation-report.py >> /var/log/zongmao/validation.log 2>&1\n"
    CRON.write_text(
        "# 宗贸网产品验证日报\nSHELL=/bin/bash\nPATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n"
        + cron_line
    )
    print(f"✅ cron installed: {CRON}")


def main():
    print("=== 宗贸网产品验证补丁 ===")
    patch_app()
    patch_common_js()
    patch_register_js()
    patch_index_sticky()
    patch_signals_gate()
    setup_cron()
    if REPORT.exists():
        subprocess.run(["python3", str(REPORT)], check=False)
    print("=== 完成 — 请重启 zongmao.service ===")


if __name__ == "__main__":
    main()
