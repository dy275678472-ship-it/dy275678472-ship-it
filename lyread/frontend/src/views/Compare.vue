<template>
  <div class="compare-page">
    <header class="compare-hero">
      <h1>AI 写小说工具对比</h1>
      <p class="lede">按长篇记忆、创作工作流、使用成本与适用场景选型——读完即可注册开写。</p>
    </header>

    <section class="compare-lens" aria-label="怎么比才有用">
      <h2>怎么比才有用</h2>
      <ol>
        <li><strong>看定位</strong> — 通用助手 vs 网文连载工具，决定上手成本与后期一致性。</li>
        <li><strong>看记忆</strong> — 写到 30 章以后，人物/伏笔是否还能稳住。</li>
        <li><strong>看计费</strong> — 套餐订阅 vs 按章点数；失败是否扣点。</li>
        <li><strong>看工作流</strong> — 有没有大纲 → 章纲 → 续写的标准路径。</li>
      </ol>
    </section>

    <!-- 次屏转化：扫完选型维度后立刻 register-first，避免裸 /workspace -->
    <section class="compare-mid-cta" aria-label="开始创作">
      <p class="mid-kicker">注册送 30 点 · 失败不扣点</p>
      <div class="mid-actions">
        <router-link
          v-if="!isLoggedIn"
          class="btn primary"
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          @click="track('compare_mid_register')"
        >免费注册开写 →</router-link>
        <router-link
          v-else
          class="btn primary"
          :to="{ path: '/workspace', query: { mode: 'new' } }"
          @click="track('compare_mid_workspace')"
        >进入创作台 →</router-link>
        <router-link
          class="btn"
          to="/trending"
          @click="track('compare_mid_trending')"
        >先看看案例</router-link>
        <router-link
          class="btn"
          to="/story"
          @click="track('compare_mid_story')"
        >试试短故事</router-link>
      </div>
    </section>

    <section class="compare-list" aria-label="全部工具对比">
      <h2>全部工具对比</h2>
      <ul>
        <li v-for="item in compares" :key="item.slug">
          <!-- 文章页仍走完整刷新 SSR，保留爬虫正文与 JSON-LD -->
          <a
            :href="`/compare/${item.slug}`"
            @click="track('compare_article_click', item.slug)"
          >{{ item.title }}</a>
        </li>
      </ul>
    </section>

    <section class="compare-bottom" aria-label="下一步">
      <router-link to="/pricing" class="text-link" @click="track('compare_pricing')">查看价格</router-link>
      <span class="sep">·</span>
      <router-link to="/guide" class="text-link" @click="track('compare_guide')">创作教程</router-link>
      <span class="sep">·</span>
      <router-link
        v-if="!isLoggedIn"
        class="text-link strong"
        :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
        @click="track('compare_bottom_register')"
      >免费注册（送 30 点）</router-link>
      <router-link
        v-else
        class="text-link strong"
        :to="{ path: '/workspace', query: { mode: 'new' } }"
        @click="track('compare_bottom_workspace')"
      >去创作台</router-link>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { trackEvent } from '../utils/analytics'

/** 与 backend COMPARE_PAGES 标题对齐，便于 SPA / SSR 口径一致 */
const compares = [
  { slug: 'biling', title: 'LyRead vs 笔灵AI写作：写长篇网文哪个更合适？' },
  { slug: 'waqupin', title: 'LyRead vs 蛙趣拼文：长篇 AI 写作工具对比' },
  { slug: 'chatgpt', title: 'LyRead vs 直接用 ChatGPT 写小说：为什么要用专业工具？' },
  { slug: 'kimi', title: 'LyRead vs Kimi 写小说：专业连载工具对比' },
  { slug: 'doubao', title: 'LyRead vs 豆包写小说：哪个更适合网文作者？' },
  { slug: 'tongyi', title: 'LyRead vs 通义千问写小说：通用大模型 vs 网文工作流' },
  { slug: 'wenxin', title: 'LyRead vs 文心一言写小说：哪个更适合日更作者？' },
]

const isLoggedIn = computed(() => !!localStorage.getItem('token'))

function track(name, label = 'compare_spa') {
  trackEvent(name, { category: 'conversion', label })
}

onMounted(() => {
  trackEvent('compare_view', { category: 'engagement', label: 'spa' })
})
</script>

<style scoped>
.compare-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 28px 20px 56px;
  color: #1e2a3a;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(74, 144, 217, 0.12), transparent 60%),
    linear-gradient(180deg, #f7fafc 0%, #eef3f9 100%);
  min-height: calc(100vh - 120px);
}
.compare-hero {
  text-align: center;
  margin-bottom: 24px;
}
.compare-hero h1 {
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
.compare-lens h2,
.compare-list h2 {
  font-size: 18px;
  margin: 0 0 12px;
}
.compare-lens ol {
  margin: 0;
  padding-left: 1.25em;
  font-size: 14px;
  line-height: 1.75;
  color: #5a6a7a;
}
.compare-lens li {
  margin-bottom: 8px;
}
.compare-lens strong {
  color: #1e2a3a;
}
.compare-mid-cta {
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
.compare-list ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.compare-list li {
  margin-bottom: 10px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(218, 230, 245, 0.9);
  border-radius: 10px;
}
.compare-list a {
  color: #1e2a3a;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.5;
}
.compare-list a:hover {
  color: #357abd;
}
.compare-bottom {
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
