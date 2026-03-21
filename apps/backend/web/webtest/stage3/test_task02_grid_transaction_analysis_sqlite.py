from __future__ import annotations

from datetime import date, datetime
from unittest.mock import patch

import pandas as pd
import pytest

from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.asset.asset import Asset
from web.models.asset.asset_code import AssetCode
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.models.grid.GridTypeRecord import GridTypeRecord
from web.models.record.record import Record
from web.services.analysis.transaction_analysis_service import GridTransactionAnalysisService
from web.webtest.test_base import TestBaseLiteWithRollback


@pytest.mark.analysis
@pytest.mark.grid
class TestGridTransactionAnalysisSQLiteStage3(TestBaseLiteWithRollback):
    @pytest.fixture(autouse=True)
    def setup_test_data(self, lite_rollback_session):
        self.test_date = date(2024, 1, 15)

        asset = Asset(
            asset_code="000001",
            asset_name="测试资产",
            asset_type=1,
            currency=1,
            market=1,
            asset_status=0,
        )
        lite_rollback_session.add(asset)
        lite_rollback_session.flush()
        self.test_asset_id = asset.id

        grid = Grid(
            grid_name="测试网格",
            asset_id=self.test_asset_id,
            grid_status=Grid.get_status_enum().ENABLE.value,
        )
        lite_rollback_session.add(grid)
        lite_rollback_session.flush()
        self.test_grid_id = grid.id

        grid_type = GridType(
            grid_id=self.test_grid_id,
            grid_type_status=0,
            type_name="测试网格类型",
            asset_id=self.test_asset_id,
        )
        lite_rollback_session.add(grid_type)
        lite_rollback_session.flush()

        lite_rollback_session.add(
            AssetCode(
                code_xq="000001",
                asset_id=self.test_asset_id,
            )
        )

        lite_rollback_session.add(
            GridTypeDetail(
                grid_type_id=grid_type.id,
                grid_id=self.test_grid_id,
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

        record = Record(
            asset_id=self.test_asset_id,
            transactions_direction=Record.get_record_directoin_enum().SELL.value,
            transactions_date=datetime.combine(self.test_date, datetime.min.time()),
        )
        lite_rollback_session.add(record)
        lite_rollback_session.flush()

        lite_rollback_session.add(
            GridTypeRecord(
                grid_type_id=grid_type.id,
                record_id=record.id,
            )
        )
        lite_rollback_session.flush()

    @patch("web.databox.databox.trade")
    @patch("web.databox.databox.summary")
    @patch("web.databox.databox.get_trade_fund_name")
    @patch("web.databox.databox.remove_trade_cache")
    @patch("web.common.utils.WebUtils.webutils.is_trading_day")
    def test_trade_analysis_persists_stage3_business_chain(
        self,
        mock_is_trading_day,
        mock_remove_cache,
        mock_get_fund_name,
        mock_summary,
        mock_trade,
    ):
        mock_is_trading_day.return_value = True
        mock_trade.return_value = 1
        mock_get_fund_name.return_value = ("测试基金",)
        mock_summary.return_value = pd.DataFrame(
            {
                "基金名称": ["测试基金"],
                "基金代码": ["000001"],
                "当日净值": [10000],
                "单位成本": [9500],
                "持有份额": [1000000],
                "基金现值": [10000000],
                "基金总申购": [9500000],
                "历史最大占用": [9500000],
                "基金持有成本": [9500000],
                "基金分红与赎回": [0],
                "换手率": [1000],
                "基金收益总额": [500000],
                "投资收益率": [526],
                "内部收益率": [526],
            }
        )

        service = GridTransactionAnalysisService(grid_id=self.test_grid_id)
        service.trade_analysis(start=self.test_date, end=self.test_date)

        saved_grid_analysis = GridTradeAnalysisData.query.one()
        saved_base_analysis = TradeAnalysisData.query.one()

        assert saved_grid_analysis.asset_id == self.test_asset_id
        assert saved_grid_analysis.grid_id == self.test_grid_id
        assert saved_grid_analysis.record_date.date() == self.test_date
        assert saved_grid_analysis.sell_times == 1
        assert saved_grid_analysis.holding_times == 1
        assert saved_base_analysis.id == saved_grid_analysis.id
        mock_trade.assert_called_once()
        mock_summary.assert_called_once()
        mock_get_fund_name.assert_called_once()
        mock_remove_cache.assert_called_once()
