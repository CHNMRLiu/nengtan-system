<template>
  <div>
    <PageHeader title="碳资产管理">
      <template #actions>
        <el-select v-model="selectedYear" placeholder="年度" style="width:100px;margin-right:8px"><el-option v-for="y in years" :key="y" :label="y" :value="y" /></el-select>
        <el-button type="primary" @click="showAssetDialog()">登记资产</el-button>
        <el-button type="primary" @click="showTradeDialog()">配额交易</el-button>
      </template>
    </PageHeader>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6"><StatCard label="碳配额总量" :value="assets.total_quantity" unit="tCO₂e" color="#0071E3" :decimals="6" /></el-col>
      <el-col :span="6"><StatCard label="已使用量" :value="assets.total_used" unit="tCO₂e" color="#FF9500" :decimals="6" /></el-col>
      <el-col :span="6"><StatCard label="剩余可用量" :value="assets.remaining" unit="tCO₂e" color="#34C759" :decimals="6" /></el-col>
      <el-col :span="6"><StatCard label="交易记录" :value="trades.length" unit="条" color="#AF52DE" :decimals="0" /></el-col>
    </el-row>
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header><span style="font-weight:600">碳资产明细</span></template>
          <el-table :data="assets.items" border stripe>
            <el-table-column prop="asset_type" label="资产类型" width="80" align="center">
              <template #default="{row}"><el-tag :type="row.asset_type==='配额'?'':'success'" size="small">{{ row.asset_type }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="project_name" label="项目/批次" />
            <el-table-column prop="quantity" label="数量(t)" align="right"><template #default="{row}"><span class="num">{{ row.quantity.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
            <el-table-column prop="used_quantity" label="已使用(t)" align="right"><template #default="{row}"><span class="num">{{ row.used_quantity.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
            <el-table-column prop="acquisition_date" label="获取日期" width="110" />
            <el-table-column prop="expiry_date" label="有效期至" width="110" />
            <el-table-column prop="status" label="状态" width="80" align="center">
              <template #default="{row}"><el-tag :type="row.status==='有效'?'success':row.status==='已用完'?'info':'danger'" size="small">{{ row.status }}</el-tag></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never">
          <template #header><span style="font-weight:600">配额交易记录</span></template>
          <el-table :data="trades" border stripe size="small">
            <el-table-column prop="trade_date" label="日期" width="100" />
            <el-table-column prop="trade_type" label="类型" width="60" align="center">
              <template #default="{row}"><el-tag :type="row.trade_type==='买入'?'success':'danger'" size="small">{{ row.trade_type }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量(t)" align="right"><template #default="{row}"><span class="num">{{ row.quantity.toLocaleString() }}</span></template></el-table-column>
            <el-table-column prop="total_amount" label="金额(元)" align="right"><template #default="{row}"><span class="num">{{ row.total_amount.toLocaleString('zh-CN',{minimumFractionDigits:2}) }}</span></template></el-table-column>
            <el-table-column prop="market" label="市场" width="80" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    <el-dialog v-model="assetDialogVisible" title="登记碳资产" width="450px" destroy-on-close>
      <el-form ref="assetFormRef" :model="assetForm" :rules="{year:[{required:true,message:'请选择'}]}" label-width="90px">
        <el-form-item label="资产类型"><el-select v-model="assetForm.asset_type" style="width:100%"><el-option label="配额" value="配额" /><el-option label="CCER" value="CCER" /></el-select></el-form-item>
        <el-form-item label="年度" prop="year"><el-date-picker v-model="assetForm.year" type="year" value-format="YYYY" /></el-form-item>
        <el-form-item label="项目名称"><el-input v-model="assetForm.project_name" /></el-form-item>
        <el-form-item label="数量(t)"><el-input-number v-model="assetForm.quantity" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="获取日期"><el-date-picker v-model="assetForm.acquisition_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="有效期至"><el-date-picker v-model="assetForm.expiry_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="状态"><el-select v-model="assetForm.status" style="width:100%"><el-option label="有效" value="有效" /><el-option label="已用完" value="已用完" /><el-option label="已过期" value="已过期" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="assetDialogVisible=false">取消</el-button><el-button type="primary" @click="saveAsset">保存</el-button></template>
    </el-dialog>
    <el-dialog v-model="tradeDialogVisible" title="配额交易" width="450px" destroy-on-close>
      <el-form ref="tradeFormRef" :model="tradeForm" :rules="{trade_date:[{required:true,message:'请选择'}]}" label-width="90px">
        <el-form-item label="交易类型"><el-select v-model="tradeForm.trade_type" style="width:100%"><el-option label="买入" value="买入" /><el-option label="卖出" value="卖出" /></el-select></el-form-item>
        <el-form-item label="交易日期" prop="trade_date"><el-date-picker v-model="tradeForm.trade_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="数量(t)"><el-input-number v-model="tradeForm.quantity" :precision="6" style="width:100%" /></el-form-item>
        <el-form-item label="单价(元)"><el-input-number v-model="tradeForm.price" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="交易市场"><el-select v-model="tradeForm.market" style="width:100%"><el-option v-for="m in ['全国碳市场','上海','广东','湖北']" :key="m" :label="m" :value="m" /></el-select></el-form-item>
        <el-form-item label="备注"><el-input v-model="tradeForm.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="tradeDialogVisible=false">取消</el-button><el-button type="primary" @click="saveTrade">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getCarbonAssets, createCarbonAsset, getQuotaRecords, createQuotaRecord } from '../../api'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'

const selectedYear = ref(new Date().getFullYear())
const years = ref([])
const assets = reactive({ total_quantity: 0, total_used: 0, remaining: 0, items: [] })
const trades = ref([])
const assetDialogVisible = ref(false); const tradeDialogVisible = ref(false)
const assetFormRef = ref(null); const tradeFormRef = ref(null)
const assetForm = reactive({ asset_type: '配额', year: '', project_name: '', quantity: 0, acquisition_date: '', expiry_date: '', status: '有效' })
const tradeForm = reactive({ trade_type: '买入', trade_date: '', quantity: 0, price: 0, market: '全国碳市场', remark: '' })

function showAssetDialog() { Object.assign(assetForm, { asset_type:'配额', year:selectedYear.value.toString(), project_name:'', quantity:0, acquisition_date:'', expiry_date:'', status:'有效' }); assetDialogVisible.value = true }
function showTradeDialog() { Object.assign(tradeForm, { trade_type:'买入', trade_date:'', quantity:0, price:0, market:'全国碳市场', remark:'' }); tradeDialogVisible.value = true }

async function saveAsset() { await assetFormRef.value.validate(); await createCarbonAsset(assetForm); ElMessage.success('登记成功'); assetDialogVisible.value = false; loadAll() }
async function saveTrade() { await tradeFormRef.value.validate(); await createQuotaRecord(tradeForm); ElMessage.success('交易记录创建成功'); tradeDialogVisible.value = false; loadAll() }

async function loadAll() {
  try { const [r1, r2] = await Promise.all([getCarbonAssets({year:selectedYear.value}), getQuotaRecords()]); Object.assign(assets, r1.data||{total_quantity:0,total_used:0,remaining:0,items:[]}); trades.value = r2.data||[] } catch(e) {}
}

watch(selectedYear, loadAll)

onMounted(async () => {
  const now = new Date().getFullYear()
  years.value = Array.from({length:5}, (_,i) => now - i)
  loadAll()
})
</script>
