from __future__ import annotations

from dataclasses import dataclass
from flask_marshmallow import Schema
from marshmallow import post_load, fields, post_dump
from sqlalchemy import func, text, DECIMAL

from web.common.enum.fund_enum import FundTypeEnum, FundStatusEnum, FundTradingModeEnum
from web.models.asset.asset import Asset
from web.models.index.index_base import IndexBase
from web.models import db


class AssetFund(Asset):
    """
    基金资产模型 - 中间层
    继承自Asset，作为所有基金类型的基类
    使用联合表继承模式
    """
    __tablename__ = "tb_asset_fund"
    __bind_key__ = "snowball"
    __table_args__ = {"comment": "基金资产模型 - 中间层"}
    __mapper_args__ = {
        'polymorphic_identity': 'asset_fund'
    }
    
    id = db.Column(
        db.BigInteger, 
        db.ForeignKey('tb_asset.id'), 
        primary_key=True, 
        comment="主键和外键，关联到asset.id，形成联合表继承关系"
    )
    
    fund_type = db.Column(
        db.String(32), 
        nullable=False, 
        comment="基金投资策略类型，如INDEX_FUND、STOCK_FUND、BOND_FUND等"
    )
    
    trading_mode = db.Column(
        db.String(32), 
        nullable=False, 
        comment="基金交易方式，如ETF、LOF、OPEN_END、CLOSED_END等"
    )
    
    fund_company = db.Column(
        db.String(128), 
        nullable=True, 
        comment="基金管理公司名称"
    )
    
    fund_manager = db.Column(
        db.String(128), 
        nullable=True, 
        comment="基金经理姓名"
    )
    
    establishment_date = db.Column(
        db.Date, 
        nullable=True, 
        comment="基金成立日期"
    )
    
    fund_scale = db.Column(
        DECIMAL(20, 4), 
        nullable=True, 
        comment="基金规模，单位：万元"
    )
    
    fund_status = db.Column(
        db.Integer, 
        nullable=False, 
        server_default="0", 
        comment="基金状态：0-正常运作，1-暂停申购/赎回，2-已清盘，3-已合并"
    )
    
    investment_objective = db.Column(
        db.Text, 
        nullable=True, 
        comment="投资目标描述"
    )
    
    investment_strategy = db.Column(
        db.Text, 
        nullable=True, 
        comment="投资策略描述"
    )
    
    @staticmethod
    def get_fund_type_enum() -> FundTypeEnum:
        """
        获取基金类型枚举
        Returns:
            FundTypeEnum: 基金类型枚举
        """
        return FundTypeEnum
    
    @staticmethod
    def get_fund_status_enum() -> FundStatusEnum:
        """
        获取基金状态枚举
        Returns:
            FundStatusEnum: 基金状态枚举
        """
        return FundStatusEnum
    
    @staticmethod
    def get_trading_mode_enum() -> FundTradingModeEnum:
        """
        获取基金交易方式枚举
        Returns:
            FundTradingModeEnum: 基金交易方式枚举
        """
        return FundTradingModeEnum


class AssetFundETF(AssetFund):
    """
    ETF（交易型开放式指数基金）模型
    继承自AssetFund，专门用于ETF产品
    使用联合表继承模式
    """
    __tablename__ = "tb_asset_fund_etf"
    __bind_key__ = "snowball"
    __table_args__ = {"comment": "ETF基金资产模型"}
    __mapper_args__ = {
        'polymorphic_identity': 'asset_fund_etf'
    }
    
    id = db.Column(
        db.BigInteger, 
        db.ForeignKey('tb_asset_fund.id'), 
        primary_key=True, 
        comment="主键和外键，关联到asset_fund.id，形成联合表继承关系"
    )
    
    tracking_index_code = db.Column(
        db.String(32), 
        nullable=True, 
        comment="跟踪指数代码，如000300（沪深300）"
    )
    
    tracking_index_name = db.Column(
        db.String(128), 
        nullable=True, 
        comment="跟踪指数名称，如沪深300指数"
    )
    
    index_id = db.Column(
        db.BigInteger,
        db.ForeignKey('tb_index_base.id'),
        nullable=True,
        comment="关联的指数ID，外键关联到IndexBase模型"
    )
    
    primary_exchange = db.Column(
        db.String(16), 
        nullable=True, 
        comment="主要交易所：SH（上海证券交易所）、SZ（深圳证券交易所）"
    )
    
    dividend_frequency = db.Column(
        db.String(32), 
        nullable=True, 
        comment="分红频率：ANNUAL（年度）、SEMI_ANNUAL（半年度）、QUARTERLY（季度）、MONTHLY（月度）"
    )
    
    tracking_error = db.Column(
        DECIMAL(8, 6), 
        nullable=True, 
        comment="跟踪误差，年化标准差"
    )
    
    # 关系定义
    index = db.relationship(
        "IndexBase",
        foreign_keys=[index_id],
        lazy="select",
        uselist=False
    )
    


class AssetFundLOF(AssetFund):
    """
    LOF（上市开放式基金）模型
    继承自AssetFund，专门用于LOF产品
    使用联合表继承模式
    """
    __tablename__ = "tb_asset_fund_lof"
    __bind_key__ = "snowball"
    __table_args__ = {"comment": "LOF基金资产模型"}
    __mapper_args__ = {
        'polymorphic_identity': 'asset_fund_lof'
    }
    
    id = db.Column(
        db.BigInteger, 
        db.ForeignKey('tb_asset_fund.id'), 
        primary_key=True, 
        comment="主键和外键，关联到asset_fund.id，形成联合表继承关系"
    )
    
    listing_exchange = db.Column(
        db.String(16), 
        nullable=True, 
        comment="上市交易所：SH（上海证券交易所）、SZ（深圳证券交易所）"
    )
    
    subscription_fee_rate = db.Column(
        DECIMAL(8, 6), 
        nullable=True, 
        comment="申购费率"
    )
    
    redemption_fee_rate = db.Column(
        DECIMAL(8, 6), 
        nullable=True, 
        comment="赎回费率"
    )
    
    nav_calculation_time = db.Column(
        db.Time, 
        nullable=True, 
        comment="净值计算时间"
    )
    
    trading_suspension_info = db.Column(
        db.Text, 
        nullable=True, 
        comment="停牌信息"
    )
    
    index_id = db.Column(
        db.BigInteger,
        db.ForeignKey('tb_index_base.id'),
        nullable=True,
        comment="关联的指数ID，外键关联到IndexBase模型，仅指数型LOF使用"
    )
    
    # 关系定义
    index = db.relationship(
        "IndexBase",
        foreign_keys=[index_id],
        lazy="select",
        uselist=False
    )


# Schema定义
class AssetFundSchema(Schema):
    """基金资产数据Schema，用于序列化和反序列化"""
    SKIP_VALUES = set([None])
    
    # AssetFund特有字段
    id = fields.Integer(allow_none=True)
    fund_type = fields.String(allow_none=False)
    trading_mode = fields.String(allow_none=False)
    fund_company = fields.String(allow_none=True)
    fund_manager = fields.String(allow_none=True)
    establishment_date = fields.Date(allow_none=True)
    fund_scale = fields.Decimal(allow_none=True)
    fund_status = fields.Integer(allow_none=False)
    investment_objective = fields.String(allow_none=True)
    investment_strategy = fields.String(allow_none=True)
    
    # 继承Asset的所有字段
    currency = fields.Integer(allow_none=True)
    asset_type = fields.Integer(allow_none=True)
    asset_name = fields.String(allow_none=True)
    market = fields.Integer(allow_none=True)
    asset_code = fields.String(allow_none=True)
    asset_short_code = fields.String(allow_none=True)
    asset_status = fields.Integer(allow_none=True)
    asset_subtype = fields.String(allow_none=True)
    
    @post_load
    def post_load(self, data, **kwargs):
        return AssetFund(**data)
    
    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }


class AssetFundVOSchema(Schema):
    """基金资产数据VO对象，用于从数据库转换数据到外部接口使用"""
    SKIP_VALUES = set([None])
    
    # AssetFund特有字段
    id = fields.Integer(allow_none=True, data_key="id")
    fund_type = fields.String(allow_none=False, data_key="fundType")
    trading_mode = fields.String(allow_none=False, data_key="tradingMode")
    fund_company = fields.String(allow_none=True, data_key="fundCompany")
    fund_manager = fields.String(allow_none=True, data_key="fundManager")
    establishment_date = fields.Date(allow_none=True, data_key="establishmentDate")
    fund_scale = fields.Decimal(allow_none=True, data_key="fundScale")
    fund_status = fields.Integer(allow_none=False, data_key="fundStatus")
    investment_objective = fields.String(allow_none=True, data_key="investmentObjective")
    investment_strategy = fields.String(allow_none=True, data_key="investmentStrategy")
    
    # 继承Asset的所有字段
    currency = fields.Integer(allow_none=True, data_key="currency")
    asset_type = fields.Integer(allow_none=True, data_key="assetType")
    asset_name = fields.String(allow_none=True, data_key="assetName")
    market = fields.Integer(allow_none=True, data_key="market")
    asset_code = fields.String(allow_none=True, data_key="assetCode")
    asset_short_code = fields.String(allow_none=True, data_key="assetShortCode")
    asset_status = fields.Integer(allow_none=True, data_key="assetStatus")
    
    @post_load
    def post_load(self, data, **kwargs):
        return AssetFund(**data)
    
    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }


class AssetFundETFSchema(Schema):
    """ETF资产数据Schema，用于序列化和反序列化"""
    SKIP_VALUES = set([None])
    
    # AssetFundETF特有字段
    id = fields.Integer(allow_none=True)
    tracking_index_code = fields.String(allow_none=True)
    tracking_index_name = fields.String(allow_none=True)
    index_id = fields.Integer(allow_none=True)
    primary_exchange = fields.String(allow_none=True)
    dividend_frequency = fields.String(allow_none=True)
    tracking_error = fields.Decimal(allow_none=True)
    
    # 继承AssetFund的所有字段
    fund_type = fields.String(allow_none=False)
    trading_mode = fields.String(allow_none=False)
    fund_company = fields.String(allow_none=True)
    fund_manager = fields.String(allow_none=True)
    establishment_date = fields.Date(allow_none=True)
    fund_scale = fields.Decimal(allow_none=True)
    fund_status = fields.Integer(allow_none=False)
    investment_objective = fields.String(allow_none=True)
    investment_strategy = fields.String(allow_none=True)
    
    # 继承Asset的所有字段
    currency = fields.Integer(allow_none=True)
    asset_type = fields.Integer(allow_none=True)
    asset_name = fields.String(allow_none=True)
    market = fields.Integer(allow_none=True)
    asset_code = fields.String(allow_none=True)
    asset_short_code = fields.String(allow_none=True)
    asset_status = fields.Integer(allow_none=True)
    asset_subtype = fields.String(allow_none=True)
    
    @post_load
    def post_load(self, data, **kwargs):
        return AssetFundETF(**data)
    
    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }


class AssetFundETFVOSchema(Schema):
    """ETF资产数据VO对象，用于从数据库转换数据到外部接口使用"""
    SKIP_VALUES = set([None])
    
    # AssetFundETF特有字段
    id = fields.Integer(allow_none=True, data_key="id")
    tracking_index_code = fields.String(allow_none=True, data_key="trackingIndexCode")
    tracking_index_name = fields.String(allow_none=True, data_key="trackingIndexName")
    index_id = fields.Integer(allow_none=True, data_key="indexId")
    primary_exchange = fields.String(allow_none=True, data_key="primaryExchange")
    dividend_frequency = fields.String(allow_none=True, data_key="dividendFrequency")
    tracking_error = fields.Decimal(allow_none=True, data_key="trackingError")
    
    # 继承AssetFund的所有字段
    fund_type = fields.String(allow_none=False, data_key="fundType")
    trading_mode = fields.String(allow_none=False, data_key="tradingMode")
    fund_company = fields.String(allow_none=True, data_key="fundCompany")
    fund_manager = fields.String(allow_none=True, data_key="fundManager")
    establishment_date = fields.Date(allow_none=True, data_key="establishmentDate")
    fund_scale = fields.Decimal(allow_none=True, data_key="fundScale")
    fund_status = fields.Integer(allow_none=False, data_key="fundStatus")
    investment_objective = fields.String(allow_none=True, data_key="investmentObjective")
    investment_strategy = fields.String(allow_none=True, data_key="investmentStrategy")
    
    # 继承Asset的所有字段
    currency = fields.Integer(allow_none=True, data_key="currency")
    asset_type = fields.Integer(allow_none=True, data_key="assetType")
    asset_name = fields.String(allow_none=True, data_key="assetName")
    market = fields.Integer(allow_none=True, data_key="market")
    asset_code = fields.String(allow_none=True, data_key="assetCode")
    asset_short_code = fields.String(allow_none=True, data_key="assetShortCode")
    asset_status = fields.Integer(allow_none=True, data_key="assetStatus")
    
    @post_load
    def post_load(self, data, **kwargs):
        return AssetFundETF(**data)
    
    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }


class AssetFundLOFSchema(Schema):
    """LOF资产数据Schema，用于序列化和反序列化"""
    SKIP_VALUES = set([None])
    
    # AssetFundLOF特有字段
    id = fields.Integer(allow_none=True)
    listing_exchange = fields.String(allow_none=True)
    subscription_fee_rate = fields.Decimal(allow_none=True)
    redemption_fee_rate = fields.Decimal(allow_none=True)
    nav_calculation_time = fields.Time(allow_none=True)
    trading_suspension_info = fields.String(allow_none=True)
    index_id = fields.Integer(allow_none=True)
    
    # 继承AssetFund的所有字段
    fund_type = fields.String(allow_none=False)
    trading_mode = fields.String(allow_none=False)
    fund_company = fields.String(allow_none=True)
    fund_manager = fields.String(allow_none=True)
    establishment_date = fields.Date(allow_none=True)
    fund_scale = fields.Decimal(allow_none=True)
    fund_status = fields.Integer(allow_none=False)
    investment_objective = fields.String(allow_none=True)
    investment_strategy = fields.String(allow_none=True)
    
    # 继承Asset的所有字段
    currency = fields.Integer(allow_none=True)
    asset_type = fields.Integer(allow_none=True)
    asset_name = fields.String(allow_none=True)
    market = fields.Integer(allow_none=True)
    asset_code = fields.String(allow_none=True)
    asset_short_code = fields.String(allow_none=True)
    asset_status = fields.Integer(allow_none=True)
    asset_subtype = fields.String(allow_none=True)
    
    @post_load
    def post_load(self, data, **kwargs):
        return AssetFundLOF(**data)
    
    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }


class AssetFundLOFVOSchema(AssetFundVOSchema):
    """LOF基金VO Schema"""
    listing_exchange = fields.String(allow_none=True, data_key="listingExchange")
    subscription_fee_rate = fields.Decimal(allow_none=True, data_key="subscriptionFeeRate")
    redemption_fee_rate = fields.Decimal(allow_none=True, data_key="redemptionFeeRate")
    nav_calculation_time = fields.Time(allow_none=True, data_key="navCalculationTime")
    trading_suspension_info = fields.String(allow_none=True, data_key="tradingSuspensionInfo")
    index_id = fields.Integer(allow_none=True, data_key="indexId")
    
    # 继承AssetFund的所有字段
    fund_type = fields.String(allow_none=False, data_key="fundType")
    trading_mode = fields.String(allow_none=False, data_key="tradingMode")
    fund_company = fields.String(allow_none=True, data_key="fundCompany")
    fund_manager = fields.String(allow_none=True, data_key="fundManager")
    establishment_date = fields.Date(allow_none=True, data_key="establishmentDate")
    fund_scale = fields.Decimal(allow_none=True, data_key="fundScale")
    fund_status = fields.Integer(allow_none=False, data_key="fundStatus")
    investment_objective = fields.String(allow_none=True, data_key="investmentObjective")
    investment_strategy = fields.String(allow_none=True, data_key="investmentStrategy")
    
    # 继承Asset的所有字段
    currency = fields.Integer(allow_none=True, data_key="currency")
    asset_type = fields.Integer(allow_none=True, data_key="assetType")
    asset_name = fields.String(allow_none=True, data_key="assetName")
    market = fields.Integer(allow_none=True, data_key="market")
    asset_code = fields.String(allow_none=True, data_key="assetCode")
    asset_short_code = fields.String(allow_none=True, data_key="assetShortCode")
    asset_status = fields.Integer(allow_none=True, data_key="assetStatus")
    
    @post_load
    def post_load(self, data, **kwargs):
        return AssetFundLOF(**data)
    
    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }