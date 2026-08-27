<template>
  <div class="page-header">
    <div class="page-header-left">
      <h1 class="page-title">{{ title }}</h1>
      <span v-if="subtitle" class="page-subtitle">{{ subtitle }}</span>
    </div>
    <div class="page-header-right">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-title {
  font-size: 32px;
  font-weight: 600;
  line-height: 1.2;
  color: #1D1D1F;
}
.page-subtitle {
  font-size: 14px;
  color: #6E6E73;
  margin-top: 4px;
  display: block;
}
.page-header-right {
  display: flex;
  gap: 8px;
}
</style>
