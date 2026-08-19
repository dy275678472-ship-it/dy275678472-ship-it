<template>
  <div class="notfound-page">
    <EmptyState
      :image="images.emptyCreate"
      image-alt="页面未找到"
      title="页面未找到"
      description="链接可能已失效或输错。可以回首页、读案例、试短故事，或直接注册开写。"
      :image-width="160"
    >
      <div v-if="resumeBanner" class="resume-banner" role="status">
        <div class="resume-copy">
          <span class="resume-kicker">上次读到</span>
          <strong class="resume-title">{{ resumeBanner.title }}</strong>
          <span class="resume-meta">已读约 {{ resumeBanner.pct }}%{{ resumeBanner.category ? ` · ${resumeBanner.category}` : '' }}</span>
        </div>
        <router-link
          class="resume-go"
          :to="`/ep/${resumeBanner.id}`"
          @click="onResumeClick"
        >继续读 →</router-link>
      </div>

      <div class="actions">
        <router-link to="/" class="btn" @click="track('notfound_home')">返回首页</router-link>
        <router-link to="/trending" class="btn" @click="track('notfound_trending')">案例阅读</router-link>
        <router-link to="/story" class="btn" @click="track('notfound_story')">试试短故事 →</router-link>
        <router-link
          v-if="!isLoggedIn"
          class="btn primary"
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          @click="track('notfound_register')"
        >免费注册（送 30 点）</router-link>
        <router-link
          v-else
          class="btn primary"
          :to="{ path: '/workspace', query: { mode: 'new' } }"
          @click="track('notfound_workspace')"
        >进入创作台</router-link>
      </div>
    </EmptyState>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import EmptyState from '../components/EmptyState.vue'
import { IMAGES } from '../assets/images'
import { findLatestResumeProgress } from '../utils/caseProgress'
import { trackEvent } from '../utils/analytics'

const route = useRoute()
const images = IMAGES
const resumeBanner = ref(null)
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

function refreshResume() {
  const hit = findLatestResumeProgress()
  resumeBanner.value = hit
    ? {
        id: hit.id,
        title: hit.title,
        category: hit.category,
        pct: Math.round(hit.ratio * 100),
      }
    : null
}

function track(name) {
  trackEvent(name, {
    category: 'funnel',
    label: route.fullPath || '/404',
  })
}

function onResumeClick() {
  const b = resumeBanner.value
  trackEvent('notfound_resume_click', {
    category: 'engagement',
    label: b?.title || '',
    value: Number(b?.id) || 0,
  })
}

onMounted(() => {
  refreshResume()
  trackEvent('notfound_view', {
    category: 'engagement',
    label: route.fullPath || '/404',
  })
})
</script>

<style scoped>
.notfound-page {
  min-height: calc(100vh - 62px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px 48px;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(77, 161, 255, 0.14), transparent 55%),
    linear-gradient(180deg, #f1f6fa 0%, #f7fafc 100%);
}
.resume-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: min(440px, 100%);
  margin: 0 auto 16px;
  padding: 12px 14px;
  text-align: left;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 12px;
}
.resume-copy { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.resume-kicker { font-size: 12px; color: #2563eb; font-weight: 600; letter-spacing: 0.02em; }
.resume-title {
  font-size: 14px;
  color: #1e2a3a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.resume-meta { font-size: 12px; color: #64748b; }
.resume-go {
  flex-shrink: 0;
  padding: 8px 14px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4da1ff, #2563eb);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}
.resume-go:hover { filter: brightness(1.05); }
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}
.btn {
  padding: 12px 20px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  color: #5a6a7a;
  background: #f1f5f9;
}
.btn.primary {
  background: linear-gradient(135deg, #4da1ff, #2563eb);
  color: #fff;
}
@media (max-width: 560px) {
  .resume-banner { flex-direction: column; align-items: stretch; }
  .resume-go { text-align: center; }
  .btn { width: 100%; text-align: center; }
}
</style>
