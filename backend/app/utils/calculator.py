"""
能碳计算工具函数
所有计算公式和参数来源均依据国家标准：
- 折标煤系数：GB/T 2589《综合能耗计算通则》
- 碳排放因子：《企业温室气体排放核算方法与报告指南》
"""

from decimal import Decimal, ROUND_HALF_UP


def calc_cost(consumption: float, unit_price: float) -> float:
    """计算费用 = 消耗量 × 单价"""
    return float(Decimal(str(consumption)) * Decimal(str(unit_price)))


def calc_standard_coal(consumption: float, coefficient: float) -> float:
    """计算折标煤 = 消耗量 × 折标煤系数
    coefficient: 折标煤系数，如电力 0.1229 kgce/kWh
    """
    result = Decimal(str(consumption)) * Decimal(str(coefficient))
    return float(result.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP))


def calc_carbon_emission(consumption: float, factor: float) -> float:
    """计算碳排放量 = 消耗量 × 碳排放因子
    factor: 碳排放因子，单位根据能源类型不同而不同
    """
    result = Decimal(str(consumption)) * Decimal(str(factor))
    return float(result.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP))


def calc_unit_consumption(total_consumption: float, output: float) -> float:
    """计算单位产品能耗 = 总能耗 / 总产量"""
    if output == 0:
        return 0
    result = Decimal(str(total_consumption)) / Decimal(str(output))
    return float(result.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP))


def calc_deviation(actual: float, benchmark: float) -> float:
    """计算偏差率 = (实际值 - 基准值) / 基准值 × 100%"""
    if benchmark == 0:
        return 0
    result = (Decimal(str(actual)) - Decimal(str(benchmark))) / Decimal(str(benchmark)) * 100
    return float(result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def get_efficiency_level(deviation: float) -> str:
    """根据偏差率判定能效等级
    偏差率 < -10% → 领先（绿色）
    -10% ≤ 偏差率 < 0 → 先进（蓝色）
    0 ≤ 偏差率 < 20% → 合格（橙色）
    偏差率 ≥ 20% → 落后（红色）
    """
    if deviation < -10:
        return "领先"
    elif deviation < 0:
        return "先进"
    elif deviation < 20:
        return "合格"
    else:
        return "落后"


def calc_budget_value(unit_consumption: float, planned_output: float) -> float:
    """计算预算量 = 单耗 × 计划产量"""
    result = Decimal(str(unit_consumption)) * Decimal(str(planned_output))
    return float(result.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP))


def calc_carbon_budget(intensity: float, planned_output: float) -> float:
    """计算碳排放预算 = 碳排放强度 × 计划产量/产值"""
    result = Decimal(str(intensity)) * Decimal(str(planned_output))
    return float(result.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP))


def calc_footprint_total(raw_material: float, production: float, transport: float,
                         use_phase: float, disposal: float) -> float:
    """计算碳足迹合计 = 原材料 + 生产 + 运输 + 使用 + 废弃处理"""
    result = (Decimal(str(raw_material)) + Decimal(str(production)) +
              Decimal(str(transport)) + Decimal(str(use_phase)) +
              Decimal(str(disposal)))
    return float(result.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP))


def calc_quota_remaining(quantity: float, used_quantity: float) -> float:
    """计算剩余碳资产 = 总量 - 已使用量"""
    result = Decimal(str(quantity)) - Decimal(str(used_quantity))
    return float(result.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP))


def calc_trade_amount(quantity: float, price: float) -> float:
    """计算交易金额 = 数量 × 单价"""
    result = Decimal(str(quantity)) * Decimal(str(price))
    return float(result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def calc_execution_rate(actual: float, budget: float) -> float:
    """计算执行率 = 实际值 / 预算值 × 100%"""
    if budget == 0:
        return 0
    result = Decimal(str(actual)) / Decimal(str(budget)) * 100
    return float(result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def calc_energy_efficiency(input_energy: float, effective_energy: float) -> float:
    """计算综合能效 = 有效利用量 / 输入总量 × 100%"""
    if input_energy == 0:
        return 0
    result = Decimal(str(effective_energy)) / Decimal(str(input_energy)) * 100
    return float(result.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def format_number(value: float, decimals: int = 2) -> str:
    """格式化数字，添加千分位"""
    if value is None:
        return "0"
    if decimals == 0:
        return f"{value:,.0f}"
    return f"{value:,.{decimals}f}"
