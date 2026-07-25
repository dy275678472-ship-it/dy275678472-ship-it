<template>
  <div class="case-cover-wrap" :style="wrapStyle">
    <span v-if="showBadge" class="excerpt-badge">节选</span>
    <img
      v-if="cover.type === 'image'"
      :src="cover.src"
      :alt="alt"
      class="case-cover-img"
      loading="lazy"
    />
    <div v-else class="case-cover-gradient" :style="cover.style">
      <span class="cover-label">{{ cover.label }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { resolveCaseCover } from '../assets/images'

const props = defineProps({
  item: { type: Object, required: true },
  index: { type: Number, default: 0 },
  alt: { type: String, default: '案例封面' },
  height: { type: String, default: '120px' },
  showBadge: { type: Boolean, default: true },
})

const cover = computed(() => resolveCaseCover(props.item, props.index))
const wrapStyle = computed(() => ({ height: props.height }))
</script>

<style scoped>
.case-cover-wrap { width: 100%; overflow: hidden; display: block; position: relative; }
.excerpt-badge {
  position: absolute; top: 8px; left: 8px; z-index: 1;
  padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 600;
  background: rgba(15, 23, 42, 0.55); color: #fff; backdrop-filter: blur(4px);
}
.case-cover-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.case-cover-gradient {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
}
.cover-label {
  font-size: 28px; font-weight: 800; color: rgba(255,255,255,0.92);
  text-shadow: 0 2px 8px rgba(0,0,0,0.15);
  letter-spacing: 0.08em;
}
</style>
