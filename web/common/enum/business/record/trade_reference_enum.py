# -*- coding: UTF-8 -*-
"""
交易关联枚举
"""
from enum import IntEnum
from web.common.utils.enum_utils import register_labels_by_name


@register_labels_by_name(
    {
        "OTHER": "其他",
        "GRID": "网格",
    }
)
class TradeReferenceGroupTypeEnum(IntEnum):
    """
    交易关联分组类型枚举
    用于 TradeReference.group_type 字段
    0-其他
    1-网格
    """

    OTHER = 0
    """
    0 - 其他
    """
    GRID = 1
    """
    1 - 网格
    """
