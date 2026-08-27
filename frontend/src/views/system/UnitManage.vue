<template>
  <div>
    <PageHeader title="用能单元管理"><template #actions><el-button type="primary" @click="showDialog()">新增单元</el-button></template></PageHeader>
    <el-card shadow="never">
      <el-table :data="treeData" border stripe row-key="id" :tree-props="{children:'children'}" v-loading="loading">
        <el-table-column prop="name" label="单元名称" min-width="200" />
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="level" label="层级" width="80" align="center"><template #default="{row}">{{ row.level===1?'车间':'工序' }}</template></el-table-column>
        <el-table-column prop="area" label="区域" width="100" />
        <el-table-column prop="responsible_person" label="负责人" width="80" />
        <el-table-column prop="phone" label="电话" width="120" />
        <el-table-column label="操作" width="140" align="center">
          <template #default="{row}">
            <el-button text type="primary" size="small" @click="showDialog(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="form.id?'编辑单元':'新增单元'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="编码" prop="code"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="上级单元"><el-tree-select v-model="form.parent_id" :data="treeData" :props="{label:'name',value:'id',children:'children'}" clearable check-strictly placeholder="无（顶级）" style="width:100%" /></el-form-item>
        <el-form-item label="层级"><el-select v-model="form.level" style="width:100%"><el-option label="车间" :value="1" /><el-option label="工序" :value="2" /></el-select></el-form-item>
        <el-form-item label="区域"><el-input v-model="form.area" /></el-form-item>
        <el-form-item label="负责人"><el-input v-model="form.responsible_person" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEnergyUnitTree, createEnergyUnit, updateEnergyUnit, deleteEnergyUnit } from '../../api'
import PageHeader from '../../components/PageHeader.vue'

const loading = ref(false); const saving = ref(false)
const treeData = ref([])
const dialogVisible = ref(false); const formRef = ref(null)
const form = reactive({ id: null, code: '', name: '', parent_id: null, level: 1, area: '', responsible_person: '', phone: '' })
const rules = { code: [{required:true,message:'请输入'}], name: [{required:true,message:'请输入'}] }

function showDialog(row) {
  if (row) { Object.assign(form, row) } else { Object.assign(form, { id:null, code:'', name:'', parent_id:null, level:1, area:'', responsible_person:'', phone:'' }) }
  dialogVisible.value = true
}

async function handleSave() {
  await formRef.value.validate(); saving.value = true
  try {
    if (form.id) { await updateEnergyUnit(form.id, form) } else { await createEnergyUnit(form) }
    ElMessage.success('保存成功'); dialogVisible.value = false; fetchData()
  } catch(e) {} finally { saving.value = false }
}

async function handleDelete(id) { await ElMessageBox.confirm('确定删除？'); await deleteEnergyUnit(id); ElMessage.success('删除成功'); fetchData() }

async function fetchData() { loading.value = true; try { const r = await getEnergyUnitTree(); treeData.value = r.data||[] } catch(e) {} finally { loading.value = false } }

onMounted(fetchData)
</script>
