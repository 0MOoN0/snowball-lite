import unittest
from datetime import date
from web.models.index.index_base import IndexBase, IndexBaseSchema, IndexBaseJSONSchema
from web.common.enum.business.index.index_enum import IndexTypeEnum, WeightMethodEnum, CalculationMethodEnum
from web.common.enum.common_enum import MarketEnum, CurrencyEnum


class IndexBaseTest(unittest.TestCase):
    def test_create_index_base(self):
        """
        测试创建IndexBase实例
        """
        index_base = IndexBase(
            index_code='000001.SH',
            index_name='上证指数',
            index_type=IndexTypeEnum.STOCK.value,
            market=MarketEnum.CN.value,
            base_date=date(1990, 12, 19),
            base_point=100,
            currency=CurrencyEnum.CNY.value,
            weight_method=WeightMethodEnum.MARKET_CAP.value,
            calculation_method=CalculationMethodEnum.PRICE.value
        )
        self.assertEqual(index_base.index_code, '000001.SH')
        self.assertEqual(index_base.index_type, 0)
        self.assertEqual(index_base.market, 0)
        self.assertEqual(index_base.currency, 0)
        self.assertEqual(index_base.base_point, 100)

    def test_to_dict(self):
        """
        测试to_dict方法
        """
        index_base = IndexBase(
            index_code='000001.SH',
            index_name='上证指数',
            index_type=IndexTypeEnum.STOCK.value,
            market=MarketEnum.CN.value,
            base_date=date(1990, 12, 19),
            base_point=100,
            currency=CurrencyEnum.CNY.value,
            weight_method=WeightMethodEnum.MARKET_CAP.value,
            calculation_method=CalculationMethodEnum.PRICE.value
        )
        data = index_base.to_dict()
        self.assertEqual(data['index_type'], 0)
        self.assertEqual(data['market'], 0)
        self.assertEqual(data['currency'], 0)
        self.assertEqual(data['base_point'], 100)

    def test_index_base_schema(self):
        """
        测试IndexBaseSchema
        """
        schema = IndexBaseSchema()
        data = {
            'indexCode': '000001.SH',
            'indexName': '上证指数',
            'indexType': 0,
            'market': 0,
            'baseDate': '1990-12-19',
            'basePoint': 100,
            'currency': 0
        }
        result = schema.load(data)
        self.assertEqual(result['index_code'], '000001.SH')
        self.assertEqual(result['index_type'], 0)

    def test_index_base_json_schema(self):
        """
        测试IndexBaseJSONSchema
        """
        schema = IndexBaseJSONSchema()
        data = {
            'index_code': '000001.SH',
            'index_name': '上证指数',
            'index_type': 0,
            'market': 0,
            'base_date': date(1990, 12, 19),
            'base_point': 100,
            'currency': 0
        }
        result = schema.dump(data)
        self.assertEqual(result['index_code'], '000001.SH')
        self.assertEqual(result['index_type'], 0)


if __name__ == '__main__':
    unittest.main()