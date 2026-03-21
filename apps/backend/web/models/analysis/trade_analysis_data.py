from typing import Dict, Union

from _decimal import Decimal
from flask_marshmallow import Schema
from marshmallow import fields, post_load, post_dump
from sqlalchemy import func, text

from web.common.cons import webcons
from web.common.enum.AnalysisEnum import TransactionAnalysisTypeEnum
from web.common.utils.WebUtils import web_utils
from web.models import db


class TradeAnalysisData(db.Model):
    """
    交易分析数据表，不包含业务
    """

    __bind_key__ = "snowball"
    __tablename__ = "tb_trade_analysis_data"
    __table_args__ = {"comment": "交易分析数据表，不包含业务"}
    __mapper_args__ = {
        'polymorphic_identity': 'trade_analysis',
        'polymorphic_on': 'sub_analysis_type'
    }

    id = db.Column(
        db.BigInteger, primary_key=True, comment="主键ID", autoincrement=True
    )
    asset_id = db.Column(
        db.BigInteger,
        nullable=True,
        comment="对应的资产ID，部分业务，如总计数据没有资产ID",
    )
    record_date = db.Column(
        db.DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="记录时间",
    )
    maximum_occupancy = db.Column(db.Integer, comment="历史最大占用（单位：分）")
    unit_cost = db.Column(db.Integer, comment="单位成本（单位：毫）")
    purchase_amount = db.Column(db.Integer, comment="申购总额（单位：分）")
    present_value = db.Column(db.Integer, comment="基金现值（分）")
    irr = db.Column(db.Integer, comment="内部收益率（万倍，即实际值0.1234存储为1234）")
    investment_yield = db.Column(db.Integer, comment="投资收益率（万倍，即实际值12.3456存储为123456，计算值已为百分比）")
    annualized_return = db.Column(db.Integer, comment="年化收益率（万倍，即实际值0.1234存储为1234）")
    turnover_rate = db.Column(db.Integer, comment="换手率（万倍，即实际值0.1234存储为1234）")
    analysis_type = db.Column(
        db.Integer, comment="分析类型：0-网格，1-网格类型，2-网格策略，3-按仓位分析"
    )
    attributable_share = db.Column(db.Integer, comment="持有份额（百倍，即实际值12.34存储为1234）")
    holding_cost = db.Column(db.Integer, comment="持有成本（单位：分）")
    dividend = db.Column(db.Integer, comment="分红与赎回（单位：分）")
    profit = db.Column(db.Integer, comment="收益总额（单位：分）")
    net_value = db.Column(db.Integer, comment="当日净值（单位：毫，即1.2345元存储为12345）")
    sub_analysis_type = db.Column(db.String(50), nullable=True, comment="分析类型，对应业务表类型，用于关系关联")
    create_time = db.Column(
        db.DateTime, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间"
    )
    update_time = db.Column(
        db.DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.now(),
        comment="更新时间",
    )

    @staticmethod
    def get_analysis_type_enum():
        return TransactionAnalysisTypeEnum

    @staticmethod
    def get_conversion_factor(field_name=None) -> Union[int, Dict[str, int]]:
        """
        获取指定字段名的转换系数。
        用于将实际程序中的数值（通常为小数，部分已为百分比）转换为数据库存储的整数。
        例如：转换系数为10000时，实际值 0.1234 将被存储为 1234；
        若实际值已为百分比 12.34，转换系数为100时，存储为1234。

        Args:
            field_name (str, optional): 字段名。默认为None。如果为None，则返回所有字段的转换系数字典。

        Returns:
            Union[int, Dict[str, int]]:
                - 如果指定了field_name，则返回该字段对应的转换系数（int类型）。
                - 如果field_name为None，则返回包含所有字段转换系数的字典（Dict[str, int]）。

        Raises:
            ValueError: 如果指定的field_name在转换系数字典中不存在，则抛出ValueError异常。

        """
        # 定义转换系数
        # 所有百分比类字段（如IRR、投资收益率等）系数均为10000
        # 即：实际小数 0.1234 * 10000 = 1234 (存储值)
        conversion_factors = {
            "maximum_occupancy": 100,
            "purchase_amount": 100,
            "present_value": 100,
            "unit_cost": 10000,
            "attributable_share": 100,
            "holding_cost": 100,
            "dividend": 100,
            "profit": 100,
            "net_value": 10000,
            "irr": 10000,
            "investment_yield": 10000,  # 特殊：计算值已为百分比（如12.34），为了存储万倍（1234），系数设为100
            "annualized_return": 10000,
            "turnover_rate": 10000,
        }
        if field_name is None:
            return conversion_factors
        if field_name not in conversion_factors:
            raise ValueError(f"Field name '{field_name}' is not supported.")
        return conversion_factors[field_name]


class TransactionAnalysisDataDomainSchema(Schema):
    id = fields.Integer(allow_none=True)
    asset_id = fields.Integer(allow_none=True)
    create_time = fields.DateTime(allow_none=True)
    record_date = fields.DateTime(allow_none=True, format="%Y-%m-%d")
    maximum_occupancy = fields.Integer(allow_none=True)
    unit_cost = fields.Integer(allow_none=True)
    purchase_amount = fields.Integer(allow_none=True)
    present_value = fields.Integer(allow_none=True)
    irr = fields.Integer(allow_none=True)
    net_value = fields.Integer(allow_none=True)
    investment_yield = fields.Integer(allow_none=True)
    annualized_return = fields.Integer(allow_none=True)
    turnover_rate = fields.Integer(allow_none=True)
    analysis_type = fields.Integer(allow_none=True)
    attributable_share = fields.Integer(allow_none=True)
    holding_cost = fields.Integer(allow_none=True)
    dividend = fields.Integer(allow_none=True)
    profit = fields.Integer(allow_none=True)
    sub_analysis_type = fields.String(allow_none=True)
    update_time = fields.DateTime(allow_none=True)

    @post_load
    def post_load(self, data, **kwargs):
        return TradeAnalysisData(**data)

    SKIP_VALUES = set([None])

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items() if value not in self.SKIP_VALUES
        }


class TransactionAnalysisDataVOSchema(Schema):
    RECORD_DATE = "recordDate"
    ASSET_ID = "assetId"
    MAXIMUM_OCCUPANCY = "maximumOccupancy"
    UNIT_COST = "unitCost"
    PURCHASE_AMOUNT = "purchaseAmount"
    PRESENT_VALUE = "presentValue"
    NET_VALUE = "netValue"
    IRR = "irr"
    INVESTMENT_YIELD = "investmentYield"
    ANNUALIZED_RETURN = "annualizedReturn"
    TURNOVER_RATE = "turnoverRate"
    DIVIDEND = "dividend"
    PROFIT = "profit"
    UPDATE_TIME = "updateTime"
    CREATE_TIME = "createTime"
    ATTRIBUTABLE_SHARE = "attributableShare"
    HOLDING_COST = "holdingCost"
    ANALYSIS_TYPE = "analysisType"
    SUB_ANALYSIS_TYPE = "subAnalysisType"

    record_date = fields.DateTime(
        data_key=RECORD_DATE, format=webcons.DataFormatStr.Y_m_d_H_M_S
    )
    asset_id = fields.Integer(data_key=ASSET_ID)
    maximum_occupancy = fields.Integer(data_key=MAXIMUM_OCCUPANCY)
    unit_cost = fields.Integer(data_key=UNIT_COST)
    purchase_amount = fields.Integer(data_key=PURCHASE_AMOUNT)
    present_value = fields.Integer(data_key=PRESENT_VALUE)
    net_value = fields.Integer(data_key=NET_VALUE)
    irr = fields.Integer()
    investment_yield = fields.Integer(data_key=INVESTMENT_YIELD)
    annualized_return = fields.Integer(data_key=ANNUALIZED_RETURN)
    turnover_rate = fields.Integer(data_key=TURNOVER_RATE)
    analysis_type = fields.Integer(data_key=ANALYSIS_TYPE)
    attributable_share = fields.Integer(data_key=ATTRIBUTABLE_SHARE)
    holding_cost = fields.Integer(data_key=HOLDING_COST)
    dividend = fields.Integer(data_key=DIVIDEND)
    profit = fields.Integer(data_key=PROFIT)
    update_time = fields.DateTime(
        data_key=UPDATE_TIME, format=webcons.DataFormatStr.Y_m_d_H_M_S
    )
    create_time = fields.DateTime(
        data_key=CREATE_TIME, format=webcons.DataFormatStr.Y_m_d_H_M_S
    )
    sub_analysis_type = fields.String(data_key=SUB_ANALYSIS_TYPE)

    def get_field(self, key: str):
        return self.fields.get(key, key)

    @post_load
    def post_load(self, data, **kwargs):
        return TradeAnalysisData(**data)

    @post_dump
    def post_dump(self, data: Dict, **kwargs):
        if "maximumOccupancy" in data and data["maximumOccupancy"] is not None:
            data["maximumOccupancy"] = web_utils.to_currency(
                data["maximumOccupancy"] / 100
            )
        if "unitCost" in data and data["unitCost"] is not None:
            data["unitCost"] = web_utils.to_currency(data["unitCost"] / 10000)
        if "purchaseAmount" in data and data["purchaseAmount"] is not None:
            data["purchaseAmount"] = web_utils.to_currency(data["purchaseAmount"] / 100)
        if "presentValue" in data and data["presentValue"] is not None:
            data["presentValue"] = web_utils.to_currency(data["presentValue"] / 100)
        if "investmentYield" in data and data["investmentYield"] is not None:
            data["investmentYield"] = str(data["investmentYield"] / 10000) + "%"
        if "annualizedReturn" in data and data["annualizedReturn"] is not None:
            data["annualizedReturn"] = str(data["annualizedReturn"] / 10000) + "%"
        if "turnoverRate" in data and data["turnoverRate"] is not None:
            data["turnoverRate"] = str(data["turnoverRate"] / 10000) + "%"
        if "holdingCost" in data and data["holdingCost"] is not None:
            data["holdingCost"] = web_utils.to_currency(data["holdingCost"] / 100)
        if "dividend" in data and data["dividend"] is not None:
            data["dividend"] = web_utils.to_currency(data["dividend"] / 100)
        if "profit" in data and data["profit"] is not None:
            data["profit"] = web_utils.to_currency(data["profit"] / 100)
        if "attributableShare" in data and data["attributableShare"] is not None:
            data["attributableShare"] /= 100
        if "irr" in data and data["irr"] is not None:
            data["irr"] = str(data["irr"] / 100) + "%"
        if "netValue" in data and data["netValue"] is not None:
            data["netValue"] = web_utils.to_currency(data["netValue"] / 10000)
        return data


class TransactionAnalysisDataAPISchema(Schema):
    """
    交易分析数据API接口Schema（原始数据版本）
    返回原始数值数据，不进行格式化处理，由前端负责数据格式化
    """
    # 基础字段
    id = fields.Integer(allow_none=True)
    asset_id = fields.Integer(data_key='assetId', allow_none=True)
    record_date = fields.DateTime(data_key='recordDate', format=webcons.DataFormatStr.Y_m_d_H_M_S, allow_none=True)
    
    # 金额字段（原始数值，单位：分）
    maximum_occupancy = fields.Integer(data_key='maximumOccupancy', allow_none=True)
    purchase_amount = fields.Integer(data_key='purchaseAmount', allow_none=True)
    present_value = fields.Integer(data_key='presentValue', allow_none=True)
    holding_cost = fields.Integer(data_key='holdingCost', allow_none=True)
    dividend = fields.Integer(data_key='dividend', allow_none=True)
    profit = fields.Integer(data_key='profit', allow_none=True)
    
    # 价格字段（原始数值，单位：毫）
    unit_cost = fields.Integer(data_key='unitCost', allow_none=True)
    net_value = fields.Integer(data_key='netValue', allow_none=True)
    
    # 百分比字段（原始数值）
    # IRR字段：单位为百倍（即12.34%存储为1234）
    irr = fields.Integer(allow_none=True)
    # 其他百分比字段：单位为万倍（即12.34%存储为123400）
    investment_yield = fields.Integer(data_key='investmentYield', allow_none=True)
    annualized_return = fields.Integer(data_key='annualizedReturn', allow_none=True)
    turnover_rate = fields.Integer(data_key='turnoverRate', allow_none=True)
    
    # 份额字段（原始数值，单位：百倍）
    attributable_share = fields.Integer(data_key='attributableShare', allow_none=True)
    
    # 其他字段
    analysis_type = fields.Integer(data_key='analysisType', allow_none=True)
    sub_analysis_type = fields.String(data_key='subAnalysisType', allow_none=True)
    create_time = fields.DateTime(data_key='createTime', format=webcons.DataFormatStr.Y_m_d_H_M_S, allow_none=True)
    update_time = fields.DateTime(data_key='updateTime', format=webcons.DataFormatStr.Y_m_d_H_M_S, allow_none=True)


class TransactionAnalysisDataChartsSchema(Schema):
    RECORD_DATE = "recordDate"
    ASSET_ID = "assetId"
    MAXIMUM_OCCUPANCY = "maximumOccupancy"
    UNIT_COST = "unitCost"
    PURCHASE_AMOUNT = "purchaseAmount"
    PRESENT_VALUE = "presentValue"
    NET_VALUE = "netValue"
    IRR = "irr"
    INVESTMENT_YIELD = "investmentYield"
    ANNUALIZED_RETURN = "annualizedReturn"
    TURNOVER_RATE = "turnoverRate"
    DIVIDEND = "dividend"
    PROFIT = "profit"
    UPDATE_TIME = "updateTime"
    CREATE_TIME = "createTime"
    ATTRIBUTABLE_SHARE = "attributableShare"
    HOLDING_COST = "holdingCost"
    ANALYSIS_TYPE = "analysisType"
    SUB_ANALYSIS_TYPE = "subAnalysisType"

    record_date = fields.DateTime(
        data_key=RECORD_DATE, format=webcons.DataFormatStr.Y_m_d_H_M_S
    )
    asset_id = fields.Integer(data_key=ASSET_ID)
    maximum_occupancy = fields.Integer(data_key=MAXIMUM_OCCUPANCY)
    unit_cost = fields.Integer(data_key=UNIT_COST)
    purchase_amount = fields.Integer(data_key=PURCHASE_AMOUNT)
    present_value = fields.Integer(data_key=PRESENT_VALUE)
    net_value = fields.Integer(data_key=NET_VALUE)
    irr = fields.Integer()
    investment_yield = fields.Integer(data_key=INVESTMENT_YIELD)
    annualized_return = fields.Integer(data_key=ANNUALIZED_RETURN)
    turnover_rate = fields.Integer(data_key=TURNOVER_RATE)
    analysis_type = fields.Integer(data_key=ANALYSIS_TYPE)
    attributable_share = fields.Integer(data_key=ATTRIBUTABLE_SHARE)
    holding_cost = fields.Integer(data_key=HOLDING_COST)
    dividend = fields.Integer(data_key=DIVIDEND)
    profit = fields.Integer(data_key=PROFIT)
    update_time = fields.DateTime(
        data_key=UPDATE_TIME, format=webcons.DataFormatStr.Y_m_d_H_M_S
    )
    create_time = fields.DateTime(
        data_key=CREATE_TIME, format=webcons.DataFormatStr.Y_m_d_H_M_S
    )
    sub_analysis_type = fields.String(data_key=SUB_ANALYSIS_TYPE)

    def get_field(self, key: str):
        return self.fields.get(key, key)

    @post_load
    def post_load(self, data, **kwargs):
        return TradeAnalysisData(**data)

    @post_dump
    def post_dump(self, data: Dict, **kwargs):
        conversion_factors = {
            "maximumOccupancy": 100,
            "unitCost": 10000,
            "purchaseAmount": 100,
            "presentValue": 100,
            "investmentYield": 10000,
            "annualizedReturn": 100,
            "turnoverRate": 10000,
            "holdingCost": 100,
            "dividend": 100,
            "profit": 100,
            "netValue": 10000,
            "irr": 10000,  # 注意：IRR实际存储为百倍，但这里使用10000是为了统一处理
        }
        for key, factor in conversion_factors.items():
            if key in data and data.get(key) is not None:
                # 对于'attributableShare'特殊处理，不转为字符串
                if key == "attributableShare":
                    data[key] /= factor
                # 对于IRR字段特殊处理：实际存储为百倍，所以除以100而不是10000
                elif key == "irr":
                    data[key] = str(data[key] / 100)
                else:
                    data[key] = str(data[key] / factor)
        return data
