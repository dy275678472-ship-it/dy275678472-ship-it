<template>
  <div class="trending-page">
    <header class="hero">
      <img :src="images.features.novel" alt="案例阅读" class="hero-icon" width="40" height="40" />
      <h1>案例阅读</h1>
      <p>平台真实生成案例，点击阅读全文，或用这个风格开始创作</p>
    </header>

    <div class="filters" v-if="categories.length">
      <button
        type="button"
        class="filter-chip"
        :class="{ active: !activeCategory }"
        @click="setCategory('')"
      >全部 ({{ totalCount }})</button>
      <button
        v-for="cat in categories"
        :key="cat.name"
        type="button"
        class="filter-chip"
        :class="{ active: activeCategory === cat.name }"
        @click="setCategory(cat.name)"
      >{{ cat.name }} ({{ cat.count }})</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <EmptyState
      v-else-if="!cases.length"
      :image="images.emptyCreate"
      title="暂无案例"
      :description="activeCategory ? `「${activeCategory}」暂无案例，试试其他题材` : '审核通过的作品将展示在这里，敬请期待'"
      :image-width="160"
    />
    <div v-else class="case-grid">
      <router-link v-for="(c, i) in cases" :key="c.id" :to="`/case/${c.id}`" class="case-card">
        <img :src="coverForCase(c, i)" :alt="`${c.title} 封面`" class="case-cover" loading="lazy" />
        <div class="case-body">
          <span class="cat">{{ c.category || '都市' }}</span>
          <h3>{{ c.title }}</h3>
          <p v-if="c.excerpt" class="excerpt">{{ c.excerpt }}</p>
          <div class="meta">
            <span>{{ formatWords(c.word_count) }}</span>
            <span class="heat"><img :src="images.fire" alt="热度" width="14" height="14" /> {{ c.heat }}</span>
          </div>
        </div>
      </router-link>
    </div>

    <div class="cta">
      <router-link :to="{ path: '/workspace', query: { mode: 'new' } }" class="btn-cta">用这个风格开始创作 →</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { casesApi } from '../api'
import { coverForCase, IMAGES } from '../assets/images'
import EmptyState from '../components/EmptyState.vue'

const images = IMAGES

const cases = ref([])
const categories = ref([])
const activeCategory = ref('')
const totalCount = ref(0)
const loading = ref(true)

function formatWords(n) {
  const w = Number(n) || 0
  return w >= 10000 ? `${(w / 10000).toFixed(1)} 万字` : `${w} 字`
}

async function loadCases() {
  loading.value = true
  try {
    const res = await casesApi.list(60, activeCategory.value)
    if (res?.success) cases.value = res.cases || []
  } finally {
    loading.value = false
  }
}

function setCategory(name) {
  activeCategory.value = name
  loadCases()
}

onMounted(async () => {
  try {
    const [catRes] = await Promise.all([
      casesApi.categories(),
      loadCases(),
    ])
    if (catRes?.success) {
      categories.value = catRes.categories || []
      totalCount.value = categories.value.reduce((s, c) => s + c.count, 0)
    }
  } catch {
    await loadCases()
  }
})
</script>

<style scoped>
.trending-page { max-width: 1100px; margin: 0 auto; padding: 32px 20px 80px; }
.hero { text-align: center; margin-bottom: 28px; }
.hero-icon { display: block; margin: 0 auto 12px; }
.hero h1 { font-size: 28px; color: #1e2a3a; margin-bottom: 8px; }
.hero p { color: #5a6a7a; }
.filters {
  display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;
  margin-bottom: 28px; max-width: 900px; margin-left: auto; margin-right: auto;
}
.filter-chip {
  padding: 6px 14px; border-radius: 999px; border: 1px solid #e2e8f0;
  background: #fff; color: #64748b; font-size: 13px; cursor: pointer;
  transition: all 0.15s;
}
.filter-chip:hover { border-color: #93c5fd; color: #2563eb; }
.filter-chip.active {
  background: rgba(77, 161, 255, 0.12); border-color: #4da1ff; color: #2563eb; font-weight: 600;
}
.loading { text-align: center; color: #94a3b8; padding: 60px; }
.heat { display: inline-flex; align-items: center; gap: 4px; }
.case-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 40px; }
.case-card {
  display: block; text-decoration: none; background: #fff; border-radius: 14px;
  overflow: hidden; border: 1px solid #e8f0fa; transition: all 0.2s;
}
.case-cover {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
}
.case-body { padding: 16px 20px 20px; }
.case-card:hover { box-shadow: 0 8px 24px rgba(77,161,255,0.12); transform: translateY(-2px); border-color: #bfdbfe; }
.cat { display: inline-block; padding: 3px 10px; background: rgba(77,161,255,0.12); color: #2563eb; border-radius: 999px; font-size: 12px; margin-bottom: 10px; }
.case-card h3 { font-size: 16px; color: #1e2a3a; margin-bottom: 8px; line-height: 1.4; }
.excerpt { font-size: 12px; color: #64748b; line-height: 1.5; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.meta { display: flex; gap: 12px; font-size: 12px; color: #94a3b8; }
.cta { text-align: center; }
.btn-cta {
  display: inline-block; padding: 14px 28px; border-radius: 12px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff;
  font-weight: 600; text-decoration: none;
}
@media (max-width: 768px) { .case-grid { grid-template-columns: 1fr; } }
</style>
