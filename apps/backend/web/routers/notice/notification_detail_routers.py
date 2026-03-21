from typing import List

from flask_restx import Namespace, Resource

from web.common.api_factory import get_api
from web.common.utils import R
from web.weblogger import debug, error
from .notification_schemas import create_notification_models
from .notification_routers import Notification, NotificationVOSchema, db
from .notification_detail_schemas import NotificationBatchReadBodySchema
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.record.record import Record, RecordListSchema
from web.web_exception import WebBaseException


notification_api_ns = Namespace("notification", description="通知管理接口")

api = get_api()
if api:
    api.add_namespace(notification_api_ns, path="/api/notification")

notification_models = create_notification_models(notification_api_ns)


@notification_api_ns.route('/<int:notification_id>')
class NotificationRouters(Resource):
    @notification_api_ns.doc('get_notification_by_id')
    @notification_api_ns.marshal_with(notification_models['single_notification_response_model'])
    def get(self, notification_id):
        """
        通知详情查询接口

        根据通知ID获取指定通知的详细信息，同时自动处理通知的阅读状态更新。
        主要用于通知详情页面展示和通知内容的完整查看。

        路径参数:
        - notification_id (int, required): 通知的唯一标识ID

        返回数据:
        - 成功时返回通知的完整详细信息，格式：{"code": 20000, "data": {...}, "message": "成功", "success": true}
        - 通知不存在时返回失败响应，格式：{"code": 20500, "data": false, "message": "通知不存在", "success": false}
        - 系统错误时返回错误响应，格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        自动状态更新:
        - 如果通知状态为"未读"，自动更新为"已读"状态
        - 状态更新会立即提交到数据库
        - 其他状态（已读、已处理）保持不变

        通知详情包含:
        - 基础信息：ID、标题、内容、业务类型
        - 状态信息：通知状态、重要性等级
        - 时间信息：创建时间、更新时间
        - 业务数据：相关的业务上下文和处理数据

        业务场景:
        - 用户点击通知列表中的通知项
        - 通知中心的详情查看
        - 通知处理前的信息确认

        注意事项:
        - 通知ID必须存在，否则返回失败响应（非HTTP 404状态码）
        - 状态更新是自动的，无需额外调用
        - 支持所有业务类型的通知详情查看

        使用示例:
        GET /api/notification/123

        返回示例:
        {
            "code": 200,
            "msg": "success",
            "data": {
                "id": 123,
                "title": "网格交易通知",
                "content": "...",
                "businessType": 0,
                "noticeStatus": 1,
                "noticeLevel": 2,
                "timestamp": "2025-01-14T10:30:00",
                "contextData": {...}
            }
        }
        """
        try:
            debug(f"根据ID获取通知 - notification_id: {notification_id}")

            notification = Notification.query.get(notification_id)
            if notification is None:
                error(f"通知不存在 - notification_id: {notification_id}")
                return R.fail(msg="通知不存在")

            if notification.notice_status == notification.get_notice_status_enum().NOT_READ.value:
                notification.notice_status = notification.get_notice_status_enum().READ.value
                db.session.commit()

            result = NotificationVOSchema().dump(notification)

            debug(f"获取通知成功 - notification_id: {notification_id}")
            return R.ok(data=result)
        except Exception as e:
            error(f"根据ID获取通知失败 - notification_id: {notification_id}, error: {str(e)}")
            return R.fail(msg=str(e))

    @notification_api_ns.doc('update_notification_status')
    @notification_api_ns.expect(notification_models['notification_confirm_data_model'])
    @notification_api_ns.marshal_with(notification_models['base_response_model'])
    def put(self, notification_id):
        """
        通知状态更新接口

        确认处理指定通知，将通知状态更新为已处理，并根据通知类型执行相应的业务逻辑处理。
        这是一个复合操作接口，不仅更新通知状态，还会处理相关的业务数据。

        路径参数:
        - notification_id (int, required): 要处理的通知ID

        请求体参数:
        - confirmData (array, required): 确认处理的业务数据列表
          - 对于网格交易通知：包含网格配置变更和交易记录确认
          - 对于其他类型通知：包含相应的业务处理数据

        返回数据:
        - 成功时返回处理确认信息，格式：{"code": 20000, "data": true, "message": "更新成功", "success": true}
        - 通知不存在时抛出WebBaseException异常，返回错误响应
        - 通知已处理时抛出WebBaseException异常，返回错误响应
        - 系统错误时返回错误响应，格式：{"code": 20500, "data": false, "message": "错误信息", "success": false}

        业务处理逻辑:

        网格交易通知处理:
        1. 网格监控位置变更：
           - 根据currentChange数据更新网格类型详情的当前监控位置
           - 将旧的监控位置设为非当前状态
           - 将新的监控位置设为当前状态

        2. 交易记录处理：
           - 解析tradeRecord中的交易数据
           - 创建新的交易记录（Record表）
           - 建立网格类型与交易记录的关联（GridTypeRecord表）
           - 更新网格类型详情的监控类型（异或操作）
           - 处理金额数据的精度转换（乘以1000）

        3. 通知状态更新：
           - 将通知状态更新为"已处理"
           - 提交所有数据库变更

        事务处理:
        - 所有操作在同一事务中执行
        - 任何步骤失败都会回滚所有变更
        - 确保数据一致性和完整性

        前置检查:
        - 验证通知是否存在
        - 验证通知是否已经处理过
        - 验证请求数据格式的正确性

        使用示例:
        PUT /api/notification/123
        {
            "confirmData": [
                {
                    "currentChange": [oldDetailId, newDetailId],
                    "tradeRecord": [
                        {
                            "detailId": {
                                "transactionsPrice": 50.123,
                                "transactionsAmount": 100.0,
                                "transactionsFee": 0.1,
                                "transactionsType": 1
                            }
                        }
                    ]
                }
            ]
        }

        注意事项:
        - 通知处理是不可逆操作，请确认后再执行
        - 交易数据会进行精度处理（乘以1000存储）
        - 支持批量处理多个网格的交易记录
        - 处理失败会自动回滚所有变更
        """
        try:
            debug(f"更新通知状态 - notification_id: {notification_id}")

            payload = notification_api_ns.payload
            confirm_data = payload.get('confirmData', [])

            self.pre_check_notice_confirm(notification_id)

            for grid_record in confirm_data:
                if grid_record.get('currentChange') is not None and len(grid_record.get('currentChange')) == 2:
                    target_gt_detail_id = grid_record.get('currentChange')[1]
                    target_gt_detail: GridTypeDetail = GridTypeDetail.query.get(target_gt_detail_id)
                    GridTypeDetail.query.filter(GridTypeDetail.grid_type_id == target_gt_detail.grid_type_id).update(
                        {GridTypeDetail.is_current: False})
                    target_gt_detail.is_current = True
                if grid_record.get('tradeRecord') is not None and len(grid_record.get('tradeRecord')) > 0:
                    grid_type_detail_ids: List[int] = [int(key) for trade_dict in grid_record.get('tradeRecord') for key in
                                                       trade_dict.keys()]
                    grid_type_details: List[GridTypeDetail] = GridTypeDetail.query \
                        .filter(GridTypeDetail.id.in_(grid_type_detail_ids)).all()
                    for grid_type_detail in grid_type_details:
                        grid_type_detail.monitor_type ^= 1
                    grid_type_detail_id = grid_type_detail_ids[0]
                    grid_type: GridType = db.session.query(GridType) \
                        .join(GridTypeDetail, GridType.id == GridTypeDetail.grid_type_id, isouter=True) \
                        .filter(GridTypeDetail.id == grid_type_detail_id) \
                        .first()
                    trade_records: List[dict] = [record for trade_dict in grid_record.get('tradeRecord') for record in
                                                 trade_dict.values()]
                    trade_records: List[Record] = RecordListSchema().load(trade_records, many=True, partial=True,
                                                                          unknown='EXCLUDE')
                    for trade_record in trade_records:
                        trade_record.asset_id = grid_type.asset_id
                        trade_record.transactions_fee *= 1000
                        trade_record.transactions_price *= 1000
                        trade_record.transactions_amount = abs(trade_record.transactions_amount * 1000)
                    db.session.add_all(trade_records)
                    db.session.flush()
                    grid_type_records: List[GridTypeRecord] = [GridTypeRecord(grid_type_id=grid_type.id,
                                                                              record_id=trade_record.id) for
                                                               trade_record in trade_records]
                    db.session.add_all(grid_type_records)
                    db.session.flush()
            Notification.query.filter(Notification.id == notification_id).update(
                {Notification.notice_status: Notification.get_notice_status_enum().PROCESSED.value})
            db.session.commit()

            debug(f"更新通知状态成功 - notification_id: {notification_id}")
            return R.ok(msg='更新成功')
        except Exception as e:
            db.session.rollback()
            error(f"更新通知状态失败 - notification_id: {notification_id}, error: {str(e)}")
            return R.fail(msg=str(e))

    def _handle_confirm_data(self, notification, confirm_data):
        try:
            if notification.business_type == 0:
                self._handle_grid_confirm(confirm_data)
            elif notification.business_type == 1:
                self._handle_message_confirm(confirm_data)
        except Exception as e:
            raise e

    def _handle_grid_confirm(self, confirm_data):
        for data in confirm_data:
            grid_type_id = data.get('gridTypeId')
            action = data.get('action')
            if grid_type_id and action:
                grid_type = GridType.query.get(grid_type_id)
                if grid_type:
                    if action == 'enable':
                        grid_type.status = 1
                    elif action == 'disable':
                        grid_type.status = 0

    def _handle_message_confirm(self, confirm_data):
        for data in confirm_data:
            record_id = data.get('recordId')
            action = data.get('action')
            if record_id and action:
                record = Record.query.get(record_id)
                if record and action == 'processed':
                    record.status = 'processed'

    def _handle_grid_type_detail_confirm(self, confirm_data):
        for data in confirm_data:
            detail_id = data.get('detailId')
            action = data.get('action')
            if detail_id and action:
                detail = GridTypeDetail.query.get(detail_id)
                if detail:
                    if action == 'enable':
                        detail.status = 1
                    elif action == 'disable':
                        detail.status = 0

    def _handle_grid_type_record_confirm(self, confirm_data):
        for data in confirm_data:
            record_id = data.get('recordId')
            action = data.get('action')
            if record_id and action:
                record = GridTypeRecord.query.get(record_id)
                if record and action == 'processed':
                    record.status = 'processed'

    def pre_check_notice_confirm(self, notification_id: int) -> bool:
        notification = Notification.query.get(notification_id)
        if notification is None:
            raise WebBaseException("通知不存在")
        if notification.notice_status == notification.get_notice_status_enum().PROCESSED.value:
            raise WebBaseException("通知已处理")
        return True


@notification_api_ns.route('/batch_read')
class NotificationBatchReadRouters(Resource):
    @notification_api_ns.doc('batch_read_notifications')
    @notification_api_ns.expect(notification_models['notification_batch_read_request_model'], validate=False)
    @notification_api_ns.marshal_with(notification_models['base_response_model'])
    def put(self):
        """
        批量确认通知为已读接口

        将请求体中提供的通知ID列表中处于“未读”状态的通知批量更新为“已读”，返回成功更新的数量。

        请求体参数:
        - ids (array[int], required): 需要标记为已读的通知ID列表

        返回数据:
        - 成功: {"code": 20000, "data": {"updated": number}, "message": "批量更新成功", "success": true}
        - 失败: {"code": 20500, "data": false, "message": "错误信息", "success": false}

        注意事项:
        - 仅更新处于“未读”状态的通知为“已读”
        - 对不存在或非未读的ID会被忽略，不影响整体事务
        - 大批量处理采用单条SQL批量更新，提升性能

        使用示例:
        PUT /api/notification/batch_read
        {
            "ids": [12, 15, 18]
        }
        """
        try:
            body = NotificationBatchReadBodySchema().load(notification_api_ns.payload or {})
            ids = body.get("ids")
            business_type = body.get("business_type")

            if ids is not None:
                debug(f"批量已读 - ids: {ids}")
                updated = Notification.query \
                    .filter(
                        Notification.id.in_(ids),
                        Notification.notice_status == Notification.get_notice_status_enum().NOT_READ.value,
                    ) \
                    .update(
                        {Notification.notice_status: Notification.get_notice_status_enum().READ.value},
                        synchronize_session=False,
                    )
            elif business_type is not None:
                debug(f"按业务类型批量已读 - businessType: {business_type}")
                updated = Notification.query \
                    .filter(
                        Notification.business_type == business_type,
                        Notification.notice_status == Notification.get_notice_status_enum().NOT_READ.value,
                    ) \
                    .update(
                        {Notification.notice_status: Notification.get_notice_status_enum().READ.value},
                        synchronize_session=False,
                    )
            else:
                return R.fail(msg='ids或businessType至少提供一个')

            db.session.commit()
            debug(f"批量已读成功 - 更新数量: {updated}")
            return R.ok(data={"updated": updated}, msg='批量更新成功')
        except Exception as e:
            db.session.rollback()
            error(f"批量已读失败: {str(e)}", exc_info=True)
            return R.fail(msg=str(e))