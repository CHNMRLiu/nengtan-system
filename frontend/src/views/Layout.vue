<template>
  <div class="layout">
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-header">
        <span class="sidebar-logo">⚡</span>
        <span v-show="!isCollapsed" class="sidebar-title">能碳管理</span>
      </div>
      <el-scrollbar>
        <el-menu :default-active="activeMenu" :collapse="isCollapsed" router
          background-color="#1D1D1F" text-color="#D2D2D7" active-text-color="#fff"
          :collapse-transition="false">
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>首页看板</span>
          </el-menu-item>
          <el-menu-item index="/screen" @click="openScreen">
            <el-icon><Monitor /></el-icon>
            <span>数据大屏</span>
          </el-menu-item>
          <el-divider style="border-color:#3A3A3C;margin:4px 16px" />
          <el-sub-menu index="energy-menu">
            <template #title>
              <el-icon><Lightning /></el-icon>
              <span>能源消费</span>
            </template>
            <el-menu-item index="/energy/comprehensive">综合能耗</el-menu-item>
            <el-menu-item index="/energy/unit-stat">单元统计</el-menu-item>
            <el-menu-item index="/energy/meter-query">计量查询</el-menu-item>
            <el-menu-item index="/energy/unit-query">单元查询</el-menu-item>
            <el-menu-item index="/energy/efficiency">能效统计</el-menu-item>
            <el-menu-item index="/energy/production">生产数据</el-menu-item>
            <el-menu-item index="/energy/manual-entry">录接数据</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="analysis-menu">
            <template #title>
              <el-icon><TrendCharts /></el-icon>
              <span>能源分析</span>
            </template>
            <el-menu-item index="/analysis/meter-compare">计量对标</el-menu-item>
            <el-menu-item index="/analysis/meter-ratio">计量环比</el-menu-item>
            <el-menu-item index="/analysis/unit-ratio">单元环比</el-menu-item>
            <el-menu-item index="/analysis/unit-compare">单元对标</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="/efficiency/assessment">
            <el-icon><Aim /></el-icon>
            <span>能效对标</span>
          </el-menu-item>
          <el-sub-menu index="flow-menu">
            <template #title>
              <el-icon><Share /></el-icon>
              <span>能流分析</span>
            </template>
            <el-menu-item index="/energy-flow">能流桑基图</el-menu-item>
            <el-menu-item index="/energy-balance">能效平衡</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="budget-menu">
            <template #title>
              <el-icon><Money /></el-icon>
              <span>预算管理</span>
            </template>
            <el-menu-item index="/budget/energy">用能预算</el-menu-item>
            <el-menu-item index="/budget/carbon">碳排放预算</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="carbon-menu">
            <template #title>
              <el-icon><CloudyAndSunny /></el-icon>
              <span>碳排放</span>
            </template>
            <el-menu-item index="/carbon/statistics">碳排统计</el-menu-item>
            <el-menu-item index="/carbon/report">碳排报告</el-menu-item>
            <el-menu-item index="/carbon/footprint">产品碳足迹</el-menu-item>
            <el-menu-item index="/carbon/supply-chain">供应链碳管理</el-menu-item>
            <el-menu-item index="/carbon/verification">碳核查支撑</el-menu-item>
            <el-menu-item index="/carbon/assets">碳资产管理</el-menu-item>
          </el-sub-menu>
          <el-sub-menu index="system-menu">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/system/organization">企业信息</el-menu-item>
            <el-menu-item index="/system/unit-manage">用能单元管理</el-menu-item>
            <el-menu-item index="/system/meter-manage">表计管理</el-menu-item>
            <el-menu-item index="/system/product-manage">产品管理</el-menu-item>
            <el-menu-item index="/system/source-manage">排放源管理</el-menu-item>
            <el-menu-item index="/system/factor-manage">碳因子管理</el-menu-item>
            <el-menu-item index="/system/logs">操作日志</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>
    </aside>
    <div class="main-area">
      <header class="topbar">
        <div class="topbar-left">
          <el-icon class="collapse-btn" @click="isCollapsed = !isCollapsed">
            <Fold v-if="!isCollapsed" /><Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="topbar-right">
          <span class="user-name">{{ userStore.name || userStore.username }}</span>
          <el-button text @click="handleLogout">退出</el-button>
        </div>
      </header>
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import {
  HomeFilled, Monitor, Lightning, TrendCharts, Aim, Share, Money,
  Setting, Fold, Expand, CloudyAndSunny
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isCollapsed = ref(false)

const activeMenu = computed(() => route.path)

function openScreen() {
  window.open('/screen', '_blank')
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: 220px;
  background: #1D1D1F;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}
.sidebar.collapsed {
  width: 64px;
}
.sidebar-header {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 10px;
  border-bottom: 1px solid #3A3A3C;
}
.sidebar-logo {
  font-size: 24px;
}
.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}
.sidebar :deep(.el-menu) {
  border-right: none;
}
.sidebar :deep(.el-menu-item.is-active) {
  background: #0071E3 !important;
}
.sidebar :deep(.el-menu-item:hover) {
  background: #2A2A2C !important;
}
.sidebar :deep(.el-sub-menu__title:hover) {
  background: #2A2A2C !important;
}
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.topbar {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #E8E8ED;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}
.topbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #6E6E73;
}
.collapse-btn:hover {
  color: #0071E3;
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.user-name {
  font-size: 14px;
  color: #1D1D1F;
}
.content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  background: #F5F5F7;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
