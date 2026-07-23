<template>
  <div class="trending-page">
    <header class="hero">
      <img :src="images.features.novel" alt="案例阅读" class="hero-icon" width="40" height="40" />
      <h1>案例阅读</h1>
      <p>{{ heroSubtitle }}</p>
      <router-link
        v-if="!isLoggedIn"
        class="hero-register"
        :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
        @click="trackHeroRegister"
      >免费注册，送 30 点 →</router-link>
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
      :description="activeCategory ? `「${activeCategory}」还没有可读节选。先看全部案例找灵感，或把这个题材带进创作台开写` : '审核通过的作品将展示在这里。也可以先注册领 30 点，去创作台开写第一篇'"
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
          :to="emptyCtaLink"
          @click="trackEmptyWrite"
        >{{ emptyCtaLabel }}</router-link>
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
          <p
            v-if="c.excerpt"
            class="excerpt"
            :class="{ expanded: expandedExcerptId === c.id }"
          >{{ c.excerpt }}</p>
          <button
            v-if="c.excerpt && c.excerpt.length > 72"
            type="button"
            class="excerpt-toggle"
            @click.prevent.stop="toggleExcerpt(c)"
          >{{ expandedExcerptId === c.id ? '收起节选' : '展开节选' }}</button>
          <div class="meta">
            <span>{{ c.word_count }} 字</span>
            <span class="heat"><img :src="images.fire" alt="热度" width="14" height="14" /> {{ c.heat }}</span>
          </div>
        </div>
      </router-link>
    </div>

    <div class="cta">
      <p v-if="!isLoggedIn" class="guest-cta-hint">注册送 30 点，约可 AI 续写 3 章</p>
      <router-link :to="footerCtaLink" class="btn-cta" @click="trackFooterCta">{{ footerCtaLabel }}</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { casesApi } from '../api'
import { coverForCase, IMAGES } from '../assets/images'
import EmptyState from '../components/EmptyState.vue'
import { trackEvent } from '../utils/analytics'
import { workspaceWizardQuery } from '../utils/wizardGenre'

const images = IMAGES

const cases = ref([])
const loading = ref(true)
const activeCategory = ref('')
const expandedExcerptId = ref(null)
const isLoggedIn = computed(() => typeof localStorage !== 'undefined' && !!localStorage.getItem('token'))

/** 游客首屏强调注册赠点，缩短案例浏览 → 注册路径 */
const heroSubtitle = computed(() =>
  isLoggedIn.value
    ? '平台真实生成案例，点击阅读全文，或用这个风格开始创作'
    : '平台真实生成案例。注册送 30 点，约可 AI 续写 3 章；读完即可用同风格开写',
)

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
    query: workspaceWizardQuery({
      category: activeCategory.value,
      prompt: `写一个${activeCategory.value}题材的故事`,
    }),
  }
})

/** 游客直达注册并带回创作台意图，与 CaseReader 漏斗对齐 */
function withRegisterRedirect(ws) {
  if (isLoggedIn.value) return ws
  const q = new URLSearchParams(ws.query || {}).toString()
  const redirect = q ? `${ws.path}?${q}` : ws.path
  return { path: '/login', query: { mode: 'register', redirect } }
}

const emptyCtaLink = computed(() => withRegisterRedirect(emptyWorkspaceLink.value))
const emptyCtaLabel = computed(() => {
  if (isLoggedIn.value) return activeCategory.value ? '用同题材开写 →' : '开始创作 →'
  return activeCategory.value ? '注册送 30 点，开写 →' : '免费注册，开始创作（送 30 点）→'
})

/** 页脚 CTA：有筛选时带同题材进向导 */
const footerWorkspaceLink = computed(() => {
  if (!activeCategory.value) return { path: '/workspace', query: { mode: 'new' } }
  return {
    path: '/workspace',
    query: workspaceWizardQuery({ category: activeCategory.value }),
  }
})
const footerCtaLink = computed(() => withRegisterRedirect(footerWorkspaceLink.value))
const footerCtaLabel = computed(() =>
  isLoggedIn.value
    ? (activeCategory.value ? `用同题材开写（${activeCategory.value}）→` : '开始创作 →')
    : '免费注册，用同题材开写（送 30 点）→',
)

function selectCategory(cat) {
  activeCategory.value = cat
  trackEvent('trending_filter', { category: 'funnel', label: cat || 'all' })
}

function trackEmptyWrite() {
  trackEvent('trending_empty_cta', {
    category: 'conversion',
    label: `${isLoggedIn.value ? 'user' : 'guest'}:${activeCategory.value || 'all'}`,
  })
}

function trackFooterCta() {
  trackEvent('trending_footer_cta', {
    category: 'conversion',
    label: isLoggedIn.value ? 'user' : 'guest',
  })
}

function trackHeroRegister() {
  trackEvent('trending_hero_register', { category: 'conversion', label: 'guest' })
}

function onCaseClick(c) {
  trackEvent('case_click', {
    category: 'funnel',
    label: String(c.id),
    value: Number(c.heat) || 0,
  })
}

/** 触控端无 hover：点按展开节选，避免只能看 2～3 行钩子 */
function toggleExcerpt(c) {
  const next = expandedExcerptId.value === c.id ? null : c.id
  expandedExcerptId.value = next
  trackEvent('trending_excerpt_toggle', {
    category: 'engagement',
    label: next ? 'expand' : 'collapse',
    value: Number(c.id) || 0,
  })
}

onMounted(async () => {
  try {
    const res = await casesApi.list(100)
    if (res?.success) cases.value = res.cases || []
  } finally {
    loading.value = false
  }
  // 触控端无 hover：默认展开首卡节选，降低只看标题就跳出
  try {
    const coarse = typeof window !== 'undefined'
      && window.matchMedia
      && window.matchMedia('(hover: none), (pointer: coarse)').matches
    const first = cases.value.find((c) => c.excerpt && String(c.excerpt).length > 72)
    if (coarse && first) {
      expandedExcerptId.value = first.id
      trackEvent('trending_excerpt_auto', { category: 'engagement', label: 'first_card', value: Number(first.id) || 0 })
    }
  } catch { /* ignore */ }
})
</script>

<style scoped>
.trending-page { max-width: 1100px; margin: 0 auto; padding: 32px 20px 80px; }
.hero { text-align: center; margin-bottom: 28px; }
.hero-icon { display: block; margin: 0 auto 12px; }
.hero h1 { font-size: 28px; color: #1e2a3a; margin-bottom: 8px; }
.hero p { color: #5a6a7a; max-width: 36em; margin: 0 auto; line-height: 1.55; }
.hero-register {
  display: inline-block;
  margin-top: 14px;
  padding: 10px 18px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4da1ff, #2563eb);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
}
.hero-register:hover { filter: brightness(1.05); }
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
/* tip 列表节选约 200 字：触控默认多露一行；桌面 hover/focus 展开；按钮可点按展开满节选 */
.excerpt {
  font-size: 12px;
  color: #64748b;
  line-height: 1.55;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color 0.15s ease;
}
.excerpt.expanded {
  display: block;
  -webkit-line-clamp: unset;
  color: #475569;
}
.excerpt-toggle {
  appearance: none;
  border: 0;
  background: transparent;
  color: #2563eb;
  font-size: 12px;
  padding: 0;
  margin: 0 0 8px;
  cursor: pointer;
  font-weight: 500;
}
.excerpt-toggle:hover { color: #1d4ed8; text-decoration: underline; }
@media (hover: hover) and (pointer: fine) {
  .excerpt { -webkit-line-clamp: 2; }
  .case-card:hover .excerpt:not(.expanded),
  .case-card:focus-within .excerpt:not(.expanded) {
    -webkit-line-clamp: 6;
    color: #475569;
  }
}
.meta { display: flex; gap: 12px; font-size: 12px; color: #94a3b8; }
.cta { text-align: center; }
.guest-cta-hint {
  margin: 0 0 10px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.5;
}
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
