<template>
  <div>
    <PageHeader title="单元查询" />
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="用能单元" required>
          <el-tree-select v-model="query.unit_id" :data="unitTree" :props="{label:'name',value:'id',children:'children'}" placeholder="请选择" clearable check-strictly style="width:200px" />
        </el-form-item>
        <el-form-item label="统计维度">
          <el-select v-model="query.stat_type" style="width:120px">
            <el-option label="能耗" value="consumption" /><el-option label="成本" value="cost" />
            <el-option label="标准煤" value="standard_coal" /><el-option label="碳排放" value="carbon_emission" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:260px" />
        </el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData" :disabled="!query.unit_id">查询</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card shadow="never" style="margin-bottom:16px">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="time" label="时间" />
        <el-table-column prop="consumption" label="消耗量" align="right"><template #default="{row}"><span class="num">{{ row.consumption.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="cost" label="费用(元)" align="right"><template #default="{row}"><span class="num">{{ row.cost.toLocaleString('zh-CN',{minimumFractionDigits:2}) }}</span></template></el-table-column>
        <el-table-column prop="standard_coal" label="折标煤" align="right"><template #default="{row}"><span class="num">{{ row.standard_coal.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="carbon_emission" label="碳排放" align="right"><template #default="{row}"><span class="num">{{ row.carbon_emission.toLocaleString('zh-CN',{minimumFractionDigits:6}) }}</span></template></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { getUnitStat, getEnergyUnitTree } from '../../api'
import PageHeader from '../../components/PageHeader.vue'

const loading = ref(false)
const unitTree = ref([])
const dateRange = ref(null)
const items = ref([])
const query = reactive({ unit_id: null, stat_type: 'consumption', period: 'month' })
watch(dateRange, v => { query.start_date = v?v[0]:null; query.end_date = v?v[1]:null })

async function fetchData() {
  if (!query.unit_id) return
  loading.value = true
  try { const res = await getUnitStat(query); items.value = res.data.items || [] } catch(e) {} finally { loading.value = false }
}

onMounted(async () => {
  try { const r = await getEnergyUnitTree(); unitTree.value = r.data } catch(e) {}
})
</script>
