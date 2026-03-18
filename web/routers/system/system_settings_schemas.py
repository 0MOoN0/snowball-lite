# -*- coding: UTF-8 -*-
"""
@File    ：system_settings_schemas.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/2/16 15:30
@Description: 系统设置相关的API模型定义
"""

from flask_restx import fields, Namespace

# 导入通用的响应模型创建函数
# from web.routers.common.response_schemas import (
#     create_base_response_model,
#     create_pagination_model,
# )


def create_system_settings_models(api: Namespace):
    """
    创建系统设置相关的API模型

    Args:
        api: flask-restx的Namespace实例

    Returns:
        dict: 包含所有模型的字典
    """

    # 基础设置项模型
    setting_model = api.model(
        "Setting",
        {
            "id": fields.Integer(description="设置项ID"),
            "key": fields.String(
                required=True, description="设置项唯一标识键", max_length=100
            ),
            "value": fields.String(required=True, description="设置项的值"),
            "settingType": fields.String(
                required=True,
                description="设置类型",
                enum=["string", "int", "float", "bool", "json", "password"],
            ),
            "group": fields.String(
                description="设置分组", default="general", max_length=100
            ),
            "description": fields.String(description="设置项描述"),
            "defaultValue": fields.String(
                description="设置项默认值",
            ),
            "createdTime": fields.DateTime(
                description="创建时间",
            ),
            "updatedTime": fields.DateTime(
                description="更新时间",
            ),
        },
    )

    # 创建设置项请求模型
    setting_create_model = api.model(
        "SettingCreate",
        {
            "key": fields.String(
                required=True, description="设置项唯一标识键", max_length=100
            ),
            "value": fields.String(required=True, description="设置项的值"),
            "settingType": fields.String(
                required=True,
                description="设置类型",
                enum=["string", "int", "float", "bool", "json", "password"],
                attribute="setting_type"  # 映射到数据库字段
            ),
            "group": fields.String(
                description="设置分组", default="general", max_length=100
            ),
            "description": fields.String(description="设置项描述"),
            "defaultValue": fields.String(
                description="设置项默认值",
                attribute="default_value"  # 映射到数据库字段
            ),
        },
    )

    # 更新设置项请求模型
    setting_update_model = api.model(
        "SettingUpdate",
        {
            "key": fields.String(required=True, description="要更新的设置项唯一标识键"),
            "value": fields.String(required=True, description="新的设置值"),
            "settingType": fields.String(description="设置类型：string/int/float/bool/json/password"),
            "group": fields.String(description="设置分组：general/email/security/notification等"),
            "description": fields.String(description="新的设置描述"),
            "defaultValue": fields.String(description="设置项默认值"),
        },
    )

    # 设置项列表模型已移除，使用通用的分页响应模型

    # 统一响应模型 (使用通用的基础响应模型)
    # 当 data 字段是 setting_model 时
    single_setting_response_model = api.model(
        "SingleSettingResponse",
        {
            "code": fields.Integer(required=True, description="响应码"),
            "message": fields.String(required=True, description="响应消息"),
            "data": fields.Nested(
                setting_model, allow_null=True, description="响应数据"
            ),
            "success": fields.Boolean(required=True, description="是否成功"),
        },
    )

    # 列表响应模型已移除，使用通用的分页响应模型

    # 查询参数模型已移除，使用reqparse处理查询参数

    # 批量更新请求模型
    setting_batch_update_item_model = api.model(
        "SettingBatchUpdateItem",
        {
            "key": fields.String(required=True, description="要更新的设置项唯一标识键"),
            "value": fields.String(description="新的设置值"),
            "settingType": fields.String(description="设置类型：string/int/float/bool/json/password"),
            "group": fields.String(description="设置分组：general/email/security/notification等"),
            "description": fields.String(description="新的设置描述"),
            "defaultValue": fields.String(description="设置项默认值"),
        },
    )

    setting_batch_update_model = api.model(
        "SettingBatchUpdate",
        {
            "settings": fields.List(
                fields.Nested(setting_batch_update_item_model),
                required=True,
                description="要批量更新的设置项列表",
                min_items=1,
                max_items=50
            )
        },
    )

    # 批量更新响应模型 - 使用通用响应格式
    batch_update_response_model = api.model(
        "BatchUpdateResponse",
        {
            "code": fields.Integer(required=True, description="响应码"),
            "message": fields.String(required=True, description="响应消息"),
            "data": fields.Raw(allow_null=True, description="批量更新结果"),
            "success": fields.Boolean(required=True, description="是否成功"),
        },
    )

    # 如果希望data字段更通用，可以使用 fields.Raw，但会失去部分校验能力
    # response_model = create_base_response_model(api)

    return {
        "setting_model": setting_model,
        "setting_create_model": setting_create_model,
        "setting_update_model": setting_update_model,
        "single_setting_response_model": single_setting_response_model,
        "setting_batch_update_model": setting_batch_update_model,
        "batch_update_response_model": batch_update_response_model,
    }
