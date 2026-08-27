<template>
  <div>
    <PageHeader title="计量对标" />
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="表计A"><el-select v-model="query.meter_a" placeholder="请选择" clearable filterable style="width:180px"><el-option v-for="m in meters" :key="m.id" :label="m.name" :value="m.id" /></el-select></el-form-item>
        <el-form-item label="表计B"><el-select v-model="query.meter_b" placeholder="请选择" clearable filterable style="width:180px"><el-option v-for="m in meters" :key="m.id" :label="m.name" :value="m.id" /></el-select></el-form-item>
        <el-form-item label="统计维度">
          <el-select v-model="query.stat_type" style="width:120px"><el-option label="能耗" value="consumption" /><el-option label="标准煤" value="standard_coal" /><el-option label="碳排放" value="carbon_emission" /></el-select>
        </el-form-item>
        <el-form-item label="日期范围"><el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:260px" /></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData" :disabled="!query.meter_a||!query.meter_b">对比分析</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card shadow="never" style="margin-bottom:16px"><ChartCard title="双表计对比" :option="chartOption" :height="350" /></el-card>
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
import { getMeterQuery, getMeters } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import ChartCard from '../../components/ChartCard.vue'

const meters = ref([]); const dateRange = ref(null)
const nameA = ref('表计A'); const nameB = ref('表计B')
const itemsA = ref([]); const itemsB = ref([])
const query = reactive({ meter_a: null, meter_b: null, stat_type: 'consumption', period: 'month' })
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
  if (!query.meter_a || !query.meter_b) return
  try {
    const [r1, r2] = await Promise.all([getMeterQuery({meter_id:query.meter_a,...query}), getMeterQuery({meter_id:query.meter_b,...query})])
    nameA.value = r1.data.meter_name; nameB.value = r2.data.meter_name
    itemsA.value = r1.data.items||[]; itemsB.value = r2.data.items||[]
  } catch(e) {}
}

onMounted(async () => { try { const r = await getMeters({page_size:999}); meters.value = r.data||[] } catch(e) {} })
</script>
