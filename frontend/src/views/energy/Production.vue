<template>
  <div>
    <PageHeader title="生产数据">
      <template #actions><el-button type="primary" @click="showDialog()">新增产量</el-button></template>
    </PageHeader>
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="product_name" label="产品" />
        <el-table-column prop="unit_name" label="用能单元" />
        <el-table-column prop="stat_date" label="统计日期" />
        <el-table-column prop="output" label="产量" align="right"><template #default="{row}"><span class="num">{{ row.output.toLocaleString() }}</span></template></el-table-column>
        <el-table-column prop="output_unit" label="单位" width="80" />
        <el-table-column prop="output_value" label="产值(元)" align="right"><template #default="{row}"><span class="num">{{ row.output_value.toLocaleString('zh-CN',{minimumFractionDigits:2}) }}</span></template></el-table-column>
        <el-table-column prop="period" label="周期" width="80" />
        <el-table-column label="操作" width="140" align="center">
          <template #default="{row}">
            <el-button text type="primary" size="small" @click="showDialog(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total>0" :current-page="page" :page-size="pageSize" :total="total" @current-change="p=>{page=p;fetchData()}" layout="total,prev,pager,next" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id?'编辑生产数据':'新增生产数据'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="产品" prop="product_id">
          <el-select v-model="form.product_id" placeholder="请选择" style="width:100%">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="用能单元" prop="unit_id">
          <el-tree-select v-model="form.unit_id" :data="unitTree" :props="{label:'name',value:'id',children:'children'}" placeholder="请选择" check-strictly style="width:100%" />
        </el-form-item>
        <el-form-item label="统计日期" prop="stat_date">
          <el-date-picker v-model="form.stat_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-form-item label="产量" prop="output"><el-input-number v-model="form.output" :min="0" :precision="4" style="width:100%" /></el-form-item>
        <el-form-item label="产值(元)"><el-input-number v-model="form.output_value" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="统计周期">
          <el-select v-model="form.period" style="width:100%"><el-option label="月" value="月" /><el-option label="年" value="年" /></el-select>
        </el-form-item>
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
import { getProductionData, createProductionData, updateProductionData, deleteProductionData, getProducts, getEnergyUnitTree } from '../../api'
import PageHeader from '../../components/PageHeader.vue'

const loading = ref(false); const saving = ref(false)
const items = ref([]); const products = ref([]); const unitTree = ref([])
const total = ref(0); const page = ref(1); const pageSize = 20
const dialogVisible = ref(false); const formRef = ref(null)
const form = reactive({ id: null, product_id: null, unit_id: null, stat_date: '', output: 0, output_value: 0, period: '月', remark: '' })
const rules = { product_id: [{required:true,message:'请选择产品'}], unit_id: [{required:true,message:'请选择单元'}], stat_date: [{required:true,message:'请选择日期'}] }

function showDialog(row) {
  if (row) { Object.assign(form, row) } else { Object.assign(form, { id:null, product_id:null, unit_id:null, stat_date:'', output:0, output_value:0, period:'月', remark:'' }) }
  dialogVisible.value = true
}

async function handleSave() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (form.id) { await updateProductionData(form.id, form) } else { await createProductionData(form) }
    ElMessage.success('保存成功'); dialogVisible.value = false; fetchData()
  } catch(e) {} finally { saving.value = false }
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确定删除该记录？', '确认')
  await deleteProductionData(id); ElMessage.success('删除成功'); fetchData()
}

async function fetchData() {
  loading.value = true
  try { const res = await getProductionData({ page: page.value, page_size: pageSize }); items.value = res.data || []; total.value = res.total } catch(e) {} finally { loading.value = false }
}

onMounted(async () => {
  try { const [r1, r2] = await Promise.all([getProducts(), getEnergyUnitTree()]); products.value = r1.data||[]; unitTree.value = r2.data||[] } catch(e) {}
  fetchData()
})
</script>
