from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract

from app.database import get_db
from app.models import (
    MeterReading, ManualEntry, ProductionData, EfficiencyIndicator,
    EfficiencyAssessment, EnergyFlowNode, EnergyFlowLink, EnergyBudget,
    CarbonBudget, Meter, EnergyType, EnergyUnit, Product
)
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas import (
    ResponseModel, MeterReadingCreate, MeterReadingUpdate,
    ManualEntryCreate, ManualEntryUpdate, ProductionDataCreate, ProductionDataUpdate,
    EfficiencyIndicatorCreate, EfficiencyIndicatorUpdate,
    EfficiencyAssessmentCreate, EfficiencyAssessmentUpdate,
    EnergyFlowNodeCreate, EnergyFlowNodeUpdate,
    EnergyFlowLinkCreate, EnergyFlowLinkUpdate,
    EnergyBudgetCreate, EnergyBudgetUpdate,
    CarbonBudgetCreate, CarbonBudgetUpdate,
)
from app.utils.calculator import (
    calc_cost, calc_standard_coal, calc_carbon_emission,
    calc_unit_consumption, calc_deviation, get_efficiency_level,
    calc_budget_value, calc_carbon_budget, calc_execution_rate
)

router = APIRouter()


def success(data=None, message="操作成功", total=0):
    return ResponseModel(code=200, message=message, data=data, total=total)


def error(message="操作失败", code=400):
    return ResponseModel(code=code, message=message)


def _get_energy_type_info(db: Session, energy_type_id: int):
    et = db.query(EnergyType).filter(EnergyType.id == energy_type_id).first()
    if not et:
        return None
    return {
        "id": et.id, "code": et.code, "name": et.name, "unit": et.unit,
        "standard_coal_coefficient": float(et.standard_coal_coefficient),
        "carbon_factor": float(et.carbon_factor), "default_price": float(et.default_price),
    }


# ==================== 表计读数 ====================
@router.get("/meter-readings", response_model=ResponseModel)
def list_meter_readings(
    meter_id: int = None, start_date: str = None, end_date: str = None,
    page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
):
    q = db.query(MeterReading)
    if meter_id:
        q = q.filter(MeterReading.meter_id == meter_id)
    if start_date:
        q = q.filter(MeterReading.reading_time >= start_date)
    if end_date:
        q = q.filter(MeterReading.reading_time <= end_date)
    total = q.count()
    items = q.order_by(desc(MeterReading.reading_time)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for i in items:
        meter = db.query(Meter).filter(Meter.id == i.meter_id).first()
        et = db.query(EnergyType).filter(EnergyType.id == meter.energy_type_id).first() if meter else None
        unit = db.query(EnergyUnit).filter(EnergyUnit.id == meter.unit_id).first() if meter else None
        result.append({
            "id": i.id, "meter_id": i.meter_id,
            "meter_name": meter.name if meter else "",
            "energy_type_name": et.name if et else "",
            "unit_name": unit.name if unit else "",
            "reading_time": i.reading_time,
            "last_reading": float(i.last_reading), "current_reading": float(i.current_reading),
            "consumption": float(i.consumption), "unit_price": float(i.unit_price),
            "cost": float(i.cost), "standard_coal": float(i.standard_coal),
            "carbon_emission": float(i.carbon_emission),
            "recorder": i.recorder, "remark": i.remark,
            "created_at": i.created_at.strftime("%Y-%m-%d %H:%M:%S") if i.created_at else "",
        })
    return success(data=result, total=total)


@router.post("/meter-readings", response_model=ResponseModel)
def create_meter_reading(req: MeterReadingCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    meter = db.query(Meter).filter(Meter.id == req.meter_id).first()
    if not meter:
        return error("表计不存在")
    et = _get_energy_type_info(db, meter.energy_type_id)
    if not et:
        return error("能源类型不存在")

    consumption = req.current_reading - req.last_reading
    if consumption < 0:
        return error("本次读数不能小于上次读数")

    cost = calc_cost(consumption, req.unit_price)
    standard_coal = calc_standard_coal(consumption, et["standard_coal_coefficient"])
    carbon_emission = calc_carbon_emission(consumption, et["carbon_factor"])

    item = MeterReading(
        meter_id=req.meter_id, reading_time=req.reading_time,
        last_reading=req.last_reading, current_reading=req.current_reading,
        consumption=consumption, unit_price=req.unit_price,
        cost=cost, standard_coal=standard_coal, carbon_emission=carbon_emission,
        recorder=req.recorder, remark=req.remark,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="录入成功")


@router.put("/meter-readings/{item_id}", response_model=ResponseModel)
def update_meter_reading(item_id: int, req: MeterReadingCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    item = db.query(MeterReading).filter(MeterReading.id == item_id).first()
    if not item:
        return error("读数记录不存在")
    meter = db.query(Meter).filter(Meter.id == req.meter_id).first()
    if not meter:
        return error("表计不存在")
    et = _get_energy_type_info(db, meter.energy_type_id)

    consumption = req.current_reading - req.last_reading
    if consumption < 0:
        return error("本次读数不能小于上次读数")

    cost = calc_cost(consumption, req.unit_price)
    standard_coal = calc_standard_coal(consumption, et["standard_coal_coefficient"]) if et else 0
    carbon_emission = calc_carbon_emission(consumption, et["carbon_factor"]) if et else 0

    item.meter_id = req.meter_id
    item.reading_time = req.reading_time
    item.last_reading = req.last_reading
    item.current_reading = req.current_reading
    item.consumption = consumption
    item.unit_price = req.unit_price
    item.cost = cost
    item.standard_coal = standard_coal
    item.carbon_emission = carbon_emission
    item.recorder = req.recorder
    item.remark = req.remark
    db.commit()
    return success(message="更新成功")


@router.delete("/meter-readings/{item_id}", response_model=ResponseModel)
def delete_meter_reading(item_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    item = db.query(MeterReading).filter(MeterReading.id == item_id).first()
    if not item:
        return error("读数记录不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 手工录接 ====================
@router.get("/manual-entries", response_model=ResponseModel)
def list_manual_entries(
    energy_type_id: int = None, unit_id: int = None,
    start_date: str = None, end_date: str = None,
    page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
):
    q = db.query(ManualEntry)
    if energy_type_id:
        q = q.filter(ManualEntry.energy_type_id == energy_type_id)
    if unit_id:
        q = q.filter(ManualEntry.unit_id == unit_id)
    if start_date:
        q = q.filter(ManualEntry.entry_date >= start_date)
    if end_date:
        q = q.filter(ManualEntry.entry_date <= end_date)
    total = q.count()
    items = q.order_by(desc(ManualEntry.entry_date)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for i in items:
        et = db.query(EnergyType).filter(EnergyType.id == i.energy_type_id).first()
        unit = db.query(EnergyUnit).filter(EnergyUnit.id == i.unit_id).first()
        result.append({
            "id": i.id, "energy_type_id": i.energy_type_id, "unit_id": i.unit_id,
            "energy_type_name": et.name if et else "", "unit_name": unit.name if unit else "",
            "entry_date": i.entry_date, "consumption": float(i.consumption),
            "unit_price": float(i.unit_price), "cost": float(i.cost),
            "standard_coal": float(i.standard_coal), "carbon_emission": float(i.carbon_emission),
            "data_source": i.data_source, "recorder": i.recorder, "remark": i.remark,
        })
    return success(data=result, total=total)


@router.post("/manual-entries", response_model=ResponseModel)
def create_manual_entry(req: ManualEntryCreate, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    et = _get_energy_type_info(db, req.energy_type_id)
    if not et:
        return error("能源类型不存在")

    cost = calc_cost(req.consumption, req.unit_price if req.unit_price > 0 else et["default_price"])
    price = req.unit_price if req.unit_price > 0 else et["default_price"]
    cost = calc_cost(req.consumption, price)
    standard_coal = calc_standard_coal(req.consumption, et["standard_coal_coefficient"])
    carbon_emission = calc_carbon_emission(req.consumption, et["carbon_factor"])

    item = ManualEntry(
        energy_type_id=req.energy_type_id, unit_id=req.unit_id,
        meter_id=req.meter_id, entry_date=req.entry_date,
        consumption=req.consumption, unit_price=price,
        cost=cost, standard_coal=standard_coal, carbon_emission=carbon_emission,
        data_source=req.data_source or "手工录入", recorder=req.recorder, remark=req.remark,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="录入成功")


@router.put("/manual-entries/{item_id}", response_model=ResponseModel)
def update_manual_entry(item_id: int, req: ManualEntryCreate, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    item = db.query(ManualEntry).filter(ManualEntry.id == item_id).first()
    if not item:
        return error("记录不存在")
    et = _get_energy_type_info(db, req.energy_type_id)

    price = req.unit_price if req.unit_price > 0 else (et["default_price"] if et else 0)
    cost = calc_cost(req.consumption, price)
    standard_coal = calc_standard_coal(req.consumption, et["standard_coal_coefficient"]) if et else 0
    carbon_emission = calc_carbon_emission(req.consumption, et["carbon_factor"]) if et else 0

    for k, v in req.model_dump().items():
        setattr(item, k, v)
    item.unit_price = price
    item.cost = cost
    item.standard_coal = standard_coal
    item.carbon_emission = carbon_emission
    db.commit()
    return success(message="更新成功")


@router.delete("/manual-entries/{item_id}", response_model=ResponseModel)
def delete_manual_entry(item_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    item = db.query(ManualEntry).filter(ManualEntry.id == item_id).first()
    if not item:
        return error("记录不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 生产数据 ====================
@router.get("/production-data", response_model=ResponseModel)
def list_production_data(
    product_id: int = None, unit_id: int = None, period: str = None,
    start_date: str = None, end_date: str = None,
    page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
):
    q = db.query(ProductionData)
    if product_id:
        q = q.filter(ProductionData.product_id == product_id)
    if unit_id:
        q = q.filter(ProductionData.unit_id == unit_id)
    if period:
        q = q.filter(ProductionData.period == period)
    if start_date:
        q = q.filter(ProductionData.stat_date >= start_date)
    if end_date:
        q = q.filter(ProductionData.stat_date <= end_date)
    total = q.count()
    items = q.order_by(desc(ProductionData.stat_date)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for i in items:
        prod = db.query(Product).filter(Product.id == i.product_id).first()
        unit = db.query(EnergyUnit).filter(EnergyUnit.id == i.unit_id).first()
        result.append({
            "id": i.id, "product_id": i.product_id, "unit_id": i.unit_id,
            "product_name": prod.name if prod else "", "unit_name": unit.name if unit else "",
            "stat_date": i.stat_date, "output": float(i.output),
            "output_unit": i.output_unit, "output_value": float(i.output_value),
            "period": i.period, "remark": i.remark,
        })
    return success(data=result, total=total)


@router.post("/production-data", response_model=ResponseModel)
def create_production_data(req: ProductionDataCreate, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    item = ProductionData(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="录入成功")


@router.put("/production-data/{item_id}", response_model=ResponseModel)
def update_production_data(item_id: int, req: ProductionDataUpdate, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    item = db.query(ProductionData).filter(ProductionData.id == item_id).first()
    if not item:
        return error("记录不存在")
    for k, v in req.model_dump().items():
        setattr(item, k, v)
    db.commit()
    return success(message="更新成功")


@router.delete("/production-data/{item_id}", response_model=ResponseModel)
def delete_production_data(item_id: int, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    item = db.query(ProductionData).filter(ProductionData.id == item_id).first()
    if not item:
        return error("记录不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 能效指标 ====================
@router.get("/efficiency-indicators", response_model=ResponseModel)
def list_efficiency_indicators(db: Session = Depends(get_db)):
    items = db.query(EfficiencyIndicator).order_by(EfficiencyIndicator.sort_order).all()
    result = []
    for i in items:
        et = db.query(EnergyType).filter(EnergyType.id == i.energy_type_id).first()
        result.append({
            "id": i.id, "name": i.name, "energy_type_id": i.energy_type_id,
            "energy_type_name": et.name if et else "",
            "benchmark_value": float(i.benchmark_value), "target_value": float(i.target_value),
            "unit": i.unit, "is_active": i.is_active,
        })
    return success(data=result)


@router.post("/efficiency-indicators", response_model=ResponseModel)
def create_efficiency_indicator(req: EfficiencyIndicatorCreate, db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    item = EfficiencyIndicator(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="创建成功")


@router.delete("/efficiency-indicators/{item_id}", response_model=ResponseModel)
def delete_efficiency_indicator(item_id: int, db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    item = db.query(EfficiencyIndicator).filter(EfficiencyIndicator.id == item_id).first()
    if not item:
        return error("指标不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 能效测评 ====================
@router.get("/efficiency-assessments", response_model=ResponseModel)
def list_efficiency_assessments(
    indicator_id: int = None, start_date: str = None, end_date: str = None,
    page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
):
    q = db.query(EfficiencyAssessment)
    if indicator_id:
        q = q.filter(EfficiencyAssessment.indicator_id == indicator_id)
    if start_date:
        q = q.filter(EfficiencyAssessment.stat_date >= start_date)
    if end_date:
        q = q.filter(EfficiencyAssessment.stat_date <= end_date)
    total = q.count()
    items = q.order_by(desc(EfficiencyAssessment.stat_date)).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for i in items:
        ind = db.query(EfficiencyIndicator).filter(EfficiencyIndicator.id == i.indicator_id).first()
        result.append({
            "id": i.id, "indicator_id": i.indicator_id,
            "indicator_name": ind.name if ind else "",
            "stat_date": i.stat_date, "energy_consumption": float(i.energy_consumption),
            "output": float(i.output), "actual_value": float(i.actual_value),
            "benchmark_value": float(i.benchmark_value), "deviation": float(i.deviation),
            "level": i.level, "remark": i.remark,
        })
    return success(data=result, total=total)


@router.post("/efficiency-assessments", response_model=ResponseModel)
def create_efficiency_assessment(req: EfficiencyAssessmentCreate, db: Session = Depends(get_db),
                                 current_user: User = Depends(get_current_user)):
    ind = db.query(EfficiencyIndicator).filter(EfficiencyIndicator.id == req.indicator_id).first()
    if not ind:
        return error("测评指标不存在")

    actual_value = calc_unit_consumption(req.energy_consumption, req.output)
    deviation = calc_deviation(actual_value, float(ind.benchmark_value))
    level = get_efficiency_level(deviation)

    item = EfficiencyAssessment(
        indicator_id=req.indicator_id, stat_date=req.stat_date,
        energy_consumption=req.energy_consumption, output=req.output,
        actual_value=actual_value, benchmark_value=float(ind.benchmark_value),
        deviation=deviation, level=level, remark=req.remark,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="测评创建成功")


@router.delete("/efficiency-assessments/{item_id}", response_model=ResponseModel)
def delete_efficiency_assessment(item_id: int, db: Session = Depends(get_db),
                                 current_user: User = Depends(get_current_user)):
    item = db.query(EfficiencyAssessment).filter(EfficiencyAssessment.id == item_id).first()
    if not item:
        return error("测评记录不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 能流节点 ====================
@router.get("/energy-flow/nodes", response_model=ResponseModel)
def list_energy_flow_nodes(db: Session = Depends(get_db)):
    items = db.query(EnergyFlowNode).order_by(EnergyFlowNode.sort_order).all()
    return success(data=[{
        "id": i.id, "name": i.name, "node_type": i.node_type,
        "sort_order": i.sort_order, "remark": i.remark,
    } for i in items])


@router.post("/energy-flow/nodes", response_model=ResponseModel)
def create_energy_flow_node(req: EnergyFlowNodeCreate, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    item = EnergyFlowNode(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="创建成功")


@router.delete("/energy-flow/nodes/{item_id}", response_model=ResponseModel)
def delete_energy_flow_node(item_id: int, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    item = db.query(EnergyFlowNode).filter(EnergyFlowNode.id == item_id).first()
    if not item:
        return error("节点不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 能流连接 ====================
@router.get("/energy-flow/links", response_model=ResponseModel)
def list_energy_flow_links(db: Session = Depends(get_db)):
    items = db.query(EnergyFlowLink).all()
    nodes = {n.id: n.name for n in db.query(EnergyFlowNode).all()}
    return success(data=[{
        "id": i.id, "source_node_id": i.source_node_id,
        "source_name": nodes.get(i.source_node_id, ""),
        "target_node_id": i.target_node_id,
        "target_name": nodes.get(i.target_node_id, ""),
        "flow_value": float(i.flow_value), "unit": i.unit,
        "loss_rate": float(i.loss_rate), "remark": i.remark,
    } for i in items])


@router.post("/energy-flow/links", response_model=ResponseModel)
def create_energy_flow_link(req: EnergyFlowLinkCreate, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    item = EnergyFlowLink(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="创建成功")


@router.delete("/energy-flow/links/{item_id}", response_model=ResponseModel)
def delete_energy_flow_link(item_id: int, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    item = db.query(EnergyFlowLink).filter(EnergyFlowLink.id == item_id).first()
    if not item:
        return error("连接不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 用能预算 ====================
@router.get("/energy-budgets", response_model=ResponseModel)
def list_energy_budgets(
    year: int = None, unit_id: int = None,
    page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
):
    q = db.query(EnergyBudget)
    if year:
        q = q.filter(EnergyBudget.year == year)
    if unit_id:
        q = q.filter(EnergyBudget.unit_id == unit_id)
    total = q.count()
    items = q.order_by(EnergyBudget.year, EnergyBudget.month).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for i in items:
        et = db.query(EnergyType).filter(EnergyType.id == i.energy_type_id).first()
        unit = db.query(EnergyUnit).filter(EnergyUnit.id == i.unit_id).first()
        rate = calc_execution_rate(float(i.actual_value), float(i.budget_value))
        result.append({
            "id": i.id, "year": i.year, "month": i.month,
            "energy_type_id": i.energy_type_id, "unit_id": i.unit_id,
            "energy_type_name": et.name if et else "", "unit_name": unit.name if unit else "",
            "budget_value": float(i.budget_value), "actual_value": float(i.actual_value),
            "unit_consumption": float(i.unit_consumption),
            "planned_output": float(i.planned_output),
            "source_type": i.source_type, "execution_rate": rate, "remark": i.remark,
        })
    return success(data=result, total=total)


@router.post("/energy-budgets", response_model=ResponseModel)
def create_energy_budget(req: EnergyBudgetCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    budget_value = calc_budget_value(req.unit_consumption, req.planned_output)
    if req.budget_value > 0:
        budget_value = req.budget_value

    item = EnergyBudget(
        year=req.year, month=req.month, energy_type_id=req.energy_type_id,
        unit_id=req.unit_id, budget_value=budget_value,
        unit_consumption=req.unit_consumption, planned_output=req.planned_output,
        source_type=req.source_type, remark=req.remark,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="创建成功")


@router.put("/energy-budgets/{item_id}", response_model=ResponseModel)
def update_energy_budget(item_id: int, req: EnergyBudgetUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    item = db.query(EnergyBudget).filter(EnergyBudget.id == item_id).first()
    if not item:
        return error("预算记录不存在")
    budget_value = calc_budget_value(req.unit_consumption, req.planned_output)
    if req.budget_value > 0:
        budget_value = req.budget_value

    item.year = req.year
    item.month = req.month
    item.energy_type_id = req.energy_type_id
    item.unit_id = req.unit_id
    item.budget_value = budget_value
    item.unit_consumption = req.unit_consumption
    item.planned_output = req.planned_output
    item.source_type = req.source_type
    item.remark = req.remark
    db.commit()
    return success(message="更新成功")


@router.delete("/energy-budgets/{item_id}", response_model=ResponseModel)
def delete_energy_budget(item_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    item = db.query(EnergyBudget).filter(EnergyBudget.id == item_id).first()
    if not item:
        return error("预算记录不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 碳排放预算 ====================
@router.get("/carbon-budgets", response_model=ResponseModel)
def list_carbon_budgets(
    year: int = None, unit_id: int = None,
    page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
):
    q = db.query(CarbonBudget)
    if year:
        q = q.filter(CarbonBudget.year == year)
    if unit_id:
        q = q.filter(CarbonBudget.unit_id == unit_id)
    total = q.count()
    items = q.order_by(CarbonBudget.year, CarbonBudget.month).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for i in items:
        unit = db.query(EnergyUnit).filter(EnergyUnit.id == i.unit_id).first()
        rate = calc_execution_rate(float(i.actual_carbon), float(i.budget_carbon))
        result.append({
            "id": i.id, "year": i.year, "month": i.month, "unit_id": i.unit_id,
            "unit_name": unit.name if unit else "",
            "budget_carbon": float(i.budget_carbon), "actual_carbon": float(i.actual_carbon),
            "carbon_intensity": float(i.carbon_intensity),
            "intensity_type": i.intensity_type,
            "planned_output": float(i.planned_output),
            "execution_rate": rate, "remark": i.remark,
        })
    return success(data=result, total=total)


@router.post("/carbon-budgets", response_model=ResponseModel)
def create_carbon_budget(req: CarbonBudgetCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    budget_carbon = calc_carbon_budget(req.carbon_intensity, req.planned_output)
    if req.budget_carbon > 0:
        budget_carbon = req.budget_carbon

    item = CarbonBudget(
        year=req.year, month=req.month, unit_id=req.unit_id,
        budget_carbon=budget_carbon, carbon_intensity=req.carbon_intensity,
        intensity_type=req.intensity_type, planned_output=req.planned_output,
        remark=req.remark,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="创建成功")


@router.put("/carbon-budgets/{item_id}", response_model=ResponseModel)
def update_carbon_budget(item_id: int, req: CarbonBudgetUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    item = db.query(CarbonBudget).filter(CarbonBudget.id == item_id).first()
    if not item:
        return error("预算记录不存在")
    budget_carbon = calc_carbon_budget(req.carbon_intensity, req.planned_output)
    if req.budget_carbon > 0:
        budget_carbon = req.budget_carbon

    item.year = req.year
    item.month = req.month
    item.unit_id = req.unit_id
    item.budget_carbon = budget_carbon
    item.carbon_intensity = req.carbon_intensity
    item.intensity_type = req.intensity_type
    item.planned_output = req.planned_output
    item.remark = req.remark
    db.commit()
    return success(message="更新成功")


@router.delete("/carbon-budgets/{item_id}", response_model=ResponseModel)
def delete_carbon_budget(item_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    item = db.query(CarbonBudget).filter(CarbonBudget.id == item_id).first()
    if not item:
        return error("预算记录不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 综合能耗统计 ====================
@router.get("/comprehensive", response_model=ResponseModel)
def get_comprehensive(
    unit_id: int = None, start_date: str = None, end_date: str = None,
    db: Session = Depends(get_db)
):
    # 从表计读数和手工录入两个来源汇总
    readings_q = db.query(
        func.sum(MeterReading.consumption).label("consumption"),
        func.sum(MeterReading.cost).label("cost"),
        func.sum(MeterReading.standard_coal).label("standard_coal"),
        func.sum(MeterReading.carbon_emission).label("carbon_emission"),
    )
    if start_date:
        readings_q = readings_q.filter(MeterReading.reading_time >= start_date)
    if end_date:
        readings_q = readings_q.filter(MeterReading.reading_time <= end_date)

    manual_q = db.query(
        func.sum(ManualEntry.consumption).label("consumption"),
        func.sum(ManualEntry.cost).label("cost"),
        func.sum(ManualEntry.standard_coal).label("standard_coal"),
        func.sum(ManualEntry.carbon_emission).label("carbon_emission"),
    )
    if unit_id:
        manual_q = manual_q.filter(ManualEntry.unit_id == unit_id)
    if start_date:
        manual_q = manual_q.filter(ManualEntry.entry_date >= start_date)
    if end_date:
        manual_q = manual_q.filter(ManualEntry.entry_date <= end_date)

    r = readings_q.first()
    m = manual_q.first()

    total_consumption = (float(r[0] or 0)) + (float(m[0] or 0))
    total_cost = (float(r[1] or 0)) + (float(m[1] or 0))
    total_standard_coal = (float(r[2] or 0)) + (float(m[2] or 0))
    total_carbon = (float(r[3] or 0)) + (float(m[3] or 0))

    # 按能源类型统计
    energy_stats = []
    energy_types = db.query(EnergyType).filter(EnergyType.is_active == True).all()
    for et in energy_types:
        et_consumption = 0
        et_cost = 0
        et_sc = 0
        et_carbon = 0

        # 查表计读数中属于该能源类型的
        meter_ids = [m.id for m in db.query(Meter).filter(Meter.energy_type_id == et.id).all()]
        if meter_ids:
            rq = db.query(
                func.sum(MeterReading.consumption),
                func.sum(MeterReading.cost),
                func.sum(MeterReading.standard_coal),
                func.sum(MeterReading.carbon_emission),
            ).filter(MeterReading.meter_id.in_(meter_ids))
            if start_date:
                rq = rq.filter(MeterReading.reading_time >= start_date)
            if end_date:
                rq = rq.filter(MeterReading.reading_time <= end_date)
            rr = rq.first()
            et_consumption += float(rr[0] or 0)
            et_cost += float(rr[1] or 0)
            et_sc += float(rr[2] or 0)
            et_carbon += float(rr[3] or 0)

        # 查手工录入中属于该能源类型的
        mq = db.query(
            func.sum(ManualEntry.consumption),
            func.sum(ManualEntry.cost),
            func.sum(ManualEntry.standard_coal),
            func.sum(ManualEntry.carbon_emission),
        ).filter(ManualEntry.energy_type_id == et.id)
        if unit_id:
            mq = mq.filter(ManualEntry.unit_id == unit_id)
        if start_date:
            mq = mq.filter(ManualEntry.entry_date >= start_date)
        if end_date:
            mq = mq.filter(ManualEntry.entry_date <= end_date)
        mm = mq.first()
        et_consumption += float(mm[0] or 0)
        et_cost += float(mm[1] or 0)
        et_sc += float(mm[2] or 0)
        et_carbon += float(mm[3] or 0)

        if et_consumption > 0:
            pct = round(et_consumption / total_consumption * 100, 2) if total_consumption > 0 else 0
            energy_stats.append({
                "energy_type_id": et.id, "energy_type_name": et.name, "unit": et.unit,
                "consumption": round(et_consumption, 4), "cost": round(et_cost, 2),
                "standard_coal": round(et_sc, 4), "carbon_emission": round(et_carbon, 6),
                "percentage": pct,
            })

    return success(data={
        "total_consumption": round(total_consumption, 4),
        "total_cost": round(total_cost, 2),
        "total_standard_coal": round(total_standard_coal, 4),
        "total_carbon_emission": round(total_carbon, 6),
        "energy_type_count": len(energy_stats),
        "energy_stats": energy_stats,
    })


# ==================== 单元统计 ====================
@router.get("/unit-stat", response_model=ResponseModel)
def get_unit_stat(
    unit_id: int, stat_type: str = "consumption",
    period: str = "month", start_date: str = None, end_date: str = None,
    db: Session = Depends(get_db)
):
    unit = db.query(EnergyUnit).filter(EnergyUnit.id == unit_id).first()
    if not unit:
        return error("用能单元不存在")

    # 从手工录入表按时间聚合
    q = db.query(ManualEntry).filter(ManualEntry.unit_id == unit_id)
    if start_date:
        q = q.filter(ManualEntry.entry_date >= start_date)
    if end_date:
        q = q.filter(ManualEntry.entry_date <= end_date)
    items = q.order_by(ManualEntry.entry_date).all()

    # 按月或年聚合
    time_data = {}
    for i in items:
        if period == "month":
            key = i.entry_date[:7]  # YYYY-MM
        elif period == "year":
            key = i.entry_date[:4]  # YYYY
        else:
            key = i.entry_date

        if key not in time_data:
            time_data[key] = {"consumption": 0, "cost": 0, "standard_coal": 0, "carbon_emission": 0}
        time_data[key]["consumption"] += float(i.consumption)
        time_data[key]["cost"] += float(i.cost)
        time_data[key]["standard_coal"] += float(i.standard_coal)
        time_data[key]["carbon_emission"] += float(i.carbon_emission)

    result = []
    total = 0
    for key in sorted(time_data.keys()):
        d = time_data[key]
        val = d.get(stat_type, d["consumption"])
        total += val
        result.append({"time": key, **{k: round(v, 4) for k, v in d.items()}})

    return success(data={
        "unit_name": unit.name,
        "period": period,
        "stat_type": stat_type,
        "total": round(total, 4),
        "items": result,
    })


# ==================== 计量查询 ====================
@router.get("/meter-query", response_model=ResponseModel)
def get_meter_query(
    meter_id: int, stat_type: str = "consumption",
    period: str = "month", start_date: str = None, end_date: str = None,
    db: Session = Depends(get_db)
):
    meter = db.query(Meter).filter(Meter.id == meter_id).first()
    if not meter:
        return error("表计不存在")

    q = db.query(MeterReading).filter(MeterReading.meter_id == meter_id)
    if start_date:
        q = q.filter(MeterReading.reading_time >= start_date)
    if end_date:
        q = q.filter(MeterReading.reading_time <= end_date)
    items = q.order_by(MeterReading.reading_time).all()

    time_data = {}
    for i in items:
        if period == "month":
            key = i.reading_time[:7]
        elif period == "year":
            key = i.reading_time[:4]
        else:
            key = i.reading_time

        if key not in time_data:
            time_data[key] = {"consumption": 0, "cost": 0, "standard_coal": 0, "carbon_emission": 0}
        time_data[key]["consumption"] += float(i.consumption)
        time_data[key]["cost"] += float(i.cost)
        time_data[key]["standard_coal"] += float(i.standard_coal)
        time_data[key]["carbon_emission"] += float(i.carbon_emission)

    result = []
    total = 0
    for key in sorted(time_data.keys()):
        d = time_data[key]
        val = d.get(stat_type, d["consumption"])
        total += val
        result.append({"time": key, **{k: round(v, 4) for k, v in d.items()}})

    return success(data={
        "meter_name": meter.name,
        "period": period,
        "stat_type": stat_type,
        "total": round(total, 4),
        "items": result,
    })


# ==================== 能效统计 ====================
@router.get("/efficiency-stat", response_model=ResponseModel)
def get_efficiency_stat(
    product_id: int = None, unit_id: int = None,
    start_date: str = None, end_date: str = None,
    db: Session = Depends(get_db)
):
    q = db.query(ProductionData)
    if product_id:
        q = q.filter(ProductionData.product_id == product_id)
    if unit_id:
        q = q.filter(ProductionData.unit_id == unit_id)
    if start_date:
        q = q.filter(ProductionData.stat_date >= start_date)
    if end_date:
        q = q.filter(ProductionData.stat_date <= end_date)
    items = q.order_by(ProductionData.stat_date).all()

    result = []
    for i in items:
        prod = db.query(Product).filter(Product.id == i.product_id).first()
        unit = db.query(EnergyUnit).filter(EnergyUnit.id == i.unit_id).first()

        # 查该单元同期能耗
        cons_q = db.query(func.sum(ManualEntry.standard_coal)).filter(
            ManualEntry.unit_id == i.unit_id,
            ManualEntry.entry_date >= i.stat_date[:7] + "-01",
            ManualEntry.entry_date <= i.stat_date[:7] + "-31",
        )
        total_energy = float(cons_q.scalar() or 0)
        unit_energy = calc_unit_consumption(total_energy, float(i.output))

        result.append({
            "id": i.id, "product_name": prod.name if prod else "",
            "unit_name": unit.name if unit else "",
            "stat_date": i.stat_date, "output": float(i.output),
            "output_value": float(i.output_value),
            "total_energy": round(total_energy, 4),
            "unit_energy": unit_energy,
        })
    return success(data=result)
