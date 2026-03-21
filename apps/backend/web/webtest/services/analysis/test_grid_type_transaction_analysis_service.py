# -*- coding: UTF-8 -*-
"""
@File    ：test_grid_type_transaction_analysis_service.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025-01-14
@Description: GridTypeTransactionAnalysisService集成测试用例
"""
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from web.models import db
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.asset.asset import Asset
from web.models.asset.asset_code import AssetCode
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.record.record import Record
from web.services.analysis.transaction_analysis_service import GridTypeTransactionAnalysisService
from web.webtest.test_base import TestBaseWithRollback


@pytest.mark.integration
@pytest.mark.analysis
@pytest.mark.grid_type
class TestGridTypeTransactionAnalysisService(TestBaseWithRollback):
    """
    GridTypeTransactionAnalysisService集成测试类
    
    测试覆盖范围：
    - 服务初始化和配置
    - 核心业务方法功能验证
    - 数据库操作和事务处理
    - 异常情况和边界条件
    - 数据一致性和完整性
    - 空值处理和边界测试
    """
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, rollback_session):
        """为每个测试方法设置测试数据"""
        # 创建测试数据 - 使用动态ID避免主键冲突
        import time
        import random
        unique_id = int(time.time() * 1000) + random.randint(1, 1000)
        self.test_date = date(2024, 1, 15)
        
        # 创建测试用的Asset对象
        self.test_asset = Asset(
            asset_code="000001",
            asset_name="测试资产",
            asset_type=1,
            currency=1,
            market=1,
            asset_status=0
        )
        
        # 先添加Asset到session并flush以获取ID
        rollback_session.add(self.test_asset)
        rollback_session.flush()
        self.test_asset_id = self.test_asset.id
        
        # 创建测试用的Grid对象
        self.test_grid = Grid(
            grid_name="测试网格",
            asset_id=self.test_asset_id,
            grid_status=Grid.get_status_enum().ENABLE.value
        )
        
        # 添加Grid到session并flush以获取ID
        rollback_session.add(self.test_grid)
        rollback_session.flush()
        self.test_grid_id = self.test_grid.id
        
        # 创建测试用的AssetCode对象
        self.test_asset_code = AssetCode(
            code_xq="000001",
            asset_id=self.test_asset_id
        )
        
        # 创建测试用的GridType对象
        self.test_grid_type = GridType(
            grid_id=self.test_grid_id,
            grid_type_status=0,
            type_name="测试网格类型",
            asset_id=self.test_asset_id
        )
        
        # 添加GridType到session并flush以获取ID
        rollback_session.add(self.test_grid_type)
        rollback_session.flush()
        self.test_grid_type_id = self.test_grid_type.id
        
        # 创建测试用的GridTypeDetail对象
        self.test_grid_type_detail = GridTypeDetail(
            grid_type_id=self.test_grid_type_id,
            grid_id=self.test_grid_id,
            gear="1",
            monitor_type=GridTypeDetail.get_monitor_type_enum().SELL.value,
            trigger_sell_price=11000,  # 1.1元
            sell_price=11000,  # 1.1元
            sell_shares=1000,  # 1000股
            actual_sell_shares=1000,  # 实际1000股
            sell_amount=11000000,  # 1100元
            trigger_purchase_price=9000,  # 0.9元
            purchase_price=9000,  # 0.9元
            purchase_amount=100000,  # 100元
            purchase_shares=1111,  # 1111股
            profit=1000000,  # 100元收益
            save_share_profit=0,  # 留股收益
            save_share=0,  # 留存股数
            is_current=False  # 不是当前档位
        )
        
        # 创建测试用的Record对象
        self.test_record = Record(
            asset_id=self.test_asset_id,
            transactions_direction=Record.get_record_directoin_enum().SELL.value,
            transactions_date=datetime.combine(self.test_date, datetime.min.time())
        )
        
        # 添加剩余对象到rollback_session
        rollback_session.add_all([
            self.test_asset_code,
            self.test_grid_type_detail,
            self.test_record
        ])
        rollback_session.flush()
        
        # 创建GridTypeRecord关联记录
        self.test_grid_type_record = GridTypeRecord(
            grid_type_id=self.test_grid_type_id,
            record_id=self.test_record.id
        )
        rollback_session.add(self.test_grid_type_record)
        rollback_session.flush()
    
    # 初始化测试
    def test_init_with_valid_grid_type_id(self):
        """
        测试使用有效网格类型ID初始化服务
        
        验证点：
        - 服务正确初始化所有属性
        - 网格类型ID正确设置
        - 分析类型设置正确
        - 更新列表和日期字典正确初始化
        """
        service = GridTypeTransactionAnalysisService(
            grid_type_id=self.test_grid_type_id,
            start=date(2024, 1, 1),
            end=date(2024, 1, 31)
        )
        
        assert service.grid_type_id == self.test_grid_type_id
        assert service.analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value
        assert service.start == date(2024, 1, 1)
        assert service.end == date(2024, 1, 31)
        assert isinstance(service.date_trade_dict, dict)
        assert isinstance(service.update_trade_list, list)
        assert len(service.update_trade_list) == 0
        assert len(service.date_trade_dict) == 0
    
    def test_init_with_none_grid_type_id(self):
        """
        测试使用None网格类型ID初始化服务
        
        验证点：
        - grid_type_id为None时应该抛出ValueError异常
        - 不允许None的grid_type_id
        """
        with pytest.raises(ValueError, match="网格类型ID不能为None"):
            GridTypeTransactionAnalysisService(grid_type_id=None)
    
    def test_init_with_invalid_grid_type_id(self):
        """
        测试使用无效网格类型ID初始化服务
        
        验证点：
        - 不存在的网格类型ID应该抛出ValueError异常
        - 不允许无效的grid_type_id
        """
        with pytest.raises(ValueError, match="未找到ID为99999的网格类型"):
            GridTypeTransactionAnalysisService(grid_type_id=99999)
    
    def test_init_with_default_dates(self):
        """
        测试使用默认日期初始化服务
        
        验证点：
        - start和end默认为None
        - 其他属性正确初始化
        """
        service = GridTypeTransactionAnalysisService(grid_type_id=self.test_grid_type_id)
        
        assert service.start is None
        assert service.end is None
        assert service.grid_type_id == self.test_grid_type_id
    
    # fetch_and_organize_trade_data方法测试
    def test_fetch_and_organize_trade_data_success(self):
        """
        测试成功获取和组织交易数据
        
        验证点：
        - 正确查询GridTradeAnalysisData
        - 返回正确的日期交易字典
        - 数据按日期正确组织
        """
        # 创建测试用的GridTradeAnalysisData，使用datetime类型
        test_datetime = datetime.combine(self.test_date, datetime.min.time())
        grid_trade_data = GridTradeAnalysisData(
            asset_id=self.test_asset_id,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value,
            business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
            record_date=test_datetime,
            grid_type_id=self.test_grid_type_id,
            sub_analysis_type='grid_trade_analysis'
        )
        
        # 保存到数据库
        db.session.add(grid_trade_data)
        db.session.commit()
        
        service = GridTypeTransactionAnalysisService(grid_type_id=self.test_grid_type_id)
        result = service.fetch_and_organize_trade_data()
        
        assert isinstance(result, dict)
        assert test_datetime in result
        assert isinstance(result[test_datetime], GridTradeAnalysisData)
        assert result[test_datetime].grid_type_id == self.test_grid_type_id
    
    def test_fetch_and_organize_trade_data_no_data(self):
        """
        测试没有交易数据的情况
        
        验证点：
        - 返回空字典
        - 不会抛出异常
        """
        service = GridTypeTransactionAnalysisService(grid_type_id=self.test_grid_type_id)
        result = service.fetch_and_organize_trade_data()
        
        assert isinstance(result, dict)
        assert len(result) == 0
    
    def test_fetch_and_organize_trade_data_with_date_filter(self):
        """
        测试带日期过滤的数据获取
        
        验证点：
        - 正确应用日期过滤条件
        - 只返回指定日期范围内的数据
        """
        # 创建不同日期的测试数据，使用datetime类型
        datetime1 = datetime.combine(date(2024, 1, 10), datetime.min.time())
        datetime2 = datetime.combine(date(2024, 1, 20), datetime.min.time())
        
        grid_trade_data1 = GridTradeAnalysisData(
            asset_id=self.test_asset_id,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value,
            business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
            record_date=datetime1,
            grid_type_id=self.test_grid_type_id,
            sub_analysis_type='grid_trade_analysis'
        )
        
        grid_trade_data2 = GridTradeAnalysisData(
            asset_id=self.test_asset_id,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value,
            business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
            record_date=datetime2,
            grid_type_id=self.test_grid_type_id,
            sub_analysis_type='grid_trade_analysis'
        )
        
        db.session.add_all([grid_trade_data1, grid_trade_data2])
        db.session.commit()
        
        service = GridTypeTransactionAnalysisService(
            grid_type_id=self.test_grid_type_id,
            start=date(2024, 1, 15),
            end=date(2024, 1, 25)
        )
        result = service.fetch_and_organize_trade_data()
        
        assert len(result) == 1
        assert datetime2 in result
        assert datetime1 not in result
    
    # assemble_data方法测试
    @patch('web.services.analysis.transaction_analysis_service.GridTypeTransactionAnalysisService.assemble_trade_analysis')
    @patch('web.services.analysis.transaction_analysis_service.GridTypeTransactionAnalysisService.assemble_grid_trade_analysis')
    def test_assemble_data_success(self, mock_assemble_grid, mock_assemble_trade):
        """
        测试数据组装成功场景
        
        验证点：
        - 正确处理DataFrame数据
        - 调用交易分析组装方法时传入正确参数
        - 验证组装后的参数内容是否符合预期
        - 更新trade_list正确
        - 正确设置grid_type_id
        """
        # 准备测试数据
        summary_data = pd.DataFrame({
            '基金名称': ['测试基金'],
            '基金代码': ['000001'],
            '当日净值': [1.0],
            '单位成本': [0.95],
            '持有份额': [1000],
            '基金现值': [1000],
            '基金总申购': [950],
            '历史最大占用': [950],
            '基金持有成本': [950],
            '基金分红与赎回': [0],
            '换手率': [0.1],
            '基金收益总额': [50],
            '投资收益率': [0.0526],
            '内部收益率': [0.0526]
        })
        
        fund_names = ('测试基金',)
        today = self.test_date
        
        # Mock返回值
        mock_trade_analysis = TradeAnalysisData(
            asset_id=self.test_asset_id,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value,
            record_date=today,
            unit_cost=95000,  # 0.95 * 100000
            present_value=100000,  # 1000 * 100
            purchase_amount=95000,  # 950 * 100
            maximum_occupancy=95000,  # 950 * 100
            holding_cost=95000,  # 950 * 100
            profit=5000,  # 50 * 100
            investment_yield=526,  # 0.0526 * 10000
            irr=526  # 0.0526 * 10000
        )
        mock_assemble_trade.return_value = mock_trade_analysis
        
        mock_grid_analysis = GridTradeAnalysisData(
            asset_id=self.test_asset_id,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value,
            business_type=GridTradeAnalysisData.get_business_type_enum().GRID_STRATEGY_ANALYSIS.value,
            record_date=today,
            sub_analysis_type='grid_trade_analysis',
            sell_times=2,
            estimate_maximum_occupancy=1000,
            holding_times=3,
            # 继承TradeAnalysisData的字段
            unit_cost=95000,
            present_value=100000,
            purchase_amount=95000,
            maximum_occupancy=95000,
            holding_cost=95000,
            profit=5000,
            investment_yield=526,
            irr=526
        )
        mock_assemble_grid.return_value = mock_grid_analysis
        
        # 创建服务并设置必要属性
        service = GridTypeTransactionAnalysisService(grid_type_id=self.test_grid_type_id)
        service.records = [self.test_record]
        service.grid_type_details = [self.test_grid_type_detail]
        
        # 执行测试
        service.assemble_data(summary_data, fund_names, today)
        
        # 验证assemble_trade_analysis调用参数
        mock_assemble_trade.assert_called_once()
        call_args = mock_assemble_trade.call_args
        assert call_args[1]['analysis_type'] == TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value
        assert call_args[1]['date'] == today
        assert call_args[1]['asset_id'] == self.test_grid_type.asset_id
        # 验证传入的summary_data是否正确过滤
        passed_summary = call_args[1]['summary_data']
        assert len(passed_summary) == 1
        assert passed_summary.iloc[0]['基金名称'] == '测试基金'
        
        # 验证assemble_grid_trade_analysis调用参数
        mock_assemble_grid.assert_called_once()
        grid_call_args = mock_assemble_grid.call_args
        assert grid_call_args[1]['date'] == today
        assert grid_call_args[1]['analysis_data'] == mock_trade_analysis
        assert grid_call_args[1]['grid_type_details'] == service.grid_type_details
        assert grid_call_args[1]['records'] == service.records
        
        # 验证update_trade_list更新
        assert len(service.update_trade_list) == 1
        result_data = service.update_trade_list[0]
        assert isinstance(result_data, GridTradeAnalysisData)
        
        # 验证组装后的参数内容是否符合预期
        assert result_data.grid_type_id == self.test_grid_type_id
        assert result_data.asset_id == self.test_asset_id
        assert result_data.analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value
        assert result_data.record_date == today
        assert result_data.sub_analysis_type == 'grid_trade_analysis'
        assert result_data.business_type == GridTradeAnalysisData.get_business_type_enum().GRID_STRATEGY_ANALYSIS.value
        
        # 验证继承的TradeAnalysisData字段
        assert result_data.unit_cost == 95000
        assert result_data.present_value == 100000
        assert result_data.purchase_amount == 95000
        assert result_data.maximum_occupancy == 95000
        assert result_data.holding_cost == 95000
        assert result_data.profit == 5000
        assert result_data.investment_yield == 526
        assert result_data.irr == 526
        
        # 验证GridTradeAnalysisData特有字段
        assert result_data.sell_times == 2
        assert result_data.estimate_maximum_occupancy == 1000
        assert result_data.holding_times == 3
    
    def test_assemble_data_empty_fund_names(self):
        """
        测试空基金名称列表的处理
        
        验证点：
        - 空基金名称列表会抛出ValueError异常
        - 异常信息正确
        """
        summary_data = pd.DataFrame({
            '基金名称': ['总计'],
            '买入金额': [1000.0],
            '卖出金额': [500.0],
            '持有金额': [500.0]
        })
        fund_names = ()  # 空的基金名称元组
        today = self.test_date
        
        service = GridTypeTransactionAnalysisService(grid_type_id=self.test_grid_type_id)
        
        with pytest.raises(ValueError, match="基金名称列表不能为空"):
            service.assemble_data(summary_data, fund_names, today)
    
    def test_assemble_data_none_values(self):
        """
        测试None值的处理
        
        验证点：
        - 能够处理None的summary_data
        - 能够处理None的fund_names
        - 能够处理None的today
        """
        service = GridTypeTransactionAnalysisService(grid_type_id=self.test_grid_type_id)
        
        # 测试None summary_data
        with pytest.raises(AttributeError):
            service.assemble_data(None, ('测试基金',), self.test_date)
        
        # 测试None fund_names
        summary_data = pd.DataFrame({'基金名称': ['测试基金']})
        with pytest.raises(TypeError):
            service.assemble_data(summary_data, None, self.test_date)
    
    # finalize_analysis方法测试
    def test_finalize_analysis_success(self):
        """
        测试分析完成处理成功场景
        
        验证点：
        - 正确保存GridTradeAnalysisData对象
        - 正确设置grid_type_id关联
        - 数据库事务正确提交
        """
        # 准备测试数据
        grid_analysis = GridTradeAnalysisData(
            asset_id=self.test_asset_id,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value,
            business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
            record_date=self.test_date,
            grid_type_id=self.test_grid_type_id,
            sub_analysis_type='grid_trade_analysis'
        )
        
        service = GridTypeTransactionAnalysisService(grid_type_id=self.test_grid_type_id)
        service.update_trade_list = [grid_analysis]
        
        # 执行测试
        service.finalize_analysis()
        
        # 验证数据库中的数据
        saved_grid_analysis = GridTradeAnalysisData.query.filter_by(
            grid_type_id=self.test_grid_type_id
        ).first()
        assert saved_grid_analysis is not None
        assert saved_grid_analysis.asset_id == self.test_asset_id
        assert saved_grid_analysis.grid_type_id == self.test_grid_type_id
    
    def test_finalize_analysis_empty_update_list(self):
        """
        测试空更新列表的处理
        
        验证点：
        - 空列表不会导致错误
        - 数据库中没有新增数据
        """
        service = GridTypeTransactionAnalysisService(grid_type_id=self.test_grid_type_id)
        service.update_trade_list = []
        
        # 执行测试
        service.finalize_analysis()
        
        # 验证数据库中没有相关数据
        assert GridTradeAnalysisData.query.filter_by(
            grid_type_id=self.test_grid_type_id
        ).count() == 0
    
    def test_finalize_analysis_none_update_list(self):
        """
        测试None更新列表的处理
        
        验证点：
        - None列表不会导致错误
        - 能够优雅处理None值
        - 数据库中没有新增数据
        """
        service = GridTypeTransactionAnalysisService(grid_type_id=self.test_grid_type_id)
        service.update_trade_list = None
        
        # 执行测试 - None值应该被优雅处理，不抛出异常
        service.finalize_analysis()
        
        # 验证数据库中没有相关数据
        assert GridTradeAnalysisData.query.filter_by(
            grid_type_id=self.test_grid_type_id
        ).count() == 0
    
    @patch('web.models.db.session.bulk_save_objects')
    @patch('web.models.db.session.commit')
    def test_finalize_analysis_database_error(self, mock_commit, mock_bulk_save):
        """
        测试数据库操作异常处理
        
        验证点：
        - 数据库异常能够正确抛出
        - 不会导致程序崩溃
        """
        mock_bulk_save.side_effect = Exception("数据库连接失败")
        
        service = GridTypeTransactionAnalysisService(grid_type_id=self.test_grid_type_id)
        service.update_trade_list = [
            GridTradeAnalysisData(
                business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
                grid_type_id=self.test_grid_type_id
            )
        ]
        
        with pytest.raises(Exception, match="数据库连接失败"):
            service.finalize_analysis()
    
    # 边界条件和异常测试
    def test_service_with_zero_grid_type_id(self):
        """
        测试网格类型ID为0的情况
        
        验证点：
        - ID为0的网格类型不存在时应该抛出ValueError异常
        - 不允许无效的grid_type_id
        """
        with pytest.raises(ValueError, match="未找到ID为0的网格类型"):
            GridTypeTransactionAnalysisService(grid_type_id=0)
    
    def test_service_with_negative_grid_type_id(self):
        """
        测试网格类型ID为负数的情况
        
        验证点：
        - 负数ID的网格类型不存在时应该抛出ValueError异常
        - 不允许无效的grid_type_id
        """
        with pytest.raises(ValueError, match="未找到ID为-1的网格类型"):
            GridTypeTransactionAnalysisService(grid_type_id=-1)
    
    def test_fetch_and_organize_trade_data_with_none_grid_type_id(self):
        """
        测试grid_type_id为None时的数据获取
        
        验证点：
        - grid_type_id为None时应该抛出ValueError异常
        - 不允许None的grid_type_id
        """
        with pytest.raises(ValueError, match="网格类型ID不能为None"):
            GridTypeTransactionAnalysisService(grid_type_id=None)
    
    def test_assemble_data_with_none_grid_type_id(self):
        """
        测试grid_type_id为None时的数据组装
        
        验证点：
        - grid_type_id为None时应该抛出ValueError异常
        - 不允许None的grid_type_id
        """
        # 期望在初始化时就抛出异常
        with pytest.raises(ValueError, match="网格类型ID不能为None"):
            GridTypeTransactionAnalysisService(grid_type_id=None)
    

    
    # 集成测试
    @patch('web.services.analysis.transaction_analysis_service.GridTypeTransactionAnalysisService.get_trade_analysis_record')
    def test_full_analysis_workflow(self, mock_get_records):
        """
        测试完整的分析工作流程
        
        验证点：
        - 端到端的分析流程正常工作
        - 各个组件协同工作正常
        - 数据流转正确
        """
        # Mock记录数据
        mock_get_records.return_value = [self.test_record]
        
        # 创建服务
        service = GridTypeTransactionAnalysisService(
            grid_type_id=self.test_grid_type_id,
            start=date(2024, 1, 1),
            end=date(2024, 1, 31)
        )
        
        # 准备分析
        service.prepare_analysis(date(2024, 1, 1), date(2024, 1, 31))
        
        # 验证准备阶段
        assert service.start == date(2024, 1, 1)
        assert service.end == date(2024, 1, 31)
        
        # 模拟数据组装
        summary_data = pd.DataFrame({
            '基金名称': ['测试基金'],
            '基金代码': ['000001'],
            '当日净值': [1.0]
        })
        
        with patch.object(service, 'assemble_trade_analysis') as mock_assemble:
            mock_trade_analysis = GridTradeAnalysisData(
                asset_id=self.test_asset_id,
                analysis_type=TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value,
                business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
                record_date=self.test_date,
                grid_type_id=self.test_grid_type_id,
                sub_analysis_type='grid_trade_analysis'
            )
            mock_assemble.return_value = mock_trade_analysis
            
            service.assemble_data(summary_data, ('测试基金',), self.test_date)
            
            # 验证数据组装
            assert len(service.update_trade_list) == 1
            assert service.update_trade_list[0].grid_type_id == self.test_grid_type_id
            
            # 完成分析
            service.finalize_analysis()
            
            # 验证数据库保存
            saved_data = GridTradeAnalysisData.query.filter_by(
                grid_type_id=self.test_grid_type_id
            ).first()
            assert saved_data is not None
            assert saved_data.grid_type_id == self.test_grid_type_id
    
    @patch('web.services.analysis.transaction_analysis_service.databox')
    @patch('web.services.analysis.transaction_analysis_service.AssetCode')
    @patch('web.services.analysis.transaction_analysis_service.GridTypeTransactionAnalysisService.get_trade_analysis_record')
    @patch('web.common.utils.WebUtils.webutils.is_trading_day')
    def test_trade_analysis_integration(self, mock_is_trading_day, mock_get_records, mock_asset_code, mock_databox):
        """
        从trade_analysis方法开始的集成测试，主要Mock数据，保持业务逻辑
        
        验证点：
        - trade_analysis方法的完整流程
        - databox方法调用正确
        - 数据组装和转换正确
        - 数据库保存操作正确
        """
        # 准备测试数据
        test_records = [
            Record(
                asset_id=self.test_asset_id,
                transactions_direction=Record.get_record_directoin_enum().PURCHASE.value,
                transactions_date=datetime(2024, 1, 1),
                transactions_amount=100000  # 1000元
            ),
            Record(
                asset_id=self.test_asset_id,
                transactions_direction=Record.get_record_directoin_enum().SELL.value,
                transactions_date=datetime(2024, 1, 15),
                transactions_amount=50000  # 500元
            )
        ]
        
        # Mock DataFrame数据 - 模拟summary返回的数据
        mock_summary_data = pd.DataFrame({
            '基金名称': ['华宝油气LOF', '总计'],
            '基金代码': ['161129', 'total'],
            '当日净值': [1.2345, None],
            '单位成本': [1.1500, 1.1500],
            '持有份额': [800.0, 800.0],
            '基金现值': [987.60, 987.60],
            '基金总申购': [1300.0, 1300.0],
            '历史最大占用': [1300.0, 1300.0],
            '基金持有成本': [920.0, 920.0],
            '基金分红与赎回': [0.0, 0.0],
            '换手率': [0.85, 0.85],
            '基金收益总额': [67.60, 67.60],
            '投资收益率': [0.0735, 0.0735],
            '内部收益率': [0.0698, 0.0698]
        })
        
        # Mock基金名称
        mock_fund_names = ('华宝油气LOF',)
        
        # Mock trade_id
        mock_trade_id = 12345
        
        # Mock分析日期
        analysis_date = datetime(2024, 2, 1)
        
        # 设置Mock返回值
        mock_is_trading_day.return_value = True
        mock_databox.trade.return_value = mock_trade_id
        mock_databox.summary.return_value = mock_summary_data
        mock_databox.get_trade_fund_name.return_value = mock_fund_names
        
        # Mock AssetCode查询
        mock_asset = MagicMock()
        mock_asset.asset_id = self.test_asset_id
        mock_asset_code.query.filter.return_value.first.return_value = mock_asset
        
        # 设置mock返回值
        mock_get_records.return_value = test_records
        
        # 创建服务实例
        service = GridTypeTransactionAnalysisService(grid_type_id=self.test_grid_type_id)
        service.grid_type_details = [self.test_grid_type_detail]
        
        # 执行trade_analysis方法 - 只测试一天以避免多次调用summary
        service.trade_analysis(start=analysis_date, end=analysis_date)
        
        # 验证databox方法调用
        mock_databox.trade.assert_called_once_with(test_records)
        mock_databox.summary.assert_called_once_with(trade_id=mock_trade_id, date=analysis_date)
        mock_databox.get_trade_fund_name.assert_called_once_with(mock_trade_id)
        mock_databox.remove_trade_cache.assert_called_once_with(mock_trade_id)
        
        # 验证数据完整性
        assert len(service.update_trade_list) == 1
        
        # 获取组装的数据进行详细验证
        assembled_data = service.update_trade_list[0]
        
        # 验证基础数据字段
        assert assembled_data.asset_id == self.test_asset_id
        assert assembled_data.analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID_TYPE.value
        assert assembled_data.record_date == analysis_date
        assert assembled_data.grid_type_id == self.test_grid_type_id
        
        # 验证财务数据字段（按照conversion_factors转换）
        # 验证单位成本 (1.1500 * 10000 = 11500)
        assert assembled_data.unit_cost == 11500
        
        # 验证持有份额 (800.0 * 100 = 80000)
        assert assembled_data.attributable_share == 80000
        
        # 验证基金现值 (987.60 * 100 = 98760)
        assert assembled_data.present_value == 98760
        
        # 验证基金总申购 (1300.0 * 100 = 130000)
        assert assembled_data.purchase_amount == 130000
        
        # 验证历史最大占用 (1300.0 * 100 = 130000)
        assert assembled_data.maximum_occupancy == 130000
        
        # 验证基金持有成本 (920.0 * 100 = 92000)
        assert assembled_data.holding_cost == 92000
        
        # 验证基金分红与赎回 (0.0 * 100 = 0)
        assert assembled_data.dividend == 0
        
        # 验证换手率 (0.85 * 10000 = 8500)
        assert assembled_data.turnover_rate == 8500
        
        # 验证基金收益总额 (67.60 * 100 = 6760)
        assert assembled_data.profit == 6760
        
        # 验证投资收益率 (0.0735 * 10000 = 735)
        assert assembled_data.investment_yield == 735
        
        # 验证内部收益率 (0.0698 * 10000 = 698)
        assert assembled_data.irr == 698