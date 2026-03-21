from enum import Enum


class IndicatorEnum(str, Enum):
    """
    指标枚举
    - 使用该枚举避免魔法值
    - 随着能力扩展，可在此继续补充（如 PE、PB、ROE 等）
    """

    DIVIDEND_YIELD = "dividend_yield"  # 股息率


