from __future__ import annotations

import pytest
from alembic import command
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect, text

from web import create_app
from web.common.enum.asset_enum import AssetTypeEnum
from web.common.enum.business.index.index_enum import IndexTypeEnum
from web.lite_bootstrap import (
    LITE_STAGE5_REQUIRED_TABLES,
    build_lite_alembic_config,
    bootstrap_lite_database,
    get_lite_head_revision,
)
from web.models import db
from web.models.asset.asset_fund import AssetFundETF, AssetFundLOF
from web.models.index.index_stock import StockIndex

pytestmark = [pytest.mark.local, pytest.mark.integration]


def test_lite_bootstrap_stage5_builds_core_schema(tmp_path, monkeypatch):
    db_path = tmp_path / "snowball_lite.db"
    cache_dir = tmp_path / "lite_xalpha_cache"
    monkeypatch.setenv("LITE_DB_PATH", str(db_path))
    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("LITE_XALPHA_CACHE_BACKEND", "csv")
    monkeypatch.setenv("LITE_ENABLE_SCHEDULER", "false")

    app = create_app("lite")

    with app.app_context():
        bootstrap_lite_database(app)

        engine = db.engines["snowball"]
        table_names = set(inspect(engine).get_table_names())

        with engine.connect() as conn:
            version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()

        assert version == get_lite_head_revision()
        assert LITE_STAGE5_REQUIRED_TABLES.issubset(table_names)
        assert {
            "tb_apscheduler_log",
            "tb_apscheduler_job_state",
            "system_settings",
            "tb_notification",
            "tb_index_base",
            "tb_index_stock",
            "tb_index_alias",
            "tb_amount_trade_analysis_data",
            "tb_category",
            "tb_asset_category",
        }.issubset(table_names)

    db.session.remove()
    for engine in db.engines.values():
        engine.dispose()


def test_lite_bootstrap_upgrades_existing_stage3_baseline_to_current_head(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "snowball_lite.db"
    cache_dir = tmp_path / "lite_xalpha_cache"
    monkeypatch.setenv("LITE_DB_PATH", str(db_path))
    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("LITE_XALPHA_CACHE_BACKEND", "csv")
    monkeypatch.setenv("LITE_ENABLE_SCHEDULER", "false")

    app = create_app("lite")

    with app.app_context():
        command.upgrade(build_lite_alembic_config(app), "lite_stage3_baseline")

        engine = db.engines["snowball"]
        table_names_before = set(inspect(engine).get_table_names())
        assert "tb_apscheduler_log" not in table_names_before
        assert "tb_apscheduler_job_state" not in table_names_before

        with engine.connect() as conn:
            version_before = conn.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar()

        assert version_before == "lite_stage3_baseline"

        bootstrap_lite_database(app)

        table_names_after = set(inspect(engine).get_table_names())
        with engine.connect() as conn:
            version_after = conn.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar()

        assert "tb_apscheduler_log" in table_names_after
        assert "tb_apscheduler_job_state" in table_names_after
        assert version_after == get_lite_head_revision()

    db.session.remove()
    for engine in db.engines.values():
        engine.dispose()


@pytest.mark.parametrize(
    "fund_cls,asset_type,fund_kwargs",
    [
        (
            AssetFundETF,
            AssetTypeEnum.FUND_ETF.value,
            {
                "fund_type": "INDEX_FUND",
                "trading_mode": "ETF",
                "tracking_index_code": "000300",
                "tracking_index_name": "沪深300",
                "primary_exchange": "SH",
            },
        ),
        (
            AssetFundLOF,
            AssetTypeEnum.FUND_LOF.value,
            {
                "fund_type": "INDEX_FUND",
                "trading_mode": "LOF",
                "listing_exchange": "SH",
            },
        ),
    ],
)
def test_lite_bootstrap_stage5_rejects_invalid_index_fk(
    tmp_path,
    monkeypatch,
    fund_cls,
    asset_type,
    fund_kwargs,
):
    db_path = tmp_path / "snowball_lite.db"
    cache_dir = tmp_path / "lite_xalpha_cache"
    monkeypatch.setenv("LITE_DB_PATH", str(db_path))
    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("LITE_XALPHA_CACHE_BACKEND", "csv")

    app = create_app("lite")

    with app.app_context():
        bootstrap_lite_database(app)

        valid_index = StockIndex(
            index_code="000300.SH",
            index_name="沪深300",
            index_type=IndexTypeEnum.STOCK.value,
            market=0,
            index_status=1,
        )
        db.session.add(valid_index)
        db.session.commit()

        db.session.add(
            fund_cls(
                asset_name="非法索引基金",
                asset_type=asset_type,
                asset_status=0,
                currency=0,
                market=0,
                fund_status=0,
                index_id=valid_index.id + 9999,
                **fund_kwargs,
            )
        )

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

    db.session.remove()
    for engine in db.engines.values():
        engine.dispose()
