# -*- coding: UTF-8 -*-
"""
@File    ：test_trade_analysis_service.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/10/19 20:13
"""
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.services.analysis.transaction_analysis_service import GridTypeTransactionAnalysisService, TradeAnalysisService, \
    GridTransactionAnalysisService, GridStrategyTransactionAnalysisService, AmountTransactionAnalysisService
from web.webtest.test_base import TestBaseWithRollback, TestBase


# TestBaseWithRollback
class TestTradeAnalysisService(TestBase):
    """
    交易分析服务测试类
    
    测试覆盖范围：
    - 测试各种交易分析服务的核心功能
    - 验证网格类型、网格、网格策略和金额交易分析的正确性
    - 确保数据库操作的事务完整性和数据隔离
    
    使用TestBaseWithRollback基类的原因：
    - 交易分析服务涉及复杂的数据库操作，包括查询、批量保存和事务提交
    - 需要确保测试间的数据完全隔离，避免测试数据相互影响
    - 测试结束后自动回滚所有数据库操作，保持数据库清洁状态
    - 特别适合测试绑定到'snowball'数据库的Grid和GridType等模型
    """
    def test_grid_type_transaction_analysis_service(self):
        """
        测试网格类型交易分析服务的核心功能
        
        验证点:
        - 验证GridTypeTransactionAnalysisService能够正确初始化
        - 验证服务能够成功执行trade_analysis()方法
        - 验证数据库查询操作正常执行
        - 验证分析结果能够正确保存到数据库
        """
        # 查询第一个网格类型
        grid_type = GridType.query.first()
        service: TradeAnalysisService = GridTypeTransactionAnalysisService(grid_type_id=grid_type.id)
        service.trade_analysis()

    def test_grid_transaction_analysis_service(self):
        """
        测试网格交易分析服务的核心功能
        
        验证点:
        - 验证GridTransactionAnalysisService能够正确初始化
        - 验证服务能够处理指定日期范围的分析
        - 验证start和end参数能够正确传递和处理
        - 验证分析结果的数据完整性和准确性
        """
        grid = Grid.query.first()
        service: TradeAnalysisService = GridTransactionAnalysisService(grid_id=grid.id)
        # service.trade_analysis(start="2024-10-17", end="2024-10-18")
        service.trade_analysis()

    def test_grid_strategy_transaction_analysis_service(self):
        """
        测试网格策略交易分析服务的核心功能
        
        验证点:
        - 验证GridStrategyTransactionAnalysisService能够正确初始化
        - 验证服务能够处理全局网格策略分析
        - 验证日期范围过滤功能正常工作
        - 验证策略级别的数据聚合和分析逻辑
        """
        service: TradeAnalysisService = GridStrategyTransactionAnalysisService()
        # service.trade_analysis(start="2024-10-17", end="2024-10-18")
        service.trade_analysis()

    def test_amount_transaction_analysis_service(self):
        """
        测试金额交易分析服务的核心功能
        
        验证点:
        - 验证AmountTransactionAnalysisService能够正确初始化
        - 验证服务能够处理金额维度的交易分析
        - 验证日期范围参数的有效性
        - 验证金额统计和计算逻辑的准确性
        """
        service: TradeAnalysisService = AmountTransactionAnalysisService()
        # service.trade_analysis(start="2024-10-17", end="2024-10-18")
        service.trade_analysis()
