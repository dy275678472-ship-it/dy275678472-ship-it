/* Esylink Page Tracking Beacon v2 — 增强埋点
 * 采集: URL/referrer/timeOnPage/scrollDepth/CTAclicks/conversions
 * 部署: 所有SEO页面通过 generate.py / generate_blog.py 自动嵌入
 */
(function(){
  var url = window.location.pathname;
  var parts = url.replace(/^\/|\/$/g, '').split('/');
  var industry = parts[1] || '';
  var scene = parts[2] || '';
  var startTime = Date.now();
  var sent = false;
  var maxScroll = 0;
  var ctaClicks = 0;
  var conversions = 0;

  // ── 滚动深度追踪 ──
  function trackScroll() {
    var scrollPct = Math.round((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100);
    if (scrollPct > maxScroll) maxScroll = Math.min(scrollPct, 100);
  }
  window.addEventListener('scroll', trackScroll, {passive: true});

  // ── CTA点击追踪 ──
  document.addEventListener('click', function(e) {
    var el = e.target.closest('a, button');
    if (!el) return;
    var href = el.getAttribute('href') || '';
    var text = (el.textContent || '').trim();
    // 转化类链接：联系/报价/试用/外呼/电话/企微登录
    if (/^\/(contact|pricing|demo|dialer|free-trial|cs|api\/v1\/leads)/.test(href) ||
        /^tel:/.test(href) ||
        /token\.kexun\.ltd/.test(href) ||
        /免费试用|免费领|获取方案|查看报价|立即试用|加企微|在线咨询/.test(text)) {
      ctaClicks++;
    }
    // 聊天按钮也算转化触点
    if (el.id === 'esylink-chat-btn' || el.closest('#esylink-chat-btn')) {
      ctaClicks++;
    }
  }, {passive: true});

  // ── 表单提交追踪 ──
  document.addEventListener('submit', function(e) {
    var form = e.target.closest('form');
    if (form && (form.action || '').includes('/api/v1/leads')) {
      conversions++;
    }
  }, {passive: true});

  // ── V8 行为线索检测: 高意向访问自动创建线索 ──
  var leadDetected = false;
  function checkLeadIntent() {
    if (leadDetected) return;
    var timeOnPage = Math.round((Date.now() - startTime) / 1000);
    // 触发条件: 停留>60s + 滚动>70%, 或 CTA点击
    var isHot = (timeOnPage > 60 && maxScroll > 70) || ctaClicks > 0;
    if (isHot) {
      leadDetected = true;
      var leadPayload = JSON.stringify({
        page_url: url,
        industry: industry,
        scene: scene,
        time_on_page: timeOnPage,
        scroll_depth: maxScroll,
        cta_clicks: ctaClicks,
        referrer: document.referrer || '',
        intent: ctaClicks > 0 ? 'hot' : (timeOnPage > 120 ? 'hot' : 'warm')
      });
      if (navigator.sendBeacon) {
        navigator.sendBeacon('/api/v1/track/lead-detect', leadPayload);
      }
    }
  }
  // 每15秒检查一次, 以及离开时检查
  setInterval(checkLeadIntent, 15000);
  window.addEventListener('beforeunload', checkLeadIntent);

  // ── 发送信标 ──
  function sendVisit() {
    if (sent) return; sent = true;
    var timeOnPage = Math.round((Date.now() - startTime) / 1000);
    var payload = JSON.stringify({
      page_url: url,
      industry: industry,
      scene: scene,
      city: parts[2] || '',
      referrer: document.referrer || '',
      time_on_page: timeOnPage,
      scroll_depth: maxScroll,
      cta_clicks: ctaClicks,
      conversions: conversions
    });

    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/v1/track/visit', payload);
    } else {
      fetch('/api/v1/track/visit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: payload,
        keepalive: true
      }).catch(function(){});
    }
  }

  // 3秒后或页面离开时发送
  setTimeout(sendVisit, 3000);
  window.addEventListener('beforeunload', sendVisit);
  window.addEventListener('pagehide', sendVisit);
})();
