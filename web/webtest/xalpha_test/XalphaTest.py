import pandas as pd

from web.databox.adapter.data.xa_data_adapter import XaDataAdapter
from web.models.asset.asset_code import AssetCode
from web.models.asset.AssetFundDailyData import AssetFundDailyDataSchema
from web.webtest.TestModelsClass import TestBasicModels


class XalphaTestBasicModels(TestBasicModels):
    # def setUp(self):
    #     self.app = create_app(config_name='testing')
    #     self.client = self.app.test_client()

    def test_get_daily(self):
        """
        测试获取日线数据，使用XaDataAdapter的get_daily接口
        参数为code_xq值为SH513050的代码，开始日期为2023-03-15，结束日期为2023-03-22，如果获取的条数为5条则测试通过
        Returns:

        """
        xa = XaDataAdapter()
        start_date = pd.to_datetime('2023-03-15')
        end_date = pd.to_datetime('2023-03-22')
        # 获取AssetCode
        asset_code: AssetCode = AssetCode.query.filter(AssetCode.code_xq == 'SH513050').first()
        daily_data = xa.get_daily(start_date=start_date, end_date=end_date, asset_code=asset_code)
        self.assertEqual(len(daily_data), 6)
        # 将列表转换成字典后输出
        print(AssetFundDailyDataSchema().dump(daily_data, many=True))

        # 测试获取日线数据，不传入asset_code参数，如果获取的条数为0条则测试通过
        daily_data = xa.get_daily(start_date=start_date, end_date=end_date)
        self.assertEqual(len(daily_data), 0)

        # 测试3，创建XaDataAdapter时传入asset_code参数，调用获取日线数据方法，如果获取的条数为5条则测试通过
        xa = XaDataAdapter(code_xq=asset_code.code_xq, code_ttjj=asset_code.code_ttjj)
        daily_data = xa.get_daily(start_date=start_date, end_date=end_date)
        self.assertEqual(len(daily_data), 6)
