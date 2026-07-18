<template>
  <div class="workspace">
    <aside class="sidebar" v-if="!editing">
      <div class="sidebar-head">
        <h2>我的作品</h2>
        <button class="btn-new" @click="newStory">+ 新建</button>
      </div>
      <div v-if="loading" class="empty">加载中...</div>
      <EmptyState
        v-else-if="!stories.length"
        :image="images.emptyCreate"
        title="还没有作品"
        description="创建第一部小说，开始 AI 辅助创作"
        :image-width="160"
      >
        <button class="btn-new" @click="newStory">+ 新建作品</button>
      </EmptyState>
      <ul v-else class="story-list">
        <li v-for="s in stories" :key="s.id" @click="openStory(s.id)" class="story-item">
          <img :src="images.defaultStoryCover" alt="" class="story-thumb" width="36" height="48" aria-hidden="true" />
          <div class="story-item-body">
            <span class="s-title">{{ s.title || '未命名' }}</span>
            <span class="s-meta">{{ s.word_count || 0 }} 字 · {{ s.status }}</span>
          </div>
        </li>
      </ul>
    </aside>

    <main class="editor" v-if="editing">
      <div v-if="welcomeBanner" class="welcome-banner">
        🎉 欢迎！已到账 <strong>30 点</strong>，试试「AI 续写正文」感受完整创作流程。
        <button class="welcome-close" @click="welcomeBanner = false">知道了</button>
      </div>
      <div v-if="creditsLow" class="credits-banner">
        <span>点数不足，无法继续生成。</span>
        <router-link to="/wallet">领取每日免费 5 点</router-link>
        <router-link to="/pricing">立即充值</router-link>
        <button class="welcome-close" @click="creditsLow = false">×</button>
      </div>
      <div class="editor-toolbar">
        <button class="btn-back" @click="backToList">← 返回</button>
        <span class="toolbar-title">{{ form.title || '未命名作品' }}</span>
        <div class="toolbar-actions">
          <button class="btn-sm" :disabled="busy" @click="save">保存</button>
          <button class="btn-sm" @click="exportStory('txt')">导出 TXT</button>
          <button class="btn-sm" @click="exportStory('md')">导出 MD</button>
          <button class="btn-sm" @click="submitReview">提交审核</button>
        </div>
      </div>

      <div class="editor-body">
        <section class="panel">
          <PanelHeading>基本信息</PanelHeading>
          <input v-model="form.title" placeholder="书名" class="input" />
          <input v-model="form.genre" placeholder="题材（如：都市神豪）" class="input" />
          <textarea v-model="form.intro" placeholder="简介 / 故事钩子" class="textarea" rows="3"></textarea>
        </section>

        <section class="panel actions">
          <PanelHeading :icon="images.features.brain">AI 创作流程</PanelHeading>
          <div class="action-grid">
            <button class="btn-action" :disabled="busy" @click="doGenerateTitle">
              <img :src="images.workspaceActions.title" alt="生成书名" width="18" height="18" />
              <span>生成书名 <em>1点</em></span>
            </button>
            <button class="btn-action" :disabled="busy" @click="doGenerateOutline">
              <img :src="images.workspaceActions.outline" alt="生成大纲" width="18" height="18" />
              <span>生成大纲 <em>3点</em></span>
            </button>
            <button class="btn-action" :disabled="busy" @click="doGenerateChapters">
              <img :src="images.workspaceActions.chapters" alt="生成章纲" width="18" height="18" />
              <span>生成章纲 <em>5点</em></span>
            </button>
            <button class="btn-action primary" :disabled="busy" @click="doContinue">
              <img :src="images.workspaceActions.continue" alt="AI续写正文" width="18" height="18" />
              <span>AI 续写正文 <em>10点</em></span>
            </button>
          </div>
          <p v-if="msg" class="msg" :class="{ err: msgErr }">{{ msg }}</p>
        </section>

        <section class="panel" v-if="outlinePreview">
          <PanelHeading :icon="images.features.novel">大纲</PanelHeading>
          <pre class="code">{{ outlinePreview }}</pre>
        </section>

        <section class="panel">
          <PanelHeading :icon="images.features.short">章节内容</PanelHeading>
          <textarea v-model="chapterContent" class="textarea content-area" placeholder="在此编辑或 AI 续写正文..."></textarea>
        </section>

        <section class="panel" v-if="chapterList.length">
          <PanelHeading>章节列表</PanelHeading>
          <ul class="chapter-list">
            <li v-for="ch in chapterList" :key="ch.idx || ch.chapter" @click="loadChapter(ch)">
              {{ ch.title || `第${ch.idx || ch.chapter}章` }} <span class="wc">{{ ch.word_count || (ch.content||'').length }}字</span>
            </li>
          </ul>
        </section>

        <section class="panel brain-panel" v-if="memory.characters?.length || memory.foreshadowings?.length">
          <PanelHeading :icon="images.features.brain">小说大脑</PanelHeading>
          <div v-if="memory.characters?.length" class="brain-block">
            <h4>人物</h4>
            <p v-for="c in memory.characters" :key="c.id"><strong>{{ c.name }}</strong> {{ c.profile }}</p>
          </div>
          <div v-if="memory.foreshadowings?.length" class="brain-block">
            <h4>伏笔</h4>
            <p v-for="f in memory.foreshadowings" :key="f.id" :class="{ done: f.status==='recovered' }">
              第{{ f.planted_chapter }}章：{{ f.content }} <em>({{ f.status }})</em>
            </p>
          </div>
          <div v-if="memory.summaries?.length" class="brain-block">
            <h4>章节摘要</h4>
            <p v-for="m in memory.summaries" :key="m.chapter_idx">第{{ m.chapter_idx }}章：{{ m.summary }}</p>
          </div>
        </section>

        <section class="panel brain-panel" v-else-if="memory.summaries && memory.summaries.length">
          <PanelHeading :icon="images.features.brain">小说大脑 · 章节摘要</PanelHeading>
          <ul class="memory-list">
            <li v-for="m in memory.summaries" :key="m.chapter_idx">
              <strong>第{{ m.chapter_idx }}章</strong> {{ m.summary }}
            </li>
          </ul>
        </section>
      </div>
    </main>

    <div v-if="!editing && !loading" class="welcome">
      <img :src="images.workspace" alt="创作台欢迎横幅" class="welcome-banner" />
      <h2>创作台</h2>
      <p>从左侧选择作品，或新建一部小说开始 AI 辅助创作。</p>
      <button class="btn-new large" @click="newStory">+ 新建作品</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storyApi } from '../api'
import { IMAGES } from '../assets/images'
import EmptyState from '../components/EmptyState.vue'
import PanelHeading from '../components/PanelHeading.vue'

const images = IMAGES

const route = useRoute()
const stories = ref([])
const loading = ref(true)
const editing = ref(false)
const busy = ref(false)
const msg = ref('')
const msgErr = ref(false)
const creditsLow = ref(false)
const welcomeBanner = ref(false)
const outlinePreview = ref('')
const chapterContent = ref('')
const memory = reactive({ summaries: [], characters: [], foreshadowings: [], settings: [] })
const chapterList = ref([])

const form = reactive({
  id: null, title: '', genre: '', intro: '',
  outline: '', characters: '', chapters: '[]', status: 'draft',
})

function setMsg(text, err = false) {
  msg.value = text; msgErr.value = err
}

function handleApiError(res, fallback) {
  if (res?.insufficient_credits || res?.status === 402) {
    creditsLow.value = true
    setMsg(res.detail || '点数不足，请先充值或领取每日免费额度', true)
    return true
  }
  setMsg(res?.error || res?.detail || fallback, true)
  return false
}

async function loadList() {
  loading.value = true
  try {
    const res = await storyApi.list()
    if (res?.success) stories.value = res.stories || []
  } finally { loading.value = false }
}

async function openStory(id) {
  const res = await storyApi.get(id)
  if (!res?.success) { setMsg(res?.detail || '加载失败', true); return }
  const s = res.story
  Object.assign(form, { id: s.id, title: s.title || '', genre: s.genre || '', intro: s.intro || '',
    outline: s.outline || '', characters: s.characters || '', chapters: s.chapters || '[]', status: s.status || 'draft' })
  try {
    const chs = JSON.parse(form.chapters || '[]')
    const last = chs[chs.length - 1]
    chapterContent.value = last?.content || ''
  } catch { chapterContent.value = '' }
  outlinePreview.value = form.outline
  editing.value = true
  await loadMemory()
  await loadChapterList()
}

async function loadChapterList() {
  if (!form.id) { chapterList.value = []; return }
  const res = await storyApi.chapters(form.id)
  if (res?.success) chapterList.value = res.chapters || []
}

function loadChapter(ch) {
  chapterContent.value = ch.content || ''
  form.chapter_title = ch.title
}

async function loadMemory() {
  if (!form.id) return
  const res = await storyApi.memory(form.id)
  if (res?.success) {
    memory.summaries = res.summaries || []
    memory.characters = res.characters || []
    memory.foreshadowings = res.foreshadowings || []
    memory.settings = res.settings || []
  }
}

function newStory() {
  Object.assign(form, { id: null, title: '', genre: '', intro: '', outline: '', characters: '', chapters: '[]', status: 'draft' })
  chapterContent.value = ''; outlinePreview.value = ''; memory.summaries = []
  editing.value = true
  const q = route.query
  if (q.generatedTitle) form.title = q.generatedTitle
  if (q.prompt) form.intro = q.prompt
  if (q.type) form.genre = q.type
}

function backToList() { editing.value = false; loadList() }

async function save() {
  busy.value = true
  try {
    let chs = []
    try { chs = JSON.parse(form.chapters || '[]') } catch { chs = [] }
    if (chapterContent.value) {
      if (chs.length) chs[chs.length - 1] = { ...chs[chs.length - 1], content: chapterContent.value }
      else chs = [{ chapter: 1, title: '第1章', content: chapterContent.value }]
    }
    form.chapters = JSON.stringify(chs)
    const res = await storyApi.save({ ...form })
    if (res?.success) {
      form.id = res.story_id
      setMsg('保存成功')
      window.dispatchEvent(new Event('credits-changed'))
    } else setMsg(res?.detail || '保存失败', true)
  } finally { busy.value = false }
}

async function doGenerateTitle() {
  if (!form.intro && !form.title) { setMsg('请先填写简介或想法', true); return }
  busy.value = true
  try {
    const res = await storyApi.generateTitle({ genre: form.genre || '都市', prompt: form.intro || form.title })
    if (res?.success) {
      if (res.title) form.title = res.title
      if (res.description) form.intro = res.description
      setMsg('书名生成成功')
      window.dispatchEvent(new Event('credits-changed'))
    } else handleApiError(res, '生成失败')
  } finally { busy.value = false }
}

async function doGenerateOutline() {
  if (!form.title) { setMsg('请先填写书名', true); return }
  busy.value = true
  try {
    const res = await storyApi.generateOutline({
      title: form.title, intro: form.intro || form.title,
      genre: form.genre || '都市', hot_points: ['打脸', '逆袭', '装逼'],
    })
    if (res?.success) {
      form.outline = JSON.stringify(res.outline, null, 2)
      outlinePreview.value = form.outline
      setMsg('大纲生成成功')
      window.dispatchEvent(new Event('credits-changed'))
    } else handleApiError(res, '生成失败')
  } finally { busy.value = false }
}

async function doGenerateChapters() {
  let outline = {}
  try { outline = JSON.parse(form.outline) } catch { setMsg('请先生成大纲', true); return }
  busy.value = true
  try {
    const res = await storyApi.generateChapters({ outline, chapter_count: 10 })
    if (res?.success) {
      form.chapters = JSON.stringify(res.chapters)
      setMsg(`已生成 ${res.chapters?.length || 0} 章章纲`)
      window.dispatchEvent(new Event('credits-changed'))
    } else handleApiError(res, '生成失败')
  } finally { busy.value = false }
}

async function doContinue() {
  if (!chapterContent.value && !form.intro) { setMsg('请先写一些内容或填写简介', true); return }
  if (!form.id) await save()
  busy.value = true
  try {
    const res = await storyApi.continue({
      story_id: form.id, content: chapterContent.value, style: '网文爽文',
      chapter_title: form.title,
    })
    if (res?.success) {
      chapterContent.value += (chapterContent.value ? '\n\n' : '') + res.content
      setMsg(`续写成功 +${res.length} 字`)
      await loadMemory()
      await loadChapterList()
      window.dispatchEvent(new Event('credits-changed'))
    } else handleApiError(res, '续写失败')
  } finally { busy.value = false }
}

async function submitReview() {
  if (!form.id) { await save(); if (!form.id) return }
  busy.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/story/${form.id}/submit-review`, {
      method: 'POST', headers: { Authorization: `Bearer ${token}` },
    })
    const d = await res.json()
    setMsg(d?.message || d?.detail || '已提交', !d?.success)
  } finally { busy.value = false }
}

function exportStory(format) {
  if (!form.id) { setMsg('请先保存作品', true); return }
  const token = localStorage.getItem('token')
  fetch(storyApi.exportUrl(form.id, format), { headers: { Authorization: `Bearer ${token}` } })
    .then(r => r.blob())
    .then(blob => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = `${form.title || 'story'}.${format}`
      a.click()
    })
}

onMounted(async () => {
  await loadList()
  if (route.query.welcome === '1') welcomeBanner.value = true
  if (route.query.generatedTitle || route.query.prompt) newStory()
})
</script>

<style scoped>
.workspace { display: flex; min-height: calc(100vh - 62px); }
.sidebar { width: 280px; border-right: 1px solid #e8f0fa; background: #fff; padding: 20px 16px; }
.sidebar-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.sidebar-head h2 { font-size: 18px; }
.btn-new { padding: 8px 14px; border: none; border-radius: 8px; background: #2563eb; color: #fff; font-weight: 600; cursor: pointer; font-size: 13px; }
.btn-new.large { padding: 12px 24px; font-size: 15px; }
.story-list { list-style: none; }
.story-item {
  display: flex; align-items: center; gap: 10px;
  padding: 12px; border-radius: 10px; cursor: pointer; margin-bottom: 6px; border: 1px solid transparent;
}
.story-thumb { flex-shrink: 0; border-radius: 6px; object-fit: cover; background: #eef5ff; }
.story-item-body { min-width: 0; flex: 1; }
.story-item:hover { background: #f0f7ff; border-color: #dbeafe; }
.s-title { display: block; font-weight: 600; font-size: 14px; color: #1e2a3a; }
.s-meta { font-size: 12px; color: #94a3b8; }
.empty { color: #94a3b8; font-size: 14px; padding: 20px 0; }
.welcome { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; color: #5a6a7a; padding: 40px 24px; }
.welcome-banner { width: min(480px, 90%); border-radius: 16px; box-shadow: 0 8px 24px rgba(37,99,235,0.12); margin-bottom: 8px; }
.welcome h2 { color: #1e2a3a; font-size: 24px; margin: 0; }
.editor { flex: 1; display: flex; flex-direction: column; }
.editor-toolbar { display: flex; align-items: center; gap: 12px; padding: 12px 20px; background: #fff; border-bottom: 1px solid #e8f0fa; }
.btn-back { border: none; background: none; color: #2563eb; cursor: pointer; font-weight: 600; }
.toolbar-title { flex: 1; font-weight: 700; }
.toolbar-actions { display: flex; gap: 8px; }
.btn-sm { padding: 6px 12px; border-radius: 8px; border: 1px solid #dbeafe; background: #fff; cursor: pointer; font-size: 13px; }
.editor-body { padding: 20px; max-width: 900px; margin: 0 auto; width: 100%; }
.panel { background: #fff; border-radius: 14px; padding: 20px; margin-bottom: 16px; border: 1px solid #e8f0fa; }
.panel h3 { font-size: 15px; margin-bottom: 12px; color: #1e2a3a; }
.input, .textarea { width: 100%; padding: 10px 14px; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 14px; margin-bottom: 10px; font-family: inherit; }
.content-area { min-height: 280px; line-height: 1.8; }
.action-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.btn-action {
  display: flex; align-items: center; gap: 8px; justify-content: flex-start;
  padding: 12px 14px; border-radius: 10px; border: 1px solid #dbeafe; background: #f8fbff;
  cursor: pointer; font-size: 13px; font-weight: 600; color: #2563eb;
}
.btn-action img { flex-shrink: 0; }
.btn-action em { font-style: normal; font-weight: 500; opacity: 0.75; margin-left: auto; font-size: 12px; }
.btn-action.primary { background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; border: none; }
.btn-action.primary em { opacity: 0.9; }
.brain-panel { background: linear-gradient(180deg, #f8fbff 0%, #fff 100%); }
.btn-action:disabled { opacity: 0.5; cursor: not-allowed; }
.msg { font-size: 13px; margin-top: 10px; color: #16a34a; }
.msg.err { color: #ef4444; }
.welcome-banner, .credits-banner {
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  padding: 12px 16px; margin-bottom: 12px; border-radius: 10px; font-size: 13px;
}
.welcome-banner { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.credits-banner { background: #fff7ed; color: #9a3412; border: 1px solid #fed7aa; }
.credits-banner a { color: #2563eb; font-weight: 600; text-decoration: none; }
.welcome-close {
  margin-left: auto; border: none; background: transparent; cursor: pointer;
  font-size: 14px; color: inherit; opacity: 0.7;
}
.code { background: #f8fafc; padding: 12px; border-radius: 8px; font-size: 12px; overflow: auto; max-height: 200px; white-space: pre-wrap; }
.memory-list { list-style: none; font-size: 13px; color: #5a6a7a; }
.memory-list li { padding: 8px 0; border-bottom: 1px solid #f0f4f8; }
.chapter-list { list-style: none; max-height: 200px; overflow-y: auto; }
.chapter-list li { padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 13px; display: flex; justify-content: space-between; }
.chapter-list li:hover { background: #f0f7ff; }
.wc { color: #94a3b8; font-size: 11px; }
.brain-block { margin-bottom: 12px; font-size: 13px; color: #5a6a7a; }
.brain-block h4 { font-size: 12px; color: #2563eb; margin-bottom: 6px; }
.brain-block p.done { opacity: 0.5; text-decoration: line-through; }
@media (max-width: 768px) {
  .workspace { flex-direction: column; }
  .sidebar { width: 100%; border-right: none; border-bottom: 1px solid #e8f0fa; }
  .action-grid { grid-template-columns: 1fr; }
}
</style>
