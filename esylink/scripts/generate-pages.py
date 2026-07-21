#!/usr/bin/env python3
"""Generate new pages: legal, trust, compliance, industry."""
from pathlib import Path

WEB = Path("/var/www/esylink")

HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://esylink.cn{url}">
<link rel="stylesheet" href="/css/tw.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
</head>
<body class="bg-slate-50 text-slate-800">
<header class="bg-indigo-700 text-white py-4">
  <div class="max-w-4xl mx-auto px-4 flex justify-between items-center">
    <a href="/" class="font-bold text-lg">易连云通信</a>
    <a href="/contact" class="text-sm text-indigo-200 hover:text-white">联系我们</a>
  </div>
</header>
<main class="max-w-4xl mx-auto px-4 py-12 prose prose-slate">
"""

FOOT = """
</main>
<footer class="text-center text-xs text-slate-400 py-8">
  <a href="/legal/privacy.html" class="hover:text-slate-600 mx-2">隐私政策</a>
  <a href="/legal/terms.html" class="hover:text-slate-600 mx-2">服务条款</a>
  <a href="/compliance/" class="hover:text-slate-600 mx-2">合规说明</a>
  <p class="mt-2">© 合肥科讯通信技术有限公司 · 皖ICP备2026010967号-2</p>
</footer>
<script src="/js/page-track.js" defer></script>
<script src="/js/esylink-chat.js" defer></script>
</body></html>
"""

PAGES = {
    "legal/privacy.html": {
        "title": "隐私政策 — 易连云通信",
        "desc": "易连云通信隐私政策，说明我们如何收集、使用和保护您的个人信息。",
        "url": "/legal/privacy.html",
        "body": """<h1>隐私政策</h1>
<p>最后更新：2026年7月18日</p>
<p>合肥科讯通信技术有限公司（"我们"）运营 esylink.cn，重视用户隐私保护。</p>
<h2>一、信息收集</h2>
<p>我们可能收集：姓名、手机号、公司名称、行业信息、通话记录（经您授权）、网站访问日志。</p>
<h2>二、信息使用</h2>
<p>用于提供云通信服务、客户支持、产品改进、合规审计。不会出售您的个人信息。</p>
<h2>三、信息存储</h2>
<p>数据存储于中国大陆境内服务器，采用加密传输（HTTPS/TLS）和访问控制。</p>
<h2>四、您的权利</h2>
<p>您有权查询、更正、删除个人信息。联系：021-67173000 或 token.kexun.ltd。</p>
<h2>五、Cookie</h2>
<p>我们使用 Cookie 和类似技术进行会话管理和分析（Microsoft Clarity、自建 Analytics）。</p>""",
    },
    "legal/terms.html": {
        "title": "服务条款 — 易连云通信",
        "desc": "易连云通信服务条款，规范平台使用方式和双方权利义务。",
        "url": "/legal/terms.html",
        "body": """<h1>服务条款</h1>
<p>最后更新：2026年7月18日</p>
<p>使用易连云通信服务即表示您同意以下条款。</p>
<h2>一、服务内容</h2>
<p>我们提供 AI 智能外呼、云客服、400 电话、本地号码等云通信 SaaS 服务。</p>
<h2>二、用户义务</h2>
<p>您应合法使用服务，不得用于骚扰、诈骗、未授权营销。外呼需遵守《通信短信息和语音呼叫服务管理规定》。</p>
<h2>三、费用与退款</h2>
<p>按套餐计费，年付享折扣。试用期内可免费取消。付费后按合同约定处理退款。</p>
<h2>四、免责声明</h2>
<p>因不可抗力、第三方服务中断导致的服务暂停，我们不承担间接损失责任。</p>
<h2>五、争议解决</h2>
<p>适用中华人民共和国法律，争议由合肥市有管辖权法院管辖。</p>""",
    },
    "legal/ai-outbound-compliance.html": {
        "title": "AI外呼合规说明 — 易连云通信",
        "desc": "AI智能外呼合规流程：时段管控、黑名单、录音留痕、话术审核。",
        "url": "/legal/ai-outbound-compliance.html",
        "body": """<h1>AI 外呼合规说明</h1>
<p>易连云通信提供<strong>合规流程辅助</strong>，帮助企业建立可控、可追踪、可审计的客户沟通流程。</p>
<h2>合规能力</h2>
<ul>
<li><strong>外呼时段控制</strong>：默认 8:00-21:00，可自定义</li>
<li><strong>黑名单管理</strong>：支持导入 DNC 名单，自动过滤</li>
<li><strong>全程录音留痕</strong>：通话录音加密存储，可追溯审计</li>
<li><strong>话术审核</strong>：上线前话术模板审核，避免违规表述</li>
<li><strong>客户拒绝处理</strong>：客户明确拒绝后自动停止触达</li>
<li><strong>频次限制</strong>：同一号码每日/每周外呼次数上限</li>
</ul>
<h2>适用法规</h2>
<p>遵守《网络安全法》《个人信息保护法》《通信短信息和语音呼叫服务管理规定》等。</p>
<p><a href="/contact" class="text-indigo-600">获取合规外呼方案 →</a></p>""",
    },
    "trust/index.html": {
        "title": "信任中心 — 易连云通信",
        "desc": "易连云通信资质认证、安全合规、客户案例与服务承诺。",
        "url": "/trust/",
        "body": """<h1>信任中心</h1>
<p>易连云通信（合肥科讯通信技术有限公司）致力于为企业提供安全、合规、可靠的云通信服务。</p>
<div class="grid md:grid-cols-2 gap-6 not-prose my-8">
  <div class="bg-white rounded-xl p-6 shadow-sm border">
    <i class="fas fa-shield-alt text-indigo-600 text-2xl mb-3"></i>
    <h3 class="font-bold text-lg mb-2">等保三级认证</h3>
    <p class="text-sm text-slate-600">信息系统安全等级保护三级认证，数据加密传输与存储。</p>
  </div>
  <div class="bg-white rounded-xl p-6 shadow-sm border">
    <i class="fas fa-certificate text-indigo-600 text-2xl mb-3"></i>
    <h3 class="font-bold text-lg mb-2">通信增值业务许可</h3>
    <p class="text-sm text-slate-600">持有合法通信增值业务经营许可证。</p>
  </div>
  <div class="bg-white rounded-xl p-6 shadow-sm border">
    <i class="fas fa-users text-indigo-600 text-2xl mb-3"></i>
    <h3 class="font-bold text-lg mb-2">2,000+ 企业客户</h3>
    <p class="text-sm text-slate-600">覆盖教育、金融、电商、医疗、保险等 10+ 行业。</p>
  </div>
  <div class="bg-white rounded-xl p-6 shadow-sm border">
    <i class="fas fa-headset text-indigo-600 text-2xl mb-3"></i>
    <h3 class="font-bold text-lg mb-2">7×24 技术支持</h3>
    <p class="text-sm text-slate-600">全国 53 城本地化服务，1 小时响应。</p>
  </div>
</div>
<p><a href="/cases/" class="text-indigo-600 font-semibold">查看客户案例 →</a></p>""",
    },
    "compliance/index.html": {
        "title": "合规中心 — AI外呼·电销·催收合规指南",
        "desc": "AI外呼合规指南、电销机器人合规要求、智能催收合规流程。",
        "url": "/compliance/",
        "body": """<h1>合规中心</h1>
<p>帮助企业安全、合规地使用 AI 外呼、电销机器人和智能催收系统。</p>
<h2><a href="/legal/ai-outbound-compliance.html">AI 外呼合规说明</a></h2>
<p>时段管控、黑名单、录音留痕、话术审核、拒绝后停止触达。</p>
<h2>电销合规要点</h2>
<ul>
<li>获得用户事先同意或具有合法呼叫事由</li>
<li>明示身份和呼叫目的</li>
<li>提供退订/拒绝渠道</li>
<li>遵守每日外呼时段限制</li>
</ul>
<h2>催收合规要点</h2>
<ul>
<li>全程录音，话术合规审核</li>
<li>禁止威胁、辱骂、骚扰</li>
<li>频次和时段严格管控</li>
<li>配合监管检查和投诉处理</li>
</ul>
<p><a href="/free-trial.html" class="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold mt-4">获取合规方案</a></p>""",
    },
}

INDUSTRIES = {
    "solutions/dental.html": ("口腔诊所AI外呼系统", "种植牙邀约、复诊提醒、术后回访", "dental", "口腔"),
    "solutions/insurance.html": ("保险续保AI外呼系统", "续保提醒、保单回访、客户激活", "insurance", "保险"),
    "solutions/saas.html": ("SaaS企业AI外呼方案", "Demo邀约、试用转化、客户成功回访", "saas", "SaaS"),
    "solutions/government.html": ("政务通知外呼系统", "政策通知、办事提醒、满意度调查", "government", "政务"),
}

INDUSTRY_TEMPLATE = """<h1>{title}</h1>
<p class="text-lg text-slate-600 mb-8">{subtitle}。易连云通信为{industry_cn}行业提供 AI 智能外呼 + 云客服一体化方案。</p>
<div class="grid md:grid-cols-3 gap-4 not-prose mb-8">
  <div class="bg-indigo-50 rounded-xl p-5 text-center"><div class="text-2xl font-bold text-indigo-700">80%</div><div class="text-sm text-slate-600">人工成本降低</div></div>
  <div class="bg-indigo-50 rounded-xl p-5 text-center"><div class="text-2xl font-bold text-indigo-700">3x</div><div class="text-sm text-slate-600">接通率提升</div></div>
  <div class="bg-indigo-50 rounded-xl p-5 text-center"><div class="text-2xl font-bold text-indigo-700">7天</div><div class="text-sm text-slate-600">免费试用</div></div>
</div>
<h2>适用场景</h2>
<ul><li>{subtitle}</li><li>意向客户自动分级与 CRM 同步</li><li>7×24 自动外呼与人工坐席协同</li></ul>
<h2>行业话术模板</h2>
<p>提供{industry_cn}行业专属话术模板，开箱即用，支持 A/B 测试优化。</p>
<div class="not-prose flex gap-4 mt-8">
  <a href="/free-trial.html?industry={slug}" class="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold">免费试用</a>
  <a href="/pricing" class="border border-indigo-300 text-indigo-700 px-6 py-3 rounded-lg font-semibold">查看报价</a>
</div>"""


def main():
    for path, data in PAGES.items():
        fp = WEB / path
        fp.parent.mkdir(parents=True, exist_ok=True)
        html = HEAD.format(**data) + data["body"] + FOOT
        fp.write_text(html, encoding="utf-8")
        print(f"  ✓ {path}")

    for path, (title, subtitle, slug, industry_cn) in INDUSTRIES.items():
        fp = WEB / path
        fp.parent.mkdir(parents=True, exist_ok=True)
        url = "/" + path.replace("solutions/", "solutions/").replace(".html", "")
        data = {
            "title": f"{title} | 易连云通信",
            "desc": f"易连云通信{industry_cn}行业AI外呼方案：{subtitle}。7天免费试用。",
            "url": f"/{path}",
        }
        body = INDUSTRY_TEMPLATE.format(
            title=title, subtitle=subtitle, slug=slug, industry_cn=industry_cn,
        )
        html = HEAD.format(**data) + body + FOOT
        fp.write_text(html, encoding="utf-8")
        print(f"  ✓ {path}")

    print("✅ Pages generated")


if __name__ == "__main__":
    main()
