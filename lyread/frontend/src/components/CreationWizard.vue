<template>
  <div class="wizard">
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

    <div v-if="creditsLow" class="credits-banner">
      <span>点数不足</span>
      <router-link to="/wallet">领每日免费</router-link>
      <router-link to="/pricing">充值</router-link>
    </div>

    <!-- Step 0: Genre -->
    <section v-show="step === 0" class="wizard-panel">
      <h2>选择题材</h2>
      <p class="hint">点击热门题材，或在下方输入自定义题材</p>
      <div class="chip-grid">
        <button
          v-for="g in genres"
          :key="g.id"
          type="button"
          class="chip"
          :class="{ selected: draft.genreId === g.id }"
          @click="pickGenre(g)"
        >
          <strong>{{ g.name }}</strong>
          <span>热度 {{ g.hot }}</span>
          <em>{{ (g.tags || []).join(' · ') }}</em>
        </button>
      </div>
      <input v-model="draft.genreCustom" class="input" placeholder="或输入自定义题材，如：科幻末世" @input="draft.genreId = ''" />
    </section>

    <!-- Step 1: Idea -->
    <section v-show="step === 1" class="wizard-panel">
      <h2>故事灵感</h2>
      <p class="hint">选一个灵感模板，或写下你自己的想法</p>
      <div class="template-list">
        <button
          v-for="(t, i) in ideaTemplates"
          :key="i"
          type="button"
          class="template-card"
          :class="{ selected: draft.intro === t }"
          @click="draft.intro = t"
        >{{ t }}</button>
      </div>
      <textarea v-model="draft.intro" class="textarea" rows="4" placeholder="描述你的故事核心冲突、主角处境..." />
    </section>

    <!-- Step 2: Title -->
    <section v-show="step === 2" class="wizard-panel">
      <h2>书名</h2>
      <p class="hint">AI 生成 5 个候选书名，点击选用或自行修改</p>
      <button class="btn-primary" :disabled="busy" @click="generateTitles">
        {{ busy ? '生成中...' : `AI 生成书名（${prices.title || 1} 点）` }}
      </button>
      <div v-if="draft.titleCandidates.length" class="title-grid">
        <button
          v-for="(t, i) in draft.titleCandidates"
          :key="i"
          type="button"
          class="title-card"
          :class="{ selected: draft.title === t.title }"
          @click="selectTitle(t)"
        >
          <strong>{{ t.title }}</strong>
          <span>{{ t.hook || t.description }}</span>
        </button>
      </div>
      <input v-model="draft.title" class="input" placeholder="最终书名" />
    </section>

    <!-- Step 3: Setup -->
    <section v-show="step === 3" class="wizard-panel">
      <h2>金手指与爽点</h2>
      <p class="hint">选择主角能力和故事爽点（可多选）</p>
      <h3>金手指</h3>
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
      <h3>爽点标签</h3>
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
      <button class="btn-primary" :disabled="busy" @click="generateOutline">
        {{ busy ? '生成中...' : `AI 生成大纲（${prices.outline || 3} 点）` }}
      </button>
      <textarea v-model="draft.outlineText" class="textarea code-area" rows="12" placeholder="大纲 JSON 或文字，可编辑" />
    </section>

    <!-- Step 5: Chapters -->
    <section v-show="step === 5" class="wizard-panel">
      <h2>章纲规划</h2>
      <div class="row">
        <label>章数 <input v-model.number="draft.chapterCount" type="number" min="3" max="30" class="input short" /></label>
        <button class="btn-primary" :disabled="busy" @click="generateChapterPlans">
          {{ busy ? '生成中...' : `AI 生成章纲（${prices.chapters || 5} 点）` }}
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
import { HOT_POINTS, WRITE_STYLES, templatesForGenre, WIZARD_STEPS } from '../constants/creation'

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
const genres = ref([])
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
  hotPoints: ['打脸', '逆袭'],
  levelSystem: '',
  outlineText: '',
  chapterCount: 10,
  chapterPlans: [],
  writeStyle: 'shuang',
  chapterContent: '',
  ...props.initial,
})

const ideaTemplates = computed(() => templatesForGenre(draft.genreId || 'default'))

const genreLabel = computed(() => draft.genreCustom || draft.genreName || '都市')

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
    setMsg(res.detail || '点数不足', true)
    return true
  }
  setMsg(res?.error || res?.detail || fallback, true)
  return false
}

function pickGenre(g) {
  draft.genreId = g.id
  draft.genreName = g.name
  draft.genreCustom = ''
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

async function generateTitles() {
  busy.value = true
  setMsg('')
  try {
    const res = await storyApi.generateTitle({ genre: genreLabel.value, prompt: draft.intro })
    if (res?.success) {
      draft.titleCandidates = res.titles || [{ title: res.title, hook: res.description }]
      if (!draft.title && res.title) draft.title = res.title
      setMsg('已生成候选书名，请点击选用')
      window.dispatchEvent(new Event('credits-changed'))
    } else handleErr(res, '生成书名失败')
  } finally { busy.value = false }
}

async function generateOutline() {
  busy.value = true
  try {
    const res = await storyApi.generateOutline({
      title: draft.title,
      intro: draft.intro,
      genre: genreLabel.value,
      hot_points: draft.hotPoints,
      godfinger: draft.godfinger,
      level_system: draft.levelSystem,
    })
    if (res?.success) {
      draft.outlineText = JSON.stringify(res.outline, null, 2)
      setMsg('大纲生成成功')
      window.dispatchEvent(new Event('credits-changed'))
    } else handleErr(res, '生成大纲失败')
  } finally { busy.value = false }
}

async function generateChapterPlans() {
  let outline = {}
  try { outline = JSON.parse(draft.outlineText) } catch { setMsg('请先生成有效大纲', true); return }
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
    godfinger: draft.godfinger,
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

onMounted(async () => {
  const [g, gf, ls, p] = await Promise.all([
    storyApi.suggestGenres(),
    storyApi.godfingers(),
    storyApi.levelSystems(),
    creditsApi.prices(),
  ])
  if (g?.success) genres.value = g.genres || []
  if (gf?.success) godfingers.value = gf.godfingers || []
  if (ls?.success) levelSystems.value = ls.systems || []
  if (p?.success) prices.value = p.prices || {}
  const init = props.initial || {}
  if (init.type) { draft.genreId = init.type; draft.genreName = init.type }
  if (init.prompt) draft.intro = init.prompt
  if (init.generatedTitle) draft.title = init.generatedTitle
})
</script>

<style scoped>
.wizard { max-width: 900px; }
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
  display: flex; gap: 12px; align-items: center; padding: 10px 14px; margin-bottom: 12px;
  background: #fff7ed; border: 1px solid #fed7aa; border-radius: 10px; font-size: 13px;
}
.credits-banner a { color: #2563eb; font-weight: 600; text-decoration: none; }
.report {
  margin-top: 12px; padding: 12px; background: #f8fafc; border-radius: 10px;
  font-size: 12px; white-space: pre-wrap; max-height: 200px; overflow: auto;
}
@media (max-width: 768px) {
  .chapter-plans li { grid-template-columns: 1fr; }
  .wizard-steps .label { display: none; }
}
</style>
