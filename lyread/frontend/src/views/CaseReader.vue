<template>
  <div class="reader-page">
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
      </header>
      <section v-if="chapters.length" class="body">
        <div v-for="(ch, i) in chapters" :key="i" class="chapter">
          <h2 v-if="ch.title" class="chapter-title">{{ ch.title }}</h2>
          <p v-for="(para, j) in ch.paragraphs" :key="j" class="paragraph">{{ para }}</p>
        </div>
      </section>
      <section v-else class="body empty-body">
        <p>该案例暂无正文节选。</p>
        <router-link :to="`/ep/${caseData.id}`" target="_blank" class="link">查看 SEO 页面 →</router-link>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { casesApi } from '../api'
import { parseChapters, countChapters } from '../utils/caseContent'
import { formatStorySettingWords } from '../utils/format'
import { trackEvent } from '../utils/analytics'

const route = useRoute()
const loading = ref(true)
const caseData = ref(null)
const rawBody = ref('')
const prevCase = ref(null)
const nextCase = ref(null)
const isLoggedIn = computed(() => typeof localStorage !== 'undefined' && !!localStorage.getItem('token'))

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
  }
}

const chapters = computed(() => parseChapters(rawBody.value))
const excerptChapters = computed(() => caseData.value?.excerpt_chapters ?? countChapters(rawBody.value))
const excerptChars = computed(() => caseData.value?.excerpt_chars ?? rawBody.value.length)

const workspaceLink = computed(() => {
  const cat = caseData.value?.category || ''
  return { path: '/workspace', query: { type: cat, prompt: `参考《${caseData.value?.title}》的风格创作` } }
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

onMounted(() => loadCase(route.params.id))
watch(() => route.params.id, (id) => { if (id) loadCase(id) })
</script>

<style scoped>
.reader-page { max-width: 720px; margin: 0 auto; padding: 32px 20px 80px; }
.loading, .empty { text-align: center; color: #94a3b8; padding: 60px 20px; display: flex; flex-direction: column; align-items: center; gap: 16px; }
.empty-link { font-size: 14px; }
.article { background: #fff; border-radius: 16px; padding: 28px 28px 32px; border: 1px solid #e8f0fa; }
.cat { display: inline-block; padding: 4px 10px; background: #eff6ff; color: #2563eb; border-radius: 999px; font-size: 12px; }
h1 { font-size: 24px; margin: 12px 0 8px; line-height: 1.35; color: #1e2a3a; }
.meta { color: #64748b; font-size: 13px; margin-bottom: 8px; }
.excerpt-note { color: #94a3b8; font-size: 12px; margin-bottom: 28px; line-height: 1.5; }
.chapter { margin-bottom: 28px; }
.chapter-title {
  font-size: 18px; font-weight: 700; color: #1e2a3a;
  margin: 0 0 16px; padding-bottom: 10px; border-bottom: 1px solid #eef2f7;
}
.paragraph {
  margin: 0 0 14px; line-height: 1.95; font-size: 16px; color: #2c3e50;
  text-indent: 2em;
}
.paragraph:last-child { margin-bottom: 0; }
.empty-body { color: #64748b; font-size: 14px; }
.link { color: #2563eb; }
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
  display: inline-block; padding: 14px 28px; border-radius: 12px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; font-weight: 600; text-decoration: none;
}
</style>
