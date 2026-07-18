/** 站点静态图片路径（public/images） */
export const IMAGES = {
  logo: '/images/logo-icon.webp',
  hero: '/images/hero-banner.webp',
  point: '/images/icon-point.webp',
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
}

export function coverForCase(item, index = 0) {
  const cat = String(item?.category || '').toLowerCase()
  if (/仙侠|玄幻|修仙/.test(cat)) return IMAGES.covers[0]
  if (/战神|都市|神豪/.test(cat)) return IMAGES.covers[1]
  if (/重生|穿越/.test(cat)) return IMAGES.covers[2]
  return IMAGES.covers[index % IMAGES.covers.length]
}
