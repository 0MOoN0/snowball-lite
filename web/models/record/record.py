from _decimal import Decimal
from flask_marshmallow import Schema
from marshmallow import post_load, fields, post_dump

from web.common.cons import webcons
from web.common.enum.record_enum import RecordStrategyKeyEnum, RecordDirectionEnum
from web.models import db


class Record(db.Model):
    __tablename__ = "tb_record"
    __bind_key__ = "snowball"
    __table_args__ = {"comment": "交易记录表"}

    id = db.Column(db.BigInteger, primary_key=True, comment="主键", autoincrement=True)
    transactions_fee = db.Column(
        db.Integer, nullable=False, server_default="0", comment="交易费用（单位：厘）"
    )
    transactions_share = db.Column(
        db.Integer, nullable=False, server_default="0", comment="交易份额"
    )
    transactions_date = db.Column(db.DateTime, nullable=False, comment="交易时间")
    asset_id = db.Column(db.BigInteger, nullable=False, comment="资产ID")
    transactions_price = db.Column(
        db.Integer, nullable=False, server_default="0", comment="交易价格（单位：厘）"
    )
    transactions_direction = db.Column(
        db.Integer,
        nullable=False,
        comment="交易方向，0:卖出,1:买入,2:转托管入,3:转托管出,4:申购,5:赎回",
    )
    transactions_amount = db.Column(
        db.Integer, nullable=False, server_default="0", comment="交易金额（单位：厘）"
    )
    strategy_type = db.Column(db.Integer, comment="策略类型：0-网格")
    strategy_key = db.Column(db.BigInteger, comment="策略类型对应的具体策略ID")

    @staticmethod
    def get_strategy_key_enum():
        return RecordStrategyKeyEnum

    @staticmethod
    def get_record_directoin_enum():
        return RecordDirectionEnum


class RecordSchema(Schema):
    id = fields.Integer()
    transactions_fee = fields.Integer()
    transactions_share = fields.Integer()
    transactions_date = fields.DateTime(format=webcons.DataFormatStr.Y_m_d_H_M_S)
    asset_id = fields.Integer()
    transactions_price = fields.Integer()
    transactions_direction = fields.Integer()
    transactions_amount = fields.Integer()
    strategy_type = fields.Integer()
    strategy_key = fields.Integer()

    @post_load
    def post_load(self, data, **kwargs):
        return Record(**data)


# 驼峰与下划线互转
class RecordListSchema(Schema):
    record_id = fields.Integer(data_key="recordId", required=True)
    transactions_fee = fields.Decimal(data_key="transactionsFee", as_string=True)
    transactions_share = fields.Decimal(data_key="transactionsShare", as_string=True)
    transactions_date = fields.DateTime(
        data_key="transactionsDate", format=webcons.DataFormatStr.Y_m_d_H_M_S
    )
    asset_id = fields.Integer(data_key="assetId", allow_none=True)
    transactions_price = fields.Decimal(data_key="transactionsPrice", as_string=True)
    transactions_direction = fields.Integer(data_key="transactionsDirection")
    transactions_amount = fields.Decimal(data_key="transactionsAmount", as_string=True)
    strategy_type = fields.Integer(data_key="strategyType", allow_none=True)
    strategy_key = fields.Integer(data_key="strategyKey", allow_none=True)
    asset_name = fields.String(data_key="assetName", allow_none=True)
    asset_id = fields.Integer(data_key="assetId", required=True)

    @post_load
    def post_load(self, data, **kwargs):
        return Record(**data)


class RecordExportSchema(Schema):
    """
    数据库导出数据专用Schema
    """

    transactions_fee = fields.Integer()
    transactions_share = fields.Integer()
    transactions_date = fields.DateTime(format=webcons.DataFormatStr.Y_m_d_H_M_S)
    transactions_price = fields.Integer()
    transactions_direction = fields.Integer()

    @post_dump
    def post_dump(self, data, **kwargs):
        # 根据交易方向处理份额，交易方向为0时卖出，份额减少，为1时买入，份额增加
        if "transactions_direction" in data:
            data["transactions_share"] = (
                -(data["transactions_share"])
                if data["transactions_direction"] in [0, 3, 5]
                else data["transactions_share"]
            )
        # 对费用做处理
        if "transactions_fee" in data:
            data["transactions_fee"] = str(Decimal(data["transactions_fee"]) / 1000)
        if "transactions_price" in data:
            data["transactions_price"] = str(Decimal(data["transactions_price"]) / 1000)
        return data
