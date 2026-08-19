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

/**
 * 案例题材 → /genre/:slug（与 backend GENRE_PAGES 对齐）。
 * 无匹配时回退 /trending，供题材链尾完读回流。
 */
export function genreHubPathFromCategory(category) {
  const cat = String(category || '').trim()
  if (!cat) return '/trending'
  if (cat.includes('系统')) return '/genre/xitong'
  if (['战神', '兵王'].some((k) => cat.includes(k))) return '/genre/zhanshen'
  if (['重生', '穿越'].some((k) => cat.includes(k))) return '/genre/chongsheng'
  if (['仙侠', '玄幻', '修仙'].some((k) => cat.includes(k))) return '/genre/xianxia'
  if (cat.includes('萌宝')) return '/genre/mengbao'
  if (['言情', '甜宠'].some((k) => cat.includes(k))) return '/genre/yanqing'
  // 灵异悬疑须先于悬疑，避免「悬疑」子串误入 xuanyi
  if (['灵异', '恐怖'].some((k) => cat.includes(k))) return '/genre/lingyi'
  if (['悬疑', '推理'].some((k) => cat.includes(k))) return '/genre/xuanyi'
  if (cat.includes('短篇')) return '/genre/duanpian'
  if (cat.includes('末世')) return '/genre/moshi'
  if (['宫廷', '宫斗'].some((k) => cat.includes(k))) return '/genre/gongting'
  if (cat.includes('赛博')) return '/genre/saibo'
  if (cat.includes('赘婿')) return '/genre/zhuixu'
  if (['科幻', '脑洞'].some((k) => cat.includes(k))) return '/genre/kehuan'
  if (cat.includes('校园')) return '/genre/xiaoyuan'
  if (['游戏', '电竞', '竞技'].some((k) => cat.includes(k))) return '/genre/youxi'
  if (cat.includes('历史')) return '/genre/lishi'
  if (['都市', '神豪'].some((k) => cat.includes(k))) return '/genre/dushi'
  return '/trending'
}
