<template>
  <component :is="tag" class="section-heading" :class="{ center }">
    <img v-if="icon" :src="icon" :alt="iconAlt" class="section-heading__icon" :width="iconSize" :height="iconSize" aria-hidden="true" />
    <span class="section-heading__text"><slot /></span>
  </component>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '' },
  iconAlt: { type: String, default: '' },
  iconSize: { type: Number, default: 24 },
  center: { type: Boolean, default: false },
  tag: { type: String, default: 'h2' },
})
</script>

<style scoped>
.section-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  color: #1e2a3a;
  font-size: inherit;
  font-weight: 700;
}
.section-heading.center { justify-content: center; }
.section-heading__icon { object-fit: contain; flex-shrink: 0; }
</style>
