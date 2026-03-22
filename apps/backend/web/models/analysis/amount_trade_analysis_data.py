from typing import Dict, Union

from flask_marshmallow import Schema
from marshmallow import fields, post_dump, post_load

from web.common.cons import webcons
from web.common.utils.WebUtils import web_utils
from web.models import db
from web.models.analysis.trade_analysis_data import (
    TradeAnalysisData,
    TransactionAnalysisDataAPISchema,
    TransactionAnalysisDataChartsSchema,
    TransactionAnalysisDataDomainSchema,
    TransactionAnalysisDataVOSchema,
)


class AmountTradeAnalysisData(TradeAnalysisData):
    """
    金额交易分析数据表，继承自TradeAnalysisData，新增股息率字段
    """
    
    __tablename__ = "tb_amount_trade_analysis_data"
    __table_args__ = {"comment": "金额交易分析数据表，新增股息率字段"}
    __mapper_args__ = {
        'polymorphic_identity': 'amount_trade_analysis'
    }
    
    id = db.Column(
        db.BigInteger, 
        db.ForeignKey('tb_trade_analysis_data.id'), 
        primary_key=True, 
        comment="主键ID，外键关联父表"
    )
    dividend_yield = db.Column(
        db.Integer, 
        comment="股息率（万倍，即12.34%存储为123400）"
    )
    
    @staticmethod
    def get_conversion_factor(field_name=None) -> Union[int, Dict[str, int]]:
        """
        获取指定字段名的转换系数，继承父类并新增股息率字段。
        
        Args:
            field_name (str, optional): 字段名。默认为None。如果为None，则返回所有字段的转换系数字典。
            
        Returns:
            Union[int, Dict[str, int]]:
                - 如果指定了field_name，则返回该字段对应的转换系数（int类型）。
                - 如果field_name为None，则返回包含所有字段转换系数的字典（Dict[str, int]）。
                
        Raises:
            ValueError: 如果指定的field_name在转换系数字典中不存在，则抛出ValueError异常。
        """
        # 获取父类的转换系数
        conversion_factors = TradeAnalysisData.get_conversion_factor()
        # 新增股息率字段的转换系数
        conversion_factors["dividend_yield"] = 10000
        
        if field_name is None:
            return conversion_factors
        if field_name not in conversion_factors:
            raise ValueError(f"Field name '{field_name}' is not supported.")
        return conversion_factors[field_name]


class AmountTradeAnalysisDataDomainSchema(TransactionAnalysisDataDomainSchema):
    """
    金额交易分析数据Domain Schema，继承自TransactionAnalysisDataDomainSchema
    """
    # 新增股息率字段
    dividend_yield = fields.Integer(allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return AmountTradeAnalysisData(**data)


class AmountTradeAnalysisDataVOSchema(TransactionAnalysisDataVOSchema):
    """
    金额交易分析数据VO Schema，继承自TransactionAnalysisDataVOSchema
    """
    DIVIDEND_YIELD = "dividendYield"
    
    # 新增股息率字段
    dividend_yield = fields.Integer(data_key=DIVIDEND_YIELD)

    @post_load
    def post_load(self, data, **kwargs):
        return AmountTradeAnalysisData(**data)

    @post_dump
    def post_dump(self, data: Dict, **kwargs):
        # 调用父类的post_dump方法处理基础字段
        data = super().post_dump(data, **kwargs)
        # 处理新增的股息率字段
        if "dividendYield" in data and data["dividendYield"] is not None:
            data["dividendYield"] = str(data["dividendYield"] / 10000) + "%"
        return data


class AmountTradeAnalysisDataAPISchema(TransactionAnalysisDataAPISchema):
    """
    金额交易分析数据API接口Schema，继承自TransactionAnalysisDataAPISchema
    返回原始数值数据，不进行格式化处理，由前端负责数据格式化
    """
    # 新增股息率字段（原始数值，单位：万倍）
    dividend_yield = fields.Integer(data_key='dividendYield', allow_none=True)


class AmountTradeAnalysisDataChartsSchema(TransactionAnalysisDataChartsSchema):
    """
    金额交易分析数据Charts Schema，继承自TransactionAnalysisDataChartsSchema
    """
    DIVIDEND_YIELD = "dividendYield"
    
    # 新增股息率字段
    dividend_yield = fields.Integer(data_key=DIVIDEND_YIELD)

    @post_load
    def post_load(self, data, **kwargs):
        return AmountTradeAnalysisData(**data)

    @post_dump
    def post_dump(self, data: Dict, **kwargs):
        # 调用父类的post_dump方法处理基础字段
        data = super().post_dump(data, **kwargs)
        # 处理新增的股息率字段
        if "dividendYield" in data and data.get("dividendYield") is not None:
            data["dividendYield"] = str(data["dividendYield"] / 10000)
        return data