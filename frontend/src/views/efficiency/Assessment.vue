<template>
  <div>
    <PageHeader title="能效测评">
      <template #actions>
        <el-button type="primary" @click="showIndicatorDialog()">新增指标</el-button>
        <el-button type="primary" @click="showAssessmentDialog()">新增测评</el-button>
      </template>
    </PageHeader>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="never">
          <template #header><span style="font-weight:600">能效指标</span></template>
          <el-table :data="indicators" border stripe size="small">
            <el-table-column prop="name" label="指标名称" />
            <el-table-column prop="benchmark_value" label="基准值" align="right" />
            <el-table-column prop="target_value" label="目标值" align="right" />
            <el-table-column prop="unit" label="单位" width="60" />
            <el-table-column label="操作" width="60" align="center">
              <template #default="{row}"><el-button text type="danger" size="small" @click="deleteIndicator(row.id)">删除</el-button></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card shadow="never">
          <template #header><span style="font-weight:600">测评记录</span></template>
          <el-table :data="assessments" border stripe>
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="indicator_name" label="指标名称" />
            <el-table-column prop="stat_date" label="日期" width="110" />
            <el-table-column prop="energy_consumption" label="能耗量" align="right"><template #default="{row}"><span class="num">{{ row.energy_consumption.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
            <el-table-column prop="output" label="产量" align="right" />
            <el-table-column prop="actual_value" label="单位能耗" align="right"><template #default="{row}"><span class="num">{{ row.actual_value.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
            <el-table-column prop="deviation" label="偏差率%" align="right"><template #default="{row}"><span :style="{color:row.deviation>=20?'#FF3B30':row.deviation>=0?'#FF9500':row.deviation>=-10?'#0071E3':'#34C759'}">{{ row.deviation }}%</span></template></el-table-column>
            <el-table-column prop="level" label="等级" align="center" width="80">
              <template #default="{row}">
                <el-tag :type="levelType(row.level)">{{ row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="60" align="center">
              <template #default="{row}"><el-button text type="danger" size="small" @click="deleteAssessment(row.id)">删除</el-button></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="indDialogVisible" title="新增能效指标" width="450px" destroy-on-close>
      <el-form ref="indFormRef" :model="indForm" :rules="indRules" label-width="100px">
        <el-form-item label="指标名称" prop="name"><el-input v-model="indForm.name" /></el-form-item>
        <el-form-item label="关联能源" prop="energy_type_id"><el-select v-model="indForm.energy_type_id" style="width:100%"><el-option v-for="e in energyTypes" :key="e.id" :label="e.name" :value="e.id" /></el-select></el-form-item>
        <el-form-item label="基准值"><el-input-number v-model="indForm.benchmark_value" :precision="4" style="width:100%" /></el-form-item>
        <el-form-item label="目标值"><el-input-number v-model="indForm.target_value" :precision="4" style="width:100%" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="indForm.unit" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="indDialogVisible=false">取消</el-button><el-button type="primary" @click="saveIndicator">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="assDialogVisible" title="新增能效测评" width="450px" destroy-on-close>
      <el-form ref="assFormRef" :model="assForm" :rules="assRules" label-width="100px">
        <el-form-item label="测评指标" prop="indicator_id"><el-select v-model="assForm.indicator_id" style="width:100%"><el-option v-for="i in indicators" :key="i.id" :label="i.name" :value="i.id" /></el-select></el-form-item>
        <el-form-item label="测评日期" prop="stat_date"><el-date-picker v-model="assForm.stat_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="能源消耗量" prop="energy_consumption"><el-input-number v-model="assForm.energy_consumption" :min="0" :precision="4" style="width:100%" /></el-form-item>
        <el-form-item label="产量" prop="output"><el-input-number v-model="assForm.output" :min="0" :precision="4" style="width:100%" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="assForm.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="assDialogVisible=false">取消</el-button><el-button type="primary" @click="saveAssessment">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEfficiencyIndicators, createEfficiencyIndicator, deleteEfficiencyIndicator as delInd, getEfficiencyAssessments, createEfficiencyAssessment, deleteEfficiencyAssessment as delAss, getEnergyTypes } from '../../api'
import PageHeader from '../../components/PageHeader.vue'

const indicators = ref([]); const assessments = ref([]); const energyTypes = ref([])
const indDialogVisible = ref(false); const assDialogVisible = ref(false)
const indFormRef = ref(null); const assFormRef = ref(null)

const indForm = reactive({ name: '', energy_type_id: null, benchmark_value: 0, target_value: 0, unit: '' })
const assForm = reactive({ indicator_id: null, stat_date: '', energy_consumption: 0, output: 0, remark: '' })
const indRules = { name: [{required:true,message:'请输入'}], energy_type_id: [{required:true,message:'请选择'}] }
const assRules = { indicator_id: [{required:true,message:'请选择'}], stat_date: [{required:true,message:'请选择'}] }

function levelType(level) { return { '领先':'success', '先进':'', '合格':'warning', '落后':'danger' }[level] || 'info' }

function showIndicatorDialog() { Object.assign(indForm, { name:'', energy_type_id:null, benchmark_value:0, target_value:0, unit:'' }); indDialogVisible.value = true }
function showAssessmentDialog() { Object.assign(assForm, { indicator_id:null, stat_date:'', energy_consumption:0, output:0, remark:'' }); assDialogVisible.value = true }

async function saveIndicator() {
  await indFormRef.value.validate()
  await createEfficiencyIndicator(indForm)
  ElMessage.success('创建成功'); indDialogVisible.value = false; loadIndicators()
}

async function saveAssessment() {
  await assFormRef.value.validate()
  await createEfficiencyAssessment(assForm)
  ElMessage.success('测评创建成功'); assDialogVisible.value = false; loadAssessments()
}

async function deleteIndicator(id) { await ElMessageBox.confirm('确定删除？'); await delInd(id); ElMessage.success('删除成功'); loadIndicators() }
async function deleteAssessment(id) { await ElMessageBox.confirm('确定删除？'); await delAss(id); ElMessage.success('删除成功'); loadAssessments() }

async function loadIndicators() { try { const r = await getEfficiencyIndicators(); indicators.value = r.data||[] } catch(e) {} }
async function loadAssessments() { try { const r = await getEfficiencyAssessments({page_size:999}); assessments.value = r.data||[] } catch(e) {} }

onMounted(async () => {
  try { const r = await getEnergyTypes({is_active:true}); energyTypes.value = r.data||[] } catch(e) {}
  loadIndicators(); loadAssessments()
})
</script>
