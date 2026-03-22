from flask_restx import fields
from marshmallow import Schema, fields as ma_fields, validate, EXCLUDE


def create_asset_alias_list_models(api_ns):
    alias_model = api_ns.model(
        "AssetAlias",
        {
            "id": fields.Integer(description="别名ID"),
            "assetId": fields.Integer(description="关联资产ID"),
            "assetName": fields.String(description="关联资产名称"),
            "providerCode": fields.String(description="数据提供商代码"),
            "providerSymbol": fields.String(description="提供商的资产代码"),
            "providerName": fields.String(description="提供商资产名称"),
            "isPrimary": fields.Boolean(description="是否为主要别名"),
            "status": fields.Integer(description="状态：0-停用，1-启用"),
            "createTime": fields.String(description="创建时间"),
            "updateTime": fields.String(description="更新时间"),
        },
    )

    list_response_model = api_ns.model(
        "AliasListResponse",
        {
            "code": fields.Integer(description="响应码"),
            "message": fields.String(description="响应消息"),
            "data": fields.Nested(
                api_ns.model(
                    "AliasListData",
                    {
                        "items": fields.List(
                            fields.Nested(alias_model), description="别名列表"
                        ),
                        "total": fields.Integer(description="总数量"),
                        "page": fields.Integer(description="页码"),
                        "size": fields.Integer(description="每页条数"),
                    },
                ),
                allow_null=True,
                description="分页数据",
            ),
            "success": fields.Boolean(description="是否成功"),
        },
    )

    base_response_model = api_ns.model(
        "BaseResponse",
        {
            "code": fields.Integer(description="响应码"),
            "message": fields.String(description="响应消息"),
            "data": fields.Raw(allow_null=True, description="响应数据"),
            "success": fields.Boolean(description="是否成功"),
        },
    )

    batch_associate_request_model = api_ns.model(
        "BatchAssociateRequest",
        {
            "assetId": fields.Integer(required=True, description="要关联的资产ID"),
            "aliasIds": fields.List(
                fields.Integer, required=True, description="要批量关联的别名ID列表"
            ),
        },
    )

    return {
        "alias_model": alias_model,
        "list_response_model": list_response_model,
        "base_response_model": base_response_model,
        "batch_associate_request_model": batch_associate_request_model,
    }


class AssetAliasListQuerySchema(Schema):
    page = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="page 必须大于等于 1"),
        error_messages={"required": "page 为必填参数", "invalid": "page 必须为整数"},
    )
    pageSize = ma_fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="pageSize 必须大于等于 1"),
        error_messages={
            "required": "pageSize 为必填参数",
            "invalid": "pageSize 必须为整数",
        },
    )
    providerCode = ma_fields.String(
        required=False,
        allow_none=True,
        error_messages={"invalid": "providerCode 必须为字符串"},
    )
    providerSymbol = ma_fields.String(
        required=False,
        allow_none=True,
        error_messages={"invalid": "providerSymbol 必须为字符串"},
    )
    assetId = ma_fields.Integer(
        required=False,
        allow_none=True,
        error_messages={"invalid": "assetId 必须为整数"},
    )
    status = ma_fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.OneOf([0, 1], error="status 只能是 0 或 1"),
        error_messages={"invalid": "status 必须为整数"},
    )
    isPrimary = ma_fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.OneOf([0, 1], error="isPrimary 只能是 0 或 1"),
        error_messages={"invalid": "isPrimary 必须为整数"},
    )

    class Meta:
        unknown = EXCLUDE
