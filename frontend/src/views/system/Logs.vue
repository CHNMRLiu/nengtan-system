<template>
  <div>
    <PageHeader title="操作日志" />
    <el-card shadow="never">
      <el-table :data="items" border stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="username" label="用户" width="100" />
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="action" label="操作" />
        <el-table-column prop="ip" label="IP地址" width="130" />
        <el-table-column prop="created_at" label="操作时间" width="170" />
      </el-table>
      <el-pagination v-if="total>0" :current-page="page" :page-size="pageSize" :total="total" @current-change="p=>{page=p;fetchData()}" layout="total,prev,pager,next" style="margin-top:16px;justify-content:flex-end" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLogs } from '../../api'
import PageHeader from '../../components/PageHeader.vue'

const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20

async function fetchData() {
  loading.value = true
  try { const res = await getLogs({ page: page.value, page_size: pageSize }); items.value = res.data || []; total.value = res.total } catch(e) {} finally { loading.value = false }
}

onMounted(fetchData)
</script>
