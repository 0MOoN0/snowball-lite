# -*- coding: UTF-8 -*-
"""
@File    ：TestNotificationAnalyser.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025-01-14
@Description: 通知分析器测试用例
"""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from web.services.notice.analyser.notification_analyser import (
    BusinessType,
    ChannelType,
    NotificationAnalysisStrategyFactory,
    GridTradeBotAnalysisStrategy,
    GridTradeHTMLAnalysisStrategy,
    GridTradeClientAnalysisStrategy,
    BaseNotificationAnalysisStrategy,
    AnalysisNotificationContentContext,
    grid_trade_bot_notification_analysis_strategy,
    grid_trade_html_notification_analysis_strategy,
    grid_trade_client_notification_analysis_strategy
)
from web.models.notice.Notification import Notification
from web.webtest.test_base import TestBase


class TestNotificationAnalyser(TestBase):
    """
    通知分析器测试类
    """
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """
        测试数据准备fixture
        """
        # 标准的网格交易通知内容（来自系统说明文档）
        self.standard_grid_trade_content = {
            "title": "网格交易确认通知",
            "grid_info": [
                {
                    "asset_name": "国泰中证全指证券公司ETF",
                    "grid_type_name": "小网",
                    "trade_list": [
                        {
                            "gridId": 8,
                            "profit": 1314600,
                            "triggerPurchasePrice": 9320,
                            "purchasePrice": 9270,
                            "triggerSellPrice": 10160,
                            "actualSellShares": 1300,
                            "sellAmount": 13271700,
                            "id": 102,
                            "gridTypeId": 8,
                            "gear": "0.95",
                            "purchaseAmount": 12978000,
                            "purchaseShares": 1400,
                            "saveShareProfit": 293700,
                            "sellShares": 1400,
                            "saveShare": 100,
                            "monitorType": 0,
                            "sellPrice": 10209,
                            "isCurrent": True
                        }
                    ],
                    "current_change": [
                        {
                            "sellPrice": 11330,
                            "sellAmount": 12463000,
                            "purchaseShares": 1200,
                            "profit": 1236000,
                            "saveShare": 100,
                            "id": 101,
                            "purchasePrice": 10300,
                            "gridId": 7,
                            "triggerSellPrice": 11279,
                            "monitorType": 1,
                            "actualSellShares": 1100,
                            "triggerPurchasePrice": 10350,
                            "gear": "1.0",
                            "sellShares": 1200,
                            "purchaseAmount": 12360000,
                            "gridTypeId": 8,
                            "isCurrent": True,
                            "saveShareProfit": 103000
                        }
                    ]
                }
            ]
        }
        
        # 创建模拟的通知对象
        self.mock_notification = Mock(spec=Notification)
        self.mock_notification.id = 1
        self.mock_notification.title = "网格交易确认通知"
        self.mock_notification.content = json.dumps(self.standard_grid_trade_content)
        self.mock_notification.timestamp = datetime.now()
        self.mock_notification.notice_level = 1
        self.mock_notification.business_type = 0
    
    @pytest.mark.local
    def test_business_type_enum(self):
        """
        测试业务类型枚举
        """
        assert BusinessType.GRID_TRADE.value == 0
        assert BusinessType.MESSAGE_REMIND.value == 1
        assert BusinessType.SYSTEM_RUNNING.value == 2
        assert BusinessType.DAILY_REPORT.value == 3
    
    @pytest.mark.local
    def test_channel_type_enum(self):
        """
        测试渠道类型枚举
        """
        assert ChannelType.BOT.value == "bot"
        assert ChannelType.HTML.value == "html"
        assert ChannelType.MARKDOWN.value == "markdown"
        assert ChannelType.CLIENT.value == "client"
    
    @pytest.mark.local
    def test_strategy_factory_registration(self):
        """
        测试策略工厂注册
        """
        strategies = NotificationAnalysisStrategyFactory.get_registered_strategies()
        
        # 验证网格交易策略已注册
        assert (BusinessType.GRID_TRADE, ChannelType.BOT) in strategies
        assert (BusinessType.GRID_TRADE, ChannelType.HTML) in strategies
        assert (BusinessType.GRID_TRADE, ChannelType.CLIENT) in strategies
        assert (BusinessType.GRID_TRADE, ChannelType.MARKDOWN) in strategies
    
    @pytest.mark.local
    def test_strategy_factory_create_strategy(self):
        """
        测试策略工厂创建策略
        """
        # 测试创建Bot策略
        bot_strategy = NotificationAnalysisStrategyFactory.create_strategy(
            BusinessType.GRID_TRADE, ChannelType.BOT
        )
        assert isinstance(bot_strategy, GridTradeBotAnalysisStrategy)
        
        # 测试创建HTML策略
        html_strategy = NotificationAnalysisStrategyFactory.create_strategy(
            BusinessType.GRID_TRADE, ChannelType.HTML
        )
        assert isinstance(html_strategy, GridTradeHTMLAnalysisStrategy)
        
        # 测试创建客户端策略
        client_strategy = NotificationAnalysisStrategyFactory.create_strategy(
            BusinessType.GRID_TRADE, ChannelType.CLIENT
        )
        assert isinstance(client_strategy, GridTradeClientAnalysisStrategy)
        
        # 测试未注册的策略组合，应该返回默认策略
        default_strategy = NotificationAnalysisStrategyFactory.create_strategy(
            BusinessType.MESSAGE_REMIND, ChannelType.BOT
        )
        assert isinstance(default_strategy, GridTradeBotAnalysisStrategy)
    
    @pytest.mark.local
    def test_grid_trade_bot_analysis_strategy(self):
        """
        测试网格交易Bot分析策略
        """
        strategy = GridTradeBotAnalysisStrategy()
        result = strategy.analysis(self.mock_notification)
        
        # 验证基本结构
        assert 'title' in result
        assert 'business_type' in result
        assert 'channel_type' in result
        assert 'grid_info' in result
        
        # 验证业务类型和渠道类型
        assert result['business_type'] == BusinessType.GRID_TRADE.value
        assert result['channel_type'] == ChannelType.BOT.value
        
        # 验证网格信息
        assert len(result['grid_info']) == 1
        grid_info = result['grid_info'][0]
        
        assert grid_info['asset_name'] == "国泰中证全指证券公司ETF"
        assert grid_info['grid_type_name'] == "小网"
        assert 'buy_count' in grid_info
        assert 'sell_count' in grid_info
        assert 'current_change' in grid_info
        assert 'trade_summary' in grid_info
    
    @pytest.mark.local
    def test_grid_trade_html_analysis_strategy(self):
        """
        测试网格交易HTML分析策略
        """
        strategy = GridTradeHTMLAnalysisStrategy()
        result = strategy.analysis(self.mock_notification)
        
        # 验证基本结构
        assert 'title' in result
        assert 'timestamp' in result
        assert 'business_type' in result
        assert 'channel_type' in result
        assert 'grid_info' in result
        
        # 验证业务类型和渠道类型
        assert result['business_type'] == BusinessType.GRID_TRADE.value
        assert result['channel_type'] == ChannelType.HTML.value
        
        # 验证网格信息的详细结构
        grid_info = result['grid_info'][0]
        assert 'trade_details' in grid_info
        assert 'current_monitoring' in grid_info
        assert 'statistics' in grid_info
        
        # 验证统计信息
        stats = grid_info['statistics']
        assert 'total_trades' in stats
        assert 'total_profit' in stats
        assert 'avg_profit' in stats
    
    @pytest.mark.local
    def test_grid_trade_client_analysis_strategy(self):
        """
        测试网格交易客户端分析策略
        """
        strategy = GridTradeClientAnalysisStrategy()
        result = strategy.analysis(self.mock_notification)
        
        # 验证基本结构
        assert 'title' in result
        assert 'summary' in result
        assert 'timestamp' in result
        assert 'business_type' in result
        assert 'channel_type' in result
        assert 'notification_level' in result
        
        # 验证业务类型和渠道类型
        assert result['business_type'] == BusinessType.GRID_TRADE.value
        assert result['channel_type'] == ChannelType.CLIENT.value
        
        # 验证摘要信息
        summary = result['summary']
        assert 'total_assets' in summary
        assert 'total_trades' in summary
        assert 'message' in summary
    
    @pytest.mark.local
    def test_legacy_function_grid_trade_bot_notification_analysis_strategy(self):
        """
        测试遗留的网格交易Bot通知分析函数
        """
        result = grid_trade_bot_notification_analysis_strategy(self.standard_grid_trade_content)
        
        # 验证基本结构
        assert 'title' in result
        assert 'grid_info' in result
        
        # 验证网格信息结构（Bot策略应该将trade_list展开）
        grid_info = result['grid_info'][0]
        assert 'buy_count' in grid_info
        assert 'sell_count' in grid_info
        assert 'current_change' in grid_info
        
        # 验证trade_list已被展开
        assert 'trade_list' not in grid_info
    
    @pytest.mark.local
    def test_legacy_function_grid_trade_html_notification_analysis_strategy(self):
        """
        测试遗留的网格交易HTML通知分析函数
        """
        result = grid_trade_html_notification_analysis_strategy(self.standard_grid_trade_content)
        
        # 验证基本结构
        assert 'title' in result
        assert 'grid_info' in result
        
        # 验证网格信息结构（HTML策略保留trade_list结构）
        grid_info = result['grid_info'][0]
        assert 'trade_list' in grid_info
        assert 'current_change' in grid_info
        
        # 验证trade_list结构
        trade_list = grid_info['trade_list']
        assert 'buy_count' in trade_list
        assert 'sell_count' in trade_list
    
    @pytest.mark.local
    @patch('web.models.grid.GridTypeDetail.GridTypeDetail.query')
    def test_legacy_function_grid_trade_client_notification_analysis_strategy(self, mock_query):
        """
        测试遗留的网格交易客户端通知分析函数
        """
        # 模拟数据库查询
        mock_detail = MagicMock()
        mock_detail.id = 101
        mock_query.filter.return_value.all.return_value = [mock_detail]
        mock_query.get.return_value = mock_detail
        
        # 准备测试数据（使用ID列表而不是完整对象）
        client_content = {
            "title": "网格交易确认通知",
            "grid_info": [
                {
                    "asset_name": "国泰中证全指证券公司ETF",
                    "grid_type_name": "小网",
                    "trade_list": [102],  # 使用ID列表
                    "current_change": [101, 102]  # 使用ID列表
                }
            ]
        }
        
        with patch('web.services.notice.analyser.notification_analyser.GridTypeDetailVOSchema') as mock_schema:
            mock_schema.return_value.dump.return_value = [{'id': 101, 'gear': '1.0'}]
            
            result = grid_trade_client_notification_analysis_strategy(client_content)
            
            # 验证基本结构
            assert 'title' in result
            assert 'grid_info' in result
    
    @pytest.mark.local
    def test_analysis_notification_content_context_with_strategy(self):
        """
        测试通知内容分析上下文（使用策略）
        """
        def strategy_func(content):
            return grid_trade_bot_notification_analysis_strategy(content)
        
        context = AnalysisNotificationContentContext(strategy=strategy_func)
        
        result = context.analysis(self.standard_grid_trade_content)
        
        # 验证结果结构
        assert 'title' in result
        assert 'grid_info' in result
    
    @pytest.mark.local
    def test_analysis_notification_content_context_with_business_type(self):
        """
        测试通知内容分析上下文（使用业务类型）
        """
        # 测试网格交易 + HTML渠道
        context = AnalysisNotificationContentContext(
            notice_business_type=0, 
            channel_type="html"
        )
        result = context.analysis(self.standard_grid_trade_content)
        assert 'title' in result
        
        # 测试网格交易 + 客户端渠道
        with patch('web.services.notice.analyser.notification_analyser.GridTypeDetail.query'):
            context = AnalysisNotificationContentContext(
                notice_business_type=0, 
                channel_type="client"
            )
            # 为客户端测试准备简化的数据
            client_content = {
                "title": "网格交易确认通知",
                "grid_info": []
            }
            result = context.analysis(client_content)
            assert 'title' in result
        
        # 测试网格交易 + Bot渠道（默认）
        context = AnalysisNotificationContentContext(
            notice_business_type=0, 
            channel_type="bot"
        )
        result = context.analysis(self.standard_grid_trade_content)
        assert 'title' in result
    
    @pytest.mark.local
    def test_analysis_notification_content_context_error_cases(self):
        """
        测试通知内容分析上下文错误情况
        """
        # 测试业务类型和策略都为空的情况
        with pytest.raises(Exception) as exc_info:
            AnalysisNotificationContentContext()
        assert 'notice business type and strategy is null' in str(exc_info.value)
    
    @pytest.mark.local
    def test_invalid_notification_content(self):
        """
        测试无效的通知内容
        """
        # 创建无效内容的通知
        invalid_notification = Mock(spec=Notification)
        invalid_notification.id = 2
        invalid_notification.title = "无效通知"
        invalid_notification.content = "invalid json"
        invalid_notification.timestamp = datetime.now()
        invalid_notification.notice_level = 1
        
        strategy = GridTradeBotAnalysisStrategy()
        result = strategy.analysis(invalid_notification)
        
        # 验证错误处理
        assert 'error' in result
        assert result['title'] == "无效通知"
    
    @pytest.mark.local
    def test_missing_required_fields(self):
        """
        测试缺少必需字段的情况
        """
        # 测试缺少title字段
        content_without_title = {
            "grid_info": []
        }
        
        with pytest.raises(Exception) as exc_info:
            grid_trade_html_notification_analysis_strategy(content_without_title)
        assert 'grid trade notification content error' in str(exc_info.value)
        
        # 测试缺少grid_info字段
        content_without_grid_info = {
            "title": "测试通知"
        }
        
        with pytest.raises(Exception) as exc_info:
            grid_trade_html_notification_analysis_strategy(content_without_grid_info)
        assert 'grid trade notification content error' in str(exc_info.value)
    
    @pytest.mark.local
    def test_empty_grid_info(self):
        """
        测试空的网格信息
        """
        empty_content = {
            "title": "空网格通知",
            "grid_info": []
        }
        
        strategy = GridTradeBotAnalysisStrategy()
        mock_notification = Mock(spec=Notification)
        mock_notification.id = 3
        mock_notification.title = "空网格通知"
        mock_notification.content = json.dumps(empty_content)
        mock_notification.timestamp = datetime.now()
        mock_notification.notice_level = 1
        
        result = strategy.analysis(mock_notification)
        
        # 验证空网格信息的处理
        assert len(result['grid_info']) == 0
        assert result['title'] == "空网格通知"
    
    @pytest.mark.local
    def test_multiple_grid_info(self):
        """
        测试多个网格信息
        """
        multi_grid_content = {
            "title": "多网格交易通知",
            "grid_info": [
                {
                    "asset_name": "资产1",
                    "grid_type_name": "小网",
                    "trade_list": [],
                    "current_change": []
                },
                {
                    "asset_name": "资产2",
                    "grid_type_name": "大网",
                    "trade_list": [],
                    "current_change": []
                }
            ]
        }
        
        strategy = GridTradeBotAnalysisStrategy()
        mock_notification = Mock(spec=Notification)
        mock_notification.id = 4
        mock_notification.title = "多网格交易通知"
        mock_notification.content = json.dumps(multi_grid_content)
        mock_notification.timestamp = datetime.now()
        mock_notification.notice_level = 1
        
        result = strategy.analysis(mock_notification)
        
        # 验证多个网格信息的处理
        assert len(result['grid_info']) == 2
        assert result['grid_info'][0]['asset_name'] == "资产1"
        assert result['grid_info'][1]['asset_name'] == "资产2"

    # 保留原有的测试方法以确保向后兼容
    @pytest.mark.local
    def test_grid_trade_bot_notification_analysis_strategy(self):
        """
        查询通知，限制一条数据，如果数据为空则抛出异常，提示没有合适的测试数据.
        如果不为空，判断是否存在通知里面的content是否含有title和grid_info两个列表对象
        """
        # 使用模拟数据
        notice = self.mock_notification
        
        # 解码通知内容
        notice_content = json.loads(notice.content)
        # 判断通知内容是否包含title和grid_info两个列表对象
        if 'title' not in notice_content or 'grid_info' not in notice_content:
            raise Exception('grid trade notification content error')
        # 调用解码通知内容上下文
        def strategy_func(content):
            return grid_trade_bot_notification_analysis_strategy(content)
        context = AnalysisNotificationContentContext(strategy=strategy_func)
        content = context.analysis(notice_content)
        # 判断context是否为空，如果context不为空则测试通过
        assert content is not None

    @pytest.mark.local
    @patch('web.services.notice.analyser.notification_analyser.GridTypeDetailVOSchema')
    @patch('web.models.grid.GridTypeDetail.GridTypeDetail.query')
    def test_grid_trade_client_notification_analysis_strategy(self, mock_query, mock_schema):
        # 模拟数据库查询结果
        mock_grid_detail = Mock()
        mock_grid_detail.id = 101
        mock_grid_detail.gear = '1.0'
        mock_query.filter.return_value.all.return_value = [mock_grid_detail]
        mock_query.get.return_value = mock_grid_detail
        
        # 模拟序列化结果
        mock_schema.return_value.dump.return_value = [{'id': 101, 'gear': '1.0'}]
        
        # 使用模拟数据
        notice = self.mock_notification
        
        # 解码通知内容
        notice_content = json.loads(notice.content)
        # 判断通知内容是否包含title和grid_info两个列表对象
        if 'title' not in notice_content or 'grid_info' not in notice_content:
            raise Exception('grid trade notification content error')
        # 调用解码通知内容上下文
        def strategy_func(content):
            return grid_trade_client_notification_analysis_strategy(content)
        context = AnalysisNotificationContentContext(strategy=strategy_func)
        content = context.analysis(notice_content)
        # 判断context是否为空，如果context不为空则测试通过
        assert content is not None

    # 测试通知内容解析上下文，使用grid_trade_client_notification_analysis_strategy解析通知内容
    @pytest.mark.local
    @patch('web.services.notice.analyser.notification_analyser.GridTypeDetailVOSchema')
    @patch('web.models.grid.GridTypeDetail.GridTypeDetail.query')
    def test_analysis_notification_content_context(self, mock_query, mock_schema):
        # 模拟数据库查询结果
        mock_grid_detail = Mock()
        mock_grid_detail.id = 101
        mock_grid_detail.gear = '1.0'
        mock_query.filter.return_value.all.return_value = [mock_grid_detail]
        mock_query.get.return_value = mock_grid_detail
        
        # 模拟序列化结果
        mock_schema.return_value.dump.return_value = [{'id': 101, 'gear': '1.0'}]
        
        # 使用模拟数据
        notice = self.mock_notification
        
        # 解码通知内容
        notice_content = json.loads(notice.content)
        # 判断通知内容是否包含title和grid_info两个列表对象
        if 'title' not in notice_content or 'grid_info' not in notice_content:
            raise Exception('grid trade notification content error')
        # 调用解码通知内容上下文
        def strategy_func(content):
            return grid_trade_client_notification_analysis_strategy(content)
        context = AnalysisNotificationContentContext(strategy=strategy_func)
        content = context.analysis(notice_content)
        # 判断context是否为空，如果context不为空则测试通过
        assert content is not None

    @pytest.mark.local
    def test_analysis_notification_render_context(self):
        """
        测试通知内容解析上下文，使用grid_trade_html_notification_analysis_strategy解析通知内容
        Returns:

        """
        # 使用模拟数据
        notice = self.mock_notification
        
        # 解码通知内容
        notice_content = json.loads(notice.content)
        # 判断通知内容是否包含title和grid_info两个列表对象
        if 'title' not in notice_content or 'grid_info' not in notice_content:
            raise Exception('grid trade notification content error')
        # 调用解码通知内容上下文
        def strategy_func(content):
            return grid_trade_html_notification_analysis_strategy(content)
        context = AnalysisNotificationContentContext(strategy=strategy_func)
        content = context.analysis(notice_content)
        # 判断context是否为空，如果context不为空则测试通过
        assert content is not None


if __name__ == '__main__':
    pytest.main([__file__])
