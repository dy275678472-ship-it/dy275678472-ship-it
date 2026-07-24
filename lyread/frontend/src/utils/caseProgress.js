/** CaseReader / Trending 共用：本地阅读进度 */

export const CASE_PROGRESS_KEY = 'lyread_case_progress'
export const RESUME_MIN_RATIO = 0.12
export const RESUME_MAX_RATIO = 0.92
export const DONE_RATIO = 0.96

export function caseProgressStorageKey(id) {
  return `${CASE_PROGRESS_KEY}:${id}`
}

export function readCaseProgress(id) {
  try {
    const raw = localStorage.getItem(caseProgressStorageKey(id))
    if (!raw) return null
    const data = JSON.parse(raw)
    if (!data || typeof data.ratio !== 'number') return null
    return data
  } catch {
    return null
  }
}

/**
 * 扫描 localStorage，取最近一次可读进度（未读完、进度在合理区间）。
 * @param {Array<{id:number|string,title?:string,category?:string}>} [cases]
 */
export function findLatestResumeProgress(cases = []) {
  if (typeof localStorage === 'undefined') return null
  const byId = new Map()
  for (const c of cases) {
    if (c?.id != null) byId.set(String(c.id), c)
  }
  const prefix = `${CASE_PROGRESS_KEY}:`
  let best = null
  try {
    for (let i = 0; i < localStorage.length; i += 1) {
      const key = localStorage.key(i)
      if (!key || !key.startsWith(prefix)) continue
      const id = key.slice(prefix.length)
      if (!id) continue
      let data
      try {
        data = JSON.parse(localStorage.getItem(key) || '')
      } catch {
        continue
      }
      if (!data || typeof data.ratio !== 'number') continue
      if (data.ratio >= DONE_RATIO) {
        try { localStorage.removeItem(key) } catch { /* ignore */ }
        continue
      }
      if (data.ratio < RESUME_MIN_RATIO || data.ratio > RESUME_MAX_RATIO) continue
      const updatedAt = Number(data.updatedAt) || 0
      if (best && updatedAt <= best.updatedAt) continue
      const hit = byId.get(String(id))
      best = {
        id: Number(id) || id,
        ratio: data.ratio,
        chapterIndex: Number.isFinite(data.chapterIndex) ? data.chapterIndex : 0,
        updatedAt,
        title: data.title || hit?.title || `案例 #${id}`,
        category: data.category || hit?.category || '',
      }
    }
  } catch {
    return null
  }
  return best
}
