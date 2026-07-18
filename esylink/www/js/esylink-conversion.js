/**
 * 易连云通信 — 转化优化组件
 * 悬浮咨询按钮 + 退出意图弹窗 + 浏览时长触发 + 信任信号
 */
(function() {
  'use strict';

  // ── 检测 V8-lite 聊天组件是否已加载 ──
  var hasChat = !!document.getElementById('esylink-chat-btn');

  // ==================== 1. 悬浮咨询按钮 ====================
  // 如果已加载聊天组件，不重复创建按钮；否则创建旧版按钮
  var btn = null;
  if (!hasChat) {
    btn = document.createElement('div');
    btn.id = 'esylink-float-btn';
    btn.innerHTML = '<div class="float-pulse"></div><i class="fas fa-headset"></i><span class="float-label">在线咨询</span>';
    btn.onclick = function() { window.location.href = '/contact.html'; };
  }

  // ── 统一跳转：优先打开聊天，备用跳转 /contact ──
  function openContact() {
    if (hasChat) {
      var chatBtn = document.getElementById('esylink-chat-btn');
      if (chatBtn) { chatBtn.click(); return; }
    }
    window.location.href = '/contact.html';
  }

  var style = document.createElement('style');
  style.textContent = `
    #esylink-float-btn {
      position: fixed; bottom: 24px; right: 24px; z-index: 9999;
      width: 56px; height: 56px; border-radius: 50%;
      background: linear-gradient(135deg, #4f46e5, #6366f1);
      color: #fff; display: flex; align-items: center; justify-content: center;
      cursor: pointer; box-shadow: 0 4px 16px rgba(79,70,229,.4);
      transition: all .3s ease; font-size: 22px;
    }
    #esylink-float-btn:hover {
      transform: scale(1.08); box-shadow: 0 6px 24px rgba(79,70,229,.55);
      width: auto; border-radius: 28px; padding: 0 20px; gap: 8px;
    }
    #esylink-float-btn .float-label { display: none; font-size: 14px; font-weight: 600; white-space: nowrap; }
    #esylink-float-btn:hover .float-label { display: inline; }
    .float-pulse {
      position: absolute; width: 56px; height: 56px; border-radius: 50%;
      background: rgba(99,102,241,.35); animation: floatPulse 2s infinite;
    }
    @keyframes floatPulse {
      0% { transform: scale(1); opacity: 1; }
      100% { transform: scale(1.8); opacity: 0; }
    }
    @media (max-width: 768px) {
      #esylink-float-btn { bottom: 16px; right: 16px; width: 48px; height: 48px; font-size: 18px; }
      .float-pulse { width: 48px; height: 48px; }
    }

    /* ==================== 2. 退出意图弹窗 ==================== */
    #esylink-exit-popup {
      display: none; position: fixed; inset: 0; z-index: 99999;
      background: rgba(0,0,0,.55); backdrop-filter: blur(4px);
      align-items: center; justify-content: center;
    }
    #esylink-exit-popup.active { display: flex; }
    .exit-dialog {
      background: #fff; border-radius: 20px; padding: 36px 32px 28px;
      max-width: 420px; width: 90%; text-align: center;
      box-shadow: 0 24px 64px rgba(0,0,0,.25); animation: exitSlideUp .4s ease;
      position: relative;
    }
    @keyframes exitSlideUp {
      from { transform: translateY(40px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    .exit-dialog h3 { font-size: 22px; font-weight: 800; color: #1e1b4b; margin: 0 0 8px; }
    .exit-dialog .exit-sub { color: #64748b; font-size: 14px; margin-bottom: 20px; line-height: 1.6; }
    .exit-benefits { display: flex; gap: 12px; justify-content: center; margin-bottom: 20px; flex-wrap: wrap; }
    .exit-benefit { background: #eef2ff; border-radius: 10px; padding: 10px 14px; font-size: 13px; color: #4338ca; font-weight: 600; display: flex; align-items: center; gap: 6px; }
    .exit-dialog .exit-cta {
      display: block; background: linear-gradient(135deg, #4f46e5, #7c3aed);
      color: #fff; padding: 14px 32px; border-radius: 12px; font-size: 16px;
      font-weight: 700; text-decoration: none; transition: transform .2s, box-shadow .2s;
      box-shadow: 0 4px 16px rgba(79,70,229,.35);
    }
    .exit-dialog .exit-cta:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(79,70,229,.5); }
    .exit-close {
      position: absolute; top: 12px; right: 16px; background: none; border: none;
      font-size: 22px; color: #94a3b8; cursor: pointer; line-height: 1;
    }
    .exit-close:hover { color: #475569; }
    .exit-nothanks { display: block; margin-top: 14px; font-size: 13px; color: #94a3b8; cursor: pointer; border: none; background: none; }
    .exit-nothanks:hover { color: #64748b; }

    /* ==================== 3. 浏览时长触发提示 ==================== */
    #esylink-time-tip {
      display: none; position: fixed; bottom: 96px; right: 24px; z-index: 9998;
      background: #fff; border-radius: 12px; padding: 12px 18px;
      box-shadow: 0 8px 32px rgba(0,0,0,.12); font-size: 13px; color: #334155;
      max-width: 240px; animation: exitSlideUp .4s ease;
    }
    #esylink-time-tip .tip-arrow {
      position: absolute; bottom: -6px; right: 20px; width: 12px; height: 12px;
      background: #fff; transform: rotate(45deg); box-shadow: 2px 2px 4px rgba(0,0,0,.06);
    }
    #esylink-time-tip.active { display: block; }
    @media (max-width: 768px) {
      #esylink-time-tip { bottom: 80px; right: 8px; }
    }
  `;

  document.head.appendChild(style);
  if (btn) document.body.appendChild(btn);

  // ==================== 退出意图弹窗 ====================
  var exitPopup = document.createElement('div');
  exitPopup.id = 'esylink-exit-popup';
  exitPopup.innerHTML = `
    <div class="exit-dialog">
      <button class="exit-close" onclick="document.getElementById('esylink-exit-popup').classList.remove('active')">&times;</button>
      <h3>🎯 等一下！专属方案免费领</h3>
      <p class="exit-sub">留下联系方式，专业顾问1对1为您定制<br>最优云通信方案，限时免费报价</p>
      <div class="exit-benefits">
        <span class="exit-benefit"><i class="fas fa-check-circle"></i> 免费方案</span>
        <span class="exit-benefit"><i class="fas fa-check-circle"></i> 1对1服务</span>
        <span class="exit-benefit"><i class="fas fa-check-circle"></i> 24h响应</span>
      </div>
      <a href="javascript:void(0)" class="exit-cta" onclick="var c=document.querySelector('#esylink-chat-btn');if(c)c.click();else window.location.href='/contact.html';">立即获取专属方案 →</a>
      <button class="exit-nothanks" onclick="document.getElementById('esylink-exit-popup').classList.remove('active')">暂时不需要，谢谢</button>
    </div>
  `;
  document.body.appendChild(exitPopup);

  var exitShown = false;
  var exitTimer = null;

  function showExitPopup() {
    if (exitShown) return;
    exitShown = true;
    exitPopup.classList.add('active');
  }

  document.addEventListener('mouseout', function(e) {
    if (e.clientY <= 5 && !exitShown) {
      showExitPopup();
    }
  });

  // Mobile: 即将离开时（页面切换前）触发
  document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
      exitTimer = setTimeout(function() {
        if (document.hidden && !exitShown) showExitPopup();
      }, 3000);
    } else {
      if (exitTimer) clearTimeout(exitTimer);
    }
  });

  // 关闭弹窗 — 点击背景
  exitPopup.addEventListener('click', function(e) {
    if (e.target === exitPopup) exitPopup.classList.remove('active');
  });

  // ==================== 3. 浏览时长触发提示 ====================
  var timeTip = document.createElement('div');
  timeTip.id = 'esylink-time-tip';
  timeTip.innerHTML = '<div class="tip-arrow"></div>💡 看了这么久，不如聊聊您的需求？<br><a href="javascript:void(0)" onclick="var c=document.querySelector(\'#esylink-chat-btn\');if(c)c.click();else window.location.href=\'/contact.html\';" style="color:#4f46e5;font-weight:600;margin-top:4px;display:inline-block;">免费咨询 →</a>';
  document.body.appendChild(timeTip);

  var tipShown = false;
  setTimeout(function() {
    if (!tipShown && !exitShown) {
      tipShown = true;
      timeTip.classList.add('active');
      setTimeout(function() { timeTip.classList.remove('active'); }, 8000);
    }
  }, 25000); // 25秒后显示

  // ==================== 4. 信任信号 — 页面底部动态计数器 ====================
  // 仅在首页、产品页显示
  var trustPages = ['/', '/index.html', '/cloud-cs.html', '/ai-voice.html', '/400.html', '/pricing.html', '/dialer/', '/free-trial.html'];
  var currentPath = window.location.pathname;
  if (trustPages.indexOf(currentPath) !== -1 || currentPath === '/' || currentPath.endsWith('/')) {
    // 在hero区域或第一个section后注入信任条
    var insertAfter = document.querySelector('main section:first-of-type, main > div:first-of-type, .hero-gradient + div, main');
    if (insertAfter) {
      var baseCount = Math.floor(Math.random() * 200) + 800;
      var trustBar = document.createElement('div');
      trustBar.style.cssText = 'text-align:center;padding:16px 0;background:#f8fafc;border-bottom:1px solid #e2e8f0;font-size:14px;color:#64748b;';
      trustBar.innerHTML = '<span style="display:inline-flex;align-items:center;gap:6px;">🟢 <strong style="color:#16a34a;">' + baseCount + '+</strong> 企业正在使用易连云通信  ·  <strong style="color:#4f46e5;">98%</strong> 客户满意度  ·  覆盖全国 <strong style="color:#4f46e5;">52</strong> 城</span>';
      insertAfter.parentNode.insertBefore(trustBar, insertAfter);
    }
  }
})();
