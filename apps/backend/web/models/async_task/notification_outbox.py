import json

from sqlalchemy import func, text

from web.common.enum.task.notification_outbox_enum import (
    NotificationOutboxEventTypeEnum,
    NotificationOutboxStatusEnum,
)
from web.models import db


class NotificationOutbox(db.Model):
    __tablename__ = "tb_notification_outbox"
    __bind_key__ = "snowball"
    __table_args__ = (
        db.UniqueConstraint(
            "event_type",
            "event_key",
            name="uq_notification_outbox_event_type_event_key",
        ),
        db.Index(
            "ix_notification_outbox_status_next_run_at",
            "status",
            "next_run_at",
        ),
        {"comment": "lite 通知 outbox"},
    )

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    event_type = db.Column(db.String(64), nullable=False, comment="事件类型")
    event_key = db.Column(db.String(191), nullable=False, comment="业务去重键")
    payload = db.Column(db.Text, nullable=False, comment="事件载荷(JSON)")
    status = db.Column(
        db.SmallInteger,
        nullable=False,
        server_default="0",
        comment="状态：0-待执行，1-执行中，2-等待重试，3-成功，4-失败",
    )
    retry_count = db.Column(
        db.Integer,
        nullable=False,
        server_default="0",
        comment="已执行重试次数",
    )
    max_retry_count = db.Column(
        db.Integer,
        nullable=False,
        server_default="3",
        comment="最大重试次数",
    )
    next_run_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="下次执行时间",
    )
    last_error = db.Column(db.Text, nullable=True, comment="最近一次错误信息")
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.now(),
        comment="更新时间",
    )

    @staticmethod
    def get_status_enum() -> NotificationOutboxStatusEnum:
        return NotificationOutboxStatusEnum

    @staticmethod
    def get_event_type_enum() -> NotificationOutboxEventTypeEnum:
        return NotificationOutboxEventTypeEnum

    def payload_dict(self) -> dict:
        return json.loads(self.payload or "{}")
