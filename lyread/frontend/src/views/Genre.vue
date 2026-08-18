<template>
  <div class="genre-page">
    <header class="genre-hero">
      <h1>AI 小说题材聚合</h1>
      <p class="lede">按都市神豪、战神归来、系统流等题材挑开篇——读完可用同风格开写，游客先注册领 30 点。</p>
    </header>

    <section class="genre-lens" aria-label="怎么用题材枢纽">
      <h2>怎么用题材枢纽</h2>
      <ol>
        <li><strong>选题材</strong> — 先锁定合胃口的网文赛道与核心爽点。</li>
        <li><strong>看案例</strong> — 进入叶子页浏览同题材公开开篇与热度。</li>
        <li><strong>同风开写</strong> — 满意就注册回流创作台，用该题材新建长篇。</li>
        <li><strong>短篇试手</strong> — 想先练手，可去短故事页快速出一篇。</li>
      </ol>
    </section>

    <!-- 次屏转化：扫完用法后立刻 register-first，避免裸 /workspace -->
    <section class="genre-mid-cta" aria-label="开始创作">
      <p class="mid-kicker">注册送 30 点 · 失败不扣点</p>
      <div class="mid-actions">
        <router-link
          v-if="!isLoggedIn"
          class="btn primary"
          :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
          @click="track('genre_mid_register')"
        >免费注册开写 →</router-link>
        <router-link
          v-else
          class="btn primary"
          :to="{ path: '/workspace', query: { mode: 'new' } }"
          @click="track('genre_mid_workspace')"
        >进入创作台 →</router-link>
        <router-link
          class="btn"
          to="/trending"
          @click="track('genre_mid_trending')"
        >热门案例</router-link>
        <router-link
          class="btn"
          to="/story"
          @click="track('genre_mid_story')"
        >试试短故事</router-link>
      </div>
    </section>

    <section class="genre-list" aria-label="全部题材">
      <h2>全部题材</h2>
      <ul>
        <li v-for="item in genres" :key="item.slug">
          <!-- 叶子页仍走完整刷新 SSR，保留爬虫正文与案例列表 -->
          <a
            :href="`/genre/${item.slug}`"
            @click="track('genre_leaf_click', item.slug)"
          >
            <span class="name">{{ item.category }}</span>
            <span class="intro">{{ item.intro }}</span>
          </a>
        </li>
      </ul>
    </section>

    <section class="genre-bottom" aria-label="下一步">
      <router-link to="/ep" class="text-link" @click="track('genre_ep')">作品索引</router-link>
      <span class="sep">·</span>
      <router-link to="/pricing" class="text-link" @click="track('genre_pricing')">查看价格</router-link>
      <span class="sep">·</span>
      <router-link to="/guide" class="text-link" @click="track('genre_guide')">创作教程</router-link>
      <span class="sep">·</span>
      <router-link
        v-if="!isLoggedIn"
        class="text-link strong"
        :to="{ path: '/login', query: { mode: 'register', redirect: '/workspace?mode=new' } }"
        @click="track('genre_bottom_register')"
      >免费注册（送 30 点）</router-link>
      <router-link
        v-else
        class="text-link strong"
        :to="{ path: '/workspace', query: { mode: 'new' } }"
        @click="track('genre_bottom_workspace')"
      >去创作台</router-link>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { trackEvent } from '../utils/analytics'

/** 与 backend GENRE_PAGES 口径对齐，便于 SPA / SSR 一致 */
const genres = [
  { slug: 'dushi', category: '都市神豪', intro: '身份反转、财富碾压与打脸逆袭' },
  { slug: 'zhanshen', category: '战神归来', intro: '归来打脸、护女护家，开篇冲突强' },
  { slug: 'chongsheng', category: '重生', intro: '先知先觉逆袭，商业与人生改写' },
  { slug: 'xianxia', category: '仙侠玄幻', intro: '境界体系与修炼升级，适合日更' },
  { slug: 'yanqing', category: '言情甜宠', intro: '感情线与虐甜节奏，短长篇皆宜' },
  { slug: 'xuanyi', category: '悬疑推理', intro: '伏笔布局与线索管理要求高' },
  { slug: 'xitong', category: '系统流', intro: '任务奖励升级，节奏快爽点密' },
  { slug: 'duanpian', category: '短篇故事', intro: '结构完整、反转有力的短篇赛道' },
  { slug: 'moshi', category: '末世求生', intro: '囤货与异能，开局节奏要快' },
  { slug: 'gongting', category: '宫廷权谋', intro: '人物关系网与权谋伏笔' },
  { slug: 'saibo', category: '赛博朋克', intro: '高科技低生活与反乌托邦叙事' },
  { slug: 'zhuixu', category: '赘婿逆袭', intro: '隐忍后爆发，打脸节点要清晰' },
  { slug: 'kehuan', category: '科幻脑洞', intro: '星际末世等新设定与世界观' },
  { slug: 'xiaoyuan', category: '校园青春', intro: '学霸逆袭、校草甜宠与青春节奏' },
  { slug: 'youxi', category: '游戏竞技', intro: '电竞复出、隐藏职业等高光操作' },
  { slug: 'lishi', category: '历史架空', intro: '穿越权谋，兼顾史实与爽点' },
  { slug: 'mengbao', category: '萌宝甜宠', intro: '萌宝助攻与追妻火葬场' },
  { slug: 'lingyi', category: '灵异悬疑', intro: '氛围与线索一致性是关键' },
]

const isLoggedIn = computed(() => !!localStorage.getItem('token'))

function track(name, label = 'genre_spa') {
  trackEvent(name, { category: 'conversion', label })
}

onMounted(() => {
  trackEvent('genre_view', { category: 'engagement', label: 'spa' })
})
</script>

<style scoped>
.genre-page {
  max-width: 720px;
  margin: 0 auto;
  padding: 28px 20px 56px;
  color: #1e2a3a;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(74, 144, 217, 0.12), transparent 60%),
    linear-gradient(180deg, #f7fafc 0%, #eef3f9 100%);
  min-height: calc(100vh - 120px);
}
.genre-hero {
  text-align: center;
  margin-bottom: 24px;
}
.genre-hero h1 {
  font-size: 28px;
  margin: 0 0 10px;
  letter-spacing: 0.02em;
}
.lede {
  margin: 0 auto;
  max-width: 34em;
  font-size: 15px;
  line-height: 1.65;
  color: #5a6a7a;
}
.genre-lens h2,
.genre-list h2 {
  font-size: 18px;
  margin: 0 0 12px;
}
.genre-lens ol {
  margin: 0;
  padding-left: 1.25em;
  font-size: 14px;
  line-height: 1.75;
  color: #5a6a7a;
}
.genre-lens li {
  margin-bottom: 8px;
}
.genre-lens strong {
  color: #1e2a3a;
}
.genre-mid-cta {
  margin: 28px 0;
  padding: 20px 18px;
  text-align: center;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(218, 230, 245, 0.9);
  border-radius: 12px;
}
.mid-kicker {
  margin: 0 0 14px;
  font-size: 14px;
  color: #4a90d9;
  font-weight: 600;
}
.mid-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}
.btn {
  display: inline-block;
  padding: 10px 18px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  color: #357abd;
  background: #e8f0fe;
  border: 1px solid #d0e0f5;
}
.btn.primary {
  color: #fff;
  background: linear-gradient(135deg, #4a90d9 0%, #357abd 100%);
  border-color: transparent;
}
.genre-list ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.genre-list li {
  margin-bottom: 10px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(218, 230, 245, 0.9);
  border-radius: 10px;
}
.genre-list a {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #1e2a3a;
  text-decoration: none;
}
.genre-list a:hover .name {
  color: #357abd;
}
.genre-list .name {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.5;
}
.genre-list .intro {
  font-size: 13px;
  color: #7a8ba8;
  line-height: 1.5;
}
.genre-bottom {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #7a8ba8;
}
.text-link {
  color: #357abd;
  text-decoration: none;
}
.text-link.strong {
  font-weight: 600;
}
.sep {
  margin: 0 6px;
}
@media (max-width: 560px) {
  .mid-actions { flex-direction: column; }
  .btn { width: 100%; text-align: center; box-sizing: border-box; }
}
</style>
