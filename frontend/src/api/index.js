import request from './request'

// ==================== 认证 ====================
export const login = data => request.post('/auth/login', data)
export const getUserinfo = () => request.get('/auth/userinfo')
export const changePassword = data => request.post('/auth/change-password', data)

// ==================== 系统管理 ====================
export const getOrganization = () => request.get('/system/organization')
export const updateOrganization = (id, data) => request.put(`/system/organization/${id}`, data)

export const getEnergyTypes = params => request.get('/system/energy-types', { params })
export const createEnergyType = data => request.post('/system/energy-types', data)
export const updateEnergyType = (id, data) => request.put(`/system/energy-types/${id}`, data)
export const deleteEnergyType = id => request.delete(`/system/energy-types/${id}`)

export const getEnergyUnits = params => request.get('/system/energy-units', { params })
export const getEnergyUnitTree = () => request.get('/system/energy-units/tree')
export const createEnergyUnit = data => request.post('/system/energy-units', data)
export const updateEnergyUnit = (id, data) => request.put(`/system/energy-units/${id}`, data)
export const deleteEnergyUnit = id => request.delete(`/system/energy-units/${id}`)

export const getMeters = params => request.get('/system/meters', { params })
export const createMeter = data => request.post('/system/meters', data)
export const updateMeter = (id, data) => request.put(`/system/meters/${id}`, data)
export const deleteMeter = id => request.delete(`/system/meters/${id}`)

export const getProducts = params => request.get('/system/products', { params })
export const createProduct = data => request.post('/system/products', data)
export const updateProduct = (id, data) => request.put(`/system/products/${id}`, data)
export const deleteProduct = id => request.delete(`/system/products/${id}`)

export const getEmissionSources = params => request.get('/system/emission-sources', { params })
export const createEmissionSource = data => request.post('/system/emission-sources', data)
export const updateEmissionSource = (id, data) => request.put(`/system/emission-sources/${id}`, data)
export const deleteEmissionSource = id => request.delete(`/system/emission-sources/${id}`)

export const getCarbonFactors = params => request.get('/system/carbon-factors', { params })
export const createCarbonFactor = data => request.post('/system/carbon-factors', data)
export const updateCarbonFactor = (id, data) => request.put(`/system/carbon-factors/${id}`, data)
export const deleteCarbonFactor = id => request.delete(`/system/carbon-factors/${id}`)

export const getLogs = params => request.get('/system/logs', { params })

// ==================== 能源业务 ====================
export const getMeterReadings = params => request.get('/energy/meter-readings', { params })
export const createMeterReading = data => request.post('/energy/meter-readings', data)
export const updateMeterReading = (id, data) => request.put(`/energy/meter-readings/${id}`, data)
export const deleteMeterReading = id => request.delete(`/energy/meter-readings/${id}`)

export const getManualEntries = params => request.get('/energy/manual-entries', { params })
export const createManualEntry = data => request.post('/energy/manual-entries', data)
export const updateManualEntry = (id, data) => request.put(`/energy/manual-entries/${id}`, data)
export const deleteManualEntry = id => request.delete(`/energy/manual-entries/${id}`)

export const getProductionData = params => request.get('/energy/production-data', { params })
export const createProductionData = data => request.post('/energy/production-data', data)
export const updateProductionData = (id, data) => request.put(`/energy/production-data/${id}`, data)
export const deleteProductionData = id => request.delete(`/energy/production-data/${id}`)

export const getEfficiencyIndicators = () => request.get('/energy/efficiency-indicators')
export const createEfficiencyIndicator = data => request.post('/energy/efficiency-indicators', data)
export const deleteEfficiencyIndicator = id => request.delete(`/energy/efficiency-indicators/${id}`)

export const getEfficiencyAssessments = params => request.get('/energy/efficiency-assessments', { params })
export const createEfficiencyAssessment = data => request.post('/energy/efficiency-assessments', data)
export const deleteEfficiencyAssessment = id => request.delete(`/energy/efficiency-assessments/${id}`)

export const getEnergyFlowNodes = () => request.get('/energy/energy-flow/nodes')
export const createEnergyFlowNode = data => request.post('/energy/energy-flow/nodes', data)
export const deleteEnergyFlowNode = id => request.delete(`/energy/energy-flow/nodes/${id}`)

export const getEnergyFlowLinks = () => request.get('/energy/energy-flow/links')
export const createEnergyFlowLink = data => request.post('/energy/energy-flow/links', data)
export const deleteEnergyFlowLink = id => request.delete(`/energy/energy-flow/links/${id}`)

export const getEnergyBudgets = params => request.get('/energy/energy-budgets', { params })
export const createEnergyBudget = data => request.post('/energy/energy-budgets', data)
export const updateEnergyBudget = (id, data) => request.put(`/energy/energy-budgets/${id}`, data)
export const deleteEnergyBudget = id => request.delete(`/energy/energy-budgets/${id}`)

export const getCarbonBudgets = params => request.get('/energy/carbon-budgets', { params })
export const createCarbonBudget = data => request.post('/energy/carbon-budgets', data)
export const updateCarbonBudget = (id, data) => request.put(`/energy/carbon-budgets/${id}`, data)
export const deleteCarbonBudget = id => request.delete(`/energy/carbon-budgets/${id}`)

export const getComprehensive = params => request.get('/energy/comprehensive', { params })
export const getUnitStat = params => request.get('/energy/unit-stat', { params })
export const getMeterQuery = params => request.get('/energy/meter-query', { params })
export const getEfficiencyStat = params => request.get('/energy/efficiency-stat', { params })

// ==================== 碳业务 ====================
export const getCarbonAccounting = params => request.get('/carbon/accounting', { params })
export const createCarbonAccounting = data => request.post('/carbon/accounting', data)
export const updateCarbonAccounting = (id, data) => request.put(`/carbon/accounting/${id}`, data)
export const deleteCarbonAccounting = id => request.delete(`/carbon/accounting/${id}`)

export const getCarbonStatistics = params => request.get('/carbon/statistics', { params })
export const getCarbonReports = () => request.get('/carbon/reports')
export const generateCarbonReport = data => request.post('/carbon/reports/generate', data)
export const getCarbonReport = year => request.get(`/carbon/reports/${year}`)

export const getProductFootprints = params => request.get('/carbon/footprints', { params })
export const createProductFootprint = data => request.post('/carbon/footprints', data)
export const updateProductFootprint = (id, data) => request.put(`/carbon/footprints/${id}`, data)
export const deleteProductFootprint = id => request.delete(`/carbon/footprints/${id}`)

export const getSuppliers = () => request.get('/carbon/suppliers')
export const createSupplier = data => request.post('/carbon/suppliers', data)
export const updateSupplier = (id, data) => request.put(`/carbon/suppliers/${id}`, data)
export const deleteSupplier = id => request.delete(`/carbon/suppliers/${id}`)

export const getSupplierCarbonData = params => request.get('/carbon/supplier-carbon-data', { params })
export const createSupplierCarbonData = data => request.post('/carbon/supplier-carbon-data', data)
export const deleteSupplierCarbonData = id => request.delete(`/carbon/supplier-carbon-data/${id}`)

export const getCarbonVerifications = params => request.get('/carbon/verifications', { params })
export const createCarbonVerification = data => request.post('/carbon/verifications', data)
export const updateCarbonVerification = (id, data) => request.put(`/carbon/verifications/${id}`, data)
export const deleteCarbonVerification = id => request.delete(`/carbon/verifications/${id}`)

export const getCarbonAssets = params => request.get('/carbon/assets', { params })
export const createCarbonAsset = data => request.post('/carbon/assets', data)
export const updateCarbonAsset = (id, data) => request.put(`/carbon/assets/${id}`, data)
export const deleteCarbonAsset = id => request.delete(`/carbon/assets/${id}`)

export const getQuotaRecords = () => request.get('/carbon/quota-records')
export const createQuotaRecord = data => request.post('/carbon/quota-records', data)
export const deleteQuotaRecord = id => request.delete(`/carbon/quota-records/${id}`)

// ==================== 看板 ====================
export const getDashboardStats = params => request.get('/dashboard/stats', { params })
export const getRealtimeData = () => request.get('/dashboard/realtime')
