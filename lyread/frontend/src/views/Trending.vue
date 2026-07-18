<template>
  <div class="trending-page">
    <header class="hero">
      <h1>案例阅读</h1>
      <p>平台真实生成案例，点击阅读全文，或用这个风格开始创作</p>
    </header>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!cases.length" class="empty">暂无案例，敬请期待</div>
    <div v-else class="case-grid">
      <a v-for="c in cases" :key="c.id" :href="c.url" class="case-card" target="_blank" rel="noopener">
        <span class="cat">{{ c.category || '都市' }}</span>
        <h3>{{ c.title }}</h3>
        <div class="meta">
          <span>{{ c.word_count }} 字</span>
          <span>🔥 {{ c.heat }}</span>
        </div>
      </a>
    </div>

    <div class="cta">
      <router-link to="/workspace" class="btn-cta">用这个风格开始创作 →</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { casesApi } from '../api'

const cases = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await casesApi.list(24)
    if (res?.success) cases.value = res.cases || []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.trending-page { max-width: 1100px; margin: 0 auto; padding: 32px 20px 80px; }
.hero { text-align: center; margin-bottom: 36px; }
.hero h1 { font-size: 28px; color: #1e2a3a; margin-bottom: 8px; }
.hero p { color: #5a6a7a; }
.loading, .empty { text-align: center; color: #94a3b8; padding: 60px; }
.case-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px; }
.case-card {
  display: block; text-decoration: none; background: #fff; border-radius: 14px;
  padding: 20px; border: 1px solid #e8f0fa; transition: all 0.2s;
}
.case-card:hover { box-shadow: 0 8px 24px rgba(77,161,255,0.12); transform: translateY(-2px); border-color: #bfdbfe; }
.cat { display: inline-block; padding: 3px 10px; background: rgba(77,161,255,0.12); color: #2563eb; border-radius: 999px; font-size: 12px; margin-bottom: 10px; }
.case-card h3 { font-size: 16px; color: #1e2a3a; margin-bottom: 12px; line-height: 1.4; }
.meta { display: flex; gap: 12px; font-size: 12px; color: #94a3b8; }
.cta { text-align: center; }
.btn-cta {
  display: inline-block; padding: 14px 28px; border-radius: 12px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff;
  font-weight: 600; text-decoration: none;
}
@media (max-width: 768px) { .case-grid { grid-template-columns: 1fr; } }
</style>
