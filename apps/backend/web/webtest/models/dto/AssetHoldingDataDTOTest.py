"""
使用pytest测试AssetHoldingDataDTO schema转换
"""
from datetime import datetime

from web.models.asset.AssetHoldingData import AssetHoldingDataDTOSchema, AssetHoldingDataDTO


class TestAssetHoldingDataDTOSchema:
    def test_load(self):
        """
        测试反序列化
        :return:
        """
        data = {
            'code': '162411',
            'name': '华宝油气',
            'ratio': 100,
            'share': 100,
            'value': 100
        }
        schema = AssetHoldingDataDTOSchema()
        result = schema.load(data)
        print(result)

    def test_dump(self):
        """
        测试序列化
        :return:
        """
        data = AssetHoldingDataDTO(
            id=1,
            asset_id=1,
            ah_date=datetime(2020, 1, 1),
            ah_asset_name="测试",
            ah_holding_asset_id=1,
            ah_holding_percent=100,
            ah_percent=100,
            ah_quarter=1,
            ah_year=2020
        )
        schema = AssetHoldingDataDTOSchema()
        result = schema.dump(data)
        assert result == {
            "id": 1,
            "asset_id": 1,
            "ah_date": "2020-01-01 00:00:00",
            "ah_asset_name": "测试",
            "ah_holding_asset_id": 1,
            "ah_holding_percent": 100,
            "ah_percent": 100,
            "ah_quarter": 1,
            "ah_year": 2020
        }
