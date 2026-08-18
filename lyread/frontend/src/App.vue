<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">
          <img :src="logo" alt="LyRead" class="logo-img" width="32" height="32" />
          <span class="title">LyRead<span class="title-ai">AI</span></span>
        </router-link>
        <button class="mobile-menu-btn" @click="menuOpen = !menuOpen" :aria-label="menuOpen ? '关闭菜单' : '打开菜单'">
          <img :src="menuOpen ? uiIcons.close : uiIcons.menu" alt="" width="24" height="24" />
        </button>
      </div>
      <div class="nav-links" :class="{ open: menuOpen }">
        <router-link to="/" class="nav-link" @click="menuOpen = false">首页</router-link>
        <router-link :to="novelNavLink" class="nav-link" @click="menuOpen = false">长篇小说</router-link>
        <router-link to="/story" class="nav-link" @click="menuOpen = false">短故事</router-link>
        <router-link to="/trending" class="nav-link" @click="menuOpen = false">案例阅读</router-link>
        <router-link to="/pricing" class="nav-link" @click="menuOpen = false">价格</router-link>
        <template v-if="isLoggedIn">
          <router-link to="/workspace" class="nav-link nav-link-primary" @click="menuOpen = false">创作台</router-link>
          <router-link v-if="isAdmin" to="/admin" class="nav-link" @click="menuOpen = false">后台</router-link>
          <router-link to="/wallet" class="nav-credits" @click="menuOpen = false" title="我的点数">
            <img :src="pointIcon" alt="点数" class="credits-icon-img" width="14" height="14" />
            <span class="credits-num">{{ credits === null ? '—' : credits }}</span>
            <span class="credits-label">点</span>
          </router-link>
          <router-link to="/login" class="nav-link btn-logout" @click="logout">退出</router-link>
        </template>
        <router-link
          v-else
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          class="nav-link btn-login"
          @click="menuOpen = false"
        >登录 / 注册</router-link>
      </div>
    </nav>
    <router-view @credits-changed="fetchCredits" />
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <img :src="logo" alt="LyRead AI" width="20" height="20" />
          <span>LyRead AI · AI 写小说平台</span>
        </div>
        <nav class="footer-links">
          <router-link to="/faq">常见问题</router-link>
          <router-link to="/about">关于我们</router-link>
          <router-link to="/compare">工具对比</router-link>
          <router-link to="/guide">创作教程</router-link>
          <router-link to="/ep">作品索引</router-link>
          <router-link to="/pricing">价格</router-link>
          <router-link to="/trending">创作案例</router-link>
          <router-link
            v-if="!isLoggedIn"
            :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          >免费注册</router-link>
          <router-link to="/privacy">隐私政策</router-link>
          <router-link to="/terms">用户协议</router-link>
        </nav>
        <p class="footer-note">按章计费 · 失败全额返还 · 注册送 30 点</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { creditsApi } from './api'
import { IMAGES } from './assets/images'

export default {
  name: 'App',
  data() {
    return { menuOpen: false, credits: null, isAdmin: false, logo: IMAGES.logo, pointIcon: IMAGES.point, uiIcons: IMAGES.ui }
  },
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token')
    },
    /** 游客 register-first，避免先撞 /workspace 守卫再回跳 */
    novelNavLink() {
      if (this.isLoggedIn) return { path: '/workspace', query: { mode: 'new' } }
      return {
        path: '/login',
        query: { mode: 'register', redirect: '/workspace?mode=new' },
      }
    },
  },
  watch: {
    $route() {
      this.menuOpen = false
      if (this.isLoggedIn) this.fetchCredits()
    }
  },
  mounted() {
    if (this.isLoggedIn) { this.fetchCredits(); this.fetchMe() }
    window.addEventListener('credits-changed', this.fetchCredits)
  },
  beforeUnmount() {
    window.removeEventListener('credits-changed', this.fetchCredits)
  },
  methods: {
    async fetchMe() {
      try {
        const token = localStorage.getItem('token')
        if (!token) return
        const res = await fetch('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } })
        const d = await res.json()
        this.isAdmin = d?.role === 'admin'
      } catch (e) { /* ignore */ }
    },
    async fetchCredits() {
      if (!this.isLoggedIn) { this.credits = null; return }
      try {
        const d = await creditsApi.balance()
        if (d && d.success) this.credits = d.total
      } catch (e) { /* 忽略 */ }
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.menuOpen = false
      this.credits = null
      this.$router.push('/')
    }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: "PingFang SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, sans-serif;
  background: linear-gradient(180deg, #f1f6fa 0%, #f6f9ff 40%, #eef5ff 100%);
  color: #1e2a3a;
  min-height: 100vh;
}

#app { min-height: 100vh; display: flex; flex-direction: column; background: #f1f6fa; }
.site-footer {
  margin-top: auto; padding: 24px 20px; font-size: 13px; color: #94a3b8;
  border-top: 1px solid #e8f0fa; background: #fff;
}
.footer-inner { max-width: 1100px; margin: 0 auto; text-align: center; }
.footer-brand {
  display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 12px;
  font-weight: 600; color: #64748b;
}
.footer-links {
  display: flex; flex-wrap: wrap; justify-content: center; gap: 16px; margin-bottom: 10px;
}
.footer-links a { color: #64748b; text-decoration: none; font-weight: 500; }
.footer-links a:hover { color: #2563eb; }
.footer-note { font-size: 12px; color: #94a3b8; }

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  height: 62px;
  background: rgba(255, 255, 255, 0.72);
  -webkit-backdrop-filter: blur(20px);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(218, 230, 245, 0.6);
  box-shadow: 0 2px 14px rgba(77, 163, 255, 0.06);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand { display: flex; align-items: center; gap: 8px; }
.logo { font-size: 26px; }
.title { font-size: 20px; font-weight: 800; color: #2563eb; letter-spacing: 0.3px; }
.title-ai {
  background: linear-gradient(135deg, #4da1ff, #2563eb);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-left: 2px;
}

.nav-links { display: flex; align-items: center; gap: 6px; }

.nav-link {
  padding: 8px 15px;
  text-decoration: none;
  color: #5a6a7a;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}
.nav-link:hover { background: #eef4fb; color: #2563eb; }
.nav-link.router-link-active { color: #2563eb; background: #eaf2ff; }

.nav-link-primary,
.nav-link-primary.router-link-active {
  background: linear-gradient(135deg, #4da1ff, #2563eb);
  color: #fff;
}
.nav-link-primary:hover { color: #fff; opacity: 0.92; }

.nav-credits {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 999px;
  text-decoration: none;
  background: linear-gradient(135deg, #fff7e6, #ffe9c7);
  border: 1px solid #ffd591;
  color: #ad6800;
  font-weight: 700;
  font-size: 13px;
  transition: all 0.2s;
}
.nav-credits:hover { box-shadow: 0 3px 10px rgba(250, 173, 20, 0.25); transform: translateY(-1px); }
.credits-icon { color: #fa8c16; }
.credits-num { font-variant-numeric: tabular-nums; }
.credits-label { opacity: 0.7; font-weight: 500; }

.btn-login {
  background: linear-gradient(135deg, #4da1ff, #2563eb);
  color: #fff;
}
.btn-login:hover { color: #fff; opacity: 0.92; }

.btn-logout { color: #94a3b8; font-size: 13px; }
.btn-logout:hover { color: #ef4444; background: #fef2f2; }

.brand-link { display: flex; align-items: center; gap: 8px; text-decoration: none; }
.logo-img { display: block; border-radius: 8px; object-fit: cover; }
.credits-icon-img { display: block; flex-shrink: 0; }
.mobile-menu-btn { display: none; }

@media (max-width: 860px) {
  .navbar { height: 56px; padding: 0 14px; }
  .nav-brand { flex: 1; }
  .mobile-menu-btn {
    display: block; background: none; border: none;
    cursor: pointer; padding: 8px; line-height: 0;
  }
  .nav-links {
    display: none; position: absolute; top: 56px; left: 0; right: 0;
    background: #fff; flex-direction: column; align-items: stretch;
    padding: 12px; gap: 4px; box-shadow: 0 8px 20px rgba(0,0,0,0.1);
  }
  .nav-links.open { display: flex; }
  .nav-link, .nav-credits { padding: 12px 16px; text-align: center; justify-content: center; border-radius: 10px; }
}
</style>
