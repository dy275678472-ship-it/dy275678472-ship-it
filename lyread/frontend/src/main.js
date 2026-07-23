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
