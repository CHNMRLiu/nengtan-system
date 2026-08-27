from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.database import get_db
from app.models import (
    MeterReading, ManualEntry, CarbonAccounting, EmissionSource,
    EnergyType, Meter, EnergyUnit, CarbonReport
)

router = APIRouter()


def success(data=None, message="ok"):
    from app.schemas import ResponseModel
    return ResponseModel(code=200, message=message, data=data)


@router.get("/stats")
def get_dashboard_stats(year: int = None, db: Session = Depends(get_db)):
    """首页看板统计"""
    if not year:
        from datetime import datetime
        year = datetime.now().year

    # 年度能耗统计
    readings = db.query(MeterReading).filter(
        MeterReading.reading_time >= f"{year}-01-01",
        MeterReading.reading_time <= f"{year}-12-31"
    ).all()
    manuals = db.query(ManualEntry).filter(
        ManualEntry.entry_date >= f"{year}-01-01",
        ManualEntry.entry_date <= f"{year}-12-31"
    ).all()

    total_consumption = sum(float(r.consumption) for r in readings) + sum(float(m.consumption) for m in manuals)
    total_cost = sum(float(r.cost) for r in readings) + sum(float(m.cost) for m in manuals)
    total_standard_coal = sum(float(r.standard_coal) for r in readings) + sum(float(m.standard_coal) for m in manuals)
    total_carbon = sum(float(r.carbon_emission) for r in readings) + sum(float(m.carbon_emission) for m in manuals)

    # 能源类型统计
    energy_stats = {}
    for r in readings:
        meter = db.query(Meter).filter(Meter.id == r.meter_id).first()
        if meter:
            et = db.query(EnergyType).filter(EnergyType.id == meter.energy_type_id).first()
            if et:
                if et.name not in energy_stats:
                    energy_stats[et.name] = 0
                energy_stats[et.name] += float(r.standard_coal)
    for m in manuals:
        et = db.query(EnergyType).filter(EnergyType.id == m.energy_type_id).first()
        if et:
            if et.name not in energy_stats:
                energy_stats[et.name] = 0
            energy_stats[et.name] += float(m.standard_coal)

    # 月度碳排放趋势
    carbon_monthly = {}
    for i in db.query(CarbonAccounting).filter(CarbonAccounting.year == year).all():
        month_key = f"{i.month:02d}"
        if month_key not in carbon_monthly:
            carbon_monthly[month_key] = 0
        carbon_monthly[month_key] += float(i.emission)

    # 碳排放范围分布
    scope1 = 0
    scope2 = 0
    scope3 = 0
    for i in db.query(CarbonAccounting).filter(CarbonAccounting.year == year).all():
        source = db.query(EmissionSource).filter(EmissionSource.id == i.source_id).first()
        s = source.scope if source else "范围1"
        emission = float(i.emission)
        if s == "范围1":
            scope1 += emission
        elif s == "范围2":
            scope2 += emission
        else:
            scope3 += emission

    # 最新碳报告
    report = db.query(CarbonReport).filter(CarbonReport.year == year).first()

    return success(data={
        "year": year,
        "total_consumption": round(total_consumption, 4),
        "total_cost": round(total_cost, 2),
        "total_standard_coal": round(total_standard_coal, 4),
        "total_carbon_emission": round(total_carbon, 6),
        "energy_stats": [{"name": k, "value": round(v, 4)} for k, v in sorted(energy_stats.items(), key=lambda x: -x[1])],
        "carbon_monthly": [{"month": k, "emission": round(v, 6)} for k, v in sorted(carbon_monthly.items())],
        "carbon_scope": {
            "scope1": round(scope1, 6),
            "scope2": round(scope2, 6),
            "scope3": round(scope3, 6),
        },
        "report_status": report.status if report else "未生成",
    })


@router.get("/realtime")
def get_realtime_data(db: Session = Depends(get_db)):
    """实时数据（数据大屏用）"""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    year = datetime.now().year
    month = datetime.now().month

    # 今日能耗
    today_readings = db.query(MeterReading).filter(MeterReading.reading_time == today).all()
    today_manuals = db.query(ManualEntry).filter(ManualEntry.entry_date == today).all()
    today_energy = sum(float(r.standard_coal) for r in today_readings) + sum(float(m.standard_coal) for m in today_manuals)

    # 本月能耗
    month_start = f"{year}-{month:02d}-01"
    month_readings = db.query(MeterReading).filter(
        MeterReading.reading_time >= month_start, MeterReading.reading_time <= today
    ).all()
    month_manuals = db.query(ManualEntry).filter(
        ManualEntry.entry_date >= month_start, ManualEntry.entry_date <= today
    ).all()
    month_energy = sum(float(r.standard_coal) for r in month_readings) + sum(float(m.standard_coal) for m in month_manuals)

    # 本年能耗
    year_start = f"{year}-01-01"
    year_readings = db.query(MeterReading).filter(
        MeterReading.reading_time >= year_start, MeterReading.reading_time <= today
    ).all()
    year_manuals = db.query(ManualEntry).filter(
        ManualEntry.entry_date >= year_start, ManualEntry.entry_date <= today
    ).all()
    year_energy = sum(float(r.standard_coal) for r in year_readings) + sum(float(m.standard_coal) for m in year_manuals)

    # 用能单元排行
    unit_energy = {}
    for m in year_manuals:
        unit = db.query(EnergyUnit).filter(EnergyUnit.id == m.unit_id).first()
        if unit:
            if unit.name not in unit_energy:
                unit_energy[unit.name] = 0
            unit_energy[unit.name] += float(m.standard_coal)

    # 设备在线统计
    total_meters = db.query(Meter).count()
    active_meters = db.query(Meter).filter(Meter.is_active == True).count()

    # 本月碳排放
    month_carbon = sum(float(r.carbon_emission) for r in month_readings) + sum(float(m.carbon_emission) for m in month_manuals)

    return success(data={
        "today_energy": round(today_energy, 4),
        "month_energy": round(month_energy, 4),
        "year_energy": round(year_energy, 4),
        "month_carbon": round(month_carbon, 6),
        "total_meters": total_meters,
        "active_meters": active_meters,
        "offline_meters": total_meters - active_meters,
        "unit_ranking": [{"name": k, "value": round(v, 4)} for k, v in sorted(unit_energy.items(), key=lambda x: -x[1])[:10]],
    })
