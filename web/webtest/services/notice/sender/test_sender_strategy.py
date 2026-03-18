# -*- coding: UTF-8 -*-
"""
@File    ：TestSenderStrategy.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/12/19 10:00
@Description: 通知发送策略测试用例
包含Mock测试（默认）和可选的真实发送测试
"""
import pytest
import json
import os
from unittest.mock import Mock, patch, AsyncMock
from web.models.notice.Notification import Notification
from web.services.notice.sender.sender_strategy import (
    ServerChenSenderStrategy, 
    TelegramBotSenderStrategy, 
    PushPlusSenderStrategy,
    WeComSenderStrategy,
    SenderContext
)
from web.webtest.test_base import TestBase


@pytest.mark.usefixtures("rollback_session")
class TestSenderStrategy(TestBase):
    
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
            notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value
        )
        rollback_session.add(notification)
        rollback_session.flush()
        return notification

    @patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key')
    @patch('web.services.notice.sender.sender_strategy.requests.post')
    def test_server_chan_send_success(self, mock_post, mock_get_setting, rollback_session):
        """测试Server酱发送成功"""
        # 模拟配置获取
        mock_get_setting.return_value = "test_sendkey_123"
        
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'errno': 0}
        }
        mock_post.return_value = mock_response
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 执行测试
        strategy = ServerChenSenderStrategy()
        strategy.send(notification)
        
        # 验证调用
        mock_get_setting.assert_called_once_with("notification_sender.server_chan")
        mock_post.assert_called_once()
        
        # 验证请求参数
        call_args = mock_post.call_args
        assert 'https://sctapi.ftqq.com/test_sendkey_123.send' in call_args[1]['url']
        assert 'text' in call_args[1]['data']
        assert 'desp' in call_args[1]['data']

    @patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key')
    def test_server_chan_send_no_config(self, mock_get_setting, rollback_session):
        """测试Server酱配置为空的情况"""
        # 模拟配置为空
        mock_get_setting.return_value = None
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 执行测试并验证异常
        strategy = ServerChenSenderStrategy()
        with pytest.raises(Exception) as exc_info:
            strategy.send(notification)
        
        assert "Server酱 sendkey 配置为空" in str(exc_info.value)

    @patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key')
    @patch('web.services.notice.sender.sender_strategy.requests.post')
    def test_server_chan_send_api_error(self, mock_post, mock_get_setting, rollback_session):
        """测试Server酱API返回错误"""
        # 模拟配置获取
        mock_get_setting.return_value = "test_sendkey_123"
        
        # 模拟HTTP错误响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'errno': 1, 'errmsg': 'API错误'}
        }
        mock_post.return_value = mock_response
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 执行测试（不应该抛出异常，但会记录错误日志）
        strategy = ServerChenSenderStrategy()
        strategy.send(notification)  # 这里不会抛出异常，只是记录日志

    @patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key')
    @patch('web.services.notice.sender.sender_strategy.asyncio.run')
    def test_telegram_bot_send_success(self, mock_asyncio_run, mock_get_setting, rollback_session):
        """测试Telegram Bot发送成功"""
        # 模拟配置获取
        telegram_config = {
            "token": "test_bot_token",
            "chat_id": "test_chat_id"
        }
        mock_get_setting.return_value = json.dumps(telegram_config)
        
        # 模拟异步调用结果
        mock_asyncio_run.return_value = Mock()
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 执行测试
        strategy = TelegramBotSenderStrategy()
        result = strategy.send(notification)
        
        # 验证调用
        mock_get_setting.assert_called_once_with("notification_sender.telegram_bot")
        mock_asyncio_run.assert_called_once()

    @patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key')
    def test_telegram_bot_send_no_config(self, mock_get_setting, rollback_session):
        """测试Telegram Bot配置为空的情况"""
        # 模拟配置为空
        mock_get_setting.return_value = None
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 执行测试并验证异常
        strategy = TelegramBotSenderStrategy()
        with pytest.raises(Exception) as exc_info:
            strategy.send(notification)
        
        assert "Telegram Bot 配置为空" in str(exc_info.value)

    @patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key')
    def test_telegram_bot_send_invalid_json(self, mock_get_setting, rollback_session):
        """测试Telegram Bot配置JSON格式错误"""
        # 模拟无效的JSON配置
        mock_get_setting.return_value = "invalid json string"
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 执行测试并验证异常
        strategy = TelegramBotSenderStrategy()
        with pytest.raises(Exception) as exc_info:
            strategy.send(notification)
        
        assert "Telegram Bot 配置JSON格式错误" in str(exc_info.value)

    @patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key')
    def test_telegram_bot_send_missing_fields(self, mock_get_setting, rollback_session):
        """测试Telegram Bot配置缺少必要字段"""
        # 模拟缺少字段的配置
        telegram_config = {"token": "test_token"}  # 缺少chat_id
        mock_get_setting.return_value = json.dumps(telegram_config)
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 执行测试并验证异常
        strategy = TelegramBotSenderStrategy()
        with pytest.raises(Exception) as exc_info:
            strategy.send(notification)
        
        assert "Telegram Bot token 或 chat_id 配置为空" in str(exc_info.value)

    @patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key')
    @patch('web.services.notice.sender.sender_strategy.requests.post')
    def test_pushplus_send_success(self, mock_post, mock_get_setting, rollback_session):
        """测试PushPlus发送成功"""
        # 模拟配置获取
        mock_get_setting.return_value = "test_pushplus_token"
        
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 执行测试
        strategy = PushPlusSenderStrategy()
        strategy.send(notification)
        
        # 验证调用
        mock_get_setting.assert_called_once_with("notification_sender.pushplus")
        mock_post.assert_called_once_with('http://www.pushplus.plus/send', {
            'token': 'test_pushplus_token',
            'title': self.test_notification_content['title'],
            'content': mock_post.call_args[0][1]['content']  # 内容会被渲染，所以只检查结构
        })

    @patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key')
    def test_pushplus_send_no_config(self, mock_get_setting, rollback_session):
        """测试PushPlus配置为空的情况"""
        # 模拟配置为空
        mock_get_setting.return_value = None
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 执行测试并验证异常
        strategy = PushPlusSenderStrategy()
        with pytest.raises(Exception) as exc_info:
            strategy.send(notification)
        
        assert "PushPlus token 配置为空" in str(exc_info.value)

    @patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key')
    @patch('web.services.notice.sender.sender_strategy.requests.post')
    def test_wecom_send_success(self, mock_post, mock_get_setting, rollback_session):
        """测试企业微信发送成功"""
        # 模拟配置获取
        mock_get_setting.return_value = "test_key"
        
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'errcode': 0}
        mock_post.return_value = mock_response
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 执行测试
        strategy = WeComSenderStrategy()
        strategy.send(notification)
        
        # 验证调用
        mock_get_setting.assert_called_once_with("notification_sender.wecom")
        mock_post.assert_called_once()
        
        # 验证请求参数
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test_key"
        request_body = call_args[1]['json']
        assert request_body['msgtype'] == 'text'
        assert 'content' in request_body['text']

    @patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key')
    def test_wecom_send_no_config(self, mock_get_setting, rollback_session):
        """测试企业微信配置为空的情况"""
        # 模拟配置为空
        mock_get_setting.return_value = None
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 执行测试并验证异常
        strategy = WeComSenderStrategy()
        with pytest.raises(Exception) as exc_info:
            strategy.send(notification)
        
        assert "企业微信 webhook key 配置为空" in str(exc_info.value)

    def test_sender_context_with_default_strategy(self, rollback_session):
        """测试发送上下文使用默认策略"""
        # 创建mock策略
        mock_strategy = Mock()
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 创建发送上下文
        context = SenderContext(mock_strategy)
        context.send(notification)
        
        # 验证策略被调用
        mock_strategy.send.assert_called_once_with(notification)

    def test_sender_context_with_override_strategy(self, rollback_session):
        """测试发送上下文使用覆盖策略"""
        # 创建mock策略
        default_strategy = Mock()
        override_strategy = Mock()
        
        # 创建测试通知
        notification = self.create_test_notification(rollback_session)
        
        # 创建发送上下文并使用覆盖策略
        context = SenderContext(default_strategy)
        context.send(notification, sender_strategy=override_strategy)
        
        # 验证覆盖策略被调用，默认策略未被调用
        override_strategy.send.assert_called_once_with(notification)
        default_strategy.send.assert_not_called()

    # ========== 可选的真实发送测试方法 ==========
    # 注意：以下测试方法需要手动运行，不会在自动化测试中执行
    # 运行前请确保设置了相应的环境变量
    
    @pytest.mark.manual
    @pytest.mark.skipif(
        not os.getenv('REAL_TEST_TELEGRAM_BOT_TOKEN') or not os.getenv('REAL_TEST_TELEGRAM_CHAT_ID'),
        reason="需要设置 REAL_TEST_TELEGRAM_BOT_TOKEN 和 REAL_TEST_TELEGRAM_CHAT_ID 环境变量"
    )
    def test_telegram_bot_real_send_manual(self, rollback_session):
        """
        手动测试Telegram Bot真实发送
        
        使用方法：
        export REAL_TEST_TELEGRAM_BOT_TOKEN="your_bot_token"
        export REAL_TEST_TELEGRAM_CHAT_ID="your_chat_id"
        pytest -m manual -k telegram_bot_real_send_manual -v
        """
        telegram_config = {
            "token": os.getenv('REAL_TEST_TELEGRAM_BOT_TOKEN'),
            "chat_id": os.getenv('REAL_TEST_TELEGRAM_CHAT_ID')
        }
        
        with patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key') as mock_get_setting:
            mock_get_setting.return_value = json.dumps(telegram_config)
            
            notification = self.create_test_notification(rollback_session)
            
            strategy = TelegramBotSenderStrategy()
            try:
                result = strategy.send(notification)
                print(f"✅ Telegram Bot 真实发送成功: {result}")
                assert result is not None
            except Exception as e:
                pytest.fail(f"❌ Telegram Bot 真实发送失败: {str(e)}")

    @pytest.mark.manual
    @pytest.mark.skipif(
        not os.getenv('REAL_TEST_PUSHPLUS_TOKEN'),
        reason="需要设置 REAL_TEST_PUSHPLUS_TOKEN 环境变量"
    )
    def test_pushplus_real_send_manual(self, rollback_session):
        """
        手动测试PushPlus真实发送
        
        使用方法：
        export REAL_TEST_PUSHPLUS_TOKEN="your_pushplus_token"
        pytest -m manual -k pushplus_real_send_manual -v
        """
        pushplus_token = os.getenv('REAL_TEST_PUSHPLUS_TOKEN')
        
        with patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key') as mock_get_setting:
            mock_get_setting.return_value = pushplus_token
            
            notification = self.create_test_notification(rollback_session)
            
            strategy = PushPlusSenderStrategy()
            try:
                strategy.send(notification)
                print("✅ PushPlus 真实发送成功")
            except Exception as e:
                pytest.fail(f"❌ PushPlus 真实发送失败: {str(e)}")

    @pytest.mark.manual
    @pytest.mark.skipif(
        not os.getenv('REAL_TEST_WECOM_WEBHOOK'),
        reason="需要设置 REAL_TEST_WECOM_WEBHOOK 环境变量"
    )
    def test_wecom_real_send_manual(self, rollback_session):
        """
        手动测试企业微信真实发送
        
        使用方法：
        export REAL_TEST_WECOM_WEBHOOK="your_wecom_webhook_url"
        pytest -m manual -k wecom_real_send_manual -v
        """
        wecom_webhook = os.getenv('REAL_TEST_WECOM_WEBHOOK')
        
        with patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key') as mock_get_setting:
            mock_get_setting.return_value = wecom_webhook
            
            notification = self.create_test_notification(rollback_session)
            
            strategy = WeComSenderStrategy()
            try:
                strategy.send(notification)
                print("✅ 企业微信真实发送成功")
            except Exception as e:
                pytest.fail(f"❌ 企业微信真实发送失败: {str(e)}")

    @pytest.mark.manual
    @pytest.mark.skipif(
        not os.getenv('REAL_TEST_SERVER_CHAN_SENDKEY'),
        reason="需要设置 REAL_TEST_SERVER_CHAN_SENDKEY 环境变量"
    )
    def test_server_chan_real_send_manual(self, rollback_session):
        """
        手动测试Server酱真实发送
        
        ⚠️ 警告：这会真实发送消息并消耗每日限额！
        
        使用方法：
        export REAL_TEST_SERVER_CHAN_SENDKEY="your_sendkey"
        pytest -m manual -k server_chan_real_send_manual -v
        """
        sendkey = os.getenv('REAL_TEST_SERVER_CHAN_SENDKEY')
        
        with patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key') as mock_get_setting:
            mock_get_setting.return_value = sendkey
            
            notification = self.create_test_notification(rollback_session)
            
            strategy = ServerChenSenderStrategy()
            try:
                strategy.send(notification)
                print("✅ Server酱真实发送成功")
            except Exception as e:
                pytest.fail(f"❌ Server酱真实发送失败: {str(e)}")

    @pytest.mark.manual
    def test_all_strategies_real_send_manual(self, rollback_session):
        """
        手动测试所有配置的策略真实发送
        
        这个测试会尝试使用所有配置了环境变量的发送策略
        
        使用方法：
        # 设置需要测试的环境变量
        export REAL_TEST_TELEGRAM_BOT_TOKEN="..."
        export REAL_TEST_TELEGRAM_CHAT_ID="..."
        export REAL_TEST_PUSHPLUS_TOKEN="..."
        export REAL_TEST_WECOM_WEBHOOK="..."
        export REAL_TEST_SERVER_CHAN_SENDKEY="..."
        
        # 运行测试
        pytest -m manual -k all_strategies_real_send_manual -v
        """
        notification = self.create_test_notification(rollback_session)
        
        strategies_to_test = []
        
        # Telegram Bot
        if os.getenv('REAL_TEST_TELEGRAM_BOT_TOKEN') and os.getenv('REAL_TEST_TELEGRAM_CHAT_ID'):
            telegram_config = {
                "token": os.getenv('REAL_TEST_TELEGRAM_BOT_TOKEN'),
                "chat_id": os.getenv('REAL_TEST_TELEGRAM_CHAT_ID')
            }
            strategies_to_test.append(("Telegram Bot", TelegramBotSenderStrategy(), json.dumps(telegram_config), "notification_sender.telegram_bot"))
        
        # PushPlus
        if os.getenv('REAL_TEST_PUSHPLUS_TOKEN'):
            strategies_to_test.append(("PushPlus", PushPlusSenderStrategy(), os.getenv('REAL_TEST_PUSHPLUS_TOKEN'), "notification_sender.pushplus"))
        
        # 企业微信
        if os.getenv('REAL_TEST_WECOM_WEBHOOK'):
            strategies_to_test.append(("企业微信", WeComSenderStrategy(), os.getenv('REAL_TEST_WECOM_WEBHOOK'), "notification_sender.wecom"))
        
        # Server酱
        if os.getenv('REAL_TEST_SERVER_CHAN_SENDKEY'):
            strategies_to_test.append(("Server酱", ServerChenSenderStrategy(), os.getenv('REAL_TEST_SERVER_CHAN_SENDKEY'), "notification_sender.server_chan"))
        
        if not strategies_to_test:
            pytest.skip("没有配置任何真实测试环境变量，跳过多策略测试")
        
        print(f"\n准备测试 {len(strategies_to_test)} 个发送策略...")
        
        success_count = 0
        failed_strategies = []
        
        for strategy_name, strategy, config_value, config_key in strategies_to_test:
            try:
                with patch('web.services.notice.sender.sender_strategy.notification_config_service.get_setting_by_key') as mock_get_setting:
                    mock_get_setting.return_value = config_value
                    
                    context = SenderContext(strategy)
                    context.send(notification)
                    print(f"✅ {strategy_name} 发送成功")
                    success_count += 1
            except Exception as e:
                error_msg = f"❌ {strategy_name} 发送失败: {str(e)}"
                print(error_msg)
                failed_strategies.append(error_msg)
        
        print(f"\n测试结果: 成功 {success_count}/{len(strategies_to_test)} 个策略")
        
        if failed_strategies:
            print("失败的策略:")
            for error in failed_strategies:
                print(f"  {error}")
        
        # 至少要有一个策略发送成功
        assert success_count > 0, f"所有发送策略都失败了！失败详情: {failed_strategies}"