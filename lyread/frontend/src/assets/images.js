/** 站点静态图片路径（public/images） */
export const IMAGES = {
  logo: '/images/logo-icon.webp',
  hero: '/images/hero-banner.webp',
  workspace: '/images/workspace-banner.webp',
  emptyCreate: '/images/empty-create.webp',
  point: '/images/icon-point.webp',
  fire: '/images/icon-fire.webp',
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
    '/images/cover-xianxia.svg',
    '/images/cover-romance.svg',
  ],
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
    signup: '/images/icon-gift.webp',
    daily: '/images/icon-daily.webp',
    recharge: '/images/icon-gem.webp',
    refund: '/images/icon-credits.webp',
    spend: '/images/icon-point.webp',
    reserve: '/images/icon-point.webp',
  },
}

export function coverForCase(item, index = 0) {
  const cat = String(item?.category || '').toLowerCase()
  if (/仙侠|玄幻|修仙/.test(cat)) return IMAGES.covers[3]
  if (/言情|甜宠|恋爱/.test(cat)) return IMAGES.covers[4]
  if (/战神|都市|神豪/.test(cat)) return IMAGES.covers[1]
  if (/重生|穿越/.test(cat)) return IMAGES.covers[2]
  return IMAGES.covers[index % 3]
}
