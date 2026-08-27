<template>
  <div>
    <PageHeader title="碳排放预算"><template #actions><el-button type="primary" @click="showDialog()">新增预算</el-button></template></PageHeader>
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="年度"><el-date-picker v-model="query.year" type="year" value-format="YYYY" placeholder="选择年度" style="width:120px" /></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData">查询</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card shadow="never" style="margin-bottom:16px"><ChartCard title="预算 vs 实际碳排放" :option="chartOption" :height="300" /></el-card>
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="year" label="年度" width="80" />
        <el-table-column prop="month" label="月份" width="80"><template #default="{row}">{{ row.month || '年度' }}</template></el-table-column>
        <el-table-column prop="unit_name" label="用能单元" />
        <el-table-column prop="budget_carbon" label="预算碳排放(t)" align="right"><template #default="{row}"><span class="num">{{ row.budget_carbon.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="actual_carbon" label="实际碳排放(t)" align="right"><template #default="{row}"><span class="num">{{ row.actual_carbon.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="execution_rate" label="执行率" align="right"><template #default="{row}"><span :style="{color:row.execution_rate>110?'#FF3B30':row.execution_rate>=90?'#FF9500':'#34C759'}">{{ row.execution_rate }}%</span></template></el-table-column>
        <el-table-column prop="intensity_type" label="强度类型" width="100" />
        <el-table-column label="操作" width="140" align="center"><template #default="{row}"><el-button text type="primary" size="small" @click="showDialog(row)">编辑</el-button><el-button text type="danger" size="small" @click="handleDelete(row.id)">删除</el-button></template></el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="form.id?'编辑碳预算':'新增碳预算'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-form-item label="年度" prop="year"><el-date-picker v-model="form.year" type="year" value-format="YYYY" /></el-form-item>
        <el-form-item label="月份"><el-select v-model="form.month" clearable placeholder="不填=年度"><el-option v-for="m in 12" :key="m" :label="m+'月'" :value="m" /></el-select></el-form-item>
        <el-form-item label="用能单元" prop="unit_id"><el-tree-select v-model="form.unit_id" :data="unitTree" :props="{label:'name',value:'id',children:'children'}" check-strictly style="width:100%" /></el-form-item>
        <el-form-item label="强度类型"><el-select v-model="form.intensity_type" style="width:100%"><el-option label="产值强度" value="产值强度" /><el-option label="产品强度" value="产品强度" /></el-select></el-form-item>
        <el-form-item label="碳排放强度"><el-input-number v-model="form.carbon_intensity" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="计划产量/产值"><el-input-number v-model="form.planned_output" :precision="4" style="width:100%" /></el-form-item>
        <el-form-item label="预算碳排放"><el-input-number v-model="form.budget_carbon" :precision="6" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCarbonBudgets, createCarbonBudget, updateCarbonBudget, deleteCarbonBudget, getEnergyUnitTree } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import ChartCard from '../../components/ChartCard.vue'

const loading = ref(false); const saving = ref(false)
const items = ref([]); const unitTree = ref([])
const dialogVisible = ref(false); const formRef = ref(null)
const query = reactive({ year: new Date().getFullYear().toString() })
const form = reactive({ id: null, year: '', month: null, unit_id: null, intensity_type: '产值强度', carbon_intensity: 0, planned_output: 0, budget_carbon: 0 })
const rules = { year: [{required:true,message:'请选择'}], unit_id: [{required:true,message:'请选择'}] }

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis' }, legend: { bottom: 0, data: ['预算','实际'], textStyle: { color: '#6E6E73' } },
  xAxis: { type: 'category', data: items.value.map(i => (i.month?i.month+'月':'年度')), axisLabel: { color: '#6E6E73' } },
  yAxis: { type: 'value', axisLabel: { color: '#6E6E73' }, splitLine: { lineStyle: { type: 'dashed', color: '#E8E8ED' } } },
  grid: { left: '3%', right: '3%', bottom: '10%', containLabel: true },
  series: [
    { name: '预算', type: 'bar', data: items.value.map(i=>i.budget_carbon), itemStyle: { color: '#0071E3', borderRadius: [4,4,0,0] } },
    { name: '实际', type: 'bar', data: items.value.map(i=>i.actual_carbon), itemStyle: { color: '#FF9500', borderRadius: [4,4,0,0] } },
  ],
}))

function showDialog(row) { if (row) { Object.assign(form, row) } else { Object.assign(form, { id:null, year:query.year, month:null, unit_id:null, intensity_type:'产值强度', carbon_intensity:0, planned_output:0, budget_carbon:0 }) }; dialogVisible.value = true }

async function handleSave() { await formRef.value.validate(); saving.value = true; try { if (form.id) { await updateCarbonBudget(form.id, form) } else { await createCarbonBudget(form) }; ElMessage.success('保存成功'); dialogVisible.value = false; fetchData() } catch(e) {} finally { saving.value = false } }
async function handleDelete(id) { await ElMessageBox.confirm('确定删除？'); await deleteCarbonBudget(id); ElMessage.success('删除成功'); fetchData() }

async function fetchData() { loading.value = true; try { const res = await getCarbonBudgets(query); items.value = res.data||[] } catch(e) {} finally { loading.value = false } }

onMounted(async () => { try { const r = await getEnergyUnitTree(); unitTree.value = r.data } catch(e) {}; fetchData() })
</script>
