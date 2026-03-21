from enum import IntEnum
from web.common.utils.enum_utils import register_labels_by_name


@register_labels_by_name(
    {
        "STOCK": "股票指数",
        "BOND": "债券指数",
        "COMMODITY": "商品指数",
        "CURRENCY": "货币指数",
        "MIXED": "混合指数",
        "OTHER": "其他",
    }
)
class IndexTypeEnum(IntEnum):
    """
    指数类型枚举（底层资产类型）
    0-股票指数
    1-债券指数
    2-商品指数
    3-货币指数
    4-混合指数
    5-其他
    """
    STOCK = 0
    """
    股票指数
    """
    BOND = 1
    """
    债券指数
    """
    COMMODITY = 2
    """
    商品指数
    """
    CURRENCY = 3
    """
    货币指数
    """
    MIXED = 4
    """
    混合指数
    """
    OTHER = 5
    """
    其他
    """


@register_labels_by_name(
    {
        "BROAD_BASED": "宽基指数",
        "INDUSTRY": "行业指数", 
        "THEME": "主题指数",
        "STRATEGY": "策略指数",
    }
)
class InvestmentStrategyEnum(IntEnum):
    """
    投资策略枚举
    0-宽基指数
    1-行业指数
    2-主题指数
    3-策略指数
    """
    BROAD_BASED = 0
    """
    宽基指数
    """
    INDUSTRY = 1
    """
    行业指数
    """
    THEME = 2
    """
    主题指数
    """
    STRATEGY = 3
    """
    策略指数
    """


@register_labels_by_name(
    {
        "MARKET_CAP": "市值加权",
        "EQUAL_WEIGHT": "等权重",
        "FUNDAMENTAL": "基本面加权",
        "OTHER": "其他",
    }
)
class WeightMethodEnum(IntEnum):
    """
    权重方法枚举
    0-市值加权
    1-等权重
    2-基本面加权
    3-其他
    """
    MARKET_CAP = 0
    """
    市值加权
    """
    EQUAL_WEIGHT = 1
    """
    等权重
    """
    FUNDAMENTAL = 2
    """
    基本面加权
    """
    OTHER = 3
    """
    其他
    """


@register_labels_by_name(
    {
        "PRICE_WEIGHTED": "价格加权",
        "TOTAL_RETURN": "总收益",
        "NET_RETURN": "净收益",
        "OTHER": "其他",
    }
)
class CalculationMethodEnum(IntEnum):
    """
    计算方法枚举
    0-价格加权
    1-总收益
    2-净收益
    3-其他
    """
    PRICE_WEIGHTED = 0
    """
    价格加权
    """
    TOTAL_RETURN = 1
    """
    总收益
    """
    NET_RETURN = 2
    """
    净收益
    """
    OTHER = 3
    """
    其他
    """


@register_labels_by_name(
    {
        "DISABLED": "停用",
        "ENABLED": "启用",
    }
)
class IndexStatusEnum(IntEnum):
    """
    指数状态枚举
    0-停用
    1-启用
    """
    DISABLED = 0
    """
    停用
    """
    ENABLED = 1
    """
    启用
    """