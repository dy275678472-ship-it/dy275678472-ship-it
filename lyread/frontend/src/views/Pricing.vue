<template>
  <div class="pricing-page">
    <img :src="images.pricingHero" alt="" class="pricing-hero-banner" aria-hidden="true" />
    <header class="page-hero">
      <img :src="images.pricing.gem" alt="点数计费图标" class="page-hero-icon" width="44" height="44" />
      <h1>AI 写小说价格 · 按章约 1 元</h1>
      <p>无订阅、无终身无限套餐。生成前显示预计消耗，失败自动全额返还。</p>
      <p v-if="firstRechargeEligible" class="first-recharge-banner">🎁 首充加赠 <strong>20%</strong> 点数（限时活动）</p>
    </header>

    <section class="highlights" v-if="info">
      <div class="highlight-card">
        <img :src="images.pricing.gift" alt="注册赠送点数" class="hl-icon-img" width="40" height="40" />
        <div>
          <strong>新用户注册送 {{ info.signup_bonus }} 点</strong>
          <p>足够体验书名、大纲与章节生成</p>
        </div>
      </div>
      <div class="highlight-card">
        <img :src="images.pricing.daily" alt="每日免费点数" class="hl-icon-img" width="40" height="40" />
        <div>
          <strong>每日免费 {{ info.daily_free }} 点</strong>
          <p>登录领取，当日有效，不累计</p>
        </div>
      </div>
      <div class="highlight-card">
        <img :src="images.pricing.gem" alt="充值套餐" class="hl-icon-img" width="40" height="40" />
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
      <p v-if="!isLoggedIn" class="guest-pricing-hint">
        游客可先
        <router-link :to="{ path: '/login', query: { mode: 'register', redirect: '/pricing' } }" @click="trackEvent('pricing_guest_register', { category: 'funnel', label: 'packages_hint' })">免费注册领 30 点</router-link>
        ，再选择套餐充值。
      </p>
      <p v-if="highlightPkgId && resumeHint" class="pkg-resume-hint">{{ resumeHint }}</p>
      <div class="pkg-grid">
        <div
          v-for="pkg in packages"
          :key="pkg.id"
          class="pkg-card"
          :class="{ popular: pkg.popular, intent: highlightPkgId === pkg.id }"
          :id="`pkg-${pkg.id}`"
        >
          <div v-if="pkg.popular" class="badge">推荐</div>
          <h3>{{ pkg.name }}</h3>
          <div class="pkg-price">¥{{ pkg.price }}</div>
          <div class="pkg-credits">{{ pkg.credits }} 点</div>
          <p class="pkg-desc">{{ pkg.desc }}</p>
          <button class="btn-buy" type="button" @click="buy(pkg)">
            {{ isLoggedIn ? '立即充值' : '注册后充值（送 30 点）' }}
          </button>
        </div>
      </div>
      <p class="pay-note pay-error" v-if="payError">{{ payError }}</p>
      <p class="pay-note" v-if="sandboxMode">当前为<strong>沙箱充值模式</strong>：点击充值后确认即可模拟到账。配置支付宝商户密钥后将跳转真实支付。</p>
      <p class="pay-note" v-else-if="alipayReady">支持支付宝扫码/网页支付，支付成功后点数自动到账。</p>
      <p class="pay-note" v-else>支付宝参数配置中。可先使用注册赠送与每日免费额度，或联系管理员开通沙箱测试充值。</p>
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
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { creditsApi, ordersApi } from '../api'
import { IMAGES } from '../assets/images'
import { trackEvent } from '../utils/analytics'

const router = useRouter()
const route = useRoute()
const info = ref(null)
const sandboxMode = ref(false)
const alipayReady = ref(false)
const payError = ref('')
const firstRechargeEligible = ref(false)
const firstRechargeBonusPercent = ref(20)
const highlightPkgId = ref('')
const resumeHint = ref('')
const images = IMAGES

const VALID_PKG_IDS = new Set(['s', 'm', 'l'])

function pricingRedirectFor(pkgId) {
  return `/pricing?pkg=${encodeURIComponent(pkgId)}`
}

const LABELS = {
  title: ['生成 5 个书名', '含黄金钩子简介'],
  outline: ['生成完整大纲', '总纲 + 分卷结构'],
  chapters: ['生成 10 章章纲', '批量章纲规划'],
  chapter: ['生成一章正文', '约 2000 字'],
  continue: ['章节续写', '承接上文继续写'],
  consistency: ['一致性检查', '人物/伏笔冲突检测'],
  short_story: ['短故事一键生成', '约 3000 字完整短篇'],
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
  { q: '可以先免费试用吗？', a: '可以。首页支持游客免费生成书名；注册后再领 30 点 + 每日 5 点，约可续写 3 章。' },
  { q: '首充加赠怎么算？', a: '首次充值任意套餐，额外赠送套餐点数的 20%。例如体验包 100 点，首充实得 120 点。' },
]

const isLoggedIn = computed(() => !!localStorage.getItem('token'))

onMounted(async () => {
  trackEvent('pricing_view', { category: 'funnel', label: 'page_load' })
  try {
    const [prices, pkgs, bal] = await Promise.all([
      creditsApi.prices(),
      ordersApi.packages().catch(() => null),
      isLoggedIn.value ? creditsApi.balance().catch(() => null) : Promise.resolve(null),
    ])
    info.value = prices
    if (prices?.first_recharge_bonus_percent) {
      firstRechargeBonusPercent.value = prices.first_recharge_bonus_percent
    }
    if (bal?.first_recharge_eligible) firstRechargeEligible.value = true
    if (pkgs) {
      alipayReady.value = !!pkgs.alipay_ready
      sandboxMode.value = pkgs.payment_mode === 'sandbox'
      if (pkgs.first_recharge_bonus_percent) {
        firstRechargeBonusPercent.value = pkgs.first_recharge_bonus_percent
      }
    }
  } catch (e) { /* 使用默认展示 */ }

  // 游客点套餐 → 注册回流：保留 pkg 意图并自动续充
  const rawPkg = typeof route.query.pkg === 'string' ? route.query.pkg.trim() : ''
  if (VALID_PKG_IDS.has(rawPkg)) {
    highlightPkgId.value = rawPkg
    const target = packages.find((p) => p.id === rawPkg)
    if (target) {
      resumeHint.value = isLoggedIn.value
        ? `已保留你选择的「${target.name}」，正在继续充值…`
        : `已记住「${target.name}」：注册后将自动回到本套餐`
    }
    if (route.query.pkg != null) {
      router.replace({ path: '/pricing' })
    }
    await nextTick()
    document.getElementById(`pkg-${rawPkg}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    if (isLoggedIn.value && target) {
      trackEvent('pricing_pkg_resume', { category: 'funnel', label: rawPkg, value: target.price })
      await buy(target)
    }
  }
})

async function buy(pkg) {
  payError.value = ''
  if (!isLoggedIn.value) {
    trackEvent('pricing_buy_click', { category: 'funnel', label: 'redirect_login', value: pkg.price })
    router.push({
      path: '/login',
      query: { mode: 'register', redirect: pricingRedirectFor(pkg.id) },
    })
    return
  }
  trackEvent('pricing_buy_click', { category: 'funnel', label: pkg.id, value: pkg.price })
  const key = `pkg-${pkg.id}-${Date.now()}`
  const res = await ordersApi.create(pkg.id, key)
  if (!res?.success) {
    payError.value = res?.detail || '创建订单失败，请稍后再试'
    return
  }
  if (res.sandbox || !res.alipay_ready) {
    const bonusHint = firstRechargeEligible.value ? `（首充加赠 ${Math.floor(pkg.credits * firstRechargeBonusPercent.value / 100)} 点）` : ''
    const ok = confirm(`沙箱模式：模拟支付 ¥${pkg.price} 获得 ${pkg.credits} 点${bonusHint}？`)
    if (!ok) {
      resumeHint.value = `已选中「${pkg.name}」，点击按钮即可继续充值`
      return
    }
    const paid = await ordersApi.sandboxConfirm(res.out_trade_no)
    if (paid?.success) {
      trackEvent('recharge_complete', { category: 'funnel', label: pkg.id, value: pkg.price })
      window.dispatchEvent(new Event('credits-changed'))
      payError.value = ''
      firstRechargeEligible.value = false
      highlightPkgId.value = ''
      resumeHint.value = ''
      alert(paid?.message || '充值完成，点数已到账')
    } else {
      payError.value = paid?.detail || '沙箱充值失败'
    }
    return
  }
  if (res.pay_url) {
    window.location.href = res.pay_url
    return
  }
  payError.value = '支付宝下单失败。请确认商户密钥已配置，或联系管理员开启沙箱测试充值。'
}
</script>

<style scoped>
.pricing-page { max-width: 960px; margin: 0 auto; padding: 32px 20px 80px; }
.pricing-hero-banner { width: 100%; height: auto; border-radius: 16px; margin-bottom: 28px; display: block; object-fit: cover; max-height: 180px; }
.page-hero { text-align: center; margin-bottom: 40px; }
.page-hero-icon { display: block; margin: 0 auto 12px; }
.page-hero h1 { font-size: 32px; color: #1e2a3a; margin-bottom: 12px; }
.page-hero p { color: #5a6a7a; font-size: 16px; }
.first-recharge-banner {
  margin-top: 14px; display: inline-block; padding: 8px 16px; border-radius: 999px;
  background: linear-gradient(135deg, #fff7e6, #ffe9c7); color: #ad6800; font-size: 14px;
}

.highlights { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 48px; }
.highlight-card {
  display: flex; gap: 14px; align-items: flex-start;
  background: #fff; border-radius: 14px; padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #e8f0fa;
}
.hl-icon-img { flex-shrink: 0; object-fit: contain; }
.highlight-card strong { display: block; color: #1e2a3a; margin-bottom: 4px; }
.highlight-card p { font-size: 13px; color: #5a6a7a; }

.price-table { margin-bottom: 48px; }
.price-table h2, .packages h2, .faq h2 { font-size: 22px; margin-bottom: 20px; color: #1e2a3a; }
.guest-pricing-hint {
  margin: -8px 0 18px; color: #5a6a7a; font-size: 14px; text-align: center;
}
.guest-pricing-hint a { color: #2563eb; font-weight: 600; text-decoration: none; }
.guest-pricing-hint a:hover { text-decoration: underline; }
.table-wrap { background: #fff; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 14px 18px; text-align: left; border-bottom: 1px solid #f0f4f8; }
th { background: #f8fafc; font-size: 13px; color: #64748b; }
.pts { font-weight: 700; color: #2563eb; white-space: nowrap; }
.note { color: #94a3b8; font-size: 13px; }
.pay-error { color: #dc2626; background: #fef2f2; padding: 12px 16px; border-radius: 10px; border: 1px solid #fecaca; }

.pkg-resume-hint {
  margin: 0 0 14px; padding: 10px 14px; border-radius: 10px;
  background: #eff6ff; color: #1e40af; font-size: 14px; line-height: 1.5;
}
.pkg-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 16px; }
.pkg-card {
  position: relative; background: #fff; border-radius: 16px; padding: 28px 22px;
  text-align: center; border: 2px solid #e8f0fa; transition: transform 0.2s;
}
.pkg-card.popular { border-color: #4da1ff; box-shadow: 0 8px 24px rgba(77,161,255,0.15); }
.pkg-card.intent { border-color: #2563eb; box-shadow: 0 8px 28px rgba(37,99,235,0.18); }
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
