from _decimal import Decimal
from flask_marshmallow import Schema
from marshmallow import fields, post_dump


class TransactionAmountChartsSchema(Schema):
    RECORD_DATE = 'recordDate'
    PRESENT_VALUE = 'presentValue'
    ASSET_NAME = 'assetName'

    record_date = fields.Date(data_key=RECORD_DATE)
    present_value = fields.Decimal(data_key=PRESENT_VALUE)
    asset_name = fields.String(data_key=ASSET_NAME)

    @post_dump
    def post_dump(self, data: dict, **kwargs):
        if self.PRESENT_VALUE in data:
            data[self.PRESENT_VALUE] = str(Decimal(data[self.PRESENT_VALUE]) / 100)
        return data


class TransactionProfitRankChartsSchema(Schema):
    RECORD_DATE = 'recordDate'
    PROFIT = 'profit'
    ASSET_NAME = 'assetName'

    record_date = fields.Date(data_key=RECORD_DATE)
    profit = fields.Decimal(data_key=PROFIT)
    asset_name = fields.String(data_key=ASSET_NAME)

    @post_dump
    def post_dump(self, data: dict, **kwargs):
        if self.PROFIT in data:
            # 处理Decimal转字符串，避免 .0 丢失或格式不一致
            # 这里使用 / 100 转换为元，然后转为 str
            # 数据库中存的是分，如 200000 分 -> 2000.00 元 (float/Decimal)
            # str(Decimal(200000)/100) -> '2000' 如果是整除
            # 让我们统一格式化为两位小数
            val = Decimal(data[self.PROFIT]) / 100
            data[self.PROFIT] = "{:.2f}".format(val)
        return data
