<template>
  <div>
    <PageHeader title="单元环比" />
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="用能单元"><el-tree-select v-model="query.unit_id" :data="unitTree" :props="{label:'name',value:'id',children:'children'}" placeholder="请选择" clearable check-strictly style="width:180px" /></el-form-item>
        <el-form-item label="统计维度"><el-select v-model="query.stat_type" style="width:120px"><el-option label="能耗" value="consumption" /><el-option label="标准煤" value="standard_coal" /><el-option label="碳排放" value="carbon_emission" /></el-select></el-form-item>
        <el-form-item label="本期"><el-date-picker v-model="period1" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:260px" /></el-form-item>
        <el-form-item label="上期"><el-date-picker v-model="period2" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:260px" /></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData" :disabled="!query.unit_id">环比分析</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card shadow="never" style="margin-bottom:16px"><ChartCard title="本期 vs 上期" :option="chartOption" :height="300" /></el-card>
    <el-card shadow="never">
      <el-table :data="tableData" border stripe>
        <el-table-column prop="label" label="周期" /><el-table-column prop="value" label="数值" align="right"><template #default="{row}"><span class="num">{{ row.value.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="diff" label="差值" align="right"><template #default="{row}"><span class="num">{{ row.diff.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="ratio" label="环比" align="right"><template #default="{row}"><span :style="{color:row.ratio>0?'#FF3B30':'#34C759'}">{{ row.ratio }}%</span></template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getUnitStat, getEnergyUnitTree } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import ChartCard from '../../components/ChartCard.vue'

const unitTree = ref([]); const period1 = ref(null); const period2 = ref(null)
const value1 = ref(0); const value2 = ref(0)
const query = reactive({ unit_id: null, stat_type: 'consumption', period: 'month' })

const diff = computed(() => +(value1.value - value2.value).toFixed(4))
const ratio = computed(() => value2.value ? +((value1.value - value2.value) / value2.value * 100).toFixed(2) : 0)
const tableData = computed(() => [{ label: '本期', value: value1.value, diff: diff.value, ratio: ratio.value }, { label: '上期', value: value2.value, diff: 0, ratio: 0 }])

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['本期', '上期'], axisLabel: { color: '#6E6E73' } },
  yAxis: { type: 'value', axisLabel: { color: '#6E6E73' }, splitLine: { lineStyle: { type: 'dashed', color: '#E8E8ED' } } },
  grid: { left: '3%', right: '3%', bottom: '3%', containLabel: true },
  series: [{ type: 'bar', data: [value1.value, value2.value], barWidth: '40%', itemStyle: { color: '#0071E3', borderRadius: [4,4,0,0] } }],
}))

async function fetchData() {
  if (!query.unit_id || !period1.value || !period2.value) return
  try {
    const [r1, r2] = await Promise.all([
      getUnitStat({unit_id:query.unit_id, stat_type:query.stat_type, period:'day', start_date:period1.value[0], end_date:period1.value[1]}),
      getUnitStat({unit_id:query.unit_id, stat_type:query.stat_type, period:'day', start_date:period2.value[0], end_date:period2.value[1]})
    ])
    value1.value = r1.data.total||0; value2.value = r2.data.total||0
  } catch(e) {}
}

onMounted(async () => { try { const r = await getEnergyUnitTree(); unitTree.value = r.data } catch(e) {} })
</script>
