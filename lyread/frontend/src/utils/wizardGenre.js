/**
 * Map showcase/case Chinese categories → CreationWizard genre seed.
 * suggest-genres ids: urban/system/reborn/warrior/fantasy/brainhole/games/entertainment
 * Passing raw Chinese as genreId breaks chip selection + IDEA_TEMPLATES lookup.
 */
export function wizardGenreFromCategory(category) {
  const cat = String(category || '').trim()
  if (!cat) return { type: '', genreCustom: '', genreName: '' }

  if (/系统/.test(cat)) return { type: 'system', genreCustom: '', genreName: '系统流' }
  if (/战神|兵王/.test(cat)) return { type: 'warrior', genreCustom: '', genreName: '战神归来' }
  if (/重生|穿越/.test(cat)) return { type: 'reborn', genreCustom: '', genreName: '重生流' }
  if (/仙侠|玄幻|修仙/.test(cat)) return { type: 'fantasy', genreCustom: '', genreName: '玄幻修仙' }
  if (/脑洞|科幻|末世/.test(cat)) return { type: 'brainhole', genreCustom: '', genreName: '脑洞文' }
  if (/游戏|竞技|电竞/.test(cat)) return { type: 'games', genreCustom: '', genreName: '游戏文' }
  if (/文娱|明星|娱乐/.test(cat)) return { type: 'entertainment', genreCustom: '', genreName: '文娱' }
  if (/都市|神豪/.test(cat)) return { type: 'urban', genreCustom: '', genreName: '都市神豪' }
  if (/言情|甜宠|恋爱|校园|青春/.test(cat)) {
    return { type: '', genreCustom: cat.slice(0, 40), genreName: cat.slice(0, 40) }
  }

  return { type: '', genreCustom: cat.slice(0, 40), genreName: cat.slice(0, 40) }
}

/** Build /workspace query that opens wizard with genre + prompt prefilled. */
export function workspaceWizardQuery({ category, title, prompt } = {}) {
  const seed = wizardGenreFromCategory(category)
  const catLabel = seed.genreName || String(category || '').trim() || '同题材'
  const titlePart = title ? `参考《${String(title).slice(0, 40)}》的风格，` : ''
  const query = {
    mode: 'new',
    prompt: String(prompt || `${titlePart}写一个${catLabel}题材的故事`).slice(0, 500),
  }
  if (seed.type) query.type = seed.type
  if (seed.genreCustom) query.genreCustom = seed.genreCustom
  if (seed.genreName) query.genreName = seed.genreName
  return query
}
