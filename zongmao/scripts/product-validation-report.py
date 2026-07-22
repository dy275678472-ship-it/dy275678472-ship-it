#!/usr/bin/env python3
"""宗贸网产品验证周报 — 从 nginx 日志 + SQLite 生成验证指标"""
from __future__ import annotations

import gzip
import json
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

DB = Path("/opt/zongmao/zongmao.db")
NGINX_DIR = Path("/var/log/nginx")
OUT = Path("/var/log/zongmao/validation-latest.txt")
DAYS = 7

def is_zongmao_request(line: str, path: str) -> bool:
    """Only count zongmao.cn traffic (shared nginx access.log)."""
    if "zongmao.cn" in line:
        return True
    # Direct hits without referer (homepage, bots)
    zm_paths = (
        "/signals", "/register", "/login", "/market", "/news", "/cards",
        "/price/", "/performance", "/premium", "/welcome", "/tutorial",
        "/compare", "/glossary", "/stats/", "/trading-contest", "/daily-brief",
        "/correlation", "/backtest", "/data", "/about", "/methodology",
        "/llms.txt", "/signal/", "/category/", "/api/auth/", "/api/signals",
        "/api/validation/", "/api/performance/", "/api/symbol/",
    )
    if path == "/" and "zongmao" in line.lower():
        return True
    return any(path == p or path.startswith(p) for p in zm_paths)


BOT_RE = re.compile(
    r"bot|spider|crawl|slurp|baiduspider|googlebot|bingbot|yandex|sogou|360spider|bytespider|headless",
    re.I,
)
LOG_LINE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+)'
)


def parse_log_date(ts: str) -> datetime | None:
    try:
        return datetime.strptime(ts.split()[0], "%d/%b/%Y:%H:%M:%S")
    except ValueError:
        return None


def iter_nginx_lines(days: int):
    files = [NGINX_DIR / "access.log"]
    for i in range(1, days + 3):
        p = NGINX_DIR / f"access.log.{i}"
        gz = NGINX_DIR / f"access.log.{i}.gz"
        if p.exists():
            files.append(p)
        elif gz.exists():
            files.append(gz)

    for fp in files:
        try:
            if str(fp).endswith(".gz"):
                with gzip.open(fp, "rt", errors="ignore") as f:
                    for line in f:
                        yield line
            else:
                with open(fp, errors="ignore") as f:
                    for line in f:
                        yield line
        except OSError:
            continue


def analyze_traffic(days: int = DAYS):
    since = datetime.now() - timedelta(days=days)
    daily_ips: dict[str, set] = defaultdict(set)
    daily_paths: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    funnel = {
        "home": set(),
        "signals": set(),
        "register_page": set(),
        "register_api": set(),
        "welcome": set(),
        "contest": set(),
    }
    entry_pages: dict[str, int] = defaultdict(int)
    cta_events: dict[str, int] = defaultdict(int)

    for line in iter_nginx_lines(days):
        m = LOG_LINE.match(line)
        if not m:
            continue
        ip, ts, method, path = m["ip"], m["ts"], m["method"], m["path"]
        clean = path.split("?")[0]
        if not is_zongmao_request(line, clean):
            continue

        ua = line.split('"')[-1] if '"' in line else ""
        if BOT_RE.search(ua) or BOT_RE.search(ip):
            continue

        dt = parse_log_date(ts)
        if not dt or dt < since:
            continue

        day = dt.strftime("%Y-%m-%d")
        daily_ips[day].add(ip)
        daily_paths[day][clean] += 1

        if clean == "/":
            funnel["home"].add(ip)
        elif clean in ("/signals",):
            funnel["signals"].add(ip)
        elif clean == "/register":
            funnel["register_page"].add(ip)
        elif clean == "/welcome":
            funnel["welcome"].add(ip)
        elif clean == "/trading-contest":
            funnel["contest"].add(ip)
        if method == "POST" and clean == "/api/auth/register":
            funnel["register_api"].add(ip)
        if method == "POST" and clean == "/api/validation/event":
            cta_events["beacon_total"] += 1

    return {
        "daily_uv": {d: len(v) for d, v in sorted(daily_ips.items())},
        "funnel": {k: len(v) for k, v in funnel.items()},
        "daily_paths": dict(daily_paths),
        "cta_events": dict(cta_events),
    }


def db_metrics():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    def q(sql, params=()):
        return c.execute(sql, params).fetchall()

    real_filter = (
        "phone NOT LIKE '139000000%' "
        "AND phone NOT LIKE '138001380%' "
        "AND phone NOT LIKE '138000000%'"
    )

    total_users = q(f"SELECT COUNT(*) n FROM users WHERE {real_filter}")[0]["n"]
    new_7d = q(
        f"SELECT COUNT(*) n FROM users WHERE {real_filter} "
        "AND date(created_at) >= date('now','-7 days','localtime')"
    )[0]["n"]
    new_1d = q(
        f"SELECT COUNT(*) n FROM users WHERE {real_filter} "
        "AND date(created_at) = date('now','localtime')"
    )[0]["n"]

    regs_by_day = q(
        f"SELECT date(created_at) d, COUNT(*) n FROM users "
        f"WHERE {real_filter} GROUP BY d ORDER BY d DESC LIMIT 14"
    )

    contest_users = q(
        f"SELECT COUNT(DISTINCT cp.user_id) n FROM contest_participants cp "
        f"JOIN users u ON cp.user_id=u.id WHERE {real_filter}"
    )[0]["n"]

    leads = q("SELECT COUNT(*) n FROM lead_captures")[0]["n"]
    leads_7d = q(
        "SELECT COUNT(*) n FROM lead_captures "
        "WHERE date(created_at) >= date('now','-7 days','localtime')"
    )[0]["n"]

    closed = q("SELECT COUNT(*) n FROM trade_signals WHERE status='closed'")[0]["n"]
    wins = q(
        "SELECT COUNT(*) n FROM trade_signals WHERE status='closed' AND result_pct > 0"
    )[0]["n"]
    win_rate = round(wins / closed * 100, 1) if closed else 0

    revenue = q(
        "SELECT COALESCE(SUM(amount_yuan),0) n FROM revenue_log WHERE status='completed'"
    )[0]["n"]

    cta_rows = []
    if c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='product_events'"
    ).fetchone():
        cta_rows = q(
            "SELECT event, COUNT(*) n FROM product_events "
            "WHERE date(created_at) >= date('now','-7 days','localtime') "
            "GROUP BY event ORDER BY n DESC"
        )

    conn.close()
    return {
        "total_real_users": total_users,
        "new_users_7d": new_7d,
        "new_users_1d": new_1d,
        "regs_by_day": [(r["d"], r["n"]) for r in regs_by_day],
        "contest_users": contest_users,
        "leads_total": leads,
        "leads_7d": leads_7d,
        "signals_closed": closed,
        "win_rate": win_rate,
        "revenue": revenue,
        "cta_events_db": [(r["event"], r["n"]) for r in cta_rows],
    }


def verdict(traffic, db):
    uv_7d = sum(traffic["daily_uv"].values())
    reg_api = traffic["funnel"]["register_api"]
    reg_page = traffic["funnel"]["register_page"]
    new_users = db["new_users_7d"]

    conv_page = round(reg_api / reg_page * 100, 1) if reg_page else 0
    conv_uv = round(new_users / uv_7d * 100, 2) if uv_7d else 0

    lines = []
    lines.append("## 验证判定（自动）")
    lines.append("")
    lines.append(f"- 7日真人 UV（估算）: **{uv_7d}**")
    lines.append(f"- 注册页访问 IP: **{reg_page}** → 完成注册 API: **{reg_api}**（页内转化 {conv_page}%）")
    lines.append(f"- 7日新增真实用户（DB）: **{new_users}**（UV 转化率 {conv_uv}%）")
    lines.append("")

    # Success criteria for 14-day validation
    if new_users >= 3 and conv_uv >= 2:
        lines.append("✅ **H1 初步成立**：有用户愿意注册，继续观察留存和模拟赛参与")
    elif reg_page >= 5 and reg_api == 0:
        lines.append("⚠️ **注册页有流量但无人提交**：检查表单体验或流量质量（非目标用户）")
    elif uv_7d < 50:
        lines.append("⚠️ **流量不足**：样本量太小，验证结论不可靠。优先 SEO/渠道引流或手动邀测")
    else:
        lines.append("❌ **H1 未成立**：有流量但注册转化极低，需调整价值主张或钩子")

    if db["contest_users"] > 0 and db["total_real_users"] > 0:
        pct = round(db["contest_users"] / db["total_real_users"] * 100)
        lines.append(f"- 模拟赛参与率: {pct}%（{'✅' if pct >= 40 else '⚠️ 待提升'}）")

    if db["signals_closed"] < 20:
        lines.append(f"- ⚠️ 已平仓信号仅 {db['signals_closed']} 条，战绩可信度不足（目标 ≥20）")

    baidu = ""
    cfg = Path("/opt/zongmao/site_config.json")
    if cfg.exists():
        try:
            baidu = json.loads(cfg.read_text()).get("baidu_hm_id", "")
        except json.JSONDecodeError:
            pass
    if not baidu:
        lines.append("- ⚠️ **百度统计未接入**：请在 site_config.json 填入 baidu_hm_id")

    return "\n".join(lines), conv_uv, new_users


def build_report():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    traffic = analyze_traffic(DAYS)
    db = db_metrics()
    verdict_text, conv_uv, new_users = verdict(traffic, db)

    lines = [
        f"# 宗贸网产品验证报告",
        f"生成时间: {now}",
        f"观察窗口: 近 {DAYS} 天",
        "",
        "## 验证假设",
        "1. **H1** 大宗商品交易者看到 AI 信号后愿意免费注册",
        "2. **H2** 模拟赛+自动跟单是有吸引力的注册钩子",
        "3. **H3** SEO（新闻/信号页）能带来目标流量",
        "",
        "## 成功标准（14天观察期）",
        "| 指标 | 目标 | 当前 |",
        "|------|------|------|",
        f"| 周新增真实注册 | ≥3 | {db['new_users_7d']} |",
        f"| UV→注册转化率 | ≥2% | {conv_uv}% |",
        f"| 已平仓信号数 | ≥20 | {db['signals_closed']} |",
        f"| 收入 | >¥0 | ¥{db['revenue']} |",
        "",
        "## 流量（真人 UV / 天）",
    ]
    for day, uv in traffic["daily_uv"].items():
        lines.append(f"- {day}: {uv}")

    lines += [
        "",
        "## 转化漏斗（7日去重 IP）",
        f"- 首页 `/`: {traffic['funnel']['home']}",
        f"- 信号 `/signals`: {traffic['funnel']['signals']}",
        f"- 注册页 `/register`: {traffic['funnel']['register_page']}",
        f"- 注册提交 `POST /api/auth/register`: {traffic['funnel']['register_api']}",
        f"- 欢迎页 `/welcome`: {traffic['funnel']['welcome']}",
        f"- 模拟赛 `/trading-contest`: {traffic['funnel']['contest']}",
        "",
        "## 用户数据",
        f"- 真实用户累计: {db['total_real_users']}",
        f"- 今日新增: {db['new_users_1d']}",
        f"- 7日新增: {db['new_users_7d']}",
        f"- 模拟赛参与者: {db['contest_users']}",
        f"- 线索（邮箱/手机）: {db['leads_total']}（7日 +{db['leads_7d']}）",
        f"- 信号胜率（已平仓）: {db['win_rate']}%（{db['signals_closed']} 条）",
    ]

    if db["regs_by_day"]:
        lines += ["", "## 注册趋势"]
        for d, n in db["regs_by_day"]:
            lines.append(f"- {d}: +{n}")

    if db["cta_events_db"]:
        lines += ["", "## CTA 点击（7日）"]
        for ev, n in db["cta_events_db"]:
            lines.append(f"- {ev}: {n}")

    lines += ["", verdict_text, ""]
    return "\n".join(lines)


def main():
    report = build_report()
    print(report)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(report, encoding="utf-8")
    print(f"\n[saved] {OUT}")


if __name__ == "__main__":
    main()
