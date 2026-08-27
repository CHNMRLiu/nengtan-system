<template>
  <div>
    <PageHeader title="计量查询" />
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="表计" required>
          <el-select v-model="query.meter_id" placeholder="请选择表计" clearable filterable style="width:200px">
            <el-option v-for="m in meters" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="统计维度">
          <el-select v-model="query.stat_type" style="width:120px">
            <el-option label="能耗" value="consumption" /><el-option label="成本" value="cost" />
            <el-option label="标准煤" value="standard_coal" /><el-option label="碳排放" value="carbon_emission" />
          </el-select>
        </el-form-item>
        <el-form-item label="查询周期">
          <el-select v-model="query.period" style="width:100px">
            <el-option label="日" value="day" /><el-option label="月" value="month" /><el-option label="年" value="year" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:260px" />
        </el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData" :disabled="!query.meter_id">查询</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="24"><ChartCard :title="`${meterName} - 消耗曲线`" :option="lineOption" :height="350" /></el-col>
    </el-row>
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="time" label="时间" />
        <el-table-column prop="consumption" label="消耗量" align="right"><template #default="{row}"><span class="num">{{ row.consumption.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="cost" label="费用(元)" align="right"><template #default="{row}"><span class="num">{{ row.cost.toLocaleString('zh-CN',{minimumFractionDigits:2}) }}</span></template></el-table-column>
        <el-table-column prop="standard_coal" label="折标煤" align="right"><template #default="{row}"><span class="num">{{ row.standard_coal.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="carbon_emission" label="碳排放" align="right"><template #default="{row}"><span class="num">{{ row.carbon_emission.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { getMeterQuery, getMeters } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import ChartCard from '../../components/ChartCard.vue'

const loading = ref(false)
const meters = ref([])
const dateRange = ref(null)
const meterName = ref('')
const items = ref([])
const query = reactive({ meter_id: null, stat_type: 'consumption', period: 'month' })

watch(dateRange, v => { query.start_date = v?v[0]:null; query.end_date = v?v[1]:null })

const lineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: items.value.map(i=>i.time), axisLabel: { color: '#6E6E73' } },
  yAxis: { type: 'value', axisLabel: { color: '#6E6E73' }, splitLine: { lineStyle: { type: 'dashed', color: '#E8E8ED' } } },
  grid: { left: '3%', right: '3%', bottom: '3%', containLabel: true },
  series: [{ type: 'line', smooth: true, data: items.value.map(i=>i[query.stat_type]||0), lineStyle: { color: '#0071E3', width: 2 }, areaStyle: { color: { type: 'linear', x:0,y:0,x2:0,y2:1, colorStops: [{offset:0,color:'rgba(0,113,227,0.15)'},{offset:1,color:'rgba(0,113,227,0)'}] } }, itemStyle: { color: '#0071E3' } }],
}))

async function fetchData() {
  if (!query.meter_id) return
  loading.value = true
  try {
    const res = await getMeterQuery(query)
    meterName.value = res.data.meter_name
    items.value = res.data.items || []
  } catch(e) {} finally { loading.value = false }
}

onMounted(async () => {
  try { const r = await getMeters({ page_size: 999 }); meters.value = r.data || [] } catch(e) {}
})
</script>
