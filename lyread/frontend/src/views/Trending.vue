<template>
  <div class="trending-page">
    <header class="hero">
      <img :src="images.features.novel" alt="案例阅读" class="hero-icon" width="40" height="40" />
      <h1>案例阅读</h1>
      <p>{{ heroSubtitle }}</p>
      <router-link
        v-if="!isLoggedIn"
        class="hero-register"
        :to="guestRegisterLink"
      >免费注册，送 30 点 →</router-link>
    </header>

    <div v-if="resumeBanner" class="resume-banner" role="status">
      <div class="resume-copy">
        <span class="resume-kicker">上次读到</span>
        <strong class="resume-title">{{ resumeBanner.title }}</strong>
        <span class="resume-meta">已读约 {{ resumeBanner.pct }}%{{ resumeBanner.category ? ` · ${resumeBanner.category}` : '' }}</span>
      </div>
      <router-link
        class="resume-go"
        :to="`/case/${resumeBanner.id}`"
        @click="onResumeBannerClick"
      >继续读 →</router-link>
    </div>

    <div class="filters" v-if="categories.length">
      <button
        type="button"
        class="filter-chip"
        :class="{ active: !activeCategory }"
        @click="setCategory('')"
      >全部 ({{ totalCount }})</button>
      <button
        v-for="cat in categories"
        :key="cat.name"
        type="button"
        class="filter-chip"
        :class="{ active: activeCategory === cat.name }"
        @click="setCategory(cat.name)"
      >{{ cat.name }} ({{ cat.count }})</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <EmptyState
      v-else-if="!cases.length"
      :image="images.emptyCreate"
      title="暂无案例"
      :description="activeCategory ? `「${activeCategory}」暂无案例，试试其他题材或直接开写` : '审核通过的作品将展示在这里；也可先注册开写第一篇'"
      :image-width="160"
    >
      <div class="empty-actions">
        <button
          v-if="activeCategory"
          type="button"
          class="btn-empty-secondary"
          @click="setCategory('')"
        >查看全部题材</button>
        <router-link :to="footerCtaLink" class="btn-cta btn-empty-primary">{{ emptyCtaLabel }}</router-link>
      </div>
    </EmptyState>
    <div v-else class="case-grid">
      <router-link v-for="(c, i) in cases" :key="c.id" :to="`/case/${c.id}`" class="case-card">
        <CaseCover :item="c" :index="i" :alt="`${c.title} 封面`" />
        <div class="case-body">
          <div class="card-top">
            <span class="cat">{{ c.category || '都市' }}</span>
            <span v-if="progressById[c.id]" class="progress-chip">已读 {{ progressById[c.id] }}%</span>
          </div>
          <h3>{{ c.title }}</h3>
          <p v-if="c.excerpt" class="excerpt">{{ c.excerpt }}</p>
          <div class="meta">
            <span>{{ formatExcerptLabel(c) }}</span>
            <span class="heat"><img :src="images.fire" alt="热度" width="14" height="14" /> {{ c.heat }}</span>
          </div>
        </div>
      </router-link>
    </div>

    <div class="cta">
      <p v-if="!isLoggedIn" class="guest-cta-hint">注册送 30 点，约可 AI 续写 3 章</p>
      <router-link :to="footerCtaLink" class="btn-cta">{{ footerCtaLabel }}</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { casesApi } from '../api'
import { IMAGES } from '../assets/images'
import EmptyState from '../components/EmptyState.vue'
import CaseCover from '../components/CaseCover.vue'
import { formatExcerptLabel } from '../utils/format'
import {
  findLatestResumeProgress,
  readCaseProgress,
  RESUME_MIN_RATIO,
  DONE_RATIO,
} from '../utils/caseProgress'
import { trackEvent } from '../utils/analytics'

const images = IMAGES

const cases = ref([])
const categories = ref([])
const activeCategory = ref('')
const totalCount = ref(0)
const loading = ref(true)
const resumeBanner = ref(null)
const progressById = ref({})
const isLoggedIn = computed(() => typeof localStorage !== 'undefined' && !!localStorage.getItem('token'))

function refreshCardProgress(list = cases.value) {
  const next = {}
  for (const c of list || []) {
    if (c?.id == null) continue
    const data = readCaseProgress(c.id)
    if (!data || typeof data.ratio !== 'number') continue
    if (data.ratio < RESUME_MIN_RATIO || data.ratio >= DONE_RATIO) continue
    next[c.id] = Math.round(data.ratio * 100)
  }
  progressById.value = next
}

function refreshResumeBanner(list = cases.value) {
  const hit = findLatestResumeProgress(list)
  resumeBanner.value = hit
    ? {
        id: hit.id,
        title: hit.title,
        category: hit.category,
        pct: Math.round(hit.ratio * 100),
      }
    : null
  refreshCardProgress(list)
}

function onResumeBannerClick() {
  const b = resumeBanner.value
  trackEvent('trending_resume_click', {
    category: 'engagement',
    label: b?.title || '',
    value: Number(b?.id) || 0,
  })
}

/** 游客首屏强调注册赠点，缩短案例浏览 → 注册路径 */
const heroSubtitle = computed(() =>
  isLoggedIn.value
    ? '平台真实生成案例，点击阅读全文，或用这个风格开始创作'
    : '平台真实生成案例。注册送 30 点，约可 AI 续写 3 章；读完即可用同风格开写',
)

const guestRegisterLink = {
  path: '/login',
  query: { mode: 'register', redirect: '/workspace?mode=new' },
}

const footerCtaLink = computed(() =>
  isLoggedIn.value
    ? { path: '/workspace', query: { mode: 'new' } }
    : guestRegisterLink,
)

const footerCtaLabel = computed(() =>
  isLoggedIn.value ? '用这个风格开始创作 →' : '免费注册，用同题材开写（送 30 点）→',
)

const emptyCtaLabel = computed(() =>
  isLoggedIn.value ? '去创作台开写 →' : '免费注册开写（送 30 点）→',
)

async function loadCases() {
  loading.value = true
  try {
    const res = await casesApi.list(140, activeCategory.value)
    if (res?.success) cases.value = res.cases || []
    refreshResumeBanner(cases.value)
  } finally {
    loading.value = false
  }
}

function setCategory(name) {
  activeCategory.value = name
  loadCases()
}

onMounted(async () => {
  refreshResumeBanner([])
  try {
    const [catRes] = await Promise.all([
      casesApi.categories(),
      loadCases(),
    ])
    if (catRes?.success) {
      categories.value = catRes.categories || []
      totalCount.value = categories.value.reduce((s, c) => s + c.count, 0)
    }
  } catch {
    await loadCases()
  }
})
</script>

<style scoped>
.trending-page { max-width: 1100px; margin: 0 auto; padding: 32px 20px 80px; }
.hero { text-align: center; margin-bottom: 28px; }
.hero-icon { display: block; margin: 0 auto 12px; }
.hero h1 { font-size: 28px; color: #1e2a3a; margin-bottom: 8px; }
.hero p { color: #5a6a7a; }
.hero-register {
  display: inline-block; margin-top: 14px; padding: 10px 18px; border-radius: 10px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff;
  font-weight: 600; font-size: 14px; text-decoration: none;
}
.hero-register:hover { filter: brightness(1.05); }
.resume-banner {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  max-width: 720px; margin: 0 auto 24px; padding: 14px 18px;
  border: 1px solid #bfdbfe; border-radius: 12px;
  background: linear-gradient(135deg, rgba(77,161,255,0.08), rgba(37,99,235,0.04));
}
.resume-copy { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.resume-kicker { font-size: 12px; color: #2563eb; font-weight: 600; letter-spacing: 0.02em; }
.resume-title {
  font-size: 15px; color: #1e2a3a; font-weight: 650;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.resume-meta { font-size: 12px; color: #64748b; }
.resume-go {
  flex-shrink: 0; padding: 10px 16px; border-radius: 10px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff;
  font-weight: 600; font-size: 13px; text-decoration: none;
}
.resume-go:hover { filter: brightness(1.05); }
.guest-cta-hint { color: #64748b; font-size: 13px; margin-bottom: 10px; }
@media (max-width: 640px) {
  .resume-banner { flex-direction: column; align-items: stretch; text-align: left; }
  .resume-go { text-align: center; }
}
.empty-actions {
  display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; align-items: center;
}
.btn-empty-secondary {
  padding: 10px 16px; border-radius: 10px; border: 1px solid #bfdbfe;
  background: #fff; color: #2563eb; font-weight: 600; font-size: 14px; cursor: pointer;
}
.btn-empty-secondary:hover { background: #f0f7ff; }
.btn-empty-primary { padding: 10px 18px; font-size: 14px; }
.filters {
  display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;
  margin-bottom: 28px; max-width: 900px; margin-left: auto; margin-right: auto;
}
.filter-chip {
  padding: 6px 14px; border-radius: 999px; border: 1px solid #e2e8f0;
  background: #fff; color: #64748b; font-size: 13px; cursor: pointer;
  transition: all 0.15s;
}
.filter-chip:hover { border-color: #93c5fd; color: #2563eb; }
.filter-chip.active {
  background: rgba(77, 161, 255, 0.12); border-color: #4da1ff; color: #2563eb; font-weight: 600;
}
.loading { text-align: center; color: #94a3b8; padding: 60px; }
.heat { display: inline-flex; align-items: center; gap: 4px; }
.case-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px; }
.case-card {
  display: block; text-decoration: none; background: #fff; border-radius: 14px;
  overflow: hidden; border: 1px solid #e8f0fa; transition: all 0.2s;
}
.case-body { padding: 16px 20px 20px; }
.card-top {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  margin-bottom: 10px;
}
.case-card:hover { box-shadow: 0 8px 24px rgba(77,161,255,0.12); transform: translateY(-2px); border-color: #bfdbfe; }
.case-card :deep(.case-cover-wrap) { height: 120px; }
.cat { display: inline-block; padding: 3px 10px; background: rgba(77,161,255,0.12); color: #2563eb; border-radius: 999px; font-size: 12px; }
.progress-chip {
  flex-shrink: 0; padding: 2px 8px; border-radius: 999px;
  background: rgba(15, 118, 110, 0.1); color: #0f766e;
  font-size: 11px; font-weight: 650; letter-spacing: 0.01em;
}
.case-card h3 { font-size: 16px; color: #1e2a3a; margin-bottom: 8px; line-height: 1.4; }
.excerpt { font-size: 12px; color: #64748b; line-height: 1.5; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.meta { display: flex; gap: 12px; font-size: 12px; color: #94a3b8; }
.cta { text-align: center; }
.btn-cta {
  display: inline-block; padding: 14px 28px; border-radius: 12px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff;
  font-weight: 600; text-decoration: none;
}
@media (max-width: 768px) { .case-grid { grid-template-columns: 1fr; } }
</style>
