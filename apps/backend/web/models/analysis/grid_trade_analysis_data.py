from flask_marshmallow import Schema
from marshmallow import fields, post_load, post_dump
from sqlalchemy import func, text, ForeignKey

from web.common.cons import webcons
from web.common.enum.AnalysisEnum import GridTransactionAnalysisBusinessTypeEnum
from web.common.utils.WebUtils import web_utils
from web.models import db
from web.models.analysis.trade_analysis_data import TradeAnalysisData, TransactionAnalysisDataDomainSchema, TransactionAnalysisDataVOSchema, TransactionAnalysisDataAPISchema


class GridTradeAnalysisData(TradeAnalysisData):
    """
    网格交易业务数据分析表，继承TransactionAnalysisData
    """
    __tablename__ = 'tb_grid_trade_analysis_data'
    __bind_key__ = 'snowball'
    __table_args__ = (
        {'comment': '网格交易分析表'}
    )
    __mapper_args__ = {
        'polymorphic_identity': 'grid_trade_analysis'
    }

    id = db.Column(db.BigInteger, db.ForeignKey('tb_trade_analysis_data.id'), primary_key=True, comment='主键和外键，关联到trade_analysis_data.id，形成联合表继承关系')
    business_type = db.Column(db.Integer, nullable=False, comment='业务类型：0-网格类型交易分析，1-网格交易分析，2-网格策略交易分析')
    grid_type_id = db.Column(db.BigInteger, nullable=True, comment='对应的网格交易类型ID')
    grid_id = db.Column(db.BigInteger, nullable=True, comment='对应的网格ID')
    sell_times = db.Column(db.Integer, nullable=False, server_default='0', comment='出售次数')
    estimate_maximum_occupancy = db.Column(db.Integer, nullable=False, server_default='0',
                                           comment='预估剩余最大占用金额（单位：分）')
    holding_times = db.Column(db.Integer, nullable=False, server_default='0', comment='待出网次数')
    up_sold_percent = db.Column(db.Integer, nullable=True,server_default=None,
                                comment='距离卖出需要上涨的数量（万倍）')
    down_bought_percent = db.Column(db.Integer, nullable=True,server_default=None,
                                    comment='距离买入需要下跌的数量（万倍）')
    dividend_yield = db.Column(db.Integer, nullable=True, comment='股息率（万倍）')

    @staticmethod
    def get_business_type_enum():
        return GridTransactionAnalysisBusinessTypeEnum


class GridTransactionAnalysisDataDomainSchema(TransactionAnalysisDataDomainSchema):
    # 继承TransactionAnalysisDataDomainSchema，只定义GridTransactionAnalysisData特有的字段
    business_type = fields.Integer()
    grid_type_id = fields.Integer(allow_none=True)
    grid_id = fields.Integer(allow_none=True)
    sell_times = fields.Integer()
    estimate_maximum_occupancy = fields.Integer()
    holding_times = fields.Integer()
    up_sold_percent = fields.Integer()
    down_bought_percent = fields.Integer()
    dividend_yield = fields.Integer(allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return GridTradeAnalysisData(**data)


class GridTransactionAnalysisDataVOSchema(TransactionAnalysisDataVOSchema):
    """
    网格分析数据展示（格式化版本，已废弃）
    注意：此Schema会对数据进行格式化处理，不建议在API接口中使用
    请使用GridTransactionAnalysisDataAPISchema获取原始数据
    """
    # 继承TransactionAnalysisDataVOSchema，只定义GridTransactionAnalysisData特有的字段
    business_type = fields.Integer(data_key='businessType')
    grid_type_id = fields.Integer(data_key='gridTypeId')
    grid_id = fields.Integer(data_key='gridId')
    sell_times = fields.Integer(data_key='sellTimes')
    estimate_maximum_occupancy = fields.Integer(data_key='estimateMaximumOccupancy')
    holding_times = fields.Integer(data_key='holdingTimes')
    up_sold_percent = fields.Integer(data_key='upSoldPercent')
    down_bought_percent = fields.Integer(data_key='downBoughtPercent')
    dividend_yield = fields.Integer(data_key='dividendYield', allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return GridTradeAnalysisData(**data)

    @post_dump
    def post_dump(self, data, **kwargs):
        # 先调用父类的post_dump方法处理继承的字段
        data = super().post_dump(data, **kwargs)
        
        # 处理GridTransactionAnalysisData特有字段
        if 'estimateMaximumOccupancy' in data and data['estimateMaximumOccupancy'] is not None:
            data['estimateMaximumOccupancy'] = web_utils.to_currency(data['estimateMaximumOccupancy'] / 1000)
        if 'upSoldPercent' in data and data['upSoldPercent'] is not None:
            data['upSoldPercent'] = str(data['upSoldPercent'] / 100) + '%'
        if 'downBoughtPercent' in data and data['downBoughtPercent'] is not None:
            data['downBoughtPercent'] = str(data['downBoughtPercent'] / 100) + '%'
        if 'dividendYield' in data and data['dividendYield'] is not None:
            data['dividendYield'] = str(data['dividendYield'] / 10000) + '%'
        return data


class GridTransactionAnalysisDataAPISchema(TransactionAnalysisDataAPISchema):
    """
    网格分析数据API接口Schema（原始数据版本）
    继承TransactionAnalysisDataAPISchema，只定义GridTransactionAnalysisData特有的字段
    返回原始数值数据，不进行格式化处理，由前端负责数据格式化
    """
    # GridTransactionAnalysisData特有字段
    business_type = fields.Integer(data_key='businessType', allow_none=True)
    grid_type_id = fields.Integer(data_key='gridTypeId', allow_none=True)
    grid_id = fields.Integer(data_key='gridId', allow_none=True)
    sell_times = fields.Integer(data_key='sellTimes', allow_none=True)
    estimate_maximum_occupancy = fields.Integer(data_key='estimateMaximumOccupancy', allow_none=True)
    holding_times = fields.Integer(data_key='holdingTimes', allow_none=True)
    up_sold_percent = fields.Integer(data_key='upSoldPercent', allow_none=True)
    down_bought_percent = fields.Integer(data_key='downBoughtPercent', allow_none=True)
    dividend_yield = fields.Integer(data_key='dividendYield', allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return GridTradeAnalysisData(**data)
