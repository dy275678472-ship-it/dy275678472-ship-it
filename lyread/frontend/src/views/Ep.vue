<template>
  <div class="ep-page">
    <header class="ep-hero">
      <h1>公开作品索引</h1>
      <p class="lede">浏览 AI 开篇节选与题材标签——读完可用同风格开写，游客先注册领 30 点。</p>
    </header>

    <section class="ep-lens" aria-label="怎么用这份索引">
      <h2>怎么用这份索引</h2>
      <ol>
        <li><strong>扫题材</strong> — 先按都市/战神/系统等标签挑合胃口的开篇。</li>
        <li><strong>读节选</strong> — 看节奏与钩子是否对味，再决定是否深读。</li>
        <li><strong>同风开写</strong> — 满意就注册回流创作台，用同题材新建长篇。</li>
        <li><strong>短篇试手</strong> — 想先练手，可去短故事页快速出一篇。</li>
      </ol>
    </section>

    <!-- 次屏转化：扫完用法后立刻 register-first，避免裸 /workspace -->
    <section class="ep-mid-cta" aria-label="开始创作">
      <p class="mid-kicker">注册送 30 点 · 失败不扣点</p>
      <div class="mid-actions">
        <router-link
          v-if="!isLoggedIn"
          class="btn primary"
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          @click="track('ep_mid_register')"
        >免费注册开写 →</router-link>
        <router-link
          v-else
          class="btn primary"
          :to="{ path: '/workspace', query: { mode: 'new' } }"
          @click="track('ep_mid_workspace')"
        >进入创作台 →</router-link>
        <router-link
          class="btn"
          to="/trending"
          @click="track('ep_mid_trending')"
        >热门案例</router-link>
        <router-link
          class="btn"
          to="/story"
          @click="track('ep_mid_story')"
        >试试短故事</router-link>
      </div>
    </section>

    <section class="ep-list" aria-label="公开作品列表">
      <h2>公开作品</h2>
      <p v-if="loading" class="ep-status">加载中…</p>
      <p v-else-if="error" class="ep-status">{{ error }}</p>
      <p v-else-if="!cases.length" class="ep-status">
        暂无公开案例 ·
        <router-link
          v-if="!isLoggedIn"
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          @click="track('ep_empty_register')"
        >注册领 30 点开写 →</router-link>
        <router-link
          v-else
          :to="{ path: '/workspace', query: { mode: 'new' } }"
          @click="track('ep_empty_workspace')"
        >去创作台 →</router-link>
      </p>
      <ul v-else>
        <li v-for="item in cases" :key="item.id">
          <!-- 规范深链 /ep/:id（人类 SPA CaseReader；抵御生产 /case→/ep 301） -->
          <router-link
            :to="`/ep/${item.id}`"
            @click="track('ep_case_click', String(item.id))"
          >{{ item.title }}</router-link>
          <span v-if="item.category" class="tag">{{ item.category }}</span>
          <span v-if="item.word_count" class="stat">{{ item.word_count }}字</span>
        </li>
      </ul>
    </section>

    <section class="ep-bottom" aria-label="下一步">
      <router-link to="/pricing" class="text-link" @click="track('ep_pricing')">查看价格</router-link>
      <span class="sep">·</span>
      <router-link to="/genre" class="text-link" @click="track('ep_genre')">题材聚合</router-link>
      <span class="sep">·</span>
      <router-link to="/guide" class="text-link" @click="track('ep_guide')">创作教程</router-link>
      <span class="sep">·</span>
      <router-link
        v-if="!isLoggedIn"
        class="text-link strong"
        :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
        @click="track('ep_bottom_register')"
      >免费注册（送 30 点）</router-link>
      <router-link
        v-else
        class="text-link strong"
        :to="{ path: '/workspace', query: { mode: 'new' } }"
        @click="track('ep_bottom_workspace')"
      >去创作台</router-link>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { casesApi } from '../api'
import { trackEvent } from '../utils/analytics'

const cases = ref([])
const loading = ref(true)
const error = ref('')

const isLoggedIn = computed(() => !!localStorage.getItem('token'))

function track(name, label = 'ep_spa') {
  trackEvent(name, { category: 'conversion', label })
}

async function loadCases() {
  loading.value = true
  error.value = ''
  try {
    const data = await casesApi.list(50)
    if (data?.success === false) {
      error.value = data.detail || '加载失败，请稍后重试'
      cases.value = []
      return
    }
    cases.value = data?.cases || []
  } catch (e) {
    error.value = '加载失败，请稍后重试'
    cases.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  trackEvent('ep_view', { category: 'engagement', label: 'spa' })
  loadCases()
})
</script>

<style scoped>
.ep-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 28px 20px 56px;
  color: #1e2a3a;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(74, 144, 217, 0.12), transparent 60%),
    linear-gradient(180deg, #f7fafc 0%, #eef3f9 100%);
  min-height: calc(100vh - 120px);
}
.ep-hero {
  text-align: center;
  margin-bottom: 24px;
}
.ep-hero h1 {
  font-size: 28px;
  margin: 0 0 10px;
  letter-spacing: 0.02em;
}
.lede {
  margin: 0 auto;
  max-width: 34em;
  font-size: 15px;
  line-height: 1.65;
  color: #5a6a7a;
}
.ep-lens h2,
.ep-list h2 {
  font-size: 18px;
  margin: 0 0 12px;
}
.ep-lens ol {
  margin: 0;
  padding-left: 1.25em;
  font-size: 14px;
  line-height: 1.75;
  color: #5a6a7a;
}
.ep-lens li {
  margin-bottom: 8px;
}
.ep-lens strong {
  color: #1e2a3a;
}
.ep-mid-cta {
  margin: 28px 0;
  padding: 20px 18px;
  text-align: center;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(218, 230, 245, 0.9);
  border-radius: 12px;
}
.mid-kicker {
  margin: 0 0 14px;
  font-size: 14px;
  color: #4a90d9;
  font-weight: 600;
}
.mid-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}
.btn {
  display: inline-block;
  padding: 10px 18px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  color: #357abd;
  background: #e8f0fe;
  border: 1px solid #d0e0f5;
}
.btn.primary {
  color: #fff;
  background: linear-gradient(135deg, #4a90d9 0%, #357abd 100%);
  border-color: transparent;
}
.ep-list ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.ep-list li {
  margin-bottom: 10px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(218, 230, 245, 0.9);
  border-radius: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  align-items: baseline;
}
.ep-list a {
  color: #1e2a3a;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.5;
  flex: 1 1 12em;
}
.ep-list a:hover {
  color: #357abd;
}
.tag {
  font-size: 12px;
  color: #4a90d9;
  background: #e8f0fe;
  padding: 2px 8px;
  border-radius: 999px;
}
.stat {
  font-size: 12px;
  color: #7a8ba8;
}
.ep-status {
  margin: 0;
  padding: 20px 8px;
  text-align: center;
  font-size: 14px;
  color: #5a6a7a;
}
.ep-status a {
  color: #357abd;
  font-weight: 600;
  text-decoration: none;
}
.ep-bottom {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #7a8ba8;
}
.text-link {
  color: #357abd;
  text-decoration: none;
}
.text-link.strong {
  font-weight: 600;
}
.sep {
  margin: 0 6px;
}
@media (max-width: 560px) {
  .mid-actions { flex-direction: column; }
  .btn { width: 100%; text-align: center; box-sizing: border-box; }
}
</style>
