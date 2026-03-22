"""    @File    ：conftest.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/12/19 15:00
@Description: 通知发送测试的fixtures配置
"""
import os

import pytest
import json
from web.models.notice.Notification import Notification
from web.models.setting.system_settings import Setting
from web.services.notice.notification_config_service import notification_config_service


@pytest.fixture(scope="session")
def notification_test_configs():
    """
    通知发送测试的预设配置数据
    
    从环境变量中获取配置，如果环境变量不存在则使用默认值
    这样可以避免在代码中硬编码敏感信息
    
    Returns:
        dict: 包含各种发送渠道配置的字典
    """
    # Telegram Bot 配置
    telegram_config = None
    telegram_token = os.getenv('TEST_TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TEST_TELEGRAM_CHAT_ID')
    if telegram_token and telegram_chat_id:
        telegram_config = {
            "token": telegram_token,
            "chat_id": telegram_chat_id
        }
    
    return {
        "notification_sender.server_chan": os.getenv('TEST_SERVER_CHAN_KEY'),
        "notification_sender.telegram_bot": telegram_config,
        "notification_sender.wecom": os.getenv('TEST_WECOM_WEBHOOK_KEY'),
        "notification_sender.pushplus": os.getenv('TEST_PUSHPLUS_TOKEN')
    }


@pytest.fixture(scope="session")
def test_notification_content():
    """
    测试通知的内容模板
    
    提供标准的测试通知内容，可以在多个测试中复用
    
    Returns:
        dict: 测试通知的内容字典
    """
    return {
        "title": "[测试] 网格交易通知",
        "content": "这是一个集成测试通知内容，用于验证真实发送功能",
        "grid_info": [
            {
                "asset_name": "测试ETF",
                "grid_type_name": "小网",
                "trade_list": [],
                "current_change": []
            }
        ]
    }


@pytest.fixture(scope="function")
def test_notification(rollback_session, test_notification_content):
    """
    创建测试通知对象的fixture
    
    Args:
        rollback_session: 数据库会话
        test_notification_content: 测试通知内容
        
    Returns:
        Notification: 创建的测试通知对象
    """
    notification = Notification(
        title="[集成测试] 通知发送测试",
        content=json.dumps(test_notification_content),
        notice_level=0,
        business_type=Notification.get_business_type_enum().GRID_TRADE.value,
        notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value
    )
    rollback_session.add(notification)
    rollback_session.flush()
    return notification


@pytest.fixture(scope="function")
def setup_notification_config(setup_system_setting):
    """
    设置通知相关配置到数据库的fixture
    
    基于父级的通用设置函数，专门用于通知相关配置的设置
    包含通知特有的逻辑，如清空配置缓存
    
    Args:
        setup_system_setting: 父级提供的通用设置函数
        
    Returns:
        function: 用于设置通知配置的函数
    """
    def _setup_notification_config(session, config_key: str, config_value: str):
        """
        设置通知配置到数据库
        
        Args:
            session: 数据库会话
            config_key: 配置键
            config_value: 配置值
        """
        # 使用父级的通用设置函数，指定通知相关的默认参数
        setup_system_setting(
            session,
            config_key,
            config_value,
            group="notification",
            description=f"集成测试配置 - {config_key}",
            setting_type="string"
        )
        # 清空配置缓存，确保获取最新配置
        notification_config_service.clear_cache()
    
    return _setup_notification_config


@pytest.fixture(scope="function")
def setup_all_test_configs(setup_notification_config, notification_test_configs):
    """
    批量设置所有通知测试配置到数据库的fixture
    
    Args:
        setup_notification_config: 设置单个通知配置的函数
        notification_test_configs: 预设的测试配置数据
        
    Returns:
        function: 用于批量设置配置的函数
    """
    def _setup_all_configs(session):
        """
        批量设置所有测试配置到数据库
        
        这个方法会从预设配置数据中设置测试所需的所有配置项
        如果某些配置不存在，则尝试从环境变量获取
        
        Args:
            session: 数据库会话
        """
        # Server酱配置
        if notification_test_configs["notification_sender.server_chan"]:
            setup_notification_config(
                session,
                "notification_sender.server_chan",
                notification_test_configs["notification_sender.server_chan"]
            )
        
        # Telegram Bot配置
        if notification_test_configs["notification_sender.telegram_bot"]:
            telegram_config = json.dumps(notification_test_configs["notification_sender.telegram_bot"])
            setup_notification_config(
                session,
                "notification_sender.telegram_bot",
                telegram_config
            )
        
        # 企业微信配置
        if notification_test_configs["notification_sender.wecom"]:
            setup_notification_config(
                session,
                "notification_sender.wecom",
                notification_test_configs["notification_sender.wecom"]
            )
        
        # PushPlus配置（如果有的话）
        if notification_test_configs["notification_sender.pushplus"]:
            setup_notification_config(
                session,
                "notification_sender.pushplus",
                notification_test_configs["notification_sender.pushplus"]
            )
    
    return _setup_all_configs


@pytest.fixture(scope="session")
def sender_strategy_configs():
    """
    发送策略相关的配置数据
    
    提供各种发送策略测试时需要的配置信息
    
    Returns:
        dict: 发送策略配置字典
    """
    return {
        "test_strategies": [
            "telegram_bot",
            "pushplus", 
            "wecom"
        ],
        "strategy_names": {
            "telegram_bot": "Telegram Bot",
            "pushplus": "PushPlus",
            "wecom": "企业微信",
            "server_chan": "Server酱"
        }
    }