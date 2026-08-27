<template>
  <div class="chart-card">
    <div v-if="title" class="chart-card-title">
      <span class="title-bar"></span>
      <span>{{ title }}</span>
    </div>
    <div ref="chartRef" class="chart-container" :style="{ height: height + 'px' }"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  title: { type: String, default: '' },
  option: { type: Object, default: () => ({}) },
  height: { type: Number, default: 300 },
})

const chartRef = ref(null)
let chart = null

onMounted(() => {
  chart = echarts.init(chartRef.value)
  if (props.option && Object.keys(props.option).length > 0) {
    chart.setOption(props.option)
  }
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.dispose()
    chart = null
  }
})

watch(() => props.option, (val) => {
  if (chart && val) {
    chart.setOption(val, true)
  }
}, { deep: true })

function handleResize() {
  if (chart) chart.resize()
}

defineExpose({ getChart: () => chart })
</script>

<style scoped>
.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04);
}
.chart-card-title {
  font-size: 17px;
  font-weight: 500;
  color: #1D1D1F;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.title-bar {
  width: 4px;
  height: 20px;
  background: #0071E3;
  border-radius: 2px;
}
.chart-container {
  width: 100%;
}
</style>
