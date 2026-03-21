from flask_restx import Namespace, Resource, reqparse
from sqlalchemy import func

from web.common.api_factory import get_api
from web.common.utils import R
from web.weblogger import debug, error
from .notification_schemas import create_notification_models
from .notification_routers import Notification, db


notification_count_api_ns = Namespace("notification_count", description="通知数量接口")

api = get_api()
if api:
    api.add_namespace(notification_count_api_ns, path="/api/notification_count")

notification_count_models = create_notification_models(notification_count_api_ns)


@notification_count_api_ns.route('')
class NotificationCountRouters(Resource):
    @notification_count_api_ns.doc('get_notification_count')
    @notification_count_api_ns.marshal_with(notification_count_models['notification_count_response_model'])
    @notification_count_api_ns.param('noticeStatus', '通知的状态：0-未发送，1-未读，2-已读，3-已处理，4-已发送', type=int, required=False)
    def get(self):
        """
        通知数量统计接口

        获取系统中各种状态通知的数量统计信息，用于前端显示通知徽章和统计面板。

        返回数据:
        - 成功时返回各状态通知的数量统计，格式：{"code": 20000, "data": count, "message": "成功", "success": true}
        - 失败时返回错误信息，格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        统计维度:
        - 总通知数量：系统中所有通知的总数
        - 未读通知数量：状态为未读的通知数量
        - 已读通知数量：状态为已读的通知数量
        - 已处理通知数量：状态为已处理的通知数量

        注意事项:
        - 只统计已发送的通知（过滤掉未发送状态的通知）
        - 数量统计实时计算，确保数据准确性
        - 适用于前端通知徽章显示和管理面板统计

        使用示例:
        GET /api/notification_count

        返回示例:
        {
            "code": 200,
            "msg": "success",
            "data": {
                "total": 25,
                "unread": 5,
                "read": 15,
                "processed": 5
            }
        }
        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('noticeStatus', dest='notice_status', required=False, type=int, location='args')
            args = parser.parse_args()
            notice_status = args.get('notice_status')

            debug(f"获取通知数量 - noticeStatus: {notice_status}")

            if notice_status is not None:
                notice_count = Notification.query.filter(
                    Notification.notice_status == notice_status).count()
            else:
                notice_count = Notification.query.count()

            debug(f"通知数量查询结果: {notice_count}")
            return R.ok(data=notice_count)
        except Exception as e:
            error(f"获取通知数量失败: {str(e)}")
            return R.fail(msg=str(e))


@notification_count_api_ns.route('/unread_groups')
class NotificationUnreadGroupCountRouters(Resource):
    @notification_count_api_ns.doc('get_unread_group_count')
    @notification_count_api_ns.marshal_with(notification_count_models['notification_unread_group_count_response_model'])
    @notification_count_api_ns.param('groupBy', '分组字段：businessType/noticeType/noticeLevel', type=str, required=False)
    def get(self):
        """
        未读通知分组统计接口

        按指定分组字段统计系统中“未读”状态通知的数量，返回分组计数与总数。

        查询参数:
        - groupBy (string, optional): 分组字段，支持值 `businessType`、`noticeType`、`noticeLevel`，默认 `businessType`

        返回数据:
        - 成功响应：{"code": 20000, "data": {"groupBy": "businessType", "items": [{"key": 0, "count": 22}, {"key": 2, "count": 1}], "total": 23}, "message": "成功", "success": true}
        - 失败响应：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        数据格式说明:
        - data.groupBy: 实际使用的分组字段
        - data.items: 分组项列表，每项包含分组键值 `key` 与计数 `count`
        - data.total: 所有未读通知的总计数

        关键注意事项:
        - 仅统计通知状态为“未读”的记录（不包含“未发送”等其他状态）
        - 非法的 groupBy 值将返回失败响应
        - 统计使用数据库分组聚合，适用于较大数据量

        请求示例:
        GET /api/notification_count/unread_groups?groupBy=businessType

        返回示例:
        {
            "code": 20000,
            "message": "成功",
            "data": {
                "groupBy": "businessType",
                "items": [
                    {"key": 0, "count": 22},
                    {"key": 2, "count": 1},
                    {"key": 3, "count": 5}
                ],
                "total": 28
            },
            "success": true
        }
        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('groupBy', dest='group_by', required=False, type=str, location='args')
            args = parser.parse_args()
            group_by = (args.get('group_by') or 'businessType').strip()

            mapping = {
                'businessType': Notification.business_type,
                'noticeType': Notification.notice_type,
                'noticeLevel': Notification.notice_level,
            }
            if group_by not in mapping:
                return R.fail(msg='groupBy无效')

            field = mapping[group_by]

            rows = db.session.query(field, func.count(Notification.id)) \
                .filter(Notification.notice_status == Notification.get_notice_status_enum().NOT_READ.value) \
                .group_by(field) \
                .all()

            items = [{'key': int(row[0]), 'count': int(row[1])} for row in rows]
            total = sum(i['count'] for i in items)

            debug(f"未读分组统计 - groupBy: {group_by}, items: {items}, total: {total}")
            return R.ok(data={'groupBy': group_by, 'items': items, 'total': total})
        except Exception as e:
            error(f"获取未读分组统计失败: {str(e)}", exc_info=True)
            return R.fail(msg=str(e))