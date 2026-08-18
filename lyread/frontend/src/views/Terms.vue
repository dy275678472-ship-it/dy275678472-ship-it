<template>
  <div class="legal-page">
    <header class="legal-hero">
      <h1>用户协议</h1>
      <p class="lede">更新日期：2026-07-21。欢迎使用 LyRead AI。请在使用前仔细阅读本协议。</p>
    </header>

    <section class="legal-block" aria-label="服务说明">
      <h2>服务说明</h2>
      <p>LyRead AI 提供 AI 辅助小说创作服务，包括书名生成、大纲、章纲、正文续写、短故事生成等。生成内容由 AI 模型产出，平台不对内容的文学质量、版权归属或商业结果作保证。</p>
    </section>

    <!-- 次屏转化：读完服务说明后立刻 register-first，对齐 SSR mid CTA -->
    <section class="legal-mid-cta" aria-label="开始创作">
      <p class="mid-kicker">注册送 30 点 · 失败不扣点</p>
      <div class="mid-actions">
        <router-link
          v-if="!isLoggedIn"
          class="btn primary"
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          @click="track('terms_mid_register')"
        >免费注册开写 →</router-link>
        <router-link
          v-else
          class="btn primary"
          :to="{ path: '/workspace', query: { mode: 'new' } }"
          @click="track('terms_mid_workspace')"
        >进入创作台 →</router-link>
        <router-link
          class="btn"
          to="/trending"
          @click="track('terms_mid_trending')"
        >先看看案例</router-link>
        <router-link
          class="btn"
          to="/pricing"
          @click="track('terms_mid_pricing')"
        >查看价格</router-link>
      </div>
    </section>

    <section class="legal-block" aria-label="账号与点数">
      <h2>账号与点数</h2>
      <ul>
        <li>注册即获赠体验点数；充值点数不可转让、不可兑换现金（法律另有规定除外）</li>
        <li>生成任务失败将全额返还已冻结点数</li>
        <li>禁止利用漏洞刷点、批量注册、恶意攻击系统</li>
      </ul>
    </section>

    <section class="legal-block" aria-label="内容规范">
      <h2>内容规范</h2>
      <p>您不得利用本平台生成、发布违反法律法规、侵犯他人权益、含有色情暴力政治敏感等内容。平台有权删除违规内容并暂停或终止账号。</p>
    </section>

    <section class="legal-block" aria-label="知识产权">
      <h2>知识产权</h2>
      <p>您对输入的原创设定与经人工实质性修改后的输出内容享有相应权利。平台服务界面、技术与品牌标识归 LyRead 所有。提交公开展示的案例，您授权平台在站内展示用于宣传与 SEO。</p>
    </section>

    <section class="legal-block" aria-label="免责声明">
      <h2>免责声明</h2>
      <p>AI 生成内容仅供参考，投稿前请自行审核合规性与原创性。因不可抗力、第三方服务中断导致的服务暂停，平台将尽力恢复但不承担间接损失。</p>
    </section>

    <section class="legal-block" aria-label="协议变更">
      <h2>协议变更</h2>
      <p>我们可能更新本协议，重大变更将在站内公告。继续使用即视为接受更新后的条款。</p>
    </section>

    <section class="legal-bottom" aria-label="下一步">
      <router-link to="/" class="text-link" @click="track('terms_home')">返回首页</router-link>
      <span class="sep">·</span>
      <router-link to="/trending" class="text-link" @click="track('terms_bottom_trending')">看案例</router-link>
      <span class="sep">·</span>
      <router-link to="/privacy" class="text-link" @click="track('terms_privacy')">隐私政策</router-link>
      <span class="sep">·</span>
      <router-link to="/faq" class="text-link" @click="track('terms_faq')">常见问题</router-link>
      <span class="sep">·</span>
      <router-link
        v-if="!isLoggedIn"
        class="text-link strong"
        :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
        @click="track('terms_bottom_register')"
      >免费注册（送 30 点）</router-link>
      <router-link
        v-else
        class="text-link strong"
        :to="{ path: '/workspace', query: { mode: 'new' } }"
        @click="track('terms_bottom_workspace')"
      >去创作台</router-link>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { trackEvent } from '../utils/analytics'

const isLoggedIn = computed(() => !!localStorage.getItem('token'))

function track(name) {
  trackEvent(name, { category: 'conversion', label: 'terms_spa' })
}

onMounted(() => {
  trackEvent('terms_view', { category: 'engagement', label: 'spa' })
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
