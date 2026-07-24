/** 站点分析：百度统计 + GA4（通过环境变量注入 ID）；无 ID 时一方 /behavior/track 兜底 */

const BAIDU_ID = (import.meta.env.VITE_BAIDU_TONGJI_ID || '').trim()
const GA4_ID = (import.meta.env.VITE_GA4_MEASUREMENT_ID || '').trim()

const FIRST_PARTY_CATEGORIES = new Set([
  'conversion',
  'funnel',
  'auth',
  'monetization',
  'engagement',
])

let loaded = false

function hasThirdParty() {
  return !!(BAIDU_ID || GA4_ID)
}

function loadScripts() {
  if (loaded || typeof window === 'undefined') return
  loaded = true

  if (BAIDU_ID) {
    window._hmt = window._hmt || []
    const s = document.createElement('script')
    s.async = true
    s.src = `https://hm.baidu.com/hm.js?${BAIDU_ID}`
    document.head.appendChild(s)
  }

  if (GA4_ID) {
    const g = document.createElement('script')
    g.async = true
    g.src = `https://www.googletagmanager.com/gtag/js?id=${GA4_ID}`
    document.head.appendChild(g)
    window.dataLayer = window.dataLayer || []
    window.gtag = function gtag() { window.dataLayer.push(arguments) }
    window.gtag('js', new Date())
    window.gtag('config', GA4_ID, { send_page_view: false })
  }
}

/** 无第三方 ID 时，把关键转化事件落到一方行为接口（占位友好，不丢漏斗信号） */
function trackFirstParty(name, params = {}) {
  if (typeof window === 'undefined') return
  if (hasThirdParty()) return
  const category = String(params.category || 'site')
  if (!FIRST_PARTY_CATEGORIES.has(category)) return
  try {
    const q = new URLSearchParams({
      content_id: String(name || 'event').slice(0, 120),
      content_type: 'event',
      action: category.slice(0, 40),
      from_source: String(params.label || params.page_path || '').slice(0, 120),
      stay_time: String(Number(params.value) || 0),
    })
    const url = `/behavior/track?${q}`
    if (navigator.sendBeacon) {
      navigator.sendBeacon(url)
    } else {
      fetch(url, { method: 'POST', keepalive: true }).catch(() => {})
    }
  } catch {
    /* ignore beacon errors */
  }
}

export function initAnalytics() {
  loadScripts()
}

export function analyticsConfigured() {
  return hasThirdParty()
}

export function trackPageView(path, title) {
  loadScripts()
  if (BAIDU_ID && window._hmt) {
    window._hmt.push(['_trackPageview', path])
  }
  if (GA4_ID && window.gtag) {
    window.gtag('event', 'page_view', {
      page_path: path,
      page_title: title || document.title,
    })
  }
  trackFirstParty('page_view', { category: 'engagement', label: path, page_path: path })
}

export function trackEvent(name, params = {}) {
  loadScripts()
  if (BAIDU_ID && window._hmt) {
    window._hmt.push(['_trackEvent', params.category || 'site', name, params.label || '', params.value || 0])
  }
  if (GA4_ID && window.gtag) {
    window.gtag('event', name, params)
  }
  trackFirstParty(name, params)
}
