# -*- coding: UTF-8 -*-
"""
@File    ：test_null_field_handling.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/12/19
@Description: 测试notification_analyser.py中对空值字段的处理
"""

import pytest
from unittest.mock import Mock
from web.services.notice.analyser.notification_analyser import (
    GridTradeBotAnalysisStrategy,
    GridTradeHTMLAnalysisStrategy,
    GridTradeClientAnalysisStrategy,
    BaseNotificationAnalysisStrategy,
    BusinessType,
    ChannelType
)
from web.models.notice.Notification import Notification
from web.webtest.test_base import TestBase


class TestNullFieldHandling(TestBase):
    """
    测试通知分析器对空值字段的处理
    """
    
    def setup_method(self):
        """测试前准备"""
        self.bot_strategy = GridTradeBotAnalysisStrategy()
        self.html_strategy = GridTradeHTMLAnalysisStrategy()
        self.client_strategy = GridTradeClientAnalysisStrategy()
        self.base_strategy = BaseNotificationAnalysisStrategy(BusinessType.GRID_TRADE, ChannelType.BOT)
    
    def create_mock_notification_with_nulls(self, **overrides):
        """创建包含空值的模拟通知对象"""
        mock_notification = Mock(spec=Notification)
        # 设置默认的空值
        mock_notification.id = None
        mock_notification.title = None
        mock_notification.content = None
        mock_notification.timestamp = None
        mock_notification.notice_level = None
        mock_notification.business_type = 0
        mock_notification.template_key = None
        
        # 应用覆盖值
        for key, value in overrides.items():
            setattr(mock_notification, key, value)
        
        return mock_notification
    
    @pytest.mark.local
    def test_base_strategy_with_null_fields(self):
        """测试基础策略处理空值字段"""
        notification = self.create_mock_notification_with_nulls()
        
        result = self.base_strategy.analysis(notification)
        
        # 验证空值被正确处理
        assert result['title'] == '未知标题'
        assert result['timestamp'] == '未知时间'
        assert result['notification_level'] == 0
        assert 'content' in result
    
    @pytest.mark.local
    def test_base_strategy_with_null_content(self):
        """测试基础策略处理空content字段"""
        notification = self.create_mock_notification_with_nulls(
            title="测试标题",
            content=None
        )
        
        result = self.base_strategy.analysis(notification)
        
        # 验证空content被正确处理
        assert result['title'] == '测试标题'
        assert 'content' in result
        assert isinstance(result['content'], dict)
    
    @pytest.mark.local
    def test_base_strategy_with_invalid_json_content(self):
        """测试基础策略处理无效JSON content"""
        notification = self.create_mock_notification_with_nulls(
            title="测试标题",
            content="invalid json content"
        )
        
        result = self.base_strategy.analysis(notification)
        
        # 验证无效JSON被正确处理
        assert result['title'] == '测试标题'
        assert 'content' in result
        assert result['content']['title'] == '测试标题'
        assert result['content']['content'] == 'invalid json content'
    
    @pytest.mark.local
    def test_bot_strategy_with_null_fields(self):
        """测试Bot策略处理空值字段"""
        notification = self.create_mock_notification_with_nulls()
        
        result = self.bot_strategy.analysis(notification)
        
        # 验证空值被正确处理
        assert result['title'] == '未知标题'
        assert 'grid_info' in result
        assert isinstance(result['grid_info'], list)
    
    @pytest.mark.local
    def test_html_strategy_with_null_fields(self):
        """测试HTML策略处理空值字段"""
        notification = self.create_mock_notification_with_nulls()
        
        result = self.html_strategy.analysis(notification)
        
        # 验证空值被正确处理
        assert result['title'] == '未知标题'
        assert result['timestamp'] == '未知时间'
        assert 'grid_info' in result
        assert isinstance(result['grid_info'], list)
    
    @pytest.mark.local
    def test_html_strategy_error_response_with_null_fields(self):
        """测试HTML策略错误响应处理空值字段"""
        notification = self.create_mock_notification_with_nulls(
            content="invalid json"
        )
        
        result = self.html_strategy.analysis(notification)
        
        # 验证错误响应中的空值被正确处理
        assert result['title'] == '未知标题'
        assert result['timestamp'] == '未知时间'
        assert result['error'] == '通知内容解析失败'
    
    @pytest.mark.local
    def test_client_strategy_with_null_fields(self):
        """测试客户端策略处理空值字段"""
        notification = self.create_mock_notification_with_nulls()
        
        result = self.client_strategy.analysis(notification)
        
        # 验证空值被正确处理
        assert result['title'] == '未知标题'
        assert result['timestamp'] == '未知时间'
        assert result['notification_level'] == 0
        assert 'summary' in result
    
    @pytest.mark.local
    def test_client_strategy_error_response_with_null_fields(self):
        """测试客户端策略错误响应处理空值字段"""
        notification = self.create_mock_notification_with_nulls(
            content="invalid json"
        )
        
        result = self.client_strategy.analysis(notification)
        
        # 验证错误响应中的空值被正确处理
        assert result['title'] == '未知标题'
        assert result['timestamp'] == '未知时间'
        assert result['notification_level'] == 0
        assert result['summary']['message'] == '通知内容解析失败'
    
    @pytest.mark.local
    def test_strategies_with_partial_null_fields(self):
        """测试策略处理部分空值字段"""
        notification = self.create_mock_notification_with_nulls(
            id=123,
            title="部分空值测试",
            content='{"title": "JSON标题", "grid_info": []}',
            notice_level=None,  # 这个仍然为空
            timestamp=None      # 这个仍然为空
        )
        
        # 测试所有策略
        strategies = [
            self.base_strategy,
            self.bot_strategy,
            self.html_strategy,
            self.client_strategy
        ]
        
        for strategy in strategies:
            result = strategy.analysis(notification)
            
            # 验证非空字段被正确使用
            assert result['title'] == 'JSON标题'  # 来自content中的title
            
            # 验证空字段被正确处理（只对有timestamp字段的策略检查）
            if 'timestamp' in result:
                assert result['timestamp'] == '未知时间'
            
            # 对于有notification_level的策略，验证空值处理
            if 'notification_level' in result:
                assert result['notification_level'] == 0
    
    @pytest.mark.local
    def test_debug_logs_with_null_id(self):
        """测试debug日志处理空ID"""
        notification = self.create_mock_notification_with_nulls(
            id=None,
            content='{}'
        )
        
        # 这个测试主要确保不会因为空ID而抛出异常
        # 实际的日志输出验证需要mock logging，这里只验证不抛异常
        try:
            self.bot_strategy.analysis(notification)
            self.html_strategy.analysis(notification)
            self.client_strategy.analysis(notification)
            self.base_strategy.analysis(notification)
        except Exception as e:
            pytest.fail(f"策略处理空ID时抛出异常: {e}")