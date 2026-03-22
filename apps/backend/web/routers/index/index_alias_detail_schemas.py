from flask_restx import fields
from marshmallow import Schema, fields as ma_fields, validate, EXCLUDE


def create_index_alias_detail_models(api_ns):
    alias_model = api_ns.model(
        "IndexAlias",
        {
            "id": fields.Integer(description="别名ID"),
            "indexId": fields.Integer(description="关联指数ID"),
            "indexName": fields.String(description="关联指数名称"),
            "providerCode": fields.String(description="数据提供商代码"),
            "providerSymbol": fields.String(description="提供商的指数代码"),
            "providerName": fields.String(description="提供商指数名称"),
            "isPrimary": fields.Boolean(description="是否为主要别名"),
            "status": fields.Integer(description="状态：0-停用，1-启用"),
            "createTime": fields.DateTime(description="创建时间"),
            "updateTime": fields.DateTime(description="更新时间"),
        },
    )

    single_alias_response_model = api_ns.model(
        "SingleIndexAliasResponse",
        {
            "code": fields.Integer(description="响应码"),
            "message": fields.String(description="响应消息"),
            "data": fields.Nested(alias_model, allow_null=True, description="别名数据"),
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

    alias_create_request_model = api_ns.model(
        "IndexAliasCreateRequest",
        {
            "indexId": fields.Integer(required=True, description="关联指数ID"),
            "providerCode": fields.String(required=True, description="数据提供商代码"),
            "providerSymbol": fields.String(required=True, description="提供商指数代码"),
            "providerName": fields.String(required=False, description="提供商指数名称"),
            "isPrimary": fields.Boolean(required=False, description="是否主要别名"),
            "description": fields.String(required=False, description="备注"),
            "status": fields.Integer(required=False, description="状态：0-停用，1-启用"),
        },
    )

    alias_update_request_model = api_ns.clone(
        "IndexAliasUpdateRequest",
        alias_create_request_model,
    )

    return {
        "alias_model": alias_model,
        "single_alias_response_model": single_alias_response_model,
        "base_response_model": base_response_model,
        "alias_create_request_model": alias_create_request_model,
        "alias_update_request_model": alias_update_request_model,
    }


class IndexAliasCreateSchema(Schema):
    index_id = ma_fields.Integer(
        required=True,
        data_key="indexId",
        error_messages={"required": "indexId 为必填字段", "invalid": "indexId 必须为整数"},
    )
    provider_code = ma_fields.String(
        required=True,
        data_key="providerCode",
        error_messages={"required": "providerCode 为必填字段", "invalid": "providerCode 必须为字符串"},
    )
    provider_symbol = ma_fields.String(
        required=True,
        data_key="providerSymbol",
        error_messages={"required": "providerSymbol 为必填字段", "invalid": "providerSymbol 必须为字符串"},
    )
    provider_name = ma_fields.String(
        required=False,
        allow_none=True,
        data_key="providerName",
        error_messages={"invalid": "providerName 必须为字符串"},
    )
    is_primary = ma_fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.OneOf([0, 1], error="isPrimary 只能是 0 或 1"),
        data_key="isPrimary",
        error_messages={"invalid": "isPrimary 必须为整数"},
    )
    status = ma_fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.OneOf([0, 1], error="status 只能是 0 或 1"),
        error_messages={"invalid": "status 必须为整数"},
    )
    description = ma_fields.String(
        required=False,
        allow_none=True,
        error_messages={"invalid": "description 必须为字符串"},
    )

    class Meta:
        unknown = EXCLUDE


class IndexAliasUpdateSchema(Schema):
    index_id = ma_fields.Integer(
        required=False,
        allow_none=True,
        data_key="indexId",
        error_messages={"invalid": "indexId 必须为整数"},
    )
    provider_code = ma_fields.String(
        required=False,
        allow_none=True,
        data_key="providerCode",
        error_messages={"invalid": "providerCode 必须为字符串"},
    )
    provider_symbol = ma_fields.String(
        required=False,
        allow_none=True,
        data_key="providerSymbol",
        error_messages={"invalid": "providerSymbol 必须为字符串"},
    )
    provider_name = ma_fields.String(
        required=False,
        allow_none=True,
        data_key="providerName",
        error_messages={"invalid": "providerName 必须为字符串"},
    )
    is_primary = ma_fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.OneOf([0, 1], error="isPrimary 只能是 0 或 1"),
        data_key="isPrimary",
        error_messages={"invalid": "isPrimary 必须为整数"},
    )
    status = ma_fields.Integer(
        required=False,
        allow_none=True,
        validate=validate.OneOf([0, 1], error="status 只能是 0 或 1"),
        error_messages={"invalid": "status 必须为整数"},
    )
    description = ma_fields.String(
        required=False,
        allow_none=True,
        error_messages={"invalid": "description 必须为字符串"},
    )

    class Meta:
        unknown = EXCLUDE