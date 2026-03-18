"""
测试asset_scheduler中monitor_grid_type_detail方法使用fetch_daily_data避免重复数据的逻辑
"""
import datetime
from unittest.mock import MagicMock, patch
import pytest

from web.common.utils.WebUtils import web_utils
from web.models import db
from web.models.asset.asset import Asset
from web.models.asset.asset_code import AssetCode
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail


@pytest.mark.usefixtures("test_db_app", "test_db_session")
# @pytest.mark.parametrize('app', ['test'], indirect=True)
class TestAssetSchedulerDuplicates(object):
    """测试asset_scheduler中处理重复数据的功能"""

    def setup_method(self):
        """测试前的设置"""
        # 创建测试日期
        self.test_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 创建测试数据
        self.test_asset = Asset(id=99999, asset_name="测试基金", asset_type=Asset.get_asset_type_enum().FUND.value)
        self.test_asset_code = AssetCode(asset_id=99999, code_xq="SZ999999", code_ttjj="999999")
        self.test_grid = Grid(id=99999, asset_id=99999, grid_name="测试网格", grid_status=Grid.get_status_enum().ENABLE.value)
        self.test_grid_type = GridType(id=99999, grid_id=99999, asset_id=99999, type_name="测试网格类型", 
                                      grid_type_status=GridType.get_grid_status_enum().ENABLE.value)
        self.test_grid_detail = GridTypeDetail(
            id=99999, 
            grid_type_id=99999,
            grid_id=99999,
            gear="1",
            purchase_price=10000,
            trigger_purchase_price=10000,
            purchase_amount=10000,
            purchase_shares=100,
            trigger_sell_price=11000,
            sell_price=11000,
            sell_shares=100,
            actual_sell_shares=100,
            sell_amount=11000,
            profit=1000,
            save_share_profit=0,
            save_share=0,
            monitor_type=0
        )
        
        # 创建测试的日线数据
        self.test_daily_data = AssetFundDailyData(
            asset_id=99999,
            f_date=self.test_date,
            f_open=10000,
            f_close=10100,
            f_high=10200,
            f_low=9900,
            f_volume=100000,
            f_close_percent=1000
        )

    @patch('web.databox.databox.fetch_daily_data')
    @patch('web.common.utils.WebUtils.web_utils.is_trading_day')
    @patch('web.services.grid.grid_service.grid_service.to_judge_gen_transaction')
    @patch('web.services.grid.grid_service.grid_service.to_judge_monitor_change')
    def test_monitor_grid_type_detail_uses_fetch_daily_data(self, mock_judge_monitor_change, 
                                                            mock_judge_gen_transaction, 
                                                            mock_is_trading_day, 
                                                            mock_fetch_daily_data,
                                                            mocker):
        """测试monitor_grid_type_detail方法使用fetch_daily_data而不是get_daily_data"""
        # 导入被测试的函数
        from web.scheduler.asset_scheduler import monitor_grid_type_detail
        
        # 模拟交易日检查返回True
        mock_is_trading_day.return_value = True
        
        # 模拟fetch_daily_data返回测试数据
        mock_fetch_daily_data.return_value = [self.test_daily_data]
        
        # 模拟to_judge_gen_transaction和to_judge_monitor_change返回空列表
        mock_judge_gen_transaction.return_value = []
        mock_judge_monitor_change.return_value = []
        
        # 模拟数据库查询
        with patch.object(db.session, 'query') as mock_query:
            # 模拟查询GridType返回测试数据
            mock_query_instance = MagicMock()
            mock_query.return_value = mock_query_instance
            mock_query_instance.join.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            mock_query_instance.all.return_value = [self.test_grid_type]
            
            # 模拟查询GridTypeDetail返回测试数据
            mock_query_second_instance = MagicMock()
            # 第一次调用query时返回mock_query_instance，之后返回mock_query_second_instance
            mock_query.side_effect = [mock_query_instance, mock_query_second_instance]
            mock_query_second_instance.filter.return_value = mock_query_second_instance
            mock_query_second_instance.all.return_value = [self.test_grid_detail]
            
            # 模拟查询AssetCode返回测试数据
            mock_query_third_instance = MagicMock()
            # 第三次调用query时返回mock_query_third_instance
            mock_query.side_effect = [mock_query_instance, mock_query_second_instance, mock_query_third_instance]
            mock_query_third_instance.filter.return_value = mock_query_third_instance
            mock_query_third_instance.first.return_value = self.test_asset_code
            
            # 调用被测试的方法
            monitor_grid_type_detail()
            
            # 验证fetch_daily_data被调用，而不是get_daily_data
            mock_fetch_daily_data.assert_called_once()
            
            # 验证fetch_daily_data的参数
            args, kwargs = mock_fetch_daily_data.call_args
            assert kwargs['asset_code'] == self.test_asset_code
            assert kwargs['start_date'] is not None
            assert kwargs['end_date'] is not None

    @patch('web.databox.databox.fetch_daily_data')
    def test_monitor_grid_type_detail_handles_duplicate_data(self, mock_fetch_daily_data):
        """测试monitor_grid_type_detail方法处理重复数据的逻辑"""
        # 导入被测试的函数
        from web.scheduler.asset_scheduler import monitor_grid_type_detail
        
        # 设置不同的测试场景
        
        # 情景1: fetch_daily_data返回正确的一条数据
        mock_fetch_daily_data.return_value = [self.test_daily_data]
        
        # 模拟交易日检查
        with patch.object(web_utils, 'is_trading_day', return_value=True):
            # 模拟GridType查询
            with patch.object(db.session, 'query') as mock_query:
                # 设置查询返回值链
                mock_grid_type_query = MagicMock()
                mock_grid_type_detail_query = MagicMock()
                mock_asset_code_query = MagicMock()
                
                # 设置第一次query的返回值链
                mock_query.return_value = mock_grid_type_query
                mock_grid_type_query.join.return_value = mock_grid_type_query
                mock_grid_type_query.filter.return_value = mock_grid_type_query
                mock_grid_type_query.all.return_value = [self.test_grid_type]
                
                # 模拟查询GridTypeDetail
                mock_query.side_effect = [mock_grid_type_query, mock_grid_type_detail_query]
                mock_grid_type_detail_query.filter.return_value = mock_grid_type_detail_query
                mock_grid_type_detail_query.all.return_value = [self.test_grid_detail]
                
                # 模拟查询AssetCode
                mock_query.side_effect = [mock_grid_type_query, mock_grid_type_detail_query, mock_asset_code_query]
                mock_asset_code_query.filter.return_value = mock_asset_code_query
                mock_asset_code_query.first.return_value = self.test_asset_code
                
                # 模拟GridService的方法
                with patch('web.services.grid.grid_service.grid_service.to_judge_gen_transaction', return_value=[]):
                    with patch('web.services.grid.grid_service.grid_service.to_judge_monitor_change', return_value=[]):
                        
                        # 调用被测试的方法
                        monitor_grid_type_detail()
                        
                        # 验证fetch_daily_data被调用
                        mock_fetch_daily_data.assert_called()
        
        # 情景2: fetch_daily_data返回多条数据(异常情况)
        mock_fetch_daily_data.reset_mock()
        mock_fetch_daily_data.return_value = [self.test_daily_data, self.test_daily_data]
        
        # 模拟交易日检查
        with patch.object(web_utils, 'is_trading_day', return_value=True):
            # 模拟GridType查询
            with patch.object(db.session, 'query') as mock_query:
                # 设置查询返回值链
                mock_grid_type_query = MagicMock()
                mock_grid_type_detail_query = MagicMock()
                mock_asset_code_query = MagicMock()
                
                # 设置第一次query的返回值链
                mock_query.return_value = mock_grid_type_query
                mock_grid_type_query.join.return_value = mock_grid_type_query
                mock_grid_type_query.filter.return_value = mock_grid_type_query
                mock_grid_type_query.all.return_value = [self.test_grid_type]
                
                # 模拟查询GridTypeDetail
                mock_query.side_effect = [mock_grid_type_query, mock_grid_type_detail_query]
                mock_grid_type_detail_query.filter.return_value = mock_grid_type_detail_query
                mock_grid_type_detail_query.all.return_value = [self.test_grid_detail]
                
                # 模拟查询AssetCode
                mock_query.side_effect = [mock_grid_type_query, mock_grid_type_detail_query, mock_asset_code_query]
                mock_asset_code_query.filter.return_value = mock_asset_code_query
                mock_asset_code_query.first.return_value = self.test_asset_code
                
                # 模拟error函数避免真正记录错误日志
                with patch('web.weblogger.error'):
                    
                    # 调用被测试的方法 - 应该能正常处理异常情况
                    monitor_grid_type_detail()
                    
                    # 验证fetch_daily_data被调用
                    mock_fetch_daily_data.assert_called()
        
        # 情景3: fetch_daily_data抛出异常
        mock_fetch_daily_data.reset_mock()
        mock_fetch_daily_data.side_effect = Exception("测试异常")
        
        # 模拟交易日检查
        with patch.object(web_utils, 'is_trading_day', return_value=True):
            # 模拟GridType查询
            with patch.object(db.session, 'query') as mock_query:
                # 设置查询返回值链
                mock_grid_type_query = MagicMock()
                mock_grid_type_detail_query = MagicMock()
                mock_asset_code_query = MagicMock()
                
                # 设置第一次query的返回值链
                mock_query.return_value = mock_grid_type_query
                mock_grid_type_query.join.return_value = mock_grid_type_query
                mock_grid_type_query.filter.return_value = mock_grid_type_query
                mock_grid_type_query.all.return_value = [self.test_grid_type]
                
                # 模拟查询GridTypeDetail
                mock_query.side_effect = [mock_grid_type_query, mock_grid_type_detail_query]
                mock_grid_type_detail_query.filter.return_value = mock_grid_type_detail_query
                mock_grid_type_detail_query.all.return_value = [self.test_grid_detail]
                
                # 模拟查询AssetCode
                mock_query.side_effect = [mock_grid_type_query, mock_grid_type_detail_query, mock_asset_code_query]
                mock_asset_code_query.filter.return_value = mock_asset_code_query
                mock_asset_code_query.first.return_value = self.test_asset_code
                
                # 模拟logger.exception函数避免真正记录错误日志
                with patch('web.weblogger.logger.exception'):
                    
                    # 调用被测试的方法 - 应该能正常处理异常情况
                    monitor_grid_type_detail()
                    
                    # 验证fetch_daily_data被调用
                    mock_fetch_daily_data.assert_called() 