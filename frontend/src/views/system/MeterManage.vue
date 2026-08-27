<template>
  <div>
    <PageHeader title="表计管理"><template #actions><el-button type="primary" @click="showDialog()">新增表计</el-button></template></PageHeader>
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="name" label="名称" />
        <el-table-column label="能源类型" width="100"><template #default="{row}">{{ energyTypeName(row.energy_type_id) }}</template></el-table-column>
        <el-table-column label="用能单元" width="120"><template #default="{row}">{{ unitName(row.unit_id) }}</template></el-table-column>
        <el-table-column prop="meter_type" label="类型" width="80" />
        <el-table-column prop="installation_location" label="安装位置" />
        <el-table-column prop="is_active" label="状态" width="80" align="center"><template #default="{row}"><el-tag :type="row.is_active?'success':'info'" size="small">{{ row.is_active?'启用':'停用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="140" align="center">
          <template #default="{row}"><el-button text type="primary" size="small" @click="showDialog(row)">编辑</el-button><el-button text type="danger" size="small" @click="handleDelete(row.id)">删除</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="form.id?'编辑表计':'新增表计'" width="550px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="编码" prop="code"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="能源类型" prop="energy_type_id"><el-select v-model="form.energy_type_id" style="width:100%"><el-option v-for="e in energyTypes" :key="e.id" :label="e.name" :value="e.id" /></el-select></el-form-item>
        <el-form-item label="用能单元" prop="unit_id"><el-tree-select v-model="form.unit_id" :data="unitTree" :props="{label:'name',value:'id',children:'children'}" check-strictly style="width:100%" /></el-form-item>
        <el-form-item label="类型"><el-input v-model="form.meter_type" /></el-form-item>
        <el-form-item label="安装位置"><el-input v-model="form.installation_location" /></el-form-item>
        <el-form-item label="精度等级"><el-input v-model="form.accuracy" /></el-form-item>
        <el-form-item label="安装日期"><el-date-picker v-model="form.install_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMeters, createMeter, updateMeter, deleteMeter, getEnergyTypes, getEnergyUnitTree } from '../../api'
import PageHeader from '../../components/PageHeader.vue'

const loading = ref(false); const saving = ref(false)
const items = ref([]); const energyTypes = ref([]); const unitTree = ref([])
const dialogVisible = ref(false); const formRef = ref(null)
const form = reactive({ id: null, code: '', name: '', energy_type_id: null, unit_id: null, meter_type: '', installation_location: '', accuracy: '', install_date: '', remark: '' })
const rules = { code: [{required:true,message:'请输入'}], name: [{required:true,message:'请输入'}], energy_type_id: [{required:true,message:'请选择'}], unit_id: [{required:true,message:'请选择'}] }

function energyTypeName(id) { return energyTypes.value.find(e => e.id === id)?.name || '' }
function unitName(id) { const find = (tree) => { for (const n of tree) { if (n.id === id) return n.name; if (n.children) { const r = find(n.children); if (r) return r } } return '' }; return find(unitTree.value) }

function showDialog(row) { if (row) { Object.assign(form, row) } else { Object.assign(form, { id:null, code:'', name:'', energy_type_id:null, unit_id:null, meter_type:'', installation_location:'', accuracy:'', install_date:'', remark:'' }) }; dialogVisible.value = true }

async function handleSave() { await formRef.value.validate(); saving.value = true; try { if (form.id) { await updateMeter(form.id, form) } else { await createMeter(form) }; ElMessage.success('保存成功'); dialogVisible.value = false; fetchData() } catch(e) {} finally { saving.value = false } }
async function handleDelete(id) { await ElMessageBox.confirm('确定删除？'); await deleteMeter(id); ElMessage.success('删除成功'); fetchData() }

async function fetchData() { loading.value = true; try { const r = await getMeters({page_size:999}); items.value = r.data||[] } catch(e) {} finally { loading.value = false } }

onMounted(async () => {
  try { const [r1, r2] = await Promise.all([getEnergyTypes({is_active:true}), getEnergyUnitTree()]); energyTypes.value = r1.data||[]; unitTree.value = r2.data||[] } catch(e) {}
  fetchData()
})
</script>
