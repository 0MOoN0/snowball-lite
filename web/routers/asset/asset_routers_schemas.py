# -*- coding: utf-8 -*-
"""
资产响应模型定义模块

本模块定义了资产相关的Flask-RESTX响应模型，支持多态继承的动态适配。
根据asset_subtype字段自动匹配对应的数据模型结构。

主要功能：
1. 基础资产信息模型
2. 基金资产信息模型（继承基础字段）
3. ETF基金资产信息模型（继承基金字段）
4. LOF基金资产信息模型（继承基金字段）
5. 动态响应模型工厂函数

作者: Assistant
创建时间: 2024
"""

from flask_restx import fields
from marshmallow import Schema, fields as ma_fields, validate, ValidationError, pre_load, EXCLUDE

from web.common.enum.asset_enum import AssetTypeEnum

from web.common.utils.field_mapping_helper import FieldMappingHelper
from web.routers.common.response_schemas import create_typed_response_model


def create_asset_schemas(api):
    """
    创建资产相关的响应模型
    
    Args:
        api: Flask-RESTX API实例
        
    Returns:
        dict: 包含各种资产响应模型的字典
    """
    # 基础资产信息模型
    asset_info_model = api.model('AssetInfo', {
        'id': fields.Integer(description='资产ID'),
        'assetCode': fields.String(description='资产代码'),
        'assetShortCode': fields.String(description='资产简短代码'),
        'assetName': fields.String(description='资产名称'),
        'assetType': fields.Integer(description='资产类型'),
        'assetStatus': fields.Integer(description='资产状态'),
        'currency': fields.Integer(description='货币类型'),
        'market': fields.Integer(description='所在市场')
    })
    
    # 动态资产信息模型（使用Raw字段支持动态结构）
    dynamic_asset_info_model = api.model('DynamicAssetInfo', {
        'id': fields.Integer(description='资产ID'),
        'assetCode': fields.String(description='资产代码'),
        'assetShortCode': fields.String(description='资产简短代码'),
        'assetName': fields.String(description='资产名称'),
        'assetType': fields.Integer(description='资产类型'),
        'assetStatus': fields.Integer(description='资产状态'),
        'currency': fields.Integer(description='货币类型'),
        'market': fields.Integer(description='所在市场'),
        # 使用Raw字段支持动态扩展字段
        'extendedFields': fields.Raw(description='扩展字段，根据资产子类型动态包含不同字段')
    })
    
    # 创建多态响应模型
    polymorphic_asset_response_model = api.model('PolymorphicAssetResponse', {
        'code': fields.Integer(description='响应状态码'),
        'success': fields.Boolean(description='操作是否成功'),
        'message': fields.String(description='响应消息'),
        'data': fields.Raw(
            description='根据资产子类型动态返回对应的数据结构'
        )
    })
    
    # 创建各种响应模型
    asset_response_model = create_typed_response_model(asset_info_model, 'AssetResponse')
    dynamic_asset_response_model = create_typed_response_model(dynamic_asset_info_model, 'DynamicAssetResponse')
    
    asset_update_model = api.model('AssetUpdate', {
        # Asset基础字段
        'assetName': fields.String(required=True, description='资产名称'),
        'assetCode': fields.String(required=False, description='资产代码'),
        'assetShortCode': fields.String(required=False, description='资产简短代码'),
        'assetType': fields.Integer(required=True, description='资产类型'),
        'market': fields.Integer(required=False, description='所在市场'),
        'currency': fields.Integer(required=False, description='货币类型'),
        'assetStatus': fields.Integer(required=True, description='资产状态'),
        
        # AssetFund基金字段
        'fundType': fields.String(required=False, description='基金投资策略类型'),
        'tradingMode': fields.String(required=False, description='基金交易方式'),
        'fundCompany': fields.String(required=False, description='基金管理公司名称'),
        'fundManager': fields.String(required=False, description='基金经理姓名'),
        'establishmentDate': fields.String(required=False, description='基金成立日期'),
        'fundScale': fields.Float(required=False, description='基金规模（万元）'),
        'fundStatus': fields.Integer(required=False, description='基金状态'),
        'investmentObjective': fields.String(required=False, description='投资目标描述'),
        'investmentStrategy': fields.String(required=False, description='投资策略描述'),
        
        # AssetFundETF特有字段
        'trackingIndexCode': fields.String(required=False, description='跟踪指数代码'),
        'trackingIndexName': fields.String(required=False, description='跟踪指数名称'),
        'indexId': fields.Integer(required=False, description='关联的指数ID'),
        'primaryExchange': fields.String(required=False, description='主要交易所'),
        'dividendFrequency': fields.String(required=False, description='分红频率'),
        'trackingError': fields.Float(required=False, description='跟踪误差'),
        
        # AssetFundLOF特有字段
        'listingExchange': fields.String(required=False, description='上市交易所'),
        'subscriptionFeeRate': fields.Float(required=False, description='申购费率'),
        'redemptionFeeRate': fields.Float(required=False, description='赎回费率'),
        'navCalculationTime': fields.String(required=False, description='净值计算时间'),
        'tradingSuspensionInfo': fields.String(required=False, description='停牌信息')
    })

    return {
        'asset_info_model': asset_info_model,
        'dynamic_asset_info_model': dynamic_asset_info_model,
        'asset_response_model': asset_response_model,
        'dynamic_asset_response_model': dynamic_asset_response_model,
        'polymorphic_asset_response_model': polymorphic_asset_response_model,
        'asset_update_model': asset_update_model
    }





class AssetUpdateSchema(Schema):
    """
    资产更新的 Marshmallow Schema
    
    支持驼峰命名到下划线命名的自动转换，并提供完整的字段验证功能。
    适用于所有资产类型的更新操作，包括基础资产、基金、ETF、LOF等。
    """
    
    class Meta:
        """Marshmallow Schema 配置"""
        unknown = EXCLUDE  # 忽略未知字段而不是抛出异常
    
    # Asset基础字段
    asset_name = ma_fields.String(
        required=True, 
        validate=validate.Length(min=1, max=255),
        data_key='assetName',
        error_messages={'required': '资产名称不能为空', 'invalid': '资产名称格式不正确'}
    )
    asset_code = ma_fields.String(
        required=False, 
        allow_none=True,
        validate=validate.Length(max=50),
        data_key='assetCode',
        missing=None
    )
    asset_short_code = ma_fields.String(
        required=False, 
        allow_none=True,
        validate=validate.Length(max=50),
        data_key='assetShortCode',
        missing=None
    )
    asset_type = ma_fields.Integer(
        required=True,
        validate=validate.OneOf([1, 2, 3, 4, 5]),
        data_key='assetType',
        error_messages={'required': '资产类型不能为空', 'invalid': '资产类型必须是1-5之间的整数'}
    )
    market = ma_fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0),
        data_key='market',
        missing=None
    )
    currency = ma_fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0),
        data_key='currency',
        missing=None
    )
    asset_status = ma_fields.Integer(
        required=True,
        validate=validate.OneOf([0, 1]),
        data_key='assetStatus',
        error_messages={'required': '资产状态不能为空', 'invalid': '资产状态必须是0或1'}
    )
    
    # AssetFund基金字段
    fund_type = ma_fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50),
        data_key='fundType',
        missing=None
    )
    trading_mode = ma_fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50),
        data_key='tradingMode',
        missing=None
    )
    fund_company = ma_fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255),
        data_key='fundCompany',
        missing=None
    )
    fund_manager = ma_fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255),
        data_key='fundManager',
        missing=None
    )
    establishment_date = ma_fields.Date(
        required=False,
        allow_none=True,
        data_key='establishmentDate',
        missing=None
    )
    fund_scale = ma_fields.Float(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0),
        data_key='fundScale',
        missing=None
    )
    fund_status = ma_fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.OneOf([0, 1, 2, 3]),
        data_key='fundStatus',
        missing=None
    )
    investment_objective = ma_fields.String(
        required=False,
        allow_none=True,
        data_key='investmentObjective',
        missing=None
    )
    investment_strategy = ma_fields.String(
        required=False,
        allow_none=True,
        data_key='investmentStrategy',
        missing=None
    )
    
    # AssetFundETF特有字段
    tracking_index_code = ma_fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50),
        data_key='trackingIndexCode',
        missing=None
    )
    tracking_index_name = ma_fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=255),
        data_key='trackingIndexName',
        missing=None
    )
    index_id = ma_fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.Range(min=1),
        data_key='indexId',
        missing=None
    )
    primary_exchange = ma_fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100),
        data_key='primaryExchange',
        missing=None
    )
    dividend_frequency = ma_fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50),
        data_key='dividendFrequency',
        missing=None
    )
    tracking_error = ma_fields.Float(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0),
        data_key='trackingError',
        missing=None
    )
    
    # AssetFundLOF特有字段
    listing_exchange = ma_fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=100),
        data_key='listingExchange',
        missing=None
    )
    subscription_fee_rate = ma_fields.Float(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0, max=100),
        data_key='subscriptionFeeRate',
        missing=None
    )
    redemption_fee_rate = ma_fields.Float(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0, max=100),
        data_key='redemptionFeeRate',
        missing=None
    )
    nav_calculation_time = ma_fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=50),
        data_key='navCalculationTime',
        missing=None
    )
    trading_suspension_info = ma_fields.String(
        required=False,
        allow_none=True,
        data_key='tradingSuspensionInfo',
        missing=None
    )
    