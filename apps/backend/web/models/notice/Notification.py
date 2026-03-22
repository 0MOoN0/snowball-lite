# 通知模型
from flask_marshmallow import Schema
from marshmallow import fields, post_load, post_dump
from marshmallow_sqlalchemy import SQLAlchemySchema, SQLAlchemyAutoSchema
from sqlalchemy import func, text

from web.common.enum.NotificationEnum import (
    NotificationBusinessTypeEnum,
    NotificationNoticeTypeEnum,
    NotificationStatusEnum,
)
from web.models import db


class Notification(db.Model):
    __bind_key__ = "snowball"
    __tablename__ = "tb_notification"
    __table_args__ = {"comment": "通知模型"}
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    business_type = db.Column(
        db.SmallInteger,
        nullable=False,
        server_default="0",
        comment="通知的业务类型，0-网格交易通知,1-消息处理提醒通知,2-系统运行通知,3-日常报告通知",
    )  # 通知的业务类型，比如日志、系统等
    notice_type = db.Column(
        db.SmallInteger,
        nullable=False,
        server_default="0",
        comment="通知的类型，0-消息型通知，1-确认型通知",
    )
    """
    通知的类型，0-消息型通知，1-确认型通知
    消息型通知：只是通知，不需要用户确认
    确认型通知：需要用户确认，比如用户需要确认是否交易基金
    """
    notice_status = db.Column(
        db.SmallInteger,
        nullable=False,
        server_default="0",
        comment="通知的状态：0-未发送，1-未读，2-已读，3-已处理，4-已发送",
    )
    """
    通知的状态：0-未发送，1-未读，2-已读，3-已处理，4-已发送
    """
    content = db.Column(db.Text, comment="通知的内容")  # 通知的内容
    timestamp = db.Column(db.DateTime, comment="通知的时间")  # 通知的时间
    create_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )
    update_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.now(),
        comment="更新时间",
    )
    """
    通知重要性等级，重要性按数字递增，最小为0
    """
    notice_level = db.Column(
        db.SmallInteger,
        nullable=False,
        server_default="0",
        comment="通知重要性等级，重要性按数字递增，最小为0",
    )
    title = db.Column(
        db.String(255),
        nullable=False,
        server_default=db.FetchedValue(),
        comment="通知标题",
    )
    template_key = db.Column(
        db.String(100),
        nullable=True,
        comment="完整模板文件名（含扩展名），如：summary.txt、detailed.html、urgent.txt等",
    )

    @staticmethod
    def get_business_type_enum() -> NotificationBusinessTypeEnum:
        """
        获取通知业务类型枚举
        Returns:
            NotificationBusinessTypeEnum 通知业务类型枚举
        """
        return NotificationBusinessTypeEnum

    @staticmethod
    def get_notice_type_enum() -> NotificationNoticeTypeEnum:
        """
        获取通知状态
        Returns:
            int 通知状态
        """
        return NotificationNoticeTypeEnum

    @staticmethod
    def get_notice_status_enum() -> NotificationStatusEnum:
        """
        获取通知状态
        Returns:
            int 通知状态
        """
        return NotificationStatusEnum


class NotificationSchema(Schema):
    id = fields.Integer(allow_none=True)
    business_type = fields.Integer(allow_none=True)
    notice_type = fields.Integer(allow_none=True)
    notice_status = fields.Integer(allow_none=True)
    content = fields.String(allow_none=True)
    timestamp = fields.DateTime(allow_none=True)
    create_time = fields.DateTime(allow_none=True)
    update_time = fields.DateTime(allow_none=True)
    notice_level = fields.Integer(allow_none=True)
    title = fields.String(allow_none=True)
    template_key = fields.String(allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return Notification(**data)

    SKIP_VALUES = set([None])

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }


class NotificationVOSchema(Schema):
    id = fields.Integer(allow_none=True)
    business_type = fields.Integer(allow_none=True, data_key="businessType")
    notice_type = fields.Integer(allow_none=True, data_key="noticeType")
    notice_status = fields.Integer(allow_none=True, data_key="noticeStatus")
    content = fields.String(allow_none=True, data_key="content")
    timestamp = fields.DateTime(
        allow_none=True,
        data_key="timestamp",
        format="%Y-%m-%d %H:%M:%S",
        error_messages={"invalid": "timestamp格式必须为YYYY-MM-DD HH:mm:ss"},
    )
    create_time = fields.DateTime(allow_none=True, data_key="createTime")
    update_time = fields.DateTime(allow_none=True, data_key="updateTime")
    notice_level = fields.Integer(allow_none=True, data_key="noticeLevel")
    title = fields.String(allow_none=True)
    template_key = fields.String(allow_none=True, data_key="templateKey")

    SKIP_VALUES = set([None])

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }
