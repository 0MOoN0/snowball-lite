from enum import Enum, IntEnum
from web.common.enum.common_enum import ProviderCodeEnum
from web.common.utils.enum_utils import register_labels_by_name


@register_labels_by_name(
    {
        "INDEX": "指数",
        "FUND": "基金",
        "STOCK": "股票",
        "ASSET": "基础资产",
        "FUND_ETF": "ETF基金",
        "FUND_LOF": "LOF基金",
    }
)
class AssetTypeEnum(IntEnum):
    """
    资产类型枚举，
    包括：指数，基金，股票等
    以及与asset_subtype字段匹配的子类型
    """

    INDEX = 0
    """
    指数
    """

    FUND = 1
    """
    基金
    """

    STOCK = 2
    """
    股票
    """

    ASSET = 3
    """
    基础资产
    """

    FUND_ETF = 4
    """
    ETF基金
    """

    FUND_LOF = 5
    """
    LOF基金
    """


@register_labels_by_name(
    {
        "CNY": "人民币",
        "USD": "美元",
        "EUR": "欧元",
        "HKD": "港币",
    }
)
class AssetCurrencyEnum(Enum):
    """
    货币类型枚举
    0-RMB
    1-USD
    2-EUR
    3-HKD
    """

    CNY = 0
    """
    人民币
    """
    USD = 1
    """
    美元
    """
    EUR = 2
    """
    欧元
    """
    HKD = 3
    """
    港币
    """


@register_labels_by_name(
    {
        "CN": "中国",
        "HK": "香港",
        "US": "美国",
    }
)
class AssetMarketEnum(IntEnum):
    """
    资产市场枚举
    0-CN中国
    1-HK香港
    2-US美国
    """

    CN = 0
    """
    中国
    """
    HK = 1
    """
    香港
    """
    US = 2
    """
    美国
    """


@register_labels_by_name(
    {
        "ACTIVE": "活跃",
        "DELISTED": "退市",
    }
)
class AssetStatusEnum(IntEnum):
    """
    资产状态枚举
    0-ACTIVE活跃
    1-DELISTED退市
    """

    ACTIVE = 0
    """
    活跃
    """
    DELISTED = 1
    """
    退市
    """
