from contextlib import nullcontext
from unittest.mock import patch, MagicMock
from datetime import datetime

from web.models.notice.Notification import Notification
from web.scheduler.databox_test_scheduler import (
    test_databox_get_rt as run_databox_get_rt,
    _send_test_failure_notification,
)


class TestDataboxScheduler:
    """DataBox定时任务测试类"""

    @patch('web.scheduler.databox_test_scheduler.scheduler.app')
    @patch('web.scheduler.databox_test_scheduler.databox.get_rt')
    @patch('web.scheduler.databox_test_scheduler.dispatch_notification')
    def test_databox_get_rt_success(self, mock_dispatch_notification, mock_get_rt, mock_app):
        """测试DataBox get_rt功能正常情况"""
        mock_app.app_context.return_value = nullcontext()
        # 模拟成功的返回结果
        mock_result = MagicMock()
        mock_result.name = '平安银行'
        mock_get_rt.return_value = mock_result
        
        # 执行测试
        run_databox_get_rt()
        
        # 验证
        mock_get_rt.assert_called_once_with('SZ162411')
        mock_dispatch_notification.assert_not_called()  # 成功时不应发送通知

    @patch('web.scheduler.databox_test_scheduler.scheduler.app')
    @patch('web.scheduler.databox_test_scheduler.db.session.commit')
    @patch('web.scheduler.databox_test_scheduler.db.session.add')
    @patch('web.scheduler.databox_test_scheduler.databox.get_rt')
    @patch('web.scheduler.databox_test_scheduler.dispatch_notification', return_value=(True, 'actor'))
    def test_databox_get_rt_failure_none_result(self, mock_dispatch_notification, mock_get_rt, mock_add, mock_commit, mock_app):
        """测试DataBox get_rt返回None的情况"""
        mock_app.app_context.return_value = nullcontext()
        # 模拟返回None
        mock_get_rt.return_value = None

        # 执行测试
        run_databox_get_rt()

        # 验证
        mock_get_rt.assert_called_once_with('SZ162411')
        mock_dispatch_notification.assert_called_once()  # 失败时应发送通知

        # 验证通知是否正确创建
        notification = mock_add.call_args[0][0]
        assert notification.business_type == 2  # SYSTEM_RUNNING
        assert notification.notice_type == 0    # INFO_MESSAGE
        assert notification.title == 'DataBox功能测试失败'
        assert '返回结果为 None' in notification.content

    @patch('web.scheduler.databox_test_scheduler.scheduler.app')
    @patch('web.scheduler.databox_test_scheduler.db.session.commit')
    @patch('web.scheduler.databox_test_scheduler.db.session.add')
    @patch('web.scheduler.databox_test_scheduler.databox.get_rt')
    @patch('web.scheduler.databox_test_scheduler.dispatch_notification', return_value=(True, 'sync'))
    def test_databox_get_rt_exception(self, mock_dispatch_notification, mock_get_rt, mock_add, mock_commit, mock_app):
        """测试DataBox get_rt抛出异常的情况"""
        mock_app.app_context.return_value = nullcontext()
        # 模拟抛出异常
        mock_get_rt.side_effect = Exception('网络连接失败')

        # 执行测试
        run_databox_get_rt()

        # 验证
        mock_get_rt.assert_called_once_with('SZ162411')
        mock_dispatch_notification.assert_called_once()  # 异常时应发送通知

        # 验证通知是否正确创建
        notification = mock_add.call_args[0][0]
        assert notification.business_type == 2  # SYSTEM_RUNNING
        assert notification.notice_type == 0    # INFO_MESSAGE
        assert notification.title == 'DataBox功能测试失败'
        assert '网络连接失败' in notification.content

    @patch('web.scheduler.databox_test_scheduler.db.session.commit')
    @patch('web.scheduler.databox_test_scheduler.db.session.add')
    @patch('web.scheduler.databox_test_scheduler.dispatch_notification', return_value=(True, 'actor'))
    def test_send_test_failure_notification(self, mock_dispatch_notification, mock_add, mock_commit):
        """测试发送失败通知功能"""
        error_message = '测试错误信息'

        # 执行测试
        _send_test_failure_notification(error_message)

        # 验证通知是否正确创建
        notification = mock_add.call_args[0][0]

        # 验证通知属性
        assert notification.business_type == 2  # SYSTEM_RUNNING
        assert notification.notice_type == 0    # INFO_MESSAGE
        assert notification.notice_status == 0  # NOT_SENT
        assert notification.title == 'DataBox功能测试失败'
        assert error_message in notification.content
        assert notification.notice_level == 1
        assert isinstance(notification.timestamp, datetime)

        # 验证发送方法被调用
        mock_dispatch_notification.assert_called_once()
        # 验证commit被调用
        mock_commit.assert_called_once()
