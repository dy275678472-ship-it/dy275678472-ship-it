<template>
  <div class="wallet-page">
    <header class="wallet-hero">
      <img :src="images.point" alt="点数余额" class="wallet-hero-icon" width="48" height="48" />
      <div>
        <h1>我的点数</h1>
        <p>免费额度当日有效；充值点数长期有效；生成失败自动返还。</p>
      </div>
    </header>

    <section class="balance-cards" v-if="balance">
      <div class="bal-card total">
        <img :src="images.wallet.total" alt="可用总额" class="bal-icon" width="28" height="28" />
        <span class="bal-label">可用总额</span>
        <span class="bal-num">{{ balance.total }}</span>
        <span class="bal-unit">点</span>
      </div>
      <div class="bal-card">
        <img :src="images.wallet.free" alt="免费额度" class="bal-icon" width="24" height="24" />
        <span class="bal-label">免费额度</span>
        <span class="bal-num sub">{{ balance.free }}</span>
        <span class="bal-hint">今日有效</span>
      </div>
      <div class="bal-card">
        <img :src="images.wallet.paid" alt="充值点数" class="bal-icon" width="24" height="24" />
        <span class="bal-label">充值/赠送</span>
        <span class="bal-num sub">{{ balance.paid }}</span>
        <span class="bal-hint" v-if="balance.reserved">冻结 {{ balance.reserved }} 点</span>
      </div>
    </section>

    <section class="actions">
      <button class="btn-claim" :disabled="claiming || !!balance?.claimed_today" @click="claimDaily">
        <img :src="images.wallet.free" alt="每日免费" width="18" height="18" />
        {{ claiming ? '领取中...' : (balance?.claimed_today ? '今日已领取' : '领取今日免费 5 点') }}
      </button>
      <router-link to="/pricing" class="btn-recharge" @click="trackRecharge">
        <img :src="images.pricing.gem" alt="充值" width="18" height="18" />
        充值点数
      </router-link>
    </section>
    <p class="pay-hint" v-if="payHint">{{ payHint }}</p>
    <p v-if="claimMsg" class="claim-msg" :class="{ ok: claimOk }">{{ claimMsg }}</p>

    <section v-if="balance" class="next-steps" aria-label="下一步">
      <p v-if="justClaimed" class="next-hint ok">
        今日免费点已到账 · 失败不扣点，可直接去创作台开写
      </p>
      <p v-else-if="balance.claimed_today" class="next-hint">
        今日免费点已领完 · 明天再来；现在可去创作台用现有点数开写
      </p>
      <p v-else-if="(balance.total ?? 0) < 10" class="next-hint warn">
        可用点数偏低（{{ balance.total }} 点）· 先领每日免费，或充值后续写
      </p>
      <p v-else class="next-hint">
        点数就绪 · 去创作台开写第一章；生成失败自动返还
      </p>
      <div class="next-actions">
        <router-link
          to="/workspace?mode=new"
          class="btn-create"
          @click="trackEvent('wallet_create_click', { category: 'conversion', label: justClaimed ? 'after_claim' : 'wallet' })"
        >去创作台开写 →</router-link>
        <router-link
          v-if="(balance.total ?? 0) < 10 || balance.claimed_today"
          to="/pricing"
          class="btn-next-pricing"
          @click="trackRecharge"
        >查看充值套餐</router-link>
      </div>
    </section>

    <section class="transactions">
      <h2>消费记录</h2>
      <div v-if="loading" class="empty">加载中...</div>
      <EmptyState
        v-else-if="!txns.length"
        :image="images.emptyCreate"
        title="暂无消费记录"
        description="开始创作或领取每日免费点数后，记录会显示在这里"
        :image-width="140"
      />
      <ul v-else class="txn-list">
        <li v-for="(t, i) in txns" :key="i" class="txn-item">
          <img :src="txnIcon(t.type)" :alt="typeLabel(t.type)" class="txn-icon" width="32" height="32" />
          <div class="txn-left">
            <span class="txn-type">{{ typeLabel(t.type) }}</span>
            <span class="txn-note">{{ t.note || '—' }}</span>
          </div>
          <div class="txn-right">
            <span class="txn-amount" :class="{ plus: t.amount > 0 }">
              {{ t.amount > 0 ? '+' : '' }}{{ t.amount }}
            </span>
            <span class="txn-time">{{ formatTime(t.created_at) }}</span>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { creditsApi, ordersApi } from '../api'
import { IMAGES } from '../assets/images'
import EmptyState from '../components/EmptyState.vue'
import { trackEvent } from '../utils/analytics'

const images = IMAGES
const balance = ref(null)
const txns = ref([])
const loading = ref(true)
const claiming = ref(false)
const claimMsg = ref('')
const claimOk = ref(false)
const payHint = ref('')
const justClaimed = ref(false)

function trackRecharge() {
  trackEvent('wallet_recharge_click', { category: 'monetization', label: 'wallet' })
}

const TYPE_LABELS = {
  signup_bonus: '注册赠送',
  daily_grant: '每日免费',
  reserve: '预冻结',
  settle: '消费结算',
  refund: '失败返还',
  recharge: '充值到账',
}

function typeLabel(t) { return TYPE_LABELS[t] || t }

function txnIcon(type) {
  const map = {
    signup_bonus: images.txn.signup,
    daily_grant: images.txn.daily,
    recharge: images.txn.recharge,
    refund: images.txn.refund,
    settle: images.txn.spend,
    reserve: images.txn.reserve,
  }
  return map[type] || images.point
}

function formatTime(s) {
  if (!s) return ''
  return s.replace('T', ' ').slice(0, 16)
}

async function load() {
  loading.value = true
  try {
    const [bal, hist, pkgs] = await Promise.all([
      creditsApi.balance(),
      creditsApi.transactions(40),
      ordersApi.packages().catch(() => null),
    ])
    if (bal?.success) balance.value = bal
    if (hist?.success) txns.value = hist.transactions || []
    if (pkgs?.payment_mode === 'sandbox') {
      payHint.value = '充值页当前为体验沙箱：确认后模拟到账，点数可正常用于创作。'
    } else if (pkgs && !pkgs.alipay_ready) {
      payHint.value = '正式支付宝即将开通。可先领取每日免费点，或使用注册赠送额度继续创作。'
    } else {
      payHint.value = ''
    }
  } finally {
    loading.value = false
  }
}

async function claimDaily() {
  claiming.value = true
  claimMsg.value = ''
  trackEvent('wallet_claim_click', { category: 'monetization', label: 'daily_5' })
  try {
    const res = await creditsApi.dailyClaim()
    if (res?.success) {
      claimOk.value = !!res.claimed
      claimMsg.value = res.message || (res.claimed ? '领取成功' : '今日已领取')
      justClaimed.value = !!res.claimed
      trackEvent('wallet_claim_result', {
        category: 'monetization',
        label: res.claimed ? 'claimed' : 'already',
      })
      if (res.balance) balance.value = { ...balance.value, ...res.balance, total: res.balance.free + res.balance.paid }
      await load()
    } else {
      claimMsg.value = res?.detail || '领取失败'
      claimOk.value = false
      trackEvent('wallet_claim_result', { category: 'monetization', label: 'fail' })
    }
  } catch (e) {
    claimMsg.value = '领取失败，请稍后再试'
    trackEvent('wallet_claim_result', { category: 'monetization', label: 'error' })
  } finally {
    claiming.value = false
  }
}

onMounted(() => {
  trackEvent('wallet_view', { category: 'monetization', label: 'page_load' })
  load()
})
</script>

<style scoped>
.wallet-page { max-width: 720px; margin: 0 auto; padding: 32px 20px 80px; }
.wallet-hero {
  display: flex; align-items: center; gap: 16px; margin-bottom: 28px;
  padding: 20px; background: linear-gradient(135deg, #f0f7ff, #fff);
  border-radius: 16px; border: 1px solid #e8f0fa;
}
.wallet-hero-icon { flex-shrink: 0; }
.wallet-hero h1 { font-size: 28px; color: #1e2a3a; margin: 0 0 6px; }
.wallet-hero p { color: #5a6a7a; font-size: 14px; margin: 0; }

.balance-cards { display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 14px; margin-bottom: 24px; }
.bal-card {
  position: relative; background: #fff; border-radius: 14px; padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #e8f0fa;
}
.bal-icon { margin-bottom: 8px; display: block; }
.bal-card.total {
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; border: none;
}
.bal-card.total .bal-icon { filter: brightness(1.2); }
.bal-label { display: block; font-size: 13px; opacity: 0.85; margin-bottom: 8px; }
.bal-num { font-size: 36px; font-weight: 800; font-variant-numeric: tabular-nums; }
.bal-num.sub { font-size: 28px; color: #2563eb; }
.bal-card.total .bal-num { color: #fff; }
.bal-unit { font-size: 14px; margin-left: 4px; }
.bal-hint { display: block; font-size: 12px; color: #94a3b8; margin-top: 6px; }
.bal-card.total .bal-hint { color: rgba(255,255,255,0.8); }

.actions { display: flex; gap: 12px; margin-bottom: 8px; flex-wrap: wrap; }
.btn-claim, .btn-recharge {
  display: inline-flex; align-items: center; gap: 8px; justify-content: center;
  padding: 12px 22px; border-radius: 10px; font-weight: 600; font-size: 14px;
  border: none; cursor: pointer; text-decoration: none; text-align: center;
}
.btn-claim {
  background: linear-gradient(135deg, #fff7e6, #ffe9c7);
  color: #ad6800; border: 1px solid #ffd591;
}
.btn-claim:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-recharge {
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff;
}
.claim-msg { font-size: 13px; margin-bottom: 16px; color: #ef4444; }
.claim-msg.ok { color: #16a34a; }
.pay-hint {
  font-size: 13px; color: #5a6a7a; line-height: 1.55; margin: 0 0 16px;
  padding: 10px 12px; border-radius: 10px; background: #f8fafc; border: 1px solid #e8f0fa;
}
.next-steps {
  margin: 0 0 28px;
  padding: 16px 18px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f0f9ff, #fff);
  border: 1px solid #dbeafe;
}
.next-hint {
  margin: 0 0 12px;
  font-size: 14px;
  color: #475569;
  line-height: 1.55;
}
.next-hint.ok { color: #166534; }
.next-hint.warn { color: #9a3412; }
.next-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.btn-create {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 11px 18px;
  border-radius: 10px;
  background: linear-gradient(135deg, #0d9488, #0f766e);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
}
.btn-next-pricing {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 11px 16px;
  border-radius: 10px;
  background: #eff6ff;
  color: #2563eb;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  border: 1px solid #bfdbfe;
}

.transactions h2 { font-size: 20px; margin-bottom: 16px; color: #1e2a3a; }
.empty { text-align: center; color: #94a3b8; padding: 40px; background: #fff; border-radius: 12px; }
.txn-list { list-style: none; background: #fff; border-radius: 14px; overflow: hidden; border: 1px solid #e8f0fa; }
.txn-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 18px; border-bottom: 1px solid #f0f4f8; gap: 12px;
}
.txn-icon { flex-shrink: 0; border-radius: 8px; }
.txn-left { flex: 1; min-width: 0; }
.txn-item:last-child { border-bottom: none; }
.txn-type { display: block; font-weight: 600; color: #1e2a3a; font-size: 14px; }
.txn-note { display: block; font-size: 12px; color: #94a3b8; margin-top: 2px; }
.txn-right { text-align: right; flex-shrink: 0; }
.txn-amount { display: block; font-weight: 700; color: #ef4444; font-variant-numeric: tabular-nums; }
.txn-amount.plus { color: #16a34a; }
.txn-time { font-size: 11px; color: #cbd5e1; }

@media (max-width: 600px) {
  .wallet-hero { flex-direction: column; text-align: center; }
  .balance-cards { grid-template-columns: 1fr; }
  .actions { flex-direction: column; }
  .btn-claim, .btn-recharge { width: 100%; }
  .next-actions { flex-direction: column; }
  .btn-create, .btn-next-pricing { width: 100%; text-align: center; }
}
</style>
