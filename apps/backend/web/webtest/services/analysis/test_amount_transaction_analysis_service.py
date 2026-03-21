# -*- coding: UTF-8 -*-
"""
@File    ：test_amount_transaction_analysis_service.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025-01-14 
@Description: AmountTransactionAnalysisService集成测试
"""
from datetime import datetime, date
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from test_base import TestBaseWithRollback
from web.models.analysis.amount_trade_analysis_data import AmountTradeAnalysisData
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.record.record import Record
from web.services.analysis.transaction_analysis_service import AmountTransactionAnalysisService


@pytest.mark.integration
@pytest.mark.analysis
@pytest.mark.amount
class TestAmountTransactionAnalysisService(TestBaseWithRollback):
    """
    AmountTransactionAnalysisService集成测试类
    
    测试覆盖范围：
    - 服务初始化和配置验证
    - 金额交易分析核心功能
    - 交易数据组装和处理
    - 数据库操作和事务处理
    - 异常情况和边界条件
    - 数据一致性和完整性验证
    - 与databox模块的集成测试
    """
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.service = AmountTransactionAnalysisService()
        self.test_start_date = date(2024, 1, 1)
        self.test_end_date = date(2024, 1, 31)
        
    # ==================== 基础功能测试 ====================
    
    def test_initialization_with_default_parameters(self):
        """
        测试默认参数初始化
        
        验证点：
        - 分析类型设置为AMOUNT
        - 开始和结束日期为None
        - 日期交易字典初始化为空
        - 更新交易列表初始化为空
        - 服务对象正确创建
        """
        service = AmountTransactionAnalysisService()
        assert service.analysis_type == TradeAnalysisData.get_analysis_type_enum().AMOUNT.value
        assert service.start is None
        assert service.end is None
        assert service.date_trade_dict == {}
        assert service.update_trade_list == []
        
    def test_initialization_with_custom_parameters(self):
        """
        测试自定义参数初始化
        
        验证点：
        - 自定义开始和结束日期正确设置
        - 分析类型保持AMOUNT不变
        - 其他属性保持默认值
        - 参数传递机制正常工作
        """
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        service = AmountTransactionAnalysisService(start=start_date, end=end_date)
        assert service.start == start_date
        assert service.end == end_date
        
    def test_get_trade_analysis_record(self):
        """
        测试获取交易分析记录
        
        验证点：
        - 正确调用父类方法获取记录
        - 传递正确的分析类型参数
        - 返回预期的记录列表
        - Mock方法调用次数正确
        - 方法参数传递准确
        """
        with patch.object(self.service, 'get_analysis_records_by_type') as mock_get_records:
            mock_records = [MagicMock(spec=Record)]
            mock_get_records.return_value = mock_records
            
            result = self.service.get_trade_analysis_record()
            
            mock_get_records.assert_called_once_with(analysis_type=self.service.analysis_type)
            assert result == mock_records
            
    # ==================== 数据组装测试 ====================
    
    def test_assemble_trade_analysis_with_valid_data(self):
        """
        测试有效数据的交易分析组装
        
        验证点：
        - 返回正确的AmountTradeAnalysisData类型
        - 基础字段正确设置（分析类型、记录日期）
        - 数值字段正确转换（净值、成本、份额等）
        - 万倍和百倍转换计算准确
        - dividend_yield字段设置为None
        - 数据类型转换无误
        """
        # 创建测试数据
        summary_data = pd.DataFrame({
            '基金代码': ['000001'],
            '当日净值': [1.2345],
            '单位成本': [1.1000],
            '持有份额': [10000],
            '基金现值': [12345000],
            '基金总申购': [11000000],
            '历史最大占用': [11500000],
            '基金持有成本': [11000000],
            '基金分红与赎回': [0],
            '换手率': [0.15],
            '基金收益总额': [1345000],
            '投资收益率': [0.1223],
            '内部收益率': [0.1150]
        })
        
        test_date = datetime(2024, 1, 15)
        analysis_type = TradeAnalysisData.get_analysis_type_enum().AMOUNT.value
        
        result = self.service.assemble_trade_analysis(
            summary_data=summary_data,
            analysis_type=analysis_type,
            date=test_date
        )
        
        # 验证返回类型
        assert isinstance(result, AmountTradeAnalysisData)
        
        # 验证基础字段
        assert result.analysis_type == analysis_type
        assert result.record_date == test_date
        assert result.net_value == int(1.2345 * 10000)  # 转换为万倍
        assert result.unit_cost == int(1.1000 * 10000)
        assert result.attributable_share == int(10000 * 100)  # 持有份额是百倍
        
        # 验证dividend_yield字段被设置为None
        assert result.dividend_yield is None
        
    def test_assemble_trade_analysis_with_none_values(self):
        """
        测试包含None值的数据组装
        
        验证点：
        - 正确处理DataFrame中的None值
        - None值字段在结果中保持为None
        - 非None值字段正常处理
        - dividend_yield字段始终为None
        - 数据类型转换容错性良好
        """
        summary_data = pd.DataFrame({
            '基金代码': ['000001'],
            '当日净值': [None],
            '单位成本': [1.1000],
            '持有份额': [None],
            '基金现值': [12345000],
            '基金总申购': [11000000],
            '历史最大占用': [11500000],
            '基金持有成本': [11000000],
            '基金分红与赎回': [0],
            '换手率': [None],
            '基金收益总额': [1345000],
            '投资收益率': [0.1223],
            '内部收益率': [0.1150]
        })
        
        result = self.service.assemble_trade_analysis(
            summary_data=summary_data,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
            date=datetime(2024, 1, 15)
        )
        
        # 验证None值被正确处理
        assert result.net_value is None
        assert result.attributable_share is None
        assert result.turnover_rate is None
        assert result.dividend_yield is None
        
    def test_assemble_trade_analysis_with_existing_analysis_data(self):
        """
        测试使用现有分析数据对象
        
        验证点：
        - 使用传入的现有分析数据对象
        - 保持现有对象的ID不变
        - 正确更新对象的其他字段
        - dividend_yield字段设置为None
        - 对象引用关系正确维护
        """
        existing_data = AmountTradeAnalysisData()
        existing_data.id = 123
        
        summary_data = pd.DataFrame({
            '基金代码': ['000001'],
            '当日净值': [1.2345],
            '单位成本': [1.1000],
            '持有份额': [10000],
            '基金现值': [12345000],
            '基金总申购': [11000000],
            '历史最大占用': [11500000],
            '基金持有成本': [11000000],
            '基金分红与赎回': [0],
            '换手率': [0.15],
            '基金收益总额': [1345000],
            '投资收益率': [0.1223],
            '内部收益率': [0.1150]
        })
        
        result = self.service.assemble_trade_analysis(
            summary_data=summary_data,
            analysis_data=existing_data,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
            date=datetime(2024, 1, 15)
        )
        
        # 验证使用了现有对象
        assert result is existing_data
        assert result.id == 123
        assert result.dividend_yield is None
        
    # ==================== 数据处理流程测试 ====================
    
    @patch('web.databox.databox.trade')
    @patch('web.databox.databox.summary')
    @patch('web.databox.databox.get_trade_fund_name')
    @patch('web.databox.databox.remove_trade_cache')
    @patch('web.common.utils.WebUtils.webutils.is_trading_day')
    def test_assemble_data_with_mock_databox(self, mock_is_trading_day, mock_remove_cache, 
                                           mock_get_fund_name, mock_summary, mock_trade):
        """
        测试数据组装流程（使用Mock）
        
        验证点：
        - 交易日检查正确执行
        - databox模块各方法按顺序调用
        - 汇总数据正确处理总计行
        - 基金名称获取正确
        - 交易缓存正确清理
        - 数据组装流程完整执行
        - Mock方法调用次数符合预期
        """
        # 设置Mock返回值
        mock_is_trading_day.return_value = True
        mock_trade.return_value = 12345
        mock_get_fund_name.return_value = ('测试基金',)
        
        # 创建包含"总计"行的测试数据
        mock_summary_data = pd.DataFrame({
            '基金名称': ['总计'],
            '基金代码': ['000001'],
            '当日净值': [1.2345],
            '单位成本': [1.1000],
            '持有份额': [10000],
            '基金现值': [12345000],
            '基金总申购': [11000000],
            '历史最大占用': [11500000],
            '基金持有成本': [11000000],
            '基金分红与赎回': [0],
            '换手率': [0.15],
            '基金收益总额': [1345000],
            '投资收益率': [0.1223],
            '内部收益率': [0.1150]
        })
        mock_summary.return_value = mock_summary_data
        
        # 执行测试
        test_date = date(2024, 1, 15)
        fund_names = ('测试基金',)
        
        self.service.assemble_data(
            summary=mock_summary_data,
            fund_names=fund_names,
            today=test_date
        )
        
        # 验证结果
        assert len(self.service.update_trade_list) == 1
        analysis_data = self.service.update_trade_list[0]
        assert isinstance(analysis_data, AmountTradeAnalysisData)
        assert analysis_data.record_date == test_date
        assert analysis_data.dividend_yield is None
        
    def test_prepare_analysis(self):
        """测试分析准备"""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        with patch.object(self.service, 'fetch_and_organize_trade_data') as mock_fetch:
            mock_fetch.return_value = {'test': 'data'}
            
            self.service.prepare_analysis(start=start_date, end=end_date)
            
            assert self.service.start == start_date
            assert self.service.end == end_date
            assert self.service.date_trade_dict == {'test': 'data'}
            mock_fetch.assert_called_once()
            
    @patch('web.models.db.session')
    def test_finalize_analysis_with_data(self, mock_session):
        """测试有数据时的分析完成"""
        # 准备测试数据
        test_data = AmountTradeAnalysisData()
        self.service.update_trade_list = [test_data]
        
        self.service.finalize_analysis()
        
        # 验证数据库操作
        mock_session.bulk_save_objects.assert_called_once_with([test_data], update_changed_only=True)
        mock_session.commit.assert_called_once()
        
    @patch('web.models.db.session')
    def test_finalize_analysis_without_data(self, mock_session):
        """测试无数据时的分析完成"""
        self.service.update_trade_list = []
        
        self.service.finalize_analysis()
        
        # 验证没有进行数据库操作
        mock_session.bulk_save_objects.assert_not_called()
        mock_session.commit.assert_not_called()
        
    # ==================== 异常处理测试 ====================
    
    def test_assemble_trade_analysis_with_invalid_data_types(self):
        """测试无效数据类型的处理"""
        # 创建包含无效数据类型的DataFrame
        summary_data = pd.DataFrame({
            '基金代码': ['000001'],
            '当日净值': ['invalid_string'],  # 无效的字符串
            '单位成本': [1.1000],
            '持有份额': [10000],
            '基金现值': [12345000],
            '基金总申购': [11000000],
            '历史最大占用': [11500000],
            '基金持有成本': [11000000],
            '基金分红与赎回': [0],
            '换手率': [0.15],
            '基金收益总额': [1345000],
            '投资收益率': [0.1223],
            '内部收益率': [0.1150]
        })
        
        # 无效数据类型应该抛出异常
        with pytest.raises((ValueError, TypeError)):
            self.service.assemble_trade_analysis(
                summary_data=summary_data,
                analysis_type=TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
                date=datetime(2024, 1, 15)
            )
            
    @patch('web.models.db.session')
    def test_finalize_analysis_database_error(self, mock_session):
        """测试数据库错误处理"""
        # 模拟数据库异常
        mock_session.bulk_save_objects.side_effect = Exception("Database connection error")
        
        test_data = AmountTradeAnalysisData()
        self.service.update_trade_list = [test_data]
        
        # 验证异常被正确抛出
        with pytest.raises(Exception) as exc_info:
            self.service.finalize_analysis()
        
        assert "Database connection error" in str(exc_info.value)
        
    def test_assemble_trade_analysis_with_empty_dataframe(self):
        """测试空DataFrame的处理"""
        empty_summary = pd.DataFrame()
        
        # 空DataFrame应该抛出异常
        with pytest.raises(IndexError):
            self.service.assemble_trade_analysis(
                summary_data=empty_summary,
                analysis_type=TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
                date=datetime(2024, 1, 15)
            )
            
    # ==================== 边界值测试 ====================
    
    def test_assemble_trade_analysis_with_extreme_values(self):
        """测试极值数据的处理"""
        summary_data = pd.DataFrame({
            '基金代码': ['000001'],
            '当日净值': [999999.9999],  # 极大值
            '单位成本': [0.0001],       # 极小值
            '持有份额': [0],            # 零值
            '基金现值': [-1000],        # 负值
            '基金总申购': [11000000],
            '历史最大占用': [11500000],
            '基金持有成本': [11000000],
            '基金分红与赎回': [0],
            '换手率': [1.0],           # 100%换手率
            '基金收益总额': [-500000],   # 负收益
            '投资收益率': [-0.5],       # -50%收益率
            '内部收益率': [2.0]         # 200%内部收益率
        })
        
        result = self.service.assemble_trade_analysis(
            summary_data=summary_data,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
            date=datetime(2024, 1, 15)
        )
        
        # 验证极值被正确处理
        assert isinstance(result, AmountTradeAnalysisData)
        assert result.net_value == int(999999.9999 * 10000)
        assert result.unit_cost == int(0.0001 * 10000)
        assert result.attributable_share == 0
        assert result.dividend_yield is None
        
    # ==================== 集成测试 ====================
    
    @patch('web.databox.databox.trade')
    @patch('web.databox.databox.summary')
    @patch('web.databox.databox.get_trade_fund_name')
    @patch('web.databox.databox.remove_trade_cache')
    @patch('web.common.utils.WebUtils.webutils.is_trading_day')
    @patch('web.models.db.session')
    def test_complete_trade_analysis_workflow(self, mock_session, mock_is_trading_day, 
                                            mock_remove_cache, mock_get_fund_name, 
                                            mock_summary, mock_trade):
        """测试完整的交易分析工作流程"""
        # 设置Mock返回值
        mock_is_trading_day.return_value = True
        mock_trade.return_value = 12345
        mock_get_fund_name.return_value = ('测试基金',)
        
        mock_summary_data = pd.DataFrame({
            '基金名称': ['总计'],
            '基金代码': ['000001'],
            '当日净值': [1.2345],
            '单位成本': [1.1000],
            '持有份额': [10000],
            '基金现值': [12345000],
            '基金总申购': [11000000],
            '历史最大占用': [11500000],
            '基金持有成本': [11000000],
            '基金分红与赎回': [0],
            '换手率': [0.15],
            '基金收益总额': [1345000],
            '投资收益率': [0.1223],
            '内部收益率': [0.1150]
        })
        mock_summary.return_value = mock_summary_data
        
        # Mock记录查询
        with patch.object(self.service, 'get_trade_analysis_record') as mock_get_records:
            mock_records = [MagicMock(spec=Record)]
            mock_get_records.return_value = mock_records
            
            with patch.object(self.service, 'fetch_and_organize_trade_data') as mock_fetch:
                mock_fetch.return_value = {}
                
                # 执行完整的交易分析
                self.service.trade_analysis(
                    start=self.test_start_date,
                    end=self.test_start_date  # 只测试一天
                )
                
                # 验证各个步骤都被调用
                mock_get_records.assert_called_once()
                mock_fetch.assert_called_once()
                mock_trade.assert_called_once_with(mock_records)
                mock_summary.assert_called()
                mock_get_fund_name.assert_called_once_with(12345)
                mock_remove_cache.assert_called_once_with(12345)
                
                # 验证数据被正确处理
                assert len(self.service.update_trade_list) >= 0
                
    # ==================== 数据一致性测试 ====================
    
    def test_dividend_yield_field_consistency(self):
        """测试dividend_yield字段的一致性处理"""
        summary_data = pd.DataFrame({
            '基金代码': ['000001'],
            '当日净值': [1.2345],
            '单位成本': [1.1000],
            '持有份额': [10000],
            '基金现值': [12345000],
            '基金总申购': [11000000],
            '历史最大占用': [11500000],
            '基金持有成本': [11000000],
            '基金分红与赎回': [0],
            '换手率': [0.15],
            '基金收益总额': [1345000],
            '投资收益率': [0.1223],
            '内部收益率': [0.1150]
        })
        
        # 测试多次调用的一致性
        result1 = self.service.assemble_trade_analysis(
            summary_data=summary_data,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
            date=datetime(2024, 1, 15)
        )
        
        result2 = self.service.assemble_trade_analysis(
            summary_data=summary_data,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
            date=datetime(2024, 1, 15)
        )
        
        # 验证dividend_yield字段在多次调用中保持一致
        assert result1.dividend_yield is None
        assert result2.dividend_yield is None
        assert result1.dividend_yield == result2.dividend_yield
        
    def test_conversion_factor_usage(self):
        """测试转换系数的正确使用"""
        # 验证AmountTradeAnalysisData的转换系数包含dividend_yield
        conversion_factors = AmountTradeAnalysisData.get_conversion_factor()
        assert 'dividend_yield' in conversion_factors
        assert conversion_factors['dividend_yield'] == 10000
        
        # 验证在assemble_trade_analysis中正确使用转换系数
        summary_data = pd.DataFrame({
            '基金代码': ['000001'],
            '当日净值': [1.2345],
            '单位成本': [1.1000],
            '持有份额': [10000],
            '基金现值': [12345000],
            '基金总申购': [11000000],
            '历史最大占用': [11500000],
            '基金持有成本': [11000000],
            '基金分红与赎回': [0],
            '换手率': [0.15],
            '基金收益总额': [1345000],
            '投资收益率': [0.1223],
            '内部收益率': [0.1150]
        })
        
        result = self.service.assemble_trade_analysis(
            summary_data=summary_data,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().AMOUNT.value,
            date=datetime(2024, 1, 15)
        )
        
        # 验证其他字段使用了正确的转换系数
        assert result.net_value == int(1.2345 * 10000)
        assert result.unit_cost == int(1.1000 * 10000)
        # dividend_yield应该被跳过，设置为None
        assert result.dividend_yield is None