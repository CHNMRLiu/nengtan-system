<template>
  <div>
    <PageHeader title="能效平衡与优化" />
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6"><StatCard label="能源输入总量" :value="inputEnergy" unit="kWh" color="#0071E3" /></el-col>
      <el-col :span="6"><StatCard label="有效利用量" :value="effectiveEnergy" unit="kWh" color="#34C759" /></el-col>
      <el-col :span="6"><StatCard label="损失量" :value="lossEnergy" unit="kWh" color="#FF3B30" /></el-col>
      <el-col :span="6"><StatCard label="综合能效" :value="efficiency" unit="%" color="#FF9500" /></el-col>
    </el-row>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="14"><ChartCard title="能流平衡分析" :option="barOption" :height="350" /></el-col>
      <el-col :span="10">
        <el-card shadow="never">
          <template #header><span style="font-weight:600">损耗超限提示</span></template>
          <el-table :data="overLimitLinks" border stripe size="small">
            <el-table-column prop="name" label="环节" />
            <el-table-column prop="loss_rate" label="损耗率%" align="right"><template #default="{row}"><span style="color:#FF3B30">{{ row.loss_rate }}%</span></template></el-table-column>
            <el-table-column label="限值" align="center">10%</el-table-column>
            <el-table-column label="状态" align="center"><el-tag type="danger" size="small">超限</el-tag></el-table-column>
          </el-table>
          <el-empty v-if="overLimitLinks.length===0" description="无超限环节" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>
    <el-card shadow="never">
      <template #header><span style="font-weight:600">优化建议</span></template>
      <div v-if="suggestions.length > 0">
        <div v-for="(s, i) in suggestions" :key="i" style="padding:8px 0;border-bottom:1px solid #E8E8ED;color:#1D1D1F">💡 {{ s }}</div>
      </div>
      <div v-else style="color:#34C759;padding:16px 0">✅ 当前能效良好，暂无优化建议</div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getEnergyFlowNodes, getEnergyFlowLinks } from '../api'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import ChartCard from '../components/ChartCard.vue'

const nodes = ref([]); const links = ref([])

const nodeTypeMap = computed(() => {
  const m = {}
  nodes.value.forEach(n => { m[n.id] = n.node_type })
  return m
})

const inputEnergy = computed(() => links.value.filter(l => nodeTypeMap.value[l.source_node_id] === '输入').reduce((s, l) => s + l.flow_value, 0))
const effectiveEnergy = computed(() => links.value.filter(l => nodeTypeMap.value[l.target_node_id] === '利用').reduce((s, l) => s + l.flow_value, 0))
const lossEnergy = computed(() => links.value.filter(l => nodeTypeMap.value[l.target_node_id] === '损失').reduce((s, l) => s + l.flow_value, 0))
const efficiency = computed(() => inputEnergy.value > 0 ? +(effectiveEnergy.value / inputEnergy.value * 100).toFixed(2) : 0)

const overLimitLinks = computed(() => links.value.filter(l => l.loss_rate > 10).map(l => ({
  name: `${l.source_name} → ${l.target_name}`, loss_rate: l.loss_rate
})))

const suggestions = computed(() => {
  const s = []
  if (efficiency.value < 80) s.push('综合能效低于80%，建议开展能源审计，识别主要损耗环节')
  if (overLimitLinks.value.length > 0) s.push(`有${overLimitLinks.value.length}个环节损耗超限，建议优先处理`)
  if (lossEnergy.value > inputEnergy.value * 0.15) s.push('损失量超过输入的15%，建议加强设备保温和维护')
  return s
})

const stageData = computed(() => {
  const stages = { '输入': 0, '转换': 0, '分配': 0, '利用': 0, '损失': 0 }
  links.value.forEach(l => {
    const st = nodeTypeMap.value[l.source_node_id]
    if (st && stages[st] !== undefined) stages[st] += l.flow_value
  })
  return stages
})

const barOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: Object.keys(stageData.value), axisLabel: { color: '#6E6E73' } },
  yAxis: { type: 'value', name: 'kWh', axisLabel: { color: '#6E6E73' }, splitLine: { lineStyle: { type: 'dashed', color: '#E8E8ED' } } },
  grid: { left: '3%', right: '3%', bottom: '3%', containLabel: true },
  series: [{ type: 'bar', data: Object.values(stageData.value), barWidth: '40%', itemStyle: { color: p => ['#0071E3','#FF9500','#86868B','#34C759','#FF3B30'][p.dataIndex], borderRadius: [4,4,0,0] } }],
}))

onMounted(async () => {
  try {
    const [r1, r2] = await Promise.all([getEnergyFlowNodes(), getEnergyFlowLinks()])
    nodes.value = r1.data||[]; links.value = (r2.data||[]).map(l => ({...l, flow_value: Number(l.flow_value), loss_rate: Number(l.loss_rate)}))
  } catch(e) {}
})
</script>
