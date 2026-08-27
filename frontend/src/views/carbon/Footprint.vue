<template>
  <div>
    <PageHeader title="产品碳足迹"><template #actions><el-button type="primary" @click="showDialog()">新增足迹</el-button></template></PageHeader>
    <el-card shadow="never" style="margin-bottom:16px"><ChartCard title="各产品碳足迹对比" :option="chartOption" :height="300" /></el-card>
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="product_name" label="产品" />
        <el-table-column prop="functional_unit" label="功能单位" />
        <el-table-column prop="raw_material" label="原材料" align="right"><template #default="{row}"><span class="num">{{ row.raw_material.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="production" label="生产" align="right"><template #default="{row}"><span class="num">{{ row.production.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="transport" label="运输" align="right"><template #default="{row}"><span class="num">{{ row.transport.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="use_phase" label="使用阶段" align="right"><template #default="{row}"><span class="num">{{ row.use_phase.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="disposal" label="废弃处理" align="right"><template #default="{row}"><span class="num">{{ row.disposal.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="total" label="合计(kgCO₂e)" align="right"><template #default="{row}"><span class="num" style="color:#FF3B30;font-weight:700">{{ row.total.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
        <el-table-column prop="assessment_date" label="评估日期" width="110" />
        <el-table-column label="操作" width="100" align="center"><template #default="{row}"><el-button text type="primary" size="small" @click="showDetail(row)">详情</el-button></template></el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" title="新增产品碳足迹" width="550px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="产品" prop="product_id"><el-select v-model="form.product_id" style="width:100%"><el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" /></el-select></el-form-item>
        <el-form-item label="功能单位"><el-input v-model="form.functional_unit" placeholder="如：1台、1kg" /></el-form-item>
        <el-form-item label="系统边界"><el-select v-model="form.boundary" style="width:100%"><el-option label="从摇篮到大门" value="从摇篮到大门" /><el-option label="从摇篮到坟墓" value="从摇篮到坟墓" /></el-select></el-form-item>
        <el-form-item label="原材料(kgCO₂e)"><el-input-number v-model="form.raw_material" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="生产(kgCO₂e)"><el-input-number v-model="form.production" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="运输(kgCO₂e)"><el-input-number v-model="form.transport" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="使用阶段(kgCO₂e)"><el-input-number v-model="form.use_phase" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="废弃处理(kgCO₂e)"><el-input-number v-model="form.disposal" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="评估日期"><el-date-picker v-model="form.assessment_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="数据来源"><el-input v-model="form.data_source" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave" :loading="saving">保存</el-button></template>
    </el-dialog>
    <el-dialog v-model="detailVisible" title="碳足迹详情" width="500px">
      <el-descriptions :column="1" border v-if="detailItem">
        <el-descriptions-item label="产品">{{ detailItem.product_name }}</el-descriptions-item>
        <el-descriptions-item label="功能单位">{{ detailItem.functional_unit }}</el-descriptions-item>
        <el-descriptions-item label="系统边界">{{ detailItem.boundary }}</el-descriptions-item>
        <el-descriptions-item label="原材料">{{ detailItem.raw_material }} kgCO₂e</el-descriptions-item>
        <el-descriptions-item label="生产">{{ detailItem.production }} kgCO₂e</el-descriptions-item>
        <el-descriptions-item label="运输">{{ detailItem.transport }} kgCO₂e</el-descriptions-item>
        <el-descriptions-item label="使用阶段">{{ detailItem.use_phase }} kgCO₂e</el-descriptions-item>
        <el-descriptions-item label="废弃处理">{{ detailItem.disposal }} kgCO₂e</el-descriptions-item>
        <el-descriptions-item label="合计"><span style="color:#FF3B30;font-weight:700">{{ detailItem.total }} kgCO₂e</span></el-descriptions-item>
      </el-descriptions>
      <ChartCard v-if="detailItem" title="阶段占比" :option="detailPieOption" :height="250" style="margin-top:16px" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getProductFootprints, createProductFootprint, getProducts } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import ChartCard from '../../components/ChartCard.vue'

const loading = ref(false); const saving = ref(false)
const items = ref([]); const products = ref([])
const dialogVisible = ref(false); const detailVisible = ref(false)
const formRef = ref(null); const detailItem = ref(null)
const form = reactive({ product_id: null, functional_unit: '', boundary: '从摇篮到大门', raw_material: 0, production: 0, transport: 0, use_phase: 0, disposal: 0, assessment_date: '', data_source: '' })
const rules = { product_id: [{required:true,message:'请选择'}] }

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: items.value.map(i=>i.product_name), axisLabel: { color: '#6E6E73' } },
  yAxis: { type: 'value', name: 'kgCO₂e', axisLabel: { color: '#6E6E73' }, splitLine: { lineStyle: { type: 'dashed', color: '#E8E8ED' } } },
  grid: { left: '3%', right: '3%', bottom: '3%', containLabel: true },
  series: [{ type: 'bar', data: items.value.map(i=>i.total), barWidth: '40%', itemStyle: { color: '#0071E3', borderRadius: [4,4,0,0] } }],
}))

const detailPieOption = computed(() => {
  if (!detailItem.value) return {}
  const d = detailItem.value
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} kgCO₂e ({d}%)' },
    legend: { bottom: 0, textStyle: { color: '#6E6E73' } },
    series: [{ type: 'pie', radius: ['45%', '70%'], data: [
      { name: '原材料', value: d.raw_material }, { name: '生产', value: d.production },
      { name: '运输', value: d.transport }, { name: '使用阶段', value: d.use_phase }, { name: '废弃处理', value: d.disposal },
    ], itemStyle: { borderRadius: 4 } }],
    color: ['#0071E3', '#34C759', '#FF9500', '#AF52DE', '#FF2D55'],
  }
})

function showDialog() { Object.assign(form, { product_id:null, functional_unit:'', boundary:'从摇篮到大门', raw_material:0, production:0, transport:0, use_phase:0, disposal:0, assessment_date:'', data_source:'' }); dialogVisible.value = true }
function showDetail(row) { detailItem.value = row; detailVisible.value = true }

async function handleSave() { await formRef.value.validate(); saving.value = true; try { await createProductFootprint(form); ElMessage.success('创建成功'); dialogVisible.value = false; fetchData() } catch(e) {} finally { saving.value = false } }

async function fetchData() { loading.value = true; try { const res = await getProductFootprints(); items.value = res.data||[] } catch(e) {} finally { loading.value = false } }

onMounted(async () => { try { const r = await getProducts(); products.value = r.data||[] } catch(e) {}; fetchData() })
</script>
