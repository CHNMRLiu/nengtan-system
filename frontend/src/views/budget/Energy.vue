<template>
  <div>
    <PageHeader title="用能预算"><template #actions><el-button type="primary" @click="showDialog()">新增预算</el-button></template></PageHeader>
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="年度"><el-date-picker v-model="query.year" type="year" value-format="YYYY" placeholder="选择年度" style="width:120px" /></el-form-item>
        <el-form-item label="用能单元"><el-tree-select v-model="query.unit_id" :data="unitTree" :props="{label:'name',value:'id',children:'children'}" placeholder="全部" clearable check-strictly style="width:180px" /></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData">查询</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card shadow="never" style="margin-bottom:16px"><ChartCard title="预算 vs 实际" :option="chartOption" :height="300" /></el-card>
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="year" label="年度" width="80" />
        <el-table-column prop="month" label="月份" width="80"><template #default="{row}">{{ row.month || '年度' }}</template></el-table-column>
        <el-table-column prop="energy_type_name" label="能源类型" />
        <el-table-column prop="unit_name" label="用能单元" />
        <el-table-column prop="budget_value" label="预算量" align="right"><template #default="{row}"><span class="num">{{ row.budget_value.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="actual_value" label="实际量" align="right"><template #default="{row}"><span class="num">{{ row.actual_value.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="execution_rate" label="执行率" align="right">
          <template #default="{row}"><span :style="{color:row.execution_rate>110?'#FF3B30':row.execution_rate>=90?'#FF9500':'#34C759'}">{{ row.execution_rate }}%</span></template>
        </el-table-column>
        <el-table-column prop="source_type" label="单耗来源" width="100" />
        <el-table-column label="操作" width="140" align="center">
          <template #default="{row}"><el-button text type="primary" size="small" @click="showDialog(row)">编辑</el-button><el-button text type="danger" size="small" @click="handleDelete(row.id)">删除</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="form.id?'编辑预算':'新增预算'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="年度" prop="year"><el-date-picker v-model="form.year" type="year" value-format="YYYY" /></el-form-item>
        <el-form-item label="月份"><el-select v-model="form.month" clearable placeholder="不填=年度"><el-option v-for="m in 12" :key="m" :label="m+'月'" :value="m" /></el-select></el-form-item>
        <el-form-item label="能源类型" prop="energy_type_id"><el-select v-model="form.energy_type_id" style="width:100%"><el-option v-for="e in energyTypes" :key="e.id" :label="e.name" :value="e.id" /></el-select></el-form-item>
        <el-form-item label="用能单元" prop="unit_id"><el-tree-select v-model="form.unit_id" :data="unitTree" :props="{label:'name',value:'id',children:'children'}" check-strictly style="width:100%" /></el-form-item>
        <el-form-item label="单耗来源"><el-select v-model="form.source_type" style="width:100%"><el-option label="能效指标" value="能效指标" /><el-option label="能效测评" value="能效测评" /><el-option label="手工填写" value="手工填写" /></el-select></el-form-item>
        <el-form-item label="产品单耗"><el-input-number v-model="form.unit_consumption" :precision="4" style="width:100%" /></el-form-item>
        <el-form-item label="计划产量"><el-input-number v-model="form.planned_output" :precision="4" style="width:100%" /></el-form-item>
        <el-form-item label="预算量"><el-input-number v-model="form.budget_value" :precision="4" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEnergyBudgets, createEnergyBudget, updateEnergyBudget, deleteEnergyBudget, getEnergyTypes, getEnergyUnitTree } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import ChartCard from '../../components/ChartCard.vue'

const loading = ref(false); const saving = ref(false)
const items = ref([]); const energyTypes = ref([]); const unitTree = ref([])
const dialogVisible = ref(false); const formRef = ref(null)
const query = reactive({ year: new Date().getFullYear().toString(), unit_id: null })
const form = reactive({ id: null, year: '', month: null, energy_type_id: null, unit_id: null, source_type: '手工填写', unit_consumption: 0, planned_output: 0, budget_value: 0 })
const rules = { year: [{required:true,message:'请选择'}], energy_type_id: [{required:true,message:'请选择'}], unit_id: [{required:true,message:'请选择'}] }

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis' }, legend: { bottom: 0, data: ['预算量','实际量'], textStyle: { color: '#6E6E73' } },
  xAxis: { type: 'category', data: items.value.map(i => (i.month?i.month+'月':'年度')), axisLabel: { color: '#6E6E73' } },
  yAxis: { type: 'value', axisLabel: { color: '#6E6E73' }, splitLine: { lineStyle: { type: 'dashed', color: '#E8E8ED' } } },
  grid: { left: '3%', right: '3%', bottom: '10%', containLabel: true },
  series: [
    { name: '预算量', type: 'bar', data: items.value.map(i=>i.budget_value), itemStyle: { color: '#0071E3', borderRadius: [4,4,0,0] } },
    { name: '实际量', type: 'bar', data: items.value.map(i=>i.actual_value), itemStyle: { color: '#FF9500', borderRadius: [4,4,0,0] } },
  ],
}))

function showDialog(row) {
  if (row) { Object.assign(form, row) } else { Object.assign(form, { id:null, year:query.year, month:null, energy_type_id:null, unit_id:null, source_type:'手工填写', unit_consumption:0, planned_output:0, budget_value:0 }) }
  dialogVisible.value = true
}

async function handleSave() {
  await formRef.value.validate(); saving.value = true
  try {
    if (form.id) { await updateEnergyBudget(form.id, form) } else { await createEnergyBudget(form) }
    ElMessage.success('保存成功'); dialogVisible.value = false; fetchData()
  } catch(e) {} finally { saving.value = false }
}

async function handleDelete(id) { await ElMessageBox.confirm('确定删除？'); await deleteEnergyBudget(id); ElMessage.success('删除成功'); fetchData() }

async function fetchData() {
  loading.value = true
  try { const res = await getEnergyBudgets(query); items.value = res.data||[] } catch(e) {} finally { loading.value = false }
}

onMounted(async () => {
  try { const [r1, r2] = await Promise.all([getEnergyTypes({is_active:true}), getEnergyUnitTree()]); energyTypes.value = r1.data||[]; unitTree.value = r2.data||[] } catch(e) {}
  fetchData()
})
</script>
