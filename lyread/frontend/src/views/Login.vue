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
      <p v-if="showRegister" class="bonus-hint">新用户注册即送 30 点创作额度</p>
      <p v-else-if="!showForgot && !showReset" class="bonus-hint muted">还没有账号？注册即可领取 30 点试用</p>
      
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
          {{ loading ? '注册中...' : '注册，送 30 点' }}
        </button>
      </form>

      <!-- 找回密码 -->
      <form v-else-if="showForgot" @submit.prevent="handleForgot">
        <p class="forgot-hint" v-if="smtpHint">{{ smtpHint }}</p>
        <input v-model="form.username" type="text" class="input" placeholder="用户名" required />
        <input v-model="form.email" type="email" class="input" placeholder="注册邮箱" required />
        <button type="submit" class="btn btn-primary" :disabled="loading">{{ loading ? '提交中...' : '获取重置链接' }}</button>
      </form>

      <!-- 重置密码 -->
      <form v-else-if="showReset" @submit.prevent="handleReset">
        <p class="forgot-hint" v-if="resetPathHint">{{ resetPathHint }}</p>
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
          {{ showRegister ? '已有账号？登录' : '没有账号？注册送 30 点' }}
        </a>
        <span class="divider">|</span>
        <a href="#" @click.prevent="showForgot = true">忘记密码</a>
        <span class="divider">|</span>
        <a href="#" @click.prevent="$router.push('/')">先看看</a>
      </div>
      <div class="footer" v-else>
        <a href="#" @click.prevent="showForgot = false; showReset = false">返回登录</a>
      </div>

      <div class="social-login" v-if="false && !showForgot && !showReset">
        <p>第三方登录（即将上线）</p>
        <div class="social-icons">
          <button type="button" class="social-icon" disabled title="微信登录即将上线">
            <img :src="images.ui.wechat" alt="微信" width="28" height="28" />
          </button>
          <button type="button" class="social-icon" disabled title="QQ 登录即将上线">
            <img :src="images.ui.qq" alt="QQ" width="28" height="28" />
          </button>
        </div>
      </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authApi } from '../api'
import { IMAGES } from '../assets/images'
import { trackEvent } from '../utils/analytics'

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
const smtpConfigured = ref(true)
const smtpHint = ref('')
const resetPathHint = ref('')

const form = reactive({
  username: '',
  password: '',
  email: '',
  confirmPassword: ''
})

const toggleMode = () => {
  const nextRegister = !showRegister.value
  showRegister.value = nextRegister
  showForgot.value = false
  showReset.value = false
  error.value = ''
  success.value = ''
  resetPathHint.value = ''
  if (nextRegister) {
    trackEvent('register_cta_click', { category: 'funnel', label: 'login_toggle' })
  }
}

const handleForgot = async () => {
  loading.value = true
  error.value = ''
  success.value = ''
  resetPathHint.value = ''
  try {
    const res = await authApi.forgot(form.username, form.email)
    if (res?.token) {
      resetToken.value = res.token
      showForgot.value = false
      showReset.value = true
      success.value = res.message || '请在本页设置新密码'
      resetPathHint.value = res.reset_path
        ? `邮件暂未开通时，请直接在下方填写新密码完成重置（或打开 ${res.reset_path}）。`
        : '邮件暂未开通时，重置令牌已填入下方，请直接设置新密码。'
    } else {
      success.value = res?.message || '若账号匹配将收到重置指引'
      if (!smtpConfigured.value) {
        success.value = res?.message || '邮件发送暂未开通。若账号匹配，请刷新后重试或联系客服协助重置。'
      }
    }
  } catch (e) {
    error.value = '请求失败'
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
  try {
    const cfg = await fetch('/health/config').then((r) => r.json()).catch(() => null)
    smtpConfigured.value = !!cfg?.smtp?.configured
    if (!smtpConfigured.value) {
      smtpHint.value = '当前邮件发送暂未开通：提交后若账号匹配，将在本页给出重置令牌，无需等邮件。'
    }
  } catch { /* 忽略配置探测失败 */ }
})

function safeRedirectPath() {
  const raw = route.query.redirect
  if (typeof raw === 'string' && raw.startsWith('/') && !raw.startsWith('//')) {
    return raw
  }
  return null
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
      success.value = '注册成功，已到账 30 点，正在进入创作台...'
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
  margin-bottom: 12px;
}
.bonus-hint {
  font-size: 13px;
  color: #1d4ed8;
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(147, 197, 253, 0.7);
  border-radius: 10px;
  padding: 8px 12px;
  margin: 0 0 28px;
  font-weight: 500;
}
.bonus-hint.muted {
  color: #5a6a7a;
  background: #f8fafc;
  border-color: #e8f0fa;
  font-weight: 400;
}
.forgot-hint {
  font-size: 13px;
  line-height: 1.55;
  color: #5a6a7a;
  background: #f8fafc;
  border: 1px solid #e8f0fa;
  border-radius: 10px;
  padding: 10px 12px;
  margin: 0 0 14px;
  text-align: left;
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