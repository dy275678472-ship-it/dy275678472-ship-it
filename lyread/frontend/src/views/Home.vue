<template>
  <div class="home">
    <section class="hero">
      <img :src="images.hero" alt="" class="hero-bg" aria-hidden="true" />
      <div class="hero-content">
        <h1>让 AI 陪你写完一部长篇小说</h1>
        <p class="subtitle">从人物、大纲到连续章节，自动记住剧情和伏笔；也支持快速生成完整短故事</p>
        <div class="hero-btns">
          <button class="btn-primary" @click="openTrial">免费试写第一章</button>
          <button class="btn-secondary" @click="$router.push('/trending')">查看真实案例</button>
        </div>
      </div>
    </section>

    <section class="features">
      <div class="feature-card">
        <img :src="images.features.brain" alt="小说大脑功能图标" class="icon-img" width="56" height="56" />
        <h3>小说大脑</h3>
        <p>人物档案、伏笔、章节摘要自动记忆，写到第 50 章也不乱</p>
      </div>
      <div class="feature-card">
        <img :src="images.features.novel" alt="长篇连载功能图标" class="icon-img" width="56" height="56" />
        <h3>长篇连载</h3>
        <p>大纲 → 章纲 → 正文续写，专为日更作者设计</p>
      </div>
      <div class="feature-card">
        <img :src="images.features.short" alt="短故事功能图标" class="icon-img" width="56" height="56" />
        <h3>短故事</h3>
        <p>输入想法，几分钟生成完整短篇，适合盐选/公众号</p>
      </div>
      <div class="feature-card">
        <img :src="images.features.credits" alt="点数计费功能图标" class="icon-img" width="56" height="56" />
        <h3>点数计费</h3>
        <p>用多少付多少，注册送 30 点，每日免费 5 点</p>
      </div>
    </section>

    <section class="data-proof" v-if="statsLoaded">
      <div class="data-item">
        <h3>{{ stats.users }}</h3>
        <p>注册用户</p>
      </div>
      <div class="data-item">
        <h3>{{ stats.works }}</h3>
        <p>平台作品</p>
      </div>
      <div class="data-item">
        <h3>{{ stats.cases }}</h3>
        <p>公开案例</p>
      </div>
    </section>
    <p class="stats-note" v-if="statsLoaded">数据来自平台实时统计，每日更新</p>

    <section class="pricing-cta">
      <h2>透明计费，失败全额返还</h2>
      <p>生成一章约 2000 字 ≈ 10 点（约 1 元）· 10 元 = 100 点</p>
      <router-link to="/pricing" class="btn-pricing">查看价格详情 →</router-link>
    </section>

    <section class="hot-section">
      <div class="section-header">
        <SectionHeading :icon="images.features.novel">创作案例</SectionHeading>
        <router-link v-if="hotCases.length" to="/trending" class="more-link">查看全部 →</router-link>
      </div>
      <div v-if="casesLoading" class="hot-loading">加载案例中...</div>
      <div v-else-if="!hotCases.length" class="hot-empty">
        <p>暂无公开案例，<router-link to="/workspace">开始创作</router-link> 并提交审核后将展示在这里</p>
      </div>
      <div v-else class="hot-grid">
        <a
          v-for="(c, i) in hotCases"
          :key="c.id"
          :href="c.url"
          class="hot-card hot-card-link"
          target="_blank"
          rel="noopener"
          @click="trackCaseClick(c)"
        >
          <img :src="coverForCase(c, i)" :alt="`${c.title} 封面`" class="hot-cover" loading="lazy" />
          <div class="hot-body">
            <div class="hot-type">{{ c.category || '都市' }}</div>
            <h3>{{ c.title }}</h3>
            <div class="hot-tags">
              <span>{{ formatWords(c.word_count) }}</span>
              <span>热度 {{ c.heat }}</span>
            </div>
          </div>
        </a>
      </div>
    </section>

    <!-- 用户评价 -->
    <section class="testimonials">
      <SectionHeading class="testimonials-title" :icon="images.pricing.gem" center>创作者反馈</SectionHeading>
      <p class="testimonials-note">以下为典型使用场景反馈（非个别用户承诺效果）</p>
      <div class="testimonial-grid">
        <div class="testimonial-card">
          <img :src="images.avatars.author" alt="网文作者头像" class="avatar-img" width="56" height="56" />
          <div class="name">网文作者小李</div>
          <p>"AI生成大纲太香了！10分钟搞定一本书框架"</p>
        </div>
        <div class="testimonial-card">
          <img :src="images.avatars.studio" alt="工作室负责人头像" class="avatar-img" width="56" height="56" />
          <div class="name">工作室负责人</div>
          <p>"批量产出效率翻倍，团队人手必备"</p>
        </div>
      </div>
    </section>

    <!-- 试用弹窗 -->
    <div class="modal-overlay" v-if="showTrialModal" @click.self="showTrialModal = false">
      <div class="modal-content">
        <button class="modal-close" @click="showTrialModal = false">×</button>
        <SectionHeading tag="h3" :icon="images.logo" center>免费体验 AI 创作</SectionHeading>
        <p class="trial-desc">3步生成你的第一本小说！</p>
        
        <div class="trial-steps">
          <div class="trial-step">
            <span class="step-num">1</span>
            <span>输入题材和想法</span>
          </div>
          <div class="trial-step">
            <span class="step-num">2</span>
            <span>AI生成大纲</span>
          </div>
          <div class="trial-step">
            <span class="step-num">3</span>
            <span>开始写作</span>
          </div>
        </div>

        <div class="trial-input-area">
          <select v-model="trialType" class="trial-select">
            <option value="">选择题材</option>
            <option value="fantasy">玄幻修仙</option>
            <option value="urban">都市神豪</option>
            <option value="reborn">重生流</option>
            <option value="warrior">战神归来</option>
            <option value="brainhole">脑洞文</option>
          </select>
          <input v-model="trialPrompt" placeholder="描述你的故事想法...例如：主角意外获得神豪系统，在都市纵横" class="trial-input" @keyup.enter="startTrial" />
          <button class="btn-start-trial" :disabled="trialLoading" @click="startTrial">
            {{ trialLoading ? '生成中...' : '开始创作' }}
          </button>
        </div>

        <div v-if="trialResult" class="trial-result">
          <h4>AI 为你生成的书名</h4>
          <p class="result-title">{{ trialResult.title }}</p>
          <p class="result-hook">{{ trialResult.description }}</p>
        </div>

        <div class="trial-tips">
          <span class="tip-badge"><img :src="images.pricing.gift" alt="免费试用" width="16" height="16" /> 游客可免费试用一次</span>
          <span class="tip-link" @click="$router.push('/login')">注册送 30 点 →</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { IMAGES, coverForCase } from '../assets/images'
import SectionHeading from '../components/SectionHeading.vue'
import { statsApi, casesApi } from '../api'
import { formatCount, formatWords } from '../utils/format'
import { trackEvent } from '../utils/analytics'

const router = useRouter()
const images = IMAGES

const showTrialModal = ref(false)
const trialType = ref('')
const trialPrompt = ref('')
const trialLoading = ref(false)
const trialResult = ref(null)
const statsLoaded = ref(false)
const hotCases = ref([])
const casesLoading = ref(true)

const stats = ref({
  users: '—',
  works: '—',
  cases: '—',
})

function openTrial() {
  trackEvent('trial_open', { category: 'funnel', label: 'hero_cta' })
  showTrialModal.value = true
}

function trackCaseClick(c) {
  trackEvent('case_click', { category: 'funnel', label: String(c.id) })
}

onMounted(async () => {
  try {
    const [statsRes, casesRes] = await Promise.all([
      statsApi.public(),
      casesApi.list(3),
    ])
    if (statsRes?.success) {
      stats.value = {
        users: formatCount(statsRes.users),
        works: formatCount(statsRes.works),
        cases: formatCount(statsRes.cases),
      }
      statsLoaded.value = true
    }
    if (casesRes?.success) hotCases.value = casesRes.cases || []
  } catch { /* 隐藏数据区 */ }
  finally { casesLoading.value = false }
})

const startTrial = async () => {
  if (!trialType.value || !trialPrompt.value) {
    alert('请选择题材并描述你的故事想法')
    return
  }

  trackEvent('trial_submit', { category: 'funnel', label: trialType.value })
  trialLoading.value = true
  trialResult.value = null
  try {
    const token = localStorage.getItem('token')
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers.Authorization = `Bearer ${token}`
    const res = await fetch('/api/story/generate-title', {
      method: 'POST',
      headers,
      body: JSON.stringify({ genre: trialType.value, prompt: trialPrompt.value }),
    })
    const data = await res.json()
    if (!data.success) {
      alert(data.error || data.detail || 'AI 生成失败，请稍后再试')
      return
    }
    trialResult.value = { title: data.title, description: data.description }
    trackEvent('trial_success', { category: 'funnel', label: 'generate_title' })
    if (localStorage.getItem('token')) {
      router.push({
        path: '/workspace',
        query: { type: trialType.value, prompt: trialPrompt.value, generatedTitle: data.title },
      })
      showTrialModal.value = false
    }
  } catch (error) {
    console.error('试用生成失败:', error)
    alert('AI 生成失败，请稍后再试或更换内容。')
  } finally {
    trialLoading.value = false
  }
}
</script>

<style scoped>
/* 定义全局CSS变量，这里只在Home.vue中定义，后续可以考虑提取到全局style文件 */
:root {
  --lyread-bg-light: #f1f6fa; /* 微奢冰灰蓝背景 */
  --lyread-bg-gradient-start: #eef5ff;
  --lyread-bg-gradient-end: #f6f9ff;
  --lyread-primary-blue-start: #4da1ff; /* 渐变蓝按钮起始色 */
  --lyread-primary-blue-end: #2563eb;   /* 渐变蓝按钮结束色 */
  --lyread-text-dark: #1e2a3a;
  --lyread-text-secondary: #5a6a7a;
  --lyread-card-bg: #ffffff;
  --lyread-shadow-light: rgba(0,0,0,0.06);
  --lyread-shadow-medium: rgba(0,0,0,0.08);
}

.home {
  min-height: 100vh;
  background: var(--lyread-bg-light); /* 使用微奢冰灰蓝作为主背景 */
  /* background: linear-gradient(180deg, var(--lyread-bg-gradient-end), var(--lyread-bg-gradient-start)); */ /* 可以考虑更柔和的渐变 */
  font-family: 'PingFang SC', 'Helvetica Neue', Helvetica, 'Microsoft YaHei', Arial, sans-serif;
  color: var(--lyread-text-dark);
}

.hero {
  text-align: center;
  padding: 80px 24px;
  background: linear-gradient(135deg, var(--lyread-primary-blue-start) 0%, var(--lyread-primary-blue-end) 100%);
  color: white;
  border-bottom-left-radius: 40px;
  border-bottom-right-radius: 40px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}
.hero-bg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.22;
  pointer-events: none;
}
.hero-content { position: relative; z-index: 1; }
.hero h1 { font-size: 36px; margin-bottom: 16px; }
.subtitle { font-size: 18px; opacity: 0.9; margin-bottom: 32px; }
.hero-btns { display: flex; gap: 16px; justify-content: center; }
.btn-primary, .btn-secondary, .btn-start-trial {
  padding: 16px 32px; /* 增大触摸目标 */
  min-height: 44px;   /* 最小触摸高度 */
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
  -webkit-tap-highlight-color: transparent; /* 移除移动端点击蓝色高亮 */
}
.btn-primary {
  background: var(--lyread-card-bg); /* 白色按钮 */
  color: var(--lyread-primary-blue-end);
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}
.btn-secondary, .btn-start-trial {
  background: linear-gradient(135deg, var(--lyread-primary-blue-start), var(--lyread-primary-blue-end)); /* 渐变蓝按钮 */
  color: white;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
  -webkit-backdrop-filter: blur(10px); /* 毛玻璃效果 */
  backdrop-filter: blur(10px);
  background-color: rgba(77, 161, 255, 0.7); /* 兜底颜色 */
}
.btn-secondary:hover, .btn-start-trial:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3);
  opacity: 0.9;
}

.features {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: -40px auto 60px; /* 轻微上浮，避免卡片过度压盖英雄区 */
  padding: 0 24px;
  position: relative;
  z-index: 1; /* 确保浮动在英雄区之上 */
}
.feature-card {
  background: var(--lyread-card-bg);
  border-radius: 16px;
  box-shadow: 0 4px 20px var(--lyread-shadow-medium);
  padding: 32px 24px;
  text-align: center;
  border: 1px solid rgba(255,255,255,0.1); /* 增加一点边框配合微奢感 */
  -webkit-backdrop-filter: blur(8px); /* 元素自身也带点毛玻璃感 */
  backdrop-filter: blur(8px);
  background-color: rgba(255,255,255,0.9); /* 兜底 */
}
.feature-card .icon-img { display: block; margin: 0 auto 16px; object-fit: contain; }
.feature-card h3 { color: var(--lyread-text-dark); margin-bottom: 8px; }
.feature-card p { color: var(--lyread-text-secondary); font-size: 14px; }

/* Data Proof Section */
.data-proof {
  max-width: 1200px;
  margin: 60px auto;
  padding: 40px 24px;
  background: var(--lyread-card-bg);
  border-radius: 24px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-around;
  text-align: center;
  flex-wrap: wrap; /* 确保小屏下换行 */
  gap: 30px;
}
.data-item h3 {
  font-size: 38px;
  color: var(--lyread-primary-blue-end);
  margin-bottom: 8px;
  font-weight: 700;
}
.data-item p {
  font-size: 16px;
  color: var(--lyread-text-secondary);
}


.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto 24px;
  padding: 0 24px;
}
.section-header h2,
.section-header :deep(.section-heading) { font-size: 24px; color: var(--lyread-text-dark); }
.more-link { font-size: 14px; color: var(--lyread-primary-blue-end); text-decoration: none; font-weight: 600; }
.more-link:hover { text-decoration: underline; }

.hot-loading, .hot-empty { text-align: center; color: #94a3b8; padding: 32px 0; font-size: 14px; }
.hot-empty a { color: var(--lyread-primary-blue-end); }

.hot-section { padding: 40px 24px; max-width: 1200px; margin: 0 auto; }
.hot-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.hot-card {
  background: var(--lyread-card-bg);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px var(--lyread-shadow-light);
  border: 1px solid rgba(255,255,255,0.1);
}
.hot-card-link {
  display: block;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s, box-shadow 0.2s;
}
.hot-card-link:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px var(--lyread-shadow-medium);
}
.hot-cover {
  width: 100%;
  height: 140px;
  object-fit: cover;
  display: block;
}
.hot-body { padding: 16px 20px 20px; }
.hot-type {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(77, 161, 255, 0.12); /* 浅蓝色背景（修复无效的 rgba(var()) 写法） */
  color: var(--lyread-primary-blue-end); /* 深蓝色文字 */
  border-radius: 20px;
  font-size: 12px;
  margin-bottom: 12px;
}
.hot-card h3 { font-size: 16px; color: var(--lyread-text-dark); margin-bottom: 12px; }
.hot-tags span {
  display: inline-block;
  padding: 2px 8px;
  background: #f1f5f9; /* 浅灰色背景 */
  color: var(--lyread-text-secondary);
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
}

.testimonials-note { font-size: 13px; color: #94a3b8; margin: -20px 0 24px; }
.stats-note { text-align: center; font-size: 12px; color: #94a3b8; margin: -40px auto 48px; max-width: 1200px; }
.testimonials-title { margin-bottom: 32px; font-size: 24px; }
.testimonial-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.testimonial-card {
  background: var(--lyread-card-bg);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px var(--lyread-shadow-light);
  border: 1px solid rgba(255,255,255,0.1);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  background-color: rgba(255,255,255,0.9);
}
.testimonial-card .avatar-img {
  display: block;
  width: 56px;
  height: 56px;
  margin: 0 auto 12px;
  border-radius: 50%;
  object-fit: cover;
}
.testimonial-card .name { font-weight: 600; color: var(--lyread-text-dark); margin-bottom: 8px; }
.testimonial-card p { color: var(--lyread-text-secondary); font-size: 14px; }

.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.3); /* 更轻的蒙版 */
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: var(--lyread-card-bg);
  border-radius: 16px;
  padding: 40px; /* 增加内边距 */
  width: 90%;
  max-width: 560px;
  position: relative;
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.1);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  background-color: rgba(255,255,255,0.95); /* 兜底 */
}
.modal-close {
  position: absolute; top: 16px; right: 16px;
  background: none; border: none; font-size: 24px; color: #94a3b8;
  cursor: pointer;
}
.modal-content h3 { font-size: 24px; color: var(--lyread-text-dark); margin-bottom: 8px; text-align: center; }
.trial-desc { text-align: center; color: var(--lyread-text-secondary); margin-bottom: 20px; }

.trial-steps {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}
.trial-step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--lyread-text-secondary);
}
.trial-step .step-num {
  width: 28px; /* 增大 */
  height: 28px; /* 增大 */
  background: linear-gradient(135deg, var(--lyread-primary-blue-start), var(--lyread-primary-blue-end));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.trial-input-area { display: flex; flex-direction: column; gap: 12px; }
.trial-select, .trial-input {
  padding: 16px; /* 增大 */
  border: 1px solid #e2e8f0;
  border-radius: 12px; /* 增大 */
  font-size: 15px; /* 增大 */
}
.trial-select:focus, .trial-input:focus {
  outline: none;
  border-color: var(--lyread-primary-blue-start);
  box-shadow: 0 0 0 3px rgba(77, 161, 255, 0.1);
}

.trial-tips {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  font-size: 13px;
}
.trial-tips span:first-child,
.tip-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--lyread-primary-blue-end);
  background: rgba(77, 161, 255, 0.12);
  padding: 4px 12px;
  border-radius: 20px;
}
.tip-link {
  color: var(--lyread-primary-blue-start);
  cursor: pointer;
}
.tip-link:hover { text-decoration: underline; }

.pricing-cta {
  max-width: 720px; margin: 0 auto 48px; padding: 32px 24px; text-align: center;
  background: linear-gradient(135deg, #fff7e6, #ffe9c7); border-radius: 20px;
  border: 1px solid #ffd591;
}
.pricing-cta h2 { font-size: 22px; color: #ad6800; margin-bottom: 8px; }
.pricing-cta p { color: #8c6d1f; margin-bottom: 16px; font-size: 14px; }
.btn-pricing {
  display: inline-block; padding: 10px 22px; border-radius: 10px;
  background: #fff; color: #ad6800; font-weight: 600; text-decoration: none;
  border: 1px solid #ffd591;
}
.trial-result {
  margin-top: 16px; padding: 16px; background: #f0f9ff; border-radius: 12px;
  border: 1px solid #bae6fd; text-align: left;
}
.trial-result h4 { font-size: 14px; color: #0369a1; margin-bottom: 8px; }
.result-title { font-weight: 700; color: #1e2a3a; margin-bottom: 6px; }
.result-hook { font-size: 13px; color: #5a6a7a; }

/* 媒体查询调整 */
@media (max-width: 1024px) {
  .features {
    grid-template-columns: repeat(2, 1fr); /* 4列 -> 2列 */
  }
}
@media (max-width: 768px) {
  .hot-grid, .testimonial-grid {
    grid-template-columns: 1fr; /* 2列 -> 1列 */
  }
  .features {
    grid-template-columns: 1fr; /* 单列 */
    margin-top: 24px; /* 移动端不再上浮压盖英雄区，避免错位 */
    gap: 16px;
  }
  .hero {
    padding: 60px 16px;
  }
  .hero h1 {
    font-size: 28px;
  }
  .subtitle {
    font-size: 16px;
  }
  .hero-btns {
    flex-direction: column;
  }
  .btn-primary, .btn-secondary, .btn-start-trial {
    width: 100%;
    max-width: 300px;
    margin: 0 auto;
  }
  .data-proof {
    padding: 30px 16px;
    gap: 20px;
  }
  .data-item h3 {
    font-size: 30px;
  }
  .data-item p {
    font-size: 14px;
  }
  .modal-content {
    padding: 30px;
  }
  .modal-content h3 {
    font-size: 20px;
  }
  .trial-steps {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>