#!/usr/bin/env python3
"""P1: Enhance 5 core product pages with depth content + trust signals."""
from pathlib import Path

WEB = Path("/var/www/esylink")

PRODUCTS = {
    "dialer/index.html": {
        "marker": "<!-- ESYLINK-PRODUCT-DEPTH -->",
        "block": """
<!-- ESYLINK-PRODUCT-DEPTH -->
<section class="max-w-6xl mx-auto px-4 py-12">
  <h2 class="text-2xl font-bold text-slate-900 mb-6">AI 外呼核心能力</h2>
  <div class="grid md:grid-cols-3 gap-6">
    <div class="bg-white rounded-xl p-6 shadow-sm border"><i class="fas fa-brain text-indigo-600 text-xl mb-3"></i><h3 class="font-bold mb-2">大模型语义理解</h3><p class="text-sm text-slate-600">支持多轮对话、意图识别、自动分级，高意向客户实时推送给销售。</p></div>
    <div class="bg-white rounded-xl p-6 shadow-sm border"><i class="fas fa-shield-alt text-indigo-600 text-xl mb-3"></i><h3 class="font-bold mb-2">合规流程管控</h3><p class="text-sm text-slate-600">外呼时段、黑名单、录音留痕、话术审核，满足电销合规要求。</p></div>
    <div class="bg-white rounded-xl p-6 shadow-sm border"><i class="fas fa-chart-line text-indigo-600 text-xl mb-3"></i><h3 class="font-bold mb-2">实时数据看板</h3><p class="text-sm text-slate-600">接通率、意向分布、坐席效率一屏掌握，支持导出与 API 对接。</p></div>
  </div>
  <div class="mt-8 flex flex-wrap gap-4">
    <a href="/free-trial.html?from=dialer" class="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold">7天免费试用</a>
    <a href="/calculator" class="border border-indigo-300 text-indigo-700 px-6 py-3 rounded-lg font-semibold">ROI 计算器</a>
    <a href="/legal/ai-outbound-compliance.html" class="text-indigo-600 font-medium">合规说明 →</a>
  </div>
</section>""",
    },
    "cs/index.html": {
        "marker": "<!-- ESYLINK-PRODUCT-DEPTH -->",
        "block": """
<!-- ESYLINK-PRODUCT-DEPTH -->
<section class="max-w-6xl mx-auto px-4 py-12 bg-slate-50 rounded-2xl my-8">
  <h2 class="text-2xl font-bold text-slate-900 mb-6">云客服工作台亮点</h2>
  <ul class="grid md:grid-cols-2 gap-4 text-sm text-slate-700">
    <li class="flex gap-2"><i class="fas fa-check-circle text-green-500 mt-0.5"></i> 全渠道接入：电话、网页、微信、企微、APP</li>
    <li class="flex gap-2"><i class="fas fa-check-circle text-green-500 mt-0.5"></i> 智能排队 ACD + IVR 语音导航</li>
    <li class="flex gap-2"><i class="fas fa-check-circle text-green-500 mt-0.5"></i> 工单 CRM 联动，客户画像自动带出</li>
    <li class="flex gap-2"><i class="fas fa-check-circle text-green-500 mt-0.5"></i> 坐席监控、质检评分、话术库</li>
  </ul>
  <p class="mt-6 text-slate-600">起步价 <strong class="text-indigo-700">¥400/月</strong>，支持按坐席弹性扩容。<a href="/pricing" class="text-indigo-600 font-semibold">查看报价 →</a></p>
</section>""",
    },
    "400.html": {
        "marker": "<!-- ESYLINK-PRODUCT-DEPTH -->",
        "block": """
<!-- ESYLINK-PRODUCT-DEPTH -->
<section class="max-w-6xl mx-auto px-4 py-12">
  <h2 class="text-2xl font-bold mb-4">400 电话办理流程</h2>
  <ol class="grid md:grid-cols-4 gap-4 text-center text-sm">
    <li class="bg-indigo-50 rounded-xl p-4"><span class="text-2xl font-bold text-indigo-600">1</span><p class="mt-2 font-medium">选号</p><p class="text-slate-500">五级靓号 ¥20 起</p></li>
    <li class="bg-indigo-50 rounded-xl p-4"><span class="text-2xl font-bold text-indigo-600">2</span><p class="mt-2 font-medium">提交资质</p><p class="text-slate-500">营业执照即可</p></li>
    <li class="bg-indigo-50 rounded-xl p-4"><span class="text-2xl font-bold text-indigo-600">3</span><p class="mt-2 font-medium">审核开通</p><p class="text-slate-500">最快 1 个工作日</p></li>
    <li class="bg-indigo-50 rounded-xl p-4"><span class="text-2xl font-bold text-indigo-600">4</span><p class="mt-2 font-medium">绑定路由</p><p class="text-slate-500">手机/座机/云客服</p></li>
  </ol>
</section>""",
    },
    "pricing.html": {
        "marker": "<!-- ESYLINK-PRICING-TRUST -->",
        "block": """
<!-- ESYLINK-PRICING-TRUST -->
<div class="max-w-4xl mx-auto px-4 py-8 text-center text-sm text-slate-500">
  <p><i class="fas fa-shield-alt text-indigo-500"></i> 价格透明 · 无隐藏费用 · 7天免费试用 · 30天无理由退款</p>
  <p class="mt-2"><a href="/compare" class="text-indigo-600 font-medium">查看与容联云/环信/腾讯企点对比 →</a></p>
</div>""",
    },
    "free-trial.html": {
        "marker": "<!-- ESYLINK-WECHAT-LOGIN -->",
        "block": """
<!-- ESYLINK-WECHAT-LOGIN -->
<div id="wechat-login-section" class="max-w-md mx-auto mt-6 text-center">
  <div class="wechat-login-divider"><span>或使用微信快捷登录</span></div>
  <div id="wechat-login-btn"></div>
</div>
<script src="/js/wechat-login.js" defer></script>""",
    },
}


def enhance():
    for rel, data in PRODUCTS.items():
        p = WEB / rel
        if not p.exists():
            print(f"  skip {rel} (not found)")
            continue
        html = p.read_text(encoding="utf-8")
        if data["marker"] in html:
            print(f"  ✓ {rel} already enhanced")
            continue
        if "</main>" in html:
            html = html.replace("</main>", data["block"] + "\n</main>", 1)
        elif "</body>" in html:
            html = html.replace("</body>", data["block"] + "\n</body>", 1)
        else:
            continue
        p.write_text(html, encoding="utf-8")
        print(f"  ✓ {rel}")


if __name__ == "__main__":
    print("📦 Enhancing product pages...")
    enhance()
    print("✅ Done")
