from sqlalchemy import func, text

from web.models import db


class TaskLog(db.Model):
    __tablename__ = 'tb_task_log'
    __bind_key__ = 'snowball'

    id = db.Column(db.BigInteger, primary_key=True, comment='主键ID', autoincrement=True)
    asset_id = db.Column(db.BigInteger, nullable=False, comment='资产ID')
    task_id = db.Column(db.BigInteger, nullable=False, comment='任务ID')
    business_type = db.Column(db.Integer, nullable=False, comment='业务类型-0初始化资产数据，1更新收益数据，2同步资产数据')
    execute_time = db.Column(db.DateTime, nullable=False, server_default=None, comment='执行时间')
    execute_result = db.Column(db.Boolean, nullable=False, server_default=None,
                               comment='执行结果0-失败，1-成功')
    time_consuming = db.Column(db.Integer, nullable=False, server_default=None, comment='运行耗时（单位：毫秒）')
    create_time = db.Column(db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    remark = db.Column(db.String(500), nullable=False, comment='备注')
