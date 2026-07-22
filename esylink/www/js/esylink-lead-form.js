/**
 * Esylink Lead Form — 闭合企微断点
 * 在 AI 客服推企微前，先收集手机号确保线索入库
 */
(function () {
  'use strict';

  var FORM_SHOWN_KEY = '_esylink_lead_captured';

  function alreadyCaptured() {
    return sessionStorage.getItem(FORM_SHOWN_KEY) === '1';
  }

  function markCaptured() {
    sessionStorage.setItem(FORM_SHOWN_KEY, '1');
  }

  function injectStyles() {
    if (document.getElementById('esylink-lead-form-style')) return;
    var s = document.createElement('style');
    s.id = 'esylink-lead-form-style';
    s.textContent = [
      '#esylink-lead-form-overlay{display:none;position:fixed;inset:0;z-index:100000;',
      'background:rgba(0,0,0,.5);align-items:center;justify-content:center}',
      '#esylink-lead-form-overlay.open{display:flex}',
      '.esylink-lead-card{background:#fff;border-radius:16px;padding:28px 24px;',
      'max-width:380px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,.2)}',
      '.esylink-lead-card h3{font-size:18px;font-weight:700;color:#1e1b4b;margin:0 0 8px}',
      '.esylink-lead-card p{font-size:13px;color:#64748b;margin:0 0 16px}',
      '.esylink-lead-card input{width:100%;padding:10px 14px;border:1.5px solid #e2e8f0;',
      'border-radius:10px;font-size:14px;margin-bottom:10px;box-sizing:border-box}',
      '.esylink-lead-card input:focus{border-color:#4f46e5;outline:none}',
      '.esylink-lead-card button{width:100%;padding:12px;background:#4f46e5;color:#fff;',
      'border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer}',
      '.esylink-lead-card button:hover{background:#4338ca}',
      '.esylink-lead-skip{display:block;text-align:center;margin-top:10px;font-size:12px;',
      'color:#94a3b8;cursor:pointer;border:none;background:none;width:100%}',
    ].join('');
    document.head.appendChild(s);
  }

  function createOverlay() {
    var el = document.createElement('div');
    el.id = 'esylink-lead-form-overlay';
    el.innerHTML = [
      '<div class="esylink-lead-card">',
      '  <h3>📱 留下手机号，顾问立即联系</h3>',
      '  <p>填写后专属顾问将在30分钟内回复，并发送行业方案和报价</p>',
      '  <input type="text" id="esylink-lead-name" placeholder="您的姓名" autocomplete="name">',
      '  <input type="tel" id="esylink-lead-phone" placeholder="手机号（必填）" autocomplete="tel">',
      '  <input type="text" id="esylink-lead-company" placeholder="公司名称（选填）" autocomplete="organization">',
      '  <button id="esylink-lead-submit">提交并获取方案</button>',
      '  <button class="esylink-lead-skip" id="esylink-lead-skip">暂时跳过，直接咨询</button>',
      '</div>',
    ].join('\n');
    document.body.appendChild(el);
    return el;
  }

  function submitLead(name, phone, company, cb) {
    var payload = JSON.stringify({
      name: name || '网站访客',
      phone: phone,
      company: company || '',
      source: 'chat_lead_form',
      page_url: location.href,
      message: 'AI客服留资表单提交',
    });
    fetch('/api/v1/leads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payload,
    })
      .then(function (r) { return r.json(); })
      .then(function () { markCaptured(); if (cb) cb(); })
      .catch(function () { if (cb) cb(); });
  }

  function showLeadForm(onDone) {
    if (alreadyCaptured()) {
      if (onDone) onDone();
      return;
    }
    injectStyles();
    var overlay = document.getElementById('esylink-lead-form-overlay') || createOverlay();
    overlay.classList.add('open');

    document.getElementById('esylink-lead-submit').onclick = function () {
      var phone = (document.getElementById('esylink-lead-phone').value || '').trim();
      var name = (document.getElementById('esylink-lead-name').value || '').trim();
      var company = (document.getElementById('esylink-lead-company').value || '').trim();
      if (!/^1\d{10}$/.test(phone)) {
        alert('请输入正确的11位手机号');
        return;
      }
      submitLead(name, phone, company, function () {
        overlay.classList.remove('open');
        if (onDone) onDone();
      });
    };

    document.getElementById('esylink-lead-skip').onclick = function () {
      overlay.classList.remove('open');
      if (onDone) onDone();
    };
  }

  // Hook into esylinkChat.showWeCom
  function hookChat() {
    if (!window.esylinkChat) {
      setTimeout(hookChat, 500);
      return;
    }
    var orig = window.esylinkChat.showWeCom;
    window.esylinkChat.showWeCom = function () {
      showLeadForm(orig);
    };
  }

  // Expose for manual trigger
  window.esylinkLeadForm = { show: showLeadForm };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', hookChat);
  } else {
    hookChat();
  }
})();
