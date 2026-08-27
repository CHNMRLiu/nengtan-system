<template>
  <div>
    <PageHeader title="能流桑基图">
      <template #actions>
        <el-button type="primary" @click="showNodeDialog()">新增节点</el-button>
        <el-button type="primary" @click="showLinkDialog()">新增连接</el-button>
      </template>
    </PageHeader>
    <el-row :gutter="16">
      <el-col :span="14">
        <ChartCard title="能流图" :option="sankeyOption" :height="500" />
      </el-col>
      <el-col :span="10">
        <el-card shadow="never" style="margin-bottom:16px">
          <template #header><span style="font-weight:600">节点列表</span></template>
          <el-table :data="nodes" border stripe size="small" max-height="200">
            <el-table-column prop="name" label="节点名称" />
            <el-table-column prop="node_type" label="类型" width="80">
              <template #default="{row}"><el-tag :type="nodeTypeColor(row.node_type)" size="small">{{ row.node_type }}</el-tag></template>
            </el-table-column>
            <el-table-column label="操作" width="60" align="center">
              <template #default="{row}"><el-button text type="danger" size="small" @click="deleteNode(row.id)">删除</el-button></template>
            </el-table-column>
          </el-table>
        </el-card>
        <el-card shadow="never">
          <template #header><span style="font-weight:600">连接列表</span></template>
          <el-table :data="links" border stripe size="small" max-height="200">
            <el-table-column prop="source_name" label="源节点" />
            <el-table-column prop="target_name" label="目标节点" />
            <el-table-column prop="flow_value" label="能流量" align="right" />
            <el-table-column label="操作" width="60" align="center">
              <template #default="{row}"><el-button text type="danger" size="small" @click="deleteLink(row.id)">删除</el-button></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="nodeDialogVisible" title="新增节点" width="400px" destroy-on-close>
      <el-form ref="nodeFormRef" :model="nodeForm" :rules="{name:[{required:true,message:'请输入'}],node_type:[{required:true,message:'请选择'}]}" label-width="80px">
        <el-form-item label="名称" prop="name"><el-input v-model="nodeForm.name" /></el-form-item>
        <el-form-item label="类型" prop="node_type"><el-select v-model="nodeForm.node_type" style="width:100%"><el-option v-for="t in ['输入','转换','分配','利用','损失']" :key="t" :label="t" :value="t" /></el-select></el-form-item>
        <el-form-item label="排序号"><el-input-number v-model="nodeForm.sort_order" :min="0" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="nodeDialogVisible=false">取消</el-button><el-button type="primary" @click="saveNode">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="linkDialogVisible" title="新增连接" width="400px" destroy-on-close>
      <el-form ref="linkFormRef" :model="linkForm" :rules="{source_node_id:[{required:true,message:'请选择'}],target_node_id:[{required:true,message:'请选择'}]}" label-width="80px">
        <el-form-item label="源节点" prop="source_node_id"><el-select v-model="linkForm.source_node_id" style="width:100%"><el-option v-for="n in nodes" :key="n.id" :label="n.name" :value="n.id" /></el-select></el-form-item>
        <el-form-item label="目标节点" prop="target_node_id"><el-select v-model="linkForm.target_node_id" style="width:100%"><el-option v-for="n in nodes" :key="n.id" :label="n.name" :value="n.id" /></el-select></el-form-item>
        <el-form-item label="能流量"><el-input-number v-model="linkForm.flow_value" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="linkForm.unit" /></el-form-item>
        <el-form-item label="损耗率%"><el-input-number v-model="linkForm.loss_rate" :min="0" :max="100" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="linkDialogVisible=false">取消</el-button><el-button type="primary" @click="saveLink">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEnergyFlowNodes, createEnergyFlowNode, deleteEnergyFlowNode, getEnergyFlowLinks, createEnergyFlowLink, deleteEnergyFlowLink } from '../api'
import PageHeader from '../components/PageHeader.vue'
import ChartCard from '../components/ChartCard.vue'

const nodes = ref([]); const links = ref([])
const nodeDialogVisible = ref(false); const linkDialogVisible = ref(false)
const nodeFormRef = ref(null); const linkFormRef = ref(null)
const nodeForm = reactive({ name: '', node_type: '输入', sort_order: 0 })
const linkForm = reactive({ source_node_id: null, target_node_id: null, flow_value: 0, unit: 'kWh', loss_rate: 0 })

const nodeColors = { '输入': '#0071E3', '转换': '#FF9500', '分配': '#86868B', '利用': '#34C759', '损失': '#FF3B30' }
function nodeTypeColor(t) { return { '输入':'', '转换':'warning', '分配':'info', '利用':'success', '损失':'danger' }[t] || 'info' }

const sankeyOption = computed(() => {
  if (nodes.value.length === 0 || links.value.length === 0) return {}
  return {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'sankey',
      layout: 'none',
      emphasis: { focus: 'adjacency' },
      nodeAlign: 'left',
      data: nodes.value.map(n => ({ name: n.name, itemStyle: { color: nodeColors[n.node_type] || '#86868B' } })),
      links: links.value.map(l => ({ source: l.source_name, target: l.target_name, value: l.flow_value })),
      lineStyle: { color: 'gradient', curveness: 0.5 },
    }],
  }
})

function showNodeDialog() { Object.assign(nodeForm, { name:'', node_type:'输入', sort_order:0 }); nodeDialogVisible.value = true }
function showLinkDialog() { Object.assign(linkForm, { source_node_id:null, target_node_id:null, flow_value:0, unit:'kWh', loss_rate:0 }); linkDialogVisible.value = true }

async function saveNode() {
  await nodeFormRef.value.validate()
  await createEnergyFlowNode(nodeForm); ElMessage.success('创建成功'); nodeDialogVisible.value = false; loadAll()
}
async function saveLink() {
  await linkFormRef.value.validate()
  await createEnergyFlowLink(linkForm); ElMessage.success('创建成功'); linkDialogVisible.value = false; loadAll()
}
async function deleteNode(id) { await ElMessageBox.confirm('确定删除？'); await deleteEnergyFlowNode(id); ElMessage.success('删除成功'); loadAll() }
async function deleteLink(id) { await ElMessageBox.confirm('确定删除？'); await deleteEnergyFlowLink(id); ElMessage.success('删除成功'); loadAll() }

async function loadAll() {
  try { const [r1, r2] = await Promise.all([getEnergyFlowNodes(), getEnergyFlowLinks()]); nodes.value = r1.data||[]; links.value = r2.data||[] } catch(e) {}
}

onMounted(loadAll)
</script>
