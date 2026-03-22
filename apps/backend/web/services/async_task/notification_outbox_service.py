from __future__ import annotations

import json
from datetime import datetime, timedelta

from flask import current_app, has_app_context
from sqlalchemy import or_

from web.models import db
from web.models.async_task.notification_outbox import NotificationOutbox
from web.models.notice.Notification import Notification
from web.scheduler.notification_dispatch import dispatch_notification
from web.weblogger import error, info, warning


class NotificationOutboxService:
    DEFAULT_LIMIT = 20
    DEFAULT_MAX_RETRY_COUNT = 3
    DEFAULT_RETRY_DELAY_SECONDS = 60

    def is_lite_runtime(self, app=None) -> bool:
        if app is None and has_app_context():
            app = current_app
        if app is None:
            return False
        return app.config.get("_config_name") == "lite" or app.config.get("ENV") == "lite"

    def build_notification_event_key(self, notification_id: int) -> str:
        return f"notification-dispatch:{notification_id}"

    def enqueue_notification(
        self,
        notification: Notification,
        *,
        event_key: str | None = None,
        next_run_at: datetime | None = None,
        max_retry_count: int | None = None,
    ) -> NotificationOutbox:
        if notification.id is None:
            raise ValueError("notification.id 不能为空，通知必须先持久化")

        event_type = NotificationOutbox.get_event_type_enum().NOTIFICATION_DISPATCH.value
        event_key = event_key or self.build_notification_event_key(notification.id)
        existing = (
            db.session.query(NotificationOutbox)
            .filter(NotificationOutbox.event_type == event_type)
            .filter(NotificationOutbox.event_key == event_key)
            .first()
        )
        if existing is not None:
            return existing

        outbox_record = NotificationOutbox(
            event_type=event_type,
            event_key=event_key,
            payload=json.dumps({"notification_id": notification.id}, ensure_ascii=False),
            status=NotificationOutbox.get_status_enum().PENDING.value,
            retry_count=0,
            max_retry_count=max_retry_count or self.DEFAULT_MAX_RETRY_COUNT,
            next_run_at=next_run_at or datetime.now(),
        )
        db.session.add(outbox_record)
        db.session.commit()
        info(
            "lite 通知 outbox 入队成功: notification_id=%s, event_key=%s",
            notification.id,
            event_key,
        )
        return outbox_record

    def get_latest_record(self) -> NotificationOutbox | None:
        return (
            db.session.query(NotificationOutbox)
            .order_by(NotificationOutbox.id.desc())
            .first()
        )

    def process_due_events(
        self,
        *,
        now: datetime | None = None,
        limit: int = DEFAULT_LIMIT,
    ) -> dict[str, int]:
        now = now or datetime.now()
        status_enum = NotificationOutbox.get_status_enum()
        due_event_ids = [
            item.id
            for item in db.session.query(NotificationOutbox.id)
            .filter(
                or_(
                    NotificationOutbox.status == status_enum.PENDING.value,
                    NotificationOutbox.status == status_enum.RETRY_WAITING.value,
                )
            )
            .filter(NotificationOutbox.next_run_at <= now)
            .order_by(NotificationOutbox.next_run_at.asc(), NotificationOutbox.id.asc())
            .limit(limit)
            .all()
        ]

        stats = {
            "claimed": 0,
            "succeeded": 0,
            "retried": 0,
            "failed": 0,
            "skipped": 0,
        }
        for event_id in due_event_ids:
            event = self._claim_event(event_id=event_id, now=now)
            if event is None:
                stats["skipped"] += 1
                continue

            stats["claimed"] += 1
            result = self._process_claimed_event(event=event, now=now)
            stats[result] += 1

        return stats

    def _claim_event(
        self,
        *,
        event_id: int,
        now: datetime,
    ) -> NotificationOutbox | None:
        status_enum = NotificationOutbox.get_status_enum()
        updated = (
            db.session.query(NotificationOutbox)
            .filter(NotificationOutbox.id == event_id)
            .filter(
                NotificationOutbox.status.in_(
                    [
                        status_enum.PENDING.value,
                        status_enum.RETRY_WAITING.value,
                    ]
                )
            )
            .update(
                {
                    NotificationOutbox.status: status_enum.PROCESSING.value,
                    NotificationOutbox.updated_at: now,
                },
                synchronize_session=False,
            )
        )
        db.session.commit()
        if updated == 0:
            return None

        return (
            db.session.query(NotificationOutbox)
            .filter(NotificationOutbox.id == event_id)
            .first()
        )

    def _process_claimed_event(
        self,
        *,
        event: NotificationOutbox,
        now: datetime,
    ) -> str:
        try:
            payload = event.payload_dict()
        except Exception as exc:
            self._mark_failed(event=event, error_message=f"payload parse failed: {exc}", now=now)
            return "failed"

        if (
            event.event_type
            != NotificationOutbox.get_event_type_enum().NOTIFICATION_DISPATCH.value
        ):
            self._mark_failed(
                event=event,
                error_message=f"unsupported event_type: {event.event_type}",
                now=now,
            )
            return "failed"

        notification_id = payload.get("notification_id")
        if notification_id is None:
            self._mark_failed(event=event, error_message="payload missing notification_id", now=now)
            return "failed"

        notification = (
            db.session.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )
        if notification is None:
            self._mark_failed(
                event=event,
                error_message=f"notification not found: {notification_id}",
                now=now,
            )
            return "failed"

        try:
            sent, channel = dispatch_notification(notification)
        except Exception as exc:
            warning(f"消费通知 outbox 时 dispatch 抛异常，将进入重试: {exc}")
            return self._mark_retry_or_fail(
                event=event,
                error_message=f"dispatch_notification raised: {exc}",
                now=now,
            )

        if sent:
            self._mark_succeeded(event=event, now=now)
            info(
                "lite 通知 outbox 消费成功: outbox_id=%s, notification_id=%s, channel=%s",
                event.id,
                notification_id,
                channel,
            )
            return "succeeded"

        return self._mark_retry_or_fail(
            event=event,
            error_message=f"dispatch_notification returned {channel}",
            now=now,
        )

    def _mark_succeeded(self, *, event: NotificationOutbox, now: datetime) -> None:
        event.status = NotificationOutbox.get_status_enum().SUCCEEDED.value
        event.last_error = None
        event.updated_at = now
        db.session.add(event)
        db.session.commit()

    def _mark_failed(
        self,
        *,
        event: NotificationOutbox,
        error_message: str,
        now: datetime,
    ) -> None:
        event.status = NotificationOutbox.get_status_enum().FAILED.value
        event.last_error = error_message
        event.updated_at = now
        db.session.add(event)
        db.session.commit()
        error(f"lite 通知 outbox 执行失败: outbox_id={event.id}, error={error_message}")

    def _mark_retry_or_fail(
        self,
        *,
        event: NotificationOutbox,
        error_message: str,
        now: datetime,
    ) -> str:
        next_retry_count = int(event.retry_count or 0) + 1
        event.retry_count = next_retry_count
        event.last_error = error_message
        event.updated_at = now

        if next_retry_count > int(event.max_retry_count or self.DEFAULT_MAX_RETRY_COUNT):
            event.status = NotificationOutbox.get_status_enum().FAILED.value
            db.session.add(event)
            db.session.commit()
            error(
                f"lite 通知 outbox 超过最大重试次数: outbox_id={event.id}, retry_count={next_retry_count}"
            )
            return "failed"

        event.status = NotificationOutbox.get_status_enum().RETRY_WAITING.value
        event.next_run_at = now + timedelta(seconds=self.DEFAULT_RETRY_DELAY_SECONDS)
        db.session.add(event)
        db.session.commit()
        warning(
            f"lite 通知 outbox 进入重试等待: outbox_id={event.id}, retry_count={next_retry_count}"
        )
        return "retried"


notification_outbox_service = NotificationOutboxService()
