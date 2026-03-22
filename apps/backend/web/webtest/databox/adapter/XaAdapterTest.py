"""
使用pytest测试XaAdapter，测试类基于BasicModelsTestClass
包含测试内容：测试获取证券股票持仓数据
"""
from web.databox.adapter.data.xa_data_adapter import XaDataAdapter
from web.webtest.test_base import TestBase
from web.webtest.TestModelsClass import TestBasicModels


class TestXaAdapterBasicModels(TestBase):
    def test_get_stock_holdings(self):
        """
        测试获取证券股票持仓数据，测试数据为华宝油气股票持仓数据，代码为162411, 年份为2020，季度为1
        判断方法：获取到的数据不为空，并打印结果
        :return:
        """
        xa = XaDataAdapter()
        result = xa.get_stock_holdings('162411', 2020, 1)
        assert result is not None
        print(result)

    def test_get_rt(self):
        """
        测试XaAdapter的get_rt方法，测试数据为获取代码为SZ162411的实时数据，
        Returns:

        """
        xa = XaDataAdapter()
        asset_current_dto = xa.get_rt('sh600001')
        # 判断asset_current_dto不为空，并且code为SZ162411，测试通过，输出结果到控制台
        assert asset_current_dto is not None
        assert asset_current_dto.code == 'SZ162411'
        print(asset_current_dto)
