from marshmallow import Schema, fields
from flask_restx import fields as restx_fields
from web.common.cons import webcons
from web.routers.common.response_schemas import (
    create_typed_response_model,
    create_pagination_model,
)

# 导入共享的 TradeReferenceResponseItemSchema
# 注意：为了避免循环导入，最好将共享Schema定义在一个单独的文件或者record_schemas.py中
# 这里我们假设 TradeReferenceResponseItemSchema 在 record_schemas.py 中定义，并导入它
from web.routers.record.record_schemas import (
    TradeReferenceResponseItemSchema,
    trade_reference_model_definition,
)


class RecordListRequestSchema(Schema):
    page_size = fields.Integer(
        data_key="pageSize", required=True, description="每页显示的记录条数"
    )
    page = fields.Integer(required=True, description="页码")
    group_type = fields.Integer(
        data_key="groupType", load_default=None, description="分组类型: 0-其他, 1-网格"
    )
    group_id = fields.Integer(
        data_key="groupId", load_default=None, description="业务对象ID"
    )
    asset_name = fields.String(
        data_key="assetName", load_default=None, description="资产名称（模糊查询）"
    )
    asset_alias = fields.String(
        data_key="assetAlias", load_default=None, description="资产别名（模糊查询）"
    )
    start_date = fields.String(
        data_key="startDate", load_default=None, description="交易开始时间"
    )
    end_date = fields.String(
        data_key="endDate", load_default=None, description="交易结束时间"
    )
    transactions_direction = fields.Integer(
        data_key="transactionsDirection", load_default=None, description="交易方向"
    )

    class Meta:
        unknown = "EXCLUDE"


class RecordListItemSchema(Schema):
    """
    列表响应项Schema (包含group_types)
    """

    record_id = fields.Integer(data_key="recordId", required=True)
    transactions_fee = fields.Decimal(data_key="transactionsFee", as_string=True)
    transactions_share = fields.Decimal(data_key="transactionsShare", as_string=True)
    transactions_date = fields.DateTime(
        data_key="transactionsDate", format=webcons.DataFormatStr.Y_m_d_H_M_S
    )
    transactions_price = fields.Decimal(data_key="transactionsPrice", as_string=True)
    transactions_direction = fields.Integer(data_key="transactionsDirection")
    transactions_amount = fields.Decimal(data_key="transactionsAmount", as_string=True)
    asset_id = fields.Integer(data_key="assetId", required=True)
    asset_name = fields.String(data_key="assetName", allow_none=True)
    primary_alias_code = fields.String(
        data_key="primaryAliasCode", allow_none=True, description="主要别名代码"
    )
    primary_provider_name = fields.String(
        data_key="primaryProviderName", allow_none=True, description="主要提供商名称"
    )
    group_types = fields.List(
        fields.Integer(), data_key="groupTypes", description="关联的分组类型列表"
    )
    trade_references = fields.List(
        fields.Nested(TradeReferenceResponseItemSchema),
        data_key="tradeReferences",
        description="关联详情列表",
    )


def create_record_list_models(api):
    # 复用 trade_reference_model，但需要在本api namespace下重新注册或者直接使用定义
    trade_reference_model = api.model(
        "TradeReference", trade_reference_model_definition
    )

    record_list_request_model = api.model(
        "RecordListRequest",
        {
            "page": restx_fields.Integer(required=True, description="页码", example=1),
            "pageSize": restx_fields.Integer(
                required=True, description="每页条数", example=10
            ),
            "groupType": restx_fields.Integer(description="分组类型", example=1),
            "groupId": restx_fields.Integer(description="业务对象ID", example=1),
            "assetName": restx_fields.String(
                description="资产名称（模糊查询）", example="科技"
            ),
            "assetAlias": restx_fields.String(
                description="资产别名（模糊查询）", example="AAPL"
            ),
            "startDate": restx_fields.String(
                description="开始时间", example="2023-01-01 00:00:00"
            ),
            "endDate": restx_fields.String(
                description="结束时间", example="2023-12-31 23:59:59"
            ),
            "transactionsDirection": restx_fields.Integer(
                description="交易方向", example=1
            ),
        },
    )

    record_list_response_model = create_typed_response_model(
        create_pagination_model(
            api.model(
                "RecordListItem",
                {
                    "recordId": restx_fields.Integer(description="记录ID"),
                    "transactionsFee": restx_fields.String(description="交易费用"),
                    "transactionsShare": restx_fields.String(description="交易份额"),
                    "transactionsDate": restx_fields.String(description="交易时间"),
                    "transactionsPrice": restx_fields.String(description="交易价格"),
                    "transactionsDirection": restx_fields.Integer(
                        description="交易方向"
                    ),
                    "transactionsAmount": restx_fields.String(description="交易金额"),
                    "assetId": restx_fields.Integer(description="资产ID"),
                    "assetName": restx_fields.String(description="资产名称"),
                    "primaryAliasCode": restx_fields.String(description="主要别名代码"),
                    "primaryProviderName": restx_fields.String(
                        description="主要提供商名称"
                    ),
                    "groupTypes": restx_fields.List(
                        restx_fields.Integer, description="关联分组类型"
                    ),
                    "tradeReferences": restx_fields.List(
                        restx_fields.Nested(trade_reference_model),
                        description="关联详情",
                    ),
                },
            ),
            model_name_suffix="RecordList",
        ),
        model_name_suffix="RecordList",
    )

    return {
        "record_list_request_model": record_list_request_model,
        "record_list_response_model": record_list_response_model,
    }
