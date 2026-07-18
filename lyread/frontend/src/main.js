import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './styles/theme.css'
import { initAnalytics, trackPageView } from './utils/analytics'

initAnalytics()

const protectedRoutes = ['/workspace', '/wallet', '/admin', '/reader', '/story']

const routes = [
  { path: '/', component: () => import('./views/Home.vue'), meta: { title: 'LyRead AI - 让 AI 陪你写完一部长篇小说', desc: 'LyRead AI 智能小说创作平台，支持长篇小说、短故事、人物伏笔记忆与点数计费。' }},
  { path: '/login', component: () => import('./views/Login.vue'), meta: { title: '登录 - LyRead AI', desc: '登录 LyRead AI，开始智能小说创作。' }},
  { path: '/pricing', component: () => import('./views/Pricing.vue'), meta: { title: '价格 - LyRead AI', desc: 'LyRead 点数计费说明：注册送 30 点，每日免费 5 点，10 元 = 100 点。' }},
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
    next({ path: '/login', query: { redirect: to.fullPath } })
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
  if (ogImage) ogImage.content = 'https://lyread.cn/images/og-share.png'
  trackPageView(to.fullPath, title)
})

createApp(App).use(router).mount('#app')
