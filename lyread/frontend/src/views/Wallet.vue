<template>
  <div class="wallet-page">
    <header class="wallet-hero">
      <h1>我的点数</h1>
      <p>免费额度当日有效；充值点数长期有效；生成失败自动返还。</p>
    </header>

    <section class="balance-cards" v-if="balance">
      <div class="bal-card total">
        <span class="bal-label">可用总额</span>
        <span class="bal-num">{{ balance.total }}</span>
        <span class="bal-unit">点</span>
      </div>
      <div class="bal-card">
        <span class="bal-label">免费额度</span>
        <span class="bal-num sub">{{ balance.free }}</span>
        <span class="bal-hint">今日有效</span>
      </div>
      <div class="bal-card">
        <span class="bal-label">充值/赠送</span>
        <span class="bal-num sub">{{ balance.paid }}</span>
        <span class="bal-hint" v-if="balance.reserved">冻结 {{ balance.reserved }} 点</span>
      </div>
    </section>

    <section class="actions">
      <button class="btn-claim" :disabled="claiming" @click="claimDaily">
        {{ claiming ? '领取中...' : '领取今日免费 5 点' }}
      </button>
      <router-link to="/pricing" class="btn-recharge">充值点数</router-link>
    </section>
    <p v-if="claimMsg" class="claim-msg" :class="{ ok: claimOk }">{{ claimMsg }}</p>

    <section class="transactions">
      <h2>消费记录</h2>
      <div v-if="loading" class="empty">加载中...</div>
      <div v-else-if="!txns.length" class="empty">暂无记录</div>
      <ul v-else class="txn-list">
        <li v-for="(t, i) in txns" :key="i" class="txn-item">
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
import { creditsApi } from '../api'

const balance = ref(null)
const txns = ref([])
const loading = ref(true)
const claiming = ref(false)
const claimMsg = ref('')
const claimOk = ref(false)

const TYPE_LABELS = {
  signup_bonus: '注册赠送',
  daily_grant: '每日免费',
  reserve: '预冻结',
  settle: '消费结算',
  refund: '失败返还',
  recharge: '充值到账',
}

function typeLabel(t) { return TYPE_LABELS[t] || t }

function formatTime(s) {
  if (!s) return ''
  return s.replace('T', ' ').slice(0, 16)
}

async function load() {
  loading.value = true
  try {
    const [bal, hist] = await Promise.all([
      creditsApi.balance(),
      creditsApi.transactions(40),
    ])
    if (bal?.success) balance.value = bal
    if (hist?.success) txns.value = hist.transactions || []
  } finally {
    loading.value = false
  }
}

async function claimDaily() {
  claiming.value = true
  claimMsg.value = ''
  try {
    const res = await creditsApi.dailyClaim()
    if (res?.success) {
      claimOk.value = !!res.claimed
      claimMsg.value = res.message || (res.claimed ? '领取成功' : '今日已领取')
      if (res.balance) balance.value = { ...balance.value, ...res.balance, total: res.balance.free + res.balance.paid }
      await load()
    } else {
      claimMsg.value = res?.detail || '领取失败'
      claimOk.value = false
    }
  } catch (e) {
    claimMsg.value = '领取失败，请稍后再试'
  } finally {
    claiming.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.wallet-page { max-width: 720px; margin: 0 auto; padding: 32px 20px 80px; }
.wallet-hero { margin-bottom: 28px; }
.wallet-hero h1 { font-size: 28px; color: #1e2a3a; margin-bottom: 8px; }
.wallet-hero p { color: #5a6a7a; font-size: 14px; }

.balance-cards { display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 14px; margin-bottom: 24px; }
.bal-card {
  background: #fff; border-radius: 14px; padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #e8f0fa;
}
.bal-card.total {
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; border: none;
}
.bal-label { display: block; font-size: 13px; opacity: 0.85; margin-bottom: 8px; }
.bal-num { font-size: 36px; font-weight: 800; font-variant-numeric: tabular-nums; }
.bal-num.sub { font-size: 28px; color: #2563eb; }
.bal-card.total .bal-num { color: #fff; }
.bal-unit { font-size: 14px; margin-left: 4px; }
.bal-hint { display: block; font-size: 12px; color: #94a3b8; margin-top: 6px; }
.bal-card.total .bal-hint { color: rgba(255,255,255,0.8); }

.actions { display: flex; gap: 12px; margin-bottom: 8px; flex-wrap: wrap; }
.btn-claim, .btn-recharge {
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
.claim-msg { font-size: 13px; margin-bottom: 24px; color: #ef4444; }
.claim-msg.ok { color: #16a34a; }

.transactions h2 { font-size: 20px; margin-bottom: 16px; color: #1e2a3a; }
.empty { text-align: center; color: #94a3b8; padding: 40px; background: #fff; border-radius: 12px; }
.txn-list { list-style: none; background: #fff; border-radius: 14px; overflow: hidden; border: 1px solid #e8f0fa; }
.txn-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 18px; border-bottom: 1px solid #f0f4f8; gap: 12px;
}
.txn-item:last-child { border-bottom: none; }
.txn-type { display: block; font-weight: 600; color: #1e2a3a; font-size: 14px; }
.txn-note { display: block; font-size: 12px; color: #94a3b8; margin-top: 2px; }
.txn-right { text-align: right; flex-shrink: 0; }
.txn-amount { display: block; font-weight: 700; color: #ef4444; font-variant-numeric: tabular-nums; }
.txn-amount.plus { color: #16a34a; }
.txn-time { font-size: 11px; color: #cbd5e1; }

@media (max-width: 600px) {
  .balance-cards { grid-template-columns: 1fr; }
  .actions { flex-direction: column; }
  .btn-claim, .btn-recharge { width: 100%; }
}
</style>
