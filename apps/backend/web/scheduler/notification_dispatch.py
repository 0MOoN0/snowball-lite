from typing import Tuple

from flask import current_app, has_app_context

from web.models.notice.Notification import Notification, NotificationSchema
from web.services.notice.notification_service import notification_service
from web.task.actors import NotificationActors
from web.weblogger import error, info, warning


def _task_queue_available() -> bool | None:
    if not has_app_context():
        return None

    if "TASK_QUEUE_AVAILABLE" in current_app.config:
        return bool(current_app.config["TASK_QUEUE_AVAILABLE"])

    if "ENABLE_TASK_QUEUE" in current_app.config:
        return bool(current_app.config["ENABLE_TASK_QUEUE"])

    return None


def dispatch_notification(notification: Notification) -> Tuple[bool, str]:
    """
    发送通知，优先走 actor，失败后自动回退到同步发送。

    Returns:
        Tuple[bool, str]: (是否发送成功, 发送方式)
        发送方式取值：
        - actor: 通过 Dramatiq actor 发送成功
        - sync: 通过同步发送成功
        - failed: 两种方式都失败
    """
    notification_json = None
    try:
        notification_json = NotificationSchema().dumps(notification)
    except Exception as exc:
        warning(f"通知序列化失败，跳过Actor直接尝试同步发送: {exc}")

    task_queue_available = _task_queue_available()
    if notification_json is not None and task_queue_available is not False:
        try:
            NotificationActors.send_notification.send(notification_json)
            return True, "actor"
        except Exception as exc:
            warning(f"通知通过Actor发送失败，尝试同步发送: {exc}")
    elif notification_json is not None:
        info("任务队列不可用，跳过Actor直接尝试同步发送通知")

    try:
        success = notification_service.send_notification(notification)
        return bool(success), "sync"
    except Exception as exc:
        error(f"通知同步发送失败: {exc}", exc_info=True)
        return False, "failed"
