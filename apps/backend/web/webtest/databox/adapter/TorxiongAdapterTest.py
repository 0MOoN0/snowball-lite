from web.databox.adapter.data.TorxiongAdapter import TorxiongAdapter
from web.webtest.TestModelsClass import TestBasicModels


class TestTorxiongAdapter(TestBasicModels):

    def test_fetch_all_stock_asset(self):
        """
        测试获取所有股票资产数据，测试数据为获取所有股票资产数据
        判断方法：获取到的数据不为空，并且长度大于零，最后打印结果
        :return:
        """
        xa = TorxiongAdapter()
        result = xa.fetch_all_stock_asset()
        assert result is not None
        assert len(result) > 0
        print(result)

    def test_get_rt(self):
        """
        测试TorxxiongAdapter的get_rt方法，测试数据为获取代码为162411的实时数据，
        如果获取到的数据不为空，并且code为SZ162411，测试通过，输出结果到控制台
        Returns:

        """
        tx_adapter = TorxiongAdapter()
        result = tx_adapter.get_rt('162411')
        assert result is not None
        assert result.code == 'SZ162411'
        print(result)
