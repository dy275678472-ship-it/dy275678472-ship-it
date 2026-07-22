#!/usr/bin/env python3
"""宗贸网 SEO/GEO P2 补丁 — 术语词典、年度报告、资讯结构化、对比页留资"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path("/opt/zongmao")
APP = BASE / "app.py"
TPL = BASE / "templates"
GEN = BASE / "gen_news.py"
COMPARE = TPL / "compare.html"
LLMS = BASE / "static" / "llms.txt"
SITE = "https://zongmao.cn"

GLOSSARY_TERMS = [
    ("多头", "看涨方向，预期价格上涨时买入开仓。"),
    ("空头", "看跌方向，预期价格下跌时卖出开仓。"),
    ("保证金", "期货交易只需缴纳合约价值一定比例的担保资金。"),
    ("一手", "期货最小交易单位，不同品种合约规模不同。"),
    ("涨跌停板", "交易所规定的单日最大涨跌幅限制。"),
    ("持仓量", "市场上尚未平仓的合约总数量。"),
    ("成交量", "某一时间段内成交的合约数量。"),
    ("结算价", "交易所用于计算当日盈亏的参考价格。"),
    ("基差", "现货价格与期货价格之间的差额。"),
    ("升贴水", "期货价格高于现货为升水，反之为贴水。"),
    ("主力合约", "当前成交量和持仓量最大的合约月份。"),
    ("移仓换月", "将持仓从临近交割合约转移到远月合约。"),
    ("交割", "期货合约到期时按规则进行现货或现金结算。"),
    ("套保", "利用期货对冲现货价格风险。"),
    ("套利", "利用相关品种或跨期价差获取低风险收益。"),
    ("止损", "当亏损达到预设位时平仓以控制损失。"),
    ("止盈", "当盈利达到目标位时平仓锁定利润。"),
    ("盈亏比", "平均盈利与平均亏损的比值。"),
    ("胜率", "盈利交易次数占总交易次数的比例。"),
    ("回撤", "净值从高点回落的幅度。"),
    ("开仓", "建立新的期货头寸。"),
    ("平仓", "了结已有期货头寸。"),
    ("爆仓", "保证金不足被强制平仓。"),
    ("追保", "保证金不足时需追加资金。"),
    ("滑点", "下单价格与实际成交价格的偏差。"),
    ("tick", "期货价格变动的最小单位。"),
    ("多头信号", "AI或分析认为价格将上涨的交易建议。"),
    ("空头信号", "AI或分析认为价格将下跌的交易建议。"),
    ("入场价", "建议建立头寸的价格。"),
    ("目标价", "预期价格到达的止盈位置。"),
    ("SC原油", "上海国际能源交易中心上市的原油期货品种。"),
    ("螺纹钢", "建筑用钢材期货，反映基建和地产需求。"),
    ("铁矿石", "钢铁生产主要原料，与黑色产业链高度相关。"),
    ("沪铜", "反映全球铜供需和宏观预期的有色龙头品种。"),
    ("豆粕", "饲料核心原料，与养殖景气度密切相关。"),
    ("动力煤", "电力行业重要燃料，受政策和库存影响大。"),
    ("PTA", "聚酯产业链上游，与纺织服装需求相关。"),
    ("甲醇", "化工中间品，受煤制成本和下游需求影响。"),
    ("棕榈油", "全球产量最大的植物油，受产地天气影响。"),
    ("LME", "伦敦金属交易所，全球有色金属定价中心。"),
    ("OPEC", "石油输出国组织，影响原油供给预期。"),
    ("EIA库存", "美国能源信息署周度原油库存报告。"),
    ("USDA报告", "美国农业部发布的农产品供需报告。"),
    ("开工率", "生产企业实际产能利用比例。"),
    ("库存消费比", "库存水平与消费量的比值，衡量供需松紧。"),
    ("跨期套利", "同一品种不同月份合约之间的价差交易。"),
    ("跨品种套利", "相关品种之间的价差交易，如豆粕与豆油。"),
    ("模拟交易", "使用虚拟资金练习交易策略，无真实风险。"),
    ("AI交易信号", "由算法根据行情和规则自动生成的多空建议。"),
    ("宗贸网", "大宗商品AI交易信号平台，覆盖34个期货品种。"),
]

PAGE_SHELL_FOOT = """
<footer class="footer">© 2026 宗贸网 zongmao.cn · 大宗商品交易信号与行情平台
<br><a href="/about" style="color:#fff;margin:0 8px;">关于我们</a> | <a href="/methodology" style="color:#fff;margin:0 8px;">信号方法论</a> | <a href="/glossary" style="color:#fff;margin:0 8px;">术语词典</a> | <a href="/stats/2026" style="color:#fff;margin:0 8px;">2026年报</a>
<br><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener" style="color:#888;">皖ICP备2026016894号-1</a>
</footer>
<script src="/static/js/common.js"></script>
{% include "_tongji.html" %}
</body></html>"""


def backup(path: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(path, path.with_suffix(path.suffix + f".bak_{ts}"))
    print(f"  backup: {path.name}")


def write_glossary_template():
    path = TPL / "glossary.html"
    if path.exists() and "P2-GENERATED" in path.read_text(encoding="utf-8", errors="replace"):
        print("ℹ️  glossary.html exists")
        return
    items_html = "\n".join(
        f'<div class="card" style="padding:1rem 1.2rem;margin-bottom:0.8rem;" id="{t[0]}">'
        f'<h3 style="margin:0 0 0.4rem;font-size:1.05rem;">{t[0]}</h3>'
        f'<p style="margin:0;color:#555;line-height:1.7;">{t[1]}</p></div>'
        for t in GLOSSARY_TERMS
    )
    faq_entities = ",".join(
        json.dumps({
            "@type": "Question",
            "name": f"什么是{t[0]}？",
            "acceptedAnswer": {"@type": "Answer", "text": t[1]},
        }, ensure_ascii=False)
        for t in GLOSSARY_TERMS[:20]
    )
    html = f"""<!-- P2-GENERATED -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>期货术语词典 — 宗贸网</title>
<meta name="description" content="大宗商品期货术语解释：保证金、多空、套保、套利、盈亏比等{len(GLOSSARY_TERMS)}个核心概念，助您快速入门期货交易。">
<link rel="canonical" href="{SITE}/glossary">
<link rel="stylesheet" href="/static/css/style.css">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_entities}]}}
</script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
  {{"@type":"ListItem","position":1,"name":"首页","item":"{SITE}"}},
  {{"@type":"ListItem","position":2,"name":"术语词典","item":"{SITE}/glossary"}}
]}}
</script>
</head>
<body>
<nav class="navbar">
  <a href="/" class="nav-brand">宗贸网</a>
  <div class="nav-links">
    <a href="/market">行情</a><a href="/signals">信号</a><a href="/performance">战绩</a>
    <a href="/premium" style="color:#c0392b;font-weight:bold;">会员</a>
  </div>
  <div class="nav-right"><a href="/login">登录</a><a href="/register">注册</a></div>
</nav>
<div class="container" style="max-width:900px;">
  <h1>期货术语词典</h1>
  <p style="color:#666;">{len(GLOSSARY_TERMS)} 个核心概念 · 从入门到进阶 · <a href="/tutorial">新手教程</a> · <a href="/stats/2026">2026信号年报</a></p>
  <div style="margin:1.5rem 0;">{items_html}</div>
  <div style="text-align:center;margin:2rem 0;">
    <a href="/register" class="btn btn-primary" style="padding:0.8rem 2rem;">免费注册查看AI信号</a>
  </div>
</div>
{PAGE_SHELL_FOOT}"""
    path.write_text(html, encoding="utf-8")
    print("✅ glossary.html created")


def write_stats_template():
    path = TPL / "stats_2026.html"
    if path.exists() and "P2-GENERATED" in path.read_text(encoding="utf-8", errors="replace"):
        print("ℹ️  stats_2026.html exists")
        return
    html = """<!-- P2-GENERATED -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2026年AI交易信号年报 — 宗贸网</title>
<meta name="description" content="宗贸网2026年度信号统计报告：累计{{ kpi.total }}笔信号，历史胜率{{ kpi.win_rate }}%，按品种和月份分解的可验证战绩数据。">
<link rel="canonical" href="__SITE__/stats/2026">
<link rel="stylesheet" href="/static/css/style.css">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Report","name":"宗贸网2026 AI交易信号年报",
  "url":"__SITE__/stats/2026","datePublished":"2026-01-01",
  "author":{"@type":"Organization","name":"宗贸网研究院"},
  "description":"2026年度大宗商品AI交易信号战绩统计报告"}
</script>
</head>
<body>
<nav class="navbar">
  <a href="/" class="nav-brand">宗贸网</a>
  <div class="nav-links">
    <a href="/performance">战绩看板</a><a href="/methodology">方法论</a><a href="/glossary">术语词典</a>
  </div>
</nav>
<div class="container" style="max-width:900px;">
  <h1>📊 2026 AI 交易信号年报</h1>
  <p style="color:#666;">数据截至 {{ report_date }} · 全部信号公开可回溯 · <a href="/performance">实时战绩看板</a></p>
  <div class="kpi-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:1rem;margin:1.5rem 0;">
    <div class="card" style="padding:1rem;text-align:center;"><div style="font-size:1.8rem;font-weight:700;">{{ kpi.total }}</div><div style="font-size:0.8rem;color:#888;">累计信号</div></div>
    <div class="card" style="padding:1rem;text-align:center;"><div style="font-size:1.8rem;font-weight:700;">{{ kpi.closed }}</div><div style="font-size:0.8rem;color:#888;">已结信号</div></div>
    <div class="card" style="padding:1rem;text-align:center;"><div style="font-size:1.8rem;font-weight:700;">{{ kpi.win_rate }}%</div><div style="font-size:0.8rem;color:#888;">历史胜率</div></div>
    <div class="card" style="padding:1rem;text-align:center;"><div style="font-size:1.8rem;font-weight:700;">{{ kpi.profit_loss_ratio }}</div><div style="font-size:0.8rem;color:#888;">盈亏比</div></div>
    <div class="card" style="padding:1rem;text-align:center;"><div style="font-size:1.8rem;font-weight:700;">{{ '%+.1f'|format(kpi.total_pnl) }}%</div><div style="font-size:0.8rem;color:#888;">累计收益</div></div>
  </div>
  {% if by_category %}
  <h2>按板块胜率</h2>
  <table class="quote-table"><tr><th>板块</th><th>已结</th><th>胜率</th><th>累计收益</th></tr>
  {% for row in by_category %}
  <tr><td>{{ row.category }}</td><td>{{ row.cnt }}</td><td>{{ row.win_rate }}%</td><td>{{ '%+.1f'|format(row.total_pnl) }}%</td></tr>
  {% endfor %}
  </table>
  {% endif %}
  {% if monthly %}
  <h2 style="margin-top:2rem;">月度表现</h2>
  <table class="quote-table"><tr><th>月份</th><th>信号数</th><th>胜率</th><th>均收益</th></tr>
  {% for m in monthly %}
  <tr><td>{{ m.month }}</td><td>{{ m.cnt }}</td><td>{{ m.win_rate }}%</td><td>{{ '%+.2f'|format(m.avg_pnl) }}%</td></tr>
  {% endfor %}
  </table>
  {% endif %}
  {% if top_symbols %}
  <h2 style="margin-top:2rem;">品种战绩 TOP5</h2>
  <table class="quote-table"><tr><th>品种</th><th>信号数</th><th>胜率</th><th>累计收益</th></tr>
  {% for s in top_symbols %}
  <tr><td><a href="/price/{{ s.symbol }}">{{ s.name }}</a></td><td>{{ s.cnt }}</td><td>{{ s.win_rate }}%</td><td>{{ '%+.1f'|format(s.total_pnl) }}%</td></tr>
  {% endfor %}
  </table>
  {% endif %}
  <p style="margin-top:2rem;color:#888;font-size:0.9rem;">免责声明：历史战绩不代表未来表现，仅供参考，不构成投资建议。</p>
</div>
__PAGE_SHELL__"""
    html = html.replace("__SITE__", SITE).replace("__PAGE_SHELL__", PAGE_SHELL_FOOT)
    path.write_text(html, encoding="utf-8")
    print("✅ stats_2026.html created")


def patch_app():
    text = APP.read_text(encoding="utf-8")
    changed = False

    routes = '''
@app.get("/glossary")
async def page_glossary(request: Request):
    return render(request, "glossary.html")

@app.get("/stats/2026")
async def page_stats_2026(request: Request):
    kpi = get_performance_kpi()
    conn = get_db()
    by_category = [dict(r) for r in conn.execute("""
        SELECT q.category,
               COUNT(*) as cnt,
               ROUND(SUM(CASE WHEN ts.result_pct > 0 THEN 1 ELSE 0 END)*100.0/COUNT(*),1) as win_rate,
               ROUND(COALESCE(SUM(ts.result_pct),0),2) as total_pnl
        FROM trade_signals ts JOIN quotes q ON ts.symbol=q.symbol
        WHERE ts.status='closed' GROUP BY q.category ORDER BY cnt DESC
    """).fetchall()]
    monthly = [dict(r) for r in conn.execute("""
        SELECT substr(closed_at,1,7) as month, COUNT(*) as cnt,
               ROUND(SUM(CASE WHEN result_pct>0 THEN 1 ELSE 0 END)*100.0/COUNT(*),1) as win_rate,
               ROUND(AVG(result_pct),2) as avg_pnl
        FROM trade_signals WHERE status='closed' AND closed_at!=''
        GROUP BY month ORDER BY month DESC LIMIT 12
    """).fetchall()]
    top_symbols = [dict(r) for r in conn.execute("""
        SELECT ts.symbol, q.name, COUNT(*) as cnt,
               ROUND(SUM(CASE WHEN ts.result_pct>0 THEN 1 ELSE 0 END)*100.0/COUNT(*),1) as win_rate,
               ROUND(COALESCE(SUM(ts.result_pct),0),2) as total_pnl
        FROM trade_signals ts JOIN quotes q ON ts.symbol=q.symbol
        WHERE ts.status='closed' GROUP BY ts.symbol ORDER BY cnt DESC LIMIT 5
    """).fetchall()]
    conn.close()
    return render(request, "stats_2026.html", kpi=kpi, by_category=by_category,
                  monthly=monthly, top_symbols=top_symbols,
                  report_date=datetime.now().strftime("%Y-%m-%d"))

'''
    if '@app.get("/glossary")' not in text:
        text = text.replace('@app.get("/methodology")', routes + '@app.get("/methodology")', 1)
        changed = True

    if "zongmao.cn/glossary" not in text:
        text = text.replace(
            "('https://zongmao.cn/welcome', now, '0.6', 'monthly'),",
            "('https://zongmao.cn/welcome', now, '0.6', 'monthly'),\n"
            "        ('https://zongmao.cn/glossary', now, '0.7', 'monthly'),\n"
            "        ('https://zongmao.cn/stats/2026', now, '0.7', 'monthly'),",
            1,
        )
        changed = True

    if changed:
        backup(APP)
        APP.write_text(text, encoding="utf-8")
        print("✅ app.py routes + sitemap")
    else:
        print("ℹ️  app.py already patched")


def patch_compare_lead():
    if not COMPARE.exists():
        return
    text = COMPARE.read_text(encoding="utf-8")
    if "compare-lead-form" in text:
        print("ℹ️  compare.html lead form exists")
        return
    block = """
<div class="card" id="compare-lead-form" style="padding:2rem;margin-top:1.5rem;background:#f8f9fa;text-align:center;">
  <h3 style="margin:0 0 0.5rem;">获取免费信号试用</h3>
  <p style="color:#666;margin:0 0 1rem;">留下手机号，领取 7 天体验 + 每日早报推送</p>
  <div style="display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;max-width:420px;margin:0 auto;">
    <input id="leadPhone" type="tel" placeholder="手机号" maxlength="11" style="flex:1;min-width:180px;padding:0.7rem;border:1px solid #ddd;border-radius:8px;">
    <button onclick="submitCompareLead()" class="btn btn-primary" style="padding:0.7rem 1.5rem;">免费领取</button>
  </div>
  <p id="leadMsg" style="font-size:0.85rem;margin-top:0.8rem;color:#27ae60;"></p>
</div>
<script>
async function submitCompareLead(){
  const phone=document.getElementById('leadPhone').value.trim();
  const msg=document.getElementById('leadMsg');
  if(!/^1\\d{10}$/.test(phone)){msg.style.color='#e74c3c';msg.textContent='请输入正确手机号';return;}
  try{
    const r=await fetch('/api/monetize/lead',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({phone:phone,source:'compare_page',page:location.pathname})});
    const d=await r.json();
    msg.style.color='#27ae60';
    msg.textContent=d.success?(d.duplicate?'您已领取过，请直接注册登录':'领取成功！请查收短信或邮件'):(d.error||'提交失败');
    if(d.success&&!d.duplicate) setTimeout(()=>location.href='/register',1500);
  }catch(e){msg.style.color='#e74c3c';msg.textContent='网络错误';}
}
</script>"""
    text = text.replace(
        '<div style="text-align:center;margin-top:1.5rem;">\n<a href="/register"',
        block + '\n<div style="text-align:center;margin-top:1.5rem;">\n<a href="/register"',
        1,
    )
    if "/glossary" not in text:
        text = text.replace(
            '<a href="/disclaimer"',
            '<a href="/glossary" style="color:#fff;margin:0 8px;">术语词典</a> | <a href="/stats/2026" style="color:#fff;margin:0 8px;">2026年报</a> | <a href="/disclaimer"',
            1,
        )
    backup(COMPARE)
    COMPARE.write_text(text, encoding="utf-8")
    print("✅ compare.html lead form")


def patch_gen_news():
    if not GEN.exists():
        return
    text = GEN.read_text(encoding="utf-8")
    changed = False

    if '"AI分析师"' in text:
        text = text.replace('"AI分析师"', '"宗贸网研究院"')
        changed = True

    if "{style_instruction}" in text:
        text = text.replace("{style_instruction}", "{style}")
        changed = True

    extra = """
### 文末必须附加（GEO结构化块）
在正文最后追加以下两个区块：

## 行情速览
用Markdown表格列出本篇涉及的品种：| 品种 | 最新价 | 涨跌幅 | 简评 |

## 宗贸网AI信号观点
用1-2句话总结当前板块的多空倾向，并注明「详见 zongmao.cn/signals」。
"""
    if "行情速览" not in text:
        text = text.replace(
            '只输出JSON，正文务必800字以上！"""',
            extra + '\n只输出JSON，正文务必800字以上！"""',
            1,
        )
        changed = True

    if changed:
        backup(GEN)
        GEN.write_text(text, encoding="utf-8")
        print("✅ gen_news.py structured content + author fix")
    else:
        print("ℹ️  gen_news.py already patched")


def patch_llms():
    if not LLMS.exists():
        return
    text = LLMS.read_text(encoding="utf-8")
    additions = """
- 术语词典: https://zongmao.cn/glossary
- 2026信号年报: https://zongmao.cn/stats/2026
"""
    if "/glossary" not in text:
        text = text.replace("- 新手教程:", additions + "- 新手教程:")
        LLMS.write_text(text, encoding="utf-8")
        print("✅ llms.txt updated")


def main():
    print("🚀 Zongmao SEO/GEO P2 patch")
    write_glossary_template()
    write_stats_template()
    patch_app()
    patch_compare_lead()
    patch_gen_news()
    patch_llms()
    print("✅ SEO P2 complete — restart zongmao.service")


if __name__ == "__main__":
    main()
