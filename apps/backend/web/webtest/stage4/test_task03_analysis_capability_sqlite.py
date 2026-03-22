from __future__ import annotations

from datetime import date, datetime
from unittest.mock import patch

import pandas as pd
import pytest

from web.models import db
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.asset.asset import Asset
from web.models.asset.asset_code import AssetCode
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.record.record import Record
from web.services.analysis.transaction_analysis_service import (
    GridTransactionAnalysisService,
    GridTypeTransactionAnalysisService,
)
from web.webtest.test_base import TestBaseLiteWithRollback


pytestmark = [pytest.mark.local, pytest.mark.integration]


def _build_summary_frame(fund_name: str, fund_code: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "基金名称": fund_name,
                "基金代码": fund_code,
                "当日净值": 1.0,
                "单位成本": 0.95,
                "持有份额": 1000,
                "基金现值": 1000,
                "基金总申购": 950,
                "历史最大占用": 950,
                "基金持有成本": 950,
                "基金分红与赎回": 0,
                "换手率": 0.1,
                "基金收益总额": 50,
                "投资收益率": 0.0526,
                "内部收益率": 0.0526,
            },
            {
                "基金名称": "总计",
                "基金代码": fund_code,
                "当日净值": 1.0,
                "单位成本": 0.95,
                "持有份额": 1000,
                "基金现值": 1000,
                "基金总申购": 950,
                "历史最大占用": 950,
                "基金持有成本": 950,
                "基金分红与赎回": 0,
                "换手率": 0.1,
                "基金收益总额": 50,
                "投资收益率": 0.0526,
                "内部收益率": 0.0526,
            },
        ]
    )


class TestTask03AnalysisCapabilitySQLite(TestBaseLiteWithRollback):
    @pytest.fixture(autouse=True)
    def setup_data(self, lite_rollback_session):
        self.analysis_date = date(2024, 1, 15)
        self.asset = Asset(
            asset_code="000001",
            asset_name="阶段4分析资产",
            asset_type=1,
            currency=1,
            market=1,
            asset_status=0,
        )
        lite_rollback_session.add(self.asset)
        lite_rollback_session.flush()

        self.asset_code = AssetCode(code_xq="000001", asset_id=self.asset.id)
        lite_rollback_session.add(self.asset_code)
        lite_rollback_session.flush()

        self.grid = Grid(
            grid_name="阶段4分析网格",
            asset_id=self.asset.id,
            grid_status=Grid.get_status_enum().ENABLE.value,
        )
        lite_rollback_session.add(self.grid)
        lite_rollback_session.flush()

        self.grid_type = GridType(
            grid_id=self.grid.id,
            grid_type_status=0,
            type_name="阶段4分析网格类型",
            asset_id=self.asset.id,
        )
        lite_rollback_session.add(self.grid_type)
        lite_rollback_session.flush()

        lite_rollback_session.add(
            GridTypeDetail(
                grid_type_id=self.grid_type.id,
                grid_id=self.grid.id,
                gear="1",
                monitor_type=GridTypeDetail.get_monitor_type_enum().SELL.value,
                trigger_sell_price=11000,
                sell_price=11000,
                sell_shares=1000,
                actual_sell_shares=1000,
                sell_amount=11000000,
                trigger_purchase_price=9000,
                purchase_price=9000,
                purchase_amount=100000,
                purchase_shares=1111,
                profit=1000000,
                save_share_profit=0,
                save_share=0,
                is_current=False,
            )
        )

        self.record = Record(
            asset_id=self.asset.id,
            transactions_direction=Record.get_record_directoin_enum().SELL.value,
            transactions_date=datetime.combine(self.analysis_date, datetime.min.time()),
        )
        lite_rollback_session.add(self.record)
        lite_rollback_session.flush()

        lite_rollback_session.add(
            GridTypeRecord(
                grid_type_id=self.grid_type.id,
                record_id=self.record.id,
            )
        )
        lite_rollback_session.flush()

        lite_rollback_session.commit()

    @patch("web.services.analysis.transaction_analysis_service.webutils.is_trading_day")
    @patch("web.services.analysis.transaction_analysis_service.databox.trade")
    @patch("web.services.analysis.transaction_analysis_service.databox.summary")
    @patch("web.services.analysis.transaction_analysis_service.databox.get_trade_fund_name")
    @patch("web.services.analysis.transaction_analysis_service.databox.remove_trade_cache")
    def test_analysis_generation_then_query_returns_grid_and_grid_type_results(
        self,
        mock_remove_cache,
        mock_get_trade_fund_name,
        mock_summary,
        mock_trade,
        mock_is_trading_day,
        lite_webtest_client,
    ):
        mock_is_trading_day.return_value = True
        mock_trade.return_value = 1
        mock_get_trade_fund_name.return_value = ("阶段4分析基金",)
        mock_summary.return_value = _build_summary_frame("阶段4分析基金", "000001")

        grid_type_service = GridTypeTransactionAnalysisService(
            grid_type_id=self.grid_type.id
        )
        grid_type_service.trade_analysis(start=self.analysis_date, end=self.analysis_date)

        grid_service = GridTransactionAnalysisService(grid_id=self.grid.id)
        grid_service.trade_analysis(start=self.analysis_date, end=self.analysis_date)

        grid_type_response = lite_webtest_client.get(
            f"/api/analysis/grid-type-result/{self.grid_type.id}"
        )
        assert grid_type_response.status_code == 200
        grid_type_payload = grid_type_response.get_json()
        assert grid_type_payload["success"] is True
        assert grid_type_payload["data"]["gridTypeId"] == self.grid_type.id
        assert grid_type_payload["data"]["gridId"] == self.grid.id
        assert grid_type_payload["data"]["businessType"] == (
            GridTradeAnalysisData.get_business_type_enum().GRID_TYPE_ANALYSIS.value
        )
        assert grid_type_payload["data"]["sellTimes"] == 1
        assert grid_type_payload["data"]["holdingTimes"] == 1

        grid_response = lite_webtest_client.get(f"/api/analysis/grid-result/{self.grid.id}")
        assert grid_response.status_code == 200
        grid_payload = grid_response.get_json()
        assert grid_payload["success"] is True
        assert grid_payload["data"]["gridId"] == self.grid.id
        assert grid_payload["data"]["businessType"] == (
            GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value
        )
        assert grid_payload["data"]["sellTimes"] == 1
        assert grid_payload["data"]["holdingTimes"] == 1

        assert GridTradeAnalysisData.query.count() == 2
        saved_grid_type_analysis = GridTradeAnalysisData.query.filter_by(
            grid_type_id=self.grid_type.id,
            business_type=GridTradeAnalysisData.get_business_type_enum().GRID_TYPE_ANALYSIS.value,
        ).one()
        saved_grid_analysis = GridTradeAnalysisData.query.filter_by(
            grid_id=self.grid.id,
            business_type=GridTradeAnalysisData.get_business_type_enum().GRID_ANALYSIS.value,
        ).one()
        saved_base_analysis = TradeAnalysisData.query.filter_by(
            asset_id=self.asset.id
        ).order_by(TradeAnalysisData.record_date.asc()).all()

        assert saved_grid_type_analysis.grid_type_id == self.grid_type.id
        assert saved_grid_analysis.grid_id == self.grid.id
        assert len(saved_base_analysis) == 2
        assert mock_trade.call_count == 2
        assert mock_summary.call_count == 2
        assert mock_get_trade_fund_name.call_count == 2
        assert mock_remove_cache.call_count == 2
