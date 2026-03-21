import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from web.models import db
from web.models.asset.asset_code import AssetCode
from web.models.notice.Notification import Notification
from web.scheduler.databox_test_scheduler import test_databox_get_rt, _send_test_failure_notification
from web.webtest.test_base import TestBaseWithRollback


@pytest.mark.parametrize('app', ['test'], indirect=True)
class TestDataboxScheduler(TestBaseWithRollback):
    """DataBox定时任务测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, rollback_session):
        """为每个测试方法设置测试数据"""
        # 直接创建测试用的AssetCode数据
        self.test_asset_code = AssetCode(
            asset_id=1,
            code_xq='SZ000001',
            code_ttjj='000001',
            code_index='000001'
        )
        rollback_session.add(self.test_asset_code)
        rollback_session.flush()  # 使用flush代替commit，保持在同一事务中

    @patch('web.scheduler.databox_test_scheduler.databox.get_rt')
    @patch('web.scheduler.databox_test_scheduler.NotificationActors.send_notification')
    def test_databox_get_rt_success(self, mock_send_notification, mock_get_rt):
        """测试DataBox get_rt功能正常情况"""
        # 模拟成功的返回结果
        mock_result = MagicMock()
        mock_result.name = '平安银行'
        mock_get_rt.return_value = mock_result
        
        # 执行测试
        test_databox_get_rt()
        
        # 验证
        mock_get_rt.assert_called_once_with('SZ000001')
        mock_send_notification.send.assert_not_called()  # 成功时不应发送通知

    @patch('web.scheduler.databox_test_scheduler.db.session.commit')
    @patch('web.scheduler.databox_test_scheduler.databox.get_rt')
    @patch('web.scheduler.databox_test_scheduler.NotificationActors.send_notification')
    def test_databox_get_rt_failure_none_result(self, mock_send_notification, mock_get_rt, mock_commit, rollback_session):
        """测试DataBox get_rt返回None的情况"""
        # 模拟返回None
        mock_get_rt.return_value = None
        
        # 执行测试
        test_databox_get_rt()
        
        # 验证
        mock_get_rt.assert_called_once_with('SZ000001')
        mock_send_notification.send.assert_called_once()  # 失败时应发送通知
        
        # 验证通知是否正确创建
        notifications = rollback_session.query(Notification).all()
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.business_type == 2  # SYSTEM_RUNNING
        assert notification.notice_type == 0    # INFO_MESSAGE
        assert notification.title == 'DataBox功能测试失败'
        assert '返回结果为None' in notification.content

    @patch('web.scheduler.databox_test_scheduler.db.session.commit')
    @patch('web.scheduler.databox_test_scheduler.databox.get_rt')
    @patch('web.scheduler.databox_test_scheduler.NotificationActors.send_notification')
    def test_databox_get_rt_exception(self, mock_send_notification, mock_get_rt, mock_commit, rollback_session):
        """测试DataBox get_rt抛出异常的情况"""
        # 模拟抛出异常
        mock_get_rt.side_effect = Exception('网络连接失败')
        
        # 执行测试
        test_databox_get_rt()
        
        # 验证
        mock_get_rt.assert_called_once_with('SZ000001')
        mock_send_notification.send.assert_called_once()  # 异常时应发送通知
        
        # 验证通知是否正确创建
        notifications = rollback_session.query(Notification).all()
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.business_type == 2  # SYSTEM_RUNNING
        assert notification.notice_type == 0    # INFO_MESSAGE
        assert notification.title == 'DataBox功能测试失败'
        assert '网络连接失败' in notification.content

    @patch('web.scheduler.databox_test_scheduler.NotificationActors.send_notification')
    def test_databox_get_rt_no_asset_codes(self, mock_send_notification, rollback_session):
        """测试没有AssetCode数据的情况"""
        # 清空AssetCode数据
        rollback_session.query(AssetCode).delete()
        rollback_session.flush()
        
        # 执行测试
        test_databox_get_rt()
        
        # 验证应发送通知
        mock_send_notification.send.assert_called_once()
        
        # 验证通知内容
        notifications = rollback_session.query(Notification).all()
        assert len(notifications) == 1
        notification = notifications[0]
        assert '没有找到有效的AssetCode数据' in notification.content

    @patch('web.scheduler.databox_test_scheduler.db.session.commit')
    @patch('web.scheduler.databox_test_scheduler.NotificationActors.send_notification')
    def test_send_test_failure_notification(self, mock_send_notification, mock_commit, rollback_session):
        """测试发送失败通知功能"""
        error_message = '测试错误信息'
        
        # 执行测试
        _send_test_failure_notification(error_message)
        
        # 验证通知是否正确创建
        notifications = rollback_session.query(Notification).all()
        assert len(notifications) == 1
        notification = notifications[0]
        
        # 验证通知属性
        assert notification.business_type == 2  # SYSTEM_RUNNING
        assert notification.notice_type == 0    # INFO_MESSAGE
        assert notification.notice_status == 0  # NOT_SENT
        assert notification.title == 'DataBox功能测试失败'
        assert error_message in notification.content
        assert notification.notice_level == 1
        assert isinstance(notification.timestamp, datetime)
        
        # 验证actors发送方法被调用
        mock_send_notification.send.assert_called_once()
        # 验证commit被调用
        mock_commit.assert_called_once()

    @patch('web.scheduler.databox_test_scheduler.db.session.commit')
    @patch('web.scheduler.databox_test_scheduler.random.choice')
    @patch('web.scheduler.databox_test_scheduler.databox.get_rt')
    def test_random_asset_code_selection(self, mock_get_rt, mock_choice, mock_commit, rollback_session):
        """测试随机选择AssetCode的功能"""
        # 添加测试数据
        asset_code2 = AssetCode(
            asset_id=2,
            code_xq='SH600000',
            code_ttjj='600000',
            code_index='600000'
        )
        rollback_session.add(asset_code2)
        rollback_session.flush()
        
        # 模拟random.choice返回第二个AssetCode
        mock_choice.return_value = asset_code2
        mock_get_rt.return_value = MagicMock(name='浦发银行')
        
        # 执行测试
        test_databox_get_rt()
        
        # 验证random.choice被调用
        mock_choice.assert_called_once()
        # 验证使用了正确的代码
        mock_get_rt.assert_called_once_with('SH600000')