/** 站点静态图片路径（public/images） */
export const IMAGES = {
  logo: '/images/logo-icon-v2.svg',
  logoLegacy: '/images/logo-icon.webp',
  hero: '/images/hero-banner.webp',
  workspace: '/images/workspace-banner.webp',
  emptyCreate: '/images/empty-create.webp',
  ogShare: '/images/og-share.webp',
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
    '/images/cover-xianxia.svg',
    '/images/cover-romance.svg',
    '/images/cover-scifi.svg',
    '/images/cover-suspense.svg',
    '/images/cover-history.svg',
  ],
  categoryGradients: {
    '都市神豪': { from: '#1e3a5f', to: '#4da1ff', label: '都市' },
    '战神归来': { from: '#4a1942', to: '#c026d3', label: '战神' },
    '重生': { from: '#14532d', to: '#22c55e', label: '重生' },
    '仙侠玄幻': { from: '#312e81', to: '#818cf8', label: '仙侠' },
    '言情甜宠': { from: '#9d174d', to: '#f9a8d4', label: '言情' },
    '科幻脑洞': { from: '#0f172a', to: '#38bdf8', label: '科幻' },
    '悬疑推理': { from: '#1f2937', to: '#64748b', label: '悬疑' },
    '历史架空': { from: '#78350f', to: '#fbbf24', label: '历史' },
    '系统流': { from: '#134e4a', to: '#2dd4bf', label: '系统' },
    '末世求生': { from: '#1e293b', to: '#94a3b8', label: '末世' },
    '校园青春': { from: '#0369a1', to: '#7dd3fc', label: '校园' },
    '游戏竞技': { from: '#312e81', to: '#a78bfa', label: '电竞' },
    '宫廷权谋': { from: '#7c2d12', to: '#fdba74', label: '宫廷' },
    '赘婿逆袭': { from: '#1e3a8a', to: '#60a5fa', label: '赘婿' },
    '萌宝甜宠': { from: '#be185d', to: '#fbcfe8', label: '萌宝' },
    '灵异悬疑': { from: '#111827', to: '#6b7280', label: '灵异' },
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

export function coverForCase(item, index = 0) {
  const resolved = resolveCaseCover(item, index)
  return resolved.type === 'image' ? resolved.src : ''
}

export function resolveCaseCover(item, index = 0) {
  const cat = item?.category || '都市'
  const exact = IMAGES.categoryGradients[cat]
  if (exact) {
    return {
      type: 'gradient',
      label: exact.label,
      style: { background: `linear-gradient(135deg, ${exact.from}, ${exact.to})` },
    }
  }
  const lower = String(cat).toLowerCase()
  if (/仙侠|玄幻|修仙/.test(lower)) return gradientFor('仙侠玄幻')
  if (/言情|甜宠|恋爱|萌宝/.test(lower)) return gradientFor('言情甜宠')
  if (/科幻|脑洞|末世|赛博/.test(lower)) return gradientFor('科幻脑洞')
  if (/悬疑|推理|惊悚|灵异/.test(lower)) return gradientFor('悬疑推理')
  if (/历史|架空|宫廷/.test(lower)) return gradientFor('历史架空')
  if (/战神|都市|神豪|赘婿/.test(lower)) return gradientFor('都市神豪')
  if (/重生|穿越/.test(lower)) return gradientFor('重生')
  if (/系统/.test(lower)) return gradientFor('系统流')
  if (/校园/.test(lower)) return gradientFor('校园青春')
  if (/游戏|电竞/.test(lower)) return gradientFor('游戏竞技')
  const src = IMAGES.covers[index % IMAGES.covers.length]
  if (src.endsWith('.webp')) return { type: 'image', src }
  return gradientFor('都市神豪')
}

function gradientFor(key) {
  const g = IMAGES.categoryGradients[key] || IMAGES.categoryGradients['都市神豪']
  return {
    type: 'gradient',
    label: g.label,
    style: { background: `linear-gradient(135deg, ${g.from}, ${g.to})` },
  }
}
