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
      <header class="article-header">
        <img :src="coverSrc" :alt="`${caseData.title} 封面`" class="article-cover" width="88" height="118" />
        <div class="article-heading">
          <span class="cat">{{ caseData.category }}</span>
          <h1>{{ caseData.title }}</h1>
          <p class="meta">{{ caseData.word_count }} 字 · 热度 {{ caseData.heat }} · 评分 {{ caseData.score }}</p>
        </div>
      </header>
      <section v-if="body" class="body">
        <pre>{{ body }}</pre>
      </section>
      <section v-else class="body empty-body">
        <p>该案例暂无正文节选。可先浏览同风格作品，或直接用这个题材开写。</p>
        <div class="empty-actions">
          <router-link to="/trending" class="link">浏览更多案例 →</router-link>
          <router-link :to="workspaceLink" class="link" @click="trackCta('empty_body')">用这个风格开写 →</router-link>
          <a :href="sharePath" class="link subtle">SEO 预览</a>
        </div>
      </section>
      <footer class="cta">
        <div class="share-row">
          <button type="button" class="btn-share" @click="copyShareLink">{{ copyLabel }}</button>
          <button v-if="canNativeShare" type="button" class="btn-share" @click="nativeShare">分享</button>
        </div>
        <router-link :to="workspaceLink" class="btn-cta" @click="trackCta('footer')">用这个风格开始创作 →</router-link>
      </footer>
      <section v-if="related.length" class="related" aria-label="相关案例">
        <h2 class="related-title">同风格还可读</h2>
        <p class="related-sub">继续浏览相近题材，找到想写的味道再开写</p>
        <ul class="related-list">
          <li v-for="(c, i) in related" :key="c.id">
            <router-link :to="`/case/${c.id}`" class="related-link" @click="onRelatedClick(c)">
              <img :src="coverForCase(c, i)" :alt="`${c.title} 封面`" class="related-cover" width="48" height="64" loading="lazy" />
              <span class="related-text">
                <span class="related-cat">{{ c.category || '都市' }}</span>
                <span class="related-name">{{ c.title }}</span>
                <span class="related-meta">{{ c.word_count }} 字 · 热度 {{ c.heat }}</span>
              </span>
            </router-link>
          </li>
        </ul>
        <router-link to="/trending" class="related-more" @click="trackRelatedMore">查看全部案例 →</router-link>
      </section>
      <div class="sticky-cta" aria-hidden="false">
        <router-link :to="workspaceLink" class="btn-cta sticky" @click="trackCta('sticky_mobile')">
          用这个风格开始创作 →
        </router-link>
      </div>
    </article>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { casesApi } from '../api'
import { coverForCase, ogImageForCase } from '../assets/images'
import EmptyState from '../components/EmptyState.vue'
import { trackEvent } from '../utils/analytics'

const route = useRoute()
const loading = ref(true)
const caseData = ref(null)
const body = ref('')
const related = ref([])
const copyLabel = ref('复制分享链接')
const canNativeShare = ref(typeof navigator !== 'undefined' && typeof navigator.share === 'function')

const sharePath = computed(() => `/ep/${caseData.value?.id || route.params.id}`)
const shareUrl = computed(() => `https://lyread.cn${sharePath.value}`)
const coverSrc = computed(() => coverForCase(caseData.value || {}, 0))

const workspaceLink = computed(() => {
  const cat = caseData.value?.category || ''
  return { path: '/workspace', query: { type: cat, prompt: `参考《${caseData.value?.title}》的风格创作` } }
})

function setCaseMeta(c) {
  const title = `${c.title} - LyRead AI 小说作品`
  const desc = (body.value || c.excerpt || `${c.title} - ${c.category || '小说'}类型，AI 智能创作案例`).slice(0, 160)
  const image = ogImageForCase(c, 0)
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
  setMeta('meta[property="og:image"]', 'property', 'og:image', image)
  setMeta('meta[name="twitter:card"]', 'name', 'twitter:card', 'summary_large_image')
  setMeta('meta[name="twitter:image"]', 'name', 'twitter:image', image)
}

function trackCta(label) {
  trackEvent('case_cta_click', {
    category: 'conversion',
    label,
    value: Number(caseData.value?.id) || 0,
  })
}

function onRelatedClick(c) {
  trackEvent('related_case_click', {
    category: 'funnel',
    label: String(c.id),
    value: Number(caseData.value?.id) || 0,
  })
}

function trackRelatedMore() {
  trackEvent('related_case_more', {
    category: 'funnel',
    label: String(caseData.value?.id || ''),
  })
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

/** 与 coverForCase 对齐的题材家族，便于同风格推荐（showcase 类目常一对一） */
function genreFamily(category) {
  const cat = String(category || '').toLowerCase()
  if (/仙侠|玄幻|修仙/.test(cat)) return 'xianxia'
  if (/言情|甜宠|恋爱/.test(cat)) return 'romance'
  if (/科幻|脑洞|末世/.test(cat)) return 'scifi'
  if (/悬疑|推理|惊悚/.test(cat)) return 'suspense'
  if (/历史|架空|宫廷/.test(cat)) return 'history'
  if (/战神|都市|神豪|系统|游戏|竞技/.test(cat)) return 'urban'
  if (/重生|穿越|校园|青春/.test(cat)) return 'reborn'
  return 'other'
}

function pickRelated(pool, currentId, category, limit = 4) {
  const id = Number(currentId)
  const family = genreFamily(category)
  const others = (pool || []).filter((c) => Number(c.id) !== id)
  const sameCat = others.filter((c) => (c.category || '') === (category || ''))
  const sameFamily = others.filter(
    (c) => (c.category || '') !== (category || '') && genreFamily(c.category) === family,
  )
  const rest = others.filter(
    (c) => (c.category || '') !== (category || '') && genreFamily(c.category) !== family,
  )
  const seen = new Set()
  const out = []
  for (const c of [...sameCat, ...sameFamily, ...rest]) {
    if (seen.has(c.id)) continue
    seen.add(c.id)
    out.push(c)
    if (out.length >= limit) break
  }
  return out
}

async function loadCase(id) {
  loading.value = true
  caseData.value = null
  body.value = ''
  related.value = []
  try {
    const res = await casesApi.get(id)
    if (res?.success) {
      caseData.value = res.case
      // Prefer full preview_body; preview_excerpt is a truncated OG/list teaser (~1500).
      body.value = res.case.preview_body || res.case.preview_excerpt || ''
      setCaseMeta(res.case)
      trackEvent('case_read', { category: 'funnel', label: String(res.case.id) })
      try {
        const listRes = await casesApi.list(24)
        related.value = pickRelated(listRes?.cases || [], res.case.id, res.case.category, 4)
      } catch {
        related.value = []
      }
    }
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.id,
  (id) => {
    if (id != null && id !== '') loadCase(id)
  },
  { immediate: true },
)
</script>

<style scoped>
.reader-page { max-width: 720px; margin: 0 auto; padding: 32px 20px 80px; }
.loading { text-align: center; color: #94a3b8; padding: 60px; }
.article { background: #fff; border-radius: 16px; padding: 28px; border: 1px solid #e8f0fa; }
.article-header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 8px;
}
.article-cover {
  width: 88px;
  height: 118px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
  background: #e2e8f0;
}
.article-heading { min-width: 0; flex: 1; }
.cat { display: inline-block; padding: 4px 10px; background: #eff6ff; color: #2563eb; border-radius: 999px; font-size: 12px; }
h1 { font-size: 24px; margin: 12px 0 8px; line-height: 1.35; }
.meta { color: #94a3b8; font-size: 13px; margin-bottom: 16px; }
.body pre { white-space: pre-wrap; line-height: 1.9; font-size: 16px; color: #1e2a3a; font-family: inherit; }
.empty-body { color: #64748b; font-size: 14px; line-height: 1.7; }
.empty-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 16px;
  margin-top: 12px;
}
.link { color: #2563eb; font-weight: 600; text-decoration: none; }
.link.subtle { color: #64748b; font-weight: 500; }
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
.related {
  margin-top: 36px;
  padding-top: 24px;
  border-top: 1px solid #e8f0fa;
}
.related-title {
  font-size: 18px;
  margin: 0 0 6px;
  color: #0f172a;
}
.related-sub {
  margin: 0 0 16px;
  font-size: 13px;
  color: #64748b;
}
.related-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.related-link {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  background: #f8fbff;
  border: 1px solid transparent;
  transition: border-color 0.15s ease, background 0.15s ease;
}
.related-link:hover,
.related-link:focus-visible {
  border-color: #bfdbfe;
  background: #eff6ff;
  outline: none;
}
.related-cover {
  width: 48px;
  height: 64px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
  background: #e2e8f0;
}
.related-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.related-cat {
  font-size: 11px;
  color: #2563eb;
  font-weight: 600;
}
.related-name {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.related-meta {
  font-size: 12px;
  color: #94a3b8;
}
.related-more {
  display: inline-block;
  margin-top: 14px;
  font-size: 13px;
  font-weight: 600;
  color: #2563eb;
  text-decoration: none;
}
.sticky-cta { display: none; }
@media (max-width: 640px) {
  .reader-page { padding: 20px 14px 88px; }
  .article { padding: 20px 16px; border-radius: 12px; }
  .article-header { gap: 12px; }
  .article-cover { width: 72px; height: 96px; }
  h1 { font-size: 20px; }
  .body pre { font-size: 15px; line-height: 1.85; }
  .related { margin-top: 28px; padding-top: 20px; }
  .sticky-cta {
    display: block;
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 40;
    padding: 10px 14px calc(10px + env(safe-area-inset-bottom, 0px));
    background: rgba(255, 255, 255, 0.96);
    border-top: 1px solid #e8f0fa;
    box-shadow: 0 -6px 20px rgba(15, 23, 42, 0.06);
  }
  .btn-cta.sticky {
    display: block;
    width: 100%;
    text-align: center;
    padding: 13px 16px;
    box-sizing: border-box;
  }
}
</style>
