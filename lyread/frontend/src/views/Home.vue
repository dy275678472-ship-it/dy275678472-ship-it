<template>
  <div class="home">
    <!-- Hero区域 -->
    <section class="hero">
      <h1>🧠 AI智能小说创作平台</h1>
      <p class="subtitle">70% AI + 30% 人工 · 让创作更简单</p>
      <div class="hero-btns">
        <button class="btn-primary" @click="$router.push('/reader')">开始创作</button>
        <button class="btn-secondary" @click="showTrialModal = true">免费试用</button>
      </div>
    </section>

    <section class="features">
      <div class="feature-card">
        <div class="icon">✍️</div>
        <h3>AI创作</h3>
        <p>70%AI+30%人工，快速构建小说世界观</p>
      </div>
      <div class="feature-card">
        <div class="icon">🛡️</div>
        <h3>版权保护</h3>
        <p>多重加密存储，确保您的作品版权</p>
      </div>
      <div class="feature-card">
        <div class="icon">🚀</div>
        <h3>全网推流</h3>
        <p>AI智能分发，让您的作品触达更多读者</p>
      </div>
      <div class="feature-card">
        <div class="icon">💰</div>
        <h3>版权交易</h3>
        <p>一站式版权交易，收益最大化</p>
      </div>
    </section>

    <!-- 数据证明 -->
    <section class="data-proof">
      <div class="data-item">
        <h3>{{ stats.users }}</h3>
        <p>注册用户</p>
      </div>
      <div class="data-item">
        <h3>{{ stats.novels }}</h3>
        <p>AI生成小说</p>
      </div>
      <div class="data-item">
        <h3>{{ stats.satisfaction }}</h3>
        <p>用户满意度</p>
      </div>
    </section>

    <!-- 热门推荐 -->
    <section class="hot-section">
      <div class="section-header">
        <h2>🔥 热门推荐</h2>
      </div>
      <div class="hot-grid">
        <div class="hot-card">
          <div class="hot-type">都市神豪</div>
          <h3>开局十个亿，我在都市横着走</h3>
          <div class="hot-tags"><span>系统</span><span>爽文</span></div>
        </div>
        <div class="hot-card">
          <div class="hot-type">战神归来</div>
          <h3>战神回归，发现女儿住狗窝</h3>
          <div class="hot-tags"><span>虐心</span><span>逆袭</span></div>
        </div>
        <div class="hot-card">
          <div class="hot-type">重生</div>
          <h3>重生2003，当首富很简单</h3>
          <div class="hot-tags"><span>创业</span><span>赚钱</span></div>
        </div>
      </div>
    </section>

    <!-- 用户评价 -->
    <section class="testimonials">
      <h2>⭐ 用户评价</h2>
      <div class="testimonial-grid">
        <div class="testimonial-card">
          <div class="avatar">👨‍💻</div>
          <div class="name">网文作者小李</div>
          <p>"AI生成大纲太香了！10分钟搞定一本书框架"</p>
        </div>
        <div class="testimonial-card">
          <div class="avatar">👩‍🎨</div>
          <div class="name">工作室负责人</div>
          <p>"批量产出效率翻倍，团队人手必备"</p>
        </div>
      </div>
    </section>

    <!-- 试用弹窗 -->
    <div class="modal-overlay" v-if="showTrialModal" @click.self="showTrialModal = false">
      <div class="modal-content">
        <button class="modal-close" @click="showTrialModal = false">×</button>
        <h3>🎯 免费体验AI创作</h3>
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
          <button class="btn-start-trial" @click="startTrial">
            🚀 开始创作
          </button>
        </div>

        <div class="trial-tips">
          <span>🎁 今日免费次数: 3</span>
          <span class="tip-link" @click="$router.push('/login')">登录后可保存作品 →</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const showTrialModal = ref(false)
const trialType = ref('')
const trialPrompt = ref('')
const trialLoading = ref(false)

// 新增数据证明数据
const stats = ref({
  users: '10万+',
  novels: '50万+',
  satisfaction: '98%'
})

const startTrial = async () => {
  if (!trialType.value || !trialPrompt.value) {
    alert('请选择题材并描述你的故事想法')
    return
  }

  trialLoading.value = true
  try {
    // 调用 /api/story/generate-title 进行试用生成
    const response = await axios.post('/api/story/generate-title', {
      genre: trialType.value,
      prompt: trialPrompt.value
    })
    
    // 假设 generate-title 返回了 title 和 description
    const { title, description } = response.data

    // 成功后跳转到创作工作台，带上生成的内容
    router.push({
      path: '/workspace',
      query: {
        type: trialType.value,
        prompt: trialPrompt.value,
        generatedTitle: title,
        generatedDescription: description
      }
    })
    showTrialModal.value = false
  } catch (error) {
    console.error('试用生成失败:', error)
    alert('AI生成失败，请稍后再试或更换内容。')
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
  background: linear-gradient(135deg, var(--lyread-primary-blue-start) 0%, var(--lyread-primary-blue-end) 100%); /* 渐变蓝英雄区背景 */
  color: white;
  border-bottom-left-radius: 40px; /* 毛玻璃效果的圆角 */
  border-bottom-right-radius: 40px;
  position: relative;
  overflow: hidden; /* 确保背景渐变和圆角正确 */
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}
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
.feature-card .icon { font-size: 40px; margin-bottom: 16px; }
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
.section-header h2 { color: var(--lyread-text-dark); }

.hot-section { padding: 40px 24px; max-width: 1200px; margin: 0 auto; }
.hot-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.hot-card {
  background: var(--lyread-card-bg);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px var(--lyread-shadow-light);
  border: 1px solid rgba(255,255,255,0.1);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  background-color: rgba(255,255,255,0.9);
}
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

.testimonials { padding: 40px 24px; max-width: 1200px; margin: 0 auto; text-align: center; }
.testimonials h2 { margin-bottom: 32px; color: var(--lyread-text-dark); }
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
.testimonial-card .avatar { font-size: 40px; margin-bottom: 12px; }
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
.trial-tips span:first-child {
  color: var(--lyread-primary-blue-end); /* 使用蓝色 */
  background: rgba(77, 161, 255, 0.12); /* 修复无效的 rgba(var()) 写法 */
  padding: 4px 12px;
  border-radius: 20px;
}
.tip-link {
  color: var(--lyread-primary-blue-start);
  cursor: pointer;
}
.tip-link:hover { text-decoration: underline; }

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