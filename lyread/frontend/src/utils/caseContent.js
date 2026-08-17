/** 案例正文解析与展示辅助 */

const PAD_TAIL_LINE_RE = /^(故事，?\s*仍在前方。?|故事仍在前方。?)\s*$/u
const EXCERPT_END_RE = /^（节选完[^）]*）\s*$/u

export function cleanExcerptText(text) {
  if (!text) return ''
  let t = text
  if (t.includes('【阅读提示】')) t = t.split('【阅读提示】')[0]
  if (t.includes('【节选说明】')) t = t.split('【节选说明】')[0]
  const lines = t.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n')
  while (lines.length) {
    const stripped = lines[lines.length - 1].trim()
    if (!stripped || EXCERPT_END_RE.test(stripped) || PAD_TAIL_LINE_RE.test(stripped)) {
      lines.pop()
      continue
    }
    break
  }
  return lines.join('\n').trim()
}

export function parseChapters(text) {
  const cleaned = cleanExcerptText(text)
  if (!cleaned) return []
  const lines = cleaned.split('\n')
  const chapters = []
  let current = null

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue
    if (/^第[一二三四五六七八九十百千0-9]+章/.test(trimmed)) {
      if (current) chapters.push(current)
      current = { title: trimmed, paragraphs: [] }
    } else if (current) {
      current.paragraphs.push(trimmed)
    } else {
      if (!chapters.length) chapters.push({ title: '', paragraphs: [] })
      chapters[0].paragraphs.push(trimmed)
    }
  }
  if (current) chapters.push(current)
  return chapters.filter((ch) => ch.title || ch.paragraphs.length)
}

export function countChapters(text) {
  return (cleanExcerptText(text).match(/^第[一二三四五六七八九十百千0-9]+章/gm) || []).length
}

export function formatStoryWords(n) {
  const w = Number(n) || 0
  if (w >= 10000) return `设定约 ${(w / 10000).toFixed(1)} 万字`
  return `设定 ${w} 字`
}
