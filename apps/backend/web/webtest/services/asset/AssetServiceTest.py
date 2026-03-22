import unittest

import xalpha as xa
from web.common.cons import fundInfoDBSetting
from web.models.asset.AssetFundFeeRule import AssetFundFeeRule
from web.services.asset.asset_service import asset_service
from web.webtest.BasicRouterTestClass import BasicRouterTestClass


class AssetServiceTest(BasicRouterTestClass):

    def test_insert_asset_data(self):
        asset_service.init_fund_asset_data(asset_id=1, code_ttjj='F513050')

    def test_insert_fund_fee_rules(self):
        fund_info = xa.fundinfo('F513050', **fundInfoDBSetting.DB_SETTING)
        rule = AssetFundFeeRule()
        rule.save_feeinfo(feeinfo=fund_info.feeinfo, asset_id=1)


if __name__ == '__main':
    unittest.main()
