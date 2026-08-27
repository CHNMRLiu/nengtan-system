<template>
  <div>
    <PageHeader title="碳排统计" />
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="年度"><el-date-picker v-model="query.year" type="year" value-format="YYYY" placeholder="选择年度" style="width:120px" /></el-form-item>
        <el-form-item label="范围"><el-select v-model="query.scope" clearable placeholder="全部" style="width:120px"><el-option label="范围1" value="范围1" /><el-option label="范围2" value="范围2" /><el-option label="范围3" value="范围3" /></el-select></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData">查询</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6"><StatCard label="范围1(直接排放)" :value="data.scope1" unit="tCO₂e" color="#FF3B30" :decimals="6" /></el-col>
      <el-col :span="6"><StatCard label="范围2(外购能源)" :value="data.scope2" unit="tCO₂e" color="#FF9500" :decimals="6" /></el-col>
      <el-col :span="6"><StatCard label="范围3(其他间接)" :value="data.scope3" unit="tCO₂e" color="#34C759" :decimals="6" /></el-col>
      <el-col :span="6"><StatCard label="总排放" :value="data.total" unit="tCO₂e" color="#0071E3" :decimals="6" /></el-col>
    </el-row>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="12"><ChartCard title="月度碳排放趋势" :option="trendOption" :height="300" /></el-col>
      <el-col :span="12"><ChartCard title="排放源占比" :option="pieOption" :height="300" /></el-col>
    </el-row>
    <el-card shadow="never">
      <el-table :data="data.details" border stripe>
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="source_name" label="排放源" />
        <el-table-column prop="scope" label="范围" width="80" />
        <el-table-column prop="activity_data" label="活动数据" align="right" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="emission_factor" label="排放因子" align="right" />
        <el-table-column prop="emission" label="排放量(tCO₂e)" align="right"><template #default="{row}"><span class="num">{{ row.emission.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="percentage" label="占比" align="right"><template #default="{row}">{{ row.percentage }}%</template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getCarbonStatistics } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'
import ChartCard from '../../components/ChartCard.vue'

const query = reactive({ year: new Date().getFullYear().toString(), scope: '' })
const data = reactive({ scope1: 0, scope2: 0, scope3: 0, total: 0, monthly_trend: [], source_stats: [], details: [] })

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: data.monthly_trend.map(i=>i.month), axisLabel: { color: '#6E6E73' } },
  yAxis: { type: 'value', axisLabel: { color: '#6E6E73' }, splitLine: { lineStyle: { type: 'dashed', color: '#E8E8ED' } } },
  grid: { left: '3%', right: '3%', bottom: '3%', containLabel: true },
  series: [{ type: 'line', smooth: true, data: data.monthly_trend.map(i=>i.emission), lineStyle: { color: '#0071E3', width: 2 }, areaStyle: { color: { type: 'linear', x:0,y:0,x2:0,y2:1, colorStops: [{offset:0,color:'rgba(0,113,227,0.15)'},{offset:1,color:'rgba(0,113,227,0)'}] } }, itemStyle: { color: '#0071E3' } }],
}))

const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂e ({d}%)' },
  legend: { bottom: 0, textStyle: { color: '#6E6E73' } },
  series: [{ type: 'pie', radius: ['45%', '70%'], data: data.source_stats.map(i=>({name:i.name,value:i.emission})), itemStyle: { borderRadius: 4 } }],
  color: ['#0071E3', '#34C759', '#FF9500', '#AF52DE', '#FF2D55', '#5AC8FA', '#FFCC00'],
}))

async function fetchData() {
  try { const res = await getCarbonStatistics(query); Object.assign(data, res.data) } catch(e) {}
}

onMounted(fetchData)
</script>
