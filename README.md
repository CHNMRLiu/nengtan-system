# 数字化能碳管理系统

## 简介

数字化能碳管理系统是一款集能源消耗监控、碳排放核算、节能降碳决策支持于一体的本地化管理系统。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + Element Plus + ECharts |
| 后端 | Python FastAPI + SQLAlchemy |
| 数据库 | PostgreSQL 15 |
| 部署 | Docker Compose |

## 快速启动（Windows）

### 前置条件

1. 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. 启用 WSL2 后端
3. 配置国内镜像加速（可选，解决拉取超时）

### 启动步骤

```bash
# 克隆项目
git clone https://github.com/CHNMRLiu/nengtan-system.git
cd nengtan-system

# 一键启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 访问系统

- 前端地址：http://localhost:8080
- 后端API：http://localhost:8000/docs
- 默认账号：admin / admin123

## Linux 部署

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
pip install docker-compose

# 启动
docker-compose up -d
```

局域网内其他电脑通过 `http://服务器IP:8080` 访问。

## 功能模块

- 🏠 首页看板 - 年度能耗/碳排放总览
- 📊 数据大屏 - 全屏科技风数据展示
- ⚡ 能源消费 - 综合能耗/单元统计/计量查询/录接数据
- 📈 能源分析 - 计量对标/环比/单元对标/环比
- 🎯 能效对标 - 能效指标管理/能效测评
- 🌊 能流分析 - 桑基图/能效平衡
- 💰 预算管理 - 用能预算/碳排放预算
- 🌿 碳排放 - 碳排统计/碳报告/碳足迹/供应链/碳核查/碳资产
- ⚙️ 系统管理 - 企业信息/用能单元/表计/产品/排放源/碳因子/日志

## 数据备份

```bash
# 备份数据库
docker exec nengtan-db pg_dump -U nengtan nengtan > backup_$(date +%Y%m%d).sql

# 恢复数据库
cat backup.sql | docker exec -i nengtan-db psql -U nengtan nengtan
```

## 常用命令

```bash
# 查看容器状态
docker-compose ps

# 重启后端
docker-compose restart backend

# 查看后端日志
docker-compose logs -f backend

# 进入数据库
docker exec -it nengtan-db psql -U nengtan nengtan
```
