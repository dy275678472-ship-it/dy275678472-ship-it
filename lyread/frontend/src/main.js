import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './styles/theme.css'
import { initAnalytics, trackPageView } from './utils/analytics'

initAnalytics()

// /story 对游客开放：页内 register-first 门闩负责转化；勿在此拦截，否则 ShortStory 游客 CTA 永不可达
const protectedRoutes = ['/workspace', '/wallet', '/admin', '/reader']

const routes = [
  { path: '/', component: () => import('./views/Home.vue'), meta: { title: 'LyRead AI - AI写小说工具 | 按章约1元 长篇续写', desc: 'LyRead AI 中文 AI 写小说平台：大纲、章纲、正文续写，人物伏笔记忆。注册送30点，约1元/章，失败全额返还。' }},
  { path: '/login', component: () => import('./views/Login.vue'), meta: { title: '登录 - LyRead AI', desc: '登录 LyRead AI，开始智能小说创作。' }},
  { path: '/pricing', component: () => import('./views/Pricing.vue'), meta: { title: 'AI写小说价格 - LyRead AI 点数计费', desc: 'LyRead 点数计费：注册送30点，每日免费5点，10元=100点，约1元/章。首充加赠20%，失败全额返还。' }},
  { path: '/wallet', component: () => import('./views/Wallet.vue'), meta: { title: '我的点数 - LyRead AI', desc: '查看点数余额、领取每日免费额度与消费记录。' }},
  { path: '/workspace', component: () => import('./views/Workspace.vue'), meta: { title: '创作台 - LyRead AI', desc: '小说创作控制台。' }},
  { path: '/reader', component: () => import('./views/Workspace.vue'), meta: { title: '长篇小说 - LyRead AI', desc: '开始你的长篇小说创作。' }},
  { path: '/story', component: () => import('./views/ShortStory.vue'), meta: { title: '短故事 - LyRead AI', desc: '快速生成完整短篇故事。' }},
  { path: '/case/:id', component: () => import('./views/CaseReader.vue'), meta: { title: '案例阅读 - LyRead AI', desc: '阅读平台 AI 生成案例。' }},
  { path: '/trending', component: () => import('./views/Trending.vue'), meta: { title: '案例阅读 - LyRead AI', desc: '浏览平台生成案例。' }},
  { path: '/admin', component: () => import('./views/Admin.vue'), meta: { title: '运营后台 - LyRead AI', desc: '管理员控制台。' }},
  // 人类走 SPA（次屏 register CTA）；完整刷新仍由 nginx 反代后端 SSR
  { path: '/faq', component: () => import('./views/Faq.vue'), meta: { title: '常见问题 - LyRead AI', desc: 'LyRead AI 常见问题：计费方式、免费试用、长篇创作、点数返还与案例说明。' }},
  { path: '/about', component: () => import('./views/About.vue'), meta: { title: '关于 LyRead AI - 智能中文小说创作平台', desc: '了解 LyRead AI：中文 AI 长篇小说创作平台，支持大纲、续写、人物伏笔记忆与按量点数计费。' }},
  { path: '/privacy', component: () => import('./views/Privacy.vue'), meta: { title: '隐私政策 - LyRead AI', desc: 'LyRead AI 隐私政策：说明我们如何收集、使用与保护您的账号、创作内容与交易信息。' }},
  { path: '/terms', component: () => import('./views/Terms.vue'), meta: { title: '用户协议 - LyRead AI', desc: 'LyRead AI 用户服务协议：账号规则、点数计费、内容规范与知识产权说明。' }},
  // 人类走 SPA（次屏 register CTA）；完整刷新仍由 nginx 反代后端 SSR；/guide/:slug 仍 SSR
  { path: '/guide', component: () => import('./views/Guide.vue'), meta: { title: 'AI写小说教程 - LyRead AI 创作指南', desc: 'AI 小说创作教程：入门开书、大纲章纲、日更续写技巧与点数成本估算。' }},
  // SPA 软 404：未知路径仍 200 壳，但页内 register-first + 继续读，避免空白 router-view
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('./views/NotFound.vue'), meta: { title: '页面未找到 - LyRead AI', desc: '页面不存在。可回首页、读案例，或免费注册领 30 点开写。' }},
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  if (protectedRoutes.includes(to.path) && !localStorage.getItem('token')) {
    // 游客拦截统一 register-first；/reader 是创作台别名，回流默认打开新建向导
    let redirect = to.fullPath
    if (to.path === '/reader') {
      const q = { ...to.query, mode: to.query.mode || 'new' }
      redirect = `/workspace?${new URLSearchParams(q).toString()}`
    }
    next({ path: '/login', query: { redirect, mode: 'register' } })
    return
  }
  next()
})

router.afterEach((to) => {
  const meta = to.meta || {}
  const title = meta.title || 'LyRead AI'
  const desc = meta.desc || 'LyRead AI 智能小说创作平台'
  document.title = title
  let descMeta = document.querySelector('meta[name="description"]')
  if (!descMeta) {
    descMeta = document.createElement('meta')
    descMeta.name = 'description'
    document.head.appendChild(descMeta)
  }
  descMeta.content = desc
  let canonical = document.querySelector('link[rel="canonical"]')
  if (!canonical) {
    canonical = document.createElement('link')
    canonical.rel = 'canonical'
    document.head.appendChild(canonical)
  }
  canonical.href = `https://lyread.cn${to.path === '/' ? '/' : to.path}`
  const setOg = (prop, content) => {
    let el = document.querySelector(`meta[property="${prop}"]`)
    if (!el) {
      el = document.createElement('meta')
      el.setAttribute('property', prop)
      document.head.appendChild(el)
    }
    el.content = content
  }
  setOg('og:title', title)
  setOg('og:description', desc)
  setOg('og:url', `https://lyread.cn${to.path === '/' ? '/' : to.path}`)
  const ogImage = document.querySelector('meta[property="og:image"]')
  if (ogImage) ogImage.content = 'https://lyread.cn/images/og-share.webp'
  trackPageView(to.fullPath, title)
})

createApp(App).use(router).mount('#app')
