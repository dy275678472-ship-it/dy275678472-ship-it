async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  const token = localStorage.getItem('token')
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(path, { ...options, headers })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) return { ...data, detail: data.detail || data.error || res.statusText }
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
  save(data) { return request('/api/story/save', { method: 'POST', body: JSON.stringify(data) }) },
  remove(id) { return request(`/api/story/${id}`, { method: 'DELETE' }) },
  generateTitle(body) { return request('/api/story/generate-title', { method: 'POST', body: JSON.stringify(body) }) },
  generateOutline(body) { return request('/api/story/generate-outline', { method: 'POST', body: JSON.stringify(body) }) },
  generateChapters(body) { return request('/api/story/generate-chapters', { method: 'POST', body: JSON.stringify(body) }) },
  continue(body) { return request('/api/story/ai-continue', { method: 'POST', body: JSON.stringify(body) }) },
  memory(id) { return request(`/api/story/${id}/memory`) },
  exportUrl(id, format = 'txt') { return `/api/story/${id}/export?format=${format}` },
}

export const casesApi = {
  list(limit = 20) { return request(`/api/cases?limit=${limit}`) },
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
