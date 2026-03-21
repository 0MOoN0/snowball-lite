from enum import Enum


class DailyTypeEnum(Enum):
    """
    日线数据类型枚举DailyTypeEnum
    """

    # 收盘价
    CLOSE = 1
    # 单位净值
    NETVALUE = 2
    # 累计净值
    TOTVALUE = 3
