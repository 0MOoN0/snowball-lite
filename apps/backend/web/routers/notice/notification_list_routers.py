from flask_restx import Namespace, Resource
from flask import request

from web.common.api_factory import get_api
from web.common.utils import R
from web.weblogger import debug, error
from .notification_schemas import create_notification_models
from .notification_routers import Notification, NotificationVOSchema
from .notification_list_schemas import NotificationListQueryArgsSchema


notification_list_api_ns = Namespace("notification_list", description="通知列表接口")

api = get_api()
if api:
    api.add_namespace(notification_list_api_ns, path="/api/notification_list")

notification_list_models = create_notification_models(notification_list_api_ns)


@notification_list_api_ns.route('')
class NotificationListRouters(Resource):
    @notification_list_api_ns.doc('get_notification_list')
    @notification_list_api_ns.marshal_with(notification_list_models['notification_list_response_model'])
    @notification_list_api_ns.param('page', '页码', type=int, required=True)
    @notification_list_api_ns.param('pageSize', '每页大小', type=int, required=True)
    @notification_list_api_ns.param('businessType', '业务类型', type=int, required=False)
    def get(self):
        """
        通知列表查询接口

        获取系统通知列表，支持分页查询，按照特定规则排序显示。
        主要用于通知管理页面和通知中心的列表展示。

        查询参数:
        - page (int, optional): 页码，默认为1
        - pageSize (int, optional): 每页大小，默认为10，最大100
        - businessType (int, optional): 业务类型枚举，按类型过滤

        返回数据:
        - 成功时返回分页数据，格式：{"code": 20000, "data": {"items": [...], "total": number}, "message": "成功", "success": true}
        - 失败时返回错误信息，格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        排序规则:
        1. 通知重要性等级（降序）：高重要性通知优先显示
        2. 通知时间（降序）：最新通知优先显示
        3. 通知状态（升序）：未读状态优先显示

        过滤规则:
        - 只显示已发送的通知（过滤掉未发送状态的通知）
        - 包含所有业务类型的通知（网格交易、消息提醒等）

        通知信息包含:
        - 通知ID、标题、内容、业务类型
        - 通知状态、重要性等级、创建时间
        - 业务相关的上下文数据

        使用示例:
        - 获取第一页：GET /api/notification_list?page=1&pageSize=10
        - 业务类型过滤：GET /api/notification_list?page=1&pageSize=10&businessType=0

        返回示例:
        {
            "code": 200,
            "msg": "success",
            "data": {
                "items": [...],
                "total": 25
            }
        }
        """
        try:
            args = NotificationListQueryArgsSchema().load(request.args.to_dict())
            page = args.get('page')
            page_size = args.get('page_size')
            business_type = args.get('business_type')

            debug(f"获取通知列表 - page: {page}, pageSize: {page_size}")

            query = Notification.query \
                .filter(Notification.notice_status > Notification.get_notice_status_enum().NOT_SENT.value)
            if business_type is not None:
                query = query.filter(Notification.business_type == business_type)
            notifications = query \
                .order_by(Notification.notice_level.desc(), Notification.timestamp.desc(), Notification.notice_status.asc()) \
                .paginate(page=page, per_page=page_size, error_out=False)

            result = NotificationVOSchema().dump(notifications.items, many=True)

            debug(f"通知列表查询结果 - 总数: {notifications.total}, 当前页数据量: {len(result)}")
            return R.ok(data={"items": result, "total": notifications.total})
        except Exception as e:
            error(f"获取通知列表失败: {str(e)}")
            return R.fail(msg=str(e))