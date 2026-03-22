from enum import Enum, IntEnum

from web.common.utils.enum_utils import register_labels_by_name


@register_labels_by_name(
    {
        "PENDING": "待执行",
        "PROCESSING": "执行中",
        "RETRY_WAITING": "等待重试",
        "SUCCEEDED": "执行成功",
        "FAILED": "执行失败",
    }
)
class NotificationOutboxStatusEnum(IntEnum):
    PENDING = 0
    PROCESSING = 1
    RETRY_WAITING = 2
    SUCCEEDED = 3
    FAILED = 4


class NotificationOutboxEventTypeEnum(str, Enum):
    NOTIFICATION_DISPATCH = "notification_dispatch"
