from enum import Enum
from web.common.utils.enum_utils import register_labels_by_name

@register_labels_by_name(
    {
        "APPEND": "增量",
        "OVERWRITE": "全量覆盖",
        "REPLACE": "部分替换",
        "REPLACE_RANGE": "范围替换",
    }
)
class RecordImportModeEnum(Enum):
    """
    记录导入模式
    """
    APPEND = 0
    OVERWRITE = 1
    REPLACE = 2
    REPLACE_RANGE = 3


@register_labels_by_name({"GRID": "网格", "OTHER": "其他"})
class IRecordTypeEnum(Enum):
    """
    交易记录类型
    1-网格，0-其他
    """
    GRID = 1
    OTHER = 0


@register_labels_by_name(
    {
        "PURCHASE": "买入",
        "SELL": "卖出",
        "BUY": "买入",
        "TRANSFER_IN": "转托管入",
        "TRANSFER_OUT": "转托管出",
        "SUBSCRIPTION": "申购",
        "REDEMPTION": "赎回",
    }
)
class RecordDirectionEnum(Enum):
    """
    交易记录方向
    1-买入
    0-卖出
    2-转托管入
    3-转托管出
    """
    PURCHASE = 1
    """
    1-买入
    """
    SELL = 0
    """
    0-卖出
    """
    BUY = 1  # Alias for PURCHASE
    
    TRANSFER_IN = 2
    """
    2-转托管入
    """
    TRANSFER_OUT = 3
    """
    3-转托管出
    """
    SUBSCRIPTION = 4
    """
    4-申购
    """
    REDEMPTION = 5
    """
    5-赎回
    """


@register_labels_by_name({"GRID": "网格", "GRID_TYPE": "网格类型"})
class RecordStrategyKeyEnum(Enum):
    """
    交易记录策略Key
    """
    GRID = 0
    """
    0 - 网格
    """
    GRID_TYPE = 1
    """
    1 - 网格类型
    """
