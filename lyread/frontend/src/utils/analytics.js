/** 站点分析：百度统计 + GA4（通过环境变量注入 ID） */

const BAIDU_ID = import.meta.env.VITE_BAIDU_TONGJI_ID || ''
const GA4_ID = import.meta.env.VITE_GA4_MEASUREMENT_ID || ''

let loaded = false

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

export function initAnalytics() {
  loadScripts()
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
}

export function trackEvent(name, params = {}) {
  loadScripts()
  // 无第三方 ID 时仍写入内存缓冲，避免构建期 DCE 掉埋点字面量，便于沙箱/转化漏斗本地核对
  if (typeof window !== 'undefined') {
    const buf = (window.__lyreadEvents = window.__lyreadEvents || [])
    if (buf.length < 200) {
      buf.push({
        name,
        category: params.category || 'site',
        label: params.label || '',
        value: params.value || 0,
        t: Date.now(),
      })
    }
  }
  if (BAIDU_ID && window._hmt) {
    window._hmt.push(['_trackEvent', params.category || 'site', name, params.label || '', params.value || 0])
  }
  if (GA4_ID && window.gtag) {
    window.gtag('event', name, params)
  }
}
