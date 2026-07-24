<template>
  <div class="short-page">
    <header class="hero">
      <img :src="images.features.short" alt="短故事" width="40" height="40" />
      <h1>短故事 · 快速生成</h1>
      <p>选题材、写灵感，AI 一键生成完整短篇（约 3000 字，消耗 15 点）</p>
      <p v-if="!isLoggedIn" class="guest-hint">注册送 30 点，约可生成 2 篇短故事</p>
      <router-link
        v-if="!isLoggedIn"
        :to="guestRegisterLink"
        class="btn-register"
        @click="trackEvent('story_guest_register', { category: 'conversion', label: 'hero' })"
      >免费注册开写（送 30 点）→</router-link>
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
        @click="onStoryResumeClick"
      >继续读 →</router-link>
    </div>

    <div v-if="creditsLow" class="credits-banner">
      <span>点数不足</span>
      <template v-if="isLoggedIn">
        <router-link to="/wallet">领每日免费 5 点</router-link>
        <router-link to="/pricing">充值</router-link>
      </template>
      <router-link
        v-else
        :to="guestRegisterLink"
        @click="trackEvent('story_guest_register', { category: 'conversion', label: 'credits_banner' })"
      >注册领 30 点 →</router-link>
    </div>

    <section class="panel" v-if="!result">
      <h2>1. 选择题材</h2>
      <div class="chip-grid">
        <button
          v-for="g in genres"
          :key="g.id"
          type="button"
          class="chip"
          :class="{ selected: genreId === g.id }"
          @click="pickGenre(g)"
        >{{ g.name }}</button>
      </div>
      <input v-model="genreCustom" class="input" placeholder="或自定义题材" @input="genreId = ''" />

      <h2>2. 故事灵感</h2>
      <div class="action-row">
        <button type="button" class="btn-secondary" @click="shuffleTemplates">🎲 换一批模板</button>
        <button type="button" class="btn-secondary" :disabled="busy" @click="generateMoreIdeas">✨ AI 生成更多</button>
      </div>
      <div class="templates">
        <button v-for="(t, i) in displayedTemplates" :key="i" type="button" class="tpl" @click="prompt = t">{{ t }}</button>
      </div>
      <label class="lbl">或手动输入</label>
      <textarea v-model="prompt" class="textarea" rows="4" placeholder="描述你想写的短故事..." />

      <h2>3. 金手指（可选）</h2>
      <div class="chip-grid small">
        <button
          v-for="g in godfingers"
          :key="g.id"
          type="button"
          class="chip"
          :class="{ selected: godfinger === g.id }"
          @click="godfinger = g.id"
        >{{ g.icon }} {{ g.name }}</button>
      </div>

      <button class="btn-generate" :disabled="busy || !canGenerate" @click="generate">
        {{ busy ? '生成中...' : '一键生成完整短篇（15 点）' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </section>

    <section class="panel result" v-else>
      <div class="result-head">
        <h2>{{ result.title }}</h2>
        <span>{{ result.word_count }} 字</span>
      </div>
      <pre class="content">{{ result.content }}</pre>
      <div class="actions">
        <button class="btn-secondary" @click="reset">再写一篇</button>
        <button class="btn-primary" @click="saveToWorkspace">保存到创作台</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storyApi } from '../api'
import { IMAGES } from '../assets/images'
import { templatesForGenre, allTemplatesForGenre } from '../constants/creation'
import { pickRandom, mergeStringOptions } from '../utils/optionPool'
import { withNoChargeHint } from '../utils/format'
import { findLatestResumeProgress } from '../utils/caseProgress'
import { trackEvent } from '../utils/analytics'

const route = useRoute()
const router = useRouter()
const images = IMAGES
const genres = ref([])
const godfingers = ref([])
const genreId = ref('')
const genreCustom = ref('')
const genreName = ref('')
const prompt = ref('')
const godfinger = ref('')
const ideaPool = ref([])
const displayedTemplates = ref([])
const busy = ref(false)
const error = ref('')
const creditsLow = ref(false)
const result = ref(null)
const resumeBanner = ref(null)
const isLoggedIn = computed(() => typeof localStorage !== 'undefined' && !!localStorage.getItem('token'))

function refreshResumeBanner() {
  const hit = findLatestResumeProgress()
  resumeBanner.value = hit
    ? {
        id: hit.id,
        title: hit.title,
        category: hit.category,
        pct: Math.round(hit.ratio * 100),
      }
    : null
}

function onStoryResumeClick() {
  const b = resumeBanner.value
  trackEvent('story_resume_click', {
    category: 'engagement',
    label: b?.title || '',
    value: Number(b?.id) || 0,
  })
}

/** 游客注册回流：保留题材/灵感/金手指，缩短 /story → 注册 → 再生成路径 */
function buildStoryRedirect() {
  const params = new URLSearchParams()
  if (genreId.value) params.set('genreId', genreId.value)
  if (genreName.value) params.set('genreName', genreName.value.slice(0, 40))
  const custom = (genreCustom.value || '').trim()
  if (custom) params.set('genreCustom', custom.slice(0, 40))
  const p = (prompt.value || '').trim()
  if (p) params.set('prompt', p.slice(0, 500))
  if (godfinger.value) params.set('godfinger', String(godfinger.value).slice(0, 40))
  const qs = params.toString()
  return qs ? `/story?${qs}` : '/story'
}

const guestRegisterLink = computed(() => ({
  path: '/login',
  query: { mode: 'register', redirect: buildStoryRedirect() },
}))

function applyDeepLinkQuery(q) {
  if (!q || typeof q !== 'object') return
  const gid = typeof q.genreId === 'string' ? q.genreId.trim() : ''
  const gname = typeof q.genreName === 'string' ? q.genreName.trim() : ''
  const gcustom = typeof q.genreCustom === 'string' ? q.genreCustom.trim() : ''
  const type = typeof q.type === 'string' ? q.type.trim() : ''
  const p = typeof q.prompt === 'string' ? q.prompt.trim() : ''
  const gf = typeof q.godfinger === 'string' ? q.godfinger.trim() : ''
  if (gid) genreId.value = gid
  if (gname) genreName.value = gname
  if (gcustom) {
    genreCustom.value = gcustom
    genreId.value = ''
  } else if (!gid && type) {
    genreCustom.value = type
    genreName.value = type
  }
  if (p) prompt.value = p.slice(0, 500)
  if (gf) godfinger.value = gf
}

const templates = computed(() => templatesForGenre(genreId.value || 'default'))
const genreLabel = computed(() => genreCustom.value || genreName.value || '都市')
const canGenerate = computed(() => (genreId.value || genreCustom.value?.trim()) && prompt.value?.trim())

function refreshTemplates() {
  ideaPool.value = mergeStringOptions(ideaPool.value, allTemplatesForGenre(genreId.value || 'default'))
  displayedTemplates.value = pickRandom(ideaPool.value, 4)
}

function shuffleTemplates() { refreshTemplates() }

async function generateMoreIdeas() {
  if (!isLoggedIn.value) {
    trackEvent('story_guest_register', { category: 'conversion', label: 'suggest_ideas' })
    router.push(guestRegisterLink.value)
    return
  }
  busy.value = true
  error.value = ''
  try {
    const res = await storyApi.suggestIdeas({ genre: genreLabel.value, prompt: prompt.value, exclude: ideaPool.value, count: 4 })
    if (res?.success) {
      ideaPool.value = mergeStringOptions(ideaPool.value, res.ideas || [])
      displayedTemplates.value = pickRandom(ideaPool.value, 4)
      window.dispatchEvent(new Event('credits-changed'))
    } else error.value = withNoChargeHint(res?.detail || res?.error, '生成失败')
  } finally { busy.value = false }
}

function pickGenre(g) {
  genreId.value = g.id
  genreName.value = g.name
  genreCustom.value = ''
  ideaPool.value = [...allTemplatesForGenre(g.id)]
  displayedTemplates.value = pickRandom(ideaPool.value, 4)
}

async function generate() {
  if (!isLoggedIn.value) {
    trackEvent('story_guest_register', { category: 'conversion', label: 'generate_gate' })
    router.push(guestRegisterLink.value)
    return
  }
  busy.value = true
  error.value = ''
  creditsLow.value = false
  try {
    const res = await storyApi.generateShort({
      genre: genreLabel.value,
      prompt: prompt.value,
      godfinger: godfinger.value,
      hot_points: ['反转', '共鸣'],
    })
    if (res?.success) {
      result.value = res
      window.dispatchEvent(new Event('credits-changed'))
    } else if (res?.status === 401) {
      trackEvent('story_guest_register', { category: 'conversion', label: '401' })
      router.push(guestRegisterLink.value)
    } else if (res?.insufficient_credits || res?.status === 402) {
      creditsLow.value = true
      error.value = res.detail || '点数不足'
    } else {
      error.value = withNoChargeHint(res?.error || res?.detail, '生成失败')
    }
  } finally { busy.value = false }
}

function reset() {
  result.value = null
  prompt.value = ''
}

async function saveToWorkspace() {
  if (!result.value) return
  if (!isLoggedIn.value) {
    router.push(guestRegisterLink.value)
    return
  }
  const res = await storyApi.save({
    title: result.value.title,
    genre: genreLabel.value,
    intro: prompt.value,
    chapters: JSON.stringify([{ chapter: 1, title: '全文', content: result.value.content }]),
    status: 'draft',
  })
  if (res?.success) router.push(`/workspace?story=${res.story_id}`)
  else error.value = res?.detail || '保存失败'
}

onMounted(async () => {
  applyDeepLinkQuery(route.query)
  refreshResumeBanner()
  const [g, gf] = await Promise.all([storyApi.suggestGenres(), storyApi.godfingers()])
  if (g?.success) genres.value = g.genres || []
  if (gf?.success) godfingers.value = gf.godfingers || []
  // 深链 genreId 与目录对齐；未知 id 时回退到 genreName/custom
  if (genreId.value && genres.value.length) {
    const matched = genres.value.find((x) => x.id === genreId.value)
    if (matched) {
      genreName.value = matched.name
      genreCustom.value = ''
    } else if (!genreCustom.value) {
      genreCustom.value = genreName.value || genreId.value
      genreId.value = ''
    }
  }
  refreshTemplates()
  if (route.query.prompt || route.query.genreId || route.query.genreCustom || route.query.genreName) {
    trackEvent('story_intent_resume', { category: 'funnel', label: isLoggedIn.value ? 'logged_in' : 'guest' })
  }
})
</script>

<style scoped>
.short-page { max-width: 760px; margin: 0 auto; padding: 32px 20px 80px; }
.hero { text-align: center; margin-bottom: 28px; }
.guest-hint { color: #64748b; font-size: 13px; margin: 8px 0 12px; }
.btn-register {
  display: inline-block; padding: 12px 20px; border-radius: 12px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff;
  font-weight: 700; text-decoration: none; font-size: 14px;
}
.hero h1 { font-size: 26px; margin: 12px 0 8px; }
.hero p { color: #5a6a7a; }
.resume-banner {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  margin: 0 0 20px; padding: 14px 18px;
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
@media (max-width: 640px) {
  .resume-banner { flex-direction: column; align-items: stretch; text-align: left; }
  .resume-go { text-align: center; }
}
.panel { background: #fff; border-radius: 16px; padding: 24px; border: 1px solid #e8f0fa; }
.panel h2 { font-size: 16px; margin: 20px 0 10px; color: #334155; }
.panel h2:first-child { margin-top: 0; }
.chip-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.chip-grid.small .chip { font-size: 12px; padding: 8px 10px; }
.chip { padding: 10px 14px; border-radius: 10px; border: 1px solid #e2e8f0; background: #fff; cursor: pointer; }
.chip.selected { border-color: #2563eb; background: #eff6ff; }
.input, .textarea { width: 100%; padding: 10px 12px; border: 1px solid #dbeafe; border-radius: 10px; font-size: 14px; }
.lbl { display: block; font-size: 12px; color: #64748b; margin: 8px 0 6px; font-weight: 600; }
.action-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
.btn-secondary { padding: 8px 14px; border-radius: 8px; border: 1px solid #e2e8f0; background: #f8fafc; cursor: pointer; font-size: 13px; }
.templates { display: flex; flex-direction: column; gap: 8px; margin-bottom: 10px; }
.tpl { text-align: left; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0; background: #f8fafc; cursor: pointer; font-size: 13px; }
.btn-generate, .btn-primary, .btn-secondary {
  padding: 14px 20px; border-radius: 12px; border: none; font-weight: 700; cursor: pointer; margin-top: 16px;
}
.btn-generate, .btn-primary { background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; width: 100%; }
.btn-secondary { background: #f1f5f9; color: #334155; }
.error { color: #dc2626; font-size: 13px; margin-top: 10px; }
.credits-banner { display: flex; gap: 12px; padding: 12px; background: #fff7ed; border-radius: 10px; margin-bottom: 16px; font-size: 13px; }
.credits-banner a { color: #2563eb; font-weight: 600; text-decoration: none; }
.result-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.content { white-space: pre-wrap; line-height: 1.9; font-size: 15px; color: #1e2a3a; max-height: 60vh; overflow: auto; }
.actions { display: flex; gap: 10px; margin-top: 16px; }
.actions .btn-primary { width: auto; flex: 1; }
</style>
