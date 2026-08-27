<template>
  <div>
    <PageHeader title="单元对标" />
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="单元A"><el-tree-select v-model="query.unit_a" :data="unitTree" :props="{label:'name',value:'id',children:'children'}" placeholder="请选择" check-strictly style="width:180px" /></el-form-item>
        <el-form-item label="单元B"><el-tree-select v-model="query.unit_b" :data="unitTree" :props="{label:'name',value:'id',children:'children'}" placeholder="请选择" check-strictly style="width:180px" /></el-form-item>
        <el-form-item label="统计维度"><el-select v-model="query.stat_type" style="width:120px"><el-option label="能耗" value="consumption" /><el-option label="标准煤" value="standard_coal" /><el-option label="碳排放" value="carbon_emission" /></el-select></el-form-item>
        <el-form-item label="日期范围"><el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:260px" /></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData" :disabled="!query.unit_a||!query.unit_b">对比分析</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card shadow="never" style="margin-bottom:16px"><ChartCard title="双单元对比" :option="chartOption" :height="350" /></el-card>
    <el-card shadow="never">
      <el-table :data="tableData" border stripe>
        <el-table-column prop="time" label="时间" />
        <el-table-column prop="valueA" :label="nameA" align="right"><template #default="{row}"><span class="num">{{ row.valueA.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="valueB" :label="nameB" align="right"><template #default="{row}"><span class="num">{{ row.valueB.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="diff" label="差值" align="right"><template #default="{row}"><span class="num">{{ row.diff.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="diffRate" label="差值率" align="right"><template #default="{row}">{{ row.diffRate }}%</template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { getUnitStat, getEnergyUnitTree } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import ChartCard from '../../components/ChartCard.vue'

const unitTree = ref([]); const dateRange = ref(null)
const nameA = ref('单元A'); const nameB = ref('单元B')
const itemsA = ref([]); const itemsB = ref([])
const query = reactive({ unit_a: null, unit_b: null, stat_type: 'consumption', period: 'month' })
watch(dateRange, v => { query.start_date = v?v[0]:null; query.end_date = v?v[1]:null })

const tableData = computed(() => {
  const map = {}
  itemsA.value.forEach(i => { map[i.time] = { time: i.time, valueA: i[query.stat_type]||0, valueB: 0 } })
  itemsB.value.forEach(i => { if (!map[i.time]) map[i.time] = { time: i.time, valueA: 0 }; map[i.time].valueB = i[query.stat_type]||0 })
  return Object.values(map).map(i => ({ ...i, diff: +(i.valueA - i.valueB).toFixed(4), diffRate: i.valueB ? ((i.valueA - i.valueB) / i.valueB * 100).toFixed(2) : '0.00' }))
})

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis' }, legend: { bottom: 0, data: [nameA.value, nameB.value], textStyle: { color: '#6E6E73' } },
  xAxis: { type: 'category', data: tableData.value.map(i=>i.time), axisLabel: { color: '#6E6E73' } },
  yAxis: { type: 'value', axisLabel: { color: '#6E6E73' }, splitLine: { lineStyle: { type: 'dashed', color: '#E8E8ED' } } },
  grid: { left: '3%', right: '3%', bottom: '10%', containLabel: true },
  series: [
    { name: nameA.value, type: 'line', smooth: true, data: tableData.value.map(i=>i.valueA), lineStyle: { color: '#0071E3' }, itemStyle: { color: '#0071E3' } },
    { name: nameB.value, type: 'line', smooth: true, data: tableData.value.map(i=>i.valueB), lineStyle: { color: '#34C759' }, itemStyle: { color: '#34C759' } },
  ],
}))

async function fetchData() {
  if (!query.unit_a || !query.unit_b) return
  try {
    const [r1, r2] = await Promise.all([
      getUnitStat({unit_id:query.unit_a, stat_type:query.stat_type, period:'month', start_date:query.start_date, end_date:query.end_date}),
      getUnitStat({unit_id:query.unit_b, stat_type:query.stat_type, period:'month', start_date:query.start_date, end_date:query.end_date})
    ])
    nameA.value = r1.data.unit_name; nameB.value = r2.data.unit_name
    itemsA.value = r1.data.items||[]; itemsB.value = r2.data.items||[]
  } catch(e) {}
}

onMounted(async () => { try { const r = await getEnergyUnitTree(); unitTree.value = r.data } catch(e) {} })
</script>
