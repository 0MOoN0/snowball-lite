from marshmallow import Schema, fields
from flask_restx import fields as restx_fields
from web.common.cons import webcons
from web.routers.common.response_schemas import (
    get_base_response_model,
    create_typed_response_model,
)

# Shared Definition for RestX Model
trade_reference_model_definition = {
    "id": restx_fields.Integer(description="关联ID"),
    "recordId": restx_fields.Integer(description="交易记录ID"),
    "groupType": restx_fields.Integer(description="分组类型"),
    "groupId": restx_fields.Integer(description="业务对象ID"),
}


# Marshmallow Schema for Validation
class TradeReferenceUpdateItemSchema(Schema):
    """
    关联更新项Schema
    """

    group_type = fields.Integer(
        data_key="groupType", load_default=0, description="分组类型: 0-其他, 1-网格"
    )
    group_id = fields.Integer(
        data_key="groupId", required=True, description="业务对象ID"
    )

    class Meta:
        unknown = "EXCLUDE"


class TradeReferenceResponseItemSchema(Schema):
    """
    关联响应项Schema
    """

    id = fields.Integer(description="关联ID")
    record_id = fields.Integer(data_key="recordId", description="交易记录ID")
    group_type = fields.Integer(data_key="groupType", description="分组类型")
    group_id = fields.Integer(data_key="groupId", description="业务对象ID")


class RecordCreateSchema(Schema):
    group_type = fields.Integer(
        data_key="groupType", load_default=0, description="分组类型: 0-其他, 1-网格"
    )
    group_id = fields.Integer(
        data_key="groupId", load_default=None, description="业务对象ID"
    )
    asset_id = fields.Integer(required=True, data_key="assetId", description="资产ID")
    transactions_fee = fields.Integer(
        data_key="transactionsFee", description="交易费用（单位：厘）"
    )
    transactions_share = fields.Integer(
        data_key="transactionsShare", description="交易份额"
    )
    transactions_date = fields.DateTime(
        data_key="transactionsDate",
        format=webcons.DataFormatStr.Y_m_d_H_M_S,
        description="交易时间",
    )
    transactions_price = fields.Integer(
        data_key="transactionsPrice", description="交易价格（单位：厘）"
    )
    transactions_direction = fields.Integer(
        data_key="transactionsDirection", description="交易方向，0:卖出,1:买入"
    )
    transactions_amount = fields.Integer(
        data_key="transactionsAmount", description="交易金额（单位：厘）"
    )

    class Meta:
        unknown = "EXCLUDE"


class RecordUpdateSchema(Schema):
    id = fields.Integer(required=True, description="交易记录ID")
    transactions_fee = fields.Integer(
        data_key="transactionsFee", description="交易费用（单位：厘）"
    )
    transactions_share = fields.Integer(
        data_key="transactionsShare", description="交易份额"
    )
    transactions_date = fields.DateTime(
        data_key="transactionsDate",
        format=webcons.DataFormatStr.Y_m_d_H_M_S,
        description="交易时间",
    )
    transactions_price = fields.Integer(
        data_key="transactionsPrice", description="交易价格（单位：厘）"
    )
    transactions_direction = fields.Integer(
        data_key="transactionsDirection", description="交易方向，0:卖出,1:买入"
    )
    transactions_amount = fields.Integer(
        data_key="transactionsAmount", description="交易金额（单位：厘）"
    )
    # 可选的关联更新列表
    trade_references = fields.List(
        fields.Nested(TradeReferenceUpdateItemSchema),
        data_key="tradeReferences",
        load_default=None,
        description="交易关联列表（全量更新）",
    )

    class Meta:
        unknown = "EXCLUDE"


# Flask-RestX Models for Documentation
def create_record_models(api):
    record_create_model = api.model(
        "RecordCreate",
        {
            "groupType": restx_fields.Integer(
                description="分组类型: 0-其他, 1-网格", example=1
            ),
            "groupId": restx_fields.Integer(description="业务对象ID", example=1),
            "assetId": restx_fields.Integer(
                required=True, description="资产ID", example=1
            ),
            "transactionsFee": restx_fields.Integer(
                description="交易费用（单位：厘）", example=100
            ),
            "transactionsShare": restx_fields.Integer(
                description="交易份额", example=1000
            ),
            "transactionsDate": restx_fields.String(
                description="交易时间", example="2023-10-01 12:00:00"
            ),
            "transactionsPrice": restx_fields.Integer(
                description="交易价格（单位：厘）", example=10000
            ),
            "transactionsDirection": restx_fields.Integer(
                description="交易方向，0:卖出,1:买入", example=1
            ),
            "transactionsAmount": restx_fields.Integer(
                description="交易金额（单位：厘）", example=100000
            ),
        },
    )

    update_item_model = api.model(
        "TradeReferenceUpdateItem",
        {
            "groupType": restx_fields.Integer(description="分组类型", example=1),
            "groupId": restx_fields.Integer(
                required=True, description="业务对象ID", example=1
            ),
        },
    )

    record_update_model = api.model(
        "RecordUpdate",
        {
            "id": restx_fields.Integer(
                required=True, description="交易记录ID", example=1
            ),
            "transactionsFee": restx_fields.Integer(
                description="交易费用（单位：厘）", example=100
            ),
            "transactionsShare": restx_fields.Integer(
                description="交易份额", example=1000
            ),
            "transactionsDate": restx_fields.String(
                description="交易时间", example="2023-10-01 12:00:00"
            ),
            "transactionsPrice": restx_fields.Integer(
                description="交易价格（单位：厘）", example=10000
            ),
            "transactionsDirection": restx_fields.Integer(
                description="交易方向，0:卖出,1:买入", example=1
            ),
            "transactionsAmount": restx_fields.Integer(
                description="交易金额（单位：厘）", example=100000
            ),
            "tradeReferences": restx_fields.List(
                restx_fields.Nested(update_item_model), description="关联列表"
            ),
        },
    )

    trade_reference_model = api.model(
        "TradeReference", trade_reference_model_definition
    )

    record_detail_model = api.model(
        "RecordDetail",
        {
            "recordId": restx_fields.Integer(description="交易记录ID"),
            "transactionsFee": restx_fields.String(description="交易费用"),
            "transactionsShare": restx_fields.String(description="交易份额"),
            "transactionsDate": restx_fields.String(description="交易时间"),
            "transactionsPrice": restx_fields.String(description="交易价格"),
            "transactionsDirection": restx_fields.Integer(description="交易方向"),
            "transactionsAmount": restx_fields.String(description="交易金额"),
            "assetId": restx_fields.Integer(description="资产ID"),
            "assetName": restx_fields.String(description="资产名称"),
            "groupTypes": restx_fields.List(
                restx_fields.Integer, description="关联分组类型"
            ),
            "tradeReferences": restx_fields.List(
                restx_fields.Nested(trade_reference_model), description="关联详情"
            ),
        },
    )

    record_response_model = get_base_response_model()

    record_detail_response_model = create_typed_response_model(
        record_detail_model, model_name_suffix="RecordDetail"
    )

    return {
        "record_create_model": record_create_model,
        "record_update_model": record_update_model,
        "record_response_model": record_response_model,
        "record_detail_model": record_detail_model,
        "record_detail_response_model": record_detail_response_model,
    }
