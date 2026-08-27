<template>
  <div class="stat-card" :style="{ borderTop: `3px solid ${color}` }">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value num">{{ formattedValue }}</div>
    <div v-if="unit" class="stat-unit">{{ unit }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  unit: { type: String, default: '' },
  color: { type: String, default: '#0071E3' },
  decimals: { type: Number, default: 2 },
})

const formattedValue = computed(() => {
  const v = Number(props.value)
  if (isNaN(v)) return props.value
  return v.toLocaleString('zh-CN', {
    minimumFractionDigits: props.decimals,
    maximumFractionDigits: props.decimals,
  })
})
</script>

<style scoped>
.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04);
  transition: box-shadow 0.3s ease;
}
.stat-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.06);
}
.stat-label {
  font-size: 14px;
  color: #6E6E73;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 36px;
  font-weight: 700;
  line-height: 1.1;
  color: #1D1D1F;
}
.stat-unit {
  font-size: 12px;
  color: #86868B;
  margin-top: 4px;
}
</style>
