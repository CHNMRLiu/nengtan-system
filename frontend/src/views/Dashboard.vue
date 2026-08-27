<template>
  <div class="dashboard">
    <PageHeader title="首页看板" subtitle="数字化能碳管理系统总览" />
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <StatCard :label="card.label" :value="card.value" :unit="card.unit" :color="card.color" :decimals="card.decimals" />
      </el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :span="12">
        <ChartCard title="能源消费结构" :option="energyPieOption" :height="320" />
      </el-col>
      <el-col :span="12">
        <ChartCard title="月度碳排放趋势" :option="carbonTrendOption" :height="320" />
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <ChartCard title="碳排放范围分布" :option="scopePieOption" :height="320" />
      </el-col>
      <el-col :span="12">
        <div class="info-card">
          <div class="chart-card-title"><span class="title-bar"></span><span>系统信息</span></div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="企业名称">{{ stats.org_name || '示例制造有限公司' }}</el-descriptions-item>
            <el-descriptions-item label="报告年度">{{ stats.year }}</el-descriptions-item>
            <el-descriptions-item label="碳报告状态">
              <el-tag :type="stats.report_status === '已生成' ? 'success' : 'info'">{{ stats.report_status || '未生成' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数据来源">手工录入</el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getDashboardStats } from '../api'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import ChartCard from '../components/ChartCard.vue'

const stats = reactive({
  year: new Date().getFullYear(),
  total_consumption: 0, total_cost: 0, total_standard_coal: 0, total_carbon_emission: 0,
  energy_stats: [], carbon_monthly: [], carbon_scope: { scope1: 0, scope2: 0, scope3: 0 },
  report_status: '未生成',
})

const statCards = computed(() => [
  { label: '年度总能耗(折标煤)', value: stats.total_standard_coal, unit: 'kgce', color: '#0071E3', decimals: 4 },
  { label: '年度总费用', value: stats.total_cost, unit: '元', color: '#34C759', decimals: 2 },
  { label: '年度碳排放', value: stats.total_carbon_emission, unit: 'tCO₂e', color: '#FF9500', decimals: 6 },
  { label: '能源类型数', value: stats.energy_stats.length, unit: '种', color: '#AF52DE', decimals: 0 },
])

const energyPieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} kgce ({d}%)' },
  legend: { bottom: 0, textStyle: { color: '#6E6E73', fontSize: 12 } },
  series: [{
    type: 'pie', radius: ['45%', '70%'], center: ['50%', '45%'],
    label: { show: true, formatter: '{b}\n{d}%', fontSize: 12 },
    data: stats.energy_stats.map(i => ({ name: i.name, value: i.value })),
    itemStyle: { borderRadius: 4 },
  }],
  color: ['#0071E3', '#34C759', '#FF9500', '#AF52DE', '#FF2D55', '#5AC8FA'],
}))

const carbonTrendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: stats.carbon_monthly.map(i => i.month), axisLine: { lineStyle: { color: '#D2D2D7' } }, axisLabel: { color: '#6E6E73' } },
  yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { type: 'dashed', color: '#E8E8ED' } }, axisLabel: { color: '#6E6E73' } },
  grid: { left: '3%', right: '3%', bottom: '3%', containLabel: true },
  series: [{
    type: 'line', smooth: true, data: stats.carbon_monthly.map(i => i.emission),
    lineStyle: { color: '#0071E3', width: 2 },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(0,113,227,0.15)' }, { offset: 1, color: 'rgba(0,113,227,0)' }] } },
    itemStyle: { color: '#0071E3' },
  }],
}))

const scopePieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂e ({d}%)' },
  legend: { bottom: 0, textStyle: { color: '#6E6E73', fontSize: 12 } },
  series: [{
    type: 'pie', radius: ['45%', '70%'], center: ['50%', '45%'],
    data: [
      { name: '范围1(直接排放)', value: stats.carbon_scope.scope1 },
      { name: '范围2(外购能源)', value: stats.carbon_scope.scope2 },
      { name: '范围3(其他间接)', value: stats.carbon_scope.scope3 },
    ],
    itemStyle: { borderRadius: 4 },
  }],
  color: ['#FF3B30', '#FF9500', '#34C759'],
}))

onMounted(async () => {
  try {
    const res = await getDashboardStats()
    Object.assign(stats, res.data)
  } catch (e) { /* ignore */ }
})
</script>

<style scoped>
.info-card {
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
</style>
