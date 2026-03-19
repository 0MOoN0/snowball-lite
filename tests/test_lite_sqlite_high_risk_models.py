from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from web.common.enum.AnalysisEnum import (
    GridTransactionAnalysisBusinessTypeEnum,
    TransactionAnalysisTypeEnum,
)
from web.common.enum.asset_enum import AssetTypeEnum
from web.common.enum.business.index.index_enum import IndexTypeEnum
from web.models import db
from web.models.analysis.grid_trade_analysis_data import GridTradeAnalysisData
from web.models.analysis.trade_analysis_data import TradeAnalysisData
from web.models.asset.asset import Asset
from web.models.asset.asset_alias import AssetAlias
from web.models.asset.asset_fund import AssetFundETF
from web.models.index.index_alias import IndexAlias
from web.models.index.index_stock import StockIndex

pytestmark = pytest.mark.local


def _build_stock_index() -> StockIndex:
    return StockIndex(
        index_code="000300.SH",
        index_name="沪深300",
        index_type=IndexTypeEnum.STOCK.value,
        market=0,
        index_status=1,
        constituent_count=300,
    )


def _build_etf(index_id: int) -> AssetFundETF:
    return AssetFundETF(
        asset_name="沪深300ETF",
        asset_type=AssetTypeEnum.FUND_ETF.value,
        asset_status=0,
        currency=0,
        market=0,
        fund_type="INDEX_FUND",
        trading_mode="ETF",
        fund_status=0,
        index_id=index_id,
        tracking_index_code="000300",
        tracking_index_name="沪深300",
        primary_exchange="SH",
    )


def test_lite_sqlite_supports_joined_asset_and_index_models(lite_app):
    with lite_app.app_context():
        stock_index = _build_stock_index()
        db.session.add(stock_index)
        db.session.flush()

        db.session.add(
            IndexAlias(
                index_id=stock_index.id,
                provider_code="manual-index",
                provider_symbol="000300.SH",
                provider_name="manual",
                is_primary=True,
                status=1,
            )
        )

        etf = _build_etf(index_id=stock_index.id)
        db.session.add(etf)
        db.session.flush()

        db.session.add(
            AssetAlias(
                asset_id=etf.id,
                provider_code="manual-asset",
                provider_symbol="510300",
                provider_name="manual",
                is_primary=True,
                status=1,
            )
        )
        db.session.commit()
        db.session.expire_all()

        polymorphic_asset = Asset.query.filter_by(id=etf.id).one()
        stored_etf = AssetFundETF.query.filter_by(id=etf.id).one()
        stored_index = StockIndex.query.filter_by(id=stock_index.id).one()

        assert isinstance(polymorphic_asset, AssetFundETF)
        assert polymorphic_asset.asset_subtype == "asset_fund_etf"
        assert stored_etf.index.index_code == "000300.SH"
        assert stored_etf.aliases[0].provider_symbol == "510300"
        assert stored_index.aliases[0].provider_symbol == "000300.SH"

        stored_etf.asset_name = "沪深300ETF-更新"
        stored_etf.primary_exchange = "SZ"
        db.session.commit()
        db.session.expire_all()

        refreshed = AssetFundETF.query.filter_by(id=etf.id).one()
        assert refreshed.asset_name == "沪深300ETF-更新"
        assert refreshed.primary_exchange == "SZ"


def test_lite_sqlite_enforces_high_risk_model_constraints(lite_app):
    with lite_app.app_context():
        stock_index = _build_stock_index()
        db.session.add(stock_index)
        db.session.flush()

        db.session.add(
            IndexAlias(
                index_id=stock_index.id,
                provider_code="manual-index",
                provider_symbol="000300.SH",
                provider_name="manual",
                is_primary=True,
                status=1,
            )
        )
        db.session.commit()

        db.session.add(
            IndexAlias(
                index_id=stock_index.id,
                provider_code="manual-index",
                provider_symbol="000300.SH",
                provider_name="duplicate",
                is_primary=False,
                status=1,
            )
        )
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

        db.session.add(_build_etf(index_id=999999))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_lite_sqlite_supports_analysis_model_polymorphism(lite_app):
    with lite_app.app_context():
        analysis = GridTradeAnalysisData(
            asset_id=1,
            record_date=datetime(2024, 1, 2, 10, 0, 0),
            analysis_type=TransactionAnalysisTypeEnum.GRID.value,
            sub_analysis_type="grid_trade_analysis",
            business_type=GridTransactionAnalysisBusinessTypeEnum.GRID_ANALYSIS.value,
            purchase_amount=10000,
            present_value=10500,
            holding_cost=10000,
            profit=500,
            net_value=12345,
            sell_times=1,
            estimate_maximum_occupancy=20000,
            holding_times=2,
        )

        db.session.add(analysis)
        db.session.commit()
        db.session.expire_all()

        base_loaded = TradeAnalysisData.query.one()
        child_loaded = GridTradeAnalysisData.query.one()

        assert isinstance(base_loaded, GridTradeAnalysisData)
        assert base_loaded.sub_analysis_type == "grid_trade_analysis"
        assert child_loaded.business_type == (
            GridTransactionAnalysisBusinessTypeEnum.GRID_ANALYSIS.value
        )
        assert child_loaded.sell_times == 1

        child_loaded.sell_times = 3
        child_loaded.profit = 800
        db.session.commit()
        db.session.expire_all()

        refreshed = GridTradeAnalysisData.query.one()
        assert refreshed.sell_times == 3
        assert TradeAnalysisData.query.one().profit == 800
