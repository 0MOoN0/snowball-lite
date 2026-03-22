# 常用枚举
from enum import Enum


class FeeEnum(Enum):
    """
    交易费用枚举
    """

    # ETF交易费用
    ETF_TRADE = 0.0001
    # LOF场内申购4折
    # 上海可转债交易费百万分之5
    SH_CB = 0.000005
    # 深圳可转债交易费十万分之8
    SZ_CB = 0.00008
    # 股票交易费用万分之2.5
    STOCK_TRADE = 0.00025




class RecordDirectionEnum(Enum):
    """
    交易记录方向
    0-卖出
    1-买入
    2-转出
    3-赎回
    """
    SELL = 0
    """
    0-卖出
    """
    PURCHASE = 1
    """
    1-买入
    """
    TRANSFER_OUT = 2
    """
    2-转出
    """
    REDEMPTION = 3
    """
    3-赎回
    """

class NoticeTypeEnum(Enum):
    """
    通知类型
    1-网格通知
    0-其他
    """
    OTHER = 0
    GRID = 1


class OrderTypeEnum(Enum):
    """
    排序类型
    1-升序排序
    0-降序排序
    """
    DESC = 0
    ASC = 1


class AssetFeeTypeEnum(Enum):
    """
    资产交易费用
    0-申购费
    1-赎回费率
    """
    PURCHASE = 0
    """
    0 - 申购
    """
    REDEMPTION = 1
    """
    1 - 赎回
    """





class NotificationChannelEnum(Enum):
    """
    通知渠道枚举
    """
    SERVERCHAN = "serverchan"
    TELEGRAM = "telegram"
    PUSHPLUS = "pushplus"
    WECOM = "wecom"


class NotificationBusinessTypeEnum(Enum):
    """
    通知业务类型枚举
    """
    GRID = "grid"  # 网格交易
    SYSTEM = "system"  # 系统通知


