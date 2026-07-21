<template>
  <div class="trending-page">
    <header class="hero">
      <img :src="images.features.novel" alt="案例阅读" class="hero-icon" width="40" height="40" />
      <h1>案例阅读</h1>
      <p>平台真实生成案例，点击阅读全文，或用这个风格开始创作</p>
    </header>

    <div v-if="categories.length" class="chip-row" role="tablist" aria-label="案例分类">
      <button
        type="button"
        role="tab"
        class="chip"
        :class="{ active: !activeCategory }"
        :aria-selected="!activeCategory"
        @click="selectCategory('')"
      >全部</button>
      <button
        v-for="cat in categories"
        :key="cat"
        type="button"
        role="tab"
        class="chip"
        :class="{ active: activeCategory === cat }"
        :aria-selected="activeCategory === cat"
        @click="selectCategory(cat)"
      >{{ cat }}</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <EmptyState
      v-else-if="!filteredCases.length"
      :image="images.emptyCreate"
      :title="activeCategory ? `暂无「${activeCategory}」案例` : '暂无案例'"
      :description="activeCategory ? '试试其他分类，或用这个风格去创作台开写' : '审核通过的作品将展示在这里，敬请期待'"
      :image-width="160"
    >
      <div class="empty-actions">
        <button
          v-if="activeCategory"
          type="button"
          class="btn-ghost"
          @click="selectCategory('')"
        >查看全部案例</button>
        <router-link
          class="btn-cta-sm"
          :to="emptyWorkspaceLink"
          @click="trackEmptyWrite"
        >{{ activeCategory ? '用这个风格开写' : '开始创作' }} →</router-link>
      </div>
    </EmptyState>
    <div v-else class="case-grid">
      <router-link
        v-for="(c, i) in filteredCases"
        :key="c.id"
        :to="`/case/${c.id}`"
        class="case-card"
        @click="onCaseClick(c)"
      >
        <img :src="coverForCase(c, i)" :alt="`${c.title} 封面`" class="case-cover" loading="lazy" />
        <div class="case-body">
          <span class="cat">{{ c.category || '都市' }}</span>
          <h3>{{ c.title }}</h3>
          <p v-if="c.excerpt" class="excerpt">{{ c.excerpt }}</p>
          <div class="meta">
            <span>{{ c.word_count }} 字</span>
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
import { ref, computed, onMounted } from 'vue'
import { casesApi } from '../api'
import { coverForCase, IMAGES } from '../assets/images'
import EmptyState from '../components/EmptyState.vue'
import { trackEvent } from '../utils/analytics'

const images = IMAGES

const cases = ref([])
const loading = ref(true)
const activeCategory = ref('')

const categories = computed(() => {
  const seen = new Set()
  const list = []
  for (const c of cases.value) {
    const cat = (c.category || '').trim()
    if (cat && !seen.has(cat)) {
      seen.add(cat)
      list.push(cat)
    }
  }
  return list
})

const filteredCases = computed(() => {
  if (!activeCategory.value) return cases.value
  return cases.value.filter((c) => (c.category || '') === activeCategory.value)
})

const emptyWorkspaceLink = computed(() => {
  if (!activeCategory.value) return { path: '/workspace', query: { mode: 'new' } }
  return {
    path: '/workspace',
    query: { type: activeCategory.value, prompt: `写一个${activeCategory.value}题材的故事` },
  }
})

function selectCategory(cat) {
  activeCategory.value = cat
  trackEvent('trending_filter', { category: 'funnel', label: cat || 'all' })
}

function trackEmptyWrite() {
  trackEvent('trending_empty_cta', {
    category: 'conversion',
    label: activeCategory.value || 'all',
  })
}

function onCaseClick(c) {
  trackEvent('case_click', {
    category: 'funnel',
    label: String(c.id),
    value: Number(c.heat) || 0,
  })
}

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
.hero { text-align: center; margin-bottom: 28px; }
.hero-icon { display: block; margin: 0 auto 12px; }
.hero h1 { font-size: 28px; color: #1e2a3a; margin-bottom: 8px; }
.hero p { color: #5a6a7a; }
.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-bottom: 28px;
}
.chip {
  appearance: none;
  border: 1px solid #dbe7f5;
  background: #fff;
  color: #5a6a7a;
  font-size: 13px;
  line-height: 1;
  padding: 8px 14px;
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.chip:hover { border-color: #93c5fd; color: #2563eb; }
.chip.active {
  background: rgba(37, 99, 235, 0.1);
  border-color: #93c5fd;
  color: #1d4ed8;
  font-weight: 600;
}
.loading { text-align: center; color: #94a3b8; padding: 60px; }
.empty-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}
.btn-ghost {
  appearance: none;
  border: 1px solid #dbe7f5;
  background: #fff;
  color: #5a6a7a;
  font-size: 14px;
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  text-decoration: none;
}
.btn-ghost:hover { border-color: #93c5fd; color: #2563eb; }
.btn-cta-sm {
  display: inline-block;
  padding: 10px 16px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4da1ff, #2563eb);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
}
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
@media (max-width: 768px) {
  .case-grid { grid-template-columns: 1fr; }
  .chip-row { justify-content: flex-start; overflow-x: auto; flex-wrap: nowrap; padding-bottom: 4px; -webkit-overflow-scrolling: touch; }
  .chip { flex-shrink: 0; }
}
</style>
