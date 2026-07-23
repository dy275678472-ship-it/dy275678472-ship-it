/** 数字展示：小数值直接显示，大数值用「万」单位（不夸大） */
export function formatCount(n) {
  const num = Number(n) || 0
  if (num >= 10000) return `${(num / 10000).toFixed(1).replace(/\.0$/, '')}万`
  if (num >= 1000) return `${(num / 1000).toFixed(1).replace(/\.0$/, '')}千`
  return String(num)
}

export function formatWords(n) {
  const num = Number(n) || 0
  if (num >= 10000) return `${formatCount(num)}字`
  return `${num}字`
}

/** 案例卡片：节选信息（优先于设定全文字数） */
export function formatExcerptLabel(item) {
  const chapters = Number(item?.excerpt_chapters) || 0
  const chars = Number(item?.excerpt_chars) || 0
  if (chapters && chars) return `节选 ${chapters} 章 · 约 ${chars} 字`
  if (chars) return `节选约 ${chars} 字`
  return '精选节选'
}

/** 设定全文字数（用于次要展示） */
export function formatStorySettingWords(n) {
  const num = Number(n) || 0
  if (!num) return ''
  if (num >= 10000) return `设定约 ${(num / 10000).toFixed(1).replace(/\.0$/, '')} 万字`
  return `设定 ${num} 字`
}
