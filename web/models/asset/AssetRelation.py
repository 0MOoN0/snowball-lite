from dataclasses import dataclass

from flask_marshmallow import Schema
from marshmallow import fields, post_load


# @dataclass(init=False)
class AssetRelation:
    """
    证券类在系统中与其他对象关联的条数
    """
    id: int
    category: int
    daily_data: int
    fee_rule: int
    holding_data: int
    """
    该证券的持仓信息
    """
    held_data: int
    """
    该证券作为持仓被持有的数据条数，属于被其他对象依赖的项目
    """
    record_data: int
    """
    交易记录数
    """
    grid_data: int
    """
    该资产关联的网格数量，属于被其他对象依赖的项目
    """
    transaction_analysis_data: int
    """
    该证券交易分析的数据条数，属于被其他对象依赖的项目
    """


class AssetRelationSchema(Schema):
    id = fields.Integer(allow_none=True, data_key='id')
    transaction_analysis_data = fields.Integer(allow_none=True, data_key='transactionAnalysisData')
    grid_data = fields.Integer(allow_none=True, data_key='gridData')
    held_data = fields.Integer(allow_none=True, data_key='heldData')
    holding_data = fields.Integer(allow_none=True, data_key='holdingData')
    fee_rule = fields.Integer(allow_none=True, data_key='feeRule')
    category = fields.Integer(allow_none=True, data_key='category')
    daily_data = fields.Integer(allow_none=True, data_key='dailyData')
    record_data = fields.Integer(allow_none=True, data_key='recordData')

    @post_load
    def post_load(self, data, **kwargs):
        return AssetRelation(**data)

