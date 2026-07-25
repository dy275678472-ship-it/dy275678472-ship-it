/**
 * 案例题材 → 创作向导深链参数。
 * 与 backend seo_page._wizard_genre_from_category 保持一致。
 */
export function wizardGenreFromCategory(category) {
  const cat = String(category || '').trim()
  if (!cat) return { type: '', genreCustom: '', genreName: '' }
  if (cat.includes('系统')) {
    return { type: 'system', genreCustom: '', genreName: '系统流' }
  }
  if (['战神', '兵王'].some((k) => cat.includes(k))) {
    return { type: 'warrior', genreCustom: '', genreName: '战神归来' }
  }
  if (['重生', '穿越'].some((k) => cat.includes(k))) {
    return { type: 'reborn', genreCustom: '', genreName: '重生流' }
  }
  if (['仙侠', '玄幻', '修仙'].some((k) => cat.includes(k))) {
    return { type: 'fantasy', genreCustom: '', genreName: '玄幻修仙' }
  }
  if (['脑洞', '科幻', '末世'].some((k) => cat.includes(k))) {
    return { type: 'brainhole', genreCustom: '', genreName: '脑洞文' }
  }
  if (['游戏', '竞技', '电竞'].some((k) => cat.includes(k))) {
    return { type: 'games', genreCustom: '', genreName: '游戏文' }
  }
  if (['文娱', '明星', '娱乐'].some((k) => cat.includes(k))) {
    return { type: 'entertainment', genreCustom: '', genreName: '文娱' }
  }
  if (['都市', '神豪'].some((k) => cat.includes(k))) {
    return { type: 'urban', genreCustom: '', genreName: '都市神豪' }
  }
  return { type: '', genreCustom: cat.slice(0, 40), genreName: cat.slice(0, 40) }
}

/** 构建创作台深链 query（含 mode=new），供案例/SSR 回流。 */
export function workspaceWizardQuery(category = '', title = '') {
  const seed = wizardGenreFromCategory(category)
  const catLabel = seed.genreName || String(category || '').trim() || '同题材'
  const titlePart = title ? `参考《${String(title).slice(0, 40)}》的风格，` : ''
  const query = {
    mode: 'new',
    prompt: `${titlePart}写一个${catLabel}题材的故事`.slice(0, 500),
  }
  if (seed.type) query.type = seed.type
  if (seed.genreCustom) query.genreCustom = seed.genreCustom
  if (seed.genreName) query.genreName = seed.genreName
  return query
}
