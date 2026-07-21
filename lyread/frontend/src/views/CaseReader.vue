<template>
  <div class="reader-page">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!caseData" class="empty">案例不存在或已下架</div>
    <article v-else class="article">
      <header>
        <span class="cat">{{ caseData.category }}</span>
        <h1>{{ caseData.title }}</h1>
        <p class="meta">
          <span v-if="excerptChapters">节选 {{ excerptChapters }} 章</span>
          <span v-if="excerptChars"> · 约 {{ excerptChars }} 字</span>
          <span v-if="caseData.word_count"> · {{ formatStoryWords(caseData.word_count) }}</span>
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
      <footer class="cta">
        <router-link :to="workspaceLink" class="btn-cta">用这个风格开始创作 →</router-link>
      </footer>
    </article>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { casesApi } from '../api'
import { parseChapters, countChapters, formatStoryWords } from '../utils/caseContent'

const route = useRoute()
const loading = ref(true)
const caseData = ref(null)
const rawBody = ref('')

const chapters = computed(() => parseChapters(rawBody.value))
const excerptChapters = computed(() => caseData.value?.excerpt_chapters ?? countChapters(rawBody.value))
const excerptChars = computed(() => caseData.value?.excerpt_chars ?? rawBody.value.length)

const workspaceLink = computed(() => {
  const cat = caseData.value?.category || ''
  return { path: '/workspace', query: { type: cat, prompt: `参考《${caseData.value?.title}》的风格创作` } }
})

onMounted(async () => {
  try {
    const res = await casesApi.get(route.params.id)
    if (res?.success) {
      caseData.value = res.case
      rawBody.value = res.case.preview_body || res.case.preview_excerpt || ''
    }
  } finally { loading.value = false }
})
</script>

<style scoped>
.reader-page { max-width: 720px; margin: 0 auto; padding: 32px 20px 80px; }
.loading, .empty { text-align: center; color: #94a3b8; padding: 60px; }
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
.cta { text-align: center; margin-top: 32px; padding-top: 24px; border-top: 1px solid #eef2f7; }
.btn-cta {
  display: inline-block; padding: 14px 28px; border-radius: 12px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; font-weight: 600; text-decoration: none;
}
</style>
