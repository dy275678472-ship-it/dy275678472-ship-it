<template>
  <div class="home">
    <section class="hero">
      <img :src="images.hero" alt="" class="hero-bg" aria-hidden="true" fetchpriority="high" loading="eager" decoding="async" width="1920" height="600" />
      <div class="hero-content">
        <p class="hero-tagline">按章约 1 元 · 失败全额返还 · 自带长篇记忆</p>
        <h1>AI 写小说，陪你日更长篇连载</h1>
        <p class="subtitle">从书名、大纲到章纲与正文续写，人物伏笔自动记忆，写到 50 章也不乱</p>
        <div class="hero-btns">
          <button class="btn-primary" @click="openTrial">免费生成 5 个爆款书名</button>
          <button class="btn-secondary" @click="$router.push('/trending')">查看真实案例</button>
        </div>
        <p class="hero-hint">游客免费体验书名生成 · 注册送 30 点（约可续写 3 章）</p>
      </div>
    </section>

    <section class="features">
      <div class="feature-card">
        <img :src="images.features.brain" alt="小说大脑功能图标" class="icon-img" width="56" height="56" />
        <h3>小说大脑</h3>
        <p>人物档案、伏笔、章节摘要自动记忆，写到第 50 章也不乱</p>
      </div>
      <div class="feature-card">
        <img :src="images.features.novel" alt="长篇连载功能图标" class="icon-img" width="56" height="56" />
        <h3>长篇连载</h3>
        <p>大纲 → 章纲 → 正文续写，专为日更作者设计</p>
      </div>
      <div class="feature-card">
        <img :src="images.features.short" alt="短故事功能图标" class="icon-img" width="56" height="56" />
        <h3>短故事</h3>
        <p>输入想法，几分钟生成完整短篇，适合盐选/公众号</p>
      </div>
      <div class="feature-card">
        <img :src="images.features.credits" alt="点数计费功能图标" class="icon-img" width="56" height="56" />
        <h3>点数计费</h3>
        <p>用多少付多少，注册送 30 点，每日免费 5 点</p>
      </div>
    </section>

    <section class="product-demo">
      <div class="demo-inner">
        <div class="demo-copy">
          <p class="demo-label">产品预览</p>
          <h2>7 步创作向导，从灵感到正文</h2>
          <p class="demo-desc">题材 → 灵感 → 书名 → 设定 → 大纲 → 章纲 → 续写，专为中文网文日更设计。小说大脑自动记人物与伏笔，写到后期也不乱。</p>
          <ul class="demo-list">
            <li>大纲与章纲可批量生成、单章重写</li>
            <li>按章约 1 元，失败全额返还点数</li>
            <li>{{ publicCaseLine }}</li>
          </ul>
          <router-link :to="demoCreateLink" class="btn-demo">免费体验创作流程 →</router-link>
        </div>
        <div class="demo-visual">
          <img
            :src="images.workspace"
            alt="LyRead 创作台界面：大纲、章纲与正文续写工作流"
            class="demo-screenshot"
            loading="lazy"
            decoding="async"
            width="720"
            height="405"
          />
        </div>
      </div>
    </section>

    <section class="data-proof" v-if="statsLoaded">
      <div class="data-item">
        <h3>{{ stats.users }}</h3>
        <p>注册用户</p>
      </div>
      <div class="data-item">
        <h3>{{ stats.works }}</h3>
        <p>平台作品</p>
      </div>
      <div class="data-item">
        <h3>{{ stats.cases }}</h3>
        <p>公开案例</p>
      </div>
    </section>
    <p class="stats-note" v-if="statsLoaded">数据来自平台实时统计，每日更新</p>

    <section class="pricing-cta">
      <h2>透明计费，失败全额返还</h2>
      <p>生成一章约 2000 字 ≈ 10 点（约 1 元）· 10 元 = 100 点</p>
      <router-link to="/pricing" class="btn-pricing">查看价格详情 →</router-link>
    </section>

    <section class="hot-section">
      <div class="section-header">
        <SectionHeading :icon="images.features.novel">创作案例</SectionHeading>
        <router-link v-if="hotCases.length" to="/trending" class="more-link">查看全部 →</router-link>
      </div>
      <div v-if="casesLoading" class="hot-loading">加载案例中...</div>
      <div v-else-if="!hotCases.length" class="hot-empty">
        <p>暂无公开案例，<router-link :to="demoCreateLink">开始创作</router-link> 并提交审核后将展示在这里</p>
      </div>
      <div v-else class="hot-grid">
        <router-link
          v-for="(c, i) in hotCases"
          :key="c.id"
          :to="`/case/${c.id}`"
          class="hot-card hot-card-link"
          @click="trackCaseClick(c)"
        >
          <CaseCover :item="c" :index="i" :alt="`${c.title} 封面`" height="140px" />
          <div class="hot-body">
            <div class="hot-type">{{ c.category || '都市' }}</div>
            <h3>{{ c.title }}</h3>
            <p v-if="c.excerpt" class="hot-excerpt">{{ c.excerpt }}</p>
            <div class="hot-tags">
              <span>{{ formatExcerptLabel(c) }}</span>
              <span>热度 {{ c.heat }}</span>
            </div>
          </div>
        </router-link>
      </div>
    </section>

    <!-- 用户评价 -->
    <section class="testimonials">
      <SectionHeading class="testimonials-title" :icon="images.pricing.gem" center>创作者场景反馈</SectionHeading>
      <p class="testimonials-note">以下为典型使用场景描述，不代表个别用户承诺效果</p>
      <div class="testimonial-grid">
        <div v-for="t in testimonials" :key="t.name" class="testimonial-card">
          <AvatarBadge :label="t.initial" :color="t.color" :alt-color="t.altColor" />
          <div class="name">{{ t.name }}</div>
          <p>{{ t.quote }}</p>
        </div>
      </div>
    </section>

    <!-- 试用弹窗 -->
    <div class="modal-overlay" v-if="showTrialModal" @click.self="showTrialModal = false">
      <div class="modal-content">
        <button class="modal-close" @click="showTrialModal = false">×</button>
        <SectionHeading tag="h3" :icon="images.logo" center>免费体验 · AI 书名生成</SectionHeading>
        <p class="trial-desc">选题材、写灵感，AI 一次生成 5 个爆款书名</p>
        
        <div class="trial-steps">
          <div class="trial-step">
            <span class="step-num">1</span>
            <span>选题材 + 写灵感</span>
          </div>
          <div class="trial-step">
            <span class="step-num">2</span>
            <span>AI 生成 5 个书名</span>
          </div>
          <div class="trial-step">
            <span class="step-num">3</span>
            <span>注册后进创作台写大纲与正文</span>
          </div>
        </div>

        <div class="trial-input-area">
          <select v-model="trialType" class="trial-select">
            <option value="">选择题材</option>
            <option value="fantasy">玄幻修仙</option>
            <option value="urban">都市神豪</option>
            <option value="reborn">重生流</option>
            <option value="warrior">战神归来</option>
            <option value="brainhole">脑洞文</option>
          </select>
          <input v-model="trialPrompt" placeholder="描述你的故事想法...例如：主角意外获得神豪系统，在都市纵横" class="trial-input" @keyup.enter="startTrial" />
          <button class="btn-start-trial" :disabled="trialLoading" @click="startTrial">
            {{ trialLoading ? '生成中...' : '开始创作' }}
          </button>
        </div>

        <div v-if="trialResult" class="trial-result">
          <h4>AI 为你生成的书名（点击选用，不够可继续生成）</h4>
          <div class="action-row-trial" v-if="trialTitles.length">
            <button
              v-if="isLoggedIn"
              type="button"
              class="btn-more-titles"
              :disabled="trialLoading"
              @click="startTrial(true)"
            >
              {{ trialLoading ? '生成中...' : '🎲 再随机 5 个（1 点）' }}
            </button>
            <span v-else class="guest-more-hint">注册后可无限换批生成书名</span>
          </div>
          <div v-if="trialTitles.length" class="title-pick-grid">
            <button
              v-for="(t, i) in trialTitles"
              :key="i"
              type="button"
              class="title-pick"
              :class="{ selected: trialResult.title === t.title }"
              @click="pickTrialTitle(t)"
            >
              <strong>{{ t.title }}</strong>
              <span>{{ t.hook || t.description }}</span>
            </button>
          </div>
          <p v-else class="result-title">{{ trialResult.title }}</p>
          <p class="result-hook">{{ trialResult.description }}</p>
          <div v-if="!isLoggedIn" class="trial-cta-row">
            <button class="btn-continue-trial" @click="goRegisterContinue">
              用这个名字继续写 → 注册领 30 点
            </button>
            <p class="trial-cta-hint">注册即送 30 点，约可 AI 续写 3 章</p>
          </div>
          <div v-else class="trial-cta-row">
            <button class="btn-continue-trial" @click="goWorkspaceContinue">进入创作台继续 →</button>
          </div>
        </div>

        <div v-if="trialError" class="trial-error">{{ trialError }}</div>

        <div class="trial-tips" v-if="!trialResult">
          <span class="tip-badge"><img :src="images.pricing.gift" alt="免费试用" width="16" height="16" /> 游客可免费生成书名一次</span>
          <span class="tip-link" @click="goRegisterContinue">注册送 30 点 →</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { IMAGES } from '../assets/images'
import CaseCover from '../components/CaseCover.vue'
import AvatarBadge from '../components/AvatarBadge.vue'
import SectionHeading from '../components/SectionHeading.vue'
import { statsApi, casesApi } from '../api'
import { formatCount, formatExcerptLabel } from '../utils/format'
import { trackEvent } from '../utils/analytics'

const router = useRouter()
const images = IMAGES

const testimonials = [
  { initial: '日', name: '日更作者 · 长篇连载', color: '#2563eb', altColor: '#60a5fa', quote: '「章纲批量出完再续写，日更 6000 字成本约 3 元，比请人代写划算太多。」' },
  { initial: '盐', name: '盐选作者 · 短篇试错', color: '#db2777', altColor: '#f9a8d4', quote: '「短故事流程 15 点一篇，先批量试梗，命中再扩成长篇。」' },
  { initial: '工', name: '内容工作室 · 批量产出', color: '#0f766e', altColor: '#2dd4bf', quote: '「标准化大纲模板 + 人工质检，团队日产出提升明显。」' },
  { initial: '新', name: '新手作者 · 开书入门', color: '#7c3aed', altColor: '#a78bfa', quote: '「免费书名生成降低开书门槛，7 步向导不用自己搭 Prompt。」' },
]

const showTrialModal = ref(false)
const trialType = ref('')
const trialPrompt = ref('')
const trialLoading = ref(false)
const trialResult = ref(null)
const trialTitles = ref([])
const trialError = ref('')
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

/** 游客走注册表单并深链创作台新建向导；登录用户直接进入向导 */
const demoCreateLink = computed(() => {
  if (isLoggedIn.value) return { path: '/workspace', query: { mode: 'new' } }
  return {
    path: '/login',
    query: { mode: 'register', redirect: '/workspace?mode=new' },
  }
})

function pickTrialTitle(t) {
  trialResult.value = { title: t.title, description: t.hook || t.description || '' }
}

function workspaceQuery() {
  const q = { type: trialType.value, prompt: trialPrompt.value }
  if (trialResult.value?.title) q.generatedTitle = trialResult.value.title
  return q
}

function goWorkspaceContinue() {
  router.push({ path: '/workspace', query: workspaceQuery() })
  showTrialModal.value = false
}

function goRegisterContinue() {
  const redirect = `/workspace?${new URLSearchParams(workspaceQuery()).toString()}`
  router.push({ path: '/login', query: { redirect, mode: 'register' } })
  showTrialModal.value = false
  trackEvent('trial_register_cta', { category: 'funnel', label: 'continue_after_title' })
}
const statsLoaded = ref(false)
const hotCases = ref([])
const casesLoading = ref(true)

const stats = ref({
  users: '—',
  works: '—',
  cases: '—',
})

const publicCaseLine = computed(() => {
  if (!statsLoaded.value || stats.value.cases === '—') return '100+ 公开案例可参考风格与节奏'
  return `${stats.value.cases}+ 公开案例可参考风格与节奏`
})

function openTrial() {
  trackEvent('trial_open', { category: 'funnel', label: 'hero_cta' })
  showTrialModal.value = true
}

function trackCaseClick(c) {
  trackEvent('case_click', { category: 'funnel', label: String(c.id) })
}

onMounted(async () => {
  try {
    const [statsRes, casesRes] = await Promise.all([
      statsApi.public(),
      casesApi.list(3),
    ])
    if (statsRes?.success) {
      stats.value = {
        users: formatCount(statsRes.users),
        works: formatCount(statsRes.works),
        cases: formatCount(statsRes.cases),
      }
      statsLoaded.value = true
    }
    if (casesRes?.success) hotCases.value = casesRes.cases || []
  } catch { /* 隐藏数据区 */ }
  finally { casesLoading.value = false }
})

const startTrial = async (append = false) => {
  if (!trialType.value || !trialPrompt.value) {
    trialError.value = '请选择题材并描述你的故事想法'
    return
  }

  trackEvent('trial_submit', { category: 'funnel', label: trialType.value })
  trialLoading.value = true
  if (!append) {
    trialResult.value = null
    trialTitles.value = []
  }
  trialError.value = ''
  try {
    const token = localStorage.getItem('token')
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers.Authorization = `Bearer ${token}`
    const body = {
      genre: trialType.value,
      prompt: trialPrompt.value,
      exclude_titles: append ? trialTitles.value.map(t => t.title) : [],
      variation: String(Date.now()),
      count: 5,
    }
    const res = await fetch('/api/story/generate-title', {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const data = await res.json()
    if (!data.success) {
      trialError.value = data.error || data.detail || 'AI 生成失败，请稍后再试'
      return
    }
    const incoming = data.titles || [{ title: data.title, hook: data.description }]
    if (append) {
      const seen = new Set(trialTitles.value.map(t => t.title))
      for (const t of incoming) {
        if (t.title && !seen.has(t.title)) {
          trialTitles.value.push(t)
          seen.add(t.title)
        }
      }
    } else {
      trialTitles.value = incoming
      trialResult.value = { title: data.title, description: data.description }
    }
    if (!trialResult.value && trialTitles.value.length) {
      trialResult.value = { title: trialTitles.value[0].title, description: trialTitles.value[0].hook || '' }
    }
    trackEvent('trial_success', { category: 'funnel', label: append ? 'more_titles' : 'generate_title' })
    window.dispatchEvent(new Event('credits-changed'))
  } catch (error) {
    console.error('试用生成失败:', error)
    trialError.value = 'AI 生成失败，请稍后再试或更换内容。'
  } finally {
    trialLoading.value = false
  }
}
</script>

<style scoped>
/* 定义全局CSS变量，这里只在Home.vue中定义，后续可以考虑提取到全局style文件 */
:root {
  --lyread-bg-light: #f1f6fa; /* 微奢冰灰蓝背景 */
  --lyread-bg-gradient-start: #eef5ff;
  --lyread-bg-gradient-end: #f6f9ff;
  --lyread-primary-blue-start: #4da1ff; /* 渐变蓝按钮起始色 */
  --lyread-primary-blue-end: #2563eb;   /* 渐变蓝按钮结束色 */
  --lyread-text-dark: #1e2a3a;
  --lyread-text-secondary: #5a6a7a;
  --lyread-card-bg: #ffffff;
  --lyread-shadow-light: rgba(0,0,0,0.06);
  --lyread-shadow-medium: rgba(0,0,0,0.08);
}

.home {
  min-height: 100vh;
  background: var(--lyread-bg-light); /* 使用微奢冰灰蓝作为主背景 */
  /* background: linear-gradient(180deg, var(--lyread-bg-gradient-end), var(--lyread-bg-gradient-start)); */ /* 可以考虑更柔和的渐变 */
  font-family: 'PingFang SC', 'Helvetica Neue', Helvetica, 'Microsoft YaHei', Arial, sans-serif;
  color: var(--lyread-text-dark);
}

.hero {
  text-align: center;
  padding: 80px 24px;
  background: linear-gradient(135deg, var(--lyread-primary-blue-start) 0%, var(--lyread-primary-blue-end) 100%);
  color: white;
  border-bottom-left-radius: 40px;
  border-bottom-right-radius: 40px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}
.hero-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.22;
  pointer-events: none;
}
.hero-content { position: relative; z-index: 1; }
.hero-tagline {
  display: inline-block; margin-bottom: 12px; padding: 6px 14px; border-radius: 999px;
  background: rgba(255,255,255,0.18); font-size: 13px; font-weight: 600; letter-spacing: 0.02em;
}
.hero h1 { font-size: 36px; margin-bottom: 16px; }
.hero-hint { margin-top: 16px; font-size: 13px; opacity: 0.85; }
.subtitle { font-size: 18px; opacity: 0.9; margin-bottom: 32px; }
.hero-btns { display: flex; gap: 16px; justify-content: center; }
.btn-primary, .btn-secondary, .btn-start-trial {
  padding: 16px 32px; /* 增大触摸目标 */
  min-height: 44px;   /* 最小触摸高度 */
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
  -webkit-tap-highlight-color: transparent; /* 移除移动端点击蓝色高亮 */
}
.btn-primary {
  background: var(--lyread-card-bg); /* 白色按钮 */
  color: var(--lyread-primary-blue-end);
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}
.btn-secondary, .btn-start-trial {
  background: linear-gradient(135deg, var(--lyread-primary-blue-start), var(--lyread-primary-blue-end)); /* 渐变蓝按钮 */
  color: white;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
  -webkit-backdrop-filter: blur(10px); /* 毛玻璃效果 */
  backdrop-filter: blur(10px);
  background-color: rgba(77, 161, 255, 0.7); /* 兜底颜色 */
}
.btn-secondary:hover, .btn-start-trial:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3);
  opacity: 0.9;
}

.features {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: -40px auto 60px; /* 轻微上浮，避免卡片过度压盖英雄区 */
  padding: 0 24px;
  position: relative;
  z-index: 1; /* 确保浮动在英雄区之上 */
}
.feature-card {
  background: var(--lyread-card-bg);
  border-radius: 16px;
  box-shadow: 0 4px 20px var(--lyread-shadow-medium);
  padding: 32px 24px;
  text-align: center;
  border: 1px solid rgba(255,255,255,0.1); /* 增加一点边框配合微奢感 */
  -webkit-backdrop-filter: blur(8px); /* 元素自身也带点毛玻璃感 */
  backdrop-filter: blur(8px);
  background-color: rgba(255,255,255,0.9); /* 兜底 */
}
.feature-card .icon-img { display: block; margin: 0 auto 16px; object-fit: contain; }
.feature-card h3 { color: var(--lyread-text-dark); margin-bottom: 8px; }
.feature-card p { color: var(--lyread-text-secondary); font-size: 14px; }

.product-demo {
  max-width: 1200px;
  margin: 0 auto 48px;
  padding: 0 24px;
}
.demo-inner {
  display: grid;
  grid-template-columns: 1fr 1.1fr;
  gap: 40px;
  align-items: center;
  background: var(--lyread-card-bg);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 8px 30px rgba(77, 163, 255, 0.08);
  border: 1px solid rgba(218, 230, 245, 0.6);
}
.demo-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--lyread-primary-blue-end);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}
.demo-copy h2 {
  font-size: 26px;
  color: var(--lyread-text-dark);
  margin-bottom: 12px;
  line-height: 1.35;
}
.demo-desc {
  color: var(--lyread-text-secondary);
  font-size: 15px;
  line-height: 1.7;
  margin-bottom: 16px;
}
.demo-list {
  margin: 0 0 20px;
  padding-left: 20px;
  color: var(--lyread-text-secondary);
  font-size: 14px;
  line-height: 1.9;
}
.btn-demo {
  display: inline-block;
  padding: 12px 24px;
  background: linear-gradient(135deg, #4da1ff, #2563eb);
  color: #fff;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  font-size: 15px;
}
.btn-demo:hover { opacity: 0.92; }
.demo-screenshot {
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(30, 42, 58, 0.12);
  border: 1px solid rgba(218, 230, 245, 0.8);
}

/* Data Proof Section */
.data-proof {
  max-width: 1200px;
  margin: 60px auto;
  padding: 40px 24px;
  background: var(--lyread-card-bg);
  border-radius: 24px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-around;
  text-align: center;
  flex-wrap: wrap; /* 确保小屏下换行 */
  gap: 30px;
}
.data-item h3 {
  font-size: 38px;
  color: var(--lyread-primary-blue-end);
  margin-bottom: 8px;
  font-weight: 700;
}
.data-item p {
  font-size: 16px;
  color: var(--lyread-text-secondary);
}


.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto 24px;
  padding: 0 24px;
}
.section-header h2,
.section-header :deep(.section-heading) { font-size: 24px; color: var(--lyread-text-dark); }
.more-link { font-size: 14px; color: var(--lyread-primary-blue-end); text-decoration: none; font-weight: 600; }
.more-link:hover { text-decoration: underline; }

.hot-loading, .hot-empty { text-align: center; color: #94a3b8; padding: 32px 0; font-size: 14px; }
.hot-empty a { color: var(--lyread-primary-blue-end); }

.hot-section { padding: 40px 24px; max-width: 1200px; margin: 0 auto; }
.hot-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.hot-card {
  background: var(--lyread-card-bg);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px var(--lyread-shadow-light);
  border: 1px solid rgba(255,255,255,0.1);
}
.hot-card-link {
  display: block;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s, box-shadow 0.2s;
}
.hot-card-link:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px var(--lyread-shadow-medium);
}
.hot-card-link :deep(.case-cover-wrap) {
  height: 140px;
}
.hot-body { padding: 16px 20px 20px; }
.hot-type {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(77, 161, 255, 0.12); /* 浅蓝色背景（修复无效的 rgba(var()) 写法） */
  color: var(--lyread-primary-blue-end); /* 深蓝色文字 */
  border-radius: 20px;
  font-size: 12px;
  margin-bottom: 12px;
}
.hot-card h3 { font-size: 16px; color: var(--lyread-text-dark); margin-bottom: 8px; }
.hot-excerpt {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.hot-tags span {
  display: inline-block;
  padding: 2px 8px;
  background: #f1f5f9; /* 浅灰色背景 */
  color: var(--lyread-text-secondary);
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
}

.testimonials-note { font-size: 13px; color: #94a3b8; margin: -20px 0 24px; }
.stats-note { text-align: center; font-size: 12px; color: #94a3b8; margin: -40px auto 48px; max-width: 1200px; }
.testimonials-title { margin-bottom: 32px; font-size: 24px; }
.testimonial-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.testimonial-card {
  background: var(--lyread-card-bg);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px var(--lyread-shadow-light);
  border: 1px solid rgba(255,255,255,0.1);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  background-color: rgba(255,255,255,0.9);
}
.testimonial-card .avatar-img {
  display: block;
  width: 56px;
  height: 56px;
  margin: 0 auto 12px;
  border-radius: 50%;
  object-fit: cover;
}
.testimonial-card :deep(.avatar-badge) { margin: 0 auto 12px; }
.testimonial-card .name { font-weight: 600; color: var(--lyread-text-dark); margin-bottom: 8px; }
.testimonial-card p { color: var(--lyread-text-secondary); font-size: 14px; }

.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.3); /* 更轻的蒙版 */
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: var(--lyread-card-bg);
  border-radius: 16px;
  padding: 40px; /* 增加内边距 */
  width: 90%;
  max-width: 560px;
  position: relative;
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.1);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  background-color: rgba(255,255,255,0.95); /* 兜底 */
}
.modal-close {
  position: absolute; top: 16px; right: 16px;
  background: none; border: none; font-size: 24px; color: #94a3b8;
  cursor: pointer;
}
.modal-content h3 { font-size: 24px; color: var(--lyread-text-dark); margin-bottom: 8px; text-align: center; }
.trial-desc { text-align: center; color: var(--lyread-text-secondary); margin-bottom: 20px; }

.trial-steps {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}
.trial-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--lyread-text-secondary);
}
.trial-step .step-num {
  width: 28px; /* 增大 */
  height: 28px; /* 增大 */
  background: linear-gradient(135deg, var(--lyread-primary-blue-start), var(--lyread-primary-blue-end));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.trial-input-area { display: flex; flex-direction: column; gap: 12px; }
.trial-select, .trial-input {
  padding: 16px; /* 增大 */
  border: 1px solid #e2e8f0;
  border-radius: 12px; /* 增大 */
  font-size: 15px; /* 增大 */
}
.trial-select:focus, .trial-input:focus {
  outline: none;
  border-color: var(--lyread-primary-blue-start);
  box-shadow: 0 0 0 3px rgba(77, 161, 255, 0.1);
}

.trial-tips {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  font-size: 13px;
}
.trial-tips span:first-child,
.tip-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--lyread-primary-blue-end);
  background: rgba(77, 161, 255, 0.12);
  padding: 4px 12px;
  border-radius: 20px;
}
.tip-link {
  color: var(--lyread-primary-blue-start);
  cursor: pointer;
}
.tip-link:hover { text-decoration: underline; }

.pricing-cta {
  max-width: 720px; margin: 0 auto 48px; padding: 32px 24px; text-align: center;
  background: linear-gradient(135deg, #fff7e6, #ffe9c7); border-radius: 20px;
  border: 1px solid #ffd591;
}
.pricing-cta h2 { font-size: 22px; color: #ad6800; margin-bottom: 8px; }
.pricing-cta p { color: #8c6d1f; margin-bottom: 16px; font-size: 14px; }
.btn-pricing {
  display: inline-block; padding: 10px 22px; border-radius: 10px;
  background: #fff; color: #ad6800; font-weight: 600; text-decoration: none;
  border: 1px solid #ffd591;
}
.trial-result {
  margin-top: 16px; padding: 16px; background: #f0f9ff; border-radius: 12px;
  border: 1px solid #bae6fd; text-align: left;
}
.trial-result h4 { font-size: 14px; color: #0369a1; margin-bottom: 8px; }
.title-pick-grid { display: grid; gap: 8px; margin-bottom: 10px; }
.title-pick {
  text-align: left; padding: 12px; border-radius: 10px; border: 1px solid #bae6fd;
  background: #fff; cursor: pointer; width: 100%;
}
.title-pick.selected { border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37,99,235,0.15); }
.title-pick strong { display: block; color: #1e2a3a; margin-bottom: 4px; }
.title-pick span { font-size: 12px; color: #64748b; }
.action-row-trial { margin-bottom: 10px; }
.btn-more-titles {
  padding: 8px 14px; border-radius: 8px; border: 1px solid #93c5fd;
  background: #fff; color: #2563eb; font-size: 13px; font-weight: 600; cursor: pointer;
}
.guest-more-hint { font-size: 12px; color: #64748b; }
.result-title { font-weight: 700; color: #1e2a3a; margin-bottom: 6px; }
.result-hook { font-size: 13px; color: #5a6a7a; }
.trial-cta-row { margin-top: 16px; text-align: center; }
.btn-continue-trial {
  width: 100%; padding: 14px 20px; border: none; border-radius: 12px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff;
  font-size: 16px; font-weight: 700; cursor: pointer;
}
.trial-cta-hint { margin-top: 8px; font-size: 12px; color: #64748b; }
.trial-error {
  margin-top: 12px; padding: 10px 12px; border-radius: 8px;
  background: #fef2f2; color: #dc2626; font-size: 13px; text-align: left;
}

/* 媒体查询调整 */
@media (max-width: 1024px) {
  .features {
    grid-template-columns: repeat(2, 1fr); /* 4列 -> 2列 */
  }
  .demo-inner {
    grid-template-columns: 1fr;
    padding: 28px;
  }
  .demo-visual { order: -1; }
}
@media (max-width: 768px) {
  .hot-grid, .testimonial-grid {
    grid-template-columns: 1fr; /* 2列 -> 1列 */
  }
  .features {
    grid-template-columns: 1fr; /* 单列 */
    margin-top: 24px; /* 移动端不再上浮压盖英雄区，避免错位 */
    gap: 16px;
  }
  .hero {
    padding: 60px 16px;
  }
  .hero h1 {
    font-size: 28px;
  }
  .subtitle {
    font-size: 16px;
  }
  .hero-btns {
    flex-direction: column;
  }
  .btn-primary, .btn-secondary, .btn-start-trial {
    width: 100%;
    max-width: 300px;
    margin: 0 auto;
  }
  .data-proof {
    padding: 30px 16px;
    gap: 20px;
  }
  .data-item h3 {
    font-size: 30px;
  }
  .data-item p {
    font-size: 14px;
  }
  .modal-content {
    padding: 30px;
  }
  .modal-content h3 {
    font-size: 20px;
  }
  .trial-steps {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>