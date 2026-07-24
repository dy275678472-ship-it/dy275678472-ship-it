<template>
  <div class="reader-page">
    <div
      v-if="caseData && chapters.length"
      class="read-progress"
      role="progressbar"
      :aria-valuenow="Math.round(scrollPct * 100)"
      aria-valuemin="0"
      aria-valuemax="100"
      aria-label="阅读进度"
    >
      <div class="read-progress-bar" :style="{ width: `${Math.round(scrollPct * 100)}%` }" />
    </div>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!caseData" class="empty">
      <p>案例不存在或已下架</p>
      <router-link
        :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
        class="btn-cta"
        @click="trackEvent('case_missing_register', { category: 'conversion', label: 'empty' })"
      >免费注册，送 30 点 →</router-link>
      <router-link to="/trending" class="link empty-link">回案例广场</router-link>
    </div>
    <article v-else class="article">
      <header>
        <span class="cat">{{ caseData.category }}</span>
        <h1>{{ caseData.title }}</h1>
        <p class="meta">
          <span v-if="excerptChapters">节选 {{ excerptChapters }} 章</span>
          <span v-if="excerptChars"> · 约 {{ excerptChars }} 字</span>
          <span v-if="caseData.word_count"> · {{ formatStorySettingWords(caseData.word_count) }}</span>
          <span> · 热度 {{ caseData.heat }}</span>
        </p>
        <p class="excerpt-note">以下为平台精选开篇节选，非完整连载。喜欢此风格可一键带入创作台。</p>
        <nav v-if="chapters.length >= 2" class="toc" aria-label="章节目录">
          <a
            v-for="(ch, i) in chapters"
            :key="i"
            class="toc-link"
            :href="`#ch-${i}`"
            @click.prevent="jumpToChapter(i)"
          >{{ shortChapterLabel(ch, i) }}</a>
        </nav>
        <button
          v-if="resumeOffer"
          type="button"
          class="resume-btn"
          @click="resumeReading"
        >继续读 · {{ resumeOffer.label }}</button>
      </header>
      <section v-if="chapters.length" class="body">
        <template v-for="(ch, i) in chapters" :key="i">
          <div :id="`ch-${i}`" class="chapter" :data-ch="i">
            <h2 v-if="ch.title" class="chapter-title">{{ ch.title }}</h2>
            <p v-for="(para, j) in ch.paragraphs" :key="j" class="paragraph">{{ para }}</p>
          </div>
          <!-- 长节选中部软 CTA：与 SSR 案例页对齐，缩短阅读→注册路径 -->
          <div
            v-if="showMidCta && i === midCtaAfterIndex"
            class="mid-cta"
            role="note"
          >
            <p class="mid-cta-text">读到一半了？注册送 30 点，用同题材接着写下去</p>
            <router-link
              :to="creationLink"
              class="mid-cta-link"
              @click="trackEvent('case_mid_cta_click', { category: 'conversion', label: isLoggedIn ? 'logged_in' : 'register_first', value: Number(caseData.id) || 0 })"
            >{{ isLoggedIn ? '用同题材开写 →' : '免费注册开写 →' }}</router-link>
          </div>
        </template>
      </section>
      <section v-else class="body empty-body">
        <p>该案例暂无正文节选。</p>
        <router-link
          :to="creationLink"
          class="btn-cta"
          @click="trackEvent('case_empty_body_cta', { category: 'conversion', label: isLoggedIn ? 'logged_in' : 'register_first', value: Number(caseData.id) || 0 })"
        >{{ ctaLabel }}</router-link>
        <router-link to="/trending" class="link empty-link">回案例广场</router-link>
      </section>
      <nav v-if="prevCase || nextCase" class="case-nav" aria-label="同题材案例">
        <router-link v-if="prevCase" :to="`/case/${prevCase.id}`" class="nav-link nav-prev">
          <span class="nav-label">← 上一篇</span>
          <span class="nav-title">{{ prevCase.title }}</span>
        </router-link>
        <span v-else class="nav-spacer" />
        <router-link v-if="nextCase" :to="`/case/${nextCase.id}`" class="nav-link nav-next">
          <span class="nav-label">下一篇 →</span>
          <span class="nav-title">{{ nextCase.title }}</span>
        </router-link>
      </nav>
      <footer class="cta">
        <router-link
          :to="creationLink"
          class="btn-cta"
          @click="trackEvent('case_cta_click', { category: 'conversion', label: isLoggedIn ? 'logged_in' : 'register_first', value: Number(caseData.id) || 0 })"
        >{{ ctaLabel }}</router-link>
      </footer>
    </article>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { casesApi } from '../api'
import { parseChapters, countChapters } from '../utils/caseContent'
import { formatStorySettingWords } from '../utils/format'
import { trackEvent } from '../utils/analytics'
import { workspaceWizardQuery } from '../utils/wizardGenre'

const PROGRESS_KEY = 'lyread_case_progress'
const RESUME_MIN_RATIO = 0.12
const RESUME_MAX_RATIO = 0.92

const route = useRoute()
const loading = ref(true)
const caseData = ref(null)
const rawBody = ref('')
const prevCase = ref(null)
const nextCase = ref(null)
const scrollPct = ref(0)
const resumeOffer = ref(null)
const isLoggedIn = computed(() => typeof localStorage !== 'undefined' && !!localStorage.getItem('token'))

function progressStorageKey(id) {
  return `${PROGRESS_KEY}:${id}`
}

function readSavedProgress(id) {
  try {
    const raw = localStorage.getItem(progressStorageKey(id))
    if (!raw) return null
    const data = JSON.parse(raw)
    if (!data || typeof data.ratio !== 'number') return null
    return data
  } catch {
    return null
  }
}

function saveProgress(id, ratio, chapterIndex) {
  try {
    localStorage.setItem(progressStorageKey(id), JSON.stringify({
      ratio: Math.min(1, Math.max(0, ratio)),
      chapterIndex: Number.isFinite(chapterIndex) ? chapterIndex : 0,
      updatedAt: Date.now(),
    }))
  } catch { /* ignore quota */ }
}

function shortChapterLabel(ch, i) {
  const t = (ch?.title || '').replace(/\s+/g, ' ').trim()
  if (!t) return `第${i + 1}章`
  return t.length > 10 ? `${t.slice(0, 10)}…` : t
}

function jumpToChapter(i) {
  const el = document.getElementById(`ch-${i}`)
  if (!el) return
  el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  trackEvent('case_toc_jump', { category: 'engagement', label: String(i), value: Number(caseData.value?.id) || 0 })
}

function measureScroll() {
  const doc = document.documentElement
  const max = Math.max(1, (doc.scrollHeight || 0) - window.innerHeight)
  const y = window.scrollY || doc.scrollTop || 0
  scrollPct.value = Math.min(1, Math.max(0, y / max))
  const id = caseData.value?.id
  if (!id) return
  let chapterIndex = 0
  const nodes = document.querySelectorAll('.chapter[data-ch]')
  const anchorY = y + Math.min(120, window.innerHeight * 0.2)
  nodes.forEach((node) => {
    if (node.offsetTop <= anchorY) chapterIndex = Number(node.dataset.ch) || 0
  })
  saveProgress(id, scrollPct.value, chapterIndex)
}

let scrollTimer = null
function onScroll() {
  if (scrollTimer) return
  scrollTimer = window.setTimeout(() => {
    scrollTimer = null
    measureScroll()
  }, 80)
}

function prepareResume(id) {
  resumeOffer.value = null
  const saved = readSavedProgress(id)
  if (!saved) return
  if (saved.ratio < RESUME_MIN_RATIO || saved.ratio > RESUME_MAX_RATIO) return
  const ch = Number.isFinite(saved.chapterIndex) ? saved.chapterIndex : 0
  resumeOffer.value = {
    ratio: saved.ratio,
    chapterIndex: ch,
    label: chapters.value[ch]?.title
      ? shortChapterLabel(chapters.value[ch], ch)
      : `约 ${Math.round(saved.ratio * 100)}%`,
  }
}

function resumeReading() {
  const offer = resumeOffer.value
  if (!offer) return
  trackEvent('case_resume_click', {
    category: 'engagement',
    label: String(offer.chapterIndex),
    value: Number(caseData.value?.id) || 0,
  })
  const el = document.getElementById(`ch-${offer.chapterIndex}`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } else {
    const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight)
    window.scrollTo({ top: Math.round(offer.ratio * max), behavior: 'smooth' })
  }
  resumeOffer.value = null
}

function updatePageMeta(c) {
  if (!c?.title) return
  const title = `${c.title} - 案例阅读 | LyRead AI`
  const desc = `${c.category || '网文'}精选节选，${c.excerpt_chars ? `约 ${c.excerpt_chars} 字` : '可一键带入创作台'}`
  document.title = title
  const descMeta = document.querySelector('meta[name="description"]')
  if (descMeta) descMeta.content = desc
  const setOg = (prop, content) => {
    const el = document.querySelector(`meta[property="${prop}"]`)
    if (el) el.content = content
  }
  setOg('og:title', title)
  setOg('og:description', desc)
  setOg('og:url', `https://lyread.cn/case/${c.id}`)
}

async function loadCase(id) {
  loading.value = true
  caseData.value = null
  rawBody.value = ''
  prevCase.value = null
  nextCase.value = null
  scrollPct.value = 0
  resumeOffer.value = null
  try {
    const [res, navRes] = await Promise.all([
      casesApi.get(id),
      casesApi.neighbors(id).catch(() => null),
    ])
    if (res?.success) {
      caseData.value = res.case
      rawBody.value = res.case.preview_body || res.case.preview_excerpt || ''
      updatePageMeta(res.case)
    }
    if (navRes?.success) {
      prevCase.value = navRes.prev
      nextCase.value = navRes.next
    }
  } finally {
    loading.value = false
    await nextTick()
    if (caseData.value?.id) prepareResume(caseData.value.id)
    measureScroll()
  }
}

const chapters = computed(() => parseChapters(rawBody.value))
const excerptChapters = computed(() => caseData.value?.excerpt_chapters ?? countChapters(rawBody.value))
const excerptChars = computed(() => caseData.value?.excerpt_chars ?? rawBody.value.length)

/** ≥4 章或正文较长时，在中部插入 register-first 软 CTA（对齐 SSR） */
const showMidCta = computed(() => chapters.value.length >= 4 || rawBody.value.length >= 900)
const midCtaAfterIndex = computed(() => {
  const n = chapters.value.length
  if (n < 2) return -1
  return Math.max(1, Math.floor(n / 2) - 1)
})

const workspaceLink = computed(() => {
  const q = workspaceWizardQuery(caseData.value?.category || '', caseData.value?.title || '')
  return { path: '/workspace', query: q }
})

/** 游客直达注册表单并带回创作台意图，缩短案例→注册路径 */
const creationLink = computed(() => {
  const ws = workspaceLink.value
  if (isLoggedIn.value) return ws
  const q = new URLSearchParams(ws.query || {}).toString()
  const redirect = q ? `${ws.path}?${q}` : ws.path
  return { path: '/login', query: { mode: 'register', redirect } }
})
const ctaLabel = computed(() =>
  isLoggedIn.value ? '用这个风格开始创作 →' : '免费注册，用这个风格开写（送 30 点）→',
)

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  loadCase(route.params.id)
})
onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll)
  if (scrollTimer) {
    clearTimeout(scrollTimer)
    scrollTimer = null
  }
})
watch(() => route.params.id, (id) => { if (id) loadCase(id) })
</script>

<style scoped>
.reader-page { max-width: 720px; margin: 0 auto; padding: 32px 20px 80px; }
.read-progress {
  position: fixed; top: 0; left: 0; right: 0; z-index: 40;
  height: 3px; background: transparent; pointer-events: none;
}
.read-progress-bar {
  height: 100%; width: 0;
  background: linear-gradient(90deg, #2563eb, #0f766e);
  transition: width 0.12s linear;
}
.loading, .empty { text-align: center; color: #94a3b8; padding: 60px 20px; display: flex; flex-direction: column; align-items: center; gap: 16px; }
.empty-link { font-size: 14px; }
.article { background: #fff; border-radius: 16px; padding: 28px 28px 32px; border: 1px solid #e8f0fa; }
.cat { display: inline-block; padding: 4px 10px; background: #eff6ff; color: #2563eb; border-radius: 999px; font-size: 12px; }
h1 { font-size: 24px; margin: 12px 0 8px; line-height: 1.35; color: #1e2a3a; }
.meta { color: #64748b; font-size: 13px; margin-bottom: 8px; }
.excerpt-note { color: #94a3b8; font-size: 12px; margin-bottom: 12px; line-height: 1.5; }
.toc {
  display: flex; flex-wrap: wrap; gap: 8px 10px;
  margin: 0 0 14px; padding: 0;
}
.toc-link {
  font-size: 12px; color: #2563eb; text-decoration: none;
  padding: 2px 0; border-bottom: 1px dashed #bfdbfe;
}
.toc-link:hover { color: #1d4ed8; border-bottom-color: #2563eb; }
.resume-btn {
  display: inline-flex; align-items: center;
  margin: 0 0 20px; padding: 8px 12px;
  border: 1px solid #bfdbfe; border-radius: 8px;
  background: #eff6ff; color: #1d4ed8;
  font-size: 13px; font-weight: 600; cursor: pointer;
}
.resume-btn:hover { background: #dbeafe; }
.chapter { margin-bottom: 28px; scroll-margin-top: 72px; }
.chapter-title {
  font-size: 18px; font-weight: 700; color: #1e2a3a;
  margin: 0 0 16px; padding-bottom: 10px; border-bottom: 1px solid #eef2f7;
}
.paragraph {
  margin: 0 0 14px; line-height: 1.95; font-size: 16px; color: #2c3e50;
  text-indent: 2em;
}
.paragraph:last-child { margin-bottom: 0; }
.empty-body { color: #64748b; font-size: 14px; display: flex; flex-direction: column; align-items: flex-start; gap: 14px; }
.link { color: #2563eb; }
.mid-cta {
  margin: 8px 0 28px;
  padding: 14px 0;
  border-top: 1px dashed #dbeafe;
  border-bottom: 1px dashed #dbeafe;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  align-items: center;
}
.mid-cta-text {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
  flex: 1 1 220px;
}
.mid-cta-link {
  font-size: 14px;
  font-weight: 600;
  color: #0f766e;
  text-decoration: none;
  white-space: nowrap;
}
.mid-cta-link:hover { text-decoration: underline; }
.case-nav {
  display: flex; justify-content: space-between; gap: 16px;
  margin-top: 28px; padding-top: 24px; border-top: 1px solid #eef2f7;
}
.nav-link {
  flex: 1; max-width: 48%; padding: 12px 14px; border-radius: 12px;
  border: 1px solid #e8f0fa; background: #f8fafc; text-decoration: none;
  transition: border-color 0.15s, background 0.15s;
}
.nav-link:hover { border-color: #93c5fd; background: #eff6ff; }
.nav-prev { text-align: left; }
.nav-next { text-align: right; margin-left: auto; }
.nav-label { display: block; font-size: 12px; color: #64748b; margin-bottom: 4px; }
.nav-title { display: block; font-size: 14px; font-weight: 600; color: #1e2a3a; line-height: 1.4; }
.nav-spacer { flex: 1; }
.cta { text-align: center; margin-top: 24px; padding-top: 24px; border-top: 1px solid #eef2f7; }
.btn-cta {
  display: inline-block; padding: 12px 28px; background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff; border-radius: 10px; text-decoration: none; font-weight: 600;
}
.btn-cta:hover { filter: brightness(1.05); }
@media (max-width: 640px) {
  .article { padding: 20px 16px 24px; }
  h1 { font-size: 20px; }
  .nav-title { font-size: 13px; }
}
</style>
