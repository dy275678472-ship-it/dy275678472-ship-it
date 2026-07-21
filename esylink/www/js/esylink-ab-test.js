/**
 * Esylink A/B Test Framework
 * 首屏标题 / CTA 文案自动分流，结果上报 analytics
 */
(function () {
  'use strict';

  var STORAGE_KEY = '_esylink_ab';
  var TESTS = {
    hero_cta: {
      variants: [
        { id: 'A', text: '免费试用 AI 外呼', href: '/free-trial.html?ab=A' },
        { id: 'B', text: '预约 15 分钟演示', href: '/contact?ab=B' },
      ],
      selector: 'a.bg-white.text-indigo-700, a[href*="free-trial"]',
    },
  };

  function getBucket(testName) {
    var stored = {};
    try { stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch (e) {}
    if (stored[testName]) return stored[testName];
    var bucket = Math.random() < 0.5 ? 'A' : 'B';
    stored[testName] = bucket;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
    return bucket;
  }

  function report(testName, variantId, event) {
    var payload = JSON.stringify({
      test: testName,
      variant: variantId,
      event: event,
      page_url: location.pathname,
    });
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/v1/track/intent', payload);
    }
  }

  function runHeroCtaTest() {
    if (location.pathname !== '/' && location.pathname !== '/index.html') return;
    var test = TESTS.hero_cta;
    var bucket = getBucket('hero_cta');
    var variant = test.variants.find(function (v) { return v.id === bucket; });
    if (!variant) return;

    var links = document.querySelectorAll('a.bg-white.text-indigo-700');
    links.forEach(function (a) {
      if (a.textContent.indexOf('免费试用') !== -1 || a.textContent.indexOf('试用') !== -1) {
        a.textContent = variant.text;
        a.setAttribute('href', variant.href);
        a.addEventListener('click', function () {
          report('hero_cta', variant.id, 'click');
        });
      }
    });
    report('hero_cta', variant.id, 'impression');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runHeroCtaTest);
  } else {
    runHeroCtaTest();
  }
})();
