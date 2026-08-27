"""数据库初始化 + 种子数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import *  # noqa - 触发所有表注册
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_database():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("[OK] 数据库表创建完成")


def seed_data():
    """插入种子数据"""
    db = SessionLocal()
    try:
        # 检查是否已有数据
        if db.query(User).first():
            print("[SKIP] 种子数据已存在，跳过")
            return

        # 1. 管理员账号
        admin = User(
            username="admin",
            password_hash=pwd_context.hash("admin123"),
            name="系统管理员",
            role="admin",
        )
        db.add(admin)

        # 2. 默认企业信息
        org = Organization(
            name="示例制造有限公司",
            credit_code="91110000MA12345678",
            industry="通用制造业",
            address="河南省郑州市XX区XX路XX号",
            contact="张经理",
            phone="0371-12345678",
            scale="中型企业",
            established_date="2010-01-01",
        )
        db.add(org)

        # 3. 默认能源类型（通用制造业）
        energy_types = [
            EnergyType(code="E001", name="电力", unit="kWh",
                       standard_coal_coefficient=0.1229, carbon_factor=0.5810,
                       default_price=0.65, sort_order=1),
            EnergyType(code="E002", name="天然气", unit="m³",
                       standard_coal_coefficient=1.3300, carbon_factor=2.1622,
                       default_price=3.50, sort_order=2),
            EnergyType(code="E003", name="蒸汽", unit="MJ",
                       standard_coal_coefficient=0.0341, carbon_factor=0.1100,
                       default_price=0.20, sort_order=3),
            EnergyType(code="E004", name="柴油", unit="kg",
                       standard_coal_coefficient=1.4571, carbon_factor=3.0959,
                       default_price=7.50, sort_order=4),
            EnergyType(code="E005", name="汽油", unit="kg",
                       standard_coal_coefficient=1.4714, carbon_factor=2.9251,
                       default_price=8.00, sort_order=5),
            EnergyType(code="E006", name="原煤", unit="kg",
                       standard_coal_coefficient=0.7143, carbon_factor=1.9003,
                       default_price=0.80, sort_order=6),
        ]
        db.add_all(energy_types)

        # 4. 默认用能单元（两级：车间→设备）
        db.flush()  # 确保ID生成
        units = [
            EnergyUnit(code="U001", name="一车间", level=1, area="A区",
                       responsible_person="李主任", phone="13800000001", sort_order=1),
            EnergyUnit(code="U002", name="二车间", level=1, area="B区",
                       responsible_person="王主任", phone="13800000002", sort_order=2),
            EnergyUnit(code="U003", name="三车间", level=1, area="C区",
                       responsible_person="赵主任", phone="13800000003", sort_order=3),
        ]
        db.add_all(units)
        db.flush()

        # 子单元
        sub_units = [
            EnergyUnit(code="U00101", name="注塑工序", parent_id=units[0].id, level=2, area="A区-1F",
                       responsible_person="张班长", sort_order=1),
            EnergyUnit(code="U00102", name="装配工序", parent_id=units[0].id, level=2, area="A区-2F",
                       responsible_person="刘班长", sort_order=2),
            EnergyUnit(code="U00201", name="喷涂工序", parent_id=units[1].id, level=2, area="B区-1F",
                       responsible_person="陈班长", sort_order=1),
            EnergyUnit(code="U00202", name="包装工序", parent_id=units[1].id, level=2, area="B区-2F",
                       responsible_person="周班长", sort_order=2),
        ]
        db.add_all(sub_units)

        # 5. 默认碳排放因子
        carbon_factors = [
            CarbonFactor(name="电力排放因子（全国电网）", factor_value=0.5810,
                         unit="tCO₂/MWh", source="生态环境部2022", sort_order=1),
            CarbonFactor(name="天然气排放因子", factor_value=2.1622,
                         unit="tCO₂/万m³", source="IPCC 2006", sort_order=2),
            CarbonFactor(name="柴油排放因子", factor_value=3.0959,
                         unit="tCO₂/t", source="IPCC 2006", sort_order=3),
            CarbonFactor(name="汽油排放因子", factor_value=2.9251,
                         unit="tCO₂/t", source="IPCC 2006", sort_order=4),
            CarbonFactor(name="原煤排放因子", factor_value=1.9003,
                         unit="tCO₂/t", source="IPCC 2006", sort_order=5),
        ]
        db.add_all(carbon_factors)

        # 6. 默认排放源
        emission_sources = [
            EmissionSource(code="S001", name="锅炉天然气燃烧", scope="范围1",
                           category="固定燃烧", sort_order=1),
            EmissionSource(code="S002", name="柴油发电机燃烧", scope="范围1",
                           category="固定燃烧", sort_order=2),
            EmissionSource(code="S003", name="公司车辆燃油", scope="范围1",
                           category="移动燃烧", sort_order=3),
            EmissionSource(code="S004", name="外购电力", scope="范围2",
                           category="外购电力", sort_order=4),
            EmissionSource(code="S005", name="外购蒸汽", scope="范围2",
                           category="外购热力", sort_order=5),
            EmissionSource(code="S006", name="员工通勤", scope="范围3",
                           category="员工通勤", sort_order=6),
            EmissionSource(code="S007", name="废弃物处理", scope="范围3",
                           category="废弃物处理", sort_order=7),
        ]
        db.add_all(emission_sources)

        # 7. 默认产品
        products = [
            Product(code="P001", name="产品A", unit="吨", output_unit="吨", sort_order=1),
            Product(code="P002", name="产品B", unit="件", output_unit="件", sort_order=2),
        ]
        db.add_all(products)

        # 8. 系统配置
        configs = [
            SystemConfig(config_key="loss_rate_threshold", config_value="10",
                         config_group="能流", description="损耗率告警阈值(%)"),
            SystemConfig(config_key="data_refresh_interval", config_value="30",
                         config_group="大屏", description="数据大屏刷新间隔(秒)"),
        ]
        db.add_all(configs)

        db.commit()
        print("[OK] 种子数据插入完成")
        print("  管理员账号: admin / admin123")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] 种子数据插入失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("数字化能碳管理系统 - 数据库初始化")
    print("=" * 50)
    init_database()
    seed_data()
    print("=" * 50)
    print("初始化完成！")
