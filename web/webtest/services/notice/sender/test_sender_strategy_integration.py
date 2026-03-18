# -*- coding: UTF-8 -*-
"""    @File    ：test_sender_strategy_integration.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/12/19 15:00
@Description: 集成测试 - 真实发送消息测试用例
注意：这些测试会真正发送消息，请确保在数据库中配置了正确的发送渠道配置
"""
import pytest
import json
import os
from unittest.mock import Mock, patch
from web.models.notice.Notification import Notification
from web.models.setting.system_settings import Setting
from web.services.notice.sender.sender_strategy import (
    ServerChenSenderStrategy, 
    TelegramBotSenderStrategy, 
    PushPlusSenderStrategy,
    WeComSenderStrategy,
    SenderContext
)
from web.services.notice.notification_config_service import notification_config_service
from web.webtest.test_base import TestBase


@pytest.mark.integration
@pytest.mark.usefixtures("rollback_session")
class TestSenderStrategyIntegration(TestBase):
    """
    集成测试类 - 真实发送消息
    
    运行前请确保：
    1. 在数据库中配置了正确的发送渠道配置：
       - notification_sender.server_chan: Server酱的sendkey
       - notification_sender.telegram: Telegram Bot配置JSON {"token": "xxx", "chat_id": "xxx"}
       - notification_sender.pushplus: PushPlus的token
       - notification_sender.wecom: 企业微信的webhook地址
    2. 使用 pytest -m integration 运行这些测试
    3. 如果数据库中没有配置，可以设置环境变量作为备选
    """
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 注意：测试配置数据和通知内容现在通过fixtures提供
        # 参见 conftest.py 中的 notification_test_configs 和 test_notification_content fixtures
        pass
        
    @patch('web.services.notice.sender.sender_strategy.requests.post')
    def test_server_chan_real_send_mocked(self, mock_post, rollback_session, setup_notification_config,
                                        notification_test_configs, test_notification):
        """
        测试Server酱真实发送（使用Mock模拟，避免达到每日限制）
        
        注意：Server酱有每日5次发送限制，所以这里仍然使用Mock
        如果需要真实测试，请手动运行单独的测试方法
        """
        # 从环境变量获取真实配置，如果没有则使用测试配置
        real_sendkey = os.getenv('TEST_SERVER_CHAN_SENDKEY', 
                                notification_test_configs["notification_sender.server_chan"])
        
        # 设置数据库配置
        setup_notification_config(rollback_session, "notification_sender.server_chan", real_sendkey)
        
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'errno': 0, 'errmsg': 'success'}
        }
        mock_post.return_value = mock_response
        
        # 执行测试
        strategy = ServerChenSenderStrategy()
        strategy.send(test_notification)
        
        # 验证调用
        mock_post.assert_called_once()
        
        # 验证请求参数
        call_args = mock_post.call_args
        assert f'https://sctapi.ftqq.com/{real_sendkey}.send' in call_args[1]['url']
        assert 'text' in call_args[1]['data']
        assert 'desp' in call_args[1]['data']
        assert '[集成测试]' in call_args[1]['data']['text']

    def test_telegram_bot_real_send(self, rollback_session, setup_all_test_configs, 
                                   notification_test_configs, test_notification):
        """
        测试Telegram Bot真实发送
        
        使用预设的测试配置数据进行测试
        """
        # 预先设置测试配置
        setup_all_test_configs(rollback_session)
        
        # 检查Telegram配置是否可用
        if not notification_test_configs["notification_sender.telegram_bot"]:
            pytest.skip("Telegram Bot配置不可用，跳过测试")
        
        # 执行真实发送
        strategy = TelegramBotSenderStrategy()
        try:
            result = strategy.send(test_notification)
            print(f"Telegram Bot 发送成功: {result}")
            assert result is not None
        except Exception as e:
            pytest.fail(f"Telegram Bot 发送失败: {str(e)}")

    def test_pushplus_real_send(self, rollback_session, setup_all_test_configs, 
                              notification_test_configs, test_notification):
        """
        测试PushPlus真实发送
        
        使用预设的测试配置数据进行测试
        """
        # 预先设置测试配置
        setup_all_test_configs(rollback_session)
        
        # 检查PushPlus配置是否可用
        if not notification_test_configs["notification_sender.pushplus"]:
            pytest.skip("PushPlus配置不可用，请设置环境变量 TEST_PUSHPLUS_TOKEN")
        
        # 执行真实发送
        strategy = PushPlusSenderStrategy()
        try:
            strategy.send(test_notification)
            print("PushPlus 发送成功")
        except Exception as e:
            pytest.fail(f"PushPlus 发送失败: {str(e)}")

    def test_wecom_real_send(self, rollback_session, setup_all_test_configs, 
                           notification_test_configs, test_notification):
        """
        测试企业微信真实发送
        
        使用预设的测试配置数据进行测试
        """
        # 预先设置测试配置
        setup_all_test_configs(rollback_session)
        
        # 检查企业微信配置是否可用
        if not notification_test_configs["notification_sender.wecom"]:
            pytest.skip("企业微信配置不可用，跳过测试")
        
        # 执行真实发送
        strategy = WeComSenderStrategy()
        try:
            strategy.send(test_notification)
            print("企业微信发送成功")
        except Exception as e:
            pytest.fail(f"企业微信发送失败: {str(e)}")

    def test_sender_context_real_send_with_multiple_strategies(self, rollback_session, setup_all_test_configs, 
                                                             notification_test_configs, test_notification):
        """
        测试发送上下文使用多种策略真实发送
        
        使用预设的测试配置数据进行测试
        """
        # 预先设置测试配置
        setup_all_test_configs(rollback_session)
        
        # 测试可用的发送策略
        strategies_to_test = []
        
        # Telegram Bot
        if notification_test_configs["notification_sender.telegram_bot"]:
            strategies_to_test.append(("Telegram Bot", TelegramBotSenderStrategy()))
            print("添加Telegram Bot策略到测试列表")
        
        # PushPlus
        if notification_test_configs["notification_sender.pushplus"]:
            strategies_to_test.append(("PushPlus", PushPlusSenderStrategy()))
            print("添加PushPlus策略到测试列表")
        
        # 企业微信
        if notification_test_configs["notification_sender.wecom"]:
            strategies_to_test.append(("企业微信", WeComSenderStrategy()))
            print("添加企业微信策略到测试列表")
        
        if not strategies_to_test:
            pytest.skip("没有可用的发送策略配置，跳过多策略测试")
        
        # 执行测试
        success_count = 0
        for strategy_name, strategy in strategies_to_test:
            try:
                print(f"开始发送 {strategy_name}...")
                # 直接使用策略发送，避免SenderContext单例问题
                strategy.send(test_notification)
                print(f"{strategy_name} 发送成功")
                success_count += 1
            except Exception as e:
                print(f"{strategy_name} 发送失败: {str(e)}")
                # 打印详细的错误信息用于调试
                import traceback
                print(f"详细错误信息: {traceback.format_exc()}")
        
        # 至少要有一个策略发送成功
        assert success_count > 0, "所有发送策略都失败了"
        print(f"成功发送 {success_count}/{len(strategies_to_test)} 个渠道")

    # 手动测试方法（不会自动运行）
    @pytest.mark.manual
    def test_server_chan_real_send_manual(self, rollback_session, setup_all_test_configs, 
                                        notification_test_configs, test_notification):
        """
        手动测试Server酱真实发送
        
        警告：这会真实发送消息并消耗每日限额！
        只有在确实需要测试时才手动移除@pytest.mark.skip装饰器
        
        使用预设的测试配置数据进行测试
        """
        # 预先设置测试配置
        setup_all_test_configs(rollback_session)
        
        # 检查Server酱配置是否可用
        if not notification_test_configs["notification_sender.server_chan"]:
            pytest.skip("Server酱配置不可用，跳过测试")
        
        # 执行真实发送
        strategy = ServerChenSenderStrategy()
        try:
            strategy.send(test_notification)
            print("Server酱真实发送成功")
        except Exception as e:
            pytest.fail(f"Server酱真实发送失败: {str(e)}")
    
    def test_setup_configs_from_mcp(self, rollback_session, setup_all_test_configs, notification_test_configs):
        """
        测试从MCP服务设置配置数据
        
        这个测试验证能否正确从预设配置中设置数据库配置
        """
        # 执行配置设置
        setup_all_test_configs(rollback_session)
        
        # 验证配置是否正确设置
        # Server酱配置
        server_chan_config = notification_config_service.get_setting_by_key("notification_sender.server_chan")
        assert server_chan_config == notification_test_configs["notification_sender.server_chan"]
        
        # Telegram配置
        telegram_config = notification_config_service.get_setting_by_key("notification_sender.telegram_bot")
        if telegram_config:
            parsed_config = json.loads(telegram_config)
            assert parsed_config["token"] == notification_test_configs["notification_sender.telegram_bot"]["token"]
            assert parsed_config["chat_id"] == notification_test_configs["notification_sender.telegram_bot"]["chat_id"]
        
        # 企业微信配置
        wecom_config = notification_config_service.get_setting_by_key("notification_sender.wecom")
        assert wecom_config == notification_test_configs["notification_sender.wecom"]
        
        print("所有配置验证通过")