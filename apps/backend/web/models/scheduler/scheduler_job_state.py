from flask_marshmallow import Schema
from marshmallow import fields
from sqlalchemy import text

from web.models import db


class SchedulerJobState(db.Model):
    __tablename__ = "tb_apscheduler_job_state"
    __bind_key__ = "snowball"
    __table_args__ = {
        "comment": "apscheduler任务当前状态表",
    }

    job_id = db.Column(
        db.String(100),
        primary_key=True,
        comment="任务对应的模块方法",
    )
    last_execution_state = db.Column(
        db.Integer,
        nullable=False,
        comment="最近一次任务状态：0-已提交，1-已执行，2-执行异常，3-错过执行",
    )
    last_scheduler_run_time = db.Column(db.DateTime, comment="最近一次计划运行时间")
    last_submitted_time = db.Column(db.DateTime, comment="最近一次提交时间")
    last_finished_time = db.Column(db.DateTime, comment="最近一次完成时间")
    last_signal_run_time = db.Column(db.DateTime, comment="最近一次有业务信号的成功时间")
    last_error = db.Column(db.Text, comment="最近一次错误信息")
    last_error_time = db.Column(db.DateTime, comment="最近一次错误时间")
    create_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="数据创建时间",
    )
    update_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        comment="数据更新时间",
    )


class SchedulerJobStateSchema(Schema):
    job_id = fields.String()
    last_execution_state = fields.Integer()
    last_scheduler_run_time = fields.DateTime()
    last_submitted_time = fields.DateTime()
    last_finished_time = fields.DateTime()
    last_signal_run_time = fields.DateTime()
    last_error = fields.String()
    last_error_time = fields.DateTime()
    create_time = fields.DateTime()
    update_time = fields.DateTime()
