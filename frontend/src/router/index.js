import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { noAuth: true } },
  {
    path: '/', component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '首页看板' } },
      { path: 'energy/comprehensive', name: 'Comprehensive', component: () => import('../views/energy/Comprehensive.vue'), meta: { title: '综合能耗' } },
      { path: 'energy/unit-stat', name: 'UnitStat', component: () => import('../views/energy/UnitStat.vue'), meta: { title: '单元统计' } },
      { path: 'energy/meter-query', name: 'MeterQuery', component: () => import('../views/energy/MeterQuery.vue'), meta: { title: '计量查询' } },
      { path: 'energy/unit-query', name: 'UnitQuery', component: () => import('../views/energy/UnitQuery.vue'), meta: { title: '单元查询' } },
      { path: 'energy/efficiency', name: 'EfficiencyStat', component: () => import('../views/energy/EfficiencyStat.vue'), meta: { title: '能效统计' } },
      { path: 'energy/production', name: 'Production', component: () => import('../views/energy/Production.vue'), meta: { title: '生产数据' } },
      { path: 'energy/manual-entry', name: 'ManualEntry', component: () => import('../views/energy/ManualEntry.vue'), meta: { title: '录接数据' } },
      { path: 'analysis/meter-compare', name: 'MeterCompare', component: () => import('../views/analysis/MeterCompare.vue'), meta: { title: '计量对标' } },
      { path: 'analysis/meter-ratio', name: 'MeterRatio', component: () => import('../views/analysis/MeterRatio.vue'), meta: { title: '计量环比' } },
      { path: 'analysis/unit-ratio', name: 'UnitRatio', component: () => import('../views/analysis/UnitRatio.vue'), meta: { title: '单元环比' } },
      { path: 'analysis/unit-compare', name: 'UnitCompare', component: () => import('../views/analysis/UnitCompare.vue'), meta: { title: '单元对标' } },
      { path: 'efficiency/assessment', name: 'Assessment', component: () => import('../views/efficiency/Assessment.vue'), meta: { title: '能效测评' } },
      { path: 'energy-flow', name: 'EnergyFlow', component: () => import('../views/EnergyFlow.vue'), meta: { title: '能流桑基图' } },
      { path: 'energy-balance', name: 'EnergyBalance', component: () => import('../views/EnergyBalance.vue'), meta: { title: '能效平衡' } },
      { path: 'budget/energy', name: 'EnergyBudget', component: () => import('../views/budget/Energy.vue'), meta: { title: '用能预算' } },
      { path: 'budget/carbon', name: 'CarbonBudget', component: () => import('../views/budget/Carbon.vue'), meta: { title: '碳排放预算' } },
      { path: 'carbon/statistics', name: 'CarbonStatistics', component: () => import('../views/carbon/Statistics.vue'), meta: { title: '碳排统计' } },
      { path: 'carbon/report', name: 'CarbonReport', component: () => import('../views/carbon/Report.vue'), meta: { title: '碳排报告' } },
      { path: 'carbon/footprint', name: 'Footprint', component: () => import('../views/carbon/Footprint.vue'), meta: { title: '产品碳足迹' } },
      { path: 'carbon/supply-chain', name: 'SupplyChain', component: () => import('../views/carbon/SupplyChain.vue'), meta: { title: '供应链碳管理' } },
      { path: 'carbon/verification', name: 'Verification', component: () => import('../views/carbon/Verification.vue'), meta: { title: '碳核查支撑' } },
      { path: 'carbon/assets', name: 'CarbonAssets', component: () => import('../views/carbon/Assets.vue'), meta: { title: '碳资产管理' } },
      { path: 'system/organization', name: 'Organization', component: () => import('../views/system/Organization.vue'), meta: { title: '企业信息' } },
      { path: 'system/unit-manage', name: 'UnitManage', component: () => import('../views/system/UnitManage.vue'), meta: { title: '用能单元管理' } },
      { path: 'system/meter-manage', name: 'MeterManage', component: () => import('../views/system/MeterManage.vue'), meta: { title: '表计管理' } },
      { path: 'system/product-manage', name: 'ProductManage', component: () => import('../views/system/ProductManage.vue'), meta: { title: '产品管理' } },
      { path: 'system/source-manage', name: 'SourceManage', component: () => import('../views/system/SourceManage.vue'), meta: { title: '排放源管理' } },
      { path: 'system/factor-manage', name: 'FactorManage', component: () => import('../views/system/FactorManage.vue'), meta: { title: '碳因子管理' } },
      { path: 'system/logs', name: 'Logs', component: () => import('../views/system/Logs.vue'), meta: { title: '操作日志' } },
    ],
  },
  { path: '/screen', name: 'Screen', component: () => import('../views/Screen.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.meta.noAuth) return next()
  const token = localStorage.getItem('token')
  if (!token) return next('/login')
  next()
})

export default router
