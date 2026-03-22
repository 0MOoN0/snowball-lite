from datetime import datetime
from web.models import db
from web.common.enum.business.record.trade_reference_enum import TradeReferenceGroupTypeEnum


class TradeReference(db.Model):
    """
    通用交易关联表
    用于处理交易记录与各种业务对象的关联（如策略、组合、标签等）
    支持一对多关系
    """
    __tablename__ = 'tb_trade_reference'
    __bind_key__ = 'snowball'
    __table_args__ = (
        db.UniqueConstraint('record_id', 'group_type', 'group_id', name='uk_record_group'),
        {'comment': '通用交易关联表'}
    )

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键')
    record_id = db.Column(db.BigInteger, nullable=False, comment='交易记录ID')
    group_type = db.Column(db.Integer, nullable=False, server_default='0', comment='分组类型: 0-其他, 1-网格')
    group_id = db.Column(db.BigInteger, nullable=False, comment='业务对象ID')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    @staticmethod
    def get_group_type_enum() -> TradeReferenceGroupTypeEnum:
        """
        获取分组类型枚举
        Returns:
            TradeReferenceGroupTypeEnum: 分组类型枚举
        """
        return TradeReferenceGroupTypeEnum
