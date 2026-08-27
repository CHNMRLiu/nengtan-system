<template>
  <div>
    <PageHeader title="排放源管理"><template #actions><el-button type="primary" @click="showDialog()">新增排放源</el-button></template></PageHeader>
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="code" label="编码" width="100" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="scope" label="范围" width="80" align="center"><template #default="{row}"><el-tag :type="row.scope==='范围1'?'danger':row.scope==='范围2'?'warning':'success'" size="small">{{ row.scope }}</el-tag></template></el-table-column>
        <el-table-column prop="category" label="类别" width="100" />
        <el-table-column prop="is_active" label="状态" width="80" align="center"><template #default="{row}"><el-tag :type="row.is_active?'success':'info'" size="small">{{ row.is_active?'启用':'停用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="140" align="center"><template #default="{row}"><el-button text type="primary" size="small" @click="showDialog(row)">编辑</el-button><el-button text type="danger" size="small" @click="handleDelete(row.id)">删除</el-button></template></el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="form.id?'编辑排放源':'新增排放源'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="编码" prop="code"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="范围" prop="scope"><el-select v-model="form.scope" style="width:100%"><el-option label="范围1" value="范围1" /><el-option label="范围2" value="范围2" /><el-option label="范围3" value="范围3" /></el-select></el-form-item>
        <el-form-item label="类别"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="关联碳因子"><el-select v-model="form.carbon_factor_id" clearable style="width:100%"><el-option v-for="f in factors" :key="f.id" :label="f.name" :value="f.id" /></el-select></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEmissionSources, createEmissionSource, updateEmissionSource, deleteEmissionSource, getCarbonFactors } from '../../api'
import PageHeader from '../../components/PageHeader.vue'

const loading = ref(false); const saving = ref(false)
const items = ref([]); const factors = ref([])
const dialogVisible = ref(false); const formRef = ref(null)
const form = reactive({ id: null, code: '', name: '', scope: '范围1', category: '', carbon_factor_id: null, remark: '' })
const rules = { code: [{required:true,message:'请输入'}], name: [{required:true,message:'请输入'}] }

function showDialog(row) { if (row) { Object.assign(form, row) } else { Object.assign(form, { id:null, code:'', name:'', scope:'范围1', category:'', carbon_factor_id:null, remark:'' }) }; dialogVisible.value = true }

async function handleSave() { await formRef.value.validate(); saving.value = true; try { if (form.id) { await updateEmissionSource(form.id, form) } else { await createEmissionSource(form) }; ElMessage.success('保存成功'); dialogVisible.value = false; fetchData() } catch(e) {} finally { saving.value = false } }
async function handleDelete(id) { await ElMessageBox.confirm('确定删除？'); await deleteEmissionSource(id); ElMessage.success('删除成功'); fetchData() }

async function fetchData() { loading.value = true; try { const r = await getEmissionSources(); items.value = r.data||[] } catch(e) {} finally { loading.value = false } }

onMounted(async () => { try { const r = await getCarbonFactors({is_active:true}); factors.value = r.data||[] } catch(e) {}; fetchData() })
</script>
