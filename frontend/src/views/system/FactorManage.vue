<template>
  <div>
    <PageHeader title="碳因子管理"><template #actions><el-button type="primary" @click="showDialog()">新增碳因子</el-button></template></PageHeader>
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="因子名称" />
        <el-table-column prop="factor_value" label="因子值" align="right"><template #default="{row}"><span class="num">{{ row.factor_value }}</span></template></el-table-column>
        <el-table-column prop="unit" label="单位" width="120" />
        <el-table-column prop="source" label="来源" />
        <el-table-column prop="effective_date" label="生效日期" width="110" />
        <el-table-column prop="is_active" label="状态" width="80" align="center"><template #default="{row}"><el-tag :type="row.is_active?'success':'info'" size="small">{{ row.is_active?'启用':'停用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="140" align="center"><template #default="{row}"><el-button text type="primary" size="small" @click="showDialog(row)">编辑</el-button><el-button text type="danger" size="small" @click="handleDelete(row.id)">删除</el-button></template></el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="form.id?'编辑碳因子':'新增碳因子'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="因子名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="因子值" prop="factor_value"><el-input-number v-model="form.factor_value" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="form.unit" /></el-form-item>
        <el-form-item label="来源"><el-input v-model="form.source" /></el-form-item>
        <el-form-item label="生效日期"><el-date-picker v-model="form.effective_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCarbonFactors, createCarbonFactor, updateCarbonFactor, deleteCarbonFactor } from '../../api'
import PageHeader from '../../components/PageHeader.vue'

const loading = ref(false); const saving = ref(false)
const items = ref([]); const dialogVisible = ref(false); const formRef = ref(null)
const form = reactive({ id: null, name: '', factor_value: 0, unit: '', source: '', effective_date: '' })
const rules = { name: [{required:true,message:'请输入'}], factor_value: [{required:true,message:'请输入'}] }

function showDialog(row) { if (row) { Object.assign(form, row) } else { Object.assign(form, { id:null, name:'', factor_value:0, unit:'', source:'', effective_date:'' }) }; dialogVisible.value = true }

async function handleSave() { await formRef.value.validate(); saving.value = true; try { if (form.id) { await updateCarbonFactor(form.id, form) } else { await createCarbonFactor(form) }; ElMessage.success('保存成功'); dialogVisible.value = false; fetchData() } catch(e) {} finally { saving.value = false } }
async function handleDelete(id) { await ElMessageBox.confirm('确定删除？'); await deleteCarbonFactor(id); ElMessage.success('删除成功'); fetchData() }

async function fetchData() { loading.value = true; try { const r = await getCarbonFactors(); items.value = r.data||[] } catch(e) {} finally { loading.value = false } }
onMounted(fetchData)
</script>
