<template>
  <div class="reader-page">
    <div v-if="loading" class="loading">加载中...</div>
    <EmptyState
      v-else-if="!caseData"
      title="案例不存在或已下架"
      description="去看看其他热门案例，或用同样风格开始创作。"
    >
      <router-link to="/trending" class="btn-secondary">浏览案例</router-link>
    </EmptyState>
    <article v-else class="article">
      <header>
        <span class="cat">{{ caseData.category }}</span>
        <h1>{{ caseData.title }}</h1>
        <p class="meta">{{ caseData.word_count }} 字 · 热度 {{ caseData.heat }} · 评分 {{ caseData.score }}</p>
      </header>
      <section v-if="body" class="body">
        <pre>{{ body }}</pre>
      </section>
      <section v-else class="body empty-body">
        <p>该案例暂无正文节选，以下为平台生成作品展示。</p>
        <a :href="sharePath" class="link">查看 SEO 页面 →</a>
      </section>
      <footer class="cta">
        <div class="share-row">
          <button type="button" class="btn-share" @click="copyShareLink">{{ copyLabel }}</button>
          <button v-if="canNativeShare" type="button" class="btn-share" @click="nativeShare">分享</button>
        </div>
        <router-link :to="workspaceLink" class="btn-cta">用这个风格开始创作 →</router-link>
      </footer>
    </article>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { casesApi } from '../api'
import EmptyState from '../components/EmptyState.vue'
import { trackEvent } from '../utils/analytics'

const route = useRoute()
const loading = ref(true)
const caseData = ref(null)
const body = ref('')
const copyLabel = ref('复制分享链接')
const canNativeShare = ref(typeof navigator !== 'undefined' && typeof navigator.share === 'function')

const sharePath = computed(() => `/ep/${caseData.value?.id || route.params.id}`)
const shareUrl = computed(() => `https://lyread.cn${sharePath.value}`)

const workspaceLink = computed(() => {
  const cat = caseData.value?.category || ''
  return { path: '/workspace', query: { type: cat, prompt: `参考《${caseData.value?.title}》的风格创作` } }
})

function setCaseMeta(c) {
  const title = `${c.title} - LyRead AI 小说作品`
  const desc = (body.value || c.excerpt || `${c.title} - ${c.category || '小说'}类型，AI 智能创作案例`).slice(0, 160)
  document.title = title
  const setMeta = (selector, attr, name, content) => {
    let el = document.querySelector(selector)
    if (!el) {
      el = document.createElement(attr === 'name' ? 'meta' : attr === 'rel' ? 'link' : 'meta')
      if (attr === 'name') el.setAttribute('name', name)
      else if (attr === 'property') el.setAttribute('property', name)
      else if (attr === 'rel') el.setAttribute('rel', name)
      document.head.appendChild(el)
    }
    if (attr === 'rel') el.href = content
    else el.content = content
  }
  setMeta('meta[name="description"]', 'name', 'description', desc)
  setMeta('link[rel="canonical"]', 'rel', 'canonical', shareUrl.value)
  setMeta('meta[property="og:title"]', 'property', 'og:title', title)
  setMeta('meta[property="og:description"]', 'property', 'og:description', desc)
  setMeta('meta[property="og:url"]', 'property', 'og:url', shareUrl.value)
  setMeta('meta[property="og:type"]', 'property', 'og:type', 'article')
}

async function copyShareLink() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    copyLabel.value = '已复制'
    trackEvent('case_share', { category: 'funnel', label: 'copy', value: Number(caseData.value?.id) || 0 })
    setTimeout(() => { copyLabel.value = '复制分享链接' }, 2000)
  } catch {
    copyLabel.value = '复制失败'
    setTimeout(() => { copyLabel.value = '复制分享链接' }, 2000)
  }
}

async function nativeShare() {
  try {
    await navigator.share({
      title: caseData.value?.title || 'LyRead 案例',
      text: `读一读《${caseData.value?.title}》—— LyRead AI 创作案例`,
      url: shareUrl.value,
    })
    trackEvent('case_share', { category: 'funnel', label: 'native', value: Number(caseData.value?.id) || 0 })
  } catch {
    /* user cancelled */
  }
}

onMounted(async () => {
  try {
    const res = await casesApi.get(route.params.id)
    if (res?.success) {
      caseData.value = res.case
      // Prefer full preview_body; preview_excerpt is a truncated OG/list teaser (~1500).
      body.value = res.case.preview_body || res.case.preview_excerpt || ''
      setCaseMeta(res.case)
      trackEvent('case_read', { category: 'funnel', label: String(res.case.id) })
    }
  } finally { loading.value = false }
})
</script>

<style scoped>
.reader-page { max-width: 720px; margin: 0 auto; padding: 32px 20px 80px; }
.loading { text-align: center; color: #94a3b8; padding: 60px; }
.article { background: #fff; border-radius: 16px; padding: 28px; border: 1px solid #e8f0fa; }
.cat { display: inline-block; padding: 4px 10px; background: #eff6ff; color: #2563eb; border-radius: 999px; font-size: 12px; }
h1 { font-size: 24px; margin: 12px 0 8px; line-height: 1.35; }
.meta { color: #94a3b8; font-size: 13px; margin-bottom: 24px; }
.body pre { white-space: pre-wrap; line-height: 1.9; font-size: 16px; color: #1e2a3a; font-family: inherit; }
.empty-body { color: #64748b; font-size: 14px; }
.link { color: #2563eb; }
.cta { text-align: center; margin-top: 32px; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.share-row { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
.btn-share {
  padding: 10px 16px; border-radius: 10px; border: 1px solid #dbeafe;
  background: #f8fbff; color: #2563eb; font-weight: 600; font-size: 13px; cursor: pointer;
}
.btn-cta {
  display: inline-block; padding: 14px 28px; border-radius: 12px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; font-weight: 600; text-decoration: none;
}
.btn-secondary {
  display: inline-block; padding: 10px 18px; border-radius: 10px;
  background: #eff6ff; color: #2563eb; font-weight: 600; text-decoration: none;
}
@media (max-width: 640px) {
  .reader-page { padding: 20px 14px 64px; }
  .article { padding: 20px 16px; border-radius: 12px; }
  h1 { font-size: 20px; }
  .body pre { font-size: 15px; line-height: 1.85; }
}
</style>
