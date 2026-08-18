<template>
  <div class="about-page">
    <header class="about-hero">
      <img :src="images.logo" alt="LyRead AI" class="about-logo" width="48" height="48" />
      <h1>LyRead AI</h1>
      <p class="lede">面向中文作者的智能小说创作平台：大纲 → 章纲 → 续写，人物伏笔自动记忆，按章点数计费。</p>
    </header>

    <section class="about-problems" aria-label="我们解决什么问题">
      <h2>我们解决什么问题</h2>
      <ul>
        <li><strong>开书难</strong> — AI 快速生成书名、大纲与章纲</li>
        <li><strong>连载乱</strong> — 小说大脑记忆人物、伏笔与章节摘要</li>
        <li><strong>成本高</strong> — 按章计费，失败全额返还</li>
      </ul>
    </section>

    <!-- 次屏转化：读完痛点后立刻 register-first，不等页底 -->
    <section class="about-mid-cta" aria-label="开始创作">
      <p class="mid-kicker">注册送 30 点 · 失败不扣点</p>
      <div class="mid-actions">
        <router-link
          v-if="!isLoggedIn"
          class="btn primary"
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          @click="track('about_mid_register')"
        >免费注册开写 →</router-link>
        <router-link
          v-else
          class="btn primary"
          :to="{ path: '/workspace', query: { mode: 'new' } }"
          @click="track('about_mid_workspace')"
        >进入创作台 →</router-link>
        <router-link
          class="btn"
          to="/trending"
          @click="track('about_mid_trending')"
        >先看看案例</router-link>
        <router-link
          class="btn"
          to="/story"
          @click="track('about_mid_story')"
        >试试短故事</router-link>
      </div>
    </section>

    <section class="about-features" aria-label="核心功能">
      <h2>核心功能</h2>
      <div class="feat-grid">
        <div class="feat">
          <img :src="images.features.novel" alt="" width="40" height="40" />
          <strong>长篇连载</strong>
          <span>大纲 → 章纲 → 正文续写</span>
        </div>
        <div class="feat">
          <img :src="images.features.short" alt="" width="40" height="40" />
          <strong>短故事</strong>
          <span>几分钟生成完整短篇</span>
        </div>
        <div class="feat">
          <img :src="images.features.brain" alt="" width="40" height="40" />
          <strong>小说大脑</strong>
          <span>人物 / 伏笔 / 摘要记忆</span>
        </div>
        <div class="feat">
          <img :src="images.features.credits" alt="" width="40" height="40" />
          <strong>透明计费</strong>
          <span>10 元 = 100 点，注册送 30 点</span>
        </div>
      </div>
    </section>

    <section class="about-bottom" aria-label="下一步">
      <router-link to="/" class="text-link" @click="track('about_home')">返回首页</router-link>
      <span class="sep">·</span>
      <router-link to="/trending" class="text-link" @click="track('about_bottom_trending')">看案例</router-link>
      <span class="sep">·</span>
      <router-link to="/pricing" class="text-link" @click="track('about_pricing')">查看价格</router-link>
      <span class="sep">·</span>
      <router-link to="/faq" class="text-link" @click="track('about_faq')">常见问题</router-link>
      <span class="sep">·</span>
      <router-link
        v-if="!isLoggedIn"
        class="text-link strong"
        :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
        @click="track('about_bottom_register')"
      >免费注册（送 30 点）</router-link>
      <router-link
        v-else
        class="text-link strong"
        :to="{ path: '/workspace', query: { mode: 'new' } }"
        @click="track('about_bottom_workspace')"
      >去创作台</router-link>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { IMAGES } from '../assets/images'
import { trackEvent } from '../utils/analytics'

const images = IMAGES
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

function track(name) {
  trackEvent(name, { category: 'conversion', label: 'about_spa' })
}

onMounted(() => {
  trackEvent('about_view', { category: 'engagement', label: 'spa' })
})
</script>

<style scoped>
.about-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 28px 20px 56px;
  color: #1e2a3a;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(74, 144, 217, 0.12), transparent 60%),
    linear-gradient(180deg, #f7fafc 0%, #eef3f9 100%);
  min-height: calc(100vh - 120px);
}
.about-hero {
  text-align: center;
  margin-bottom: 28px;
}
.about-logo {
  margin-bottom: 10px;
}
.about-hero h1 {
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
.about-problems h2,
.about-features h2 {
  font-size: 18px;
  margin: 0 0 12px;
}
.about-problems ul {
  margin: 0;
  padding-left: 1.2em;
  line-height: 1.85;
  color: #3a4a5e;
  font-size: 14px;
}
.about-mid-cta {
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
.feat-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.feat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 10px;
  border: 1px solid rgba(218, 230, 245, 0.7);
  font-size: 13px;
  color: #5a6a7a;
}
.feat strong {
  color: #1e2a3a;
  font-size: 14px;
}
.about-bottom {
  margin-top: 32px;
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
  .feat-grid { grid-template-columns: 1fr; }
  .mid-actions { flex-direction: column; }
  .btn { width: 100%; text-align: center; box-sizing: border-box; }
}
</style>
