import unittest
from pprint import pprint

from web.models.asset.asset_code import AssetCodeSchema
from web.webtest.TestModelsClass import TestBasicModels


class SerializationTestBasicModels(TestBasicModels):
    # 序列化和反序列化测试
    def test_deserialization(self):
        post_data = {'assert_name': '测试', 'currency': 1, 'assert_type': 1, 'code_ttjj': '12345'}
        # failed unknown field
        data = AssetCodeSchema().load(post_data, unknown="EXCLUDE")
        pprint(data)


if __name__ == '__main__':
    unittest.main()
