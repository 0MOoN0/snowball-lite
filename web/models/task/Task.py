# coding: utf-8
from sqlalchemy import func, text

from web.models import db


class Task(db.Model):
    __tablename__ = 'tb_task'
    __bind_key__ = "snowball"

    id = db.Column(db.BigInteger, primary_key=True, comment='主键ID', autoincrement=True)
    task_name = db.Column(db.String(255), nullable=False, comment='任务名称')
    task_type = db.Column(db.Integer, nullable=False, server_default='0',
                          comment='任务类型（0一次性任务，1定时任务）')
    task_status = db.Column(db.Integer, server_default='0',
                            comment='任务状态：0未执行，1等待执行，2执行中，3执行完毕')
    business_type = db.Column(db.Integer, nullable=False, comment='业务类型（0获取资产数据，1更新收益数据，2同步资产数据）')
    time_expression = db.Column(db.String(20), comment='时间表达式')
    next_run_time = db.Column(db.DateTime, comment='下次运行时间')
    time_consuming = db.Column(db.Integer, nullable=False, server_default='0', comment='运行耗时（单位：秒）')
    update_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), onupdate=func.now(), comment='更新时间')
    create_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
