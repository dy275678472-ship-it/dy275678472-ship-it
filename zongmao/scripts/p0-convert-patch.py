#!/usr/bin/env python3
"""宗贸网商业化 P0 — 注册转化、百度统计、sparkline、支付绑定"""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path("/opt/zongmao")
APP = BASE / "app.py"
CONFIG = BASE / "site_config.json"
TPL = BASE / "templates"
STATIC = BASE / "static" / "js"
COMMON = STATIC / "common.js"
REGISTER = TPL / "register.html"
SIGNALS = TPL / "signals.html"
PREMIUM = TPL / "premium.html"
TONGJI = TPL / "_tongji.html"
INDEX = TPL / "index.html"


def backup(path: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = path.with_suffix(path.suffix + f".bak_{ts}")
    shutil.copy2(path, dest)
    print(f"  backup: {dest.name}")


def patch_site_config():
    if not CONFIG.exists():
        CONFIG.write_text(
            json.dumps({"baidu_hm_id": ""}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("✅ site_config.json created")
    else:
        print("ℹ️  site_config.json exists")


def patch_app():
    text = APP.read_text(encoding="utf-8")
    changed = False

    # 1. site_config loader + render() inject baidu_hm_id
    if "def load_site_config" not in text:
        loader = '''
_site_config_cache = {"ts": 0, "data": {}}

def load_site_config():
    """Load site_config.json with 60s cache."""
    now = time.time()
    if now - _site_config_cache["ts"] < 60 and _site_config_cache["data"]:
        return _site_config_cache["data"]
    data = {}
    cfg_path = os.path.join(BASE_DIR, "site_config.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    _site_config_cache["ts"] = now
    _site_config_cache["data"] = data
    return data

'''
        text = text.replace("def render(request, name, **kw):", loader + "def render(request, name, **kw):", 1)
        changed = True

    old_render = '''def render(request, name, **kw):
    tmpl = templates.env.get_template(name)
    return HTMLResponse(tmpl.render(request=request, **kw))'''
    new_render = '''def render(request, name, **kw):
    cfg = load_site_config()
    kw.setdefault("baidu_hm_id", cfg.get("baidu_hm_id", ""))
    tmpl = templates.env.get_template(name)
    return HTMLResponse(tmpl.render(request=request, **kw))'''
    if "baidu_hm_id" not in text.split("def render(request")[1][:200]:
        text = text.replace(old_render, new_render, 1)
        changed = True

    # 2. user_id cookie on register
    old_reg_cookie = '    resp.set_cookie("token", token, httponly=True, max_age=86400*30)\n    return resp\n\n@app.post("/api/auth/login")'
    new_reg_cookie = (
        '    resp.set_cookie("token", token, httponly=True, max_age=86400*30, samesite="lax")\n'
        '    resp.set_cookie("user_id", uid, httponly=True, max_age=86400*30, samesite="lax")\n'
        '    return resp\n\n@app.post("/api/auth/login")'
    )
    if 'set_cookie("user_id"' not in text:
        text = text.replace(old_reg_cookie, new_reg_cookie, 1)
        changed = True

    # 3. user_id cookie on login
    old_login = '''    resp = JSONResponse({"status": "ok", "token": token, "name": u["name"] or u["phone"]})
    resp.set_cookie("token", token, httponly=True, max_age=86400*30)
    return resp

@app.post("/api/auth/logout")'''
    new_login = '''    resp = JSONResponse({"status": "ok", "token": token, "name": u["name"] or u["phone"], "user_id": u["id"]})
    resp.set_cookie("token", token, httponly=True, max_age=86400*30, samesite="lax")
    resp.set_cookie("user_id", u["id"], httponly=True, max_age=86400*30, samesite="lax")
    return resp

@app.post("/api/auth/logout")'''
    if text.count('set_cookie("user_id"') < 2:
        text = text.replace(old_login, new_login, 1)
        changed = True

    # 4. clear user_id on logout
    old_logout = '    resp = JSONResponse({"status": "ok"}); resp.delete_cookie("token"); return resp'
    new_logout = '    resp = JSONResponse({"status": "ok"}); resp.delete_cookie("token"); resp.delete_cookie("user_id"); return resp'
    if 'delete_cookie("user_id")' not in text:
        text = text.replace(old_logout, new_logout, 1)
        changed = True

    # 5. sparkline API (homepage uses /api/symbol/{sym}/sparkline)
    sparkline_route = '''
@app.get("/api/symbol/{symbol}/sparkline")
async def api_symbol_sparkline(symbol: str):
    """Mini chart data for homepage sparklines."""
    conn = get_db()
    symbol = symbol.upper()
    quote = conn.execute("SELECT price FROM quotes WHERE symbol=?", (symbol,)).fetchone()
    if not quote:
        conn.close()
        raise HTTPException(404, "品种不存在")
    history = [dict(r) for r in conn.execute(
        "SELECT price, recorded_at FROM quote_history WHERE symbol=? ORDER BY recorded_at ASC LIMIT 30",
        (symbol,)).fetchall()]
    conn.close()
    if history:
        data = [{"price": round(h["price"], 2), "time": h["recorded_at"][:10]} for h in history]
    else:
        sim = _generate_simulated_history(quote["price"])
        data = [{"price": d["price"], "time": d["date"]} for d in sim]
    return {"status": "ok", "data": data}

'''
    if "/sparkline" not in text:
        anchor = '@app.get("/api/symbol/{symbol}/chart")'
        text = text.replace(anchor, sparkline_route + anchor, 1)
        changed = True

    # 6. signals page — pass logged_in flag
    old_signals_page = '''@app.get("/signals")
async def signals_page(request: Request):
    conn = get_db()
    signals = [dict(r) for r in conn.execute(
        "SELECT ts.*, q.name, q.price as current_price, q.category "
        "FROM trade_signals ts LEFT JOIN quotes q ON ts.symbol=q.symbol "
        "ORDER BY ts.created_at DESC LIMIT 100"
    ).fetchall()]
    categories = conn.execute("SELECT DISTINCT category FROM quotes").fetchall()
    conn.close()
    return render(request, "signals.html", signals=signals,
        categories=[r[0] for r in categories])'''
    new_signals_page = '''@app.get("/signals")
async def signals_page(request: Request):
    user = get_user_by_token(get_token(request))
    conn = get_db()
    signals = [dict(r) for r in conn.execute(
        "SELECT ts.*, q.name, q.price as current_price, q.category "
        "FROM trade_signals ts LEFT JOIN quotes q ON ts.symbol=q.symbol "
        "ORDER BY ts.created_at DESC LIMIT 100"
    ).fetchall()]
    categories = conn.execute("SELECT DISTINCT category FROM quotes").fetchall()
    conn.close()
    return render(request, "signals.html", signals=signals,
        categories=[r[0] for r in categories], logged_in=bool(user))'''
    if "logged_in=bool(user)" not in text:
        text = text.replace(old_signals_page, new_signals_page, 1)
        changed = True

    # 7. fix admin monetize auth (was comparing to sha256 instead of admin_ token)
    old_admin = '''    admin_token = request.cookies.get("admin_token", "")
    if admin_token != hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest():
        return {"success": False, "error": "需要管理员权限"}'''
    new_admin = '''    try:
        verify_admin(request)
    except HTTPException:
        return {"success": False, "error": "需要管理员权限"}'''
    if "verify_admin(request)" not in text.split("api_admin_monetize")[1][:400]:
        text = text.replace(old_admin, new_admin, 1)
        changed = True

    # 8. premium page — pass logged_in + user_id for payment binding
    old_premium = '''    kpi = get_performance_kpi()
    return render(request, "premium.html", tiers=tiers, stats=stats, kpi=kpi)'''
    new_premium = '''    kpi = get_performance_kpi()
    user = get_user_by_token(get_token(request))
    return render(request, "premium.html", tiers=tiers, stats=stats, kpi=kpi,
                  logged_in=bool(user), user_id=user["id"] if user else "")'''
    if 'user_id=user["id"]' not in text:
        text = text.replace(old_premium, new_premium, 1)
        changed = True

    if changed:
        backup(APP)
        APP.write_text(text, encoding="utf-8")
        print("✅ app.py patched")
    else:
        print("ℹ️  app.py already patched")


def patch_tongji():
    content = """{# 百度统计 — site_config.json baidu_hm_id，render() 自动注入 #}
{% if baidu_hm_id %}
<script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?{{ baidu_hm_id }}";
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(hm, s);
})();
</script>
{% else %}
<script>console.log("[Zongmao] Set baidu_hm_id in /opt/zongmao/site_config.json");</script>
{% endif %}"""
    TONGJI.write_text(content, encoding="utf-8")
    print("✅ _tongji.html → dynamic baidu_hm_id")


def patch_common_js():
    text = COMMON.read_text(encoding="utf-8")
    changed = False

    old_api = """async function api(url, opts = {}) {
    try {
        const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts });
        return await res.json();
    } catch (e) {
        console.error('API error:', e);
        return { status: 'error', message: e.message };
    }
}"""
    new_api = """async function api(url, opts = {}) {
    try {
        const res = await fetch(url, {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            ...opts
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
            const msg = data.detail || data.message || data.error || ('HTTP ' + res.status);
            return { status: 'error', detail: typeof msg === 'string' ? msg : JSON.stringify(msg) };
        }
        return data;
    } catch (e) {
        console.error('API error:', e);
        return { status: 'error', detail: e.message };
    }
}"""
    if "credentials: 'same-origin'" not in text:
        text = text.replace(old_api, new_api, 1)
        changed = True

    # Replace email lead popup with phone → register CTA
    old_lead = """(function() {
    if (document.cookie.indexOf('lead_shown=1') === -1 && window.location.pathname !== '/premium') {
        setTimeout(function() {
            var overlay = document.createElement('div');
            overlay.id = 'leadOverlay';
            overlay.innerHTML = '<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:9998;display:flex;align-items:center;justify-content:center;">' +
                '<div style="background:white;border-radius:16px;padding:30px;max-width:400px;width:90%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.3);position:relative;">' +
                '<button onclick="this.parentElement.parentElement.remove()" style="position:absolute;top:10px;right:15px;background:none;border:none;font-size:1.5em;cursor:pointer;color:#999;">&times;</button>' +
                '<h3 style="color:#c0392b;margin-bottom:10px;">🎁 免费获取交易信号</h3>' +
                '<p style="color:#666;margin-bottom:20px;">每日精选AI交易信号，直接发送到您的邮箱</p>' +
                '<input id="leadEmailInput" type="email" placeholder="your@email.com" style="width:100%;padding:12px;border:2px solid #ddd;border-radius:8px;font-size:1em;margin-bottom:10px;box-sizing:border-box;">' +
                '<button onclick="submitLeadCapture()" style="background:linear-gradient(135deg,#c0392b,#e74c3c);color:white;border:none;padding:12px 30px;border-radius:25px;font-size:1.1em;cursor:pointer;width:100%;">免费订阅</button>' +
                '<p style="color:#999;font-size:0.8em;margin-top:10px;">🔒 不发送垃圾邮件，随时可退订</p>' +
                '<div id="leadCaptureMsg" style="margin-top:10px;display:none;padding:8px;border-radius:6px;"></div>' +
                '</div></div>';
            document.body.appendChild(overlay);
            document.cookie = 'lead_shown=1;max-age=' + (7*86400) + ';path=/';
        }, 30000);
    }
})();"""

    new_lead = """(function() {
    var skip = ['/register', '/login', '/premium', '/welcome'];
    if (skip.indexOf(window.location.pathname) !== -1) return;
    if (document.cookie.indexOf('lead_shown=1') !== -1) return;
    setTimeout(function() {
        fetch('/api/auth/status', {credentials:'same-origin'}).then(function(r){return r.json();}).then(function(d){
            if (d.logged_in) return;
            var overlay = document.createElement('div');
            overlay.id = 'leadOverlay';
            overlay.innerHTML = '<div style="position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:9998;display:flex;align-items:center;justify-content:center;padding:16px;box-sizing:border-box;">' +
                '<div style="background:#fff;border-radius:16px;padding:28px 24px;max-width:380px;width:100%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.3);position:relative;">' +
                '<button onclick="document.getElementById(\\'leadOverlay\\').remove()" style="position:absolute;top:10px;right:15px;background:none;border:none;font-size:1.5em;cursor:pointer;color:#999;">&times;</button>' +
                '<h3 style="color:#c0392b;margin:0 0 8px;">免费注册 · 查看今日信号</h3>' +
                '<p style="color:#666;font-size:0.9rem;margin:0 0 16px;">30秒注册，自动加入模拟赛并跟单最新AI信号</p>' +
                '<a href="/register" style="display:block;background:linear-gradient(135deg,#c0392b,#e74c3c);color:#fff;text-decoration:none;padding:14px;border-radius:25px;font-size:1.05em;font-weight:600;">立即免费注册</a>' +
                '<p style="color:#999;font-size:0.75rem;margin:12px 0 0;">已有账号？<a href="/login" style="color:#c0392b;">去登录</a></p>' +
                '</div></div>';
            document.body.appendChild(overlay);
            document.cookie = 'lead_shown=1;max-age=' + (3*86400) + ';path=/';
        }).catch(function(){});
    }, 20000);
})();"""

    if "leadEmailInput" in text:
        text = text.replace(old_lead, new_lead, 1)
        changed = True

    if changed:
        backup(COMMON)
        COMMON.write_text(text, encoding="utf-8")
        print("✅ common.js patched")
    else:
        print("ℹ️  common.js already patched")


def patch_register():
    text = REGISTER.read_text(encoding="utf-8")
    if "register-benefits" in text:
        print("ℹ️  register.html already patched")
        return

    text = text.replace(
        '<p style="text-align:center;color:#666;font-size:0.9rem;margin-bottom:1.5rem;">免费查看今日AI信号 · 自动加入模拟赛</p>',
        '''<ul class="register-benefits" style="list-style:none;padding:0;margin:0 0 1.2rem;font-size:0.88rem;color:#555;">
            <li style="padding:0.25rem 0;">✅ 免费查看全部 AI 交易信号</li>
            <li style="padding:0.25rem 0;">✅ 注册即加入模拟交易赛（赠 ¥100万虚拟金）</li>
            <li style="padding:0.25rem 0;">✅ 自动跟单最新信号，无需手动操作</li>
        </ul>''',
        1,
    )

    # Hide name/email — reduce friction (name auto-filled from phone)
    text = re.sub(
        r'        <div class="form-group">\s*<label>姓名</label>.*?        </div>\s*'
        r'        <div class="form-group">\s*<label>邮箱（选填）</label>.*?        </div>\s*',
        "",
        text,
        count=1,
        flags=re.S,
    )

    old_script = """async function doRegister() {
    const phone = document.getElementById('phone').value.trim();
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const errEl = document.getElementById('errorMsg');
    errEl.style.display = 'none';
    if (!phone || !password) { errEl.textContent = '请填写手机号和密码'; errEl.style.display = 'block'; return; }
    if (password.length < 6) { errEl.textContent = '密码至少6位'; errEl.style.display = 'block'; return; }
    const res = await api('/api/auth/register', { method: 'POST', body: JSON.stringify({ phone, name, email, password }) });"""

    new_script = """async function doRegister() {
    const phone = document.getElementById('phone').value.trim();
    const password = document.getElementById('password').value;
    const btn = document.querySelector('button[onclick="doRegister()"]');
    const errEl = document.getElementById('errorMsg');
    errEl.style.display = 'none';
    if (!/^1\\d{10}$/.test(phone)) { errEl.textContent = '请输入11位手机号'; errEl.style.display = 'block'; return; }
    if (password.length < 6) { errEl.textContent = '密码至少6位'; errEl.style.display = 'block'; return; }
    btn.disabled = true; btn.textContent = '注册中...';
    const res = await api('/api/auth/register', { method: 'POST', body: JSON.stringify({ phone, name: '用户' + phone.slice(-4), email: '', password }) });"""

    text = text.replace(old_script, new_script, 1)

    text = text.replace(
        "    else { errEl.textContent = res.detail || '注册失败'; errEl.style.display = 'block'; }",
        "    else { errEl.textContent = res.detail || '注册失败'; errEl.style.display = 'block'; btn.disabled = false; btn.textContent = '注 册'; }",
        1,
    )

    text = text.replace(
        '<input type="password" id="password"',
        '<input type="password" id="password" autocomplete="new-password"',
        1,
    )
    text = text.replace(
        '<input type="tel" id="phone"',
        '<input type="tel" id="phone" inputmode="numeric" autocomplete="tel"',
        1,
    )
    text = text.replace(
        'document.querySelector(\'button\').disabled = true;',
        'btn.disabled = true;',
        1,
    )

    # Enter key submit
    if 'addEventListener' not in text.split('doRegister')[1][:500]:
        text = text.replace(
            "</script>\n{% include \"_tongji.html\" %}",
            "document.getElementById('password').addEventListener('keydown', e => { if (e.key === 'Enter') doRegister(); });\n</script>\n{% include \"_tongji.html\" %}",
            1,
        )

    backup(REGISTER)
    REGISTER.write_text(text, encoding="utf-8")
    print("✅ register.html simplified")


def patch_signals():
    text = SIGNALS.read_text(encoding="utf-8")
    if "signal-lock-overlay" in text:
        print("ℹ️  signals.html already patched")
        return

    guest_banner = """    {% if not logged_in %}
    <div style="background:linear-gradient(135deg,#c0392b15,#e74c3c15);border:1px solid #c0392b40;border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.75rem;">
        <div>
            <strong style="color:#c0392b;">🔓 注册免费查看全部信号</strong>
            <span style="font-size:0.85rem;color:#666;margin-left:0.5rem;">未登录仅预览前3条</span>
        </div>
        <a href="/register" class="btn btn-primary" style="font-size:0.85rem;padding:0.5rem 1.2rem;">30秒免费注册</a>
    </div>
    {% endif %}
"""
    text = text.replace(
        '    <div style="display:flex;gap:0.5rem;margin-bottom:1rem;">',
        guest_banner + '    <div style="display:flex;gap:0.5rem;margin-bottom:1rem;">',
        1,
    )

    # Add lock overlay for signals beyond index 2 when not logged in
    old_card_start = """        <div class="signal-card {{ dir_class }}" data-cat="{{ s.category or '' }}" data-dir="{{ s.direction }}">"""
    new_card_start = """        <div class="signal-card {{ dir_class }}{% if not logged_in and loop.index0 >= 3 %} signal-locked{% endif %}" data-cat="{{ s.category or '' }}" data-dir="{{ s.direction }}" style="position:relative;">"""
    text = text.replace(old_card_start, new_card_start, 1)

    old_rationale = """            <div class="signal-rationale">{{ s.rationale }}</div>
            <div class="signal-footer">"""
    new_rationale = """            {% if not logged_in and loop.index0 >= 3 %}
            <div class="signal-lock-overlay" style="position:absolute;inset:0;background:rgba(255,255,255,0.85);backdrop-filter:blur(4px);display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:8px;z-index:2;">
                <p style="margin:0 0 0.75rem;font-weight:600;color:#333;">🔒 注册后查看完整信号</p>
                <a href="/register" class="btn btn-primary" style="font-size:0.85rem;">免费注册</a>
            </div>
            {% endif %}
            <div class="signal-rationale"{% if not logged_in and loop.index0 >= 3 %} style="filter:blur(5px);user-select:none;"{% endif %}>{{ s.rationale }}</div>
            <div class="signal-footer">"""
    text = text.replace(old_rationale, new_rationale, 1)

    backup(SIGNALS)
    SIGNALS.write_text(text, encoding="utf-8")
    print("✅ signals.html guest gating added")


def patch_premium():
    text = PREMIUM.read_text(encoding="utf-8")
    changed = False

    old_pay = """            // Generate a random user_id for guest checkout
            const userId = 'guest_' + Math.random().toString(36).substring(2, 15);"""
    new_pay = """            const userId = {{ ('"' + user_id + '"') if user_id else 'null' }};
            if (!userId) {
                window.location.href = '/register?next=/premium';
                return;
            }"""
    if "guest_" in text:
        text = text.replace(old_pay, new_pay, 1)
        changed = True

    if changed:
        backup(PREMIUM)
        PREMIUM.write_text(text, encoding="utf-8")
        print("✅ premium.html payment uses user_id cookie")
    else:
        print("ℹ️  premium.html already patched")


def patch_index_cta():
    text = INDEX.read_text(encoding="utf-8")
    if "sticky-register-bar" in text:
        print("ℹ️  index.html CTA already patched")
        return

    sticky = """
<div id="sticky-register-bar" class="sticky-register-bar" style="display:none;position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #eee;padding:0.75rem 1rem;z-index:999;box-shadow:0 -4px 20px rgba(0,0,0,0.08);">
  <div style="max-width:600px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:0.75rem;">
    <span style="font-size:0.85rem;color:#333;">📈 免费注册 · 查看今日AI信号</span>
    <a href="/register" style="background:#c0392b;color:#fff;padding:0.5rem 1rem;border-radius:20px;text-decoration:none;font-size:0.85rem;white-space:nowrap;">立即注册</a>
  </div>
</div>
<script>
(function(){
  if (document.cookie.indexOf('token=') !== -1) return;
  var bar = document.getElementById('sticky-register-bar');
  if (!bar) return;
  var shown = false;
  window.addEventListener('scroll', function() {
    if (!shown && window.scrollY > 400) { bar.style.display = 'block'; shown = true; }
  }, {passive:true});
})();
</script>
"""
    text = text.replace("</body>", sticky + "\n</body>", 1)
    backup(INDEX)
    INDEX.write_text(text, encoding="utf-8")
    print("✅ index.html sticky register bar")


def main():
    print("=== 宗贸网商业化 P0 补丁 ===")
    patch_site_config()
    patch_app()
    patch_tongji()
    patch_common_js()
    patch_register()
    patch_signals()
    patch_premium()
    patch_index_cta()
    print("=== 完成 — 请重启 zongmao.service ===")
    print("提示: 在 site_config.json 填入 baidu_hm_id 后无需重启即可生效（60s缓存）")


if __name__ == "__main__":
    main()
