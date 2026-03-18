# -*- coding: UTF-8 -*-
"""
业务通用枚举（Business Common Enums）

用于在业务域内跨模型复用的枚举定义，例如多个指数模型都可能使用的调仓频率。
"""

from enum import Enum
from web.common.utils.enum_utils import register_labels_by_name


@register_labels_by_name(
    {
        "QUARTERLY": "季度",
        "SEMI_ANNUAL": "半年",
        "ANNUAL": "年度",
    }
)
class RebalanceFrequencyEnum(Enum):
    """
    指数调仓频率枚举（业务通用）
    值为字符串，便于与API字段 `rebalanceFrequency` 对齐
    - quarterly: 季度
    - semi_annual: 半年
    - annual: 年度
    """
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"