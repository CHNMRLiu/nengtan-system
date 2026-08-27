from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import (
    Organization, EnergyType, EnergyUnit, Meter, Product,
    EmissionSource, CarbonFactor, OperationLog
)
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas import (
    ResponseModel, OrganizationCreate, OrganizationUpdate,
    EnergyTypeCreate, EnergyTypeUpdate, EnergyUnitCreate, EnergyUnitUpdate,
    MeterCreate, MeterUpdate, ProductCreate, ProductUpdate,
    EmissionSourceCreate, EmissionSourceUpdate, CarbonFactorCreate, CarbonFactorUpdate,
)

router = APIRouter()


def success(data=None, message="操作成功", total=None):
    result = {"code": 200, "message": message, "data": data}
    if total is not None:
        result["total"] = total
    return result


def error(message="操作失败", code=400):
    return ResponseModel(code=code, message=message)


# ==================== 企业信息 ====================
@router.get("/organization", response_model=ResponseModel)
def get_organization(db: Session = Depends(get_db)):
    org = db.query(Organization).first()
    if not org:
        org = Organization(name="默认企业", industry="制造业")
        db.add(org)
        db.commit()
        db.refresh(org)
    return success(data={
        "id": org.id, "name": org.name, "credit_code": org.credit_code,
        "industry": org.industry, "address": org.address, "contact": org.contact,
        "phone": org.phone, "scale": org.scale, "established_date": org.established_date,
    })


@router.put("/organization/{org_id}", response_model=ResponseModel)
def update_organization(org_id: int, req: OrganizationUpdate, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        return error("企业信息不存在")
    for k, v in req.model_dump().items():
        setattr(org, k, v)
    db.commit()
    return success(message="企业信息更新成功")


# ==================== 能源类型 ====================
@router.get("/energy-types", response_model=ResponseModel)
def list_energy_types(is_active: bool = None, db: Session = Depends(get_db)):
    q = db.query(EnergyType)
    if is_active is not None:
        q = q.filter(EnergyType.is_active == is_active)
    items = q.order_by(EnergyType.sort_order).all()
    return success(data=[{
        "id": i.id, "code": i.code, "name": i.name, "unit": i.unit,
        "standard_coal_coefficient": float(i.standard_coal_coefficient),
        "carbon_factor": float(i.carbon_factor), "default_price": float(i.default_price),
        "is_active": i.is_active, "sort_order": i.sort_order,
    } for i in items])


@router.post("/energy-types", response_model=ResponseModel)
def create_energy_type(req: EnergyTypeCreate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    if db.query(EnergyType).filter(EnergyType.code == req.code).first():
        return error("能源类型编码已存在")
    item = EnergyType(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="创建成功")


@router.put("/energy-types/{item_id}", response_model=ResponseModel)
def update_energy_type(item_id: int, req: EnergyTypeUpdate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    item = db.query(EnergyType).filter(EnergyType.id == item_id).first()
    if not item:
        return error("能源类型不存在")
    for k, v in req.model_dump().items():
        setattr(item, k, v)
    db.commit()
    return success(message="更新成功")


@router.delete("/energy-types/{item_id}", response_model=ResponseModel)
def delete_energy_type(item_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    item = db.query(EnergyType).filter(EnergyType.id == item_id).first()
    if not item:
        return error("能源类型不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 用能单元 ====================
@router.get("/energy-units", response_model=ResponseModel)
def list_energy_units(is_active: bool = None, db: Session = Depends(get_db)):
    q = db.query(EnergyUnit)
    if is_active is not None:
        q = q.filter(EnergyUnit.is_active == is_active)
    items = q.order_by(EnergyUnit.sort_order).all()
    return success(data=[{
        "id": i.id, "code": i.code, "name": i.name, "parent_id": i.parent_id,
        "level": i.level, "area": i.area, "responsible_person": i.responsible_person,
        "phone": i.phone, "is_active": i.is_active, "sort_order": i.sort_order,
    } for i in items])


@router.get("/energy-units/tree", response_model=ResponseModel)
def get_energy_unit_tree(db: Session = Depends(get_db)):
    items = db.query(EnergyUnit).filter(EnergyUnit.is_active == True).order_by(EnergyUnit.sort_order).all()
    item_map = {}
    roots = []
    for i in items:
        node = {
            "id": i.id, "code": i.code, "name": i.name, "parent_id": i.parent_id,
            "level": i.level, "children": []
        }
        item_map[i.id] = node
    for i in items:
        node = item_map[i.id]
        if i.parent_id and i.parent_id in item_map:
            item_map[i.parent_id]["children"].append(node)
        else:
            roots.append(node)
    return success(data=roots)


@router.post("/energy-units", response_model=ResponseModel)
def create_energy_unit(req: EnergyUnitCreate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    if db.query(EnergyUnit).filter(EnergyUnit.code == req.code).first():
        return error("用能单元编码已存在")
    item = EnergyUnit(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="创建成功")


@router.put("/energy-units/{item_id}", response_model=ResponseModel)
def update_energy_unit(item_id: int, req: EnergyUnitUpdate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    item = db.query(EnergyUnit).filter(EnergyUnit.id == item_id).first()
    if not item:
        return error("用能单元不存在")
    for k, v in req.model_dump().items():
        setattr(item, k, v)
    db.commit()
    return success(message="更新成功")


@router.delete("/energy-units/{item_id}", response_model=ResponseModel)
def delete_energy_unit(item_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    item = db.query(EnergyUnit).filter(EnergyUnit.id == item_id).first()
    if not item:
        return error("用能单元不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 表计管理 ====================
@router.get("/meters", response_model=ResponseModel)
def list_meters(
    energy_type_id: int = None, unit_id: int = None, is_active: bool = None,
    page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
):
    q = db.query(Meter)
    if energy_type_id:
        q = q.filter(Meter.energy_type_id == energy_type_id)
    if unit_id:
        q = q.filter(Meter.unit_id == unit_id)
    if is_active is not None:
        q = q.filter(Meter.is_active == is_active)
    total = q.count()
    items = q.order_by(Meter.id).offset((page - 1) * page_size).limit(page_size).all()
    return success(data=[{
        "id": i.id, "code": i.code, "name": i.name,
        "energy_type_id": i.energy_type_id, "unit_id": i.unit_id,
        "meter_type": i.meter_type, "installation_location": i.installation_location,
        "rated_voltage": i.rated_voltage, "current_ratio": i.current_ratio,
        "voltage_ratio": i.voltage_ratio, "accuracy": i.accuracy,
        "install_date": i.install_date, "is_active": i.is_active, "remark": i.remark,
    } for i in items], total=total)


@router.post("/meters", response_model=ResponseModel)
def create_meter(req: MeterCreate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    if db.query(Meter).filter(Meter.code == req.code).first():
        return error("表计编码已存在")
    item = Meter(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="创建成功")


@router.put("/meters/{item_id}", response_model=ResponseModel)
def update_meter(item_id: int, req: MeterUpdate, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    item = db.query(Meter).filter(Meter.id == item_id).first()
    if not item:
        return error("表计不存在")
    for k, v in req.model_dump().items():
        setattr(item, k, v)
    db.commit()
    return success(message="更新成功")


@router.delete("/meters/{item_id}", response_model=ResponseModel)
def delete_meter(item_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    item = db.query(Meter).filter(Meter.id == item_id).first()
    if not item:
        return error("表计不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 产品管理 ====================
@router.get("/products", response_model=ResponseModel)
def list_products(is_active: bool = None, db: Session = Depends(get_db)):
    q = db.query(Product)
    if is_active is not None:
        q = q.filter(Product.is_active == is_active)
    items = q.order_by(Product.sort_order).all()
    return success(data=[{
        "id": i.id, "code": i.code, "name": i.name,
        "unit": i.unit, "output_unit": i.output_unit,
        "is_active": i.is_active, "sort_order": i.sort_order,
    } for i in items])


@router.post("/products", response_model=ResponseModel)
def create_product(req: ProductCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    if db.query(Product).filter(Product.code == req.code).first():
        return error("产品编码已存在")
    item = Product(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="创建成功")


@router.put("/products/{item_id}", response_model=ResponseModel)
def update_product(item_id: int, req: ProductUpdate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    item = db.query(Product).filter(Product.id == item_id).first()
    if not item:
        return error("产品不存在")
    for k, v in req.model_dump().items():
        setattr(item, k, v)
    db.commit()
    return success(message="更新成功")


@router.delete("/products/{item_id}", response_model=ResponseModel)
def delete_product(item_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    item = db.query(Product).filter(Product.id == item_id).first()
    if not item:
        return error("产品不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 排放源管理 ====================
@router.get("/emission-sources", response_model=ResponseModel)
def list_emission_sources(scope: str = None, db: Session = Depends(get_db)):
    q = db.query(EmissionSource)
    if scope:
        q = q.filter(EmissionSource.scope == scope)
    items = q.order_by(EmissionSource.sort_order).all()
    return success(data=[{
        "id": i.id, "code": i.code, "name": i.name, "scope": i.scope,
        "category": i.category, "carbon_factor_id": i.carbon_factor_id,
        "is_active": i.is_active, "sort_order": i.sort_order, "remark": i.remark,
    } for i in items])


@router.post("/emission-sources", response_model=ResponseModel)
def create_emission_source(req: EmissionSourceCreate, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    if db.query(EmissionSource).filter(EmissionSource.code == req.code).first():
        return error("排放源编码已存在")
    item = EmissionSource(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="创建成功")


@router.put("/emission-sources/{item_id}", response_model=ResponseModel)
def update_emission_source(item_id: int, req: EmissionSourceUpdate, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    item = db.query(EmissionSource).filter(EmissionSource.id == item_id).first()
    if not item:
        return error("排放源不存在")
    for k, v in req.model_dump().items():
        setattr(item, k, v)
    db.commit()
    return success(message="更新成功")


@router.delete("/emission-sources/{item_id}", response_model=ResponseModel)
def delete_emission_source(item_id: int, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    item = db.query(EmissionSource).filter(EmissionSource.id == item_id).first()
    if not item:
        return error("排放源不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 碳因子管理 ====================
@router.get("/carbon-factors", response_model=ResponseModel)
def list_carbon_factors(is_active: bool = None, db: Session = Depends(get_db)):
    q = db.query(CarbonFactor)
    if is_active is not None:
        q = q.filter(CarbonFactor.is_active == is_active)
    items = q.order_by(CarbonFactor.sort_order).all()
    return success(data=[{
        "id": i.id, "name": i.name, "factor_value": float(i.factor_value),
        "unit": i.unit, "source": i.source, "effective_date": i.effective_date,
        "is_active": i.is_active, "sort_order": i.sort_order,
    } for i in items])


@router.post("/carbon-factors", response_model=ResponseModel)
def create_carbon_factor(req: CarbonFactorCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    item = CarbonFactor(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="创建成功")


@router.put("/carbon-factors/{item_id}", response_model=ResponseModel)
def update_carbon_factor(item_id: int, req: CarbonFactorUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    item = db.query(CarbonFactor).filter(CarbonFactor.id == item_id).first()
    if not item:
        return error("碳因子不存在")
    for k, v in req.model_dump().items():
        setattr(item, k, v)
    db.commit()
    return success(message="更新成功")


@router.delete("/carbon-factors/{item_id}", response_model=ResponseModel)
def delete_carbon_factor(item_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    item = db.query(CarbonFactor).filter(CarbonFactor.id == item_id).first()
    if not item:
        return error("碳因子不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 操作日志 ====================
@router.get("/logs", response_model=ResponseModel)
def list_logs(
    page: int = 1, page_size: int = 20, module: str = None,
    db: Session = Depends(get_db)
):
    q = db.query(OperationLog)
    if module:
        q = q.filter(OperationLog.module == module)
    total = q.count()
    items = q.order_by(desc(OperationLog.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    return success(data=[{
        "id": i.id, "user_id": i.user_id, "username": i.username,
        "module": i.module, "action": i.action, "ip": i.ip,
        "created_at": i.created_at.strftime("%Y-%m-%d %H:%M:%S") if i.created_at else "",
    } for i in items], total=total)
