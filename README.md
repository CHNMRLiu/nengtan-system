# 数字化能碳管理系统

> 本地运行的能碳管理系统，包含 12 个核心业务模块 + 首页看板 + 数据大屏，Apple 官方设计风格。

## 快速启动（Windows）

### 前置条件

1. **安装 Docker Desktop**
   - 下载：https://www.docker.com/products/docker-desktop/
   - 安装时勾选 "Use WSL 2 instead of Hyper-V"
   - 安装后重启电脑，打开 Docker Desktop 等待引擎启动（系统托盘图标变绿）

2. **配置国内镜像加速**（可选，解决镜像拉取超时）
   
   Docker Desktop → Settings → Docker Engine，添加：
   ```json
   {
     "registry-mirrors": [
       "https://docker.1ms.run",
       "https://docker.xuanyuan.me"
     ]
   }
   ```
   点击 Apply & Restart。

### 启动步骤

```powershell
# 1. 打开 PowerShell，克隆项目
git clone https://github.com/CHNMRLiu/nengtan-system.git
cd nengtan-system

# 2. 一键启动（首次约需 3-5 分钟拉取镜像）
docker-compose up -d

# 3. 查看容器状态（3个容器都显示 Up 即为成功）
docker-compose ps
```

### 访问系统

| 地址 | 说明 |
|------|------|
| http://localhost:8080 | 前端页面 |
| http://localhost:8000/docs | 后端 API 文档（Swagger） |
| http://localhost:5432 | PostgreSQL 数据库 |

**默认账号**：`admin` / `admin123`

### 验证清单

启动后逐项验证：

- [ ] 访问 http://localhost:8080 看到登录页
- [ ] 用 admin/admin123 能登录
- [ ] 侧边栏菜单能正常展开折叠
- [ ] 系统管理 → 能源类型 能看到6种默认能源
- [ ] 系统管理 → 用能单元 能看到树形结构
- [ ] 录接数据 → 新增一条录入，综合能耗页面能看到统计
- [ ] 首页看板能显示图表（初始为空数据时显示空状态）
- [ ] 数据大屏能全屏显示（点击侧边栏"数据大屏"）

---

## Linux 部署

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# 重新登录

# 克隆并启动
git clone https://github.com/CHNMRLiu/nengtan-system.git
cd nengtan-system
docker-compose up -d
```

局域网访问：`http://服务器IP:8080`

---

## 功能模块

| 模块 | 功能 |
|------|------|
| 🏠 首页看板 | 年度能耗/碳排放总览、能源结构饼图、月度趋势 |
| 📊 数据大屏 | 全屏科技风、实时刷新、多图表联动 |
| ⚡ 能源消费 | 综合能耗、单元统计、计量查询、能效统计、生产数据、录接数据 |
| 📈 能源分析 | 计量对标/环比、单元对标/环比 |
| 🎯 能效对标 | 能效指标管理、能效测评（自动判定等级） |
| 🌊 能流分析 | 桑基图、能效平衡与优化建议 |
| 💰 预算管理 | 用能预算、碳排放预算（预算 vs 实际对比） |
| 🌿 碳排放 | 碳排统计、碳排报告、产品碳足迹、供应链碳管理、碳核查、碳资产 |
| ⚙️ 系统管理 | 企业信息、用能单元、表计、产品、排放源、碳因子、操作日志 |

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + Element Plus + ECharts |
| 后端 | Python FastAPI + SQLAlchemy + Pydantic |
| 数据库 | PostgreSQL 15 |
| 认证 | JWT (python-jose + bcrypt) |
| 部署 | Docker Compose (Nginx + Uvicorn + PostgreSQL) |

---

## 数据备份

```bash
# 备份
docker exec nengtan-db pg_dump -U nengtan nengtan > backup_$(date +%Y%m%d).sql

# 恢复
cat backup.sql | docker exec -i nengtan-db psql -U nengtan nengtan
```

## 常用命令

```bash
docker-compose ps              # 查看状态
docker-compose logs -f backend # 查看后端日志
docker-compose restart backend # 重启后端
docker-compose down            # 停止所有容器
docker-compose up -d           # 启动所有容器
docker exec -it nengtan-db psql -U nengtan nengtan  # 进入数据库
```

---

## 计算公式依据

| 计算 | 公式 | 依据 |
|------|------|------|
| 折标煤 | 消耗量 × 折标煤系数 | GB/T 2589《综合能耗计算通则》 |
| 碳排放 | 活动数据 × 排放因子 | 《企业温室气体排放核算方法与报告指南》 |
| 单位能耗 | 总能耗 / 总产量 | GB/T 2589 |
| 偏差率 | (实际值 - 基准值) / 基准值 × 100% | 能效对标通用方法 |
| 能效等级 | 领先(<-10%) / 先进(-10%~0%) / 合格(0%~20%) / 落后(≥20%) | 行业通行标准 |
