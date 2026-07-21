<template>
  <div class="wizard">
    <div v-if="showHint" class="wizard-hint" role="status">
      <div>
        <strong>首次创作提示</strong>
        <p>共 7 步：题材 → 灵感 → 书名 → 设定 → 大纲 → 章纲 → 正文。新用户注册送 30 点（约可 AI 续写 3 章）；每步可点 AI 或手填，失败不扣点，点数不足会提示充值。</p>
      </div>
      <button type="button" class="hint-dismiss" @click="dismissHint">知道了</button>
    </div>
    <nav class="wizard-steps">
      <button
        v-for="(s, i) in steps"
        :key="s.id"
        type="button"
        class="step-pill"
        :class="{ active: step === i, done: i < step }"
        @click="i <= step && (step = i)"
      >
        <span class="num">{{ i + 1 }}</span>
        <span class="label">{{ s.title }}</span>
      </button>
    </nav>

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
      <router-link to="/pricing" @click="trackEvent('wizard_recharge_click', { category: 'conversion', label: '402' })">充值</router-link>
      <router-link to="/wallet">点数中心</router-link>
    </div>

    <!-- Step 0: Genre -->
    <section v-show="step === 0" class="wizard-panel">
      <h2>选择题材</h2>
      <p class="hint">点选推荐题材，或下方手动输入 · 两者可任选</p>
      <div class="action-row">
        <button type="button" class="btn-secondary" @click="shuffleGenres">🎲 换一批推荐</button>
      </div>
      <div class="chip-grid">
        <button
          v-for="g in displayedGenres"
          :key="g.id"
          type="button"
          class="chip"
          :class="{ selected: draft.genreId === g.id && !draft.genreCustom }"
          @click="pickGenre(g)"
        >
          <strong>{{ g.name }}</strong>
          <span>热度 {{ g.hot }}</span>
          <em>{{ (g.tags || []).join(' · ') }}</em>
        </button>
      </div>
      <label class="field-label">或手动输入题材</label>
      <input v-model="draft.genreCustom" class="input" placeholder="例如：科幻末世、悬疑推理..." @input="onCustomGenre" />
    </section>

    <!-- Step 1: Idea -->
    <section v-show="step === 1" class="wizard-panel">
      <h2>故事灵感</h2>
      <p class="hint">点选灵感模板、AI 生成更多，或直接手动输入</p>
      <div class="action-row">
        <button type="button" class="btn-secondary" @click="shuffleIdeas">🎲 换一批模板</button>
        <button type="button" class="btn-secondary" :disabled="busy" @click="generateMoreIdeas">
          {{ busy ? '生成中...' : `✨ AI 生成更多（${prices.title || 1} 点）` }}
        </button>
      </div>
      <div class="template-list">
        <button
          v-for="(t, i) in displayedIdeas"
          :key="i"
          type="button"
          class="template-card"
          :class="{ selected: draft.intro === t }"
          @click="draft.intro = t"
        >{{ t }}</button>
      </div>
      <label class="field-label">或手动输入 / 编辑灵感</label>
      <textarea v-model="draft.intro" class="textarea" rows="4" placeholder="描述你的故事核心冲突、主角处境..." />
    </section>

    <!-- Step 2: Title -->
    <section v-show="step === 2" class="wizard-panel">
      <h2>书名</h2>
      <p class="hint">从 AI 推荐中点选，不够可继续随机生成；也可完全手动输入</p>
      <div class="action-row">
        <button class="btn-primary" :disabled="busy" @click="generateTitles(false)">
          {{ busy ? '生成中...' : `AI 生成书名（${prices.title || 1} 点）` }}
        </button>
        <button class="btn-secondary" :disabled="busy || !draft.titleCandidates.length" @click="generateTitles(true)">
          {{ busy ? '生成中...' : `🎲 再随机 5 个（${prices.title || 1} 点）` }}
        </button>
      </div>
      <p v-if="draft.titleCandidates.length" class="count-hint">已积累 {{ draft.titleCandidates.length }} 个候选，点击选用</p>
      <div v-if="draft.titleCandidates.length" class="title-grid">
        <button
          v-for="(t, i) in draft.titleCandidates"
          :key="`${t.title}-${i}`"
          type="button"
          class="title-card"
          :class="{ selected: draft.title === t.title }"
          @click="selectTitle(t)"
        >
          <strong>{{ t.title }}</strong>
          <span>{{ t.hook || t.description }}</span>
        </button>
      </div>
      <label class="field-label">最终书名（可手动修改）</label>
      <input v-model="draft.title" class="input" placeholder="输入或点选上方书名" />
    </section>

    <!-- Step 3: Setup -->
    <section v-show="step === 3" class="wizard-panel">
      <h2>金手指与爽点</h2>
      <p class="hint">点选推荐，或点「随机搭配」；爽点可多选</p>
      <div class="action-row">
        <button type="button" class="btn-secondary" @click="randomSetup">🎲 随机搭配一套</button>
      </div>
      <h3>金手指（点选或随机）</h3>
      <div class="chip-grid small">
        <button
          v-for="g in godfingers"
          :key="g.id"
          type="button"
          class="chip"
          :class="{ selected: draft.godfinger === g.id }"
          @click="draft.godfinger = g.id"
        >
          {{ g.icon }} {{ g.name }}
        </button>
      </div>
      <input v-model="draft.godfingerCustom" class="input" placeholder="或手动输入金手指设定，如：时间回溯能力" />
      <h3>爽点标签（多选）</h3>
      <div class="chip-grid small">
        <button
          v-for="hp in hotPointOptions"
          :key="hp"
          type="button"
          class="chip"
          :class="{ selected: draft.hotPoints.includes(hp) }"
          @click="toggleHot(hp)"
        >{{ hp }}</button>
      </div>
      <h3>等级体系（可选）</h3>
      <select v-model="draft.levelSystem" class="input">
        <option value="">不指定</option>
        <option v-for="ls in levelSystems" :key="ls.id" :value="ls.id">{{ ls.name }}</option>
      </select>
    </section>

    <!-- Step 4: Outline -->
    <section v-show="step === 4" class="wizard-panel">
      <h2>故事大纲</h2>
      <div class="action-row">
        <button class="btn-primary" :disabled="busy" @click="generateOutline(false)">
          {{ busy ? '生成中...' : `AI 生成大纲（${prices.outline || 3} 点）` }}
        </button>
        <button class="btn-secondary" :disabled="busy || !draft.outlineText" @click="generateOutline(true)">
          🎲 换一版大纲
        </button>
      </div>
      <label class="field-label">大纲内容（可手动编辑）</label>
      <textarea v-model="draft.outlineText" class="textarea code-area" rows="12" placeholder="大纲 JSON 或文字，可编辑" />
    </section>

    <!-- Step 5: Chapters -->
    <section v-show="step === 5" class="wizard-panel">
      <h2>章纲规划</h2>
      <div class="row">
        <label>章数 <input v-model.number="draft.chapterCount" type="number" min="3" max="30" class="input short" /></label>
        <button class="btn-primary" :disabled="busy" @click="generateChapterPlans(false)">
          {{ busy ? '生成中...' : `AI 生成章纲（${prices.chapters || 5} 点）` }}
        </button>
        <button class="btn-secondary" :disabled="busy || !draft.chapterPlans.length" @click="generateChapterPlans(true)">
          🎲 换一批章纲
        </button>
      </div>
      <ul v-if="draft.chapterPlans.length" class="chapter-plans">
        <li v-for="(ch, i) in draft.chapterPlans" :key="i">
          <input v-model="ch.title" class="input" />
          <input v-model="ch.hot_point" class="input short" placeholder="爽点" />
          <input v-model="ch.summary" class="input" placeholder="剧情要点" />
        </li>
      </ul>
    </section>

    <!-- Step 6: Write -->
    <section v-show="step === 6" class="wizard-panel">
      <h2>正文创作</h2>
      <div class="chip-grid small">
        <button
          v-for="st in writeStyles"
          :key="st.id"
          type="button"
          class="chip"
          :class="{ selected: draft.writeStyle === st.id }"
          @click="draft.writeStyle = st.id"
        >
          {{ st.name }}
        </button>
      </div>
      <textarea v-model="draft.chapterContent" class="textarea content-area" rows="14" placeholder="在此编辑正文，或点击下方 AI 续写" />
      <div class="action-row">
        <button class="btn-primary" :disabled="busy" @click="continueWriting">
          {{ busy ? '续写中...' : `AI 续写（${prices.continue || 10} 点）` }}
        </button>
        <button class="btn-secondary" :disabled="busy" @click="runConsistency">
          一致性检查（{{ prices.consistency || 2 }} 点）
        </button>
      </div>
      <pre v-if="consistencyReport" class="report">{{ consistencyReport }}</pre>
    </section>

    <p v-if="msg" class="msg" :class="{ err: msgErr }">{{ msg }}</p>

    <footer class="wizard-footer">
      <button v-if="step > 0" type="button" class="btn-secondary" @click="step--">上一步</button>
      <button v-if="step < 6" type="button" class="btn-primary" :disabled="!canNext" @click="step++">下一步</button>
      <button v-else type="button" class="btn-primary" :disabled="busy" @click="$emit('finish', buildPayload())">完成并保存</button>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { storyApi, creditsApi } from '../api'
import { HOT_POINTS, WRITE_STYLES, allTemplatesForGenre, WIZARD_STEPS } from '../constants/creation'
import { shuffleArray, pickRandom, mergeTitleCandidates, mergeStringOptions } from '../utils/optionPool'
import { trackEvent } from '../utils/analytics'

const HINT_KEY = 'lyread_wizard_hint_dismissed'

const props = defineProps({
  initial: { type: Object, default: () => ({}) },
})
defineEmits(['finish'])

const steps = WIZARD_STEPS
const step = ref(0)
const busy = ref(false)
const msg = ref('')
const msgErr = ref(false)
const creditsLow = ref(false)
const claiming = ref(false)
const claimDone = ref(false)
const showHint = ref(false)
const genres = ref([])
const allGenres = ref([])
const displayedGenres = ref([])
const displayedIdeas = ref([])
const ideaPool = ref([])
const godfingers = ref([])
const levelSystems = ref([])
const prices = ref({})
const consistencyReport = ref('')
const hotPointOptions = HOT_POINTS
const writeStyles = WRITE_STYLES

const draft = reactive({
  genreId: '',
  genreCustom: '',
  genreName: '',
  intro: '',
  title: '',
  titleCandidates: [],
  godfinger: '',
  godfingerCustom: '',
  hotPoints: ['打脸', '逆袭'],
  levelSystem: '',
  outlineText: '',
  chapterCount: 10,
  chapterPlans: [],
  writeStyle: 'shuang',
  chapterContent: '',
  ...props.initial,
})

const genreLabel = computed(() => draft.genreCustom?.trim() || draft.genreName || '都市')

function refreshIdeaPool() {
  const base = allTemplatesForGenre(draft.genreId || 'default')
  ideaPool.value = mergeStringOptions(ideaPool.value, base)
  displayedIdeas.value = pickRandom(ideaPool.value, 5)
}

function shuffleGenres() {
  displayedGenres.value = pickRandom(allGenres.value.length ? allGenres.value : genres.value, 6)
}

function shuffleIdeas() {
  displayedIdeas.value = pickRandom(ideaPool.value.length ? ideaPool.value : allTemplatesForGenre(draft.genreId || 'default'), 5)
}

function onCustomGenre() {
  draft.genreId = ''
  draft.genreName = ''
}

function randomSetup() {
  if (godfingers.value.length) {
    const g = godfingers.value[Math.floor(Math.random() * godfingers.value.length)]
    draft.godfinger = g.id
    draft.godfingerCustom = ''
  }
  draft.hotPoints = pickRandom(HOT_POINTS, 3)
  if (levelSystems.value.length) {
    draft.levelSystem = levelSystems.value[Math.floor(Math.random() * levelSystems.value.length)].id
  }
  setMsg('已随机搭配一套设定，可继续微调')
}

const canNext = computed(() => {
  if (step.value === 0) return !!(draft.genreId || draft.genreCustom?.trim())
  if (step.value === 1) return !!draft.intro?.trim()
  if (step.value === 2) return !!draft.title?.trim()
  if (step.value === 3) return draft.hotPoints.length > 0
  return true
})

function setMsg(text, err = false) {
  msg.value = text
  msgErr.value = err
}

function handleErr(res, fallback) {
  if (res?.insufficient_credits || res?.status === 402) {
    creditsLow.value = true
    trackEvent('credits_low', { category: 'conversion', label: 'wizard' })
    setMsg(res.detail || '点数不足，可先领取每日免费额度', true)
    refreshClaimState()
    return true
  }
  setMsg(res?.error || res?.detail || fallback, true)
  return false
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
  trackEvent('wizard_claim_click', { category: 'conversion', label: '402_inline' })
  try {
    const res = await creditsApi.dailyClaim()
    if (res?.success) {
      claimDone.value = true
      const claimed = !!res.claimed
      trackEvent('wizard_claim_result', {
        category: 'conversion',
        label: claimed ? 'claimed' : 'already',
      })
      if (claimed) {
        creditsLow.value = false
        setMsg(res.message || '已领取今日免费 5 点，可继续创作', false)
        window.dispatchEvent(new Event('credits-changed'))
      } else {
        setMsg(res.message || '今日已领取，请充值后续写', true)
      }
    } else {
      setMsg(res?.detail || '领取失败，请稍后再试', true)
      trackEvent('wizard_claim_result', { category: 'conversion', label: 'fail' })
    }
  } catch (_) {
    setMsg('领取失败，请稍后再试', true)
    trackEvent('wizard_claim_result', { category: 'conversion', label: 'error' })
  } finally {
    claiming.value = false
  }
}

function pickGenre(g) {
  draft.genreId = g.id
  draft.genreName = g.name
  draft.genreCustom = ''
  ideaPool.value = [...allTemplatesForGenre(g.id)]
  displayedIdeas.value = pickRandom(ideaPool.value, 5)
}

function toggleHot(hp) {
  const i = draft.hotPoints.indexOf(hp)
  if (i >= 0) draft.hotPoints.splice(i, 1)
  else draft.hotPoints.push(hp)
}

function selectTitle(t) {
  draft.title = t.title
  if (t.hook) draft.intro = draft.intro || t.hook
}

async function generateMoreIdeas() {
  busy.value = true
  setMsg('')
  try {
    const res = await storyApi.suggestIdeas({
      genre: genreLabel.value,
      prompt: draft.intro,
      exclude: ideaPool.value,
      count: 5,
    })
    if (res?.success) {
      ideaPool.value = mergeStringOptions(ideaPool.value, res.ideas || [])
      displayedIdeas.value = pickRandom(ideaPool.value, 5)
      setMsg(`已新增灵感，共 ${ideaPool.value.length} 条可选`)
      window.dispatchEvent(new Event('credits-changed'))
    } else handleErr(res, '生成灵感失败')
  } finally { busy.value = false }
}

async function generateTitles(append = false) {
  busy.value = true
  setMsg('')
  try {
    const exclude = append ? draft.titleCandidates.map(t => t.title) : []
    const res = await storyApi.generateTitle({
      genre: genreLabel.value,
      prompt: draft.intro,
      exclude_titles: exclude,
      count: 5,
      variation: String(Date.now()),
    })
    if (res?.success) {
      const incoming = res.titles || [{ title: res.title, hook: res.description }]
      draft.titleCandidates = append
        ? mergeTitleCandidates(draft.titleCandidates, incoming)
        : incoming
      if (!draft.title && res.title) draft.title = res.title
      setMsg(append ? `已追加，共 ${draft.titleCandidates.length} 个书名可选` : '已生成候选书名，请点击选用')
      window.dispatchEvent(new Event('credits-changed'))
    } else handleErr(res, '生成书名失败')
  } finally { busy.value = false }
}

async function generateOutline(regenerate = false) {
  busy.value = true
  try {
    const res = await storyApi.generateOutline({
      title: draft.title,
      intro: draft.intro + (regenerate ? `\n（请换一种叙事角度，变化编号${Date.now()}）` : ''),
      genre: genreLabel.value,
      hot_points: draft.hotPoints,
      godfinger: draft.godfingerCustom || draft.godfinger,
      level_system: draft.levelSystem,
    })
    if (res?.success) {
      draft.outlineText = JSON.stringify(res.outline, null, 2)
      setMsg('大纲生成成功')
      window.dispatchEvent(new Event('credits-changed'))
    } else handleErr(res, '生成大纲失败')
  } finally { busy.value = false }
}

async function generateChapterPlans(regenerate = false) {
  let outline = {}
  try { outline = JSON.parse(draft.outlineText) } catch { setMsg('请先生成有效大纲', true); return }
  if (regenerate) outline = { ...outline, _variation: Date.now() }
  busy.value = true
  try {
    const res = await storyApi.generateChapters({ outline, chapter_count: draft.chapterCount })
    if (res?.success) {
      draft.chapterPlans = res.chapters || []
      setMsg(`已生成 ${draft.chapterPlans.length} 章章纲`)
      window.dispatchEvent(new Event('credits-changed'))
    } else handleErr(res, '生成章纲失败')
  } finally { busy.value = false }
}

async function continueWriting() {
  busy.value = true
  try {
    const style = writeStyles.find(s => s.id === draft.writeStyle)?.name || '网文爽文'
    const res = await storyApi.continue({
      story_id: props.initial?.storyId || null,
      content: draft.chapterContent,
      style,
      chapter_title: draft.title,
      context: buildContext(),
    })
    if (res?.success) {
      draft.chapterContent += (draft.chapterContent ? '\n\n' : '') + res.content
      setMsg(`续写成功 +${res.length} 字`)
      window.dispatchEvent(new Event('credits-changed'))
    } else handleErr(res, '续写失败')
  } finally { busy.value = false }
}

async function runConsistency() {
  busy.value = true
  consistencyReport.value = ''
  try {
    const res = await storyApi.consistencyCheck({
      story_id: props.initial?.storyId || null,
      content: draft.chapterContent,
      context: buildContext(),
    })
    if (res?.success) {
      consistencyReport.value = typeof res.report === 'string' ? res.report : JSON.stringify(res.report, null, 2)
      setMsg('一致性检查完成')
      window.dispatchEvent(new Event('credits-changed'))
    } else handleErr(res, '检查失败')
  } finally { busy.value = false }
}

function buildContext() {
  return `书名：${draft.title}\n题材：${genreLabel.value}\n简介：${draft.intro}\n金手指：${draft.godfinger}\n爽点：${draft.hotPoints.join(',')}`
}

function buildPayload() {
  let outline = draft.outlineText
  let chapters = '[]'
  if (draft.chapterPlans.length) {
    chapters = JSON.stringify(draft.chapterPlans.map((ch, i) => ({
      chapter: ch.chapter || i + 1,
      title: ch.title,
      hot_point: ch.hot_point,
      summary: ch.summary,
      content: i === 0 ? draft.chapterContent : (ch.content || ''),
    })))
  } else if (draft.chapterContent) {
    chapters = JSON.stringify([{ chapter: 1, title: '第1章', content: draft.chapterContent }])
  }
  const characters = JSON.stringify({
    godfinger: draft.godfingerCustom || draft.godfinger,
    hot_points: draft.hotPoints,
    level_system: draft.levelSystem,
    write_style: draft.writeStyle,
  })
  return {
    title: draft.title,
    genre: genreLabel.value,
    intro: draft.intro,
    outline,
    characters,
    chapters,
    status: 'draft',
  }
}

function dismissHint() {
  showHint.value = false
  try { localStorage.setItem(HINT_KEY, '1') } catch { /* ignore */ }
  trackEvent('wizard_hint_dismiss', { category: 'creation', label: 'first_run' })
}

onMounted(async () => {
  try { showHint.value = localStorage.getItem(HINT_KEY) !== '1' } catch { showHint.value = true }
  if (showHint.value) {
    trackEvent('wizard_hint_view', { category: 'creation', label: 'first_run' })
  }
  const [g, gf, ls, p] = await Promise.all([
    storyApi.suggestGenres(),
    storyApi.godfingers(),
    storyApi.levelSystems(),
    creditsApi.prices(),
  ])
  if (g?.success) {
    allGenres.value = g.genres || []
    genres.value = allGenres.value
    displayedGenres.value = pickRandom(allGenres.value, 6)
  }
  if (gf?.success) godfingers.value = gf.godfingers || []
  if (ls?.success) levelSystems.value = ls.systems || []
  if (p?.success) prices.value = p.prices || {}
  const init = props.initial || {}
  if (init.type) { draft.genreId = init.type; draft.genreName = init.type }
  if (init.prompt) draft.intro = init.prompt
  if (init.generatedTitle) draft.title = init.generatedTitle
  refreshIdeaPool()
})
</script>

<style scoped>
.wizard { max-width: 900px; }
.wizard-hint {
  display: flex; gap: 12px; align-items: flex-start; justify-content: space-between;
  padding: 12px 14px; margin-bottom: 14px; border-radius: 12px;
  background: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a5f;
}
.wizard-hint strong { display: block; font-size: 13px; margin-bottom: 4px; }
.wizard-hint p { margin: 0; font-size: 13px; line-height: 1.55; color: #334155; }
.hint-dismiss {
  flex-shrink: 0; padding: 6px 12px; border-radius: 8px; border: 1px solid #93c5fd;
  background: #fff; color: #2563eb; font-weight: 600; cursor: pointer; font-size: 12px;
}
.wizard-steps { display: flex; gap: 6px; overflow-x: auto; margin-bottom: 20px; padding-bottom: 4px; }
.step-pill {
  display: flex; align-items: center; gap: 6px; padding: 8px 12px; border-radius: 999px;
  border: 1px solid #e2e8f0; background: #fff; cursor: pointer; white-space: nowrap; font-size: 12px;
}
.step-pill.active { background: #2563eb; color: #fff; border-color: #2563eb; }
.step-pill.done { border-color: #93c5fd; }
.step-pill .num { font-weight: 800; }
.wizard-panel { background: #fff; border-radius: 14px; padding: 20px; border: 1px solid #e8f0fa; margin-bottom: 16px; }
.wizard-panel h2 { font-size: 18px; margin-bottom: 6px; }
.wizard-panel h3 { font-size: 14px; margin: 16px 0 8px; color: #475569; }
.field-label { display: block; font-size: 12px; color: #64748b; margin: 12px 0 6px; font-weight: 600; }
.count-hint { font-size: 12px; color: #64748b; margin: 10px 0 4px; }
.hint { color: #64748b; font-size: 13px; margin-bottom: 14px; }
.chip-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; margin-bottom: 14px; }
.chip-grid.small { grid-template-columns: repeat(auto-fill, minmax(88px, 1fr)); }
.chip {
  text-align: left; padding: 10px 12px; border-radius: 10px; border: 1px solid #e2e8f0;
  background: #fff; cursor: pointer; font-size: 13px;
}
.chip.selected { border-color: #2563eb; background: #eff6ff; }
.chip strong { display: block; }
.chip span { font-size: 11px; color: #94a3b8; }
.chip em { display: block; font-size: 11px; color: #64748b; font-style: normal; margin-top: 4px; }
.input, .textarea {
  width: 100%; padding: 10px 12px; border: 1px solid #dbeafe; border-radius: 10px;
  font-size: 14px; margin-bottom: 10px;
}
.input.short { max-width: 120px; }
.textarea.code-area { font-family: ui-monospace, monospace; font-size: 12px; }
.textarea.content-area { min-height: 280px; line-height: 1.8; }
.template-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
.template-card {
  text-align: left; padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0;
  background: #f8fafc; cursor: pointer; font-size: 13px; line-height: 1.5;
}
.template-card.selected { border-color: #2563eb; background: #eff6ff; }
.title-grid { display: grid; gap: 10px; margin: 14px 0; }
.title-card {
  text-align: left; padding: 14px; border-radius: 12px; border: 1px solid #e2e8f0; background: #fff; cursor: pointer;
}
.title-card.selected { border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37,99,235,0.15); }
.title-card strong { display: block; margin-bottom: 4px; color: #1e2a3a; }
.title-card span { font-size: 12px; color: #64748b; }
.chapter-plans { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.chapter-plans li { display: grid; grid-template-columns: 1fr 100px 1fr; gap: 8px; }
.row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; }
.action-row { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
.btn-primary, .btn-secondary {
  padding: 10px 18px; border-radius: 10px; border: none; font-weight: 600; cursor: pointer; font-size: 14px;
}
.btn-primary { background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: #f1f5f9; color: #334155; }
.wizard-footer { display: flex; gap: 10px; justify-content: flex-end; margin-top: 8px; }
.msg { font-size: 13px; color: #16a34a; margin: 8px 0; }
.msg.err { color: #ef4444; }
.credits-banner {
  display: flex; gap: 10px; align-items: center; flex-wrap: wrap; padding: 10px 14px; margin-bottom: 12px;
  background: #fff7ed; border: 1px solid #fed7aa; border-radius: 10px; font-size: 13px; color: #9a3412;
}
.credits-banner a { color: #2563eb; font-weight: 600; text-decoration: none; }
.btn-claim-inline {
  padding: 6px 12px; border-radius: 8px; border: none; cursor: pointer; font-size: 13px; font-weight: 600;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff;
}
.btn-claim-inline:disabled { opacity: 0.65; cursor: not-allowed; }
.report {
  margin-top: 12px; padding: 12px; background: #f8fafc; border-radius: 10px;
  font-size: 12px; white-space: pre-wrap; max-height: 200px; overflow: auto;
}
@media (max-width: 768px) {
  .chapter-plans li { grid-template-columns: 1fr; }
  .wizard-steps .label { display: none; }
}
</style>
