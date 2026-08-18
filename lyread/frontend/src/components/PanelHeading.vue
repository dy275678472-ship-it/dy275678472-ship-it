<template>
  <div class="panel-heading">
    <img v-if="icon" :src="icon" :alt="iconAlt" class="panel-heading__icon" width="20" height="20" aria-hidden="true" />
    <h3 class="panel-heading__title"><slot /></h3>
  </div>
</template>

<script setup>
defineProps({ icon: { type: String, default: '' }, iconAlt: { type: String, default: '' } })
</script>

<style scoped>
.panel-heading {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.panel-heading__title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #1e2a3a;
}
.panel-heading__icon { object-fit: contain; }
</style>
