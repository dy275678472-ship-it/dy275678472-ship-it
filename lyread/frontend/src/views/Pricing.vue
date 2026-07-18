<template>
  <div class="pricing-page">
    <header class="page-hero">
      <h1>点数计费，用多少付多少</h1>
      <p>无订阅、无终身无限套餐。生成前显示预计消耗，失败自动全额返还。</p>
    </header>

    <section class="highlights" v-if="info">
      <div class="highlight-card">
        <span class="hl-icon">🎁</span>
        <div>
          <strong>新用户注册送 {{ info.signup_bonus }} 点</strong>
          <p>足够体验书名、大纲与章节生成</p>
        </div>
      </div>
      <div class="highlight-card">
        <span class="hl-icon">☀️</span>
        <div>
          <strong>每日免费 {{ info.daily_free }} 点</strong>
          <p>登录领取，当日有效，不累计</p>
        </div>
      </div>
      <div class="highlight-card">
        <span class="hl-icon">💎</span>
        <div>
          <strong>10 元 = 100 点</strong>
          <p>生成一章约 2000 字 ≈ 10 点（约 1 元）</p>
        </div>
      </div>
    </section>

    <section class="price-table">
      <h2>操作消耗参考</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>操作</th><th>点数</th><th>说明</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in priceRows" :key="row.key">
              <td>{{ row.label }}</td>
              <td class="pts">{{ row.points }} 点</td>
              <td class="note">{{ row.note }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="packages">
      <h2>充值套餐</h2>
      <div class="pkg-grid">
        <div v-for="pkg in packages" :key="pkg.id" class="pkg-card" :class="{ popular: pkg.popular }">
          <div v-if="pkg.popular" class="badge">推荐</div>
          <h3>{{ pkg.name }}</h3>
          <div class="pkg-price">¥{{ pkg.price }}</div>
          <div class="pkg-credits">{{ pkg.credits }} 点</div>
          <p class="pkg-desc">{{ pkg.desc }}</p>
          <button class="btn-buy" :disabled="!isLoggedIn" @click="buy(pkg)">
            {{ isLoggedIn ? '立即充值' : '登录后充值' }}
          </button>
        </div>
      </div>
      <p class="pay-note">支付宝支付即将上线。当前可先使用注册赠送与每日免费额度体验。</p>
    </section>

    <section class="faq">
      <h2>常见问题</h2>
      <details v-for="item in faqs" :key="item.q">
        <summary>{{ item.q }}</summary>
        <p>{{ item.a }}</p>
      </details>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { creditsApi, ordersApi } from '../api'

const router = useRouter()
const info = ref(null)

const LABELS = {
  title: ['生成 5 个书名', '含黄金钩子简介'],
  outline: ['生成完整大纲', '总纲 + 分卷结构'],
  chapters: ['生成 10 章章纲', '批量章纲规划'],
  chapter: ['生成一章正文', '约 2000 字'],
  continue: ['章节续写', '承接上文继续写'],
  consistency: ['一致性检查', '人物/伏笔冲突检测'],
}

const priceRows = computed(() => {
  if (!info.value) return []
  return Object.entries(info.value.prices || {}).map(([key, points]) => ({
    key,
    points,
    label: LABELS[key]?.[0] || key,
    note: LABELS[key]?.[1] || '',
  }))
})

const packages = [
  { id: 's', name: '体验包', price: 10, credits: 100, desc: '约可生成 10 章正文' },
  { id: 'm', name: '创作包', price: 30, credits: 350, desc: '多送 50 点，适合连载起步', popular: true },
  { id: 'l', name: '连载包', price: 98, credits: 1200, desc: '多送 200 点，长篇连载优选' },
]

const faqs = [
  { q: '点数会过期吗？', a: '充值点数长期有效。每日免费额度仅当日有效，次日重置为 5 点，不累计。' },
  { q: '生成失败会扣点吗？', a: '不会。任务失败会自动全额返还已冻结的点数。' },
  { q: '可以先免费试用吗？', a: '可以。首页支持匿名试用书名生成；注册后再领 30 点 + 每日 5 点。' },
]

const isLoggedIn = computed(() => !!localStorage.getItem('token'))

onMounted(async () => {
  try {
    info.value = await creditsApi.prices()
  } catch (e) { /* 使用默认展示 */ }
})

async function buy(pkg) {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }
  const key = `pkg-${pkg.id}-${Date.now()}`
  const res = await ordersApi.create(pkg.id, key)
  if (!res?.success) {
    alert(res?.detail || '创建订单失败')
    return
  }
  if (res.sandbox || !res.alipay_ready) {
    const ok = confirm(`沙箱模式：模拟支付 ¥${pkg.price} 获得 ${pkg.credits} 点？`)
    if (!ok) return
    const paid = await ordersApi.sandboxConfirm(res.out_trade_no)
    alert(paid?.message || paid?.detail || '充值完成')
    window.dispatchEvent(new Event('credits-changed'))
    return
  }
  if (res.pay_url) {
    window.location.href = res.pay_url
    return
  }
  alert('请完成支付宝支付（支付页面即将上线）')
}
</script>

<style scoped>
.pricing-page { max-width: 960px; margin: 0 auto; padding: 32px 20px 80px; }
.page-hero { text-align: center; margin-bottom: 40px; }
.page-hero h1 { font-size: 32px; color: #1e2a3a; margin-bottom: 12px; }
.page-hero p { color: #5a6a7a; font-size: 16px; }

.highlights { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 48px; }
.highlight-card {
  display: flex; gap: 14px; align-items: flex-start;
  background: #fff; border-radius: 14px; padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #e8f0fa;
}
.hl-icon { font-size: 28px; }
.highlight-card strong { display: block; color: #1e2a3a; margin-bottom: 4px; }
.highlight-card p { font-size: 13px; color: #5a6a7a; }

.price-table { margin-bottom: 48px; }
.price-table h2, .packages h2, .faq h2 { font-size: 22px; margin-bottom: 20px; color: #1e2a3a; }
.table-wrap { background: #fff; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 18px; text-align: left; border-bottom: 1px solid #f0f4f8; }
th { background: #f8fafc; font-size: 13px; color: #64748b; }
.pts { font-weight: 700; color: #2563eb; white-space: nowrap; }
.note { color: #94a3b8; font-size: 13px; }

.pkg-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 16px; }
.pkg-card {
  position: relative; background: #fff; border-radius: 16px; padding: 28px 22px;
  text-align: center; border: 2px solid #e8f0fa; transition: transform 0.2s;
}
.pkg-card.popular { border-color: #4da1ff; box-shadow: 0 8px 24px rgba(77,161,255,0.15); }
.badge {
  position: absolute; top: -10px; left: 50%; transform: translateX(-50%);
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff;
  font-size: 12px; padding: 4px 12px; border-radius: 999px;
}
.pkg-card h3 { font-size: 18px; margin-bottom: 12px; }
.pkg-price { font-size: 36px; font-weight: 800; color: #1e2a3a; }
.pkg-credits { font-size: 16px; color: #2563eb; font-weight: 600; margin: 8px 0; }
.pkg-desc { font-size: 13px; color: #94a3b8; margin-bottom: 20px; min-height: 36px; }
.btn-buy {
  width: 100%; padding: 12px; border: none; border-radius: 10px; cursor: pointer;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; font-weight: 600;
}
.btn-buy:disabled { opacity: 0.55; cursor: not-allowed; }
.pay-note { text-align: center; color: #94a3b8; font-size: 13px; margin-bottom: 48px; }

.faq details {
  background: #fff; border-radius: 12px; padding: 16px 20px; margin-bottom: 10px;
  border: 1px solid #e8f0fa;
}
.faq summary { cursor: pointer; font-weight: 600; color: #1e2a3a; }
.faq p { margin-top: 10px; color: #5a6a7a; font-size: 14px; line-height: 1.6; }

@media (max-width: 768px) {
  .highlights, .pkg-grid { grid-template-columns: 1fr; }
  .page-hero h1 { font-size: 26px; }
}
</style>
