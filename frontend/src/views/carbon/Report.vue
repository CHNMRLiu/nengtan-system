<template>
  <div>
    <PageHeader title="碳排报告">
      <template #actions>
        <el-select v-model="selectedYear" placeholder="选择年度" style="width:120px;margin-right:8px">
          <el-option v-for="y in years" :key="y" :label="y+'年'" :value="y" />
        </el-select>
        <el-button type="primary" @click="generateReport">生成报告</el-button>
        <el-button @click="exportReport" :disabled="!report">导出</el-button>
      </template>
    </PageHeader>
    <el-card v-if="!report" shadow="never"><el-empty description="请选择年度并生成碳排放报告" /></el-card>
    <template v-else>
      <el-card shadow="never" style="margin-bottom:16px">
        <div style="text-align:center;margin-bottom:24px">
          <h2 style="font-size:24px;font-weight:600">{{ report.year }}年度碳排放报告</h2>
          <p style="color:#6E6E73;margin-top:8px">编制单位：{{ orgName }} | 编制日期：{{ report.report_date }}</p>
        </div>
      </el-card>
      <el-row :gutter="16" style="margin-bottom:16px">
        <el-col :span="8"><StatCard label="总排放量" :value="report.total_emission" unit="tCO₂e" color="#0071E3" :decimals="6" /></el-col>
        <el-col :span="8"><StatCard label="范围1(直接排放)" :value="report.scope1" unit="tCO₂e" color="#FF3B30" :decimals="6" /></el-col>
        <el-col :span="8"><StatCard label="范围2(外购能源)" :value="report.scope2" unit="tCO₂e" color="#FF9500" :decimals="6" /></el-col>
      </el-row>
      <el-card shadow="never" style="margin-bottom:16px">
        <template #header><span style="font-weight:600">排放源明细</span></template>
        <el-table :data="details" border stripe>
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
      <el-card shadow="never">
        <template #header><span style="font-weight:600">减排措施与成效</span></template>
        <el-input v-model="report.measures" type="textarea" :rows="4" placeholder="请输入减排措施与成效" />
        <div style="margin-top:16px;font-weight:600">下一年度减排计划</div>
        <el-input v-model="report.next_plan" type="textarea" :rows="4" placeholder="请输入下一年度减排计划" style="margin-top:8px" />
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCarbonReports, generateCarbonReport, getCarbonReport } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'

const selectedYear = ref(new Date().getFullYear().toString())
const years = ref([])
const report = ref(null)
const details = ref([])
const orgName = ref('')

async function generateReport() {
  try {
    const res = await generateCarbonReport({ year: parseInt(selectedYear.value), measures: '', next_plan: '' })
    report.value = res.data.report
    details.value = res.data.details || []
    orgName.value = res.data.org_name || ''
    ElMessage.success('报告生成成功')
  } catch(e) {}
}

async function loadReport() {
  try {
    const res = await getCarbonReport(parseInt(selectedYear.value))
    report.value = res.data.report
    details.value = res.data.details || []
    orgName.value = res.data.org_name || ''
  } catch(e) { report.value = null; details.value = [] }
}

function exportReport() {
  const w = window.open('', '_blank')
  w.document.write(`<html><head><title>${report.value.year}年度碳排放报告</title><style>body{font-family:sans-serif;padding:40px}table{width:100%;border-collapse:collapse;margin:20px 0}th,td{border:1px solid #ddd;padding:8px;text-align:left}th{background:#f5f5f7}h1,h2{text-align:center}</style></head><body>`)
  w.document.write(`<h1>${report.value.year}年度碳排放报告</h1><p style="text-align:center">编制单位：${orgName.value} | 编制日期：${report.value.report_date}</p>`)
  w.document.write(`<h2>碳排放总量</h2><p>总排放：${report.value.total_emission} tCO₂e | 范围1：${report.value.scope1} | 范围2：${report.value.scope2} | 范围3：${report.value.scope3}</p>`)
  w.document.write('<h2>排放源明细</h2><table><tr><th>序号</th><th>排放源</th><th>范围</th><th>活动数据</th><th>排放量(tCO₂e)</th><th>占比</th></tr>')
  details.value.forEach((d, i) => { w.document.write(`<tr><td>${i+1}</td><td>${d.source_name}</td><td>${d.scope}</td><td>${d.activity_data} ${d.unit}</td><td>${d.emission}</td><td>${d.percentage}%</td></tr>`) })
  w.document.write('</table>')
  w.document.write(`<h2>减排措施与成效</h2><p>${report.value.measures || '暂无'}</p>`)
  w.document.write(`<h2>下一年度减排计划</h2><p>${report.value.next_plan || '暂无'}</p>`)
  w.document.write('</body></html>')
  w.document.close()
  w.print()
}

onMounted(async () => {
  const now = new Date().getFullYear()
  years.value = Array.from({ length: 5 }, (_, i) => now - i)
  loadReport()
})
</script>
