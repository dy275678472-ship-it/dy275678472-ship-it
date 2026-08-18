<template>
  <div class="legal-page">
    <header class="legal-hero">
      <h1>隐私政策</h1>
      <p class="lede">更新日期：2026-07-21。LyRead AI（https://lyread.cn）重视用户隐私保护。使用本平台即表示您同意本政策。</p>
    </header>

    <section class="legal-block" aria-label="我们收集的信息">
      <h2>我们收集的信息</h2>
      <ul>
        <li><strong>账号信息：</strong>注册邮箱、昵称（您主动提供）</li>
        <li><strong>创作内容：</strong>您输入的题材、大纲、章节正文等，用于提供 AI 生成服务</li>
        <li><strong>交易信息：</strong>充值订单、点数变动记录（支付由支付宝等第三方处理，我们不存储完整支付密码）</li>
        <li><strong>技术日志：</strong>IP、浏览器类型、访问时间，用于安全与故障排查</li>
      </ul>
    </section>

    <!-- 次屏转化：读完收集条款后立刻 register-first，对齐 SSR mid CTA -->
    <section class="legal-mid-cta" aria-label="开始创作">
      <p class="mid-kicker">注册送 30 点 · 失败不扣点</p>
      <div class="mid-actions">
        <router-link
          v-if="!isLoggedIn"
          class="btn primary"
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          @click="track('privacy_mid_register')"
        >免费注册开写 →</router-link>
        <router-link
          v-else
          class="btn primary"
          :to="{ path: '/workspace', query: { mode: 'new' } }"
          @click="track('privacy_mid_workspace')"
        >进入创作台 →</router-link>
        <router-link
          class="btn"
          to="/trending"
          @click="track('privacy_mid_trending')"
        >先看看案例</router-link>
        <router-link
          class="btn"
          to="/story"
          @click="track('privacy_mid_story')"
        >试试短故事</router-link>
      </div>
    </section>

    <section class="legal-block" aria-label="信息如何使用">
      <h2>信息如何使用</h2>
      <ul>
        <li>提供、维护与改进 AI 创作服务（含小说大脑记忆功能）</li>
        <li>处理充值、退款与客服请求</li>
        <li>经您同意后公开展示的案例作品（可在提交审核时选择）</li>
        <li>遵守法律法规要求</li>
      </ul>
    </section>

    <section class="legal-block" aria-label="信息存储与安全">
      <h2>信息存储与安全</h2>
      <p>数据存储于中华人民共和国境内服务器，采用加密传输（HTTPS）与访问控制。我们不会向无关第三方出售您的个人信息。</p>
    </section>

    <section class="legal-block" aria-label="您的权利">
      <h2>您的权利</h2>
      <p>您可申请查阅、更正或删除账号与创作数据。注销账号请联系客服或通过设置页面操作（功能陆续开放）。</p>
    </section>

    <section class="legal-block" aria-label="联系我们">
      <h2>联系我们</h2>
      <p>隐私相关问题请通过网站「关于我们」页面所列方式联系。</p>
    </section>

    <section class="legal-bottom" aria-label="下一步">
      <router-link to="/terms" class="text-link" @click="track('privacy_terms')">用户协议</router-link>
      <span class="sep">·</span>
      <router-link to="/about" class="text-link" @click="track('privacy_about')">关于我们</router-link>
      <span class="sep">·</span>
      <router-link
        v-if="!isLoggedIn"
        class="text-link strong"
        :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
        @click="track('privacy_bottom_register')"
      >免费注册（送 30 点）</router-link>
      <router-link
        v-else
        class="text-link strong"
        :to="{ path: '/workspace', query: { mode: 'new' } }"
        @click="track('privacy_bottom_workspace')"
      >去创作台</router-link>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { trackEvent } from '../utils/analytics'

const isLoggedIn = computed(() => !!localStorage.getItem('token'))

function track(name) {
  trackEvent(name, { category: 'conversion', label: 'privacy_spa' })
}

onMounted(() => {
  trackEvent('privacy_view', { category: 'engagement', label: 'spa' })
})
</script>

<style scoped>
.legal-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 28px 20px 56px;
  color: #1e2a3a;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(74, 144, 217, 0.12), transparent 60%),
    linear-gradient(180deg, #f7fafc 0%, #eef3f9 100%);
  min-height: calc(100vh - 120px);
}
.legal-hero {
  text-align: center;
  margin-bottom: 24px;
}
.legal-hero h1 {
  font-size: 28px;
  margin: 0 0 10px;
  letter-spacing: 0.02em;
}
.lede {
  margin: 0 auto;
  max-width: 36em;
  font-size: 15px;
  line-height: 1.65;
  color: #5a6a7a;
}
.legal-block {
  margin-bottom: 8px;
}
.legal-block h2 {
  font-size: 18px;
  margin: 20px 0 12px;
}
.legal-block ul {
  margin: 0;
  padding-left: 1.2em;
  line-height: 1.8;
  color: #3a4a5e;
  font-size: 14px;
}
.legal-block p {
  margin: 0;
  font-size: 14px;
  line-height: 1.75;
  color: #3a4a5e;
}
.legal-mid-cta {
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
.legal-bottom {
  margin-top: 28px;
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
