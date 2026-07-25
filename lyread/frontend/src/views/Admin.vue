<template>
  <div class="admin-page">
    <img :src="banner" alt="" class="admin-banner" aria-hidden="true" />
    <header class="admin-header">
      <h1>运营后台</h1>
      <button class="btn-refresh" @click="loadAll">刷新</button>
    </header>

    <div v-if="denied" class="denied">
      <img :src="deniedImg" alt="无权限访问" class="denied-img" width="200" />
      <h2>403 无权限</h2>
      <p>需要管理员权限。请在服务器设置 <code>ADMIN_USERNAMES</code> 或将用户 <code>role</code> 设为 <code>admin</code>。</p>
      <router-link to="/" class="btn-home">返回首页</router-link>
    </div>

    <template v-else>
      <section class="stats-grid" v-if="stats">
        <div class="stat-card" v-for="(v, k) in stats" :key="k">
          <span class="stat-num">{{ v }}</span>
          <span class="stat-label">{{ statLabels[k] || k }}</span>
        </div>
      </section>

      <nav class="tabs">
        <button v-for="t in tabs" :key="t.id" :class="{ active: tab === t.id }" @click="tab = t.id">{{ t.label }}</button>
      </nav>

      <section v-if="tab === 'reviews'" class="panel">
        <h2>待审核 ({{ reviews.length }})</h2>
        <EmptyState
          v-if="!reviews.length"
          :image="images.emptyCreate"
          title="暂无待审核内容"
          description="用户提交公开后会出现在这里。可先核对已上架案例，或到创作台自检种子内容。"
          :image-width="140"
        >
          <div class="empty-actions">
            <router-link
              to="/trending"
              class="btn-empty-secondary"
              @click="trackEmpty('reviews_trending')"
            >去案例广场</router-link>
            <router-link
              to="/workspace"
              class="btn-empty-primary"
              @click="trackEmpty('reviews_workspace')"
            >打开创作台</router-link>
          </div>
        </EmptyState>
        <div v-for="r in reviews" :key="r.id" class="row-card">
          <div>
            <strong>{{ r.title || '未命名' }}</strong>
            <span class="meta">{{ r.target_type }} #{{ r.target_id }} · 用户 {{ r.user_id }}</span>
          </div>
          <div class="row-actions">
            <button class="btn-preview" @click="openPreview(r.id)">预览</button>
            <button class="btn-ok" @click="approve(r.id)">通过</button>
            <button class="btn-no" @click="reject(r.id)">驳回</button>
          </div>
        </div>
      </section>

      <div
        v-if="previewOpen"
        class="preview-modal"
        role="dialog"
        aria-modal="true"
        aria-label="作品预览"
        @click.self="closePreview"
      >
        <div class="preview-panel">
          <header class="preview-head">
            <h3>{{ previewData?.title || '作品预览' }}</h3>
            <button type="button" class="preview-close" aria-label="关闭预览" @click="closePreview">×</button>
          </header>
          <div v-if="previewLoading" class="empty">加载中...</div>
          <div v-else-if="previewData" class="preview-body">
            <p class="preview-meta">{{ previewData.genre }} · {{ previewData.word_count || 0 }} 字 · {{ previewData.chapters_count || 0 }} 章</p>
            <p v-if="previewData.intro"><strong>简介：</strong>{{ previewData.intro }}</p>
            <div v-if="previewData.chapters?.length" class="preview-chapters">
              <div v-for="ch in previewData.chapters" :key="ch.idx" class="preview-ch">
                <h4>{{ ch.title || `第${ch.idx}章` }} <span class="meta">({{ ch.word_count }} 字)</span></h4>
                <pre>{{ ch.excerpt || '（无正文）' }}</pre>
              </div>
            </div>
            <div v-else class="preview-empty">
              <p class="empty">暂无章节正文，请提醒作者先 AI 续写并保存。</p>
              <router-link
                to="/workspace"
                class="btn-empty-primary"
                @click="trackEmpty('preview_workspace')"
              >打开创作台自检</router-link>
            </div>
          </div>
          <footer v-if="previewReviewId != null && !previewLoading" class="preview-actions">
            <button
              type="button"
              class="btn-ok"
              :disabled="previewActing"
              @click="approveFromPreview"
            >通过</button>
            <button
              type="button"
              class="btn-no"
              :disabled="previewActing"
              @click="rejectFromPreview"
            >驳回</button>
            <button type="button" class="btn-preview" :disabled="previewActing" @click="closePreview">关闭</button>
            <span class="preview-hint">A 通过 · R 驳回 · Esc 关闭</span>
          </footer>
        </div>
      </div>

      <section v-if="tab === 'users'" class="panel">
        <h2>用户</h2>
        <EmptyState
          v-if="!users.length"
          title="暂无用户"
          description="注册用户会出现在这里。可先走一遍注册→创作主链路做冒烟。"
          :image-width="120"
        >
          <div class="empty-actions">
            <router-link
              to="/login?mode=register"
              class="btn-empty-secondary"
              @click="trackEmpty('users_register')"
            >打开注册页</router-link>
            <router-link
              to="/workspace"
              class="btn-empty-primary"
              @click="trackEmpty('users_workspace')"
            >去创作台</router-link>
          </div>
        </EmptyState>
        <table v-else>
          <thead><tr><th>ID</th><th>用户名</th><th>点数</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>{{ u.id }}</td>
              <td>{{ u.username }} <span v-if="u.role==='admin'" class="badge">admin</span></td>
              <td>{{ (u.free_balance||0) + (u.paid_balance||0) }}</td>
              <td><button class="btn-sm" @click="adjust(u)">+10点</button></td>
            </tr>
          </tbody>
        </table>
      </section>

      <section v-if="tab === 'orders'" class="panel">
        <h2>订单</h2>
        <EmptyState
          v-if="!orders.length"
          title="暂无订单"
          description="用户在价格页下单后会出现在这里。可先核对套餐与沙箱收款链路。"
          :image-width="120"
        >
          <div class="empty-actions">
            <router-link
              to="/pricing"
              class="btn-empty-primary"
              @click="trackEmpty('orders_pricing')"
            >打开价格页</router-link>
          </div>
        </EmptyState>
        <table v-else>
          <thead><tr><th>订单号</th><th>用户</th><th>点数</th><th>金额</th><th>状态</th></tr></thead>
          <tbody>
            <tr v-for="o in orders" :key="o.out_trade_no">
              <td class="mono">{{ o.out_trade_no }}</td>
              <td>{{ o.user_id }}</td>
              <td>{{ o.points }}</td>
              <td>¥{{ (o.amount_fen/100).toFixed(2) }}</td>
              <td>{{ o.status }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section v-if="tab === 'jobs'" class="panel">
        <h2>生成任务</h2>
        <EmptyState
          v-if="!jobs.length"
          title="暂无生成任务"
          description="AI 续写/大纲等任务会列在这里。可到创作台跑一次生成做巡检。"
          :image-width="120"
        >
          <div class="empty-actions">
            <router-link
              to="/workspace"
              class="btn-empty-primary"
              @click="trackEmpty('jobs_workspace')"
            >打开创作台</router-link>
          </div>
        </EmptyState>
        <table v-else>
          <thead><tr><th>ID</th><th>用户</th><th>类型</th><th>点数</th><th>状态</th></tr></thead>
          <tbody>
            <tr v-for="j in jobs" :key="j.id">
              <td>{{ j.id }}</td>
              <td>{{ j.user_id }}</td>
              <td>{{ j.job_type }}</td>
              <td>{{ j.reserved_credits }}</td>
              <td>{{ j.status }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { adminApi } from '../api'
import { IMAGES } from '../assets/images'
import EmptyState from '../components/EmptyState.vue'
import { trackEvent } from '../utils/analytics'

const banner = IMAGES.adminBanner
const deniedImg = IMAGES.adminDenied
const images = IMAGES

const denied = ref(false)
const tab = ref('reviews')
const stats = ref(null)
const reviews = ref([])
const users = ref([])
const orders = ref([])
const jobs = ref([])
const previewOpen = ref(false)
const previewLoading = ref(false)
const previewData = ref(null)
const previewReviewId = ref(null)
const previewActing = ref(false)

function trackEmpty(label) {
  trackEvent('admin_empty_cta', { category: 'engagement', label })
}

function closePreview() {
  previewOpen.value = false
  previewReviewId.value = null
  previewData.value = null
  previewActing.value = false
}

function onPreviewKeydown(e) {
  if (!previewOpen.value || previewActing.value || previewLoading.value) return
  if (e.metaKey || e.ctrlKey || e.altKey) return
  const tag = (e.target && e.target.tagName) || ''
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || e.target?.isContentEditable) return
  if (e.key === 'Escape') {
    e.preventDefault()
    closePreview()
    return
  }
  const k = e.key.length === 1 ? e.key.toLowerCase() : e.key
  if (k === 'a') {
    e.preventDefault()
    approveFromPreview()
    return
  }
  if (k === 'r') {
    e.preventDefault()
    rejectFromPreview()
  }
}

watch(previewOpen, (open) => {
  if (open) {
    window.addEventListener('keydown', onPreviewKeydown)
  } else {
    window.removeEventListener('keydown', onPreviewKeydown)
  }
})

const tabs = [
  { id: 'reviews', label: '审核' },
  { id: 'users', label: '用户' },
  { id: 'orders', label: '订单' },
  { id: 'jobs', label: '任务' },
]

const statLabels = {
  users: '用户', stories: '作品', paid_orders: '已付订单',
  total_credits: '总点数', running_jobs: '进行中任务', pending_reviews: '待审核',
}

async function loadAll() {
  try {
    const s = await adminApi.stats()
    if (s?.success) stats.value = s.stats
    const [rv, us, od, jb] = await Promise.all([
      adminApi.reviews('pending'), adminApi.users(), adminApi.orders(), adminApi.jobs(),
    ])
    if (rv?.success) reviews.value = rv.reviews || []
    if (us?.success) users.value = us.users || []
    if (od?.success) orders.value = od.orders || []
    if (jb?.success) jobs.value = jb.jobs || []
    denied.value = false
  } catch (e) {
    denied.value = true
  }
}

async function openPreview(id) {
  previewOpen.value = true
  previewReviewId.value = id
  previewLoading.value = true
  previewData.value = null
  previewActing.value = false
  trackEvent('admin_review_preview', { category: 'engagement', label: String(id) })
  try {
    const res = await adminApi.reviewPreview(id)
    if (res?.success) previewData.value = res.preview
  } finally {
    previewLoading.value = false
  }
}

async function approve(id) {
  const res = await adminApi.approveReview(id)
  alert(res?.message || res?.detail || '完成')
  trackEvent('admin_review_approve', { category: 'engagement', label: String(id) })
  await loadAll()
}

async function reject(id) {
  const reason = prompt('驳回原因（可选）') || ''
  await adminApi.rejectReview(id, reason)
  trackEvent('admin_review_reject', { category: 'engagement', label: String(id) })
  await loadAll()
}

async function approveFromPreview() {
  const id = previewReviewId.value
  if (id == null || previewActing.value) return
  previewActing.value = true
  try {
    await approve(id)
    closePreview()
  } finally {
    previewActing.value = false
  }
}

async function rejectFromPreview() {
  const id = previewReviewId.value
  if (id == null || previewActing.value) return
  previewActing.value = true
  try {
    await reject(id)
    closePreview()
  } finally {
    previewActing.value = false
  }
}

async function adjust(u) {
  const res = await adminApi.adjustCredits(u.id, 10, '管理员赠送')
  alert(res?.success ? `已调整，余额 ${res.balance?.total}` : (res?.detail || '失败'))
  loadAll()
}

onMounted(loadAll)
onUnmounted(() => {
  window.removeEventListener('keydown', onPreviewKeydown)
})
</script>

<style scoped>
.admin-page { max-width: 1100px; margin: 0 auto; padding: 0 20px 80px; }
.admin-banner { width: 100%; height: auto; border-radius: 16px; margin: 24px 0 0; display: block; object-fit: cover; max-height: 140px; }
.admin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; margin-top: 16px; }
.admin-header h1 { font-size: 24px; }
.btn-refresh { padding: 8px 16px; border-radius: 8px; border: 1px solid #dbeafe; background: #fff; cursor: pointer; }
.denied { text-align: center; padding: 40px 20px 60px; color: #64748b; }
.denied-img { display: block; margin: 0 auto 20px; }
.denied h2 { color: #1e2a3a; margin-bottom: 12px; }
.btn-home {
  display: inline-block; margin-top: 20px; padding: 10px 20px; border-radius: 10px;
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; text-decoration: none; font-weight: 600;
}
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }
.stat-card { background: #fff; border-radius: 12px; padding: 16px; border: 1px solid #e8f0fa; text-align: center; }
.stat-num { display: block; font-size: 28px; font-weight: 800; color: #2563eb; }
.stat-label { font-size: 12px; color: #94a3b8; }
.tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.tabs button { padding: 8px 16px; border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; cursor: pointer; }
.tabs button.active { background: #2563eb; color: #fff; border-color: #2563eb; }
.panel { background: #fff; border-radius: 14px; padding: 20px; border: 1px solid #e8f0fa; }
.panel h2 { font-size: 16px; margin-bottom: 16px; }
.empty { color: #94a3b8; padding: 20px 0; }
.empty-actions {
  display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; align-items: center;
}
.btn-empty-secondary, .btn-empty-primary {
  display: inline-block; padding: 10px 16px; border-radius: 10px; font-size: 14px;
  font-weight: 600; text-decoration: none; border: 1px solid #dbeafe;
}
.btn-empty-secondary { background: #fff; color: #2563eb; }
.btn-empty-secondary:hover { background: #f0f7ff; }
.btn-empty-primary {
  background: linear-gradient(135deg, #4da1ff, #2563eb); color: #fff; border-color: transparent;
}
.preview-empty { text-align: center; padding: 8px 0 4px; }
.preview-empty .empty { padding-bottom: 12px; }
.row-card { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid #f0f4f8; gap: 12px; }
.meta { display: block; font-size: 12px; color: #94a3b8; margin-top: 4px; }
.row-actions { display: flex; gap: 8px; flex-shrink: 0; }
.btn-ok, .btn-no, .btn-sm, .btn-preview { padding: 6px 12px; border-radius: 8px; border: none; cursor: pointer; font-size: 13px; }
.btn-preview { background: #eff6ff; color: #2563eb; }
.btn-ok { background: #16a34a; color: #fff; }
.btn-no { background: #fef2f2; color: #ef4444; }
.btn-sm { background: #eff6ff; color: #2563eb; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { padding: 10px 8px; text-align: left; border-bottom: 1px solid #f0f4f8; }
.mono { font-family: monospace; font-size: 11px; }
.badge { background: #fef3c7; color: #b45309; font-size: 10px; padding: 2px 6px; border-radius: 4px; margin-left: 4px; }
.preview-modal {
  position: fixed; inset: 0; background: rgba(15,23,42,0.45); z-index: 1000;
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.preview-panel {
  width: min(760px, 100%); max-height: 85vh; overflow: auto;
  background: #fff; border-radius: 16px; padding: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}
.preview-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.preview-close { border: none; background: transparent; font-size: 24px; cursor: pointer; color: #94a3b8; }
.preview-meta { color: #64748b; font-size: 13px; margin-bottom: 12px; }
.preview-actions {
  display: flex; flex-wrap: wrap; align-items: center; gap: 8px;
  margin-top: 16px; padding-top: 14px; border-top: 1px solid #f0f4f8;
  position: sticky; bottom: 0; background: #fff;
}
.preview-actions .btn-ok,
.preview-actions .btn-no,
.preview-actions .btn-preview { padding: 8px 14px; }
.preview-actions .btn-ok:disabled,
.preview-actions .btn-no:disabled,
.preview-actions .btn-preview:disabled { opacity: 0.6; cursor: not-allowed; }
.preview-hint { margin-left: auto; font-size: 12px; color: #94a3b8; }
.preview-ch { margin-top: 16px; padding-top: 16px; border-top: 1px solid #f0f4f8; }
.preview-ch h4 { font-size: 14px; margin-bottom: 8px; }
.preview-ch pre {
  white-space: pre-wrap; word-break: break-word; font-family: inherit;
  font-size: 13px; line-height: 1.7; color: #334155; background: #f8fafc;
  padding: 12px; border-radius: 8px; max-height: 240px; overflow: auto;
}
@media (max-width: 768px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
