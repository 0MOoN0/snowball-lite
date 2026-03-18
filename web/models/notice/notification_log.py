# -*- coding: UTF-8 -*-
"""
@File    ：notification_log.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/10/2 18:58
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text

from web.models import db


class NotificationLog(db.Model):
    __bind_key__ = "snowball"
    __tablename__ = 'tb_notification_log'
    __table_args__ = (
        {'comment': '通知日志表'}
    )

    id = db.Column(db.BigInteger, primary_key=True, comment='主键', autoincrement=True)
    notification_id = db.Column(db.BigInteger, nullable=False, comment='通知ID')
    traceback_info = db.Column(db.Text, comment='异常栈信息')
    create_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='数据创建时间')
    update_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=func.now(), comment='数据更新时间')
