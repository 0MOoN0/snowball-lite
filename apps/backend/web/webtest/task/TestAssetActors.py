from web.models.asset.asset_code import AssetCode, AssetCodeSchema
from web.task.actors.AssetActors import init_asset
from web.webtest.test_base import TestBase


class TestAssetActors(TestBase):

    def test_init_asset(self):
        """
        方法内容：测试初始化资产数据
        Args:

        Returns:

        """
        # 获取code_xq为SH512980的资产代码
        asset_code: AssetCode = AssetCode.query.filter_by(code_xq='SH512980').first()
        # dump asset_code，调用初始化资产数据的方法
        # init_asset(AssetCodeSchema().dump(asset_code))
