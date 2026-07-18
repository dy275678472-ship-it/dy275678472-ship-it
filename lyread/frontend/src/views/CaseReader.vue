<template>
  <div class="reader-page">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!caseData" class="empty">案例不存在或已下架</div>
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

const route = useRoute()
const loading = ref(true)
const caseData = ref(null)
const body = ref('')

const workspaceLink = computed(() => {
  const cat = caseData.value?.category || ''
  return { path: '/workspace', query: { type: cat, prompt: `参考《${caseData.value?.title}》的风格创作` } }
})

onMounted(async () => {
  try {
    const res = await casesApi.get(route.params.id)
    if (res?.success) {
      caseData.value = res.case
      body.value = res.case.preview_excerpt || res.case.preview_body || ''
    }
  } finally { loading.value = false }
})
</script>

<style scoped>
.reader-page { max-width: 720px; margin: 0 auto; padding: 32px 20px 80px; }
.loading, .empty { text-align: center; color: #94a3b8; padding: 60px; }
.article { background: #fff; border-radius: 16px; padding: 28px; border: 1px solid #e8f0fa; }
.cat { display: inline-block; padding: 4px 10px; background: #eff6ff; color: #2563eb; border-radius: 999px; font-size: 12px; }
h1 { font-size: 24px; margin: 12px 0 8px; line-height: 1.35; }
.meta { color: #94a3b8; font-size: 13px; margin-bottom: 24px; }
.body pre { white-space: pre-wrap; line-height: 1.9; font-size: 16px; color: #1e2a3a; font-family: inherit; }
.empty-body { color: #64748b; font-size: 14px; }
.link { color: #2563eb; }
.cta { text-align: center; margin-top: 32px; }
.btn-cta {
  display: inline-block; padding: 14px 28px; border-radius: 12px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; font-weight: 600; text-decoration: none;
}
</style>
