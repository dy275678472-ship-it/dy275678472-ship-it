<template>
  <div class="placeholder-page">
    <div class="card">
      <img :src="logo" alt="LyRead AI" class="icon-img" width="64" height="64" />
      <h1>{{ title }}</h1>
      <p>{{ desc }}</p>
      <div class="actions">
        <router-link to="/" class="btn">返回首页</router-link>
        <router-link v-if="!isLoggedIn" to="/login" class="btn primary">登录 / 注册</router-link>
        <router-link v-else to="/workspace" class="btn primary">进入创作台</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { IMAGES } from '../assets/images'

const route = useRoute()
const logo = IMAGES.logo
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

const META = {
  '/workspace': { title: '创作台', desc: '作品列表、大纲编辑与章节生成正在升级中，敬请期待 V2 完整版。' },
  '/reader': { title: '长篇小说', desc: '长篇小说创作流程（人物档案 + 大纲 + 连续章节）即将上线。' },
  '/story': { title: '短故事', desc: '一键生成完整短故事，适合知乎盐选、公众号等场景。' },
  '/trending': { title: '案例阅读', desc: '平台审核通过的真实生成案例，即将开放浏览。' },
}

const title = computed(() => META[route.path]?.title || '功能开发中')
const desc = computed(() => META[route.path]?.desc || '该功能正在建设中，请先使用首页免费试用。')
</script>

<style scoped>
.placeholder-page {
  min-height: calc(100vh - 62px);
  display: flex; align-items: center; justify-content: center; padding: 40px 20px;
}
.card {
  max-width: 480px; text-align: center; background: #fff; border-radius: 20px;
  padding: 48px 32px; box-shadow: 0 8px 30px rgba(0,0,0,0.08); border: 1px solid #e8f0fa;
}
.icon-img { display: block; margin: 0 auto 16px; border-radius: 16px; object-fit: cover; }
h1 { font-size: 24px; color: #1e2a3a; margin-bottom: 12px; }
p { color: #5a6a7a; line-height: 1.6; margin-bottom: 28px; }
.actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
.btn {
  padding: 12px 24px; border-radius: 10px; text-decoration: none;
  font-weight: 600; font-size: 14px; color: #5a6a7a; background: #f1f5f9;
}
.btn.primary { background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; }
</style>
