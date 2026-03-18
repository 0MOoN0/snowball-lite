"""
使用pytest测试XaDataAdapter的fetch_daily_data方法，重点测试去重逻辑
"""
import datetime
from unittest.mock import MagicMock, patch
import pytest

from web.databox.adapter.data.xa_data_adapter import XaDataAdapter
from web.models import db
from web.models.asset.asset import Asset
from web.models.asset.asset_code import AssetCode
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.webtest.test_base import TestBase


class TestXaDataAdapterFetch(TestBase):
    """测试XaDataAdapter的fetch_daily_data方法"""

    def setup_method(self):
        """测试方法前的设置"""
        self.xa_adapter = XaDataAdapter()
        
        # 创建测试用的资产和资产代码对象
        self.asset = Asset(id=99999, asset_name="测试基金", asset_type=Asset.get_asset_type_enum().FUND.value)
        self.asset_code = AssetCode(asset_id=99999, code_xq="SZ999999", code_ttjj="999999")
        
        # 创建测试用的日线数据
        self.test_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.test_daily_data = [
            AssetFundDailyData(
                asset_id=99999,
                f_date=self.test_date,
                f_open=10000,  # 1元
                f_close=10100,  # 1.01元
                f_high=10200,
                f_low=9900,
                f_volume=100000,
                f_close_percent=1000  # 0.1%
            )
        ]

    @patch('web.databox.adapter.data.XaDataAdapter.XaDataAdapter.get_daily')
    def test_fetch_daily_data_without_duplicates(self, mock_get_daily):
        """测试fetch_daily_data方法在没有重复数据时的行为"""
        # 模拟get_daily方法返回测试数据
        mock_get_daily.return_value = self.test_daily_data
        
        # 模拟数据库查询，返回空列表表示没有重复数据
        with patch.object(db.session, 'query') as mock_query:
            mock_query_instance = MagicMock()
            mock_query.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            mock_query_instance.all.return_value = []
            
            # 调用被测试的方法
            result = self.xa_adapter.fetch_daily_data(
                asset_code=self.asset_code,
                start_date=self.test_date,
                end_date=self.test_date
            )
            
            # 验证结果
            assert len(result) == 1
            assert result[0].asset_id == 99999
            assert result[0].f_date == self.test_date
            
            # 验证调用
            mock_get_daily.assert_called_once()
            mock_query.assert_called_once()

    @patch('web.databox.adapter.data.XaDataAdapter.XaDataAdapter.get_daily')
    def test_fetch_daily_data_with_duplicates(self, mock_get_daily):
        """测试fetch_daily_data方法在有重复数据时的行为"""
        # 模拟get_daily方法返回测试数据
        mock_get_daily.return_value = self.test_daily_data
        
        # 模拟数据库查询，返回一条与测试数据日期相同的记录
        with patch.object(db.session, 'query') as mock_query:
            mock_query_instance = MagicMock()
            mock_query.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            
            # 创建一个模拟的查询结果，包含一条与测试数据日期相同的记录
            mock_record = MagicMock()
            mock_record.f_date = self.test_date
            mock_query_instance.all.return_value = [mock_record]
            
            # 调用被测试的方法
            result = self.xa_adapter.fetch_daily_data(
                asset_code=self.asset_code,
                start_date=self.test_date,
                end_date=self.test_date
            )
            
            # 验证结果 - 应该过滤掉重复的记录，结果为空列表
            assert len(result) == 0
            
            # 验证调用
            mock_get_daily.assert_called_once()
            mock_query.assert_called_once()

    @patch('web.databox.adapter.data.XaDataAdapter.XaDataAdapter.get_daily')
    def test_fetch_daily_data_with_error_handling(self, mock_get_daily):
        """测试fetch_daily_data方法在查询重复数据时出错的异常处理"""
        # 模拟get_daily方法返回测试数据
        mock_get_daily.return_value = self.test_daily_data
        
        # 模拟数据库查询抛出异常
        with patch.object(db.session, 'query') as mock_query:
            mock_query.side_effect = Exception("模拟数据库查询异常")
            
            # 调用被测试的方法 - 即使查询异常，方法也应该能继续执行并返回原始数据
            result = self.xa_adapter.fetch_daily_data(
                asset_code=self.asset_code,
                start_date=self.test_date,
                end_date=self.test_date
            )
            
            # 验证结果 - 应该返回原始数据，不受异常影响
            assert len(result) == 1
            assert result[0].asset_id == 99999
            
            # 验证调用
            mock_get_daily.assert_called_once()
            mock_query.assert_called_once()

    @patch('web.databox.adapter.data.XaDataAdapter.XaDataAdapter.get_daily')
    def test_fetch_daily_data_date_formats(self, mock_get_daily):
        """测试fetch_daily_data方法处理不同日期格式的能力"""
        # 测试日期格式: datetime对象、字符串格式
        date_obj = self.test_date
        date_str = self.test_date.strftime('%Y-%m-%d')
        
        # 设置测试数据
        test_data = self.test_daily_data.copy()
        
        # 一种情况日期是datetime对象
        test_data[0].f_date = date_obj
        mock_get_daily.return_value = test_data
        
        # 模拟数据库查询返回的数据日期是字符串格式
        with patch.object(db.session, 'query') as mock_query:
            mock_query_instance = MagicMock()
            mock_query.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            
            # 创建一个模拟的查询结果，日期是字符串格式
            mock_record = MagicMock()
            mock_record.f_date = date_str
            mock_query_instance.all.return_value = [mock_record]
            
            # 调用被测试的方法
            result = self.xa_adapter.fetch_daily_data(
                asset_code=self.asset_code,
                start_date=date_str,  # 传入字符串日期
                end_date=date_str
            )
            
            # 系统应能正确处理不同格式的日期并识别为同一天
            assert len(result) == 0  # 应该过滤掉重复记录

    @patch('web.databox.adapter.data.XaDataAdapter.XaDataAdapter.get_daily')
    def test_fetch_daily_data_with_duplicates_and_error_handling(self, mock_get_daily):
        """测试fetch_daily_data方法在有重复数据且查询异常时的行为"""
        # 模拟get_daily方法返回测试数据
        mock_get_daily.return_value = self.test_daily_data
        
        # 模拟数据库查询，返回一条与测试数据日期相同的记录
        with patch.object(db.session, 'query') as mock_query:
            mock_query_instance = MagicMock()
            mock_query.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            mock_query_instance.filter.return_value = mock_query_instance
            
            # 创建一个模拟的查询结果，包含一条与测试数据日期相同的记录
            mock_record = MagicMock()
            mock_record.f_date = self.test_date
            mock_query_instance.all.return_value = [mock_record]
            
            # 模拟数据库查询抛出异常
            mock_query.side_effect = Exception("模拟数据库查询异常")
            
            # 调用被测试的方法
            result = self.xa_adapter.fetch_daily_data(
                asset_code=self.asset_code,
                start_date=self.test_date,
                end_date=self.test_date
            )
            
            # 验证结果 - 应该过滤掉重复的记录，结果为空列表
            assert len(result) == 0
            
            # 验证调用
            mock_get_daily.assert_called_once()
            mock_query.assert_called_once() 