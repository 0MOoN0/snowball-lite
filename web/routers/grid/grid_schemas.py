# -*- coding: UTF-8 -*-
from flask_restx import fields, Namespace
from marshmallow import Schema, fields as ma_fields


from web.routers.common.response_schemas import create_typed_response_model


def create_grid_relation_models(api: Namespace):
    """
    创建网格关系相关的API模型
    Args:
        api: Flask-RestX Namespace
    Returns:
        dict: 模型字典
    """

    # GridType 模型
    grid_type_model = api.model(
        "GridTypeRelation",
        {
            "id": fields.Integer(description="网格类型ID"),
            "gridId": fields.Integer(description="所属网格ID"),
            "typeName": fields.String(description="网格类型名称"),
            "gridTypeStatus": fields.Integer(description="网格类型状态"),
            "assetId": fields.Integer(description="资产ID"),
        },
    )

    # Grid 模型 (包含 GridType 列表)
    grid_relation_model = api.model(
        "GridRelation",
        {
            "id": fields.Integer(description="网格ID"),
            "assetId": fields.Integer(description="资产ID"),
            "gridName": fields.String(description="网格名称"),
            "gridStatus": fields.Integer(description="网格状态"),
            "gridTypes": fields.List(
                fields.Nested(grid_type_model), description="关联的网格类型列表"
            ),
        },
    )

    # 使用通用函数创建响应模型
    # data 字段是一个 grid_relation_model 的列表
    grid_relation_response_model = create_typed_response_model(
        fields.List(fields.Nested(grid_relation_model)),
        model_name_suffix="_GridRelationList",
    )

    return {
        "grid_type_model": grid_type_model,
        "grid_relation_model": grid_relation_model,
        "grid_relation_response_model": grid_relation_response_model,
    }


class GridTypeSimpleSchema(Schema):
    """网格类型简单Schema"""

    id = ma_fields.Integer()
    grid_id = ma_fields.Integer(data_key="gridId")
    type_name = ma_fields.String(data_key="typeName")
    grid_type_status = ma_fields.Integer(data_key="gridTypeStatus")
    asset_id = ma_fields.Integer(data_key="assetId")


class GridRelationSchema(Schema):
    """网格关系Schema"""

    id = ma_fields.Integer()
    asset_id = ma_fields.Integer(data_key="assetId")
    grid_name = ma_fields.String(data_key="gridName")
    grid_status = ma_fields.Integer(data_key="gridStatus")
    grid_types = ma_fields.List(
        ma_fields.Nested(GridTypeSimpleSchema), data_key="gridTypes"
    )
