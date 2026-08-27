from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models import (
    CarbonAccounting, CarbonReport, ProductFootprint, Supplier,
    SupplierCarbonData, CarbonVerification, CarbonAsset, QuotaRecord,
    EmissionSource, CarbonFactor, EnergyUnit, Product, Organization
)
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas import (
    ResponseModel, CarbonAccountingCreate, CarbonAccountingUpdate,
    CarbonReportCreate, ProductFootprintCreate, ProductFootprintUpdate,
    SupplierCreate, SupplierUpdate, SupplierCarbonDataCreate, SupplierCarbonDataUpdate,
    CarbonVerificationCreate, CarbonVerificationUpdate,
    CarbonAssetCreate, CarbonAssetUpdate, QuotaRecordCreate, QuotaRecordUpdate,
)
from app.utils.calculator import (
    calc_carbon_emission, calc_footprint_total, calc_quota_remaining, calc_trade_amount
)

router = APIRouter()


def success(data=None, message="操作成功", total=0):
    return ResponseModel(code=200, message=message, data=data, total=total)


def error(message="操作失败", code=400):
    return ResponseModel(code=code, message=message)


# ==================== 碳核算 ====================
@router.get("/accounting", response_model=ResponseModel)
def list_carbon_accounting(
    source_id: int = None, year: int = None, scope: str = None,
    page: int = 1, page_size: int = 20, db: Session = Depends(get_db)
):
    q = db.query(CarbonAccounting)
    if source_id:
        q = q.filter(CarbonAccounting.source_id == source_id)
    if year:
        q = q.filter(CarbonAccounting.year == year)
    if scope:
        source_ids = [s.id for s in db.query(EmissionSource).filter(EmissionSource.scope == scope).all()]
        q = q.filter(CarbonAccounting.source_id.in_(source_ids))
    total = q.count()
    items = q.order_by(CarbonAccounting.year, CarbonAccounting.month).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for i in items:
        source = db.query(EmissionSource).filter(EmissionSource.id == i.source_id).first()
        result.append({
            "id": i.id, "source_id": i.source_id,
            "source_name": source.name if source else "",
            "scope": source.scope if source else "",
            "year": i.year, "month": i.month,
            "activity_data": float(i.activity_data), "unit": i.unit,
            "emission_factor": float(i.emission_factor),
            "emission": float(i.emission),
            "data_source": i.data_source, "remark": i.remark,
        })
    return success(data=result, total=total)


@router.post("/accounting", response_model=ResponseModel)
def create_carbon_accounting(req: CarbonAccountingCreate, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    source = db.query(EmissionSource).filter(EmissionSource.id == req.source_id).first()
    if not source:
        return error("排放源不存在")

    # 如果没有手动指定排放因子，从排放源关联的碳因子获取
    factor = req.emission_factor
    if factor == 0 and source.carbon_factor_id:
        cf = db.query(CarbonFactor).filter(CarbonFactor.id == source.carbon_factor_id).first()
        if cf:
            factor = float(cf.factor_value)

    emission = calc_carbon_emission(req.activity_data, factor)

    item = CarbonAccounting(
        source_id=req.source_id, year=req.year, month=req.month,
        activity_data=req.activity_data, unit=req.unit,
        emission_factor=factor, emission=emission,
        data_source=req.data_source, remark=req.remark,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="核算数据录入成功")


@router.put("/accounting/{item_id}", response_model=ResponseModel)
def update_carbon_accounting(item_id: int, req: CarbonAccountingUpdate, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    item = db.query(CarbonAccounting).filter(CarbonAccounting.id == item_id).first()
    if not item:
        return error("核算记录不存在")

    factor = req.emission_factor
    if factor == 0:
        source = db.query(EmissionSource).filter(EmissionSource.id == req.source_id).first()
        if source and source.carbon_factor_id:
            cf = db.query(CarbonFactor).filter(CarbonFactor.id == source.carbon_factor_id).first()
            if cf:
                factor = float(cf.factor_value)

    emission = calc_carbon_emission(req.activity_data, factor)

    item.source_id = req.source_id
    item.year = req.year
    item.month = req.month
    item.activity_data = req.activity_data
    item.unit = req.unit
    item.emission_factor = factor
    item.emission = emission
    item.data_source = req.data_source
    item.remark = req.remark
    db.commit()
    return success(message="更新成功")


@router.delete("/accounting/{item_id}", response_model=ResponseModel)
def delete_carbon_accounting(item_id: int, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    item = db.query(CarbonAccounting).filter(CarbonAccounting.id == item_id).first()
    if not item:
        return error("核算记录不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 碳排统计 ====================
@router.get("/statistics", response_model=ResponseModel)
def get_carbon_statistics(year: int = None, scope: str = None, db: Session = Depends(get_db)):
    q = db.query(CarbonAccounting)
    if year:
        q = q.filter(CarbonAccounting.year == year)
    items = q.all()

    scope1_total = 0
    scope2_total = 0
    scope3_total = 0
    monthly_data = {}
    source_data = {}

    for i in items:
        source = db.query(EmissionSource).filter(EmissionSource.id == i.source_id).first()
        s = source.scope if source else "范围1"
        emission = float(i.emission)

        if s == "范围1":
            scope1_total += emission
        elif s == "范围2":
            scope2_total += emission
        else:
            scope3_total += emission

        # 月度趋势
        month_key = f"{i.year}-{i.month:02d}"
        if month_key not in monthly_data:
            monthly_data[month_key] = 0
        monthly_data[month_key] += emission

        # 排放源占比
        src_name = source.name if source else "未知"
        if src_name not in source_data:
            source_data[src_name] = 0
        source_data[src_name] += emission

    total = scope1_total + scope2_total + scope3_total

    monthly_trend = [{"month": k, "emission": round(v, 6)} for k, v in sorted(monthly_data.items())]
    source_stats = [{"name": k, "emission": round(v, 6), "percentage": round(v / total * 100, 2) if total > 0 else 0}
                    for k, v in sorted(source_data.items(), key=lambda x: -x[1])]

    # 明细表
    detail_items = []
    for i in items:
        source = db.query(EmissionSource).filter(EmissionSource.id == i.source_id).first()
        pct = round(float(i.emission) / total * 100, 2) if total > 0 else 0
        detail_items.append({
            "id": i.id, "source_name": source.name if source else "",
            "scope": source.scope if source else "",
            "activity_data": float(i.activity_data), "unit": i.unit,
            "emission_factor": float(i.emission_factor),
            "emission": float(i.emission), "percentage": pct,
        })

    return success(data={
        "scope1": round(scope1_total, 6),
        "scope2": round(scope2_total, 6),
        "scope3": round(scope3_total, 6),
        "total": round(total, 6),
        "monthly_trend": monthly_trend,
        "source_stats": source_stats,
        "details": detail_items,
    })


# ==================== 碳报告 ====================
@router.get("/reports", response_model=ResponseModel)
def list_carbon_reports(db: Session = Depends(get_db)):
    items = db.query(CarbonReport).order_by(desc(CarbonReport.year)).all()
    return success(data=[{
        "id": i.id, "year": i.year, "total_emission": float(i.total_emission),
        "scope1": float(i.scope1), "scope2": float(i.scope2), "scope3": float(i.scope3),
        "intensity_value": float(i.intensity_value),
        "product_intensity": float(i.product_intensity),
        "per_capita": float(i.per_capita),
        "measures": i.measures, "next_plan": i.next_plan,
        "report_date": i.report_date, "status": i.status,
    } for i in items])


@router.post("/reports/generate", response_model=ResponseModel)
def generate_carbon_report(req: CarbonReportCreate, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    # 从碳核算表汇总
    items = db.query(CarbonAccounting).filter(CarbonAccounting.year == req.year).all()
    scope1 = 0
    scope2 = 0
    scope3 = 0
    for i in items:
        source = db.query(EmissionSource).filter(EmissionSource.id == i.source_id).first()
        s = source.scope if source else "范围1"
        emission = float(i.emission)
        if s == "范围1":
            scope1 += emission
        elif s == "范围2":
            scope2 += emission
        else:
            scope3 += emission

    total = scope1 + scope2 + scope3

    # 获取企业信息计算强度
    org = db.query(Organization).first()
    org_name = org.name if org else "未知企业"

    # 查已有报告，有则更新，无则创建
    report = db.query(CarbonReport).filter(CarbonReport.year == req.year).first()
    if report:
        report.total_emission = total
        report.scope1 = scope1
        report.scope2 = scope2
        report.scope3 = scope3
        report.measures = req.measures
        report.next_plan = req.next_plan
        report.report_date = req.year.__str__() + "-12-31"
        report.status = "已生成"
    else:
        report = CarbonReport(
            year=req.year, total_emission=total,
            scope1=scope1, scope2=scope2, scope3=scope3,
            measures=req.measures, next_plan=req.next_plan,
            report_date=f"{req.year}-12-31", status="已生成",
        )
        db.add(report)
    db.commit()
    db.refresh(report)

    # 获取排放源明细
    details = []
    for i in items:
        source = db.query(EmissionSource).filter(EmissionSource.id == i.source_id).first()
        pct = round(float(i.emission) / total * 100, 2) if total > 0 else 0
        details.append({
            "source_name": source.name if source else "",
            "scope": source.scope if source else "",
            "activity_data": float(i.activity_data),
            "unit": i.unit,
            "emission_factor": float(i.emission_factor),
            "emission": float(i.emission),
            "percentage": pct,
        })

    return success(data={
        "report": {
            "id": report.id, "year": report.year,
            "total_emission": float(report.total_emission),
            "scope1": float(report.scope1), "scope2": float(report.scope2),
            "scope3": float(report.scope3),
            "measures": report.measures, "next_plan": report.next_plan,
            "report_date": report.report_date, "status": report.status,
        },
        "org_name": org_name,
        "details": details,
    })


@router.get("/reports/{year}", response_model=ResponseModel)
def get_carbon_report(year: int, db: Session = Depends(get_db)):
    report = db.query(CarbonReport).filter(CarbonReport.year == year).first()
    if not report:
        return error("该年度报告未生成")

    org = db.query(Organization).first()
    items = db.query(CarbonAccounting).filter(CarbonAccounting.year == year).all()
    total = float(report.total_emission)

    details = []
    for i in items:
        source = db.query(EmissionSource).filter(EmissionSource.id == i.source_id).first()
        pct = round(float(i.emission) / total * 100, 2) if total > 0 else 0
        details.append({
            "source_name": source.name if source else "",
            "scope": source.scope if source else "",
            "activity_data": float(i.activity_data), "unit": i.unit,
            "emission_factor": float(i.emission_factor),
            "emission": float(i.emission), "percentage": pct,
        })

    return success(data={
        "report": {
            "id": report.id, "year": report.year,
            "total_emission": float(report.total_emission),
            "scope1": float(report.scope1), "scope2": float(report.scope2),
            "scope3": float(report.scope3),
            "intensity_value": float(report.intensity_value),
            "product_intensity": float(report.product_intensity),
            "measures": report.measures, "next_plan": report.next_plan,
            "report_date": report.report_date, "status": report.status,
        },
        "org_name": org.name if org else "未知企业",
        "details": details,
    })


# ==================== 碳足迹 ====================
@router.get("/footprints", response_model=ResponseModel)
def list_product_footprints(product_id: int = None, db: Session = Depends(get_db)):
    q = db.query(ProductFootprint)
    if product_id:
        q = q.filter(ProductFootprint.product_id == product_id)
    items = q.order_by(desc(ProductFootprint.assessment_date)).all()

    result = []
    for i in items:
        prod = db.query(Product).filter(Product.id == i.product_id).first()
        result.append({
            "id": i.id, "product_id": i.product_id,
            "product_name": prod.name if prod else "",
            "functional_unit": i.functional_unit, "boundary": i.boundary,
            "raw_material": float(i.raw_material), "production": float(i.production),
            "transport": float(i.transport), "use_phase": float(i.use_phase),
            "disposal": float(i.disposal), "total": float(i.total),
            "assessment_date": i.assessment_date, "data_source": i.data_source,
        })
    return success(data=result)


@router.post("/footprints", response_model=ResponseModel)
def create_product_footprint(req: ProductFootprintCreate, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    total = calc_footprint_total(req.raw_material, req.production, req.transport,
                                 req.use_phase, req.disposal)
    item = ProductFootprint(
        product_id=req.product_id, functional_unit=req.functional_unit,
        boundary=req.boundary, raw_material=req.raw_material,
        production=req.production, transport=req.transport,
        use_phase=req.use_phase, disposal=req.disposal,
        total=total, assessment_date=req.assessment_date,
        data_source=req.data_source,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="碳足迹创建成功")


@router.put("/footprints/{item_id}", response_model=ResponseModel)
def update_product_footprint(item_id: int, req: ProductFootprintUpdate, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    item = db.query(ProductFootprint).filter(ProductFootprint.id == item_id).first()
    if not item:
        return error("碳足迹记录不存在")
    total = calc_footprint_total(req.raw_material, req.production, req.transport,
                                 req.use_phase, req.disposal)
    for k, v in req.model_dump().items():
        setattr(item, k, v)
    item.total = total
    db.commit()
    return success(message="更新成功")


@router.delete("/footprints/{item_id}", response_model=ResponseModel)
def delete_product_footprint(item_id: int, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    item = db.query(ProductFootprint).filter(ProductFootprint.id == item_id).first()
    if not item:
        return error("碳足迹记录不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 供应商 ====================
@router.get("/suppliers", response_model=ResponseModel)
def list_suppliers(db: Session = Depends(get_db)):
    items = db.query(Supplier).order_by(desc(Supplier.total_emission)).all()
    return success(data=[{
        "id": i.id, "name": i.name, "credit_code": i.credit_code,
        "contact_person": i.contact_person, "phone": i.phone,
        "category": i.category, "risk_level": i.risk_level,
        "address": i.address, "total_emission": float(i.total_emission),
    } for i in items])


@router.post("/suppliers", response_model=ResponseModel)
def create_supplier(req: SupplierCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    item = Supplier(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="供应商创建成功")


@router.put("/suppliers/{item_id}", response_model=ResponseModel)
def update_supplier(item_id: int, req: SupplierUpdate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    item = db.query(Supplier).filter(Supplier.id == item_id).first()
    if not item:
        return error("供应商不存在")
    for k, v in req.model_dump().items():
        setattr(item, k, v)
    db.commit()
    return success(message="更新成功")


@router.delete("/suppliers/{item_id}", response_model=ResponseModel)
def delete_supplier(item_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    item = db.query(Supplier).filter(Supplier.id == item_id).first()
    if not item:
        return error("供应商不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 供应商碳数据 ====================
@router.get("/supplier-carbon-data", response_model=ResponseModel)
def list_supplier_carbon_data(supplier_id: int = None, year: int = None, db: Session = Depends(get_db)):
    q = db.query(SupplierCarbonData)
    if supplier_id:
        q = q.filter(SupplierCarbonData.supplier_id == supplier_id)
    if year:
        q = q.filter(SupplierCarbonData.year == year)
    items = q.order_by(SupplierCarbonData.year).all()

    result = []
    for i in items:
        supplier = db.query(Supplier).filter(Supplier.id == i.supplier_id).first()
        result.append({
            "id": i.id, "supplier_id": i.supplier_id,
            "supplier_name": supplier.name if supplier else "",
            "year": i.year, "material_name": i.material_name,
            "quantity": float(i.quantity), "unit": i.unit,
            "emission_factor": float(i.emission_factor),
            "emission": float(i.emission), "data_source": i.data_source,
        })
    return success(data=result)


@router.post("/supplier-carbon-data", response_model=ResponseModel)
def create_supplier_carbon_data(req: SupplierCarbonDataCreate, db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    emission = calc_carbon_emission(req.quantity, req.emission_factor)
    item = SupplierCarbonData(
        supplier_id=req.supplier_id, year=req.year,
        material_name=req.material_name, quantity=req.quantity,
        unit=req.unit, emission_factor=req.emission_factor,
        emission=emission, data_source=req.data_source,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    # 更新供应商总排放
    supplier = db.query(Supplier).filter(Supplier.id == req.supplier_id).first()
    if supplier:
        total = db.query(func.sum(SupplierCarbonData.emission)).filter(
            SupplierCarbonData.supplier_id == req.supplier_id
        ).scalar() or 0
        supplier.total_emission = total
        db.commit()

    return success(data={"id": item.id}, message="碳数据录入成功")


@router.delete("/supplier-carbon-data/{item_id}", response_model=ResponseModel)
def delete_supplier_carbon_data(item_id: int, db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    item = db.query(SupplierCarbonData).filter(SupplierCarbonData.id == item_id).first()
    if not item:
        return error("记录不存在")
    supplier_id = item.supplier_id
    db.delete(item)
    db.commit()

    # 更新供应商总排放
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if supplier:
        total = db.query(func.sum(SupplierCarbonData.emission)).filter(
            SupplierCarbonData.supplier_id == supplier_id
        ).scalar() or 0
        supplier.total_emission = total
        db.commit()

    return success(message="删除成功")


# ==================== 碳核查 ====================
@router.get("/verifications", response_model=ResponseModel)
def list_carbon_verifications(year: int = None, status: str = None, db: Session = Depends(get_db)):
    q = db.query(CarbonVerification)
    if year:
        q = q.filter(CarbonVerification.year == year)
    if status:
        q = q.filter(CarbonVerification.status == status)
    items = q.order_by(desc(CarbonVerification.year)).all()

    result = []
    for i in items:
        deviation = 0
        if float(i.reported_emission) > 0:
            deviation = round((float(i.verified_emission) - float(i.reported_emission)) / float(i.reported_emission) * 100, 2)
        result.append({
            "id": i.id, "year": i.year,
            "verification_agency": i.verification_agency,
            "verifier": i.verifier,
            "start_date": i.start_date, "end_date": i.end_date,
            "reported_emission": float(i.reported_emission),
            "verified_emission": float(i.verified_emission),
            "deviation": deviation,
            "status": i.status, "conclusion": i.conclusion,
            "evidence_hash": i.evidence_hash,
        })
    return success(data=result)


@router.post("/verifications", response_model=ResponseModel)
def create_carbon_verification(req: CarbonVerificationCreate, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    item = CarbonVerification(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="核查记录创建成功")


@router.put("/verifications/{item_id}", response_model=ResponseModel)
def update_carbon_verification(item_id: int, req: CarbonVerificationUpdate, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    item = db.query(CarbonVerification).filter(CarbonVerification.id == item_id).first()
    if not item:
        return error("核查记录不存在")
    for k, v in req.model_dump().items():
        setattr(item, k, v)
    db.commit()
    return success(message="更新成功")


@router.delete("/verifications/{item_id}", response_model=ResponseModel)
def delete_carbon_verification(item_id: int, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    item = db.query(CarbonVerification).filter(CarbonVerification.id == item_id).first()
    if not item:
        return error("核查记录不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 碳资产 ====================
@router.get("/assets", response_model=ResponseModel)
def list_carbon_assets(year: int = None, db: Session = Depends(get_db)):
    q = db.query(CarbonAsset)
    if year:
        q = q.filter(CarbonAsset.year == year)
    items = q.order_by(desc(CarbonAsset.year)).all()

    total_quantity = sum(float(i.quantity) for i in items)
    total_used = sum(float(i.used_quantity) for i in items)
    remaining = calc_quota_remaining(total_quantity, total_used)

    return success(data={
        "total_quantity": round(total_quantity, 6),
        "total_used": round(total_used, 6),
        "remaining": round(remaining, 6),
        "items": [{
            "id": i.id, "asset_type": i.asset_type, "year": i.year,
            "project_name": i.project_name, "quantity": float(i.quantity),
            "used_quantity": float(i.used_quantity),
            "acquisition_date": i.acquisition_date, "expiry_date": i.expiry_date,
            "status": i.status,
        } for i in items],
    })


@router.post("/assets", response_model=ResponseModel)
def create_carbon_asset(req: CarbonAssetCreate, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    item = CarbonAsset(**req.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="碳资产登记成功")


@router.put("/assets/{item_id}", response_model=ResponseModel)
def update_carbon_asset(item_id: int, req: CarbonAssetUpdate, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    item = db.query(CarbonAsset).filter(CarbonAsset.id == item_id).first()
    if not item:
        return error("碳资产不存在")
    for k, v in req.model_dump().items():
        setattr(item, k, v)
    db.commit()
    return success(message="更新成功")


@router.delete("/assets/{item_id}", response_model=ResponseModel)
def delete_carbon_asset(item_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    item = db.query(CarbonAsset).filter(CarbonAsset.id == item_id).first()
    if not item:
        return error("碳资产不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")


# ==================== 配额交易 ====================
@router.get("/quota-records", response_model=ResponseModel)
def list_quota_records(db: Session = Depends(get_db)):
    items = db.query(QuotaRecord).order_by(desc(QuotaRecord.trade_date)).all()
    return success(data=[{
        "id": i.id, "trade_date": i.trade_date, "trade_type": i.trade_type,
        "quantity": float(i.quantity), "price": float(i.price),
        "total_amount": float(i.total_amount), "market": i.market, "remark": i.remark,
    } for i in items])


@router.post("/quota-records", response_model=ResponseModel)
def create_quota_record(req: QuotaRecordCreate, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    total_amount = calc_trade_amount(req.quantity, req.price)
    item = QuotaRecord(
        trade_date=req.trade_date, trade_type=req.trade_type,
        quantity=req.quantity, price=req.price,
        total_amount=total_amount, market=req.market, remark=req.remark,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data={"id": item.id}, message="交易记录创建成功")


@router.delete("/quota-records/{item_id}", response_model=ResponseModel)
def delete_quota_record(item_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    item = db.query(QuotaRecord).filter(QuotaRecord.id == item_id).first()
    if not item:
        return error("交易记录不存在")
    db.delete(item)
    db.commit()
    return success(message="删除成功")
