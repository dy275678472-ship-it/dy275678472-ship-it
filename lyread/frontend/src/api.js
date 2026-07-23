async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  const token = localStorage.getItem('token')
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(path, { ...options, headers })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    return {
      ...data,
      detail: data.detail || data.error || res.statusText,
      status: res.status,
      insufficient_credits: res.status === 402,
    }
  }
  return data
}

export const authApi = {
  login(username, password) {
    return request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  },
  register(username, password, email) {
    return request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password, email: email || undefined }),
    })
  },
  forgot(username, email) {
    return request('/api/auth/forgot', { method: 'POST', body: JSON.stringify({ username, email }) })
  },
  reset(token, password) {
    return request('/api/auth/reset', { method: 'POST', body: JSON.stringify({ token, password }) })
  },
}

export const creditsApi = {
  balance() { return request('/api/credits/balance') },
  prices() { return request('/api/credits/prices') },
  dailyClaim() { return request('/api/credits/daily-claim', { method: 'POST' }) },
  transactions(limit = 30) { return request(`/api/credits/transactions?limit=${limit}`) },
  estimate(jobType) { return request('/api/credits/estimate', { method: 'POST', body: JSON.stringify({ job_type: jobType }) }) },
}

export const storyApi = {
  list(status) { return request(`/api/story/list${status ? `?status=${status}` : ''}`) },
  get(id) { return request(`/api/story/${id}`) },
  chapters(id) { return request(`/api/story/${id}/chapters`) },
  save(data) { return request('/api/story/save', { method: 'POST', body: JSON.stringify(data) }) },
  remove(id) { return request(`/api/story/${id}`, { method: 'DELETE' }) },
  suggestGenres() { return request('/api/story/suggest-genres') },
  godfingers() { return request('/api/story/godfingers') },
  levelSystems() { return request('/api/story/level-systems') },
  generateTitle(body) { return request('/api/story/generate-title', { method: 'POST', body: JSON.stringify(body) }) },
  suggestIdeas(body) { return request('/api/story/suggest-ideas', { method: 'POST', body: JSON.stringify(body) }) },
  generateOutline(body) { return request('/api/story/generate-outline', { method: 'POST', body: JSON.stringify(body) }) },
  generateChapters(body) { return request('/api/story/generate-chapters', { method: 'POST', body: JSON.stringify(body) }) },
  generateShort(body) { return request('/api/story/generate-short', { method: 'POST', body: JSON.stringify(body) }) },
  continue(body) { return request('/api/story/ai-continue', { method: 'POST', body: JSON.stringify(body) }) },
  consistencyCheck(body) { return request('/api/story/consistency-check', { method: 'POST', body: JSON.stringify(body) }) },
  memory(id) { return request(`/api/story/${id}/memory`) },
  exportUrl(id, format = 'txt') { return `/api/story/${id}/export?format=${format}` },
}

export const casesApi = {
  list(limit = 20, category) {
    const q = new URLSearchParams({ limit: String(limit) })
    if (category) q.set('category', category)
    return request(`/api/cases?${q}`)
  },
  get(id) { return request(`/api/cases/${id}`) },
  neighbors(id) { return request(`/api/cases/${id}/neighbors`) },
}

export const ordersApi = {
  packages() { return request('/api/orders/packages') },
  create(packageId, idempotencyKey) {
    return request('/api/orders/create', { method: 'POST', body: JSON.stringify({ package_id: packageId, idempotency_key: idempotencyKey }) })
  },
  sandboxConfirm(outTradeNo) {
    return request(`/api/orders/sandbox/confirm/${outTradeNo}`, { method: 'POST' })
  },
}

export const adminApi = {
  stats() { return request('/api/admin/stats') },
  users(limit = 50) { return request(`/api/admin/users?limit=${limit}`) },
  stories(limit = 50) { return request(`/api/admin/stories?limit=${limit}`) },
  orders(limit = 50) { return request(`/api/admin/orders?limit=${limit}`) },
  jobs(limit = 50) { return request(`/api/admin/jobs?limit=${limit}`) },
  reviews(result = 'pending') { return request(`/api/admin/reviews?result=${result}`) },
  reviewPreview(id) { return request(`/api/admin/reviews/${id}/preview`) },
  approveReview(id) { return request(`/api/admin/reviews/${id}/approve`, { method: 'POST' }) },
  rejectReview(id, reason) { return request(`/api/admin/reviews/${id}/reject`, { method: 'POST', body: JSON.stringify({ reason }) }) },
  adjustCredits(userId, points, note, target = 'paid') {
    return request(`/api/admin/users/${userId}/credits`, {
      method: 'POST', body: JSON.stringify({ points, note, target }),
    })
  },
}

export const statsApi = {
  public() { return request('/api/stats/public') },
}

export const authApiMe = () => request('/api/auth/me')
