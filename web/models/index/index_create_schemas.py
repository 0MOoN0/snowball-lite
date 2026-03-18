# -*- coding: UTF-8 -*-
"""
创建用输入 Schema（模型侧）
- IndexCreateBaseSchema: 通用基础字段（不做实例化）
- IndexBaseCreateSchema: 基础指数创建（返回 IndexBase 实例）
- StockIndexCreateSchema: 股票指数创建（返回 StockIndex 实例）

一次校验，一次反序列化，直接返回模型实例。
"""

from marshmallow import Schema, fields as ma_fields, validate, EXCLUDE, post_load
from web.common.enum.business.common_enum import RebalanceFrequencyEnum
from web.models.index.index_base import IndexBase
from web.models.index.index_stock import StockIndex


class IndexCreateBaseSchema(Schema):
    """
    通用基础字段（不做实例化），供具体创建Schema继承
    - 输入为驼峰命名
    """
    class Meta:
        unknown = EXCLUDE

    # 基础字段（必填）
    index_code = ma_fields.String(required=True, validate=validate.Length(min=1, max=50), data_key='indexCode')
    index_name = ma_fields.String(required=True, validate=validate.Length(min=1, max=255), data_key='indexName')
    index_type = ma_fields.Integer(required=True, validate=validate.OneOf([0, 1, 2, 3, 4, 5]), data_key='indexType')
    market = ma_fields.Integer(required=True, validate=validate.OneOf([0, 1, 2]), data_key='market')

    # 基础字段（可选）
    investment_strategy = ma_fields.Integer(allow_none=True, validate=validate.OneOf([0, 1, 2, 3]), data_key='investmentStrategy', missing=None)
    base_date = ma_fields.Date(allow_none=True, data_key='baseDate', missing=None)
    base_point = ma_fields.Integer(allow_none=True, validate=validate.Range(min=1), data_key='basePoint', missing=None)
    currency = ma_fields.Integer(allow_none=True, validate=validate.OneOf([0, 1, 2, 3]), data_key='currency', missing=None)
    weight_method = ma_fields.Integer(allow_none=True, validate=validate.OneOf([0, 1, 2, 3]), data_key='weightMethod', missing=None)
    calculation_method = ma_fields.Integer(allow_none=True, validate=validate.OneOf([0, 1, 2, 3]), data_key='calculationMethod', missing=None)
    index_status = ma_fields.Integer(allow_none=True, validate=validate.OneOf([0, 1]), data_key='indexStatus', missing=1)
    description = ma_fields.String(allow_none=True, validate=validate.Length(max=1000), data_key='description', missing=None)
    publisher = ma_fields.String(allow_none=True, validate=validate.Length(max=255), data_key='publisher', missing=None)
    publish_date = ma_fields.Date(allow_none=True, data_key='publishDate', missing=None)


class IndexBaseCreateSchema(IndexCreateBaseSchema):
    """
    基础指数创建输入Schema
    - 一次校验后反序列化为 IndexBase 实例
    """
    @post_load
    def make_base(self, data, **kwargs):
        return IndexBase(**data)


class StockIndexCreateSchema(IndexCreateBaseSchema):
    """
    股票指数创建输入Schema
    - 继承基础指数字段
    - 增加股票指数特有字段
    - 一次校验后反序列化为 StockIndex 实例
    """
    # 股票指数特有字段（可选）
    constituent_count = ma_fields.Integer(allow_none=True, validate=validate.Range(min=1), data_key='constituentCount', missing=None)
    market_cap = ma_fields.Float(allow_none=True, validate=validate.Range(min=0), data_key='marketCap', missing=None)
    free_float_market_cap = ma_fields.Float(allow_none=True, validate=validate.Range(min=0), data_key='freeFloatMarketCap', missing=None)
    average_pe = ma_fields.Float(allow_none=True, validate=validate.Range(min=0), data_key='averagePe', missing=None)
    average_pb = ma_fields.Float(allow_none=True, validate=validate.Range(min=0), data_key='averagePb', missing=None)
    dividend_yield = ma_fields.Float(allow_none=True, validate=validate.Range(min=0, max=100), data_key='dividendYield', missing=None)
    turnover_rate = ma_fields.Float(allow_none=True, validate=validate.Range(min=0, max=100), data_key='turnoverRate', missing=None)
    volatility = ma_fields.Float(allow_none=True, validate=validate.Range(min=0), data_key='volatility', missing=None)
    beta = ma_fields.Float(allow_none=True, data_key='beta', missing=None)
    rebalance_frequency = ma_fields.String(allow_none=True, validate=validate.OneOf([e.value for e in RebalanceFrequencyEnum]), data_key='rebalanceFrequency', missing=None)
    last_rebalance_date = ma_fields.Date(allow_none=True, data_key='lastRebalanceDate', missing=None)
    next_rebalance_date = ma_fields.Date(allow_none=True, data_key='nextRebalanceDate', missing=None)

    @post_load
    def make_stock(self, data, **kwargs):
        return StockIndex(**data)