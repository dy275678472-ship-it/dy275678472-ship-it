<template>
  <div class="reader-page">
    <div v-if="loading" class="loading">加载中...</div>
    <EmptyState
      v-else-if="!caseData"
      title="案例不存在或已下架"
      description="去看看其他热门案例，或注册后直接开写同风格作品。"
    >
      <div class="empty-cta-row">
        <router-link to="/trending" class="btn-secondary">浏览案例</router-link>
        <router-link
          v-if="!isLoggedIn"
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          class="btn-cta"
          @click="trackEvent('case_missing_register', { category: 'conversion', label: 'guest' })"
        >免费注册，送 30 点 →</router-link>
      </div>
    </EmptyState>
    <article v-else class="article">
      <header class="article-header">
        <img :src="coverSrc" :alt="`${caseData.title} 封面`" class="article-cover" width="88" height="118" />
        <div class="article-heading">
          <span class="cat">{{ caseData.category }}</span>
          <h1>{{ caseData.title }}</h1>
          <p class="meta">
            <span v-if="excerptMeta">节选 {{ excerptMeta }}</span>
            <span v-if="excerptMeta && caseData.word_count"> · </span>
            <span v-if="caseData.word_count">全书约 {{ caseData.word_count }} 字</span>
            <span> · 热度 {{ caseData.heat }}</span>
            <span v-if="caseData.score != null"> · 评分 {{ caseData.score }}</span>
          </p>
          <p class="excerpt-note">以下为平台精选开篇节选，非完整连载。喜欢此风格可一键带入创作台开写同题材。</p>
        </div>
      </header>
      <section v-if="body" class="body">
        <div class="body-text">
          <template v-for="(block, i) in bodyBlocks" :key="i">
            <aside
              v-if="block.type === 'mid_cta'"
              class="mid-read-cta"
              aria-label="读到一半，注册开写"
            >
              <p>读到一半了？注册送 30 点，用同题材接着写下去</p>
              <router-link
                :to="creationLink"
                class="body-register-link"
                @click="trackCta('mid_read_register')"
              >免费注册开写 →</router-link>
            </aside>
            <h2 v-else-if="block.type === 'chapter'" class="chapter-title">{{ block.text }}</h2>
            <p v-else class="body-para">{{ block.text }}</p>
          </template>
        </div>
        <aside
          class="body-register-strip"
          :class="{ logged: isLoggedIn }"
          aria-label="用同题材开写"
        >
          <p v-if="isLoggedIn">读完了？一键把「{{ genreLabel }}」带进创作向导开写</p>
          <p v-else>读到这里了？注册送 30 点，用同题材接着写</p>
          <router-link
            :to="creationLink"
            class="body-register-link"
            @click="trackCta(isLoggedIn ? 'body_end_write' : 'body_end_register')"
          >{{ endWriteLabel }}</router-link>
        </aside>
      </section>
      <section v-else class="body empty-body">
        <p>该案例暂无正文节选。可先浏览同风格作品，或直接用这个题材开写。</p>
        <div class="empty-actions">
          <router-link to="/trending" class="link">浏览更多案例 →</router-link>
          <router-link :to="creationLink" class="link" @click="trackCta('empty_body')">{{ ctaShortLabel }}</router-link>
          <a :href="sharePath" class="link subtle">SEO 预览</a>
        </div>
      </section>
      <footer class="cta">
        <div class="share-row">
          <button type="button" class="btn-share" @click="copyShareLink">{{ copyLabel }}</button>
          <button v-if="canNativeShare" type="button" class="btn-share" @click="nativeShare">分享</button>
        </div>
        <p v-if="!isLoggedIn" class="guest-cta-hint">注册送 30 点，约可 AI 续写 3 章</p>
        <p v-else class="guest-cta-hint">题材与灵感将预填进创作向导，可直接改大纲开写</p>
        <router-link :to="creationLink" class="btn-cta" @click="trackCta('footer')">{{ ctaLabel }}</router-link>
      </footer>
      <section v-if="related.length" class="related" aria-label="相关案例">
        <h2 class="related-title">同风格还可读</h2>
        <p class="related-sub">继续浏览相近题材，展开节选挑到想写的味道再开写</p>
        <ul class="related-list">
          <li v-for="(c, i) in related" :key="c.id">
            <div class="related-item">
              <router-link :to="`/case/${c.id}`" class="related-link" @click="onRelatedClick(c)">
                <img :src="coverForCase(c, i)" :alt="`${c.title} 封面`" class="related-cover" width="48" height="64" loading="lazy" />
                <span class="related-text">
                  <span class="related-cat">{{ c.category || '都市' }}</span>
                  <span class="related-name">{{ c.title }}</span>
                  <span class="related-meta">{{ c.word_count }} 字 · 热度 {{ c.heat }}</span>
                </span>
              </router-link>
              <p
                v-if="c.excerpt"
                class="related-excerpt"
                :class="{ expanded: expandedRelatedId === c.id }"
              >{{ c.excerpt }}</p>
              <button
                v-if="c.excerpt && c.excerpt.length > 72"
                type="button"
                class="related-excerpt-toggle"
                @click="toggleRelatedExcerpt(c)"
              >{{ expandedRelatedId === c.id ? '收起节选' : '展开节选' }}</button>
            </div>
          </li>
        </ul>
        <div class="related-actions">
          <router-link to="/trending" class="related-more" @click="trackRelatedMore">查看全部案例 →</router-link>
          <router-link
            v-if="!isLoggedIn"
            :to="creationLink"
            class="related-register"
            @click="trackCta('related_register')"
          >读完想写？免费注册送 30 点 →</router-link>
        </div>
      </section>
      <div class="sticky-cta" aria-hidden="false">
        <p v-if="!isLoggedIn" class="sticky-hint">注册送 30 点 · 用同风格开写</p>
        <router-link :to="creationLink" class="btn-cta sticky" @click="trackCta('sticky_mobile')">
          {{ ctaLabel }}
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
import { workspaceWizardQuery } from '../utils/wizardGenre'

const route = useRoute()
const loading = ref(true)
const caseData = ref(null)
const body = ref('')
const related = ref([])
const expandedRelatedId = ref(null)
const copyLabel = ref('复制分享链接')
const canNativeShare = ref(typeof navigator !== 'undefined' && typeof navigator.share === 'function')

const sharePath = computed(() => `/ep/${caseData.value?.id || route.params.id}`)
const shareUrl = computed(() => `https://lyread.cn${sharePath.value}`)
const coverSrc = computed(() => coverForCase(caseData.value || {}, 0))
const isLoggedIn = computed(() => typeof localStorage !== 'undefined' && !!localStorage.getItem('token'))

/** 识别「第X章 …」标题行，便于分章阅读（不改动正文内容） */
const CHAPTER_RE = /^(第[零〇一二三四五六七八九十百千万两\d]+章(?:\s*[·\-—:：]?\s*.*)?)$/

function isChapterTitle(text) {
  const line = String(text || '').trim()
  if (!line || line.length > 40) return false
  if (/^——+$/.test(line) || line === '——') return false
  return CHAPTER_RE.test(line)
}

/** 按空行拆段；章题升为 h2；长文中部插入游客软 CTA */
const bodyBlocks = computed(() => {
  const raw = String(body.value || '').replace(/\r\n/g, '\n').trim()
  if (!raw) return []
  const paras = raw
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter((p) => p && p !== '——' && !/^——+$/.test(p))
  const blocks = paras.map((text) => ({
    type: isChapterTitle(text) ? 'chapter' : 'para',
    text,
  }))
  if (isLoggedIn.value || raw.length < 900 || blocks.length < 4) return blocks
  const insertAt = Math.max(2, Math.floor(blocks.length / 2))
  blocks.splice(insertAt, 0, { type: 'mid_cta', text: '' })
  return blocks
})

const excerptMeta = computed(() => {
  const chapters = bodyBlocks.value.filter((b) => b.type === 'chapter').length
  const chars = String(body.value || '').replace(/\s/g, '').length
  const parts = []
  if (chapters > 0) parts.push(`${chapters} 章`)
  if (chars > 0) parts.push(`约 ${chars} 字`)
  return parts.join(' · ')
})

/** 读完 → 创作台：mode=new + 题材 id/自定义预填，避免中文类目误入 genreId */
const workspaceLink = computed(() => ({
  path: '/workspace',
  query: workspaceWizardQuery({
    category: caseData.value?.category || '',
    title: caseData.value?.title || '',
  }),
}))

const genreLabel = computed(() => {
  const cat = String(caseData.value?.category || '').trim()
  return cat || '同题材'
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
  isLoggedIn.value
    ? `用同题材开写（${genreLabel.value}）→`
    : '免费注册，用同题材开写（送 30 点）→',
)
const ctaShortLabel = computed(() =>
  isLoggedIn.value ? '用同题材开写 →' : '注册送 30 点，开写 →',
)
const endWriteLabel = computed(() =>
  isLoggedIn.value ? `用同题材开写（${genreLabel.value}）→` : '免费注册开写 →',
)

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

/** 同风格区节选：触控端点按展开，减少只能看标题就跳出 */
function toggleRelatedExcerpt(c) {
  const next = expandedRelatedId.value === c.id ? null : c.id
  expandedRelatedId.value = next
  trackEvent('related_excerpt_toggle', {
    category: 'engagement',
    label: next ? 'expand' : 'collapse',
    value: Number(c.id) || 0,
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
  expandedRelatedId.value = null
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
.meta { color: #94a3b8; font-size: 13px; margin-bottom: 8px; }
.excerpt-note {
  margin: 0 0 18px;
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.55;
}
.body-text {
  font-size: 16.5px;
  line-height: 1.95;
  color: #1e2a3a;
  letter-spacing: 0.01em;
}
.chapter-title {
  margin: 1.6em 0 0.75em;
  font-size: 1.15em;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.4;
  letter-spacing: 0.02em;
}
.chapter-title:first-child { margin-top: 0.25em; }
.body-para {
  margin: 0 0 1.05em;
  white-space: pre-wrap;
  word-break: break-word;
}
.body-para:last-child { margin-bottom: 0; }
.mid-read-cta {
  margin: 22px 0;
  padding: 12px 0;
  border-top: 1px dashed #dbeafe;
  border-bottom: 1px dashed #dbeafe;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 14px;
}
.mid-read-cta p {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
  flex: 1 1 220px;
}
.body-register-strip {
  margin: 20px 0 8px;
  padding: 14px 0 4px;
  border-top: 1px dashed #dbeafe;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 14px;
}
.body-register-strip.logged {
  border-top-color: #bbf7d0;
}
.body-register-strip p {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
  flex: 1 1 220px;
}
.body-register-link {
  font-size: 14px;
  font-weight: 600;
  color: #0f766e;
  text-decoration: none;
  white-space: nowrap;
}
.body-register-link:hover,
.body-register-link:focus-visible {
  text-decoration: underline;
  outline: none;
}
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
.empty-cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  align-items: center;
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
.related-item {
  padding: 10px 12px 12px;
  border-radius: 12px;
  background: #f8fbff;
  border: 1px solid transparent;
  transition: border-color 0.15s ease, background 0.15s ease;
}
.related-item:hover,
.related-item:focus-within {
  border-color: #bfdbfe;
  background: #eff6ff;
}
.related-link {
  display: flex;
  gap: 12px;
  align-items: center;
  text-decoration: none;
  color: inherit;
  background: transparent;
  border: none;
  padding: 0;
}
.related-link:hover,
.related-link:focus-visible {
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
.related-excerpt {
  margin: 8px 0 0;
  font-size: 13px;
  line-height: 1.65;
  color: #64748b;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}
.related-excerpt.expanded {
  display: block;
  -webkit-line-clamp: unset;
  overflow: visible;
}
.related-excerpt-toggle {
  margin-top: 4px;
  padding: 0;
  border: none;
  background: none;
  color: #2563eb;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.related-excerpt-toggle:hover { color: #1d4ed8; text-decoration: underline; }
.related-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  align-items: center;
  margin-top: 14px;
}
.related-more {
  display: inline-block;
  font-size: 13px;
  font-weight: 600;
  color: #2563eb;
  text-decoration: none;
}
.related-register {
  display: inline-block;
  font-size: 13px;
  font-weight: 600;
  color: #0f766e;
  text-decoration: none;
}
.related-register:hover,
.related-register:focus-visible {
  text-decoration: underline;
  outline: none;
}
.guest-cta-hint {
  margin: 0 0 10px;
  font-size: 13px;
  color: #64748b;
  text-align: center;
}
.sticky-cta { display: none; }
.sticky-hint {
  margin: 0 0 8px;
  font-size: 12px;
  color: #64748b;
  text-align: center;
}
@media (max-width: 640px) {
  .reader-page { padding: 20px 14px 88px; }
  .article { padding: 20px 16px; border-radius: 12px; }
  .article-header { gap: 12px; }
  .article-cover { width: 72px; height: 96px; }
  h1 { font-size: 20px; }
  .body-text { font-size: 15px; line-height: 1.9; }
  .related { margin-top: 28px; padding-top: 20px; }
  .sticky-cta {
    display: block;
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 40;
    padding: 12px 16px calc(12px + env(safe-area-inset-bottom, 0px));
    background: rgba(255, 255, 255, 0.96);
    border-top: 1px solid #e8f0fa;
    box-shadow: 0 -6px 20px rgba(15, 23, 42, 0.06);
  }
  .btn-cta.sticky {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    min-height: 48px;
    text-align: center;
    padding: 14px 18px;
    box-sizing: border-box;
    font-size: 16px;
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  .reader-page:has(.sticky-hint) { padding-bottom: 120px; }
}
</style>
