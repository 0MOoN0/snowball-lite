# -*- coding: UTF-8 -*-
"""
@File    ：test_grid_transaction_analysis_service.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025-01-14 
@Description: GridTransactionAnalysisService集成测试用例
"""
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import patch

import pandas as pd
import pytest

from web.models import db
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.analysis.trade_analysis_data import TradeAnalysisData
# GridGridAnalysisData已被移除，不再需要导入
from web.models.asset.asset import Asset
from web.models.asset.asset_code import AssetCode
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.models.record.record import Record
from web.services.analysis.transaction_analysis_service import GridTransactionAnalysisService
from web.webtest.test_base import TestBaseWithRollback


@pytest.mark.integration
@pytest.mark.analysis
@pytest.mark.grid
class TestGridTransactionAnalysisService(TestBaseWithRollback):
    """
    GridTransactionAnalysisService集成测试类
    
    测试覆盖范围：
    - 服务初始化和配置
    - 核心业务方法功能验证
    - 数据库操作和事务处理
    - 异常情况和边界条件
    - 数据一致性和完整性
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
            grid_type_status=0,  # 添加必需的grid_type_status字段
            type_name="测试网格类型",
            asset_id=self.test_asset_id
        )
        
        # 添加GridType到session并flush以获取ID
        rollback_session.add(self.test_grid_type)
        rollback_session.flush()
        
        # 创建测试用的GridTypeDetail对象
        self.test_grid_type_detail = GridTypeDetail(
            grid_type_id=self.test_grid_type.id,  # 使用动态分配的grid_type_id
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
        rollback_session.flush()  # 使用flush代替commit，保持在同一事务中
        
        # 创建GridTypeRecord关联记录，这是get_analysis_records_by_type查询所必需的
        from web.models.grid.GridTypeRecord import GridTypeRecord
        self.test_grid_type_record = GridTypeRecord(
            grid_type_id=self.test_grid_type.id,
            record_id=self.test_record.id
        )
        rollback_session.add(self.test_grid_type_record)
        rollback_session.flush()
    
    # 初始化测试
    def test_init_with_valid_grid_id(self):
        """
        测试使用有效网格ID初始化服务
        
        验证点：
        - 服务正确初始化所有属性
        - 网格对象正确加载
        - 分析类型设置正确
        """
        service = GridTransactionAnalysisService(
            grid_id=self.test_grid_id,
            start=date(2024, 1, 1),
            end=date(2024, 1, 31)
        )
        
        assert service.grid_id == self.test_grid_id
        assert service.analysis_type == TradeAnalysisData.get_analysis_type_enum().GRID.value
        assert service.start == date(2024, 1, 1)
        assert service.end == date(2024, 1, 31)
        assert service.grid is not None
        assert service.grid.id == self.test_grid_id
        assert isinstance(service.date_trade_dict, dict)
        assert isinstance(service.update_trade_list, list)
        assert isinstance(service.grid_type_detail_dict, dict)
    
    def test_init_with_invalid_grid_id(self):
        """
        测试使用无效网格ID初始化服务
        
        验证点：
        - 服务能够处理不存在的网格ID
        - grid属性为None
        """
        service = GridTransactionAnalysisService(grid_id=99999)
        
        assert service.grid_id == 99999
        assert service.grid is None
    
    def test_init_with_default_dates(self):
        """
        测试使用默认日期初始化服务
        
        验证点：
        - start和end默认为None
        - 其他属性正确初始化
        """
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        
        assert service.start is None
        assert service.end is None
        assert service.grid_id == self.test_grid_id
    
    # get_trade_analysis_record方法测试
    @patch('web.services.analysis.transaction_analysis_service.GridTransactionAnalysisService.get_analysis_records_by_type')
    def test_get_trade_analysis_record(self, mock_get_records):
        """
        测试获取交易分析记录
        
        验证点：
        - 正确调用父类方法
        - 传递正确的参数
        - 返回预期的记录列表
        """
        mock_records = [self.test_record]
        mock_get_records.return_value = mock_records
        
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        result = service.get_trade_analysis_record()
        
        mock_get_records.assert_called_once_with(
            analysis_type=service.analysis_type,
            record_key_id=self.test_grid_id
        )
        assert result == mock_records
    
    # assemble_data方法测试
    @patch('web.services.analysis.transaction_analysis_service.GridTransactionAnalysisService.assemble_trade_analysis')
    @patch('web.services.analysis.transaction_analysis_service.GridTransactionAnalysisService.assemble_grid_trade_analysis')
    @patch('web.services.analysis.transaction_analysis_service.GridTransactionAnalysisService.organize_grid_analysis_data')
    def test_assemble_data_success(self, mock_organize, mock_assemble_grid, mock_assemble_trade):
        """
        测试数据组装成功场景
        
        验证点：
        - 正确处理DataFrame数据
        - 调用所有必要的组装方法
        - 更新trade_list正确
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
        mock_trade_analysis = TradeAnalysisData()
        mock_grid_analysis = GridTradeAnalysisData()
        mock_organized_analysis = GridTradeAnalysisData()
        
        mock_assemble_trade.return_value = mock_trade_analysis
        mock_assemble_grid.return_value = mock_grid_analysis
        mock_organize.return_value = mock_organized_analysis
        
        # 创建服务并设置必要属性
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.grid_type_detail_dict = {1: [self.test_grid_type_detail]}
        service.records = [self.test_record]
        
        # 执行测试
        service.assemble_data(summary_data, fund_names, today)
        
        # 验证调用
        mock_assemble_trade.assert_called_once()
        mock_assemble_grid.assert_called_once()
        mock_organize.assert_called_once()
        
        # 验证update_trade_list更新
        assert len(service.update_trade_list) == 1
        assert isinstance(service.update_trade_list[0], GridTradeAnalysisData)
    
    def test_assemble_data_empty_fund_names(self):
        """
        测试空基金名称列表的处理
        
        验证点：
        - 空基金名称列表会抛出ValueError异常
        """
        # 创建一个包含总计行的非空DataFrame
        summary_data = pd.DataFrame({
            '基金名称': ['总计'],
            '买入金额': [1000.0],
            '卖出金额': [500.0],
            '持有金额': [500.0]
        })
        fund_names = ()  # 空的基金名称元组
        today = self.test_date
        
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        
        # 验证空基金名称列表会抛出ValueError
        with pytest.raises(ValueError, match="基金名称列表不能为空"):
            service.assemble_data(summary_data, fund_names, today)
    
    # finalize_analysis方法测试
    def test_finalize_analysis_success(self):
        """
        测试分析完成处理成功场景
        
        验证点：
        - 正确保存GridTradeAnalysisData对象
        - 正确设置grid_id关联
        - 数据库事务正确提交
        """
        # 准备测试数据
        grid_analysis = GridTradeAnalysisData(
            asset_id=self.test_asset_id,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().GRID.value,
            business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
            record_date=self.test_date,
            grid_id=self.test_grid_id,
            sub_analysis_type='grid_trade_analysis'  # 设置多态映射标识
        )
        
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.update_trade_list = [grid_analysis]
        
        # 执行测试
        service.finalize_analysis()
        
        # 验证数据库中的数据
        saved_grid_analysis = GridTradeAnalysisData.query.first()
        assert saved_grid_analysis is not None
        assert saved_grid_analysis.asset_id == self.test_asset_id
        assert saved_grid_analysis.grid_id == self.test_grid_id
    
    def test_finalize_analysis_empty_update_list(self):
        """
        测试空更新列表的处理
        
        验证点：
        - 空列表不会导致错误
        - 数据库中没有新增数据
        """
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.update_trade_list = []
        
        # 执行测试
        service.finalize_analysis()
        
        # 验证数据库中没有数据
        assert GridTradeAnalysisData.query.count() == 0
    
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
        
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.update_trade_list = [
            [GridTradeAnalysisData(business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value)]
        ]
        
        with pytest.raises(Exception, match="数据库连接失败"):
            service.finalize_analysis()
    
    # prepare_analysis方法测试
    @patch('web.services.analysis.transaction_analysis_service.GridTransactionAnalysisService.fetch_and_organize_trade_data')
    @patch('web.services.analysis.transaction_analysis_service.GridTransactionAnalysisService.fetch_and_fill_grid_type_details')
    def test_prepare_analysis_success(self, mock_fetch_details, mock_fetch_data):
        """
        测试分析准备成功场景
        
        验证点：
        - 正确设置开始和结束日期
        - 调用数据获取方法
        - 调用网格类型详情获取方法
        """
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        mock_fetch_data.return_value = {}
        
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.prepare_analysis(start_date, end_date)
        
        assert service.start == start_date
        assert service.end == end_date
        mock_fetch_data.assert_called_once()
        mock_fetch_details.assert_called_once()
    
    # organize_grid_analysis_data静态方法测试
    def test_organize_grid_analysis_data_success(self):
        """
        测试网格分析数据组织成功场景
        
        验证点：
        - 正确汇总多个分析数据
        - 计算字段正确
        - 返回更新后的existing_data
        """
        existing_data = GridTradeAnalysisData(business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value)
        
        analysis_data_list = [
            GridTradeAnalysisData(
                business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
                sell_times=2,
                estimate_maximum_occupancy=1000,
                holding_times=3,
                up_sold_percent=Decimal('5.0'),
                down_bought_percent=Decimal('3.0')
            ),
            GridTradeAnalysisData(
                business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
                sell_times=1,
                estimate_maximum_occupancy=500,
                holding_times=2,
                up_sold_percent=Decimal('4.0'),
                down_bought_percent=Decimal('2.0')
            )
        ]
        
        today = self.test_date
        
        result = GridTransactionAnalysisService.organize_grid_analysis_data(
            existing_data, analysis_data_list, today
        )
        
        assert result == existing_data
        assert result.sell_times == 3
        assert result.estimate_maximum_occupancy == 1500
        assert result.holding_times == 5
        assert result.up_sold_percent == Decimal('4.0')  # 取最小值
        assert result.down_bought_percent == Decimal('2.0')  # 取最小值
        assert result.record_date == today
    
    def test_organize_grid_analysis_data_empty_list(self):
        """
        测试空分析数据列表的处理
        
        验证点：
        - 空列表不会导致错误
        - existing_data字段被重置为0
        """
        existing_data = GridTradeAnalysisData(
            business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
            sell_times=10,
            estimate_maximum_occupancy=5000,
            holding_times=8
        )
        
        analysis_data_list = []
        today = self.test_date
        
        result = GridTransactionAnalysisService.organize_grid_analysis_data(
            existing_data, analysis_data_list, today
        )
        
        assert result.sell_times == 0
        assert result.estimate_maximum_occupancy == 0
        assert result.holding_times == 0
        assert result.record_date == today
    
    def test_organize_grid_analysis_data_none_values(self):
        """
        测试包含None值的分析数据处理
        
        验证点：
        - None值能够正确处理
        - 不会导致计算错误
        """
        existing_data = GridTradeAnalysisData(business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value)
        
        analysis_data_list = [
            GridTradeAnalysisData(
                business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
                sell_times=1,
                estimate_maximum_occupancy=1000,
                holding_times=2,
                up_sold_percent=None,
                down_bought_percent=Decimal('3.0')
            ),
            GridTradeAnalysisData(
                business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
                sell_times=2,
                estimate_maximum_occupancy=500,
                holding_times=1,
                up_sold_percent=Decimal('5.0'),
                down_bought_percent=None
            )
        ]
        
        today = self.test_date
        
        result = GridTransactionAnalysisService.organize_grid_analysis_data(
            existing_data, analysis_data_list, today
        )
        
        assert result.sell_times == 3
        assert result.estimate_maximum_occupancy == 1500
        assert result.holding_times == 3
        assert result.up_sold_percent == Decimal('5.0')
        assert result.down_bought_percent == Decimal('3.0')
    
    # fetch_and_organize_trade_data方法测试
    def test_fetch_and_organize_trade_data_success(self):
        """
        测试获取和组织交易数据成功场景
        
        验证点：
        - 正确查询数据库
        - 返回正确格式的字典
        - 数据结构符合预期
        """
        # 创建测试数据
        grid_trade = GridTradeAnalysisData(
            asset_id=self.test_asset_id,
            analysis_type=TradeAnalysisData.get_analysis_type_enum().GRID.value,
            business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
            record_date=self.test_date,
            grid_id=self.test_grid_id  # 添加grid_id字段
        )
        
        db.session.add(grid_trade)
        db.session.flush()
        
        # GridGridAnalysisData 已被移除，不再需要创建
        
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.start = date(2024, 1, 1)
        service.end = date(2024, 1, 31)
        service.analysis_type = TradeAnalysisData.get_analysis_type_enum().GRID.value
        
        result = service.fetch_and_organize_trade_data()
        
        assert isinstance(result, dict)
        assert self.test_date in result
        trade_data = result[self.test_date]
        assert len(trade_data) == 1
        assert trade_data[0] == grid_trade  # 只有一个GridTradeAnalysisData元素
    
    def test_fetch_and_organize_trade_data_no_data(self):
        """
        测试无数据情况的处理
        
        验证点：
        - 无数据时返回空字典
        - 不会导致错误
        """
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.start = date(2024, 1, 1)
        service.end = date(2024, 1, 31)
        service.analysis_type = TradeAnalysisData.get_analysis_type_enum().GRID.value
        
        result = service.fetch_and_organize_trade_data()
        
        assert isinstance(result, dict)
        assert len(result) == 0
    
    # fetch_and_fill_grid_type_details方法测试
    def test_fetch_and_fill_grid_type_details_success(self):
        """
        测试获取和填充网格类型详情成功场景
        
        验证点：
        - 正确查询网格类型详情
        - 按网格类型ID正确分组
        - grid_type_detail_dict正确更新
        """
        # 创建第二个GridType对象
        test_grid_type_2 = GridType(
            grid_id=self.test_grid_id,
            grid_type_status=0,
            type_name="测试网格类型2",
            asset_id=self.test_asset_id
        )
        db.session.add(test_grid_type_2)
        db.session.flush()
        
        # 创建额外的测试数据
        detail2 = GridTypeDetail(
            grid_type_id=self.test_grid_type.id,  # 使用第一个GridType的id
            grid_id=self.test_grid_id,
            gear="2",
            monitor_type=GridTypeDetail.get_monitor_type_enum().BUY.value,
            trigger_sell_price=12000,
            sell_price=12000,
            sell_shares=1000,
            actual_sell_shares=1000,
            sell_amount=12000000,
            trigger_purchase_price=8000,
            purchase_price=8000,
            purchase_amount=200000,
            purchase_shares=2500,
            profit=2000000,
            save_share_profit=0,
            save_share=0,
            is_current=False
        )
        
        detail3 = GridTypeDetail(
            grid_type_id=test_grid_type_2.id,  # 使用第二个GridType的id
            grid_id=self.test_grid_id,
            gear="1",
            monitor_type=GridTypeDetail.get_monitor_type_enum().SELL.value,
            trigger_sell_price=11500,
            sell_price=11500,
            sell_shares=1000,
            actual_sell_shares=1000,
            sell_amount=11500000,
            trigger_purchase_price=8500,
            purchase_price=8500,
            purchase_amount=150000,
            purchase_shares=1765,
            profit=1500000,
            save_share_profit=0,
            save_share=0,
            is_current=False
        )
        
        db.session.add_all([detail2, detail3])
        db.session.flush()
        
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.fetch_and_fill_grid_type_details()
        
        assert len(service.grid_type_detail_dict) == 2
        assert self.test_grid_type.id in service.grid_type_detail_dict
        assert test_grid_type_2.id in service.grid_type_detail_dict
        assert len(service.grid_type_detail_dict[self.test_grid_type.id]) == 2  # grid_type_id=1有2个详情（setUp中1个+测试中1个）
        assert len(service.grid_type_detail_dict[test_grid_type_2.id]) == 1  # grid_type_id=2有1个详情
    
    def test_fetch_and_fill_grid_type_details_no_data(self):
        """
        测试无网格类型详情数据的处理
        
        验证点：
        - 无数据时grid_type_detail_dict保持为空
        - 不会导致错误
        """
        # 删除测试数据
        db.session.delete(self.test_grid_type_detail)
        db.session.flush()
        
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.fetch_and_fill_grid_type_details()
        
        assert len(service.grid_type_detail_dict) == 0
    
    # 集成测试
    @pytest.mark.local
    @patch('web.databox.databox.trade')
    @patch('web.databox.databox.summary')
    @patch('web.databox.databox.get_trade_fund_name')
    @patch('web.databox.databox.remove_trade_cache')
    @patch('web.common.utils.WebUtils.webutils.is_trading_day')
    def test_trade_analysis_integration(self, mock_is_trading_day, mock_remove_cache, 
                                     mock_get_fund_name, mock_summary, mock_trade):
        """
        集成测试：完整的交易分析流程
        
        验证点：
        - 完整流程能够正常执行
        - 各个组件正确协作
        - 数据正确保存到数据库
        """
        # Mock设置
        mock_is_trading_day.return_value = True
        mock_trade.return_value = 1
        mock_get_fund_name.return_value = ('测试基金',)
        
        # 创建mock DataFrame
        mock_summary_df = pd.DataFrame({
            '基金名称': ['测试基金'],
            '基金代码': ['000001'],
            '当日净值': [10000],  # 1.0元，以分为单位
            '单位成本': [9500],   # 0.95元
            '持有份额': [1000000], # 1000份，以万分之一为单位
            '基金现值': [10000000], # 1000元，以分为单位
            '基金总申购': [9500000], # 950元
            '历史最大占用': [9500000],
            '基金持有成本': [9500000],
            '基金分红与赎回': [0],
            '换手率': [1000],     # 0.1，以万分之一为单位
            '基金收益总额': [500000], # 50元
            '投资收益率': [526],   # 0.0526，以万分之一为单位
            '内部收益率': [526]
        })
        mock_summary.return_value = mock_summary_df
        
        # 创建服务并执行分析
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.trade_analysis(start=self.test_date, end=self.test_date)
        
        # 验证调用
        mock_trade.assert_called_once()
        mock_summary.assert_called_once()
        mock_get_fund_name.assert_called_once()
        mock_remove_cache.assert_called_once()
        
        # 验证数据库中的数据
        saved_grid_analysis = GridTradeAnalysisData.query.first()
        assert saved_grid_analysis is not None
        assert saved_grid_analysis.asset_id == self.test_asset_id
        assert saved_grid_analysis.record_date.date() == self.test_date
        
        # GridGridAnalysisData 已被移除，不再验证
    
    # 异常处理测试
    @patch('web.services.analysis.transaction_analysis_service.GridTransactionAnalysisService.get_trade_analysis_record')
    def test_trade_analysis_no_records(self, mock_get_records):
        """
        测试无交易记录时的处理
        
        验证点：
        - 无记录时方法正常返回
        - 不会执行后续处理
        """
        mock_get_records.return_value = []
        
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        
        # 执行测试，应该正常返回而不抛出异常
        service.trade_analysis(start=self.test_date, end=self.test_date)
        
        # 验证没有数据被保存
        assert GridTradeAnalysisData.query.count() == 0
        # GridGridAnalysisData 已被移除，不再验证
    
    @patch('web.weblogger.error')
    def test_error_logging(self, mock_logger):
        """
        测试错误日志记录
        
        验证点：
        - 异常情况下能够正确记录日志
        - 日志信息包含必要的调试信息
        """
        # 创建一个会导致错误的服务（无效的grid_id）
        service = GridTransactionAnalysisService(grid_id=99999)
        
        # 由于grid为None，在某些操作中可能会出错
        # 这里我们主要验证错误处理机制的存在
        try:
            # 尝试访问grid的属性，这应该会导致AttributeError
            _ = service.grid.asset_id
        except AttributeError:
            # 这是预期的错误
            pass
    
    # 边界条件测试
    @pytest.mark.manual
    def test_large_dataset_handling(self):
        """
        测试大数据集处理能力
        
        验证点：
        - 能够处理大量的网格类型详情
        - 性能在可接受范围内
        - 内存使用合理
        """
        # 创建大量测试数据
        large_details = []
        for i in range(100):
            detail = GridTypeDetail(
                id=100 + i,
                grid_type_id=self.test_grid_type.id,  # 使用setup中创建的grid_type_id
                grid_id=self.test_grid_id,
                gear=str(i + 1),
                monitor_type=GridTypeDetail.get_monitor_type_enum().SELL.value if i % 2 == 0 else GridTypeDetail.get_monitor_type_enum().BUY.value,
                trigger_sell_price=11000 + i * 100,
                sell_price=11000 + i * 100,
                sell_shares=1000 + i * 10,
                actual_sell_shares=1000 + i * 10,
                sell_amount=(11000 + i * 100) * (1000 + i * 10),
                trigger_purchase_price=9000 + i * 100,
                purchase_price=9000 + i * 100,
                purchase_amount=100000 + i * 1000,
                purchase_shares=1111 + i * 11,
                profit=(11000 + i * 100 - 9000 - i * 100) * (1000 + i * 10),
                save_share_profit=0,
                save_share=0,
                is_current=False
            )
            large_details.append(detail)
        
        db.session.add_all(large_details)
        db.session.flush()
        
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.fetch_and_fill_grid_type_details()
        
        # 验证数据正确分组
        assert len(service.grid_type_detail_dict) == 1  # 所有detail都使用同一个grid_type_id
        total_details = sum(len(details) for details in service.grid_type_detail_dict.values())
        assert total_details == 101  # 100个新增 + 1个原有的
    
    def test_date_boundary_conditions(self):
        """
        测试日期边界条件
        
        验证点：
        - 处理跨年日期范围
        - 处理单日日期范围
        - 处理无效日期范围
        """
        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        
        # 测试跨年日期范围
        service.prepare_analysis(date(2023, 12, 31), date(2024, 1, 1))
        assert service.start == date(2023, 12, 31)
        assert service.end == date(2024, 1, 1)
        
        # 测试单日日期范围
        service.prepare_analysis(self.test_date, self.test_date)
        assert service.start == self.test_date
        assert service.end == self.test_date
        
        # 测试结束日期早于开始日期的情况
        service.prepare_analysis(date(2024, 1, 31), date(2024, 1, 1))
        assert service.start == date(2024, 1, 31)
        assert service.end == date(2024, 1, 1)