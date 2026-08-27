<template>
  <div>
    <PageHeader title="企业信息" />
    <el-card shadow="never">
      <el-form ref="formRef" :model="form" label-width="120px" style="max-width:600px">
        <el-form-item label="企业名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="统一信用代码"><el-input v-model="form.credit_code" /></el-form-item>
        <el-form-item label="所属行业"><el-input v-model="form.industry" /></el-form-item>
        <el-form-item label="企业地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="企业规模"><el-input v-model="form.scale" /></el-form-item>
        <el-form-item label="成立日期"><el-date-picker v-model="form.established_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getOrganization, updateOrganization } from '../../api'
import PageHeader from '../../components/PageHeader.vue'

const saving = ref(false)
const formRef = ref(null)
const form = reactive({ id: null, name: '', credit_code: '', industry: '', address: '', contact: '', phone: '', scale: '', established_date: '' })

async function handleSave() {
  saving.value = true
  try {
    await updateOrganization(form.id, form)
    ElMessage.success('保存成功')
  } catch(e) {} finally { saving.value = false }
}

onMounted(async () => {
  try {
    const res = await getOrganization()
    Object.assign(form, res.data)
  } catch(e) {}
})
</script>
