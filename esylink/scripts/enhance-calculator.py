#!/usr/bin/env python3
"""P1: Add ROI calculator lead capture → /api/v1/leads."""
from pathlib import Path

WEB = Path("/var/www/esylink")
CALC = WEB / "calculator.html"

LEAD_BLOCK = """
<!-- ESYLINK-CALC-LEAD -->
<div id="calc-lead-form" class="mt-8 bg-white rounded-2xl border border-indigo-100 p-6 shadow-sm">
  <h3 class="text-lg font-bold text-slate-900 mb-2">获取专属 ROI 报告</h3>
  <p class="text-sm text-slate-500 mb-4">填写手机号，顾问将发送基于您参数的节省测算报告</p>
  <div class="flex flex-col sm:flex-row gap-3">
    <input type="tel" id="calc-lead-phone" placeholder="手机号" class="flex-1 px-4 py-3 border border-slate-200 rounded-lg" maxlength="11">
    <button type="button" id="calc-lead-submit" class="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700">发送报告</button>
  </div>
  <p id="calc-lead-msg" class="text-sm mt-2 hidden"></p>
</div>
<script>
(function(){
  var btn=document.getElementById('calc-lead-submit');
  if(!btn)return;
  btn.onclick=function(){
    var phone=(document.getElementById('calc-lead-phone').value||'').trim();
    var msg=document.getElementById('calc-lead-msg');
    if(!/^1\\d{10}$/.test(phone)){msg.textContent='请输入正确手机号';msg.className='text-sm mt-2 text-red-500';return;}
    var agents=document.getElementById('agents')?document.getElementById('agents').value:'';
    var savings=document.getElementById('savings')?document.getElementById('savings').textContent:'';
    var roi=document.getElementById('roi')?document.getElementById('roi').textContent:'';
    fetch('/api/v1/leads',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
      name:'ROI计算器访客',phone:phone,source:'roi_calculator',
      page_url:location.href,
      message:'坐席:'+agents+' 节省:'+savings+' ROI:'+roi
    })}).then(function(){msg.textContent='已提交，顾问30分钟内联系您';msg.className='text-sm mt-2 text-green-600';})
    .catch(function(){msg.textContent='提交失败，请拨打 021-67173000';msg.className='text-sm mt-2 text-amber-600';});
  };
})();
</script>"""

MARKER = "<!-- ESYLINK-CALC-LEAD -->"


def main():
    if not CALC.exists():
        print("calculator.html not found")
        return
    html = CALC.read_text(encoding="utf-8")
    if MARKER in html:
        print("✓ calculator already enhanced")
        return
    # Insert before comparison table or footer
    if "<!-- Comparison table -->" in html:
        html = html.replace("<!-- Comparison table -->", LEAD_BLOCK + "\n<!-- Comparison table -->", 1)
    elif "</section>" in html:
        html = html.replace("</section>", LEAD_BLOCK + "\n</section>", 1)
    else:
        html = html.replace("</body>", LEAD_BLOCK + "\n</body>", 1)
    # Fix 科讯 → 易连云通信 in calculator
    html = html.replace("科讯成本", "易连云成本")
    CALC.write_text(html, encoding="utf-8")
    print("✅ calculator.html enhanced with leads API")


if __name__ == "__main__":
    main()
