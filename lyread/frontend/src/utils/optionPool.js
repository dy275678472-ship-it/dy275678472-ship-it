/** 选项池工具：洗牌、去重合并、随机抽取 */

export function shuffleArray(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

export function pickRandom(arr, n = 3) {
  return shuffleArray(arr).slice(0, Math.min(n, arr.length))
}

/** 按 title 字段去重合并候选列表 */
export function mergeTitleCandidates(existing, incoming) {
  const seen = new Set(existing.map(t => (t.title || '').trim()))
  const merged = [...existing]
  for (const t of incoming || []) {
    const key = (t.title || '').trim()
    if (!key || seen.has(key)) continue
    seen.add(key)
    merged.push({ title: key, hook: t.hook || t.description || '' })
  }
  return merged
}

export function mergeStringOptions(existing, incoming) {
  const seen = new Set(existing.map(s => s.trim()))
  const merged = [...existing]
  for (const s of incoming || []) {
    const key = (s || '').trim()
    if (!key || seen.has(key)) continue
    seen.add(key)
    merged.push(key)
  }
  return merged
}
