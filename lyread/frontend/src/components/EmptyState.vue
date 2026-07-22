<template>
  <div class="empty-state">
    <img v-if="image" :src="image" :alt="imageAlt || title || '插图'" class="empty-state__img" :width="imageWidth" loading="lazy" />
    <h3 v-if="title" class="empty-state__title">{{ title }}</h3>
    <p v-if="description" class="empty-state__desc">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  image: { type: String, default: '' },
  imageAlt: { type: String, default: '' },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  imageWidth: { type: Number, default: 200 },
})
</script>

<style scoped>
.empty-state {
  text-align: center;
  padding: 32px 20px;
}
.empty-state__img {
  display: block;
  margin: 0 auto 16px;
  max-width: 100%;
  height: auto;
  object-fit: contain;
  border-radius: 12px;
}
.empty-state__title {
  font-size: 18px;
  color: #1e2a3a;
  margin: 0 0 8px;
  font-weight: 700;
}
.empty-state__desc {
  font-size: 14px;
  color: #5a6a7a;
  margin: 0 0 16px;
  line-height: 1.5;
}
</style>
