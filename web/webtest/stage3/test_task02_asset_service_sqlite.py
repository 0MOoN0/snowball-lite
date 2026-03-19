from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from unittest.mock import patch

import pandas as pd

from web.common.enum.asset_enum import AssetTypeEnum
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.models.asset.AssetFundFeeRule import AssetFundFeeRule
from web.models.asset.AssetHoldingData import AssetHoldingData
from web.models.asset.asset import Asset, AssetCurrentDTO
from web.models.asset.asset_code import AssetCode
from web.services.asset.asset_service import asset_service
from web.webtest.test_base import TestBaseLiteWithRollback


@dataclass
class _FundInfoStub:
    price: pd.DataFrame
    rate: float
    feeinfo: list[str]
    holding_data: pd.DataFrame

    def get_stock_holdings(self, year, season):
        return self.holding_data


class TestAssetServiceSQLiteStage3(TestBaseLiteWithRollback):
    @patch("web.services.asset.asset_service.time.sleep", return_value=None)
    @patch("web.services.asset.asset_service.random.randint", return_value=0)
    @patch("web.services.asset.asset_service.databox.get_rt")
    @patch("web.services.asset.asset_service.databox.fund_info")
    def test_init_fund_asset_data_persists_stage3_business_chain(
        self,
        mock_fund_info,
        mock_get_rt,
        _mock_randint,
        _mock_sleep,
        lite_rollback_session,
    ):
        fund_asset = Asset(
            asset_name="stage3测试基金",
            asset_type=AssetTypeEnum.FUND.value,
            asset_status=0,
            currency=0,
            market=0,
        )
        lite_rollback_session.add(fund_asset)
        lite_rollback_session.flush()

        fund_asset_code = AssetCode(
            asset_id=fund_asset.id,
            code_ttjj="F000001",
        )
        lite_rollback_session.add(fund_asset_code)
        lite_rollback_session.flush()

        mock_fund_info.return_value = _FundInfoStub(
            price=pd.DataFrame(
                [
                    {
                        "date": datetime(2024, 1, 1),
                        "netvalue": 1.0,
                        "comment": 0.0,
                        "totvalue": 1.2,
                    },
                    {
                        "date": datetime(2024, 1, 2),
                        "netvalue": 1.1,
                        "comment": 0.0,
                        "totvalue": 1.3,
                    },
                ]
            ),
            rate=1.5,
            feeinfo=[],
            holding_data=pd.DataFrame(
                [
                    {
                        "code": "600519.SH",
                        "ratio": 12.34,
                    }
                ]
            ),
        )
        mock_get_rt.return_value = AssetCurrentDTO(
            code="600519",
            name="贵州茅台",
            market=0,
            price=188800,
            currency=0,
        )

        asset_service.init_fund_asset_data(fund_asset_code)

        daily_rows = (
            AssetFundDailyData.query.filter_by(asset_id=fund_asset.id)
            .order_by(AssetFundDailyData.f_date.asc())
            .all()
        )
        fee_rules = AssetFundFeeRule.query.filter_by(asset_id=fund_asset.id).all()
        holding_rows = AssetHoldingData.query.filter_by(
            ah_holding_asset_id=fund_asset.id
        ).all()
        stock_asset = Asset.query.filter_by(asset_name="贵州茅台").one()
        stock_code = AssetCode.query.filter_by(asset_id=stock_asset.id).one()

        assert len(daily_rows) == 2
        assert daily_rows[0].f_netvalue == 10000
        assert daily_rows[1].f_totvalue == 13000
        assert len(fee_rules) == 1
        assert fee_rules[0].fee_rates == 150
        assert len(holding_rows) == 1
        assert holding_rows[0].ah_holding_percent == 1234
        assert stock_code.code_xq == "600519"
        assert mock_fund_info.called
        assert mock_get_rt.called
