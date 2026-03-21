from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class IndexDividendYieldData:
    """
    股票指数股息率数据模型
    用于存储指数的股息率相关信息
    """
    symbol: str  # 指数代码
    name: str  # 指数名称
    dividend_yield: float  # 股息率（百分比）
    currency: Optional[str] = None  # 货币类型
    update_time: Optional[datetime] = None  # 更新时间
    data_source: Optional[str] = None  # 数据来源