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
}
