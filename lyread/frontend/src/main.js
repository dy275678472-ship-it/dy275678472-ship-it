import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './styles/theme.css'

const protectedRoutes = ['/workspace', '/wallet']

const routes = [
  { path: '/', component: () => import('./views/Home.vue'), meta: { title: 'LyRead AI - 让 AI 陪你写完一部长篇小说', desc: 'LyRead AI 智能小说创作平台，支持长篇小说、短故事、人物伏笔记忆与点数计费。' }},
  { path: '/login', component: () => import('./views/Login.vue'), meta: { title: '登录 - LyRead AI', desc: '登录 LyRead AI，开始智能小说创作。' }},
  { path: '/pricing', component: () => import('./views/Pricing.vue'), meta: { title: '价格 - LyRead AI', desc: 'LyRead 点数计费说明：注册送 30 点，每日免费 5 点，10 元 = 100 点。' }},
  { path: '/wallet', component: () => import('./views/Wallet.vue'), meta: { title: '我的点数 - LyRead AI', desc: '查看点数余额、领取每日免费额度与消费记录。' }},
  { path: '/workspace', component: () => import('./views/Workspace.vue'), meta: { title: '创作台 - LyRead AI', desc: '小说创作控制台。' }},
  { path: '/reader', component: () => import('./views/Workspace.vue'), meta: { title: '长篇小说 - LyRead AI', desc: '开始你的长篇小说创作。' }},
  { path: '/story', component: () => import('./views/Workspace.vue'), meta: { title: '短故事 - LyRead AI', desc: '快速生成完整短故事。' }},
  { path: '/trending', component: () => import('./views/Trending.vue'), meta: { title: '案例阅读 - LyRead AI', desc: '浏览平台生成案例。' }},
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  if (protectedRoutes.includes(to.path) && !localStorage.getItem('token')) {
    next('/login')
    return
  }
  next()
})

router.afterEach((to) => {
  const meta = to.meta || {}
  document.title = meta.title || 'LyRead AI'
  let descMeta = document.querySelector('meta[name="description"]')
  if (!descMeta) {
    descMeta = document.createElement('meta')
    descMeta.name = 'description'
    document.head.appendChild(descMeta)
  }
  descMeta.content = meta.desc || 'LyRead AI 智能小说创作平台'
})

createApp(App).use(router).mount('#app')
