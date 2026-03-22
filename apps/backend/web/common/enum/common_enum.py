from enum import Enum, IntEnum
from web.common.utils.enum_utils import register_labels_by_name


@register_labels_by_name(
    {
        "CNY": "人民币",
        "USD": "美元",
        "EUR": "欧元",
        "HKD": "港币",
    }
)
class CurrencyEnum(Enum):
    """
    货币类型枚举
    0-CNY人民币
    1-USD美元
    2-EUR欧元
    3-HKD港币
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
class MarketEnum(IntEnum):
    """
    市场枚举
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
        "XQ": "雪球",
        "YAHOO": "雅虎",
        "BLOOMBERG": "彭博",
        "WIND": "万得",
        "AKSHARE": "AkShare",
        "EASTMONEY": "东方财富",
        "TUSHARE": "TuShare",
        "SINA": "新浪",
    }
)
class ProviderCodeEnum(Enum):
    """
    数据提供商代码枚举
    用于统一 AssetAlias.provider_code 的取值范围
    """

    XQ = "xq"
    YAHOO = "yahoo"
    BLOOMBERG = "bloomberg"
    WIND = "wind"
    AKSHARE = "akshare"
    EASTMONEY = "eastmoney"
    TUSHARE = "tushare"
    SINA = "sina"
