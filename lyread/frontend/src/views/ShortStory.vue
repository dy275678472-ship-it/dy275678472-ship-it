<template>
  <div class="short-page">
    <header class="hero">
      <img :src="images.features.short" alt="短故事" width="40" height="40" />
      <h1>短故事 · 快速生成</h1>
      <p>选题材、写灵感，AI 一键生成完整短篇（约 3000 字，消耗 15 点）</p>
    </header>

    <section v-if="samples.length" class="samples" aria-label="公开案例节选">
      <h2>先读一段真实生成节选</h2>
      <p class="samples-note">以下来自平台公开案例，无需登录即可浏览</p>
      <div class="sample-grid">
        <article v-for="s in samples" :key="s.id" class="sample-card">
          <h3>{{ s.title }}</h3>
          <p class="sample-meta">{{ s.category || '短篇' }} · {{ formatWords(s.word_count) }}</p>
          <p class="sample-excerpt">{{ s.excerpt }}</p>
          <router-link :to="`/case/${s.id}`" class="sample-link">阅读全文 →</router-link>
        </article>
      </div>
    </section>
    <section v-else class="samples samples-empty" aria-label="暂无案例节选">
      <h2>先读热门，再一键生成</h2>
      <p class="samples-note">公开节选暂时不可用时，可先去热门逛逛，或直接注册开写（送 30 点）</p>
      <div class="samples-empty-actions">
        <router-link
          to="/trending"
          class="sample-link"
          @click="trackEvent('story_empty_trending', { category: 'funnel', label: 'no_samples' })"
        >去热门看看 →</router-link>
        <router-link
          :to="emptyPrimaryTo"
          class="btn-gate"
          @click="trackEvent('story_empty_register', { category: 'conversion', label: loggedIn ? 'workspace' : 'no_samples' })"
        >{{ loggedIn ? '去创作台开写' : '免费注册开始写' }}</router-link>
      </div>
    </section>

    <div v-if="!loggedIn" class="gate-banner">
      <div>
        <strong>预览模式</strong>
        <span>可自由选题材与灵感；生成短篇需注册（送 30 点）</span>
      </div>
      <router-link class="btn-gate" :to="registerTo">免费注册开始写</router-link>
    </div>

    <div v-if="creditsLow" class="credits-banner" role="status">
      <span>点数不足 · 失败不扣点</span>
      <button
        type="button"
        class="btn-claim-inline"
        :disabled="claiming || claimDone"
        @click="claimDailyInline"
      >
        {{ claiming ? '领取中...' : (claimDone ? '今日已领取' : '领取今日免费 5 点') }}
      </button>
      <router-link to="/pricing" @click="trackEvent('story_recharge_click', { category: 'conversion', label: '402' })">充值</router-link>
      <router-link to="/wallet">点数中心</router-link>
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
        <button type="button" class="btn-secondary" @click="shuffleTemplates">换一批模板</button>
        <button type="button" class="btn-secondary" :disabled="busy" @click="generateMoreIdeas">AI 生成更多</button>
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

      <button class="btn-generate" :disabled="busy || (loggedIn && !canGenerate)" @click="generate">
        {{ generateLabel }}
      </button>
      <p v-if="!loggedIn" class="gate-hint">点击后将引导注册；注册送 30 点，生成一篇约 15 点</p>
      <p v-if="error" class="error">{{ error }}</p>
    </section>

    <section class="panel result" v-else>
      <div class="result-head">
        <h2>{{ result.title }}</h2>
        <span>{{ result.word_count }} 字</span>
      </div>
      <pre class="content">{{ result.content }}</pre>
      <p class="continue-hint">短篇已成。想拉成长篇？把同题材/灵感带进创作台，继续大纲与章纲。</p>
      <div class="actions">
        <button class="btn-secondary" @click="reset">再写一篇</button>
        <button class="btn-primary" @click="saveToWorkspace">保存到创作台</button>
      </div>
      <div class="actions continue-row">
        <button type="button" class="btn-continue-long" @click="continueAsLongform">
          进创作台续写长篇 →
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storyApi, casesApi, creditsApi } from '../api'
import { IMAGES } from '../assets/images'
import { allTemplatesForGenre } from '../constants/creation'
import { pickRandom, mergeStringOptions } from '../utils/optionPool'
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
const claiming = ref(false)
const claimDone = ref(false)
const result = ref(null)
const samples = ref([])
const loggedIn = ref(!!localStorage.getItem('token'))

const genreLabel = computed(() => genreCustom.value || genreName.value || '都市')
const canGenerate = computed(() => (genreId.value || genreCustom.value?.trim()) && prompt.value?.trim())

/** Preserve guest draft across register so /story form is not blank after auth. */
function storyDraftRedirect() {
  const params = new URLSearchParams()
  if (genreCustom.value?.trim()) params.set('genreCustom', genreCustom.value.trim().slice(0, 40))
  else if (genreId.value) params.set('genre', String(genreId.value).slice(0, 40))
  if (genreName.value) params.set('genreName', String(genreName.value).slice(0, 40))
  if (prompt.value?.trim()) params.set('prompt', prompt.value.trim().slice(0, 500))
  if (godfinger.value) params.set('godfinger', String(godfinger.value).slice(0, 40))
  const qs = params.toString()
  return qs ? `/story?${qs}` : '/story'
}

const registerTo = computed(() => ({
  path: '/login',
  query: { mode: 'register', redirect: storyDraftRedirect() },
}))

/** Empty-samples CTA: guests register with draft redirect; authed users go write. */
const emptyPrimaryTo = computed(() => (
  loggedIn.value
    ? { path: '/workspace', query: { mode: 'new' } }
    : registerTo.value
))

const generateLabel = computed(() => {
  if (!loggedIn.value) return '免费注册并生成短篇'
  if (busy.value) return '生成中...'
  return '一键生成完整短篇（15 点）'
})

function formatWords(n) {
  if (!n) return '—'
  if (n >= 10000) return `${(n / 10000).toFixed(1)} 万字`
  return `${n} 字`
}

function requireAuth(action) {
  trackEvent('story_gate_click', { category: 'conversion', label: action })
  router.push(registerTo.value)
}

function restoreDraftFromQuery() {
  const q = route.query
  const str = (v) => (typeof v === 'string' ? v : '')
  if (str(q.prompt)) prompt.value = str(q.prompt).slice(0, 500)
  if (str(q.godfinger)) godfinger.value = str(q.godfinger).slice(0, 40)
  if (str(q.genreCustom)) {
    genreCustom.value = str(q.genreCustom).slice(0, 40)
    genreId.value = ''
    genreName.value = ''
  } else if (str(q.genre)) {
    genreId.value = str(q.genre).slice(0, 40)
    if (str(q.genreName)) genreName.value = str(q.genreName).slice(0, 40)
  }
}

function refreshTemplates() {
  ideaPool.value = mergeStringOptions(ideaPool.value, allTemplatesForGenre(genreId.value || 'default'))
  displayedTemplates.value = pickRandom(ideaPool.value, 4)
}

function shuffleTemplates() { refreshTemplates() }

async function generateMoreIdeas() {
  if (!loggedIn.value) {
    requireAuth('suggest_ideas')
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
    } else error.value = res?.detail || res?.error || '生成失败'
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
  if (!loggedIn.value) {
    requireAuth('generate_short')
    return
  }
  if (!canGenerate.value) {
    error.value = '请先选择题材并填写灵感'
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
      trackEvent('story_generate_ok', { category: 'creation' })
    } else if (res?.insufficient_credits || res?.status === 402) {
      creditsLow.value = true
      trackEvent('credits_low', { category: 'conversion', label: 'story' })
      error.value = res.detail || '点数不足，可先领取每日免费额度'
      refreshClaimState()
    } else {
      error.value = res?.error || res?.detail || '生成失败'
    }
  } finally { busy.value = false }
}

function reset() {
  result.value = null
  prompt.value = ''
}

async function refreshClaimState() {
  try {
    const bal = await creditsApi.balance()
    if (bal?.success) claimDone.value = !!bal.claimed_today
  } catch (_) { /* ignore */ }
}

async function claimDailyInline() {
  if (claiming.value || claimDone.value) return
  claiming.value = true
  trackEvent('story_claim_click', { category: 'conversion', label: '402_inline' })
  try {
    const res = await creditsApi.dailyClaim()
    if (res?.success) {
      claimDone.value = true
      const claimed = !!res.claimed
      trackEvent('story_claim_result', {
        category: 'conversion',
        label: claimed ? 'claimed' : 'already',
      })
      if (claimed) {
        creditsLow.value = false
        error.value = ''
        window.dispatchEvent(new Event('credits-changed'))
      } else {
        error.value = res.message || '今日已领取，请充值后续写'
      }
    } else {
      error.value = res?.detail || '领取失败，请稍后再试'
      trackEvent('story_claim_result', { category: 'conversion', label: 'fail' })
    }
  } catch (_) {
    error.value = '领取失败，请稍后再试'
    trackEvent('story_claim_result', { category: 'conversion', label: 'error' })
  } finally {
    claiming.value = false
  }
}

async function saveToWorkspace() {
  if (!result.value) return
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

/** 短篇成功 → 创作台向导：预填书名/题材/灵感，引导扩写长篇 */
function continueAsLongform() {
  if (!result.value) return
  trackEvent('story_continue_longform', { category: 'conversion', label: 'post_generate' })
  const query = {
    mode: 'new',
    generatedTitle: String(result.value.title || '').slice(0, 80),
    type: String(genreLabel.value || '').slice(0, 40),
    prompt: String(prompt.value || result.value.title || '').slice(0, 500),
  }
  router.push({ path: '/workspace', query })
}

onMounted(async () => {
  loggedIn.value = !!localStorage.getItem('token')
  restoreDraftFromQuery()
  const [g, gf, casesRes] = await Promise.all([
    storyApi.suggestGenres(),
    storyApi.godfingers(),
    casesApi.list(6),
  ])
  if (g?.success) genres.value = g.genres || []
  if (gf?.success) godfingers.value = gf.godfingers || []
  const list = casesRes?.cases || []
  samples.value = list.filter((c) => c.excerpt).slice(0, 3)
  if (genreId.value && genres.value.length) {
    const matched = genres.value.find((x) => x.id === genreId.value)
    if (matched) {
      genreName.value = matched.name
      genreCustom.value = ''
    }
  }
  refreshTemplates()
  if (route.query.prompt || route.query.genre || route.query.genreCustom) {
    trackEvent('story_draft_restored', { category: 'conversion', label: loggedIn.value ? 'auth' : 'anon' })
  }
  trackEvent('story_teaser_view', { category: 'growth', label: loggedIn.value ? 'auth' : 'anon' })
})
</script>

<style scoped>
.short-page { max-width: 760px; margin: 0 auto; padding: 32px 20px 80px; }
.hero { text-align: center; margin-bottom: 28px; }
.hero h1 { font-size: 26px; margin: 12px 0 8px; }
.hero p { color: #5a6a7a; }
.samples { margin-bottom: 24px; }
.samples h2 { font-size: 18px; margin: 0 0 6px; color: #1e293b; }
.samples-note { font-size: 13px; color: #64748b; margin: 0 0 14px; }
.samples-empty {
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  border: 1px dashed #dbe7f5;
  border-radius: 14px;
  padding: 16px 18px 18px;
}
.samples-empty-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}
.sample-grid { display: grid; gap: 12px; }
@media (min-width: 720px) {
  .sample-grid { grid-template-columns: repeat(3, 1fr); }
}
.sample-card {
  background: #fff;
  border: 1px solid #e8f0fa;
  border-radius: 14px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 100%;
}
.sample-card h3 { font-size: 15px; margin: 0; color: #0f172a; line-height: 1.4; }
.sample-meta { font-size: 12px; color: #94a3b8; margin: 0; }
.sample-excerpt {
  font-size: 13px;
  color: #475569;
  line-height: 1.7;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}
.sample-link {
  font-size: 13px;
  font-weight: 600;
  color: #2563eb;
  text-decoration: none;
  margin-top: 4px;
}
.gate-banner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  margin-bottom: 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #eff6ff, #f8fafc);
  border: 1px solid #dbeafe;
}
.gate-banner strong { display: block; font-size: 14px; color: #1e40af; margin-bottom: 2px; }
.gate-banner span { font-size: 13px; color: #475569; }
.btn-gate {
  padding: 10px 16px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4da1ff, #2563eb);
  color: #fff;
  font-weight: 700;
  font-size: 13px;
  text-decoration: none;
  white-space: nowrap;
}
.gate-hint { font-size: 12px; color: #64748b; margin-top: 8px; text-align: center; }
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
.credits-banner { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; padding: 12px; background: #fff7ed; border-radius: 10px; margin-bottom: 16px; font-size: 13px; color: #9a3412; }
.credits-banner a { color: #2563eb; font-weight: 600; text-decoration: none; }
.btn-claim-inline {
  padding: 6px 12px; border-radius: 8px; border: none; cursor: pointer; font-size: 13px; font-weight: 600;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff;
}
.btn-claim-inline:disabled { opacity: 0.65; cursor: not-allowed; }
.result-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.content { white-space: pre-wrap; line-height: 1.9; font-size: 15px; color: #1e2a3a; max-height: 60vh; overflow: auto; }
.continue-hint {
  margin: 14px 0 0; padding: 10px 12px; border-radius: 10px;
  background: linear-gradient(135deg, #eff6ff, #f8fafc); border: 1px solid #dbeafe;
  font-size: 13px; color: #334155; line-height: 1.5;
}
.actions { display: flex; gap: 10px; margin-top: 16px; }
.actions .btn-primary { width: auto; flex: 1; }
.continue-row { margin-top: 10px; }
.btn-continue-long {
  width: 100%; padding: 12px 16px; border-radius: 12px; cursor: pointer; font-weight: 700; font-size: 14px;
  border: 1px solid #93c5fd; background: #fff; color: #1d4ed8;
}
.btn-continue-long:hover { background: #eff6ff; }
</style>
