from enum import Enum, IntEnum
from web.common.utils.enum_utils import register_labels_by_name


@register_labels_by_name(
    {
        "INDEX_FUND": "指数基金 - 跟踪特定指数的基金",
        "STOCK_FUND": "股票基金 - 主要投资于股票市场的基金",
        "BOND_FUND": "债券基金 - 主要投资于债券市场的基金",
        "MONEY_MARKET_FUND": "货币市场基金 - 投资于短期货币市场工具的基金",
        "HYBRID_FUND": "混合型基金 - 同时投资股票和债券的基金",
        "QDII_FUND": "QDII基金 - 投资于海外市场的基金",
    }
)
class FundTypeEnum(Enum):
    """
    基金投资策略类型枚举
    按照投资策略和投资标的进行分类
    """

    INDEX_FUND = "INDEX_FUND"
    """
    指数基金 - 跟踪特定指数的基金
    """

    STOCK_FUND = "STOCK_FUND"
    """
    股票基金 - 主要投资于股票市场的基金
    """

    BOND_FUND = "BOND_FUND"
    """
    债券基金 - 主要投资于债券市场的基金
    """

    MONEY_MARKET_FUND = "MONEY_MARKET_FUND"
    """
    货币市场基金 - 投资于短期货币市场工具的基金
    """

    HYBRID_FUND = "HYBRID_FUND"
    """
    混合型基金 - 同时投资股票和债券的基金
    """

    QDII_FUND = "QDII_FUND"
    """
    QDII基金 - 投资于海外市场的基金
    """


@register_labels_by_name(
    {
        "ETF": "交易型开放式基金 - 可在交易所交易的开放式基金",
        "LOF": "上市型开放式基金 - 既可场内交易又可场外申赎的基金",
        "OPEN_END": "开放式基金 - 传统的场外申购赎回基金",
        "CLOSED_END": "封闭式基金 - 固定份额在交易所交易的基金",
    }
)
class FundTradingModeEnum(Enum):
    """
    基金交易方式枚举
    按照交易方式和流通性进行分类
    """

    ETF = "ETF"
    """
    交易型开放式基金 - 可在交易所交易的开放式基金
    """

    LOF = "LOF"
    """
    上市型开放式基金 - 既可场内交易又可场外申赎的基金
    """

    OPEN_END = "OPEN_END"
    """
    开放式基金 - 传统的场外申购赎回基金
    """

    CLOSED_END = "CLOSED_END"
    """
    封闭式基金 - 固定份额在交易所交易的基金
    """


@register_labels_by_name(
    {
        "ACTIVE": "正常运作",
        "SUSPENDED": "暂停申购/赎回",
        "LIQUIDATED": "已清盘",
        "MERGED": "已合并",
    }
)
class FundStatusEnum(IntEnum):
    """
    基金状态枚举
    """

    ACTIVE = 0
    """
    正常运作
    """

    SUSPENDED = 1
    """
    暂停申购/赎回
    """

    LIQUIDATED = 2
    """
    已清盘
    """

    MERGED = 3
    """
    已合并
    """
