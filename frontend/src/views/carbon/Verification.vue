<template>
  <div>
    <PageHeader title="碳核查支撑"><template #actions><el-button type="primary" @click="showDialog()">新增核查记录</el-button></template></PageHeader>
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="核查年度"><el-date-picker v-model="filters.year" type="year" value-format="YYYY" placeholder="全部" clearable style="width:120px" /></el-form-item>
        <el-form-item label="核查状态"><el-select v-model="filters.status" clearable placeholder="全部" style="width:120px"><el-option v-for="s in ['待核查','核查中','已完成','有异议']" :key="s" :label="s" :value="s" /></el-select></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData">查询</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6"><StatCard label="核查记录总数" :value="items.length" color="#0071E3" :decimals="0" /></el-col>
      <el-col :span="6"><StatCard label="已完成" :value="items.filter(i=>i.status==='已完成').length" color="#34C759" :decimals="0" /></el-col>
      <el-col :span="6"><StatCard label="核查中" :value="items.filter(i=>i.status==='核查中').length" color="#FF9500" :decimals="0" /></el-col>
      <el-col :span="6"><StatCard label="有异议" :value="items.filter(i=>i.status==='有异议').length" color="#FF3B30" :decimals="0" /></el-col>
    </el-row>
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="year" label="年度" width="80" />
        <el-table-column prop="verification_agency" label="核查机构" />
        <el-table-column prop="verifier" label="核查员" width="80" />
        <el-table-column prop="start_date" label="开始日期" width="110" />
        <el-table-column prop="end_date" label="结束日期" width="110" />
        <el-table-column prop="reported_emission" label="申报排放(t)" align="right"><template #default="{row}"><span class="num">{{ row.reported_emission.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="verified_emission" label="核查排放(t)" align="right"><template #default="{row}"><span class="num">{{ row.verified_emission.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="deviation" label="偏差%" align="right"><template #default="{row}"><span :style="{color:Math.abs(row.deviation)>5?'#FF3B30':'#1D1D1F'}">{{ row.deviation }}%</span></template></el-table-column>
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{row}"><el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{row}"><el-button text type="primary" size="small" @click="showDetail(row)">详情</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" title="新增核查记录" width="550px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="{year:[{required:true,message:'请选择'}]}" label-width="100px">
        <el-form-item label="年度" prop="year"><el-date-picker v-model="form.year" type="year" value-format="YYYY" /></el-form-item>
        <el-form-item label="核查机构"><el-input v-model="form.verification_agency" /></el-form-item>
        <el-form-item label="核查员"><el-input v-model="form.verifier" /></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.status" style="width:100%"><el-option v-for="s in ['待核查','核查中','已完成','有异议']" :key="s" :label="s" :value="s" /></el-select></el-form-item>
        <el-form-item label="开始日期"><el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="结束日期"><el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="申报排放量"><el-input-number v-model="form.reported_emission" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="核查排放量"><el-input-number v-model="form.verified_emission" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="核查结论"><el-input v-model="form.conclusion" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="存证哈希"><el-input v-model="form.evidence_hash" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
    <el-dialog v-model="detailVisible" title="核查详情" width="500px">
      <el-descriptions :column="1" border v-if="detailItem">
        <el-descriptions-item label="年度">{{ detailItem.year }}</el-descriptions-item>
        <el-descriptions-item label="核查机构">{{ detailItem.verification_agency }}</el-descriptions-item>
        <el-descriptions-item label="核查员">{{ detailItem.verifier }}</el-descriptions-item>
        <el-descriptions-item label="核查周期">{{ detailItem.start_date }} ~ {{ detailItem.end_date }}</el-descriptions-item>
        <el-descriptions-item label="申报排放量">{{ detailItem.reported_emission }} tCO₂e</el-descriptions-item>
        <el-descriptions-item label="核查排放量">{{ detailItem.verified_emission }} tCO₂e</el-descriptions-item>
        <el-descriptions-item label="偏差率"><span :style="{color:Math.abs(detailItem.deviation)>5?'#FF3B30':'#1D1D1F'}">{{ detailItem.deviation }}%</span></el-descriptions-item>
        <el-descriptions-item label="状态"><el-tag :type="statusType(detailItem.status)">{{ detailItem.status }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="核查结论">{{ detailItem.conclusion || '暂无' }}</el-descriptions-item>
        <el-descriptions-item label="存证哈希">{{ detailItem.evidence_hash || '暂无' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCarbonVerifications, createCarbonVerification } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'

const loading = ref(false); const saving = ref(false)
const items = ref([]); const filters = reactive({ year: '', status: '' })
const dialogVisible = ref(false); const detailVisible = ref(false)
const formRef = ref(null); const detailItem = ref(null)
const form = reactive({ year: '', verification_agency: '', verifier: '', start_date: '', end_date: '', reported_emission: 0, verified_emission: 0, status: '待核查', conclusion: '', evidence_hash: '' })

function statusType(s) { return { '待核查':'info', '核查中':'warning', '已完成':'success', '有异议':'danger' }[s] || 'info' }

function showDialog() { Object.assign(form, { year:'', verification_agency:'', verifier:'', start_date:'', end_date:'', reported_emission:0, verified_emission:0, status:'待核查', conclusion:'', evidence_hash:'' }); dialogVisible.value = true }
function showDetail(row) { detailItem.value = row; detailVisible.value = true }

async function handleSave() { await formRef.value.validate(); saving.value = true; try { await createCarbonVerification(form); ElMessage.success('创建成功'); dialogVisible.value = false; fetchData() } catch(e) {} finally { saving.value = false } }

async function fetchData() { loading.value = true; try { const res = await getCarbonVerifications(filters); items.value = res.data||[] } catch(e) {} finally { loading.value = false } }

onMounted(fetchData)
</script>
