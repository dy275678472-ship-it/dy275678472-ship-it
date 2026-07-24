<template>
  <div class="avatar-badge" :style="{ background: bg }" :aria-label="label">
    <span>{{ initial }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, default: '用户' },
  color: { type: String, default: '#2563eb' },
  altColor: { type: String, default: '#4da1ff' },
})

const initial = computed(() => (props.label.trim()[0] || '用'))
const bg = computed(() => `linear-gradient(135deg, ${props.color}, ${props.altColor})`)
</script>

<style scoped>
.avatar-badge {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}
</style>
