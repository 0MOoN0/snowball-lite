# -*- coding: UTF-8 -*-
"""
@File    ：index_detail_schemas.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27 16:00
@Description: 指数详情接口的Flask-RestX模型定义（仅文档模型）
"""

from flask_restx import fields
from web.common.enum.business.common_enum import RebalanceFrequencyEnum
from marshmallow import Schema as MaSchema, fields as ma_fields, validate, EXCLUDE


def create_index_create_models(api_ns):
    """
    创建指数新增相关的模型定义
    
    Args:
        api_ns: Flask-RestX Namespace对象
        
    Returns:
        dict: 包含模型的字典
    """
    # 指数创建模型（包含所有字段）
    index_create_model = api_ns.model('IndexCreate', {
        'indexCode': fields.String(required=True, description='指数代码，如000001.SH', example='000001.SH'),
        'indexName': fields.String(required=True, description='指数名称', example='上证综指'),
        'indexType': fields.Integer(required=True, description='指数类型（底层资产类型）：0-股票指数，1-债券指数，2-商品指数，3-货币指数，4-混合指数，5-其他', example=0),
        'investmentStrategy': fields.Integer(description='投资策略：0-宽基指数，1-行业指数，2-主题指数，3-策略指数', example=0),
        'market': fields.Integer(required=True, description='所属市场：0-中国，1-香港，2-美国', example=0),
        'baseDate': fields.String(description='基准日期，格式：YYYY-MM-DD', example='1990-12-19'),
        'basePoint': fields.Integer(description='基准点数', example=100),
        'currency': fields.Integer(description='计价货币：0-人民币，1-美元，2-欧元，3-港币', example=0),
        'weightMethod': fields.Integer(description='权重计算方法：0-市值加权，1-等权重，2-基本面加权，3-其他', example=0),
        'calculationMethod': fields.Integer(description='计算方法：0-价格加权，1-总收益，2-净收益，3-其他', example=1),
        'indexStatus': fields.Integer(description='状态：0-停用，1-启用', example=1),
        'description': fields.String(description='指数描述', example='反映上海证券交易所挂牌股票总体走势的统计指标'),
        'publisher': fields.String(description='发布机构', example='上海证券交易所'),
        'publishDate': fields.String(description='发布日期，格式：YYYY-MM-DD', example='1991-07-15'),
        # discriminator 字段不对外暴露，后端内部设置
        'sampleSize': fields.Integer(description='样本数量', example=50),
        'sampleSelectionCriteria': fields.String(description='样本选择标准', example='按市值排序选取前50只股票'),
        'adjustmentFrequency': fields.Integer(description='调整频率：0-不定期，1-月度，2-季度，3-半年度，4-年度', example=2),
        'lastAdjustmentDate': fields.String(description='最后调整日期，格式：YYYY-MM-DD', example='2023-12-15'),
        'nextAdjustmentDate': fields.String(description='下次调整日期，格式：YYYY-MM-DD', example='2024-03-15'),
        'sectorDistribution': fields.String(description='行业分布说明', example='金融30%，科技25%，消费20%，其他25%'),
        'marketCapRange': fields.String(description='市值范围', example='大盘股为主，市值100亿以上'),
        'liquidityRequirement': fields.String(description='流动性要求', example='日均成交额1000万以上'),
        'freeFloatRequirement': fields.Float(description='自由流通比例要求', example=0.1),
        'dividendTreatment': fields.Integer(description='分红处理方式：0-价格指数，1-全收益指数，2-净收益指数', example=1),
        'rebalanceFrequency': fields.String(description='调仓频率：quarterly-季度，semi_annual-半年，annual-年度', enum=[e.value for e in RebalanceFrequencyEnum], example='quarterly')
    })
    
    return {
        'index_create_model': index_create_model
    }


def create_index_update_models(api_ns):
    """
    创建指数更新相关的模型定义（仅用于OpenAPI文档展示，不做校验）
    """
    index_update_model = api_ns.model('IndexUpdate', {
        # 基础字段
        'indexCode': fields.String(required=False, description='指数代码，如000001.SH'),
        'indexName': fields.String(required=True, description='指数名称'),
        'indexType': fields.Integer(required=True, description='指数类型（底层资产类型）：0-股票指数，1-债券指数，2-商品指数，3-货币指数，4-混合指数，5-其他'),
        'investmentStrategy': fields.Integer(required=False, description='投资策略：0-宽基指数，1-行业指数，2-主题指数，3-策略指数'),
        'market': fields.Integer(required=False, description='所属市场：0-中国，1-香港，2-美国'),
        'baseDate': fields.String(required=False, description='基准日期，格式：YYYY-MM-DD'),
        'basePoint': fields.Integer(required=False, description='基准点数'),
        'currency': fields.Integer(required=False, description='计价货币：0-人民币，1-美元，2-欧元，3-港币'),
        'weightMethod': fields.Integer(required=False, description='权重计算方法：0-市值加权，1-等权重，2-基本面加权，3-其他'),
        'calculationMethod': fields.Integer(required=False, description='计算方法：0-价格加权，1-总收益，2-净收益，3-其他'),
        'indexStatus': fields.Integer(required=True, description='状态：0-停用，1-启用'),
        'description': fields.String(required=False, description='指数描述'),
        'publisher': fields.String(required=False, description='发布机构'),
        'publishDate': fields.String(required=False, description='发布日期，格式：YYYY-MM-DD'),
        # 股票指数特有字段
        'constituentCount': fields.Integer(required=False, description='成分股数量'),
        'marketCap': fields.Float(required=False, description='总市值（万元）'),
        'freeFloatMarketCap': fields.Float(required=False, description='自由流通市值（万元）'),
        'averagePe': fields.Float(required=False, description='平均市盈率'),
        'averagePb': fields.Float(required=False, description='平均市净率'),
        'dividendYield': fields.Float(required=False, description='股息率（%）'),
        'turnoverRate': fields.Float(required=False, description='换手率（%）'),
        'volatility': fields.Float(required=False, description='波动率（%）'),
        'beta': fields.Float(required=False, description='贝塔系数'),
        'rebalanceFrequency': fields.String(required=False, description='调仓频率：quarterly-季度，semi_annual-半年，annual-年度', enum=[e.value for e in RebalanceFrequencyEnum]),
        'lastRebalanceDate': fields.String(required=False, description='最后调仓日期，格式：YYYY-MM-DD'),
        'nextRebalanceDate': fields.String(required=False, description='下次调仓日期，格式：YYYY-MM-DD'),
    })
    return {
        'index_update_model': index_update_model
    }


class IndexUpdateSchema(MaSchema):
    """指数更新的 Marshmallow Schema（路由侧），负责校验并作驼峰→下划线转换"""
    class Meta:
        unknown = EXCLUDE

    # 基础字段（移除 missing=None，避免未提供字段被写入 None 覆盖原值）
    index_code = ma_fields.String(required=False, allow_none=True, validate=validate.Length(max=20), data_key='indexCode')
    index_name = ma_fields.String(required=True, validate=validate.Length(min=1, max=255), data_key='indexName')
    index_type = ma_fields.Integer(required=True, validate=validate.OneOf([0, 1, 2, 3, 4, 5]), data_key='indexType')
    investment_strategy = ma_fields.Integer(required=False, allow_none=True, data_key='investmentStrategy')
    market = ma_fields.Integer(required=False, allow_none=True, data_key='market')
    base_date = ma_fields.Date(required=False, allow_none=True, data_key='baseDate')
    base_point = ma_fields.Integer(required=False, allow_none=True, data_key='basePoint')
    currency = ma_fields.Integer(required=False, allow_none=True, data_key='currency')
    weight_method = ma_fields.Integer(required=False, allow_none=True, data_key='weightMethod')
    calculation_method = ma_fields.Integer(required=False, allow_none=True, data_key='calculationMethod')
    index_status = ma_fields.Integer(required=True, validate=validate.OneOf([0, 1]), data_key='indexStatus')
    description = ma_fields.String(required=False, allow_none=True, data_key='description')
    publisher = ma_fields.String(required=False, allow_none=True, validate=validate.Length(max=100), data_key='publisher')
    publish_date = ma_fields.Date(required=False, allow_none=True, data_key='publishDate')

    # 股票指数特有字段（同样移除 missing）
    constituent_count = ma_fields.Integer(required=False, allow_none=True, data_key='constituentCount')
    market_cap = ma_fields.Float(required=False, allow_none=True, data_key='marketCap')
    free_float_market_cap = ma_fields.Float(required=False, allow_none=True, data_key='freeFloatMarketCap')
    average_pe = ma_fields.Float(required=False, allow_none=True, data_key='averagePe')
    average_pb = ma_fields.Float(required=False, allow_none=True, data_key='averagePb')
    dividend_yield = ma_fields.Float(required=False, allow_none=True, data_key='dividendYield')
    turnover_rate = ma_fields.Float(required=False, allow_none=True, data_key='turnoverRate')
    volatility = ma_fields.Float(required=False, allow_none=True, data_key='volatility')
    beta = ma_fields.Float(required=False, allow_none=True, data_key='beta')
    rebalance_frequency = ma_fields.String(required=False, allow_none=True, validate=validate.OneOf([e.value for e in RebalanceFrequencyEnum]), data_key='rebalanceFrequency')
    last_rebalance_date = ma_fields.Date(required=False, allow_none=True, data_key='lastRebalanceDate')
    next_rebalance_date = ma_fields.Date(required=False, allow_none=True, data_key='nextRebalanceDate')