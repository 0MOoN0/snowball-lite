from flask_marshmallow import Schema
from marshmallow import post_load, fields, EXCLUDE, post_dump
from sqlalchemy import UniqueConstraint, func, text

from web.common import cons
from web.models import db


class AssetFundDailyData(db.Model):
    __tablename__ = 'tb_asset_fund_daily_data'
    __bind_key__ = "snowball"
    __table_args__ = {
        'comment': '基金资产日线数据'
    }
    id = db.Column(db.BigInteger, primary_key=True, comment='主键', autoincrement=True)
    asset_id = db.Column(db.BigInteger, nullable=False, comment='资产ID')
    f_date = db.Column(db.DateTime, server_default=db.FetchedValue(), comment='时间')
    f_open = db.Column(db.Integer, server_default=db.FetchedValue(), comment='开盘价（单位：毫）')
    f_close = db.Column(db.Integer, server_default=db.FetchedValue(), comment='收盘价（单位：毫）')
    f_high = db.Column(db.Integer, server_default=db.FetchedValue(), comment='当日最高价（单位：毫）')
    f_low = db.Column(db.Integer, server_default=db.FetchedValue(), comment='当日最低价（单位：毫）')
    f_volume = db.Column(db.BigInteger, server_default=db.FetchedValue(), comment='当日成交量')
    f_close_percent = db.Column(db.Integer, server_default=db.FetchedValue(), comment='日收盘价涨幅（百万倍）')
    f_totvalue = db.Column(db.Integer, server_default=db.FetchedValue(),
                           comment='累计净值（单位：毫，当资产没有天天基金代码时，无法获取累计净值）')
    f_netvalue = db.Column(db.Integer, server_default=db.FetchedValue(),
                           comment='当日净值（单位：毫，当资产没有天天基金代码时，无法获取当日净值）')
    f_comment = db.Column(db.Integer, comment='分红或下折（单位：毫）')
    create_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=func.now(), comment='更新时间')
    __table_args__ = (
        UniqueConstraint('f_date', 'asset_id', name='uk_asset_date'),  # 唯一索引
    )


class AssetFundDailyDataSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # 忽略未声明的字段
        dateformat = cons.webcons.DataFormatStr.Y_m_d_H_M_S
        ordered = True

    id = fields.Integer()
    asset_id = fields.Integer()
    f_date = fields.DateTime(allow_none=True, format=cons.webcons.DataFormatStr.Y_m_d_H_M_S)
    f_open = fields.Integer(allow_none=True)
    f_close = fields.Integer(allow_none=True)
    f_high = fields.Integer(allow_none=True)
    f_low = fields.Integer(allow_none=True)
    f_volume = fields.Integer(allow_none=True)
    f_close_percent = fields.Integer(allow_none=True)
    f_totvalue = fields.Integer(allow_none=True)
    f_netvalue = fields.Integer(allow_none=True)
    f_comment = fields.Integer(allow_none=True)
    create_time = fields.DateTime(allow_none=True)
    update_time = fields.DateTime(allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return AssetFundDailyData(**data)

    SKIP_VALUES = set([None])

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        """
        序列化时跳过None或null的字段
        Args:
            data ():
            **kwargs ():

        Returns:

        """
        return {
            key: value for key, value in data.items()
            if value not in self.SKIP_VALUES
        }


class AssetFundDailyDataChartsSchema(AssetFundDailyDataSchema):
    # 显式重新定义需要特殊处理的字段
    date = fields.DateTime(attribute='f_date', format=cons.webcons.DataFormatStr.Y_m_d)  # 单独控制日期格式
    open = fields.Integer(attribute='f_open')
    close = fields.Integer(attribute='f_close')
    high = fields.Integer(attribute='f_high')
    low = fields.Integer(attribute='f_low')
    volume = fields.Integer(attribute='f_volume')
    closePercent = fields.Integer(attribute='f_close_percent')
    totValue = fields.Integer(attribute='f_totvalue')
    netValue = fields.Integer(attribute='f_netvalue')
    comment = fields.Integer(attribute='f_comment')

    # 字段枚举
    DATE = 'date'
    OPEN = 'open'
    CLOSE = 'close'
    HIGH = 'high'
    LOW = 'low'
    VOLUME = 'volume'
    CLOSE_PERCENT = 'closePercent'
    TOT_VALUE = 'totValue'
    NET_VALUE = 'netValue'
    COMMENT = 'comment'
    CREATE_TIME = 'createTime'
    UPDATE_TIME = 'updateTime'

    class Meta(AssetFundDailyDataSchema.Meta):
        fields = (
            'date', 'open', 'close', 'high', 'low', 'volume',
            'closePercent', 'totValue', 'netValue', 'comment',
            'createTime', 'updateTime'  # 非f_前缀字段直接使用原名字段
        )

    # 可移除post_dump转换逻辑

