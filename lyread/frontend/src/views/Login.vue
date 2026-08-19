<template>
  <div class="login-page">
    <div class="login-layout">
      <div class="login-visual" aria-hidden="true">
        <img :src="illustration" alt="" class="login-illustration" />
        <p class="visual-caption">AI 陪你写完一部长篇小说</p>
      </div>
      <div class="login-card">
      <div class="brand">
        <img :src="logo" alt="LyRead" class="logo-img" width="48" height="48" />
        <span class="logo-text">LyRead</span>
      </div>
      <p class="subtitle">AI小说创作引擎</p>

      <div v-if="intentBanner" class="intent-banner" role="status">
        <strong>{{ intentBanner.title }}</strong>
        <p>{{ intentBanner.detail }}</p>
      </div>
      <div v-else-if="resumeOffer" class="resume-banner" role="status">
        <strong>上次读到 · {{ resumeOffer.title }}</strong>
        <p>已读约 {{ resumeOffer.pct }}%{{ resumeOffer.category ? ` · ${resumeOffer.category}` : '' }} · 登录后可继续读</p>
      </div>
      <div v-else-if="showRegister" class="intent-banner welcome-cold" role="status">
        <strong>注册送 30 点，马上开写</strong>
        <p>约可写 3 章 · 生成失败全额返还 · 也可先读案例找灵感</p>
      </div>
      <div v-else-if="!showForgot && !showReset" class="intent-banner welcome-cold soft" role="status">
        <strong>欢迎回来</strong>
        <p>登录后继续创作；没有账号？注册送 30 点，失败不扣点</p>
      </div>
      
      <!-- 注册表单 -->
      <form v-if="showRegister" @submit.prevent="handleRegister">
        <input 
          v-model="form.username" 
          type="text" 
          class="input" 
          placeholder="用户名"
          required
        />
        <input 
          v-model="form.email" 
          type="email" 
          class="input" 
          placeholder="邮箱（选填）"
        />
        <input 
          v-model="form.password" 
          type="password" 
          class="input" 
          placeholder="密码"
          required
        />
        <input 
          v-model="form.confirmPassword" 
          type="password" 
          class="input" 
          placeholder="确认密码"
          required
        />
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? '注册中...' : registerCtaLabel }}
        </button>
      </form>

      <!-- 找回密码 -->
      <form v-else-if="showForgot" @submit.prevent="handleForgot">
        <p v-if="recoveryHint" class="recovery-hint" role="status">{{ recoveryHint }}</p>
        <input v-model="form.username" type="text" class="input" placeholder="用户名" required />
        <input v-model="form.email" type="email" class="input" placeholder="注册邮箱" required />
        <button type="submit" class="btn btn-primary" :disabled="loading || recoveryBlocked">
          {{ loading ? '提交中...' : (recoveryBlocked ? '邮件找回暂不可用' : '获取重置链接') }}
        </button>
        <p v-if="recoveryBlocked" class="recovery-alt">
          <a href="#" @click.prevent="goRegisterInstead">注册新账号继续创作（送 30 点）</a>
          ·
          <a href="#" @click.prevent="browseCases('recovery_blocked')">先看看案例</a>
        </p>
      </form>

      <!-- 重置密码 -->
      <form v-else-if="showReset" @submit.prevent="handleReset">
        <input v-model="resetToken" type="text" class="input" placeholder="重置令牌" required />
        <input v-model="form.password" type="password" class="input" placeholder="新密码（≥8位）" required />
        <input v-model="form.confirmPassword" type="password" class="input" placeholder="确认新密码" required />
        <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? '重置中...' : '重置密码' }}</button>
      </form>

      <!-- 登录表单 -->
      <form v-else @submit.prevent="handleLogin">
        <input 
          v-model="form.username" 
          type="text" 
          class="input" 
          placeholder="用户名"
          required
        />
        <input 
          v-model="form.password" 
          type="password" 
          class="input" 
          placeholder="密码"
          required
        />
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      
      <p v-if="error" class="error" :class="{ show: error }">{{ error }}</p>
      <p v-if="success" class="success" :class="{ show: success }">{{ success }}</p>
      
      <div class="footer" v-if="!showForgot && !showReset">
        <a href="#" @click.prevent="toggleMode">
          {{ showRegister ? '已有账号？登录' : '没有账号？注册' }}
        </a>
        <span class="divider">|</span>
        <a href="#" @click.prevent="openForgot">忘记密码</a>
        <span class="divider">|</span>
        <a href="#" @click.prevent="browseCases('footer')">先看看案例</a>
      </div>
      <div class="footer" v-else>
        <a href="#" @click.prevent="closeForgot">返回登录</a>
      </div>

      <div class="social-login" v-if="!showForgot && !showReset">
        <p>快捷登录</p>
        <div class="social-icons">
          <button type="button" class="social-icon" @click="onWechatLogin" :title="oauth.wechat ? '微信登录' : '微信登录即将上线'">
            <img :src="images.ui.wechat" alt="微信" width="28" height="28" />
          </button>
          <button type="button" class="social-icon" disabled title="QQ 登录即将上线">
            <img :src="images.ui.qq" alt="QQ" width="28" height="28" />
          </button>
        </div>
        <p v-if="!oauth.wechat" class="social-hint">微信登录即将上线，请先使用邮箱注册</p>
      </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authApi } from '../api'
import { IMAGES } from '../assets/images'
import { trackEvent } from '../utils/analytics'
import { findLatestResumeProgress } from '../utils/caseProgress'

const router = useRouter()
const route = useRoute()
const logo = IMAGES.logo
const illustration = IMAGES.loginIllustration
const images = IMAGES
const loading = ref(false)
const error = ref('')
const success = ref('')
const showRegister = ref(false)
const showForgot = ref(false)
const showReset = ref(false)
const resetToken = ref('')
const oauth = ref({ wechat: false, qq: false })
/** SMTP / 令牌回显能力：来自公开 /health/config，不含密钥 */
const recoveryHint = ref('')
const recoveryBlocked = ref(false)

async function refreshRecoveryStatus() {
  recoveryHint.value = ''
  recoveryBlocked.value = false
  try {
    const cfg = await fetch('/health/config').then((r) => r.json()).catch(() => null)
    if (!cfg) return
    const smtpOk = !!cfg?.smtp?.configured
    const inlineOk = !!cfg?.expose_reset_token
    if (smtpOk) {
      recoveryHint.value = '将向注册邮箱发送重置链接（1 小时内有效）。'
      return
    }
    if (inlineOk) {
      recoveryHint.value = '邮件服务未配置：匹配成功后将在本页直接进入重置（令牌不经邮箱）。'
      return
    }
    recoveryBlocked.value = true
    recoveryHint.value =
      '邮件服务暂未开通，暂时无法发送重置邮件。可注册新账号继续创作，或联系客服协助找回。'
  } catch {
    /* 配置不可用时仍允许提交，由接口 delivery 字段兜底 */
  }
}

function goRegisterInstead() {
  trackEvent('forgot_register_fallback', { category: 'auth', label: 'smtp_unavailable' })
  showForgot.value = false
  showRegister.value = true
  error.value = ''
  success.value = ''
}

/** 登录页「先看看案例」→ 广场，避免回首页弱化阅读意图 */
function browseCases(label = 'footer') {
  trackEvent('login_browse_cases', { category: 'funnel', label })
  router.push('/trending')
}

function closeForgot() {
  showForgot.value = false
  showReset.value = false
  recoveryHint.value = ''
  recoveryBlocked.value = false
  error.value = ''
  success.value = ''
}

/** 解析 redirect 深链：试用书名 / 案例风格 / 充值套餐 / 创作台 */
function parseRedirectIntent(redirect) {
  if (typeof redirect !== 'string' || !redirect.startsWith('/') || redirect.startsWith('//')) {
    return null
  }
  try {
    const u = new URL(redirect, 'https://lyread.cn')
    const pkg = u.searchParams.get('pkg')
    const title = (u.searchParams.get('generatedTitle') || '').trim()
    const type = (u.searchParams.get('type') || '').trim()
    const prompt = (u.searchParams.get('prompt') || '').trim()
    const mode = (u.searchParams.get('mode') || '').trim()
    if (u.pathname.startsWith('/pricing') && pkg) {
      return {
        kind: 'pricing',
        title: '注册后继续充值',
        detail: `套餐意图已保留（${pkg}）。注册送 30 点，回到价格页将自动续下单。`,
      }
    }
    if (u.pathname.startsWith('/story')) {
      const g = (
        u.searchParams.get('genreName')
        || u.searchParams.get('genreCustom')
        || u.searchParams.get('type')
        || ''
      ).trim()
      const p = (u.searchParams.get('prompt') || '').trim()
      const genreBit = g ? `题材「${g.slice(0, 24)}」已保留` : '注册后生成短故事'
      const promptBit = p
        ? `灵感已带回：${p.slice(0, 48)}${p.length > 48 ? '…' : ''} · 注册送 30 点`
        : '注册送 30 点，约可生成 2 篇短篇'
      return {
        kind: 'story',
        title: genreBit,
        detail: promptBit,
      }
    }
    if (title) {
      const genreBit = type ? ` · 题材 ${type}` : ''
      return {
        kind: 'trial',
        title: `书名「${title}」将带入创作台`,
        detail: `注册送 30 点，约可续写 3 章${genreBit}`,
      }
    }
    const caseMatch = prompt.match(/参考《(.+?)》/)
    if (caseMatch) {
      return {
        kind: 'case',
        title: `按《${caseMatch[1]}》同风格开写`,
        detail: '注册送 30 点，直达创作台向导',
      }
    }
    if (u.pathname.startsWith('/workspace')) {
      return {
        kind: 'workspace',
        title: mode === 'new' ? '注册后打开新建向导' : '注册后进入创作台',
        detail: '注册送 30 点，失败全额返还',
      }
    }
    if (/^\/(case|ep)\/\d+/.test(u.pathname)) {
      return {
        kind: 'case_read',
        title: '登录后继续阅读',
        detail: '注册送 30 点，读完可按同风格开写',
      }
    }
    if (u.pathname.startsWith('/trending')) {
      return {
        kind: 'trending',
        title: '登录后继续看案例',
        detail: '注册送 30 点，读完可按同风格开写',
      }
    }
    if (u.pathname.startsWith('/wallet')) {
      return {
        kind: 'wallet',
        title: '登录后查看点数',
        detail: '注册送 30 点，每日还可领 5 点免费额度',
      }
    }
    if (u.pathname.startsWith('/pricing') && !pkg) {
      return {
        kind: 'pricing',
        title: '注册后查看充值套餐',
        detail: '注册送 30 点，再到价格页续充',
      }
    }
    return null
  } catch {
    return null
  }
}

const intentBanner = computed(() => {
  const raw = route.query.redirect
  return parseRedirectIntent(typeof raw === 'string' ? raw : null)
})

const resumeOffer = ref(null)

function refreshResumeOffer() {
  const hit = findLatestResumeProgress()
  if (!hit) {
    resumeOffer.value = null
    return
  }
  resumeOffer.value = {
    id: hit.id,
    title: hit.title,
    category: hit.category || '',
    pct: Math.round(hit.ratio * 100),
  }
}

const registerCtaLabel = computed(() => {
  const kind = intentBanner.value?.kind
  if (kind === 'pricing') return '注册并继续充值（送 30 点）'
  if (kind === 'trial' || kind === 'case') return '注册并开写（送 30 点）'
  if (kind === 'story') return '注册并生成短篇（送 30 点）'
  if (kind === 'workspace') return '注册领 30 点开写'
  if (kind === 'case_read' || kind === 'trending') return '注册领 30 点继续读'
  if (kind === 'wallet') return '注册领 30 点看余额'
  return '注册领 30 点'
})

const onWechatLogin = async () => {
  if (oauth.value.wechat) {
    authApi.wechatLogin()
    return
  }
  error.value = '微信登录即将上线，请先使用邮箱注册/登录'
}

const form = reactive({
  username: '',
  password: '',
  email: '',
  confirmPassword: ''
})

const toggleMode = () => {
  showRegister.value = !showRegister.value
  showForgot.value = false
  showReset.value = false
  error.value = ''
  success.value = ''
  recoveryHint.value = ''
  recoveryBlocked.value = false
}

const openForgot = () => {
  showForgot.value = true
  showRegister.value = false
  showReset.value = false
  error.value = ''
  success.value = ''
  trackEvent('forgot_open', { category: 'auth', label: 'login_footer' })
  refreshRecoveryStatus()
}

const handleForgot = async () => {
  if (recoveryBlocked.value) {
    error.value = '邮件找回暂不可用，请注册新账号或联系客服'
    trackEvent('forgot_blocked', { category: 'auth', label: 'smtp_unavailable' })
    return
  }
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const res = await authApi.forgot(form.username, form.email)
    const delivery = res?.delivery || (res?.token ? 'inline' : 'opaque')
    trackEvent('forgot_result', { category: 'auth', label: delivery })
    if (delivery === 'inline' && res?.token) {
      resetToken.value = res.token
      showForgot.value = false
      showReset.value = true
      success.value = res.message || '请设置新密码'
    } else if (delivery === 'unavailable') {
      recoveryBlocked.value = true
      recoveryHint.value = res.message || recoveryHint.value
      error.value = res.message || '邮件服务暂未开通，暂时无法发送重置邮件'
      success.value = ''
    } else if (delivery === 'email') {
      success.value = res.message || '重置链接已发送至您的邮箱'
    } else {
      success.value = res?.message || '若账号匹配将收到重置指引'
    }
  } catch (e) {
    error.value = '请求失败'
    trackEvent('forgot_result', { category: 'auth', label: 'error' })
  } finally { loading.value = false }
}

const handleReset = async () => {
  if (form.password !== form.confirmPassword) { error.value = '两次密码不一致'; return }
  if (form.password.length < 8) { error.value = '密码至少8位'; return }
  loading.value = true
  try {
    const res = await authApi.reset(resetToken.value, form.password)
    if (res?.success) {
      success.value = '密码已重置，请登录'
      showReset.value = false
    } else error.value = res?.detail || '重置失败'
  } finally { loading.value = false }
}

onMounted(async () => {
  if (route.query.reset) {
    resetToken.value = route.query.reset
    showReset.value = true
  }
  if (route.query.mode === 'register') {
    showRegister.value = true
  }
  refreshResumeOffer()
  if (intentBanner.value) {
    trackEvent('login_intent_resume', {
      category: 'funnel',
      label: intentBanner.value.kind,
    })
  } else if (resumeOffer.value) {
    trackEvent('login_resume_offer', {
      category: 'engagement',
      label: resumeOffer.value.title || '',
      value: Number(resumeOffer.value.id) || 0,
    })
  } else {
    trackEvent('login_cold_welcome', {
      category: 'funnel',
      label: showRegister.value ? 'register' : 'login',
    })
  }
  try {
    const res = await authApi.oauthStatus()
    if (res?.success) oauth.value = { wechat: !!res.wechat, qq: !!res.qq }
  } catch { /* ignore */ }
})

function safeRedirectPath() {
  const raw = route.query.redirect
  if (typeof raw === 'string' && raw.startsWith('/') && !raw.startsWith('//')) {
    return raw
  }
  return null
}

function registerSuccessMessage(redirect) {
  if (!redirect) return '注册成功，已到账 30 点，正在进入创作台...'
  if (redirect.startsWith('/pricing')) return '注册成功，已到账 30 点，正在回到充值页…'
  if (redirect.startsWith('/story')) {
    if (/[?&](prompt|genreId|genreCustom|genreName)=/.test(redirect)) {
      return '注册成功，已到账 30 点，正在带回短故事灵感…'
    }
    return '注册成功，已到账 30 点，正在打开短故事…'
  }
  if (redirect.includes('generatedTitle=') || /prompt=.*参考/.test(redirect)) {
    return '注册成功，已到账 30 点，正在带入你的创作意图…'
  }
  if (redirect.startsWith('/workspace')) return '注册成功，已到账 30 点，正在进入创作台...'
  if (/^\/(case|ep)\/\d+/.test(redirect) || redirect.startsWith('/trending')) {
    return '注册成功，已到账 30 点，正在回到阅读…'
  }
  if (redirect.startsWith('/wallet')) return '注册成功，已到账 30 点，正在打开点数页…'
  return '注册成功，已到账 30 点，正在跳转…'
}

function afterAuth(isRegister = false) {
  const redirect = safeRedirectPath()
  if (redirect) {
    router.push(redirect)
    return
  }
  if (isRegister) {
    router.push('/workspace?welcome=1')
    return
  }
  // 登录无深链时：若有未读完案例进度，轻量承接「继续读」
  refreshResumeOffer()
  const offer = resumeOffer.value
  if (offer?.id != null) {
    trackEvent('login_resume_redirect', {
      category: 'engagement',
      label: offer.title || '',
      value: Number(offer.id) || 0,
    })
    success.value = `登录成功，继续读《${offer.title}》…`
    router.push(`/ep/${offer.id}`)
    return
  }
  router.push('/workspace')
}

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  success.value = '' // 清除成功消息

  try {
    // authApi 基于 fetch，出错时返回 { detail } 或 { error }，不会 throw
    const res = await authApi.login(form.username, form.password)
    if (!res || !res.token) {
      error.value = (res && (res.detail || res.error)) || '用户名或密码错误'
      return
    }
    localStorage.setItem('token', res.token)
    localStorage.setItem('user', JSON.stringify(res.user || {}))
    trackEvent('login_success', { category: 'auth', label: 'password' })
    afterAuth(false)
  } catch (err) {
    error.value = '登录失败，请稍后再试'
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (form.password !== form.confirmPassword) {
    error.value = '两次密码输入不一致'
    return
  }
  if (form.password.length < 8) {
    error.value = '密码长度至少8位'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const res = await authApi.register(form.username, form.password, form.email)
    if (!res || (!res.success && !res.token)) {
      error.value = (res && (res.detail || res.error)) || '注册失败'
      return
    }
    // 后端注册成功即返回 token，直接登录进入
    if (res.token) {
      localStorage.setItem('token', res.token)
      localStorage.setItem('user', JSON.stringify(res.user || {}))
      trackEvent('register_success', { category: 'auth', label: 'auto_login' })
      {
        const redirect = safeRedirectPath()
        success.value = registerSuccessMessage(redirect)
      }
      afterAuth(true)
      return
    }
    success.value = '注册成功，请登录'
    showRegister.value = false
    form.password = ''
    form.confirmPassword = ''
  } catch (err) {
    error.value = '注册失败，请稍后再试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 引入全局CSS变量 */
:root {
  --lyread-bg-light: #f1f6fa;
  --lyread-primary-blue-start: #4da1ff;
  --lyread-primary-blue-end: #2563eb;
  --lyread-text-dark: #1e2a3a;
  --lyread-text-secondary: #5a6a7a;
  --lyread-card-bg: #ffffff;
  --lyread-shadow-medium: rgba(0,0,0,0.08);
  --lyread-shadow-strong: rgba(0,0,0,0.15);
}

.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, #eef5ff 0%, #f6f9ff 100%);
  font-family: 'PingFang SC', 'Helvetica Neue', Helvetica, 'Microsoft YaHei', Arial, sans-serif;
}

.login-layout {
  display: flex;
  align-items: stretch;
  gap: 0;
  max-width: 920px;
  width: 100%;
  background: rgba(255, 255, 255, 0.55);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 16px 48px rgba(37, 99, 235, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.login-visual {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 32px;
  background: linear-gradient(160deg, #eef5ff 0%, #dbeafe 100%);
  border-right: 1px solid rgba(218, 230, 245, 0.8);
}

.login-illustration {
  width: 100%;
  max-width: 320px;
  height: auto;
  object-fit: contain;
  margin-bottom: 16px;
}

.visual-caption {
  font-size: 15px;
  color: #5a6a7a;
  font-weight: 500;
}

.login-card {
  width: 400px;
  flex-shrink: 0;
  padding: 45px;
  background: rgba(255, 255, 255, 0.95);
  text-align: center;
  position: relative;
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 12px;
}

.logo-img {
  display: block;
  border-radius: 12px;
  object-fit: cover;
}

.logo-text {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--lyread-primary-blue-start), var(--lyread-primary-blue-end));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.login-card .subtitle {
  color: var(--lyread-text-secondary);
  font-size: 15px;
  margin-bottom: 40px;
}

.intent-banner {
  margin: -20px 0 18px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  text-align: left;
}
.intent-banner strong {
  display: block;
  font-size: 14px;
  margin-bottom: 4px;
  line-height: 1.4;
}
.intent-banner p {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: #047857;
}
.intent-banner.welcome-cold {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1e3a8a;
}
.intent-banner.welcome-cold p {
  color: #1d4ed8;
}
.intent-banner.welcome-cold.soft {
  background: #f8fafc;
  border-color: #e2e8f0;
  color: #334155;
}
.intent-banner.welcome-cold.soft p {
  color: #64748b;
}

.recovery-hint {
  margin: -12px 0 14px;
  padding: 10px 12px;
  border-radius: 10px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  color: #9a3412;
  font-size: 12px;
  line-height: 1.55;
  text-align: left;
}
.recovery-alt {
  margin: 12px 0 0;
  font-size: 13px;
  color: #5a6a7a;
  line-height: 1.5;
}
.recovery-alt a {
  color: #2563eb;
  text-decoration: none;
}
.recovery-alt a:hover {
  text-decoration: underline;
}

.resume-banner {
  margin: -20px 0 18px;
  padding: 12px 14px;
  border-radius: 12px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1e3a8a;
  text-align: left;
}
.resume-banner strong {
  display: block;
  font-size: 14px;
  margin-bottom: 4px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.resume-banner p {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: #2563eb;
}

.login-card form {
  display: flex;
  flex-direction: column;
  gap: 18px; /* 增大表单元素间距 */
}

.input {
  width: 100%;
  padding: 15px 18px; /* 增大输入框高度 */
  background: #f8fbfd; /* 浅色背景 */
  border: 1px solid #e0e6ef;
  border-radius: 12px; /* 更圆润的输入框 */
  font-size: 15px;
  color: var(--lyread-text-dark);
  box-sizing: border-box;
  transition: all 0.3s ease;
}

.input:focus {
  outline: none;
  border-color: var(--lyread-primary-blue-start);
  box-shadow: 0 0 0 4px rgba(77, 161, 255, 0.15); /* 更强的焦点阴影 */
}

.input::placeholder {
  color: #aebecd; /* 浅灰色占位符 */
}

.btn-primary {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, var(--lyread-primary-blue-start), var(--lyread-primary-blue-end));
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 48px; /* 增加触摸目标 */
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(37, 99, 235, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.error, .success {
  font-size: 14px;
  margin-top: 20px;
  padding: 8px 15px;
  border-radius: 8px;
  font-weight: 500;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.error.show, .success.show {
  opacity: 1;
  transform: translateY(0);
}
.error {
  color: #e53e3e; /* 红色 */
  background: #fff5f5;
  border: 1px solid #fed7d7;
}
.success {
  color: #38a169; /* 绿色 */
  background: #f0fff4;
  border: 1px solid #c6f6d5;
}


.footer {
  margin-top: 30px;
  font-size: 15px;
  color: var(--lyread-text-secondary);
  display: flex;
  justify-content: center;
  align-items: center;
}

.footer a {
  color: var(--lyread-primary-blue-start);
  text-decoration: none;
  font-weight: 500;
  padding: 5px 0; /* 增大点击区域 */
}

.footer a:hover {
  text-decoration: underline;
}

.divider {
  margin: 0 15px;
  color: #d1d8e6;
}

/* 第三方登录 */
.social-login {
  margin-top: 30px;
  border-top: 1px solid #e0e6ef;
  padding-top: 25px;
}
.social-login p {
  color: var(--lyread-text-secondary);
  font-size: 14px;
  margin-bottom: 20px;
}
.social-hint {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 12px;
  margin-bottom: 0;
}
.social-icons {
  display: flex;
  justify-content: center;
  gap: 20px;
}
.social-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #f0f4f9;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  min-height: 44px;
  min-width: 44px;
  border: none;
  padding: 0;
}
.social-icon:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.social-icon:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  background: var(--lyread-primary-blue-start);
  color: white;
}

/* 移动端适配 */
@media (max-width: 860px) {
  .login-layout { flex-direction: column; max-width: 400px; }
  .login-visual { display: none; }
  .login-card { width: 100%; padding: 30px 25px; border-radius: 0; }
}

@media (max-width: 480px) {
  .login-page { padding: 16px; }
  .login-layout { border-radius: 16px; }
  .login-card { padding: 30px 25px; }
  .logo-text {
    font-size: 26px;
  }
  .login-card .subtitle {
    margin-bottom: 30px;
  }
  .login-card form {
    gap: 15px;
  }
  .input {
    padding: 13px 16px;
    font-size: 14px;
  }
  .btn-primary {
    padding: 13px;
    font-size: 15px;
  }
  .footer, .social-login p {
    font-size: 13px;
  }
  .social-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}
</style>