#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    ：test_notification_actors.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025-01-14
@Description: NotificationActors测试用例
包含发送通知的各种场景测试：成功发送、失败重试、多渠道发送等
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from web.models.notice.Notification import Notification, NotificationSchema
from web.models.notice.notification_log import NotificationLog
from web.task.actors.NotificationActors import send_notification
from web.webtest.test_base import TestBaseWithRollback
from web.common.cons import webcons
from web.models import db


@pytest.mark.usefixtures("rollback_session")
class TestNotificationActors(TestBaseWithRollback):
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建测试用的通知对象
        self.test_notification_content = {
            "title": "测试网格交易通知",
            "content": "这是一个测试通知内容",
            "grid_info": [
                {
                    "asset_name": "测试ETF",
                    "grid_type_name": "小网",
                    "trade_list": [],
                    "current_change": []
                }
            ]
        }
        
    def create_test_notification(self, rollback_session):
        """创建测试通知对象"""
        notification = Notification(
            title="测试通知标题",
            content=json.dumps(self.test_notification_content),
            notice_level=0,
            business_type=Notification.get_business_type_enum().GRID_TRADE.value,
            notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value,
            notice_status=Notification.get_notice_status_enum().NOT_SENT.value,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        rollback_session.add(notification)
        rollback_session.commit()
        return notification
    
    @patch('web.task.actors.NotificationActors.notification_service')
    @patch('web.task.actors.NotificationActors.debug')
    def test_send_notification_success_single_channel(self, mock_debug, mock_notification_service, rollback_session):
        """测试单渠道发送成功场景"""
        # 准备测试数据
        notification = self.create_test_notification(rollback_session)
        notification_json = NotificationSchema().dumps(notification)
        
        # 模拟发送上下文
        mock_sender_context = Mock()
        mock_sender_context.send.return_value = None  # 发送成功
        mock_notification_service.get_sender_contexts_for_business.return_value = [mock_sender_context]
        
        # 执行测试
        send_notification(notification_json)
        
        # 验证结果
        rollback_session.refresh(notification)
        assert notification.notice_status == Notification.get_notice_status_enum().NOT_READ.value
        assert notification.timestamp is not None
        
        # 验证调用
        mock_notification_service.get_sender_contexts_for_business.assert_called_once_with(notification.business_type)
        # 验证 send 方法被调用，并且传入的通知对象具有相同的 ID
        mock_sender_context.send.assert_called_once()
        called_notification = mock_sender_context.send.call_args[0][0]
        assert called_notification.id == notification.id
        
        # 验证日志调用
        assert mock_debug.call_count >= 3  # 至少包含进入方法、获取对象、发送成功的日志
    
    @patch('web.task.actors.NotificationActors.debug')
    @patch('web.task.actors.NotificationActors.notification_service')
    def test_send_notification_success_multiple_channels(self, mock_notification_service, mock_debug, rollback_session):
        """测试多渠道发送成功场景"""
        # 准备测试数据
        notification = self.create_test_notification(rollback_session)
        notification_json = NotificationSchema().dumps(notification)
        
        # 模拟多个发送上下文
        mock_sender_context1 = Mock()
        mock_sender_context1.send.return_value = None
        mock_sender_context2 = Mock()
        mock_sender_context2.send.return_value = None
        mock_notification_service.get_sender_contexts_for_business.return_value = [mock_sender_context1, mock_sender_context2]
        
        # 执行测试
        send_notification(notification_json)
        
        # 验证结果
        rollback_session.refresh(notification)
        assert notification.notice_status == Notification.get_notice_status_enum().NOT_READ.value
        assert notification.timestamp is not None
        
        # 验证所有渠道都被调用，并且传入的通知对象具有相同的 ID
        mock_sender_context1.send.assert_called_once()
        called_notification1 = mock_sender_context1.send.call_args[0][0]
        assert called_notification1.id == notification.id
        
        mock_sender_context2.send.assert_called_once()
        called_notification2 = mock_sender_context2.send.call_args[0][0]
        assert called_notification2.id == notification.id
    
    @patch('web.task.actors.NotificationActors.notification_service')
    @patch('web.task.actors.NotificationActors.error')
    @patch('web.task.actors.NotificationActors.debug')
    def test_send_notification_single_channel_retry_then_success(self, mock_debug, mock_error, mock_notification_service, rollback_session):
        """测试单渠道重试后成功场景"""
        # 准备测试数据
        notification = self.create_test_notification(rollback_session)
        notification_json = NotificationSchema().dumps(notification)
        
        # 模拟发送上下文：第一次失败，第二次成功
        mock_sender_context = Mock()
        mock_sender_context.send.side_effect = [Exception("发送失败"), None]
        mock_notification_service.get_sender_contexts_for_business.return_value = [mock_sender_context]
        
        # 执行测试
        send_notification(notification_json)
        
        # 验证结果
        rollback_session.refresh(notification)
        assert notification.notice_status == Notification.get_notice_status_enum().NOT_READ.value
        assert notification.timestamp is not None
        
        # 验证重试调用
        assert mock_sender_context.send.call_count == 2
        
        # 验证错误日志被调用
        mock_error.assert_called()
        
        # 验证通知日志被记录
        log_count = rollback_session.query(NotificationLog).filter(
            NotificationLog.notification_id == notification.id
        ).count()
        assert log_count == 1  # 一次失败记录
    
    @patch('web.task.actors.NotificationActors.notification_service')
    @patch('web.task.actors.NotificationActors.error')
    @patch('web.task.actors.NotificationActors.debug')
    def test_send_notification_partial_channel_success(self, mock_debug, mock_error, mock_notification_service, rollback_session):
        """测试部分渠道成功场景"""
        # 准备测试数据
        notification = self.create_test_notification(rollback_session)
        notification_json = NotificationSchema().dumps(notification)
        
        # 模拟多个发送上下文：第一个成功，第二个失败
        mock_sender_context1 = Mock()
        mock_sender_context1.send.return_value = None  # 成功
        mock_sender_context2 = Mock()
        mock_sender_context2.send.side_effect = Exception("发送失败")  # 失败
        mock_notification_service.get_sender_contexts_for_business.return_value = [mock_sender_context1, mock_sender_context2]
        
        # 执行测试
        send_notification(notification_json)
        
        # 验证结果：只要有一个渠道成功，通知状态就应该更新
        rollback_session.refresh(notification)
        assert notification.notice_status == Notification.get_notice_status_enum().NOT_READ.value
        assert notification.timestamp is not None
        
        # 验证第二个渠道重试了最大次数
        assert mock_sender_context2.send.call_count == 4  # 初始1次 + 3次重试
    
    @patch('web.task.actors.NotificationActors.notification_service')
    @patch('web.task.actors.NotificationActors.error')
    @patch('web.task.actors.NotificationActors.debug')
    def test_send_notification_all_channels_fail_with_global_retry(self, mock_debug, mock_error, mock_notification_service, rollback_session):
        """测试所有渠道失败且触发全局重试场景"""
        # 准备测试数据
        notification = self.create_test_notification(rollback_session)
        notification_json = NotificationSchema().dumps(notification)
        
        # 模拟发送上下文：所有渠道都失败
        mock_sender_context = Mock()
        mock_sender_context.send.side_effect = Exception("发送失败")
        mock_notification_service.get_sender_contexts_for_business.return_value = [mock_sender_context]
        
        # 模拟全局重试次数未达到上限
        with patch('web.common.cons.webcons.NOTIFICATION_GLOBAL_MAX_RETRY', 5):
            # Mock send_with_options 方法
            with patch.object(send_notification, 'send_with_options') as mock_send_with_options:
                # 执行测试
                send_notification(notification_json)
                
                # 验证结果：通知状态不应该更新
                rollback_session.refresh(notification)
                assert notification.notice_status == Notification.get_notice_status_enum().NOT_SENT.value
                
                # 验证延时重试被调用
                mock_send_with_options.assert_called_once()
                
                # 验证通知日志被记录
                log_count = rollback_session.query(NotificationLog).filter(
                    NotificationLog.notification_id == notification.id
                ).count()
                assert log_count == 4  # 4次失败记录（初始1次 + 3次重试）
    
    @patch('web.task.actors.NotificationActors.notification_service')
    @patch('web.task.actors.NotificationActors.error')
    @patch('web.task.actors.NotificationActors.debug')
    def test_send_notification_all_channels_fail_max_global_retry(self, mock_notification_service, mock_error, mock_debug, rollback_session):
        """测试所有渠道失败且达到全局最大重试次数场景"""
        # 准备测试数据
        notification = self.create_test_notification(rollback_session)
        notification_json = NotificationSchema().dumps(notification)
        
        # 预先创建足够的失败日志，模拟已达到全局最大重试次数
        for i in range(webcons.NOTIFICATION_GLOBAL_MAX_RETRY):
            log = NotificationLog(
                notification_id=notification.id,
                traceback_info=f"模拟失败日志 {i+1}"
            )
            rollback_session.add(log)
        rollback_session.commit()
        
        # 模拟发送上下文：所有渠道都失败
        mock_sender_context = Mock()
        mock_sender_context.send.side_effect = Exception("发送失败")
        mock_notification_service.get_sender_contexts_for_business.return_value = [mock_sender_context]
        
        # 执行测试
        send_notification(notification_json)
        
        # 验证结果：通知状态不应该更新
        rollback_session.refresh(notification)
        assert notification.notice_status == Notification.get_notice_status_enum().NOT_SENT.value
        
        # 验证错误日志包含"已达到全局最大重试次数"
        error_calls = [call for call in mock_error.call_args_list if "已达到全局最大重试次数" in str(call)]
        assert len(error_calls) > 0
    
    @patch('web.task.actors.NotificationActors.notification_service')
    @patch('web.task.actors.NotificationActors.debug')
    def test_send_notification_with_invalid_json(self, mock_notification_service, mock_debug):
        """测试无效JSON输入场景"""
        # 准备无效的JSON字符串
        invalid_json = "invalid json string"
        
        # 执行测试，应该抛出异常
        with pytest.raises(Exception):
            send_notification(invalid_json)
    
    @patch('web.task.actors.NotificationActors.notification_service')
    @patch('web.task.actors.NotificationActors.debug')
    def test_send_notification_with_empty_sender_contexts(self, mock_notification_service, mock_debug, rollback_session):
        """测试没有可用发送渠道的场景"""
        # 准备测试数据
        notification = self.create_test_notification(rollback_session)
        notification_json = NotificationSchema().dumps(notification)
        
        # 模拟没有可用的发送上下文
        mock_notification_service.get_sender_contexts_for_business.return_value = []
        
        # 执行测试
        send_notification(notification_json)
        
        # 验证结果：由于没有渠道，success_count为0，应该触发全局重试逻辑
        rollback_session.refresh(notification)
        assert notification.notice_status == Notification.get_notice_status_enum().NOT_SENT.value
    
    @patch('web.task.actors.NotificationActors.notification_service')
    @patch('web.task.actors.NotificationActors.debug')
    @patch('web.task.actors.NotificationActors.traceback.format_exc')
    def test_send_notification_traceback_logging(self, mock_format_exc, mock_debug, mock_notification_service, rollback_session):
        """测试异常堆栈信息记录"""
        # 准备测试数据
        notification = self.create_test_notification(rollback_session)
        notification_json = NotificationSchema().dumps(notification)
        
        # 模拟异常和堆栈信息
        test_exception = Exception("测试异常")
        test_traceback = "测试堆栈信息\nline 1\nline 2"
        mock_format_exc.return_value = test_traceback
        
        # 模拟发送上下文失败
        mock_sender_context = Mock()
        mock_sender_context.send.side_effect = test_exception
        mock_notification_service.get_sender_contexts_for_business.return_value = [mock_sender_context]
        
        # 执行测试
        send_notification(notification_json)
        
        # 验证堆栈信息被正确记录
        notification_logs = rollback_session.query(NotificationLog).filter(
            NotificationLog.notification_id == notification.id
        ).all()
        
        assert len(notification_logs) == 4  # 4次失败记录
        for log in notification_logs:
            assert test_traceback in log.traceback_info
            assert "渠道1第" in log.traceback_info  # 验证渠道和重试次数信息
    
    @patch('web.task.actors.NotificationActors.notification_service')
    @patch('web.task.actors.NotificationActors.debug')
    def test_send_notification_timestamp_update(self, mock_debug, mock_notification_service, rollback_session):
        """测试时间戳更新"""
        # 准备测试数据
        notification = self.create_test_notification(rollback_session)
        notification_json = NotificationSchema().dumps(notification)
        
        # 模拟发送成功
        mock_sender_context = Mock()
        mock_sender_context.send.return_value = None
        mock_notification_service.get_sender_contexts_for_business.return_value = [mock_sender_context]
        
        # 记录执行前的时间戳
        before_timestamp = notification.timestamp
        
        # 执行测试
        send_notification(notification_json)
        
        # 验证时间戳被更新
        rollback_session.refresh(notification)
        assert notification.timestamp is not None
        assert notification.timestamp != before_timestamp