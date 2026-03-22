from __future__ import annotations

from web.scheduler.base import scheduler
from web.services.async_task.notification_outbox_service import (
    notification_outbox_service,
)
from web.weblogger import logger


mod_logger = logger.getChild(__name__)


def consume_notification_outbox(limit: int = 20) -> dict[str, int]:
    stats = notification_outbox_service.process_due_events(limit=limit)
    mod_logger.info(
        "lite 通知 outbox 消费完成: claimed=%s, succeeded=%s, retried=%s, failed=%s, skipped=%s",
        stats["claimed"],
        stats["succeeded"],
        stats["retried"],
        stats["failed"],
        stats["skipped"],
    )
    return stats


@scheduler.task(
    id="AsyncTaskScheduler.consume_notification_outbox",
    name="lite 通知 outbox 消费（每分钟）",
    trigger="interval",
    seconds=60,
    misfire_grace_time=30,
    coalesce=True,
    max_instances=1,
)
def consume_notification_outbox_job():
    with scheduler.app.app_context():
        if not notification_outbox_service.is_lite_runtime():
            mod_logger.debug("当前不是 lite 运行时，跳过通知 outbox 消费")
            return
        consume_notification_outbox()
