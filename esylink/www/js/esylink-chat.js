/**
 * Esylink V8-lite — SEO → 在线客服 → 企微转化闭环
 * 将所有SEO流量统一引导至企微成交入口
 */
(function() {
  'use strict';

  var THRESHOLD_TIME = 40;    // 秒
  var THRESHOLD_SCROLL = 60;  // %
  var chatOpen = false;
  var chatStep = 0;
  var userIndustry = '';
  var autoTriggered = false;
  var messages = [];
  var leadCreated = false;

  // ── 意图页面检测 ──
  var path = window.location.pathname;
  var isHighIntent = /\/(pricing|demo|contact|dialer|free-trial|cs|solutions?(\/|\.)|industries(\/|\.))/.test(path);
  var isBlog = /\/blog\//.test(path);
  var isIndustry = /\/industries\//.test(path);
  var startTime = Date.now();
  var maxScroll = 0;

  // ── 滚动追踪 ──
  window.addEventListener('scroll', function() {
    var pct = Math.round((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100);
    if (pct > maxScroll) maxScroll = Math.min(pct, 100);
  }, {passive: true});

  // ── 企微二维码 ──
  var WECOM_QR = '/images/wecom-qr.png';

  // ── CSS 注入 ──
  var css = document.createElement('style');
  css.textContent = [
    '/* 聊天按钮 */',
    '#esylink-chat-btn {',
    '  position:fixed; bottom:24px; right:24px; z-index:99998;',
    '  width:56px; height:56px; border-radius:50%;',
    '  background:linear-gradient(135deg,#4f46e5,#6366f1);',
    '  color:#fff; display:flex; align-items:center; justify-content:center;',
    '  cursor:pointer; box-shadow:0 4px 20px rgba(79,70,229,.45);',
    '  transition:all .3s ease; font-size:24px; border:none;',
    '}',
    '#esylink-chat-btn:hover { transform:scale(1.08); box-shadow:0 6px 28px rgba(79,70,229,.6); }',
    '#esylink-chat-btn .chat-dot {',
    '  position:absolute; top:4px; right:4px; width:12px; height:12px;',
    '  border-radius:50%; background:#ef4444; border:2px solid #fff;',
    '  animation:chatDotPulse 2s infinite;',
    '}',
    '@keyframes chatDotPulse { 0%,100%{opacity:1} 50%{opacity:.4} }',
    '/* 脉冲波纹 */',
    '#esylink-chat-btn::before {',
    '  content:""; position:absolute; inset:-4px; border-radius:50%;',
    '  background:rgba(99,102,241,.25); animation:chatRipple 2s infinite; z-index:-1;',
    '}',
    '@keyframes chatRipple { 0%{transform:scale(1);opacity:1} 100%{transform:scale(1.6);opacity:0} }',
    '/* 聊天窗口 */',
    '#esylink-chat-window {',
    '  display:none; position:fixed; bottom:96px; right:24px; z-index:99999;',
    '  width:380px; max-width:calc(100vw - 48px); height:520px; max-height:calc(100vh - 140px);',
    '  background:#fff; border-radius:16px; box-shadow:0 8px 40px rgba(0,0,0,.18);',
    '  flex-direction:column; overflow:hidden;',
    '  animation:chatSlideUp .3s ease;',
    '}',
    '#esylink-chat-window.open { display:flex; }',
    '@keyframes chatSlideUp { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }',
    '/* 聊天头 */',
    '.chat-header {',
    '  background:linear-gradient(135deg,#4f46e5,#6366f1);',
    '  color:#fff; padding:14px 16px; display:flex; align-items:center; gap:10px;',
    '  flex-shrink:0;',
    '}',
    '.chat-header .avatar {',
    '  width:40px; height:40px; border-radius:50%; background:rgba(255,255,255,.2);',
    '  display:flex; align-items:center; justify-content:center; font-size:18px;',
    '}',
    '.chat-header .info { flex:1; }',
    '.chat-header .name { font-weight:700; font-size:15px; }',
    '.chat-header .status { font-size:12px; opacity:.8; }',
    '.chat-header .close-btn {',
    '  background:none; border:none; color:#fff; font-size:22px; cursor:pointer;',
    '  padding:0; line-height:1; opacity:.7; transition:opacity .2s;',
    '}',
    '.chat-header .close-btn:hover { opacity:1; }',
    '/* 聊天消息区 */',
    '.chat-messages {',
    '  flex:1; overflow-y:auto; padding:16px; background:#f8fafc;',
    '  display:flex; flex-direction:column; gap:10px;',
    '}',
    '.chat-messages::-webkit-scrollbar { width:4px; }',
    '.chat-messages::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:4px; }',
    '/* 消息气泡 */',
    '.chat-msg { max-width:85%; padding:10px 14px; border-radius:14px; font-size:14px; line-height:1.6; animation:msgIn .3s ease; }',
    '@keyframes msgIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }',
    '.chat-msg.bot { align-self:flex-start; background:#fff; border:1px solid #e2e8f0; border-bottom-left-radius:4px; color:#1e293b; white-space:pre-wrap; }',
    '.chat-msg.user { align-self:flex-end; background:#4f46e5; color:#fff; border-bottom-right-radius:4px; }',
    '.chat-msg .emoji { font-size:18px; }',
    '/* 快捷回复按钮 */',
    '.chat-quick-btns { display:flex; flex-wrap:wrap; gap:6px; margin-top:2px; }',
    '.chat-quick-btn {',
    '  padding:8px 14px; border-radius:20px; border:1.5px solid #4f46e5;',
    '  background:#fff; color:#4f46e5; font-size:13px; font-weight:500;',
    '  cursor:pointer; transition:all .2s; white-space:nowrap;',
    '}',
    '.chat-quick-btn:hover { background:#4f46e5; color:#fff; }',
    '.chat-quick-btn.active { background:#4f46e5; color:#fff; }',
    '/* CTA卡片 */',
    '.chat-cta-card {',
    '  background:linear-gradient(135deg,#fef3c7,#fde68a);',
    '  border-radius:12px; padding:14px; margin-top:4px;',
    '  text-align:center; border:1px solid #fcd34d;',
    '}',
    '.chat-cta-card .cta-title { font-weight:700; color:#92400e; font-size:15px; margin-bottom:8px; }',
    '.chat-cta-card .cta-btn {',
    '  display:inline-block; background:#07C160; color:#fff;',
    '  padding:10px 28px; border-radius:22px; font-size:14px; font-weight:600;',
    '  text-decoration:none; transition:all .2s;',
    '}',
    '.chat-cta-card .cta-btn:hover { background:#06ad56; transform:scale(1.03); }',
    '.chat-cta-card .cta-desc { font-size:12px; color:#92400e; margin-top:6px; opacity:.8; }',
    '/* 二维码区 */',
    '.chat-qr {',
    '  text-align:center; padding:8px 0;',
    '}',
    '.chat-qr img { width:140px; height:140px; border-radius:8px; border:2px solid #e2e8f0; }',
    '.chat-qr .qr-tip { font-size:12px; color:#64748b; margin-top:6px; }',
    '/* 输入区 */',
    '.chat-input-area {',
    '  display:flex; gap:8px; padding:12px; border-top:1px solid #e2e8f0;',
    '  background:#fff; flex-shrink:0;',
    '}',
    '.chat-input-area input {',
    '  flex:1; padding:10px 14px; border-radius:22px; border:1.5px solid #e2e8f0;',
    '  font-size:14px; outline:none; transition:border-color .2s;',
    '}',
    '.chat-input-area input:focus { border-color:#4f46e5; }',
    '.chat-input-area .send-btn {',
    '  width:40px; height:40px; border-radius:50%; background:#4f46e5;',
    '  color:#fff; border:none; font-size:16px; cursor:pointer;',
    '  display:flex; align-items:center; justify-content:center;',
    '  transition:all .2s; flex-shrink:0;',
    '}',
    '.chat-input-area .send-btn:hover { background:#4338ca; }',
    '/* 响应式 */',
    '@media(max-width:640px) {',
    '  #esylink-chat-btn { bottom:16px; right:16px; width:48px; height:48px; font-size:20px; }',
    '  #esylink-chat-window { bottom:80px; right:8px; width:calc(100vw - 16px); height:480px; border-radius:12px; }',
    '}',
    '/* 打招呼小气泡 */',
    '.chat-greet-bubble {',
    '  position:fixed; bottom:92px; right:24px; z-index:99997;',
    '  background:#fff; border-radius:12px; padding:10px 14px;',
    '  box-shadow:0 4px 16px rgba(0,0,0,.12); font-size:13px;',
    '  max-width:220px; color:#334155; line-height:1.5;',
    '  animation:greetIn .4s ease; cursor:pointer;',
    '}',
    '.chat-greet-bubble::after {',
    '  content:""; position:absolute; bottom:-8px; right:20px;',
    '  width:0; height:0; border-left:8px solid transparent;',
    '  border-right:8px solid transparent; border-top:8px solid #fff;',
    '}',
    '.chat-greet-bubble .greet-close {',
    '  position:absolute; top:4px; right:8px; background:none; border:none;',
    '  font-size:14px; color:#94a3b8; cursor:pointer; padding:0;',
    '}',
    '@keyframes greetIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }',
    '@media(max-width:640px) { .chat-greet-bubble { bottom:76px; right:8px; max-width:200px; font-size:12px; } }',
    '/* 输入框内快捷入口 */',
    '.chat-quick-row { display:flex; gap:6px; padding:6px 12px 2px; flex-wrap:wrap; }',
    '.chat-quick-chip {',
    '  padding:5px 12px; border-radius:14px; background:#f1f5f9;',
    '  border:1px solid #e2e8f0; font-size:12px; color:#475569; cursor:pointer;',
    '  transition:all .2s;',
    '}',
    '.chat-quick-chip:hover { background:#e2e8f0; }'
  ].join('\n');
  document.head.appendChild(css);

  // ── HTML 注入 ──
  var html = document.createElement('div');
  html.innerHTML = [
    '<button id="esylink-chat-btn" aria-label="在线客服">',
    '  <span class="chat-dot"></span>',
    '  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">',
    '    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    '  </svg>',
    '</button>',
    '<div id="esylink-chat-window">',
    '  <div class="chat-header">',
    '    <div class="avatar">🤖</div>',
    '    <div class="info">',
    '      <div class="name">科讯AI顾问</div>',
    '      <div class="status">在线 · 秒回</div>',
    '    </div>',
    '    <button class="close-btn" id="chat-close">×</button>',
    '  </div>',
    '  <div class="chat-messages" id="chat-messages"></div>',
    '  <div class="chat-quick-row" id="chat-quick-row" style="display:none"></div>',
    '  <div class="chat-input-area">',
    '    <input type="text" id="chat-input" placeholder="输入您的问题..." autocomplete="off">',
    '    <button class="send-btn" id="chat-send">➤</button>',
    '  </div>',
    '</div>',
  ].join('\n');
  document.body.appendChild(html);

  var chatBtn = document.getElementById('esylink-chat-btn');
  var chatWindow = document.getElementById('esylink-chat-window');
  var chatMessages = document.getElementById('chat-messages');
  var chatInput = document.getElementById('chat-input');
  var chatSend = document.getElementById('chat-send');
  var chatClose = document.getElementById('chat-close');
  var chatQuickRow = document.getElementById('chat-quick-row');

  // ── 打开/关闭 ──
  chatBtn.onclick = function() { toggleChat(); };
  chatClose.onclick = function() { closeChat(); };

  function toggleChat() {
    if (chatOpen) { closeChat(); return; }
    openChat();
  }

  function openChat() {
    chatOpen = true;
    chatWindow.classList.add('open');
    chatBtn.style.display = 'none';
    hideGreet();
    if (chatStep === 0) { startConversation(); }
    chatInput.focus();
  }

  function closeChat() {
    chatOpen = false;
    chatWindow.classList.remove('open');
    chatBtn.style.display = '';
  }

  // ── 对话引擎 ──
  function addBotMsg(text) {
    var div = document.createElement('div');
    div.className = 'chat-msg bot';
    div.innerHTML = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function addUserMsg(text) {
    var div = document.createElement('div');
    div.className = 'chat-msg user';
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function addQuickButtons(buttons) {
    chatQuickRow.style.display = 'flex';
    chatQuickRow.innerHTML = '';
    buttons.forEach(function(b) {
      var btn = document.createElement('span');
      btn.className = 'chat-quick-chip';
      btn.textContent = b.label;
      btn.onclick = function() {
        b.action();
        chatQuickRow.style.display = 'none';
      };
      chatQuickRow.appendChild(btn);
    });
  }

  function showTyping(cb) {
    var div = document.createElement('div');
    div.className = 'chat-msg bot';
    div.innerHTML = '<span style="display:flex;gap:4px;padding:4px 0;"><span style="width:6px;height:6px;border-radius:50%;background:#94a3b8;animation:typing 1.4s infinite;"></span><span style="width:6px;height:6px;border-radius:50%;background:#94a3b8;animation:typing 1.4s .2s infinite;"></span><span style="width:6px;height:6px;border-radius:50%;background:#94a3b8;animation:typing 1.4s .4s infinite;"></span></span>';
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    setTimeout(function() {
      div.remove();
      cb();
    }, 800 + Math.random() * 600);
  }

  function startConversation() {
    chatStep = 1;
    // 根据页面类型定制开场白
    var greet;
    if (isHighIntent) {
      greet = '👋 您好！看到您在看我们的方案报价，需要我帮您快速匹配最适合的行业方案吗？';
    } else if (isBlog) {
      greet = '👋 您好！看完这篇文章，需要了解具体的行业方案和报价吗？我可以帮您快速匹配。';
    } else if (isIndustry) {
      greet = '👋 您好！想了解这个行业的详细方案和案例吗？我可以帮您对接专业顾问。';
    } else {
      greet = '👋 您好！需要AI外呼/云客服方案吗？我可以帮您快速匹配最适合的解决方案。';
    }
    addBotMsg(greet);
    setTimeout(function() {
      addQuickButtons([
        {label: '💰 了解报价', action: function() { handleUserInput('了解报价'); }},
        {label: '🏭 按行业推荐', action: function() { handleUserInput('按行业推荐'); }},
        {label: '📞 加企微咨询', action: function() { showWeCom(); }},
      ]);
    }, 600);
  }

  // ── V9 Chat Session ──
  var chatSessionId = 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 8);
  var v9Enabled = true;  // 设为false可降级到静态规则

  function handleUserInput(text) {
    addUserMsg(text);
    chatQuickRow.style.display = 'none';

    if (v9Enabled) {
      // ── V9-lite: 实时AI对话 ──
      showTyping(function() {
        fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({message: text, session_id: chatSessionId})
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
          var reply = data.reply || '好的，我让顾问联系您。';
          addBotMsg(reply);

          // AI判断该推企微
          if (data.transfer || data.v9_should_push) {
            setTimeout(function() {
              addBotMsg('📱 <strong>加企微获取完整方案和报价</strong>：');
              setTimeout(function() { showWeCom(); }, 300);
            }, 500);
          }

          // 高意向 → 自动创建线索
          if (data.v9_intent && data.v9_intent.level === 'hot' && !leadCreated) {
            createLeadFromAI(data.v9_intent);
          }
        })
        .catch(function(err) {
          console.error('V9 chat error:', err);
          // 降级到静态规则
          addBotMsg('好的，为了更好地为您服务，请选择您的行业 👇');
          addQuickButtons([
            {label: '🏦 金融', action: function() { selectIndustry('金融'); }},
            {label: '📚 教育', action: function() { selectIndustry('教育'); }},
            {label: '🛒 电商', action: function() { selectIndustry('电商'); }},
            {label: '🏥 医疗', action: function() { selectIndustry('医疗'); }},
            {label: '💼 其他', action: function() { selectIndustry('其他'); }},
          ]);
        });
      });
      return;
    }

    // ── 静态规则降级 ──
    var lower = text.toLowerCase();

    if (/报价|价格|多少钱|费用|收费|pricing/i.test(lower)) {
      showTyping(function() {
        addBotMsg('我们的方案根据行业和规模定制，价格从<span style="color:#4f46e5;font-weight:700;">几千到几万/年</span>不等。<br><br>具体报价需要根据您的需求匹配，请告诉我您的行业？');
        addQuickButtons([
          {label: '🏦 金融', action: function() { selectIndustry('金融'); }},
          {label: '📚 教育', action: function() { selectIndustry('教育'); }},
          {label: '🛒 电商', action: function() { selectIndustry('电商'); }},
          {label: '🏥 医疗', action: function() { selectIndustry('医疗'); }},
          {label: '💼 其他行业', action: function() { selectIndustry('其他'); }},
        ]);
      });
    } else if (/行业|推荐|方案|solution/i.test(lower)) {
      showTyping(function() {
        addBotMsg('我们覆盖<strong>13大行业、22个细分场景</strong>的AI外呼方案：<br><br>• 🏦 金融催收 / 信用卡提醒<br>• 📚 教育招生 / 试听转化<br>• 🛒 电商弃购挽回<br>• 🏥 医疗复诊回访<br>• 🏠 房产看房邀约<br><br>请问您的行业是？');
        addQuickButtons([
          {label: '🏦 金融', action: function() { selectIndustry('金融'); }},
          {label: '📚 教育', action: function() { selectIndustry('教育'); }},
          {label: '🛒 电商', action: function() { selectIndustry('电商'); }},
          {label: '🏥 医疗', action: function() { selectIndustry('医疗'); }},
          {label: '💼 其他', action: function() { selectIndustry('其他'); }},
        ]);
      });
    } else if (/金融|finance/i.test(lower)) {
      selectIndustry('金融');
    } else if (/教育|edu/i.test(lower)) {
      selectIndustry('教育');
    } else if (/电商|ecomm/i.test(lower)) {
      selectIndustry('电商');
    } else if (/医疗|health/i.test(lower)) {
      selectIndustry('医疗');
    } else if (/催收|loan|credit/i.test(lower)) {
      selectIndustry('金融');
    } else if (/加企微|加微信|联系|咨询|顾问|人工/i.test(lower)) {
      showWeCom();
    } else if (/免费|试用|demo/i.test(lower)) {
      showTyping(function() {
        addBotMsg('好的！我们提供<strong>免费试用</strong>。请添加企业微信，AI销售顾问将为您开通试用账号并演示功能 👇');
        setTimeout(function() { showWeCom(); }, 800);
      });
    } else {
      // 通用回复 → 引导行业选择
      showTyping(function() {
        addBotMsg('好的，为了更好地为您服务，请选择您的行业，我将推荐最匹配的方案 👇');
        addQuickButtons([
          {label: '🏦 金融', action: function() { selectIndustry('金融'); }},
          {label: '📚 教育', action: function() { selectIndustry('教育'); }},
          {label: '🛒 电商', action: function() { selectIndustry('电商'); }},
          {label: '🏥 医疗', action: function() { selectIndustry('医疗'); }},
          {label: '💼 其他', action: function() { selectIndustry('其他'); }},
        ]);
      });
    }
  }

  function selectIndustry(industry) {
    userIndustry = industry;
    var industryMap = {
      '金融': { page: '/industries/finance', emoji: '🏦', scene: '金融催收/信用卡提醒' },
      '教育': { page: '/industries/education', emoji: '📚', scene: '招生外呼/试听转化' },
      '电商': { page: '/industries/ecommerce', emoji: '🛒', scene: '弃购挽回/会员唤醒' },
      '医疗': { page: '/industries/healthcare', emoji: '🏥', scene: '复诊回访/预约提醒' },
      '其他': { page: '/solutions', emoji: '💼', scene: '通用方案' },
    };
    var info = industryMap[industry] || industryMap['其他'];

    addUserMsg(industry);
    showTyping(function() {
      addBotMsg(
        info.emoji + ' <strong>' + industry + '行业</strong>方案已匹配！<br><br>' +
        '✅ 适用场景：' + info.scene + '<br>' +
        '✅ 已服务200+企业客户<br>' +
        '✅ 支持免费试用 + 专属顾问<br><br>' +
        '👉 <a href="' + info.page + '" target="_blank" style="color:#4f46e5;text-decoration:underline;">查看' + industry + '行业详细方案</a>'
      );
      setTimeout(function() {
        addBotMsg('📱 <strong>添加企业微信，获取专属报价和免费试用</strong>：');
        setTimeout(function() { showWeCom(); }, 300);
      }, 400);
    });

    // 创建线索
    createLead(industry);
  }

  function createLeadFromAI(intentData) {
    if (leadCreated) return;
    leadCreated = true;
    var leadData = {
      name: 'Chat AI-HOT-' + (intentData.level || 'hot'),
      phone: '',
      company: '',
      industry: intentData.industry || '',
      scene: '',
      city: '',
      message: 'V9 AI判定高意向 | 评分:' + (intentData.score || 0),
      source: 'v9_chat_ai',
      page_url: window.location.href,
    };
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/v1/leads', JSON.stringify(leadData));
    }
  }

  function showWeCom() {
    chatStep = 99;
    chatQuickRow.style.display = 'none';
    
    addBotMsg(
      '<div class="chat-qr">' +
      '<img src="' + WECOM_QR + '" alt="企业微信二维码" onerror="this.parentElement.innerHTML=\'<div style=\\\'padding:20px;text-align:center;color:#64748b;\\\'><p style=\\\'font-size:28px;\\\'>📱</p><p>请搜索企业微信</p><p style=\\\'color:#4f46e5;font-weight:700;font-size:16px;\\\'>科讯软件</p></div>\'">' +
      '<div class="qr-tip">📱 扫码添加企业微信 · AI销售顾问在线</div>' +
      '</div>'
    );

    setTimeout(function() {
      addBotMsg(
        '<div class="chat-cta-card">' +
        '<div class="cta-title">🎯 扫码添加后您将获得：</div>' +
        '<div style="text-align:left;font-size:13px;color:#475569;margin:8px 0;line-height:1.8;">' +
        '✅ <strong>专属行业报价</strong><br>' +
        '✅ <strong>免费试用账号</strong><br>' +
        '✅ <strong>1v1方案定制</strong><br>' +
        '✅ <strong>同行案例参考</strong>' +
        '</div>' +
        '<a href="javascript:void(0)" class="cta-btn" onclick="var m=document.createElement(\'div\');m.innerHTML=\'<div style=position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:99999;display:flex;align-items:center;justify-content:center onclick=this.remove()><div style=background:white;border-radius:24px;padding:24px;text-align:center;max-width:280px><img src=\'+WECOM_QR+\' alt=微信 style=width:200px;height:200px;border-radius:12px;margin:0 auto><p style=color:#64748b;font-size:13px;margin-top:8px>扫码添加企业微信</p><p style=color:#94a3b8;font-size:11px>AI销售顾问 · 30分钟内回复</p></div></div>\';document.body.appendChild(m.firstChild)">打开微信添加</a>' +
        '<div class="cta-desc">AI销售顾问 30分钟内回复</div>' +
        '</div>'
      );
    }, 400);
  }

  function createLead(industry) {
    if (leadCreated) return;
    leadCreated = true;

    var timeOnPage = Math.round((Date.now() - startTime) / 1000);
    var leadData = {
      name: 'Chat访客-' + (industry || '未知'),
      phone: '',
      company: '',
      industry: PinyinMap[industry] || '',
      scene: '',
      city: '',
      message: '在线客服对话 | 停留' + timeOnPage + 's 滚动' + maxScroll + '% | 行业:' + industry,
      source: 'chat_widget',
      page_url: window.location.href,
      lead_score: timeOnPage > 60 ? 85 : 65,
    };
    
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/v1/leads', JSON.stringify(leadData));
    } else {
      fetch('/api/v1/leads', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(leadData),
      }).catch(function(){});
    }
  }

  var PinyinMap = {
    '金融': 'finance', '教育': 'education', '电商': 'ecommerce',
    '医疗': 'healthcare', '房产': 'real-estate', '保险': 'insurance',
    '政务': 'government', 'SaaS': 'saas', '其他': '',
  };

  // ── 输入发送 ──
  function sendInput() {
    var text = chatInput.value.trim();
    if (!text) return;
    chatInput.value = '';
    handleUserInput(text);
  }
  chatSend.onclick = sendInput;
  chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') { e.preventDefault(); sendInput(); }
  });

  // ── 自动触发 ──
  function checkAutoTrigger() {
    if (autoTriggered || chatOpen) return;
    var timeOnPage = Math.round((Date.now() - startTime) / 1000);
    var shouldTrigger = false;

    if (isHighIntent) {
      shouldTrigger = timeOnPage > 25;  // 高意图页面：25秒触发
    } else if (maxScroll > THRESHOLD_SCROLL) {
      shouldTrigger = true;
    } else if (timeOnPage > THRESHOLD_TIME) {
      shouldTrigger = true;
    }

    if (shouldTrigger) {
      autoTriggered = true;
      showGreetBubble();
    }
  }

  // 每10秒检查一次
  setInterval(checkAutoTrigger, 10000);

  // ── 打招呼气泡 ──
  var greetBubble = null;
  function showGreetBubble() {
    if (greetBubble) return;
    greetBubble = document.createElement('div');
    greetBubble.className = 'chat-greet-bubble';
    greetBubble.innerHTML = [
      '<button class="greet-close" id="greet-close">×</button>',
      '💬 需要了解行业方案<br>和专属报价吗？',
    ].join('\n');
    greetBubble.onclick = function(e) {
      if (e.target.id === 'greet-close') { hideGreet(); return; }
      openChat();
    };
    document.body.appendChild(greetBubble);

    document.getElementById('greet-close').onclick = function(e) {
      e.stopPropagation();
      hideGreet();
    };

    // 30秒后自动消失
    setTimeout(function() { hideGreet(); }, 30000);
  }

  function hideGreet() {
    if (greetBubble) { greetBubble.remove(); greetBubble = null; }
  }

  // ── 点击窗口外关闭（仅移动端） ──
  document.addEventListener('click', function(e) {
    if (!chatOpen) return;
    if (window.innerWidth > 640) return;
    if (!chatWindow.contains(e.target) && e.target !== chatBtn) {
      closeChat();
    }
  });

  // 暴露API给外部调用（右下角企微按钮）
  window.esylinkChat = { showWeCom: showWeCom };

})();
