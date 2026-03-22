from flask_marshmallow import Schema
from marshmallow import fields
from sqlalchemy import func, text

from web.common.enum.task.scheduler_state_enum import SchedulerStateEnum
from web.models import db


class SchedulerLog(db.Model):
    __tablename__ = 'tb_apscheduler_log'
    __bind_key__ = "snowball"
    __table_args__ = {
        'comment': 'apscheduler执行日志记录表'
    }

    id = db.Column(db.BigInteger, primary_key=True, comment='id', autoincrement=True)
    job_id = db.Column(db.String(100), nullable=False, comment='任务对应的模块方法')
    execution_state = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(),
                                comment='任务状态：0-已提交，1-已执行，2-执行异常，3-错过执行')
    scheduler_run_time = db.Column(db.DateTime, comment='预计执行时间')
    exception = db.Column(db.Text, comment='执行异常')
    traceback = db.Column(db.Text, comment='异常栈信息')
    create_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='数据创建时间')
    update_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=func.now(), comment='数据更新时间')

    @staticmethod
    def get_scheduler_state_enum():
        return SchedulerStateEnum


class SchedulerLogSchema(Schema):
    id = fields.Integer()
    job_id = fields.String()
    execution_state = fields.Integer()
    scheduler_run_time = fields.DateTime()
    exception = fields.String()
    traceback = fields.String()
    create_time = fields.DateTime()
    update_time = fields.DateTime()


class SchedulerLogVOSchema(Schema):
    id = fields.Integer()
    job_id = fields.String(data_key='jobId')
    execution_state = fields.Integer(data_key='executionState')
    scheduler_run_time = fields.DateTime(data_key='schedulerRunTime')
    exception = fields.String()
    traceback = fields.String()
