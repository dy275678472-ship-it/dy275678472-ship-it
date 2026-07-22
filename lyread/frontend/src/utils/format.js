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
