<template>
  <div class="login-page">
    <div class="login-card">
      <div class="brand">
        <span class="logo">🧠</span>
        <span class="logo-text">LyRead</span>
      </div>
      <p class="subtitle">AI小说创作引擎</p>
      
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
          {{ loading ? '注册中...' : '注册' }}
        </button>
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
      
      <div class="footer">
        <a href="#" @click.prevent="toggleMode">
          {{ showRegister ? '已有账号？登录' : '没有账号？注册' }}
        </a>
        <span class="divider">|</span>
        <a href="#" @click.prevent="$router.push('/')">先看看</a>
      </div>

      <!--
      <div class="social-login">
        <p>或使用第三方登录</p>
        <div class="social-icons">
          <div class="social-icon">💬</div>
          <div class="social-icon">QQ</div>
          <div class="social-icon">📱</div>
        </div>
      </div>
      -->
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')
const showRegister = ref(false)

const form = reactive({
  username: '',
  password: '',
  email: '',
  confirmPassword: ''
})

const toggleMode = () => {
  showRegister.value = !showRegister.value
  error.value = ''
  success.value = ''
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
    router.push('/')
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
      success.value = '注册成功，正在进入...'
      router.push('/')
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
  background: linear-gradient(135deg, #eef5ff 0%, #f6f9ff 100%); /* 微奢冰灰蓝渐变背景 */
  font-family: 'PingFang SC', 'Helvetica Neue', Helvetica, 'Microsoft YaHei', Arial, sans-serif;
}

.login-card {
  width: 400px; /* 稍微增大卡片宽度 */
  padding: 45px; /* 增加内边距 */
  background: rgba(255, 255, 255, 0.9); /* 毛玻璃效果的背景 */
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px; /* 更圆润的圆角 */
  text-align: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15); /* 更强的阴影 */
  backdrop-filter: blur(15px); /* 毛玻璃滤镜 */
  -webkit-backdrop-filter: blur(15px);
  position: relative;
  overflow: hidden;
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 12px;
}

.logo {
  font-size: 36px;
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
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  min-height: 44px; /* 确保触摸目标 */
  min-width: 44px;
}
.social-icon:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  background: var(--lyread-primary-blue-start);
  color: white;
}

/* 移动端适配 */
@media (max-width: 480px) {
  .login-card {
    width: 95%;
    padding: 30px 25px;
    border-radius: 16px;
  }
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