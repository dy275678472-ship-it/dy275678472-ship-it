<template>
  <div class="guide-page">
    <header class="guide-hero">
      <h1>AI 写小说教程</h1>
      <p class="lede">从灵感到章纲、日更与降 AI 味——按阶段选一篇，读完即可开写。</p>
    </header>

    <section class="guide-flow" aria-label="一套可执行的创作顺序">
      <h2>一套可执行的创作顺序</h2>
      <ol>
        <li><strong>确定目标</strong> — 明确题材、读者预期和本次要完成的篇幅。</li>
        <li><strong>先做结构</strong> — 锁定主线、大纲与最近一批章纲，再生成正文。</li>
        <li><strong>逐章编辑</strong> — 生成结果先人工修改对话、节奏和细节，不直接发布。</li>
        <li><strong>定期检查</strong> — 核对人物状态、时间线和未回收伏笔，再进入下一批章节。</li>
      </ol>
    </section>

    <!-- 次屏转化：扫完流程后立刻 register-first，避免裸 /workspace -->
    <section class="guide-mid-cta" aria-label="开始创作">
      <p class="mid-kicker">注册送 30 点 · 失败不扣点</p>
      <div class="mid-actions">
        <router-link
          v-if="!isLoggedIn"
          class="btn primary"
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          @click="track('guide_mid_register')"
        >免费注册开写 →</router-link>
        <router-link
          v-else
          class="btn primary"
          :to="{ path: '/workspace', query: { mode: 'new' } }"
          @click="track('guide_mid_workspace')"
        >进入创作台 →</router-link>
        <router-link
          class="btn"
          to="/trending"
          @click="track('guide_mid_trending')"
        >先看看案例</router-link>
        <router-link
          class="btn"
          to="/story"
          @click="track('guide_mid_story')"
        >试试短故事</router-link>
      </div>
    </section>

    <section class="guide-list" aria-label="全部创作教程">
      <h2>全部创作教程</h2>
      <ul>
        <li v-for="item in guides" :key="item.slug">
          <!-- 文章页仍走完整刷新 SSR，保留爬虫正文与 JSON-LD -->
          <a
            :href="`/guide/${item.slug}`"
            @click="track('guide_article_click', item.slug)"
          >{{ item.title }}</a>
        </li>
      </ul>
    </section>

    <section class="guide-bottom" aria-label="下一步">
      <router-link to="/genre" class="text-link" @click="track('guide_genre')">题材聚合</router-link>
      <span class="sep">·</span>
      <router-link to="/pricing" class="text-link" @click="track('guide_pricing')">查看价格</router-link>
      <span class="sep">·</span>
      <router-link to="/faq" class="text-link" @click="track('guide_faq')">常见问题</router-link>
      <span class="sep">·</span>
      <router-link
        v-if="!isLoggedIn"
        class="text-link strong"
        :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
        @click="track('guide_bottom_register')"
      >免费注册（送 30 点）</router-link>
      <router-link
        v-else
        class="text-link strong"
        :to="{ path: '/workspace', query: { mode: 'new' } }"
        @click="track('guide_bottom_workspace')"
      >去创作台</router-link>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { trackEvent } from '../utils/analytics'

/** 与 backend GUIDE_PAGES 标题对齐，便于 SPA / SSR 口径一致 */
const guides = [
  { slug: 'ai-novel-start', title: 'AI写小说入门教程（2026）- 从灵感到第一章' },
  { slug: 'outline-chapters', title: 'AI 小说大纲与章纲怎么写？附工作流模板' },
  { slug: 'daily-update', title: '网文日更 AI 续写技巧 - 如何稳定产出 6000 字' },
  { slug: 'monetize', title: 'AI 写小说怎么赚钱？2026 实战路径' },
  { slug: 'consistency', title: 'AI 写长篇小说如何保持设定一致？' },
  { slug: 'platform-submit', title: 'AI 小说投稿平台指南：番茄/起点/盐选怎么选？' },
  { slug: 'reduce-ai-taste', title: 'AI 写小说如何降 AI 味？7 个实操技巧' },
]

const isLoggedIn = computed(() => !!localStorage.getItem('token'))

function track(name, label = 'guide_spa') {
  trackEvent(name, { category: 'conversion', label })
}

onMounted(() => {
  trackEvent('guide_view', { category: 'engagement', label: 'spa' })
})
</script>

<style scoped>
.guide-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 28px 20px 56px;
  color: #1e2a3a;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(74, 144, 217, 0.12), transparent 60%),
    linear-gradient(180deg, #f7fafc 0%, #eef3f9 100%);
  min-height: calc(100vh - 120px);
}
.guide-hero {
  text-align: center;
  margin-bottom: 24px;
}
.guide-hero h1 {
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
.guide-flow h2,
.guide-list h2 {
  font-size: 18px;
  margin: 0 0 12px;
}
.guide-flow ol {
  margin: 0;
  padding-left: 1.25em;
  font-size: 14px;
  line-height: 1.75;
  color: #5a6a7a;
}
.guide-flow li {
  margin-bottom: 8px;
}
.guide-flow strong {
  color: #1e2a3a;
}
.guide-mid-cta {
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
.guide-list ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.guide-list li {
  margin-bottom: 10px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(218, 230, 245, 0.9);
  border-radius: 10px;
}
.guide-list a {
  color: #1e2a3a;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.5;
}
.guide-list a:hover {
  color: #357abd;
}
.guide-bottom {
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
