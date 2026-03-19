from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from web.common.enum.asset_enum import AssetTypeEnum
from web.models import db
from web.models.asset.AssetFundDailyData import AssetFundDailyData
from web.models.asset.AssetFundFeeRule import AssetFundFeeRule
from web.models.asset.AssetHoldingData import AssetHoldingData
from web.models.asset.asset import Asset, AssetCurrentDTO
from web.models.asset.asset_alias import AssetAlias
from web.models.asset.asset_code import AssetCode
from web.models.asset.asset_fund import AssetFund
from web.services.asset.asset_service import asset_service
from web.webtest.test_base import TestBaseLiteWithRollback


pytestmark = [pytest.mark.local, pytest.mark.integration]


class _FundInfoStub:
    def __init__(self):
        self.price = pd.DataFrame(
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
        )
        self.rate = 1.5
        self.feeinfo = []

    def get_stock_holdings(self, year, season):
        return pd.DataFrame([{"code": "600519.SH", "ratio": 12.34}])


class _FundInfoStubNoHoldings(_FundInfoStub):
    def get_stock_holdings(self, year, season):
        return pd.DataFrame()


def _seed_fund_asset(lite_rollback_session):
    asset = AssetFund(
        asset_name="阶段4基金",
        asset_code="000001",
        asset_short_code="JD4",
        asset_type=AssetTypeEnum.FUND.value,
        asset_status=0,
        currency=0,
        market=0,
        fund_type="STOCK_FUND",
        trading_mode="OPEN_END",
        fund_status=0,
        fund_company="阶段4基金公司",
        fund_manager="阶段4基金经理",
    )
    lite_rollback_session.add(asset)
    lite_rollback_session.flush()

    lite_rollback_session.add(
        AssetAlias(
            asset_id=asset.id,
            provider_code="manual",
            provider_symbol="000001",
            provider_name="manual",
            is_primary=True,
            status=1,
        )
    )
    lite_rollback_session.add(
        AssetCode(
            asset_id=asset.id,
            code_ttjj="F000001",
            code_xq="000001",
        )
    )
    lite_rollback_session.commit()
    return asset.id


class TestTask01AssetManagementSQLite(TestBaseLiteWithRollback):
    @patch("web.services.asset.asset_service.time.sleep", return_value=None)
    @patch("web.services.asset.asset_service.random.randint", return_value=0)
    @patch("web.services.asset.asset_service.databox.get_rt")
    @patch("web.services.asset.asset_service.databox.fetch_online_daily_data")
    @patch("web.services.asset.asset_service.databox.fund_info")
    def test_asset_service_init_fund_asset_data_writes_daily_fee_and_holding_and_api_reads_latest_data(
        self,
        mock_fund_info,
        mock_fetch_daily,
        mock_get_rt,
        _mock_randint,
        _mock_sleep,
        lite_rollback_session,
        lite_webtest_client,
    ):
        asset_id = _seed_fund_asset(lite_rollback_session)
        asset_code = AssetCode.query.filter_by(asset_id=asset_id).one()

        mock_fund_info.return_value = _FundInfoStub()
        mock_fetch_daily.return_value = pd.DataFrame(
            [
                {
                    "date": datetime(2024, 1, 1),
                    "open": 1.0,
                    "close": 1.2,
                    "high": 1.3,
                    "low": 0.9,
                    "volume": 100,
                    "percent": 1.0,
                },
                {
                    "date": datetime(2024, 1, 2),
                    "open": 1.1,
                    "close": 1.3,
                    "high": 1.4,
                    "low": 1.0,
                    "volume": 200,
                    "percent": 1.5,
                },
            ]
        )
        mock_get_rt.return_value = AssetCurrentDTO(
            code="600519",
            name="贵州茅台",
            price=188800,
            market=0,
            currency=0,
        )

        asset_service.init_fund_asset_data(asset_code)

        daily_rows = (
            AssetFundDailyData.query.filter_by(asset_id=asset_id)
            .order_by(AssetFundDailyData.f_date.asc())
            .all()
        )
        fee_rows = AssetFundFeeRule.query.filter_by(asset_id=asset_id).all()
        holding_rows = AssetHoldingData.query.filter_by(
            ah_holding_asset_id=asset_id
        ).all()
        stock_asset = Asset.query.filter_by(asset_name="贵州茅台").one()
        stock_code = AssetCode.query.filter_by(asset_id=stock_asset.id).one()

        assert len(daily_rows) == 2
        assert daily_rows[-1].f_close == 13000
        assert len(fee_rows) == 1
        assert fee_rows[0].fee_rates == 150
        assert len(holding_rows) == 1
        assert holding_rows[0].ah_holding_percent == 1234
        assert stock_code.code_xq == "600519"

        list_response = lite_webtest_client.get(
            "/api/asset/list/?page=1&pageSize=20&assetName=阶段4基金"
        )
        assert list_response.status_code == 200
        list_payload = list_response.get_json()
        assert list_payload["success"] is True
        assert list_payload["data"]["total"] == 1
        assert list_payload["data"]["items"][0]["assetName"] == "阶段4基金"
        assert list_payload["data"]["items"][0]["assetCode"] == "000001"
        assert list_payload["data"]["items"][0]["date"] == "2024-01-02"
        assert list_payload["data"]["items"][0]["close"] == "13000"

    def test_asset_detail_returns_fund_payload(self, lite_rollback_session, lite_webtest_client):
        asset_id = _seed_fund_asset(lite_rollback_session)

        response = lite_webtest_client.get(f"/api/asset/{asset_id}")

        assert response.status_code == 200
        payload = response.get_json()

        assert payload["success"] is True
        assert payload["data"]["id"] == asset_id
        assert payload["data"]["assetName"] == "阶段4基金"
        assert payload["data"]["assetCode"] == "000001"
        assert payload["data"]["fundType"] == "STOCK_FUND"
        assert payload["data"]["tradingMode"] == "OPEN_END"

    @patch("web.services.asset.asset_service.time.sleep", return_value=None)
    @patch("web.services.asset.asset_service.random.randint", return_value=0)
    @patch("web.services.asset.asset_service.databox.get_rt")
    @patch("web.services.asset.asset_service.databox.fetch_online_daily_data", return_value=None)
    @patch("web.services.asset.asset_service.databox.fund_info")
    def test_asset_service_init_fund_asset_data_should_fall_back_to_ttjj_when_xq_fetch_returns_none(
        self,
        mock_fund_info,
        mock_fetch_daily,
        mock_get_rt,
        _mock_randint,
        _mock_sleep,
        lite_rollback_session,
    ):
        asset_id = _seed_fund_asset(lite_rollback_session)
        asset_code = AssetCode.query.filter_by(asset_id=asset_id).one()

        mock_fund_info.return_value = _FundInfoStubNoHoldings()
        mock_get_rt.return_value = AssetCurrentDTO(
            code="600519",
            name="贵州茅台",
            price=188800,
            market=0,
            currency=0,
        )

        asset_service.init_fund_asset_data(asset_code)

        daily_rows = (
            AssetFundDailyData.query.filter_by(asset_id=asset_id)
            .order_by(AssetFundDailyData.f_date.asc())
            .all()
        )
        assert len(daily_rows) == 2
