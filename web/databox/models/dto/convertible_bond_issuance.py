from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date


@dataclass
class ConvertibleBondIssuanceData:
    """
    可转债发行数据模型（只读 DTO）
    对齐 AkShare bond_cov_issue_cninfo，所有字段均可空以适配不同版本与缺失情况。
    单位保持原始值（如 万元/元），不在 DTO 层做单位换算。
    """

    bond_code: str  # 债券代码
    bond_name: str  # 债券简称
    market: Optional[str] = None  # 交易市场（原始值）
    full_name: Optional[str] = None  # 债券名称（全称）

    # 日期相关
    issue_date: Optional[date] = None  # 公告日期/发行日期（以 cninfo 的“公告日期”为准）
    issue_start_date: Optional[date] = None  # 发行起始日
    issue_end_date: Optional[date] = None  # 发行终止日
    convert_start_date: Optional[date] = None  # 转股开始日期
    convert_end_date: Optional[date] = None  # 转股终止日期
    convert_happen_date: Optional[date] = None  # 转股发生日（部分数据源提供）
    online_subscribe_date: Optional[date] = None  # 网上申购日期
    online_result_announce_and_refund_date: Optional[date] = None  # 网上申购中签结果公告日及退款日
    priority_subscribe_date: Optional[date] = None  # 优先申购日
    bond_register_date: Optional[date] = None  # 债权登记日
    priority_subscribe_payment_date: Optional[date] = None  # 优先申购缴款日

    # 数值与文本（保持原始单位）
    planned_total_amount: Optional[float] = None  # 计划发行总量（万元）
    actual_total_amount: Optional[float] = None  # 实际发行总量（万元）
    par_value: Optional[int] = None  # 发行面值（元）
    issue_price: Optional[float] = None  # 发行价格（元）
    issue_method: Optional[str] = None  # 发行方式
    issue_target: Optional[str] = None  # 发行对象
    issue_scope: Optional[str] = None  # 发行范围
    underwriting_method: Optional[str] = None  # 承销方式
    use_of_proceeds: Optional[str] = None  # 募资用途说明
    initial_conversion_price: Optional[float] = None  # 初始转股价格（元）
    online_subscribe_code: Optional[str] = None  # 网上申购代码
    online_subscribe_name: Optional[str] = None  # 网上申购简称
    online_subscribe_upper_limit: Optional[float] = None  # 网上申购数量上限（万元）
    online_subscribe_lower_limit: Optional[float] = None  # 网上申购数量下限（万元）
    online_subscribe_unit: Optional[float] = None  # 网上申购单位
    placement_price: Optional[float] = None  # 配售价格（元）
    convert_code: Optional[str] = None  # 转股代码

    # 兼容旧字段（若存在“发行规模(亿元)”，映射到此字段）
    issue_amount: Optional[float] = None  # 发行规模（亿元）

    data_source: Optional[str] = None  # 数据来源标识
    update_time: Optional[datetime] = None  # 更新时间