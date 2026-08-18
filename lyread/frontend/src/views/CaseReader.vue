<template>
  <div class="reader-page" :class="{ 'has-mobile-dock': showMobileDock }">
    <div
      v-if="caseData && chapters.length"
      class="read-progress"
      role="progressbar"
      :aria-valuenow="progressPct"
      aria-valuemin="0"
      aria-valuemax="100"
      aria-label="阅读进度"
    >
      <div class="read-progress-bar" :style="{ width: `${progressPct}%` }" />
    </div>
    <div
      v-if="caseData && chapters.length && scrollPct >= 0.04 && !finishedOffer"
      class="read-progress-chip"
      aria-hidden="true"
    >{{ progressChipLabel }}</div>
    <div v-if="loading" class="loading">加载中...</div>
    <EmptyState
      v-else-if="!caseData"
      :image="images.emptyCreate"
      image-alt="案例不可用"
      title="案例不存在或已下架"
      description="可以回案例广场继续读，或直接注册开写同题材。"
      :image-width="160"
    >
      <div class="empty-actions">
        <router-link
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          class="btn-cta"
          @click="trackEvent('case_missing_register', { category: 'conversion', label: 'empty' })"
        >免费注册，送 30 点 →</router-link>
        <router-link to="/trending" class="link empty-link">回案例广场</router-link>
      </div>
    </EmptyState>
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
      <EmptyState
        v-else
        class="empty-body-wrap"
        :image="images.emptyCreate"
        image-alt="暂无节选"
        title="该案例暂无正文节选"
        description="先逛案例广场，或用同题材直接开写。"
        :image-width="140"
      >
        <div class="empty-actions">
          <router-link
            :to="creationLink"
            class="btn-cta"
            @click="trackEvent('case_empty_body_cta', { category: 'conversion', label: isLoggedIn ? 'logged_in' : 'register_first', value: Number(caseData.id) || 0 })"
          >{{ ctaLabel }}</router-link>
          <router-link to="/trending" class="link empty-link">回案例广场</router-link>
        </div>
      </EmptyState>
      <!-- 读完软引导：清进度后推下一篇，缩短案例连读路径 -->
      <div v-if="finishedOffer" class="finished-cta" role="status">
        <p class="finished-text">本节选读完了</p>
        <div class="finished-actions">
          <router-link
            v-if="nextCase"
            :to="`/case/${nextCase.id}`"
            class="finished-next"
            @click="trackEvent('case_finished_next', { category: 'engagement', label: 'next', value: Number(nextCase.id) || 0 })"
          >下一篇 · {{ nextCase.title }} →</router-link>
          <router-link
            :to="creationLink"
            class="finished-write"
            @click="trackEvent('case_finished_cta', { category: 'conversion', label: isLoggedIn ? 'logged_in' : 'register_first', value: Number(caseData.id) || 0 })"
          >{{ isLoggedIn ? '用同题材开写 →' : '注册送 30 点开写 →' }}</router-link>
        </div>
      </div>
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
    <!-- 移动端滚动中固定转化条：拇指区可达，读完后让位给 finished CTA -->
    <div v-if="showMobileDock" class="mobile-dock" role="region" aria-label="继续创作">
      <span class="mobile-dock-meta">{{ progressChipLabel }}</span>
      <router-link
        :to="creationLink"
        class="mobile-dock-cta"
        @click="trackEvent('case_mobile_dock_cta', { category: 'conversion', label: isLoggedIn ? 'logged_in' : 'register_first', value: Number(caseData?.id) || 0 })"
      >{{ isLoggedIn ? '同题材开写 →' : '注册开写 →' }}</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { casesApi } from '../api'
import { IMAGES } from '../assets/images'
import EmptyState from '../components/EmptyState.vue'
import { parseChapters, countChapters } from '../utils/caseContent'
import { formatStorySettingWords } from '../utils/format'
import { trackEvent } from '../utils/analytics'
import { workspaceWizardQuery } from '../utils/wizardGenre'
import {
  caseProgressStorageKey,
  readCaseProgress,
  RESUME_MIN_RATIO,
  RESUME_MAX_RATIO,
  DONE_RATIO,
} from '../utils/caseProgress'

/** 相邻篇正文内存预取，连读时跳过一次网络往返 */
const casePrefetchCache = new Map()

const images = IMAGES
const route = useRoute()
const loading = ref(true)
const caseData = ref(null)
const rawBody = ref('')
const prevCase = ref(null)
const nextCase = ref(null)
const scrollPct = ref(0)
const activeChapterIndex = ref(0)
const resumeOffer = ref(null)
const finishedOffer = ref(false)
let completeTrackedFor = null
const isLoggedIn = computed(() => typeof localStorage !== 'undefined' && !!localStorage.getItem('token'))
const progressPct = computed(() => Math.round(scrollPct.value * 100))
const progressChipLabel = computed(() => {
  const ch = chapters.value[activeChapterIndex.value]
  const chLabel = ch ? shortChapterLabel(ch, activeChapterIndex.value) : `第${activeChapterIndex.value + 1}章`
  return `${progressPct.value}% · ${chLabel}`
})
/** 读过开头且未读完：窄屏 CSS 显示底部拇指区 CTA（桌面隐藏） */
const showMobileDock = computed(() => {
  if (!caseData.value || !chapters.value.length || finishedOffer.value) return false
  return scrollPct.value >= 0.12 && scrollPct.value < DONE_RATIO
})

function clearProgress(id) {
  try {
    localStorage.removeItem(caseProgressStorageKey(id))
  } catch { /* ignore */ }
}

function saveProgress(id, ratio, chapterIndex) {
  try {
    // 读完不再保留进度，避免下次误出「继续读」
    if (ratio >= DONE_RATIO) {
      clearProgress(id)
      return
    }
    localStorage.setItem(caseProgressStorageKey(id), JSON.stringify({
      ratio: Math.min(1, Math.max(0, ratio)),
      chapterIndex: Number.isFinite(chapterIndex) ? chapterIndex : 0,
      updatedAt: Date.now(),
      title: caseData.value?.title || undefined,
      category: caseData.value?.category || undefined,
    }))
  } catch { /* ignore quota */ }
}

function prefetchNeighbor(id) {
  const key = Number(id)
  if (!key || casePrefetchCache.has(key)) return
  casePrefetchCache.set(
    key,
    casesApi.get(key).catch(() => null),
  )
}

function takePrefetch(id) {
  const key = Number(id)
  if (!key) return null
  const hit = casePrefetchCache.get(key)
  if (!hit) return null
  casePrefetchCache.delete(key)
  return hit
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
  activeChapterIndex.value = chapterIndex
  const done = scrollPct.value >= DONE_RATIO
  finishedOffer.value = done && !!chapters.value.length
  if (done) {
    resumeOffer.value = null
    if (completeTrackedFor !== id) {
      completeTrackedFor = id
      trackEvent('case_read_complete', {
        category: 'engagement',
        label: String(chapterIndex),
        value: Number(id) || 0,
      })
    }
  }
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
  finishedOffer.value = false
  const saved = readCaseProgress(id)
  if (!saved) return
  // 历史脏数据：已读完仍留在 localStorage 时直接清掉
  if (saved.ratio >= DONE_RATIO) {
    clearProgress(id)
    return
  }
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
  activeChapterIndex.value = 0
  resumeOffer.value = null
  finishedOffer.value = false
  completeTrackedFor = null
  window.scrollTo(0, 0)
  try {
    const cached = takePrefetch(id)
    const detailPromise = cached
      ? Promise.resolve(cached).then((res) => res)
      : casesApi.get(id)
    const [res, navRes] = await Promise.all([
      detailPromise,
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
      // 预取相邻篇正文，点「下一篇」时几乎秒开
      if (navRes.next?.id) prefetchNeighbor(navRes.next.id)
      if (navRes.prev?.id) prefetchNeighbor(navRes.prev.id)
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
.read-progress-chip {
  display: none;
}
.loading { text-align: center; color: #94a3b8; padding: 60px 20px; }
.empty-actions {
  display: flex; flex-direction: column; align-items: center; gap: 12px;
}
.empty-link { font-size: 14px; }
.empty-body-wrap { margin: 8px 0 12px; }
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
.finished-cta {
  margin: 8px 0 0;
  padding: 16px 0 4px;
  border-top: 1px dashed #bbf7d0;
}
.finished-text {
  margin: 0 0 10px;
  font-size: 14px;
  font-weight: 600;
  color: #0f766e;
}
.finished-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  align-items: center;
}
.finished-next, .finished-write {
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  line-height: 1.4;
}
.finished-next { color: #2563eb; }
.finished-next:hover { text-decoration: underline; }
.finished-write { color: #0f766e; }
.finished-write:hover { text-decoration: underline; }
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
.mobile-dock { display: none; }
@media (max-width: 640px) {
  .reader-page.has-mobile-dock { padding-bottom: calc(96px + env(safe-area-inset-bottom, 0px)); }
  .article { padding: 20px 16px 24px; }
  h1 { font-size: 20px; }
  .nav-title { font-size: 13px; }
  .read-progress-chip {
    display: block;
    position: fixed;
    top: 10px;
    right: 12px;
    z-index: 41;
    padding: 4px 8px;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.78);
    color: #f8fafc;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.01em;
    pointer-events: none;
    max-width: 55vw;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .mobile-dock {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 42;
    padding: 10px 14px calc(10px + env(safe-area-inset-bottom, 0px));
    background: rgba(255, 255, 255, 0.96);
    border-top: 1px solid #e2e8f0;
    box-shadow: 0 -6px 20px rgba(15, 23, 42, 0.06);
    backdrop-filter: blur(8px);
  }
  .mobile-dock-meta {
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .mobile-dock-cta {
    flex-shrink: 0;
    padding: 10px 14px;
    border-radius: 10px;
    background: linear-gradient(135deg, #0f766e, #0d9488);
    color: #fff;
    text-decoration: none;
    font-size: 13px;
    font-weight: 700;
  }
}
</style>
