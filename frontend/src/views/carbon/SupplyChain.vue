<template>
  <div>
    <PageHeader title="供应链碳管理">
      <template #actions>
        <el-button type="primary" @click="showSupplierDialog()">新增供应商</el-button>
        <el-button type="primary" @click="showCarbonDialog()">录入碳数据</el-button>
      </template>
    </PageHeader>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header><span style="font-weight:600">供应商列表</span></template>
          <el-table :data="suppliers" border stripe @row-click="selectSupplier" highlight-current-row>
            <el-table-column prop="name" label="供应商名称" />
            <el-table-column prop="contact_person" label="联系人" width="80" />
            <el-table-column prop="phone" label="电话" width="120" />
            <el-table-column prop="category" label="类别" width="80" />
            <el-table-column prop="risk_level" label="风险等级" width="80" align="center">
              <template #default="{row}"><el-tag :type="row.risk_level==='高'?'danger':row.risk_level==='中'?'warning':'success'" size="small">{{ row.risk_level }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="total_emission" label="总排放(t)" align="right" width="120"><template #default="{row}"><span class="num">{{ row.total_emission.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="10">
        <ChartCard title="供应商碳排放排行(TOP10)" :option="rankChartOption" :height="400" />
      </el-col>
    </el-row>
    <el-card v-if="selectedSupplier" shadow="never">
      <template #header><span style="font-weight:600">{{ selectedSupplier.name }} - 碳排放数据</span></template>
      <el-table :data="carbonData" border stripe>
        <el-table-column prop="year" label="年度" width="80" />
        <el-table-column prop="material_name" label="物料/服务" />
        <el-table-column prop="quantity" label="数量" align="right" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="emission_factor" label="排放因子" align="right" />
        <el-table-column prop="emission" label="排放量(tCO₂e)" align="right"><template #default="{row}"><span class="num">{{ row.emission.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="data_source" label="数据来源" width="100" />
        <el-table-column label="操作" width="80" align="center"><template #default="{row}"><el-button text type="danger" size="small" @click="deleteCarbonData(row.id)">删除</el-button></template></el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="supplierDialogVisible" title="新增供应商" width="500px" destroy-on-close>
      <el-form ref="supplierFormRef" :model="supplierForm" :rules="{name:[{required:true,message:'请输入'}]}" label-width="100px">
        <el-form-item label="供应商名称" prop="name"><el-input v-model="supplierForm.name" /></el-form-item>
        <el-form-item label="统一信用代码"><el-input v-model="supplierForm.credit_code" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="supplierForm.contact_person" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="supplierForm.phone" /></el-form-item>
        <el-form-item label="供应类别"><el-select v-model="supplierForm.category" style="width:100%"><el-option v-for="c in ['原材料','零部件','服务','物流','其他']" :key="c" :label="c" :value="c" /></el-select></el-form-item>
        <el-form-item label="风险等级"><el-select v-model="supplierForm.risk_level" style="width:100%"><el-option label="高" value="高" /><el-option label="中" value="中" /><el-option label="低" value="低" /></el-select></el-form-item>
        <el-form-item label="地址"><el-input v-model="supplierForm.address" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="supplierDialogVisible=false">取消</el-button><el-button type="primary" @click="saveSupplier">保存</el-button></template>
    </el-dialog>
    <el-dialog v-model="carbonDialogVisible" title="录入碳数据" width="500px" destroy-on-close>
      <el-form ref="carbonFormRef" :model="carbonForm" :rules="{supplier_id:[{required:true,message:'请选择'}],year:[{required:true,message:'请输入'}]}" label-width="100px">
        <el-form-item label="供应商" prop="supplier_id"><el-select v-model="carbonForm.supplier_id" style="width:100%"><el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" /></el-select></el-form-item>
        <el-form-item label="年度" prop="year"><el-date-picker v-model="carbonForm.year" type="year" value-format="YYYY" /></el-form-item>
        <el-form-item label="物料/服务"><el-input v-model="carbonForm.material_name" /></el-form-item>
        <el-form-item label="数量"><el-input-number v-model="carbonForm.quantity" :precision="4" style="width:100%" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="carbonForm.unit" /></el-form-item>
        <el-form-item label="排放因子"><el-input-number v-model="carbonForm.emission_factor" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="数据来源"><el-select v-model="carbonForm.data_source" style="width:100%"><el-option label="供应商申报" value="供应商申报" /><el-option label="实测" value="实测" /><el-option label="默认因子" value="默认因子" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="carbonDialogVisible=false">取消</el-button><el-button type="primary" @click="saveCarbonData">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSuppliers, createSupplier, getSupplierCarbonData, createSupplierCarbonData, deleteSupplierCarbonData } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import ChartCard from '../../components/ChartCard.vue'

const suppliers = ref([]); const carbonData = ref([]); const selectedSupplier = ref(null)
const supplierDialogVisible = ref(false); const carbonDialogVisible = ref(false)
const supplierFormRef = ref(null); const carbonFormRef = ref(null)
const supplierForm = reactive({ name: '', credit_code: '', contact_person: '', phone: '', category: '原材料', risk_level: '低', address: '' })
const carbonForm = reactive({ supplier_id: null, year: '', material_name: '', quantity: 0, unit: '', emission_factor: 0, data_source: '默认因子' })

const rankChartOption = computed(() => {
  const sorted = [...suppliers.value].sort((a, b) => b.total_emission - a.total_emission).slice(0, 10)
  return {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', axisLabel: { color: '#6E6E73' }, splitLine: { lineStyle: { type: 'dashed', color: '#E8E8ED' } } },
    yAxis: { type: 'category', data: sorted.map(i=>i.name).reverse(), axisLabel: { color: '#6E6E73' } },
    grid: { left: '3%', right: '3%', bottom: '3%', containLabel: true },
    series: [{ type: 'bar', data: sorted.map(i=>i.total_emission).reverse(), barWidth: '40%', itemStyle: { color: '#0071E3', borderRadius: [0,4,4,0] } }],
  }
})

function showSupplierDialog() { Object.assign(supplierForm, { name:'', credit_code:'', contact_person:'', phone:'', category:'原材料', risk_level:'低', address:'' }); supplierDialogVisible.value = true }
function showCarbonDialog() { Object.assign(carbonForm, { supplier_id:selectedSupplier.value?.id||null, year:'', material_name:'', quantity:0, unit:'', emission_factor:0, data_source:'默认因子' }); carbonDialogVisible.value = true }

async function selectSupplier(row) { selectedSupplier.value = row; try { const r = await getSupplierCarbonData({supplier_id:row.id}); carbonData.value = r.data||[] } catch(e) {} }

async function saveSupplier() { await supplierFormRef.value.validate(); await createSupplier(supplierForm); ElMessage.success('创建成功'); supplierDialogVisible.value = false; loadSuppliers() }
async function saveCarbonData() { await carbonFormRef.value.validate(); await createSupplierCarbonData(carbonForm); ElMessage.success('录入成功'); carbonDialogVisible.value = false; if (selectedSupplier.value) selectSupplier(selectedSupplier.value); loadSuppliers() }
async function deleteCarbonData(id) { await ElMessageBox.confirm('确定删除？'); await deleteSupplierCarbonData(id); ElMessage.success('删除成功'); if (selectedSupplier.value) selectSupplier(selectedSupplier.value); loadSuppliers() }

async function loadSuppliers() { try { const r = await getSuppliers(); suppliers.value = r.data||[] } catch(e) {} }

onMounted(loadSuppliers)
</script>
