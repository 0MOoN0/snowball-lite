# coding: utf-8
from flask_marshmallow import Schema
from marshmallow import fields, post_load, post_dump
from sqlalchemy import ForeignKey

from web.models import db
from .index_base import IndexBase, IndexBaseSchema, IndexBaseVOSchema, IndexBaseJSONSchema
from web.common.enum.business.common_enum import RebalanceFrequencyEnum


class StockIndex(IndexBase):
    """
    股票指数模型
    
    继承自IndexBase，专门用于股票指数的特定字段和方法
    使用joined table inheritance模式
    """
    __tablename__ = 'tb_index_stock'
    __bind_key__ = "snowball"
    __table_args__ = {
        'comment': '股票指数表'
    }
    
    # 继承基类的主键
    id = db.Column(db.BigInteger, ForeignKey('tb_index_base.id'), primary_key=True, comment='主键ID，外键关联index_base表')
    
    # 股票指数特有字段
    constituent_count = db.Column(db.Integer, comment='成分股数量')
    market_cap = db.Column(db.Float(15, 2), comment='总市值（万元）')
    free_float_market_cap = db.Column(db.Float(15, 2), comment='自由流通市值（万元）')
    average_pe = db.Column(db.Float(10, 2), comment='平均市盈率')
    average_pb = db.Column(db.Float(10, 2), comment='平均市净率')
    dividend_yield = db.Column(db.Float(6, 4), comment='股息率（%）')
    turnover_rate = db.Column(db.Float(6, 4), comment='换手率（%）')
    volatility = db.Column(db.Float(6, 4), comment='波动率（%）')
    beta = db.Column(db.Float(6, 4), comment='贝塔系数')
    # sector_distribution = db.Column(db.JSON, comment='行业分布（JSON格式）')
    # top_holdings = db.Column(db.JSON, comment='前十大成分股（JSON格式）')
    rebalance_frequency = db.Column(db.String(20), comment='调仓频率：quarterly-季度，semi_annual-半年，annual-年度')
    last_rebalance_date = db.Column(db.Date, comment='最后调仓日期')
    next_rebalance_date = db.Column(db.Date, comment='下次调仓日期')
    
    # 多态配置
    __mapper_args__ = {
        'polymorphic_identity': 'index_stock'
    }

    @staticmethod
    def get_rebalance_frequency_enum() -> RebalanceFrequencyEnum:
        """
        获取调仓频率枚举类
        Returns:
            RebalanceFrequencyEnum: 调仓频率枚举
        """
        return RebalanceFrequencyEnum
    
    @staticmethod
    def get_create_schema():
        """
        获取股票指数创建用Schema实例
        Returns:
            Schema: StockIndexCreateSchema 实例
        """
        from web.models.index.index_create_schemas import StockIndexCreateSchema
        return StockIndexCreateSchema()
    
    def to_dict(self):
        """
        将股票指数模型转换为字典
        
        Returns:
            dict: 股票指数字典表示
        """
        base_dict = super().to_dict()
        stock_dict = {
            'constituent_count': self.constituent_count,
            'market_cap': self.market_cap,
            'free_float_market_cap': self.free_float_market_cap,
            'average_pe': self.average_pe,
            'average_pb': self.average_pb,
            'dividend_yield': self.dividend_yield,
            'turnover_rate': self.turnover_rate,
            'volatility': self.volatility,
            'beta': self.beta,
            # 'sector_distribution': self.sector_distribution,
            # 'top_holdings': self.top_holdings,
            'rebalance_frequency': self.rebalance_frequency,
            'last_rebalance_date': self.last_rebalance_date.isoformat() if self.last_rebalance_date else None,
            'next_rebalance_date': self.next_rebalance_date.isoformat() if self.next_rebalance_date else None
        }
        base_dict.update(stock_dict)
        return base_dict
    
    def __repr__(self):
        return f'<StockIndex {self.index_code}: {self.index_name}>'


class StockIndexSchema(IndexBaseSchema):
    """
    股票指数的序列化Schema，继承自IndexBaseSchema
    """
    # 股票指数特有字段
    constituent_count = fields.Integer(data_key='constituentCount', allow_none=True)
    market_cap = fields.Float(data_key='marketCap', allow_none=True)
    free_float_market_cap = fields.Float(data_key='freeFloatMarketCap', allow_none=True)
    average_pe = fields.Float(data_key='averagePe', allow_none=True)
    average_pb = fields.Float(data_key='averagePb', allow_none=True)
    dividend_yield = fields.Float(data_key='dividendYield', allow_none=True)
    turnover_rate = fields.Float(data_key='turnoverRate', allow_none=True)
    volatility = fields.Float(allow_none=True)
    beta = fields.Float(allow_none=True)
    # sector_distribution = fields.Raw(allow_none=True)
    # top_holdings = fields.Raw(allow_none=True)
    rebalance_frequency = fields.String(data_key='rebalanceFrequency', allow_none=True)
    last_rebalance_date = fields.Date(data_key='lastRebalanceDate', allow_none=True)
    next_rebalance_date = fields.Date(data_key='nextRebalanceDate', allow_none=True)
    
    @post_load
    def post_load(self, data, **kwargs):
        return StockIndex(**data)


class StockIndexVOSchema(IndexBaseVOSchema):
    """
    股票指数的VO序列化Schema（用于输出），继承自IndexBaseVOSchema
    """
    # 股票指数特有字段
    constituent_count = fields.Integer(allow_none=True, data_key="constituentCount")
    market_cap = fields.Float(allow_none=True, data_key="marketCap")
    free_float_market_cap = fields.Float(allow_none=True, data_key="freeFloatMarketCap")
    average_pe = fields.Float(allow_none=True, data_key="averagePe")
    average_pb = fields.Float(allow_none=True, data_key="averagePb")
    dividend_yield = fields.Float(allow_none=True, data_key="dividendYield")
    turnover_rate = fields.Float(allow_none=True, data_key="turnoverRate")
    volatility = fields.Float(allow_none=True, data_key="volatility")
    beta = fields.Float(allow_none=True, data_key="beta")
    rebalance_frequency = fields.String(allow_none=True, data_key="rebalanceFrequency")
    last_rebalance_date = fields.Date(allow_none=True, data_key="lastRebalanceDate")
    next_rebalance_date = fields.Date(allow_none=True, data_key="nextRebalanceDate")
    
    @post_load
    def post_load(self, data, **kwargs):
        return StockIndex(**data)


class StockIndexJSONSchema(IndexBaseJSONSchema):
    """
    股票指数的JSON序列化Schema（用于输出），继承自IndexBaseJSONSchema
    """
    # 股票指数特有字段
    constituent_count = fields.Integer(allow_none=True)
    market_cap = fields.Float(allow_none=True)
    free_float_market_cap = fields.Float(allow_none=True)
    average_pe = fields.Float(allow_none=True)
    average_pb = fields.Float(allow_none=True)
    dividend_yield = fields.Float(allow_none=True)
    turnover_rate = fields.Float(allow_none=True)
    volatility = fields.Float(allow_none=True)
    beta = fields.Float(allow_none=True)
    # sector_distribution = fields.Raw(allow_none=True)
    # top_holdings = fields.Raw(allow_none=True)
    rebalance_frequency = fields.String(allow_none=True)
    last_rebalance_date = fields.Date(allow_none=True)
    next_rebalance_date = fields.Date(allow_none=True)
    
    @post_load
    def post_load(self, data, **kwargs):
        return StockIndex(**data)