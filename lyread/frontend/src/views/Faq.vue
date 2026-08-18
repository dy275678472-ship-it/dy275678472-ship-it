<template>
  <div class="faq-page">
    <header class="faq-hero">
      <h1>常见问题</h1>
      <p class="lede">计费、试用、长篇创作与点数返还——读完即可开写。</p>
    </header>

    <section class="faq-list" aria-label="常见问题">
      <details v-for="(item, idx) in faqs" :key="item.q" :open="idx < 2">
        <summary>{{ item.q }}</summary>
        <p>{{ item.a }}</p>
      </details>
    </section>

    <!-- 次屏转化：扫完前几条 FAQ 后立刻 register-first，不等页底 -->
    <section class="faq-mid-cta" aria-label="开始创作">
      <p class="mid-kicker">注册送 30 点 · 失败不扣点</p>
      <div class="mid-actions">
        <router-link
          v-if="!isLoggedIn"
          class="btn primary"
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          @click="track('faq_mid_register')"
        >免费注册开写 →</router-link>
        <router-link
          v-else
          class="btn primary"
          :to="{ path: '/workspace', query: { mode: 'new' } }"
          @click="track('faq_mid_workspace')"
        >进入创作台 →</router-link>
        <router-link
          class="btn"
          to="/trending"
          @click="track('faq_mid_trending')"
        >先看看案例</router-link>
        <router-link
          class="btn"
          to="/story"
          @click="track('faq_mid_story')"
        >试试短故事</router-link>
      </div>
    </section>

    <section class="faq-bottom" aria-label="下一步">
      <router-link to="/pricing" class="text-link" @click="track('faq_pricing')">查看价格</router-link>
      <span class="sep">·</span>
      <router-link to="/about" class="text-link" @click="track('faq_about')">关于我们</router-link>
      <span class="sep">·</span>
      <router-link
        v-if="!isLoggedIn"
        class="text-link strong"
        :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
        @click="track('faq_bottom_register')"
      >免费注册（送 30 点）</router-link>
      <router-link
        v-else
        class="text-link strong"
        :to="{ path: '/workspace', query: { mode: 'new' } }"
        @click="track('faq_bottom_workspace')"
      >去创作台</router-link>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { trackEvent } from '../utils/analytics'

/** 与后端 SITE_FAQS 对齐，便于 SPA / SSR 口径一致 */
const faqs = [
  {
    q: 'LyRead AI 是什么？',
    a: 'LyRead AI 是中文智能小说创作平台，支持 AI 生成书名、大纲、章纲与正文，并提供人物、伏笔记忆能力，适合长篇连载与短故事创作。',
  },
  {
    q: '如何计费？',
    a: '采用点数按量计费：注册送 30 点，每日免费 5 点，10 元 = 100 点。生成一章约 2000 字约消耗 10 点（约 1 元）。无月费或终身套餐。',
  },
  {
    q: '生成失败会扣点吗？',
    a: '不会。任务失败会自动全额返还已冻结的点数。',
  },
  {
    q: '可以写长篇小说吗？',
    a: '可以。LyRead 支持大纲、章纲、正文续写，并通过「小说大脑」记录人物、伏笔与章节摘要，适合长篇连载。',
  },
  {
    q: '有免费试用吗？',
    a: '可以。首页支持游客试用书名生成；注册后再领 30 点与每日 5 点免费额度。',
  },
  {
    q: '案例作品是真实的吗？',
    a: '案例区展示平台审核通过的 AI 生成作品，供参考风格与质量。',
  },
]

const isLoggedIn = computed(() => !!localStorage.getItem('token'))

function track(name) {
  trackEvent(name, { category: 'conversion', label: 'faq_spa' })
}

onMounted(() => {
  trackEvent('faq_view', { category: 'engagement', label: 'spa' })
})
</script>

<style scoped>
.faq-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 28px 20px 56px;
  color: #1e2a3a;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(74, 144, 217, 0.12), transparent 60%),
    linear-gradient(180deg, #f7fafc 0%, #eef3f9 100%);
  min-height: calc(100vh - 120px);
}
.faq-hero {
  text-align: center;
  margin-bottom: 24px;
}
.faq-hero h1 {
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
.faq-list details {
  margin-bottom: 10px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(218, 230, 245, 0.9);
  border-radius: 10px;
}
.faq-list summary {
  cursor: pointer;
  font-weight: 600;
  color: #1e2a3a;
  font-size: 14px;
}
.faq-list p {
  margin: 10px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: #5a6a7a;
}
.faq-mid-cta {
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
.faq-bottom {
  margin-top: 8px;
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
