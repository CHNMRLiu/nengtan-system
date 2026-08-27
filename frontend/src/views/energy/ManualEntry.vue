<template>
  <div>
    <PageHeader title="录接数据">
      <template #actions><el-button type="primary" @click="showDialog()">新增录入</el-button></template>
    </PageHeader>
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="能源类型">
          <el-select v-model="filters.energy_type_id" placeholder="全部" clearable style="width:150px">
            <el-option v-for="e in energyTypes" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="用能单元">
          <el-tree-select v-model="filters.unit_id" :data="unitTree" :props="{label:'name',value:'id',children:'children'}" placeholder="全部" clearable check-strictly style="width:180px" />
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:260px" />
        </el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData">查询</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading" show-summary :summary-method="getSummary">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="entry_date" label="录入日期" width="110" />
        <el-table-column prop="energy_type_name" label="能源类型" width="100" />
        <el-table-column prop="unit_name" label="用能单元" width="120" />
        <el-table-column prop="consumption" label="消耗量" align="right"><template #default="{row}"><span class="num">{{ row.consumption.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="unit_price" label="单价" align="right"><template #default="{row}"><span class="num">{{ row.unit_price.toLocaleString('zh-CN',{minimumFractionDigits:2}) }}</span></template></el-table-column>
        <el-table-column prop="cost" label="费用(元)" align="right"><template #default="{row}"><span class="num">{{ row.cost.toLocaleString('zh-CN',{minimumFractionDigits:2}) }}</span></template></el-table-column>
        <el-table-column prop="standard_coal" label="折标煤(kgce)" align="right"><template #default="{row}"><span class="num">{{ row.standard_coal.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="carbon_emission" label="碳排放(tCO₂e)" align="right"><template #default="{row}"><span class="num">{{ row.carbon_emission.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="recorder" label="录入人" width="80" />
        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template #default="{row}">
            <el-button text type="primary" size="small" @click="showDialog(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total>0" :current-page="page" :page-size="pageSize" :total="total" @current-change="p=>{page=p;fetchData()}" layout="total,prev,pager,next" style="margin-top:16px;justify-content:flex-end" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id?'编辑录入':'新增录入'" width="520px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="能源类型" prop="energy_type_id">
          <el-select v-model="form.energy_type_id" placeholder="请选择" style="width:100%" @change="onEnergyTypeChange">
            <el-option v-for="e in energyTypes" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="用能单元" prop="unit_id">
          <el-tree-select v-model="form.unit_id" :data="unitTree" :props="{label:'name',value:'id',children:'children'}" placeholder="请选择" check-strictly style="width:100%" />
        </el-form-item>
        <el-form-item label="录入日期" prop="entry_date">
          <el-date-picker v-model="form.entry_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="消耗量" prop="consumption">
          <el-input-number v-model="form.consumption" :min="0" :precision="4" style="width:100%" />
        </el-form-item>
        <el-form-item label="单价(元)">
          <el-input-number v-model="form.unit_price" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="费用(元)">
          <el-input :model-value="(form.consumption * form.unit_price).toFixed(2)" disabled />
        </el-form-item>
        <el-form-item label="录入人"><el-input v-model="form.recorder" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getManualEntries, createManualEntry, updateManualEntry, deleteManualEntry, getEnergyTypes, getEnergyUnitTree } from '../../api'
import PageHeader from '../../components/PageHeader.vue'

const loading = ref(false); const saving = ref(false)
const items = ref([]); const energyTypes = ref([]); const unitTree = ref([])
const total = ref(0); const page = ref(1); const pageSize = 20
const dateRange = ref(null)
const filters = reactive({ energy_type_id: null, unit_id: null })
const dialogVisible = ref(false); const formRef = ref(null)
const form = reactive({ id: null, energy_type_id: null, unit_id: null, entry_date: '', consumption: 0, unit_price: 0, recorder: '', remark: '' })
const rules = {
  energy_type_id: [{required:true,message:'请选择能源类型'}],
  unit_id: [{required:true,message:'请选择用能单元'}],
  entry_date: [{required:true,message:'请选择日期'}],
  consumption: [{required:true,message:'请输入消耗量'}],
}

function onEnergyTypeChange(id) {
  const et = energyTypes.value.find(e => e.id === id)
  if (et) form.unit_price = et.default_price
}

function showDialog(row) {
  if (row) { Object.assign(form, row) } else { Object.assign(form, { id:null, energy_type_id:null, unit_id:null, entry_date:'', consumption:0, unit_price:0, recorder:'', remark:'' }) }
  dialogVisible.value = true
}

async function handleSave() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (form.id) { await updateManualEntry(form.id, form) } else { await createManualEntry(form) }
    ElMessage.success('保存成功'); dialogVisible.value = false; fetchData()
  } catch(e) {} finally { saving.value = false }
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确定删除该记录？', '确认')
  await deleteManualEntry(id); ElMessage.success('删除成功'); fetchData()
}

function getSummary({ columns, data }) {
  const sums = []
  columns.forEach((col, idx) => {
    if (idx === 0) { sums[idx] = '合计'; return }
    if (['consumption','cost','standard_coal','carbon_emission'].includes(col.property)) {
      const total = data.reduce((s, r) => s + Number(r[col.property] || 0), 0)
      sums[idx] = col.property === 'carbon_emission' ? total.toFixed(6) : total.toFixed(4)
    } else { sums[idx] = '' }
  })
  return sums
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize, ...filters }
    if (dateRange.value) { params.start_date = dateRange.value[0]; params.end_date = dateRange.value[1] }
    const res = await getManualEntries(params); items.value = res.data || []; total.value = res.total
  } catch(e) {} finally { loading.value = false }
}

onMounted(async () => {
  try { const [r1, r2] = await Promise.all([getEnergyTypes({is_active:true}), getEnergyUnitTree()]); energyTypes.value = r1.data||[]; unitTree.value = r2.data||[] } catch(e) {}
  fetchData()
})
</script>
