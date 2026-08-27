<template>
  <div>
    <PageHeader title="能效统计" />
    <el-card shadow="never" style="margin-bottom:16px">
      <el-form :inline="true">
        <el-form-item label="产品">
          <el-select v-model="query.product_id" placeholder="全部" clearable style="width:180px">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD" style="width:260px" />
        </el-form-item>
        <el-form-item><el-button type="primary" @click="fetchData">查询</el-button></el-form-item>
      </el-form>
    </el-card>
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="product_name" label="产品" />
        <el-table-column prop="unit_name" label="用能单元" />
        <el-table-column prop="stat_date" label="统计日期" />
        <el-table-column prop="output" label="产量" align="right"><template #default="{row}"><span class="num">{{ row.output.toLocaleString() }}</span></template></el-table-column>
        <el-table-column prop="total_energy" label="总能耗(kgce)" align="right"><template #default="{row}"><span class="num">{{ row.total_energy.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
        <el-table-column prop="unit_energy" label="单位能耗" align="right"><template #default="{row}"><span class="num">{{ row.unit_energy.toLocaleString('zh-CN',{minimumFractionDigits:4}) }}</span></template></el-table-column>
      </el-table>
      <el-empty v-if="!loading && items.length === 0" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { getEfficiencyStat, getProducts } from '../../api'
import PageHeader from '../../components/PageHeader.vue'

const loading = ref(false)
const products = ref([])
const items = ref([])
const dateRange = ref(null)
const query = reactive({ product_id: null })
watch(dateRange, v => { query.start_date = v?v[0]:null; query.end_date = v?v[1]:null })

async function fetchData() {
  loading.value = true
  try { const res = await getEfficiencyStat(query); items.value = res.data || [] } catch(e) {} finally { loading.value = false }
}

onMounted(async () => {
  try { const r = await getProducts(); products.value = r.data || [] } catch(e) {}
  fetchData()
})
</script>
