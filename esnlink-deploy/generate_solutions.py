#!/usr/bin/env python3
"""Generate industry solution pages for esnlink.cn."""

from pathlib import Path

SOLUTIONS = [
    {
        "slug": "education",
        "title": "教育行业外呼与短信解决方案",
        "meta": "教培机构 AI 招生外呼、短信通知、学员回访一站式方案。招生转化率提升 40%+，免费试用 14 天。",
        "keywords": "教育外呼, 教培招生, AI招生外呼, 教育短信, 培训机构外呼系统",
        "icon": "🎓",
        "hero": "教育行业智能通信方案",
        "subtitle": "AI 招生外呼 + 短信通知 + 智能客服，赋能教培全链路",
        "pain_points": [
            ("招生成本高", "传统人工外呼效率低，单个意向学员获客成本超 200 元"),
            ("跟进不及时", "咨询线索 30 分钟内未跟进，流失率高达 60%"),
            ("通知触达难", "课程变动、活动通知依赖微信群，到达率不足 50%"),
        ],
        "solutions": [
            ("AI 招生外呼", "自动拨打潜在学员，多轮对话筛选意向，无缝转接顾问", "call-center.html"),
            ("短信通知", "开课提醒、缴费通知、活动推广，三网直达 99%+ 到达率", "sms.html"),
            ("智能客服", "7×24 小时应答课程咨询，自动归档学员信息至 CRM", "edu.html"),
        ],
        "metrics": [("40%+", "招生转化率提升"), ("3x", "外呼效率提升"), ("99%+", "短信到达率")],
        "cases": "已服务多家 K12、职业教育、成人培训机构，平均帮助客户降低 35% 招生成本。",
    },
    {
        "slug": "ecommerce",
        "title": "电商短信营销与外呼解决方案",
        "meta": "电商大促短信群发、订单通知、AI 外呼回访方案。高并发稳定送达，助力 GMV 增长。",
        "keywords": "电商短信, 短信营销, 订单通知短信, 电商外呼, 大促短信",
        "icon": "🛒",
        "hero": "电商行业智能触达方案",
        "subtitle": "大促短信 + 订单通知 + 满意度外呼，全链路用户运营",
        "pain_points": [
            ("大促短信被拦截", "营销短信到达率低，影响大促转化"),
            ("通知不及时", "发货、物流、退款通知延迟，客诉率高"),
            ("复购率低", "缺乏系统化回访机制，老客激活不足"),
        ],
        "solutions": [
            ("营销短信", "大促预热、限时优惠、购物车提醒，智能路由提升到达率", "sms.html"),
            ("通知短信", "下单确认、发货提醒、签收通知，5 秒内送达", "sms.html"),
            ("AI 外呼回访", "自动满意度回访、好评邀约、流失召回", "call-center.html"),
        ],
        "metrics": [("99%+", "通知到达率"), ("50万+", "分钟级并发"), ("25%", "复购率提升")],
        "cases": "服务多家电商及新零售品牌，双 11 期间稳定发送千万级短信，零故障。",
    },
    {
        "slug": "finance",
        "title": "金融短信验证码与安全通信方案",
        "meta": "金融级短信验证码 API、交易通知、合规外呼方案。等保三级、全链路加密，满足监管要求。",
        "keywords": "金融短信, 短信验证码API, 银行短信, 金融外呼, 交易通知短信",
        "icon": "🏦",
        "hero": "金融行业安全通信方案",
        "subtitle": "验证码 API + 交易通知 + 合规外呼，金融级安全标准",
        "pain_points": [
            ("验证码到达慢", "用户注册/支付时验证码延迟，导致转化率下降"),
            ("安全合规压力", "短信内容、外呼录音需满足金融监管要求"),
            ("成本居高不下", "大厂短信价格高，年通信费用超百万"),
        ],
        "solutions": [
            ("验证码 API", "5 秒送达，99.9% 到达率，支持一键登录", "docs/sms-api.html"),
            ("交易通知", "转账提醒、还款通知、风控告警，实时触达", "sms.html"),
            ("合规外呼", "账单提醒、催收外呼，全量录音存档", "call-center.html"),
        ],
        "metrics": [("5s", "验证码送达"), ("等保三级", "安全认证"), ("30%", "成本节省")],
        "cases": "为多家持牌金融机构提供通信服务，通过等保测评与监管合规审查。",
    },
]


def render(s: dict) -> str:
    pain_html = "".join(
        f'<div class="pain-card"><h4>{t}</h4><p>{d}</p></div>' for t, d in s["pain_points"]
    )
    sol_html = "".join(
        f'<div class="sol-card"><h4>{t}</h4><p>{d}</p><a href="/{l}">了解产品 →</a></div>'
        for t, d, l in s["solutions"]
    )
    met_html = "".join(
        f'<div class="metric"><div class="num">{n}</div><div class="lbl">{l}</div></div>'
        for n, l in s["metrics"]
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{s['title']} | 翼星科技 esnlink</title>
    <meta name="description" content="{s['meta']}">
    <meta name="keywords" content="{s['keywords']}">
    <link rel="canonical" href="https://www.esnlink.cn/solutions/{s['slug']}.html">
    <meta property="og:title" content="{s['title']} | 翼星科技">
    <meta property="og:description" content="{s['meta']}">
    <meta property="og:url" content="https://www.esnlink.cn/solutions/{s['slug']}.html">
    <meta property="og:image" content="https://www.esnlink.cn/og-image.png">
    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"WebPage","name":"{s['title']}","description":"{s['meta']}","url":"https://www.esnlink.cn/solutions/{s['slug']}.html"}}
    </script>
    <link rel="stylesheet" href="/css/header-footer.css">
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:system-ui,sans-serif;color:#1e293b;line-height:1.6}}
        .container{{max-width:1000px;margin:0 auto;padding:0 1.5rem}}
        .hero{{padding:4rem 0;background:linear-gradient(160deg,#fff,#eff6ff)}}
        .hero h1{{font-size:2.4rem;font-weight:800;margin-bottom:0.5rem}}
        .hero .sub{{color:#2563eb;font-weight:600;margin-bottom:1rem}}
        .hero p{{color:#64748b;max-width:600px}}
        .btn{{display:inline-block;padding:0.7rem 1.8rem;border-radius:40px;font-weight:600;text-decoration:none;margin-top:1.5rem;margin-right:0.5rem}}
        .btn-primary{{background:linear-gradient(135deg,#f59e0b,#ea580c);color:#fff}}
        .btn-secondary{{border:1.5px solid #2563eb;color:#2563eb}}
        section{{padding:3rem 0}}
        h2{{text-align:center;font-size:1.6rem;margin-bottom:2rem}}
        .pain-grid,.sol-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.2rem}}
        .pain-card,.sol-card{{background:#f8fafc;border-radius:12px;padding:1.5rem;border:1px solid #e2e8f0}}
        .pain-card h4,.sol-card h4{{margin-bottom:0.5rem}}
        .pain-card p,.sol-card p{{color:#64748b;font-size:0.95rem}}
        .sol-card a{{display:inline-block;margin-top:0.8rem;color:#2563eb;font-weight:600;text-decoration:none;font-size:0.9rem}}
        .metrics{{display:flex;justify-content:center;gap:3rem;flex-wrap:wrap;padding:2rem 0}}
        .metric{{text-align:center}}
        .metric .num{{font-size:2rem;font-weight:800;color:#2563eb}}
        .metric .lbl{{font-size:0.85rem;color:#64748b}}
        .case-box{{background:#0f172a;color:#e2e8f0;border-radius:12px;padding:2rem;text-align:center}}
        .breadcrumbs{{background:#f8fafc;padding:0.7rem 0;font-size:0.88rem;border-bottom:1px solid #eef2f6}}
        .breadcrumbs a{{color:#64748b;text-decoration:none}}
        .footer{{background:#0f172a;padding:2rem 0;color:#94a3b8;text-align:center;font-size:0.85rem}}
        .footer a{{color:#60a5fa;text-decoration:none}}
    </style>
</head>
<body>
<nav class="navbar">
    <div class="container nav-container">
        <a href="/index.html" class="logo"><span>esnlink · 翼星科技</span><span class="logo-slogan">行业方案</span></a>
        <div class="nav-links">
            <a href="/index.html">首页</a>
            <a href="/call-center.html">智能外呼</a>
            <a href="/sms.html">短信平台</a>
            <a href="/pricing.html">定价</a>
            <a href="/booking.html" class="nav-btn btn-trial">免费试用</a>
        </div>
        <button class="hamburger" aria-label="菜单">☰</button>
    </div>
</nav>
<nav class="breadcrumbs"><div class="container"><a href="/index.html">首页</a> · <a href="/solutions/community-hospital.html">解决方案</a> · <span>{s['icon']} {s['slug']}</span></div></nav>

<section class="hero">
    <div class="container">
        <div style="font-size:3rem;margin-bottom:0.5rem">{s['icon']}</div>
        <h1>{s['hero']}</h1>
        <p class="sub">{s['subtitle']}</p>
        <p>翼星科技深耕行业场景，提供可落地的通信解决方案，助力企业降本增效。</p>
        <a href="/booking.html" class="btn btn-primary">免费获取方案</a>
        <a href="/pricing.html" class="btn btn-secondary">查看定价</a>
    </div>
</section>

<section style="background:#f8fafc">
    <div class="container">
        <h2>行业痛点</h2>
        <div class="pain-grid">{pain_html}</div>
    </div>
</section>

<section>
    <div class="container">
        <h2>翼星解决方案</h2>
        <div class="sol-grid">{sol_html}</div>
    </div>
</section>

<section style="background:#f8fafc">
    <div class="container">
        <h2>效果数据</h2>
        <div class="metrics">{met_html}</div>
    </div>
</section>

<section>
    <div class="container case-box">
        <h2 style="color:#fff;margin-bottom:1rem">客户案例</h2>
        <p>{s['cases']}</p>
        <a href="/booking.html" class="btn btn-primary" style="margin-top:1.5rem">预约案例分享</a>
    </div>
</section>

<footer class="footer">
    <p>&copy; 2025 合肥翼星智能科技有限公司 · <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">皖ICP备2026012968号-1</a></p>
</footer>
<script>(function(){{var h=document.querySelector('.hamburger'),n=document.querySelector('.nav-links');if(h&&n)h.addEventListener('click',function(){{n.classList.toggle('open')}})}})();</script>
</body>
</html>"""


def main():
    out = Path(__file__).parent / "site" / "solutions"
    out.mkdir(parents=True, exist_ok=True)
    for s in SOLUTIONS:
        path = out / f"{s['slug']}.html"
        path.write_text(render(s), encoding="utf-8")
        print(f"Generated {path}")


if __name__ == "__main__":
    main()
