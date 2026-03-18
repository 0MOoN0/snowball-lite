from enum import Enum, IntEnum
from web.common.utils.enum_utils import register_labels_by_name


@register_labels_by_name({
    "GRID_TRADE": "网格交易",
    "MESSAGE_REMIND": "消息提醒",
    "SYSTEM_RUNNING": "系统运行",
    "DAILY_REPORT": "日常报告",
    "CB_SUBSCRIBE": "可转债申购",
})
class NotificationBusinessTypeEnum(IntEnum):
    """
    通知业务类型枚举
    0 GRID_TRADE: 网格交易通知
    1 MESSAGE_REMIND: 消息处理提醒通知
    2 SYSTEM_RUNNING: 系统运行通知
    3 DAILY_REPORT: 日常报告通知
    4 CB_SUBSCRIBE: 可转债申购通知
    """

    GRID_TRADE = 0
    """
    网格交易通知
    """
    MESSAGE_REMIND = 1
    """
    消息处理提醒通知
    """
    SYSTEM_RUNNING = 2
    """
    系统运行通知
    """
    DAILY_REPORT = 3
    """
    日常报告通知
    """
    CB_SUBSCRIBE = 4
    """
    可转债申购通知
    """


@register_labels_by_name({
    "INFO_MESSAGE": "消息型通知",
    "CONFIRM_MESSAGE": "确认型通知",
})
class NotificationNoticeTypeEnum(Enum):
    """
    通知的类型，0-消息型通知，1-确认型通知
    消息型通知：只是通知，不需要用户确认
    确认型通知：需要用户确认，比如用户需要确认是否交易基金
    """

    INFO_MESSAGE = 0
    """
    消息型通知
    """
    CONFIRM_MESSAGE = 1
    """
    确认型通知
    """


@register_labels_by_name({
    "NOT_SENT": "未发送",
    "NOT_READ": "未读",
    "READ": "已读",
    "PROCESSED": "已处理",
    "SENT": "已发送",
})
class NotificationStatusEnum(IntEnum):
    """
    通知的状态：0-未发送，1-未读，2-已读，3-已处理，4-已发送
    """

    NOT_SENT = 0
    """
    未发送
    """
    NOT_READ = 1
    """
    未读
    """
    READ = 2
    """
    已读
    """
    PROCESSED = 3
    """
    已处理
    """
    SENT = 4
    """
    已发送
    """
