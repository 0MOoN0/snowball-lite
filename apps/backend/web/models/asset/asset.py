from __future__ import annotations

from dataclasses import dataclass, field

from flask_marshmallow import Schema
from marshmallow import post_load, fields, post_dump
from sqlalchemy import func, text

from web.common.enum.asset_enum import AssetTypeEnum, AssetStatusEnum
from web.common.enum.common_enum import CurrencyEnum, MarketEnum
from web.models import db


class Asset(db.Model):
    __tablename__ = "tb_asset"
    __bind_key__ = "snowball"
    __table_args__ = {"comment": "资产模型"}
    __mapper_args__ = {
        'polymorphic_identity': 'asset',
        'polymorphic_on': 'asset_subtype'
    }
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    asset_code = db.Column(db.String(50), nullable=True, comment="资产代码")
    asset_short_code = db.Column(db.String(20), nullable=True, comment="资产简短代码")
    asset_status = db.Column(
        db.Integer, nullable=False, server_default="0", comment="资产状态,0:活跃,1:退市"
    )
    currency = db.Column(
        db.Integer, server_default="0", comment="货币类型,0:人民币,1:美元"
    )
    asset_type = db.Column(
        db.Integer,
        nullable=False,
        server_default="0",
        comment="资产类型,0:指数，1-基金，2-股票",
    )
    asset_name = db.Column(db.String(255), nullable=False, comment="资产名称")
    market = db.Column(
        db.Integer, nullable=True, comment="所在市场:0-CN中国,1-HK香港,2-US美国"
    )
    asset_subtype = db.Column(
        db.String(50), nullable=False, server_default="asset", comment="资产子类型，用于多态继承"
    )
    create_time = db.Column(
        db.DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment="创建时间"
    )
    update_time = db.Column(
        db.DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=func.now(),
        comment="更新时间",
    )

    @staticmethod
    def get_asset_type_enum():
        return AssetTypeEnum

    @staticmethod
    def get_currency_enum() -> CurrencyEnum:
        """
        获取货币类型枚举
        Returns:
        CurrencyEnum: 货币类型枚举
        """
        return CurrencyEnum

    @staticmethod
    def get_asset_type_enum() -> AssetTypeEnum:
        """
        获取Asset资产类型枚举
        Returns:
            AssetTypeEnum: 资产类型枚举
        """
        return AssetTypeEnum

    @staticmethod
    def get_market_enum() -> MarketEnum:
        return MarketEnum

    @staticmethod
    def get_asset_status_enum() -> AssetStatusEnum:
        """
        获取Asset资产状态枚举
        Returns:
            AssetStatusEnum: 资产状态枚举
        """
        return AssetStatusEnum

    @staticmethod
    def get_subtype_by_type(asset_type: AssetTypeEnum) -> str:
        """
        根据资产类型获取对应的子类型
        
        Args:
            asset_type: AssetTypeEnum枚举值
            
        Returns:
            str: 对应的asset_subtype字符串
        """
        type_to_subtype_mapping = {
            AssetTypeEnum.ASSET: 'asset',
            AssetTypeEnum.FUND: 'asset_fund',
            AssetTypeEnum.FUND_ETF: 'asset_fund_etf',
            AssetTypeEnum.FUND_LOF: 'asset_fund_lof',
            AssetTypeEnum.STOCK: 'asset',  # 股票归类为基础资产
            AssetTypeEnum.INDEX: 'asset',  # 指数归类为基础资产
        }
        return type_to_subtype_mapping.get(asset_type, 'asset')

    @staticmethod
    def get_polymorphic_model(asset_type_val: int):
        """
        根据资产类型值获取对应的多态模型类
        
        Args:
            asset_type_val: 资产类型整数值
            
        Returns:
            TargetModelClass: 要查询的SQLAlchemy模型类
        """
        # 局部导入以避免循环依赖
        from web.models.asset.asset_fund import AssetFund, AssetFundETF, AssetFundLOF
        
        # 资产类型到模型类的映射
        model_map = {
            AssetTypeEnum.FUND: AssetFund,
            AssetTypeEnum.FUND_ETF: AssetFundETF,
            AssetTypeEnum.FUND_LOF: AssetFundLOF,
            # 股票和指数目前没有独立模型，映射回Asset
            AssetTypeEnum.STOCK: Asset,
            AssetTypeEnum.INDEX: Asset,
            AssetTypeEnum.ASSET: Asset,
        }
        
        return model_map.get(asset_type_val, Asset)

    def serialize_to_vo(self, asset_subtype=None):
        """
        根据资产对象和子类型序列化数据
        
        Args:
            asset_subtype: 资产子类型，如果为None则从对象中获取
            
        Returns:
            序列化后的数据字典（不包含assetSubtype字段）
        """
        if asset_subtype is None:
            asset_subtype = getattr(self, 'asset_subtype', 'asset')
        
        # 根据子类型选择对应的Schema进行序列化
        if asset_subtype == 'asset_fund_etf':
            from web.models.asset.asset_fund import AssetFundETFVOSchema
            schema = AssetFundETFVOSchema()
        elif asset_subtype == 'asset_fund_lof':
            from web.models.asset.asset_fund import AssetFundLOFVOSchema
            schema = AssetFundLOFVOSchema()
        elif asset_subtype == 'asset_fund':
            from web.models.asset.asset_fund import AssetFundVOSchema
            schema = AssetFundVOSchema()
        else:
            schema = AssetVOSchema()
        
        # 序列化数据并移除assetSubtype字段
        serialized_data = schema.dump(self)
        # 移除assetSubtype字段，不向客户端返回
        serialized_data.pop('assetSubtype', None)
        
        return serialized_data

class AssetExchangeFund(Asset):
    """
    场内基金模型，使用联合表继承Asset
    注：已废弃，请勿再使用
    """
    __tablename__ = "tb_asset_exchange_fund"
    __bind_key__ = "snowball"
    __table_args__ = {"comment": "场内基金模型"}
    __mapper_args__ = {
        'polymorphic_identity': 'exchange_fund'
    }
    
    id = db.Column(
        db.BigInteger, 
        db.ForeignKey('tb_asset.id'), 
        primary_key=True, 
        comment="主键和外键，关联到asset.id，形成联合表继承关系"
    )
    exchange_market = db.Column(
        db.String(16), 
        nullable=False, 
        comment="交易市场，例如'SH'(上海证券交易所)或'SZ'(深圳证券交易所)"
    )
    sub_type = db.Column(
        db.String(16), 
        nullable=False, 
        comment="场内细分类型，用于区分'ETF'和'LOF'"
    )
    tracking_index = db.Column(
        db.String(128), 
        nullable=True, 
        comment="跟踪指数，例如'沪深300指数'、'中证500指数'，对于指数型基金非常重要"
    )


class AssetSchema(Schema):
    SKIP_VALUES = set([None])

    id = fields.Integer(allow_none=True)
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
        return Asset(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }


class AssetVOSchema(Schema):
    """
    资产数据VO对象，用于从数据库转换数据到外部接口使用
    """

    SKIP_VALUES = set([None])
    id = fields.Integer(allow_none=True, data_key="id")
    currency = fields.Integer(allow_none=True, data_key="currency")
    asset_type = fields.Integer(allow_none=True, data_key="assetType")
    asset_name = fields.String(allow_none=True, data_key="assetName")
    market = fields.Integer(allow_none=True, data_key="market")
    asset_code = fields.String(allow_none=True, data_key="assetCode")
    asset_short_code = fields.String(allow_none=True, data_key="assetShortCode")
    asset_status = fields.Integer(allow_none=True, data_key="assetStatus")
    asset_subtype = fields.String(allow_none=True, data_key="assetSubtype")

    @post_load
    def post_load(self, data, **kwargs):
        return Asset(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }


class AssetExchangeFundSchema(Schema):
    """场内基金数据Schema，用于序列化和反序列化"""
    SKIP_VALUES = set([None])
    
    id = fields.Integer(allow_none=True)
    exchange_market = fields.String(allow_none=True)
    sub_type = fields.String(allow_none=True)
    tracking_index = fields.String(allow_none=True)
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
        return AssetExchangeFund(**data)
    
    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }


class AssetExchangeFundVOSchema(Schema):
    """场内基金数据VO对象，用于从数据库转换数据到外部接口使用"""
    SKIP_VALUES = set([None])
    
    id = fields.Integer(allow_none=True, data_key="id")
    exchange_market = fields.String(allow_none=True, data_key="exchangeMarket")
    sub_type = fields.String(allow_none=True, data_key="subType")
    tracking_index = fields.String(allow_none=True, data_key="trackingIndex")
    # 继承Asset的所有字段
    currency = fields.Integer(allow_none=True, data_key="currency")
    asset_type = fields.Integer(allow_none=True, data_key="assetType")
    asset_name = fields.String(allow_none=True, data_key="assetName")
    market = fields.Integer(allow_none=True, data_key="market")
    asset_code = fields.String(allow_none=True, data_key="assetCode")
    asset_short_code = fields.String(allow_none=True, data_key="assetShortCode")
    asset_status = fields.Integer(allow_none=True, data_key="assetStatus")
    asset_subtype = fields.String(allow_none=True, data_key="assetSubtype")
    
    @post_load
    def post_load(self, data, **kwargs):
        return AssetExchangeFund(**data)
    
    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }


@dataclass
class AssetStockDTO:
    """
    股票资产数据传输对象（DTO），用于从外部接口转换数据到系统内部使用，包含两个属性：code(代码)、stock_name(股票名称)
    """

    code: str
    stock_name: str


class AssetStockDTOSchema(Schema):
    """
    使用marshmallow序列化证券股票持仓数据DTO
    """

    code = fields.String()
    stock_name = fields.String()

    def post_load(self, data, **kwargs):
        return AssetStockDTO(**data)


@dataclass
class AssetCurrentDTO:
    """
    资产当前数据传输对象，用于从传输资产当前的信息，包含属性：code(代码)、name(资产名称)、price(资产价格，单位厘)
    """

    code: str | None = None
    name: str | None = None
    price: int | None = None
    market: int | None = None
    currency: int | None = None
    """
    资产价格，单位厘
    """


class AssetCurrentDTOSchema(Schema):
    """
    AssetCurrentDTO的Schema，用于序列化和反序列化
    """
    code = fields.String()
    name = fields.String()
    price = fields.Integer()
    market = fields.Integer()
    currency = fields.Integer()

    def post_load(self, data, **kwargs):
        return AssetCurrentDTO(**data)


class AssetListQuerySchema(Schema):
    """
    资产列表查询结果的Schema，用于序列化资产基础信息和关联的基金日数据
    专用于资产列表API的简化数据输出
    """
    id = fields.Integer()
    asset_code = fields.String(data_key="assetCode")
    asset_short_code = fields.String(data_key="assetShortCode")
    asset_status = fields.Integer(data_key="assetStatus")
    currency = fields.Integer()
    asset_type = fields.Integer(data_key="assetType")
    asset_name = fields.String(data_key="assetName")
    market = fields.Integer()
    f_date = fields.DateTime(data_key="date", format="%Y-%m-%d")
    f_close = fields.String(data_key="close")
    f_close_percent = fields.String(data_key="closePercent")
