<template>
  <div>
    <PageHeader title="综合能耗" />
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="用能单元">
          <el-tree-select v-model="query.unit_id" :data="unitTree" :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="全部" clearable check-strictly style="width:200px" />
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束"
            value-format="YYYY-MM-DD" style="width:260px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6"><StatCard label="总能耗(折标煤)" :value="data.total_standard_coal" unit="kgce" color="#0071E3" :decimals="4" /></el-col>
      <el-col :span="6"><StatCard label="总费用" :value="data.total_cost" unit="元" color="#34C759" /></el-col>
      <el-col :span="6"><StatCard label="总碳排放" :value="data.total_carbon_emission" unit="tCO₂e" color="#FF9500" :decimals="6" /></el-col>
      <el-col :span="6"><StatCard label="能源类型" :value="data.energy_type_count" unit="种" color="#AF52DE" :decimals="0" /></el-col>
    </el-row>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="12"><ChartCard title="各能源类型消耗对比" :option="barOption" :height="300" /></el-col>
      <el-col :span="12"><ChartCard title="能源消费结构" :option="pieOption" :height="300" /></el-col>
    </el-row>
    <el-card shadow="never">
      <el-table :data="data.energy_stats" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="energy_type_name" label="能源类型" />
        <el-table-column prop="consumption" label="消耗量" align="right">
          <template #default="{ row }"><span class="num">{{ row.consumption.toLocaleString('zh-CN', { minimumFractionDigits: 4 }) }}</span></template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="cost" label="费用(元)" align="right">
          <template #default="{ row }"><span class="num">{{ row.cost.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</span></template>
        </el-table-column>
        <el-table-column prop="standard_coal" label="折标煤(kgce)" align="right">
          <template #default="{ row }"><span class="num">{{ row.standard_coal.toLocaleString('zh-CN', { minimumFractionDigits: 4 }) }}</span></template>
        </el-table-column>
        <el-table-column prop="carbon_emission" label="碳排放(tCO₂e)" align="right">
          <template #default="{ row }"><span class="num">{{ row.carbon_emission.toLocaleString('zh-CN', { minimumFractionDigits: 6 }) }}</span></template>
        </el-table-column>
        <el-table-column prop="percentage" label="占比" align="right">
          <template #default="{ row }">{{ row.percentage }}%</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { getComprehensive, getEnergyUnitTree } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'
import ChartCard from '../../components/ChartCard.vue'

const loading = ref(false)
const unitTree = ref([])
const dateRange = ref(null)
const query = reactive({ unit_id: null })
const data = reactive({ total_consumption: 0, total_cost: 0, total_standard_coal: 0, total_carbon_emission: 0, energy_type_count: 0, energy_stats: [] })

watch(dateRange, v => {
  query.start_date = v ? v[0] : null
  query.end_date = v ? v[1] : null
})

const barOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: data.energy_stats.map(i => i.energy_type_name), axisLabel: { color: '#6E6E73' } },
  yAxis: { type: 'value', axisLabel: { color: '#6E6E73' }, splitLine: { lineStyle: { type: 'dashed', color: '#E8E8ED' } } },
  grid: { left: '3%', right: '3%', bottom: '3%', containLabel: true },
  series: [{ type: 'bar', data: data.energy_stats.map(i => i.standard_coal), barWidth: '40%', itemStyle: { color: '#0071E3', borderRadius: [4, 4, 0, 0] } }],
}))

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
  legend: { bottom: 0, textStyle: { color: '#6E6E73' } },
  series: [{ type: 'pie', radius: ['45%', '70%'], data: data.energy_stats.map(i => ({ name: i.energy_type_name, value: i.consumption })), itemStyle: { borderRadius: 4 } }],
  color: ['#0071E3', '#34C759', '#FF9500', '#AF52DE', '#FF2D55', '#5AC8FA'],
}))

async function fetchData() {
  loading.value = true
  try {
    const res = await getComprehensive(query)
    Object.assign(data, res.data)
  } catch (e) {} finally { loading.value = false }
}

onMounted(async () => {
  try { const res = await getEnergyUnitTree(); unitTree.value = res.data } catch (e) {}
  fetchData()
})
</script>
