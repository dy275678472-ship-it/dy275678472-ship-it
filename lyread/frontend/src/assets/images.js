/** 站点静态图片路径（public/images） */
export const IMAGES = {
  logo: '/images/logo-icon-v2.svg',
  logoLegacy: '/images/logo-icon.webp',
  hero: '/images/hero-banner.webp',
  workspace: '/images/workspace-banner.webp',
  emptyCreate: '/images/empty-create.webp',
  ogShare: '/images/og-share.png',
  loginIllustration: '/images/login-illustration.svg',
  adminBanner: '/images/admin-banner.svg',
  adminDenied: '/images/admin-denied.svg',
  defaultStoryCover: '/images/default-story-cover.svg',
  pricingHero: '/images/pricing-hero.svg',
  point: '/images/icon-point.webp',
  fire: '/images/icon-fire.webp',
  ui: {
    menu: '/images/icon-menu.svg',
    close: '/images/icon-close.svg',
    wechat: '/images/icon-wechat.svg',
    qq: '/images/icon-qq.svg',
  },
  features: {
    brain: '/images/icon-brain.webp',
    novel: '/images/icon-novel.webp',
    short: '/images/icon-short.webp',
    credits: '/images/icon-credits.webp',
  },
  covers: [
    '/images/cover-urban.webp',
    '/images/cover-warrior.webp',
    '/images/cover-reborn.webp',
    '/images/cover-xianxia.webp',
    '/images/cover-romance.webp',
    '/images/cover-scifi.webp',
    '/images/cover-suspense.webp',
    '/images/cover-history.webp',
  ],
  /** 题材 OG 分享图（1200×630，社交爬虫兼容） */
  ogGenre: {
    urban: '/images/og-genre-urban.webp',
    warrior: '/images/og-genre-warrior.webp',
    reborn: '/images/og-genre-reborn.webp',
    xianxia: '/images/og-genre-xianxia.webp',
    romance: '/images/og-genre-romance.webp',
    scifi: '/images/og-genre-scifi.webp',
    suspense: '/images/og-genre-suspense.webp',
    history: '/images/og-genre-history.webp',
  },
  avatars: {
    author: '/images/avatar-author.webp',
    studio: '/images/avatar-studio.webp',
  },
  pricing: {
    gift: '/images/icon-gift.webp',
    daily: '/images/icon-daily.webp',
    gem: '/images/icon-gem.webp',
  },
  wallet: {
    total: '/images/icon-gem.webp',
    free: '/images/icon-daily.webp',
    paid: '/images/icon-credits.webp',
  },
  workspaceActions: {
    title: '/images/icon-action-title.svg',
    outline: '/images/icon-action-outline.svg',
    chapters: '/images/icon-action-chapters.svg',
    continue: '/images/icon-action-continue.svg',
  },
  txn: {
    signup: '/images/icon-txn-bonus.svg',
    daily: '/images/icon-daily.webp',
    recharge: '/images/icon-txn-recharge.svg',
    refund: '/images/icon-txn-refund.svg',
    spend: '/images/icon-txn-consume.svg',
    reserve: '/images/icon-txn-reserve.svg',
  },
}

/** 与后端 _cover_path_for_category / _og_image_for_category 对齐的题材键。 */
export function genreKeyForCase(item) {
  const cat = String(item?.category || '').toLowerCase()
  if (/仙侠|玄幻|修仙/.test(cat)) return 'xianxia'
  if (/言情|甜宠|恋爱/.test(cat)) return 'romance'
  if (/科幻|脑洞|末世/.test(cat)) return 'scifi'
  if (/悬疑|推理|惊悚/.test(cat)) return 'suspense'
  if (/历史|架空|宫廷/.test(cat)) return 'history'
  if (/战神|都市|神豪/.test(cat)) return 'warrior'
  if (/重生|穿越/.test(cat)) return 'reborn'
  if (/系统|游戏|竞技|校园|青春/.test(cat)) return 'urban'
  return null
}

export function coverForCase(item, index = 0) {
  const key = genreKeyForCase(item)
  if (key === 'xianxia') return IMAGES.covers[3]
  if (key === 'romance') return IMAGES.covers[4]
  if (key === 'scifi') return IMAGES.covers[5]
  if (key === 'suspense') return IMAGES.covers[6]
  if (key === 'history') return IMAGES.covers[7]
  if (key === 'warrior') return IMAGES.covers[1]
  if (key === 'reborn') return IMAGES.covers[2]
  if (key === 'urban') return IMAGES.covers[0]
  return IMAGES.covers[index % 3]
}

/** 绝对 URL OG 图：优先题材 1200×630 分享图，缺省回退站点默认图。 */
export function ogImageForCase(item, index = 0) {
  const key = genreKeyForCase(item)
  if (key && IMAGES.ogGenre[key]) return `https://lyread.cn${IMAGES.ogGenre[key]}`
  const path = coverForCase(item, index)
  if (path.endsWith('.svg')) return `https://lyread.cn${IMAGES.ogShare}`
  return `https://lyread.cn${path}`
}
