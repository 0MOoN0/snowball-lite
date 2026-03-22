import json
from unittest.mock import patch, MagicMock
from web.webtest.test_base import TestBaseWithRollback
from web.models import db
from web.models.notice.Notification import Notification


class TestNotificationRouters(TestBaseWithRollback):
    """通知管理接口测试类"""

    # ==================== 通知数量统计接口测试 ====================

    def test_get_notification_count_success(self, client, session):
        """测试成功获取通知数量统计"""
        # 模拟查询参数
        params = {
            "noticeStatus": "0",  # 未读
            "businessType": "1",  # 交易类型
            "noticeType": "1",  # 系统通知
        }

        response = client.get("/notification_count", query_string=params)

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], int)

    def test_get_notification_count_no_params(self, client, session):
        """测试不传参数的情况（查询所有）"""
        response = client.get("/notification_count")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], int)

    def test_get_notification_count_partial_params(self, client, session):
        """测试部分参数的情况"""
        response = client.get("/notification_count?noticeStatus=0")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert isinstance(data["data"], int)

    @patch("web.routers.notice.notification_routers.Notification.query")
    def test_get_notification_count_database_error(self, mock_query, client, session):
        """测试数据库异常情况"""
        # 模拟数据库异常
        mock_query.count.side_effect = Exception("Database connection error")

        response = client.get("/notification_count")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "Database connection error" in data["message"]

    def test_get_notification_count_empty_result(self, client, session):
        """测试空结果的情况"""
        # 使用不存在的条件查询
        params = {
            "noticeStatus": "999",  # 不存在的状态
            "businessType": "999",  # 不存在的业务类型
        }

        response = client.get("/notification_count", query_string=params)

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert data["data"] == 0

    # ==================== 通知列表查询接口测试 ====================

    def test_get_notification_list_success(self, client, session):
        """测试成功获取通知列表"""
        params = {"page": 1, "pageSize": 10, "noticeStatus": "0", "businessType": "1"}

        response = client.get("/notification_list", query_string=params)

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert "data" in data
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert isinstance(data["data"]["items"], list)
        assert isinstance(data["data"]["total"], int)

    def test_get_notification_list_default_pagination(self, client, session):
        """测试默认分页参数"""
        response = client.get("/notification_list?page=1&pageSize=20")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert len(data["data"]["items"]) <= 20  # 不超过页面大小

    def test_get_notification_list_missing_required_params(self, client, session):
        """测试缺少必需参数"""
        # 缺少page参数
        response = client.get("/notification_list?pageSize=10")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

        # 缺少pageSize参数
        response = client.get("/notification_list?page=1")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

    def test_get_notification_list_invalid_params(self, client, session):
        """测试无效参数"""
        response = client.get("/notification_list?page=invalid&pageSize=10")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

        response = client.get("/notification_list?page=1&pageSize=invalid")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

    @patch("web.routers.notice.notification_routers.Notification.query")
    def test_get_notification_list_database_error(self, mock_query, client, session):
        """测试数据库异常"""
        # 模拟数据库异常
        mock_query.filter.side_effect = Exception("Database error")

        response = client.get("/notification_list?page=1&pageSize=10")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "Database error" in data["message"]

    def test_get_notification_list_large_page(self, client, session):
        """测试大页码的情况"""
        response = client.get("/notification_list?page=9999&pageSize=10")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert data["data"]["items"] == []  # 空列表
        assert data["data"]["total"] >= 0

    # ==================== 通知详情查询接口测试 ====================

    @patch("web.routers.notice.notification_routers.NotificationVOSchema")
    @patch("web.routers.notice.notification_routers.Notification.query")
    @patch("web.routers.notice.notification_routers.db.session")
    def test_get_notification_detail_success(
        self, mock_session, mock_query, mock_schema, client, session
    ):
        """测试成功获取通知详情"""
        # 模拟通知对象
        mock_notification = MagicMock()
        mock_notification.id = 1
        mock_notification.title = "测试通知"
        mock_notification.content = "测试内容"
        mock_notification.notice_status = 0
        # 模拟枚举方法
        mock_enum = MagicMock()
        mock_enum.NOT_READ.value = 0
        mock_enum.READ.value = 1
        mock_notification.get_notice_status_enum.return_value = mock_enum
        mock_notification.to_dict.return_value = {
            "id": 1,
            "title": "测试通知",
            "content": "测试内容",
            "notice_status": 0,
        }

        mock_query.get.return_value = mock_notification

        # 模拟 NotificationVOSchema 的 dump 方法
        mock_schema_instance = MagicMock()
        mock_schema_instance.dump.return_value = {
            "id": 1,
            "title": "测试通知",
            "content": "测试内容",
            "noticeStatus": 0,
        }
        mock_schema.return_value = mock_schema_instance

        response = client.get("/notification/1")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert data["data"]["id"] == 1
        assert data["data"]["title"] == "测试通知"

    @patch("web.routers.notice.notification_routers.Notification.query")
    def test_get_notification_detail_not_found(self, mock_query, client, session):
        """测试通知不存在的情况"""
        mock_query.get.return_value = None

        response = client.get("/notification/999")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "通知不存在" in data["message"]

    @patch("web.routers.notice.notification_routers.Notification.query")
    def test_get_notification_detail_database_error(self, mock_query, client, session):
        """测试数据库异常"""
        mock_query.get.side_effect = Exception("Database error")

        response = client.get("/notification/1")

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "Database error" in data["message"]

    # ==================== 通知状态更新接口测试 ====================

    @patch("web.routers.notice.notification_routers.Notification.query")
    @patch("web.routers.notice.notification_routers.db.session")
    def test_update_notification_status_success(
        self, mock_session, mock_query, client, session
    ):
        """测试成功更新通知状态"""
        # 模拟通知对象
        mock_notification = MagicMock()
        mock_notification.id = 1
        mock_notification.notice_status = 0
        # 模拟枚举方法
        mock_enum = MagicMock()
        mock_enum.PROCESSED.value = 1
        mock_notification.get_notice_status_enum.return_value = mock_enum
        mock_query.get.return_value = mock_notification

        # 请求数据
        request_data = {"confirmData": []}

        response = client.put(
            "/notification/1",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert data["message"] == "更新成功"

    @patch("web.routers.notice.notification_routers.Notification.query")
    def test_update_notification_status_not_found(self, mock_query, client, session):
        """测试通知不存在的情况"""
        mock_query.get.return_value = None

        request_data = {"confirmData": []}

        response = client.put(
            "/notification/999",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "通知不存在" in data["message"]

    @patch("web.routers.notice.notification_routers.Notification.query")
    def test_update_notification_status_already_processed(
        self, mock_query, client, session
    ):
        """测试通知已处理的情况"""
        # 模拟已处理的通知
        mock_notification = MagicMock()
        mock_notification.notice_status = 3  # 已处理状态
        # 模拟枚举方法
        mock_enum = MagicMock()
        mock_enum.PROCESSED.value = 3
        mock_notification.get_notice_status_enum.return_value = mock_enum
        mock_query.get.return_value = mock_notification

        request_data = {"confirmData": []}

        response = client.put(
            "/notification/1",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "通知已处理" in data["message"]

    def test_update_notification_status_missing_data(self, client, session):
        """测试缺少请求体数据"""
        response = client.put("/notification/1")

        # 验证响应 - 全局错误处理器会返回统一格式
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

    def test_update_notification_status_invalid_json(self, client, session):
        """测试无效的JSON数据"""
        response = client.put(
            "/notification/1", data="invalid json", content_type="application/json"
        )

        # 验证响应 - 全局错误处理器会返回统一格式
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

    def test_update_notification_missing_confirm_data(self, client, session):
        """测试缺少confirmData字段"""
        request_data = {"otherField": "value"}

        response = client.put(
            "/notification/1",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

    @patch("web.routers.notice.notification_routers.Notification.query")
    @patch("web.routers.notice.notification_routers.db.session")
    def test_update_notification_status_database_error(
        self, mock_session, mock_query, client, session
    ):
        """测试数据库异常"""
        # 模拟通知对象
        mock_notification = MagicMock()
        mock_notification.notice_status = 0
        mock_query.get.return_value = mock_notification

        # 模拟数据库异常
        mock_session.commit.side_effect = Exception("Database error")

        request_data = {"confirmData": []}

        response = client.put(
            "/notification/1",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "Database error" in data["message"]

        # 验证回滚被调用
        mock_session.rollback.assert_called_once()

    # ==================== 未读分组统计接口测试 ====================

    @patch("web.routers.notice.notification_routers.db.session")
    def test_get_unread_group_count_success(self, mock_session, client, session):
        query_mock = MagicMock()
        group_by_mock = MagicMock()
        group_by_mock.all.return_value = [(0, 5), (1, 3)]
        group_by_mock.group_by.return_value = group_by_mock
        query_mock.filter.return_value = group_by_mock
        mock_session.query.return_value = query_mock

        response = client.get("/notification_count/unread_groups?groupBy=businessType")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert data["data"]["total"] == 8
        assert len(data["data"]["items"]) == 2
        assert data["data"]["groupBy"] == "businessType"
        assert set(data["data"]["items"][0].keys()) == {"key", "count"}

    def test_get_unread_group_count_invalid_group_by(self, client, session):
        response = client.get("/notification_count/unread_groups?groupBy=invalid")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

    @patch("web.routers.notice.notification_routers.db.session")
    def test_get_unread_group_count_database_error(self, mock_session, client, session):
        query_mock = MagicMock()
        group_by_mock = MagicMock()
        group_by_mock.group_by.return_value = group_by_mock
        group_by_mock.all.side_effect = Exception("Database error")
        query_mock.filter.return_value = group_by_mock
        mock_session.query.return_value = query_mock

        response = client.get("/notification_count/unread_groups")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "Database error" in data["message"]
    # ==================== 批量已读接口测试 ====================

    @patch("web.routers.notice.notification_detail_routers.Notification")
    @patch("web.routers.notice.notification_detail_routers.db.session")
    def test_batch_read_success(self, mock_session, mock_notification, client, session):
        """测试批量将未读通知更新为已读成功"""
        mock_query = MagicMock()
        mock_filter_result = MagicMock()
        mock_filter_result.update.return_value = 3
        mock_query.filter.return_value = mock_filter_result
        mock_notification.query = mock_query

        request_data = {"ids": [12, 15, 18]}
        response = client.put(
            "/notification/batch_read",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert data["data"]["updated"] == 3
        mock_session.commit.assert_called_once()

    def test_batch_read_invalid_ids(self, client, session):
        """测试无效或空的ids参数"""
        response = client.put(
            "/notification/batch_read",
            data=json.dumps({"ids": []}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

        response = client.put(
            "/notification/batch_read",
            data=json.dumps({"ids": ["abc"]}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False

    @patch("web.routers.notice.notification_detail_routers.Notification")
    @patch("web.routers.notice.notification_detail_routers.db.session")
    def test_batch_read_database_error(self, mock_session, mock_notification, client, session):
        """测试批量更新数据库异常"""
        mock_query = MagicMock()
        mock_filter_result = MagicMock()
        mock_filter_result.update.side_effect = Exception("Database error")
        mock_query.filter.return_value = mock_filter_result
        mock_notification.query = mock_query

        request_data = {"ids": [1, 2]}
        response = client.put(
            "/notification/batch_read",
            data=json.dumps(request_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is False
        assert "Database error" in data["message"]
        mock_session.rollback.assert_called_once()

    def test_batch_read_by_business_type_db(self, client):
        grid_bt = Notification.get_business_type_enum().GRID_TRADE.value
        sys_bt = Notification.get_business_type_enum().SYSTEM_RUNNING.value
        not_read = Notification.get_notice_status_enum().NOT_READ.value
        read = Notification.get_notice_status_enum().READ.value

        n1 = Notification(business_type=grid_bt, notice_type=0, notice_status=not_read, title='t1')
        n2 = Notification(business_type=grid_bt, notice_type=0, notice_status=not_read, title='t2')
        n3 = Notification(business_type=sys_bt, notice_type=0, notice_status=not_read, title='t3')
        n4 = Notification(business_type=sys_bt, notice_type=0, notice_status=read, title='t4')
        db.session.add_all([n1, n2, n3, n4])
        db.session.flush()

        resp = client.put(
            "/notification/batch_read",
            data=json.dumps({"businessType": grid_bt}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["code"] == 20000
        assert data["success"] is True
        assert data["data"]["updated"] == 2

        rows = db.session.query(Notification).filter(Notification.business_type == grid_bt).all()
        assert all(r.notice_status == read for r in rows)
        other_rows = db.session.query(Notification).filter(Notification.business_type == sys_bt).all()
        assert any(r.notice_status == not_read for r in other_rows)


if __name__ == "__main__":
    # 运行测试的命令示例：
    # pytest web/webtest/routers/notice/test_notification_routers.py -v
    # pytest web/webtest/routers/notice/test_notification_routers.py::TestNotificationRouters::test_get_notification_count_success -v
    pass
