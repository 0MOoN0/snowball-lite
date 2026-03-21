# -*- coding: UTF-8 -*-
"""
@File    ：asset_list_schemas.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/21 10:00
@Description: 资产列表接口的Flask-RestX模型定义
"""

from flask_restx import fields
from marshmallow import Schema, fields as ma_fields
from web.routers.common.response_schemas import get_pagination_response_model


class AssetListRequestSchema(Schema):
    """资产列表请求参数Schema

    接受驼峰命名的请求参数，内部转换为下划线命名供代码使用
    """

    class Meta:
        # 忽略未知字段，避免额外参数导致验证失败
        unknown = "EXCLUDE"

    # 使用attribute参数指定加载后存储的属性名
    page = ma_fields.Integer(required=True, error_messages={"required": "页码不能为空"})
    pageSize = ma_fields.Integer(
        required=True,
        attribute="page_size",
        error_messages={"required": "每页条数不能为空"},
    )
    assetName = ma_fields.String(
        required=False, load_default=None, attribute="asset_name"
    )
    assetType = ma_fields.String(
        required=False, load_default=None, attribute="asset_type"
    )
    gridId = ma_fields.String(required=False, load_default=None, attribute="grid_id")


def create_asset_list_models(api_ns):
    """
    创建资产列表相关的Flask-RestX模型

    Args:
        api_ns: Flask-RestX Namespace实例

    Returns:
        dict: 包含所有模型的字典
    """

    # 资产列表项模型
    asset_list_item_model = api_ns.model(
        "AssetListItem",
        {
            "id": fields.Integer(description="资产ID", example=1),
            "assetCode": fields.String(description="资产代码", example="600036"),
            "assetShortCode": fields.String(description="资产简称", example="招商银行"),
            "assetStatus": fields.Integer(description="资产状态", example=1),
            "currency": fields.Integer(description="货币类型", example=1),
            "assetType": fields.Integer(description="资产类型", example=1),
            "assetName": fields.String(description="资产名称", example="招商银行"),
            "market": fields.Integer(description="市场类型", example=1),
            "date": fields.String(description="最新数据日期", example="2024-01-15"),
            "close": fields.String(description="最新收盘价", example="1.2345"),
            "closePercent": fields.String(description="最新涨跌幅", example="0.0123"),
        },
    )

    # 资产列表分页响应模型
    asset_list_response_model = get_pagination_response_model(asset_list_item_model)

    # 删除请求模型
    asset_delete_model = api_ns.model(
        "AssetDeleteRequest",
        {
            "ids": fields.List(
                fields.Integer(),
                required=True,
                description="要删除的资产ID列表",
                example=[1, 2, 3],
            )
        },
    )

    # 删除响应模型
    asset_delete_response_model = api_ns.model(
        "AssetDeleteResponse",
        {
            "code": fields.Integer(description="响应码", example=20000),
            "message": fields.String(
                description="响应消息",
                example="操作成功，删除 3 条资产数据， 删除 5 条关联分类数据",
            ),
            "data": fields.Raw(description="响应数据"),
            "success": fields.Boolean(description="是否成功", example=True),
        },
    )

    return {
        "asset_list_item_model": asset_list_item_model,
        "asset_list_response_model": asset_list_response_model,
        "asset_delete_model": asset_delete_model,
        "asset_delete_response_model": asset_delete_response_model,
    }
