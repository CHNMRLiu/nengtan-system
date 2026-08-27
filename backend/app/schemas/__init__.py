from pydantic import BaseModel
from typing import Optional, List, Any

class ResponseModel(BaseModel):
    code: int = 200
    message: str = "ok"
    data: Any = None

class PageResponseModel(BaseModel):
    code: int = 200
    message: str = "ok"
    data: Any = None
    total: int = 0

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    username: str
    name: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class IdResponse(BaseModel):
    id: int

# ==================== 系统管理 ====================
class OrganizationCreate(BaseModel):
    name: str = ""
    credit_code: str = ""
    industry: str = ""
    address: str = ""
    contact: str = ""
    phone: str = ""
    scale: str = ""
    established_date: str = ""

class OrganizationUpdate(OrganizationCreate):
    pass

class EnergyTypeCreate(BaseModel):
    code: str
    name: str
    unit: str
    standard_coal_coefficient: float = 0
    carbon_factor: float = 0
    default_price: float = 0
    is_active: bool = True
    sort_order: int = 0

class EnergyTypeUpdate(EnergyTypeCreate):
    pass

class EnergyUnitCreate(BaseModel):
    code: str
    name: str
    parent_id: Optional[int] = None
    level: int = 1
    area: str = ""
    responsible_person: str = ""
    phone: str = ""
    is_active: bool = True
    sort_order: int = 0

class EnergyUnitUpdate(EnergyUnitCreate):
    pass

class MeterCreate(BaseModel):
    code: str
    name: str
    energy_type_id: int
    unit_id: int
    meter_type: str = ""
    installation_location: str = ""
    rated_voltage: str = ""
    current_ratio: str = ""
    voltage_ratio: str = ""
    accuracy: str = ""
    install_date: str = ""
    is_active: bool = True
    remark: str = ""

class MeterUpdate(MeterCreate):
    pass

class ProductCreate(BaseModel):
    code: str
    name: str
    unit: str = "吨"
    output_unit: str = "吨"
    is_active: bool = True
    sort_order: int = 0

class ProductUpdate(ProductCreate):
    pass

class EmissionSourceCreate(BaseModel):
    code: str
    name: str
    scope: str = "范围1"
    category: str = ""
    carbon_factor_id: Optional[int] = None
    is_active: bool = True
    sort_order: int = 0
    remark: str = ""

class EmissionSourceUpdate(EmissionSourceCreate):
    pass

class CarbonFactorCreate(BaseModel):
    name: str
    factor_value: float = 0
    unit: str = ""
    source: str = ""
    effective_date: str = ""
    is_active: bool = True
    sort_order: int = 0

class CarbonFactorUpdate(CarbonFactorCreate):
    pass

# ==================== 能源业务 ====================
class MeterReadingCreate(BaseModel):
    meter_id: int
    reading_time: str
    last_reading: float = 0
    current_reading: float = 0
    unit_price: float = 0
    recorder: str = ""
    remark: str = ""

class MeterReadingUpdate(MeterReadingCreate):
    pass

class ManualEntryCreate(BaseModel):
    energy_type_id: int
    unit_id: int
    meter_id: Optional[int] = None
    entry_date: str
    consumption: float = 0
    unit_price: float = 0
    recorder: str = ""
    remark: str = ""

class ManualEntryUpdate(ManualEntryCreate):
    pass

class ProductionDataCreate(BaseModel):
    product_id: int
    unit_id: int
    stat_date: str
    output: float = 0
    output_unit: str = "吨"
    output_value: float = 0
    period: str = "月"
    remark: str = ""

class ProductionDataUpdate(ProductionDataCreate):
    pass

class EfficiencyIndicatorCreate(BaseModel):
    name: str
    energy_type_id: int
    benchmark_value: float = 0
    target_value: float = 0
    unit: str = ""
    is_active: bool = True
    sort_order: int = 0

class EfficiencyIndicatorUpdate(EfficiencyIndicatorCreate):
    pass

class EfficiencyAssessmentCreate(BaseModel):
    indicator_id: int
    stat_date: str
    energy_consumption: float = 0
    output: float = 0
    remark: str = ""

class EfficiencyAssessmentUpdate(EfficiencyAssessmentCreate):
    pass

class EnergyFlowNodeCreate(BaseModel):
    name: str
    node_type: str
    sort_order: int = 0
    remark: str = ""

class EnergyFlowNodeUpdate(EnergyFlowNodeCreate):
    pass

class EnergyFlowLinkCreate(BaseModel):
    source_node_id: int
    target_node_id: int
    flow_value: float = 0
    unit: str = "kWh"
    loss_rate: float = 0
    remark: str = ""

class EnergyFlowLinkUpdate(EnergyFlowLinkCreate):
    pass

class EnergyBudgetCreate(BaseModel):
    year: int
    month: Optional[int] = None
    energy_type_id: int
    unit_id: int
    budget_value: float = 0
    unit_consumption: float = 0
    planned_output: float = 0
    source_type: str = "手工填写"
    remark: str = ""

class EnergyBudgetUpdate(EnergyBudgetCreate):
    pass

class CarbonBudgetCreate(BaseModel):
    year: int
    month: Optional[int] = None
    unit_id: int
    budget_carbon: float = 0
    carbon_intensity: float = 0
    intensity_type: str = "产值强度"
    planned_output: float = 0
    remark: str = ""

class CarbonBudgetUpdate(CarbonBudgetCreate):
    pass

# ==================== 碳业务 ====================
class CarbonAccountingCreate(BaseModel):
    source_id: int
    year: int
    month: int
    activity_data: float = 0
    unit: str = ""
    emission_factor: float = 0
    data_source: str = "手工录入"
    remark: str = ""

class CarbonAccountingUpdate(CarbonAccountingCreate):
    pass

class CarbonReportCreate(BaseModel):
    year: int
    measures: str = ""
    next_plan: str = ""

class ProductFootprintCreate(BaseModel):
    product_id: int
    functional_unit: str = ""
    boundary: str = "从摇篮到大门"
    raw_material: float = 0
    production: float = 0
    transport: float = 0
    use_phase: float = 0
    disposal: float = 0
    assessment_date: str = ""
    data_source: str = ""

class ProductFootprintUpdate(ProductFootprintCreate):
    pass

class SupplierCreate(BaseModel):
    name: str
    credit_code: str = ""
    contact_person: str = ""
    phone: str = ""
    category: str = "原材料"
    risk_level: str = "低"
    address: str = ""

class SupplierUpdate(SupplierCreate):
    pass

class SupplierCarbonDataCreate(BaseModel):
    supplier_id: int
    year: int
    material_name: str = ""
    quantity: float = 0
    unit: str = ""
    emission_factor: float = 0
    data_source: str = "默认因子"

class SupplierCarbonDataUpdate(SupplierCarbonDataCreate):
    pass

class CarbonVerificationCreate(BaseModel):
    year: int
    verification_agency: str = ""
    verifier: str = ""
    start_date: str = ""
    end_date: str = ""
    reported_emission: float = 0
    verified_emission: float = 0
    status: str = "待核查"
    conclusion: str = ""
    evidence_hash: str = ""

class CarbonVerificationUpdate(CarbonVerificationCreate):
    pass

class CarbonAssetCreate(BaseModel):
    asset_type: str = "配额"
    year: int
    project_name: str = ""
    quantity: float = 0
    used_quantity: float = 0
    acquisition_date: str = ""
    expiry_date: str = ""
    status: str = "有效"

class CarbonAssetUpdate(CarbonAssetCreate):
    pass

class QuotaRecordCreate(BaseModel):
    trade_date: str
    trade_type: str = "买入"
    quantity: float = 0
    price: float = 0
    market: str = "全国碳市场"
    remark: str = ""

class QuotaRecordUpdate(QuotaRecordCreate):
    pass
