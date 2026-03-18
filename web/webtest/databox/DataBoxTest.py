from pprint import pprint

import pandas as pd
import pytest

from test_base import TestBase
from web.databox import databox
from web.databox.data_box import DataBox
from web.models.asset.asset_code import AssetCode
from web.models.asset.AssetFundDailyData import AssetFundDailyData


class TestDataBox(TestBase):

    def test_get_rt(self):
        """
        测试DataBox的get_rt方法，测试数据为162411和SZ162411
        获取他们的试试数据，并对比结果，如果两次获取的结果不为空，并且结果字段内容相同，测试通过，输出结果到控制台
        Returns:

        """
        data_box = DataBox()
        result1 = data_box.get_rt('162411')
        result2 = data_box.get_rt('SZ162411')
        assert result1 is not None
        assert result2 is not None
        assert result1.code == result2.code
        assert result1.name == result2.name
        assert result1.price == result2.price
        print(result1)
        print('===========')
        print(result2)

    def test_get_daily(self):
        """
        测试DataBox的get_daily方法，测试数据为SH513050
        Returns:

        """
        start_date = pd.to_datetime('2023-03-15')
        end_date = pd.to_datetime('2023-03-22')
        test_asset_code = 'SH513050'
        # 根据code_xq获取asset_code
        asset_code: AssetCode = AssetCode.query.filter(AssetCode.code_xq == test_asset_code).first()
        data_box = DataBox()
        # 测试开始日期为2023-03-15，结束日期为2023-03-22，如果获取的条数为条则测试通过
        daily_data = data_box.fetch_daily_data(start_date=start_date, end_date=end_date, asset_code=asset_code)
        assert len(daily_data) == 6

        # 测试不传入日期，如果获取的条数为1条则测试通过
        daily_data = data_box.fetch_daily_data(asset_code=asset_code)
        assert len(daily_data) == 1

        # 测试不传入asset_code，传入asset_id，如果获取的条数为1条则测试通过
        daily_data = data_box.fetch_daily_data(asset_id=asset_code.id)
        assert len(daily_data) == 1

    def test_get_daily_data(self, session):
        """
        测试DataBox的get_daily_data方法，测试数据为SH513050
        Returns:

        """
        # 删除SH513050的2023-03-24的daily_data数据
        asset_code: AssetCode = AssetCode.query.filter(AssetCode.code_xq == 'SH513050').first()
        res = AssetFundDailyData.query.filter(AssetFundDailyData.asset_id == asset_code.asset_id) \
            .filter(AssetFundDailyData.f_date == '2023-03-24').delete()
        # 如果删除的条数为1条则测试通过
        assert res == 1
        # 查询SH513050的2023-03-24的daily_data数据，如果为空则测试通过
        AssetFundDailyData.query.filter(AssetFundDailyData.asset_id == asset_code.asset_id) \
            .filter(AssetFundDailyData.f_date == '2023-03-24').first()
        daily_data = session.query(AssetFundDailyData).filter(AssetFundDailyData.asset_id == asset_code.asset_id) \
            .filter(AssetFundDailyData.f_date == '2023-03-24').first()
        # session.flush()
        assert daily_data is None
        data_box = DataBox()
        # 获取SH513050的2023-03-24的daily_data数据，如果不为空则测试通过
        daily_data = data_box.get_daily_data(asset_code=asset_code, start_date='2023-03-24', end_date='2023-03-24')
        assert daily_data is not None
        # 查询SH513050的2023-03-24的daily_data数据，如果不为空则测试通过
        daily_data = AssetFundDailyData.query.filter(AssetFundDailyData.asset_id == asset_code.id) \
            .filter(AssetFundDailyData.f_date == '2023-03-24').first()
        assert daily_data is not None

    def test_get_rt(self):
        rt = databox.get_rt(code="SZ162411")
        pprint(rt)

    def test_fund_info(self):
        fund_info = databox.fund_info("162411")
        pprint(fund_info)
