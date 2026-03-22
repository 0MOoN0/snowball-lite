# -*- coding: UTF-8 -*-
from marshmallow import Schema, fields, EXCLUDE, validate


class AssetSelectQuerySchema(Schema):
    page = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="page 必须大于等于 1"),
        error_messages={"required": "page 为必填参数", "invalid": "page 必须为整数"},
    )
    pageSize = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="pageSize 必须大于等于 1"),
        error_messages={
            "required": "pageSize 为必填参数",
            "invalid": "pageSize 必须为整数",
        },
    )
    assetName = fields.String(
        required=True,
        error_messages={
            "required": "assetName 为必填参数",
            "invalid": "assetName 必须为字符串",
        },
    )

    class Meta:
        unknown = EXCLUDE


class AssetSelectItemSchema(Schema):
    id = fields.Integer()
    asset_name = fields.String(data_key="assetName")