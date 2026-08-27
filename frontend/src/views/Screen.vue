<template>
  <div class="screen" @keyup.esc="exitScreen">
    <div class="screen-header">
      <div class="screen-title">⚡ {{ orgName }} · 数字化能碳管理指挥中心</div>
      <div class="screen-time">{{ currentTime }}</div>
    </div>
    <div class="screen-body">
      <div class="screen-left">
        <div class="screen-card">
          <div class="card-title">实时能耗指标</div>
          <div class="metric-grid">
            <div class="metric-item"><div class="metric-label">今日能耗</div><div class="metric-value num">{{ data.today_energy }}</div><div class="metric-unit">kgce</div></div>
            <div class="metric-item"><div class="metric-label">本月能耗</div><div class="metric-value num">{{ data.month_energy }}</div><div class="metric-unit">kgce</div></div>
            <div class="metric-item"><div class="metric-label">本年能耗</div><div class="metric-value num">{{ data.year_energy }}</div><div class="metric-unit">kgce</div></div>
            <div class="metric-item"><div class="metric-label">本月碳排放</div><div class="metric-value num">{{ data.month_carbon }}</div><div class="metric-unit">tCO₂e</div></div>
          </div>
        </div>
        <div class="screen-card">
          <div class="card-title">设备状态</div>
          <div class="metric-grid">
            <div class="metric-item"><div class="metric-label">在线设备</div><div class="metric-value" style="color:#34C759">{{ data.active_meters }}</div></div>
            <div class="metric-item"><div class="metric-label">离线设备</div><div class="metric-value" style="color:#FF3B30">{{ data.offline_meters }}</div></div>
          </div>
        </div>
        <div class="screen-card" style="flex:1">
          <div class="card-title">能源类型占比</div>
          <div ref="energyPieRef" style="width:100%;height:200px"></div>
        </div>
      </div>
      <div class="screen-center">
        <div class="screen-card" style="flex:1">
          <div class="card-title">月度能耗趋势</div>
          <div ref="trendRef" style="width:100%;height:300px"></div>
        </div>
        <div class="screen-card" style="flex:1">
          <div class="card-title">用能单元排行</div>
          <div ref="rankRef" style="width:100%;height:250px"></div>
        </div>
      </div>
      <div class="screen-right">
        <div class="screen-card">
          <div class="card-title">碳排放范围分布</div>
          <div ref="scopePieRef" style="width:100%;height:200px"></div>
        </div>
        <div class="screen-card">
          <div class="card-title">碳排放指标</div>
          <div class="metric-grid">
            <div class="metric-item"><div class="metric-label">范围1</div><div class="metric-value num" style="color:#FF3B30">{{ stats.scope1 }}</div><div class="metric-unit">tCO₂e</div></div>
            <div class="metric-item"><div class="metric-label">范围2</div><div class="metric-value num" style="color:#FF9500">{{ stats.scope2 }}</div><div class="metric-unit">tCO₂e</div></div>
          </div>
        </div>
        <div class="screen-card" style="flex:1">
          <div class="card-title">能效雷达</div>
          <div ref="radarRef" style="width:100%;height:250px"></div>
        </div>
      </div>
    </div>
    <div class="screen-footer">
      <div class="scroll-bar">
        <span v-for="(item, i) in scrollItems" :key="i" class="scroll-item">{{ item }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getRealtimeData, getDashboardStats } from '../api'

const orgName = ref('示例制造有限公司')
const currentTime = ref('')
const data = reactive({ today_energy: 0, month_energy: 0, year_energy: 0, month_carbon: 0, active_meters: 0, offline_meters: 0, unit_ranking: [] })
const stats = reactive({ scope1: 0, scope2: 0, scope3: 0, energy_stats: [], carbon_monthly: [] })
const scrollItems = ref(['系统运行正常', '数据每30秒自动刷新', '按ESC退出全屏'])

const energyPieRef = ref(null)
const trendRef = ref(null)
const rankRef = ref(null)
const scopePieRef = ref(null)
const radarRef = ref(null)

let charts = []
let timer = null
let timeTimer = null

function updateTime() {
  currentTime.value = new Date().toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function initCharts() {
  const theme = { backgroundColor: 'transparent', textStyle: { color: '#D2D2D7' } }

  // 能源占比饼图
  const c1 = echarts.init(energyPieRef.value)
  c1.setOption({ ...theme, tooltip: { trigger: 'item' }, series: [{ type: 'pie', radius: ['40%', '65%'], data: stats.energy_stats.map(i => ({ name: i.name, value: i.value })), label: { color: '#D2D2D7', fontSize: 11 }, itemStyle: { borderRadius: 4 } }], color: ['#0071E3', '#34C759', '#FF9500', '#AF52DE', '#FF2D55', '#5AC8FA'] })
  charts.push(c1)

  // 月度趋势
  const c2 = echarts.init(trendRef.value)
  c2.setOption({
    ...theme, tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: stats.carbon_monthly.map(i => i.month), axisLine: { lineStyle: { color: '#3A3A3C' } }, axisLabel: { color: '#86868B' } },
    yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: '#2A2A2C' } }, axisLabel: { color: '#86868B' } },
    grid: { left: '5%', right: '5%', bottom: '5%', containLabel: true },
    series: [{ type: 'line', smooth: true, data: stats.carbon_monthly.map(i => i.emission), lineStyle: { color: '#0071E3', width: 2 }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,113,227,0.3)' }, { offset: 1, color: 'rgba(0,113,227,0)' }] } }, itemStyle: { color: '#0071E3' } }],
  })
  charts.push(c2)

  // 单元排行
  const c3 = echarts.init(rankRef.value)
  const sorted = data.unit_ranking || []
  c3.setOption({
    ...theme, tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: '#2A2A2C' } }, axisLabel: { color: '#86868B' } },
    yAxis: { type: 'category', data: sorted.map(i => i.name).reverse(), axisLabel: { color: '#D2D2D7' } },
    grid: { left: '5%', right: '5%', bottom: '5%', containLabel: true },
    series: [{ type: 'bar', data: sorted.map(i => i.value).reverse(), barWidth: '40%', itemStyle: { color: '#0071E3', borderRadius: [0, 4, 4, 0] } }],
  })
  charts.push(c3)

  // 碳范围饼图
  const c4 = echarts.init(scopePieRef.value)
  c4.setOption({
    ...theme, tooltip: { trigger: 'item' },
    series: [{ type: 'pie', radius: ['40%', '65%'], data: [
      { name: '范围1', value: stats.scope1 }, { name: '范围2', value: stats.scope2 }, { name: '范围3', value: stats.scope3 },
    ], label: { color: '#D2D2D7', fontSize: 11 }, itemStyle: { borderRadius: 4 } }],
    color: ['#FF3B30', '#FF9500', '#34C759'],
  })
  charts.push(c4)

  // 雷达图
  const c5 = echarts.init(radarRef.value)
  c5.setOption({
    ...theme, tooltip: {},
    radar: { indicator: [ { name: '能效', max: 100 }, { name: '碳强度', max: 100 }, { name: '设备完好率', max: 100 }, { name: '数据完整率', max: 100 }, { name: '预算执行', max: 100 } ], axisName: { color: '#86868B' }, splitLine: { lineStyle: { color: '#2A2A2C' } }, splitArea: { show: false } },
    series: [{ type: 'radar', data: [{ value: [75, 60, 90, 85, 80], name: '综合评分' }], areaStyle: { color: 'rgba(0,113,227,0.2)' }, lineStyle: { color: '#0071E3' }, itemStyle: { color: '#0071E3' } }],
  })
  charts.push(c5)
}

async function loadData() {
  try {
    const [r1, r2] = await Promise.all([getRealtimeData(), getDashboardStats()])
    Object.assign(data, r1.data)
    Object.assign(stats, r2.data)
    // 重新设置图表数据
    if (charts.length >= 5) {
      charts[0].setOption({ series: [{ data: stats.energy_stats.map(i => ({ name: i.name, value: i.value })) }] })
      charts[1].setOption({ xAxis: { data: stats.carbon_monthly.map(i => i.month) }, series: [{ data: stats.carbon_monthly.map(i => i.emission) }] })
      const sorted = data.unit_ranking || []
      charts[2].setOption({ yAxis: { data: sorted.map(i => i.name).reverse() }, series: [{ data: sorted.map(i => i.value).reverse() }] })
      charts[3].setOption({ series: [{ data: [{ name: '范围1', value: stats.scope1 }, { name: '范围2', value: stats.scope2 }, { name: '范围3', value: stats.scope3 }] }] })
    }
  } catch (e) { /* ignore */ }
}

function exitScreen() {
  window.close()
}

onMounted(async () => {
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
  await loadData()
  initCharts()
  timer = setInterval(loadData, 30000)
  window.addEventListener('resize', () => charts.forEach(c => c.resize()))
})

onUnmounted(() => {
  clearInterval(timer)
  clearInterval(timeTimer)
  charts.forEach(c => c.dispose())
})
</script>

<style scoped>
.screen {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(180deg, #0A0A0A 0%, #000000 100%);
  color: #D2D2D7;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
}
.screen-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  border-bottom: 1px solid #1A1A1C;
}
.screen-title {
  font-size: 22px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 2px;
}
.screen-time {
  font-size: 16px;
  color: #86868B;
  font-variant-numeric: tabular-nums;
}
.screen-body {
  flex: 1;
  display: flex;
  gap: 16px;
  padding: 16px;
  min-height: 0;
}
.screen-left, .screen-right {
  width: 25%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.screen-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.screen-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 16px;
}
.card-title {
  font-size: 14px;
  color: #86868B;
  margin-bottom: 12px;
  font-weight: 500;
}
.metric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.metric-item {
  text-align: center;
}
.metric-label {
  font-size: 12px;
  color: #86868B;
  margin-bottom: 4px;
}
.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  font-variant-numeric: tabular-nums;
}
.metric-unit {
  font-size: 11px;
  color: #6E6E73;
  margin-top: 2px;
}
.screen-footer {
  height: 36px;
  border-top: 1px solid #1A1A1C;
  display: flex;
  align-items: center;
  overflow: hidden;
}
.scroll-bar {
  display: flex;
  gap: 48px;
  animation: scroll 20s linear infinite;
  white-space: nowrap;
}
.scroll-item {
  font-size: 13px;
  color: #86868B;
}
@keyframes scroll {
  from { transform: translateX(100vw); }
  to { transform: translateX(-100%); }
}
</style>
