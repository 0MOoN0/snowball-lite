# -*- coding: UTF-8 -*-
"""
@File    ：notification_schemas.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/2/16 15:30
@Description: 通知相关的API模型定义
"""

from flask_restx import fields, Namespace


def create_notification_models(api: Namespace):
    """
    创建通知相关的API模型

    Args:
        api: flask-restx的Namespace实例

    Returns:
        dict: 包含所有模型的字典
    """

    # 基础通知模型
    notification_model = api.model(
        "Notification",
        {
            "id": fields.Integer(description="通知ID"),
            "businessType": fields.Integer(
                description="通知的业务类型，0-网格交易通知,1-消息处理提醒通知,2-系统运行通知,3-日常报告通知"
            ),
            "noticeType": fields.Integer(
                description="通知的类型，0-消息型通知，1-确认型通知"
            ),
            "noticeStatus": fields.Integer(
                description="通知的状态：0-未发送，1-未读，2-已读，3-已处理，4-已发送"
            ),
            "content": fields.String(description="通知的内容"),
            "timestamp": fields.String(description="通知的时间"),
            "createTime": fields.DateTime(description="创建时间"),
            "updateTime": fields.DateTime(description="更新时间"),
            "noticeLevel": fields.Integer(
                description="通知重要性等级，重要性按数字递增，最小为0"
            ),
            "title": fields.String(description="通知标题"),
        },
    )

    # 通知确认数据模型
    notification_confirm_data_model = api.model(
        "NotificationConfirmData",
        {
            "confirmData": fields.List(
                fields.Raw(), required=True, description="确认数据列表"
            )
        },
    )

    # 批量已读请求模型
    notification_batch_read_request_model = api.model(
        "NotificationBatchReadRequest",
        {
            "ids": fields.List(
                fields.Integer, required=False, description="待标记为已读的通知ID列表"
            ),
            "businessType": fields.Integer(
                required=False, description="按业务类型批量标记未读为已读"
            ),
        },
    )

    # 通知列表响应模型
    notification_list_response_model = api.model(
        "NotificationListResponse",
        {
            "code": fields.Integer(required=True, description="响应码"),
            "message": fields.String(required=True, description="响应消息"),
            "data": fields.Nested(
                api.model(
                    "NotificationListData",
                    {
                        "items": fields.List(
                            fields.Nested(notification_model), description="通知列表"
                        ),
                        "total": fields.Integer(description="总数量"),
                    },
                ),
                allow_null=True,
                description="响应数据",
            ),
            "success": fields.Boolean(required=True, description="是否成功"),
        },
    )

    # 单个通知响应模型
    single_notification_response_model = api.model(
        "SingleNotificationResponse",
        {
            "code": fields.Integer(required=True, description="响应码"),
            "message": fields.String(required=True, description="响应消息"),
            "data": fields.Nested(
                notification_model, allow_null=True, description="响应数据"
            ),
            "success": fields.Boolean(required=True, description="是否成功"),
        },
    )

    # 通知数量响应模型
    notification_count_response_model = api.model(
        "NotificationCountResponse",
        {
            "code": fields.Integer(required=True, description="响应码"),
            "message": fields.String(required=True, description="响应消息"),
            "data": fields.Integer(allow_null=True, description="通知数量"),
            "success": fields.Boolean(required=True, description="是否成功"),
        },
    )

    # 未读分组统计响应模型
    unread_group_item_model = api.model(
        "UnreadGroupItem",
        {
            "key": fields.Integer(description="分组键值"),
            "count": fields.Integer(description="数量"),
        },
    )
    notification_unread_group_count_response_model = api.model(
        "NotificationUnreadGroupCountResponse",
        {
            "code": fields.Integer(required=True, description="响应码"),
            "message": fields.String(required=True, description="响应消息"),
            "data": fields.Nested(
                api.model(
                    "NotificationUnreadGroupCountData",
                    {
                        "groupBy": fields.String(description="分组字段"),
                        "items": fields.List(
                            fields.Nested(unread_group_item_model),
                            description="分组列表",
                        ),
                        "total": fields.Integer(description="未读总数"),
                    },
                ),
                allow_null=True,
                description="响应数据",
            ),
            "success": fields.Boolean(required=True, description="是否成功"),
        },
    )

    # 基础响应模型（用于更新操作）
    base_response_model = api.model(
        "BaseResponse",
        {
            "code": fields.Integer(required=True, description="响应码"),
            "message": fields.String(required=True, description="响应消息"),
            "data": fields.Raw(allow_null=True, description="响应数据"),
            "success": fields.Boolean(required=True, description="是否成功"),
        },
    )

    return {
        "notification_model": notification_model,
        "notification_confirm_data_model": notification_confirm_data_model,
        "notification_batch_read_request_model": notification_batch_read_request_model,
        "notification_list_response_model": notification_list_response_model,
        "single_notification_response_model": single_notification_response_model,
        "notification_count_response_model": notification_count_response_model,
        "notification_unread_group_count_response_model": notification_unread_group_count_response_model,
        "base_response_model": base_response_model,
    }
