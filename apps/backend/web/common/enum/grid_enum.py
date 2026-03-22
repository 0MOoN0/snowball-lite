from enum import IntEnum
from web.common.utils.enum_utils import register_labels_by_name


@register_labels_by_name(
    {
        "ENABLE": "启用",
        "DISABLE": "停用",
    }
)
class GridStatusEnum(IntEnum):
    """
    网格状态枚举
    0：启用，1：停用
    """

    ENABLE = 0
    """
     0 - 启用
    """
    DISABLE = 1
    """
     1 - 停用
    """


@register_labels_by_name(
    {
        "ENABLE": "启用",
        "DISABLE": "停用",
        "SELL_ONLY": "只卖出",
        "BUY_ONLY": "只买入",
    }
)
class GridTypeStatusEnum(IntEnum):
    """
    网格类型状态枚举
    0:启用,1:停用,2:只卖出,3只买入
    """

    ENABLE = 0
    """
    0 - 启用
    """
    DISABLE = 1
    """
    1 - 停用
    """
    SELL_ONLY = 2
    """
    2 - 只卖出
    """
    BUY_ONLY = 3
    """
    3 - 只买入
    """


@register_labels_by_name(
    {
        "BUY": "买入",
        "SELL": "卖出",
    }
)
class GridTypeDetailMonitorTypeEnum(IntEnum):
    """
    网格类型详情监控类型
    0-买入，1-卖出
    """

    BUY = 0
    """
    0 - 买入
    """
    SELL = 1
    """
    1 - 卖出
    """
