from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import pytest
from flask import Flask
from sqlalchemy import MetaData, create_engine, select, text
from sqlalchemy.exc import OperationalError

from web import settings
from web.lite_bootstrap import bootstrap_lite_database
from web.models import db, ini_app
from web.services.migration import (
    MigrationConfig,
    MysqlToSqliteBusinessMigrationService,
    execute_with_retries,
    is_retryable_source_error,
)
from web.weblogger import logger_initialize


pytestmark = [pytest.mark.local, pytest.mark.integration]


def _bootstrap_lite_sqlite(db_path: Path, cache_dir: Path) -> None:
    app = Flask("test-mysql-to-sqlite-migration")
    old_env = {
        "LITE_DB_PATH": os.environ.get("LITE_DB_PATH"),
        "LITE_XALPHA_CACHE_DIR": os.environ.get("LITE_XALPHA_CACHE_DIR"),
        "LITE_XALPHA_CACHE_BACKEND": os.environ.get("LITE_XALPHA_CACHE_BACKEND"),
    }

    os.environ["LITE_DB_PATH"] = str(db_path)
    os.environ["LITE_XALPHA_CACHE_DIR"] = str(cache_dir)
    os.environ["LITE_XALPHA_CACHE_BACKEND"] = "csv"

    try:
        app.config.from_object(settings.config["lite"])
        settings.apply_runtime_overrides(app, "lite")
        app.config["_config_name"] = "lite"
        app.config["_config_class_name"] = settings.config["lite"].__name__
        logger_initialize.init_logger(app)

        ctx = app.app_context()
        ctx.push()
        try:
            assert ini_app(app) is True
            bootstrap_lite_database(app)
        finally:
            db.session.remove()
            for engine in db.engines.values():
                engine.dispose()
            ctx.pop()
    finally:
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _seed_source_database(source_db_path: Path) -> None:
    _bootstrap_lite_sqlite(source_db_path, source_db_path.parent / "source-cache")
    engine = create_engine(f"sqlite:///{source_db_path}", future=True)
    metadata = MetaData()
    metadata.reflect(
        bind=engine,
        only=[
            "tb_index_base",
            "tb_asset",
            "tb_asset_fund",
            "tb_asset_fund_etf",
            "tb_grid",
            "tb_grid_type",
            "tb_record",
            "tb_trade_reference",
            "tb_trade_analysis_data",
            "tb_grid_trade_analysis_data",
            "tb_amount_trade_analysis_data",
            "tb_notification",
            "system_settings",
        ],
    )
    tables = metadata.tables
    now = datetime(2026, 3, 20, 12, 0, 0)

    with engine.begin() as connection:
        connection.execute(
            tables["tb_index_base"].insert(),
            [
                {
                    "id": 10,
                    "index_code": "000300.SH",
                    "index_name": "沪深300",
                    "index_type": 0,
                    "market": 0,
                    "index_status": 1,
                }
            ],
        )
        connection.execute(
            tables["tb_asset"].insert(),
            [
                {
                    "id": 100,
                    "asset_code": "510300",
                    "asset_short_code": "300ETF",
                    "asset_status": 0,
                    "currency": 0,
                    "asset_type": 3,
                    "asset_name": "沪深300ETF",
                    "market": 0,
                    "asset_subtype": "fund",
                }
            ],
        )
        connection.execute(
            tables["tb_asset_fund"].insert(),
            [
                {
                    "id": 100,
                    "fund_type": "INDEX_FUND",
                    "trading_mode": "ETF",
                    "fund_status": 0,
                }
            ],
        )
        connection.execute(
            tables["tb_asset_fund_etf"].insert(),
            [
                {
                    "id": 100,
                    "tracking_index_code": "000300",
                    "tracking_index_name": "沪深300",
                    "index_id": 10,
                    "primary_exchange": "SH",
                }
            ],
        )
        connection.execute(
            tables["tb_grid"].insert(),
            [{"id": 200, "asset_id": 100, "grid_name": "主网格", "grid_status": 0}],
        )
        connection.execute(
            tables["tb_grid_type"].insert(),
            [
                {
                    "id": 300,
                    "grid_id": 200,
                    "grid_type_status": 0,
                    "asset_id": 100,
                    "type_name": "核心策略",
                }
            ],
        )
        connection.execute(
            tables["tb_record"].insert(),
            [
                {
                    "id": 400,
                    "transactions_fee": 10,
                    "transactions_share": 1000,
                    "transactions_date": now,
                    "asset_id": 100,
                    "transactions_price": 12345,
                    "transactions_direction": 1,
                    "transactions_amount": 1234500,
                }
            ],
        )
        connection.execute(
            tables["tb_trade_reference"].insert(),
            [
                {
                    "id": 500,
                    "record_id": 400,
                    "group_type": 1,
                    "group_id": 300,
                }
            ],
        )
        connection.execute(
            tables["tb_trade_analysis_data"].insert(),
            [
                {
                    "id": 600,
                    "asset_id": 100,
                    "record_date": now,
                    "analysis_type": 1,
                    "sub_analysis_type": "grid_trade_analysis",
                },
                {
                    "id": 601,
                    "asset_id": 100,
                    "record_date": now,
                    "analysis_type": 3,
                    "sub_analysis_type": "amount_trade_analysis",
                },
            ],
        )
        connection.execute(
            tables["tb_grid_trade_analysis_data"].insert(),
            [
                {
                    "id": 600,
                    "business_type": 1,
                    "grid_type_id": 300,
                    "grid_id": 200,
                    "sell_times": 2,
                    "estimate_maximum_occupancy": 100000,
                    "holding_times": 1,
                    "dividend_yield": 2222,
                }
            ],
        )
        connection.execute(
            tables["tb_amount_trade_analysis_data"].insert(),
            [{"id": 601, "dividend_yield": 3333}],
        )
        connection.execute(
            tables["tb_notification"].insert(),
            [
                {
                    "id": 700,
                    "business_type": 0,
                    "notice_type": 0,
                    "notice_status": 0,
                    "title": "迁移通知",
                }
            ],
        )
        connection.execute(
            tables["system_settings"].insert(),
            [
                {
                    "id": 800,
                    "key": "mail.smtp_host",
                    "value": "smtp.example.com",
                    "setting_type": "string",
                    "group": "mail",
                }
            ],
        )
        connection.execute(
            text(
                """
                UPDATE system_settings
                SET value = :value
                WHERE key = 'version:enum'
                """
            ),
            {"value": json.dumps({"global": 1}, ensure_ascii=False)},
        )

    engine.dispose()


def test_migration_service_moves_business_tables_and_preserves_runtime_settings(tmp_path):
    source_db_path = tmp_path / "source.db"
    target_db_path = tmp_path / "target.db"
    report_path = tmp_path / "migration-report.json"
    _seed_source_database(source_db_path)

    config = MigrationConfig(
        source_url=f"sqlite:///{source_db_path}",
        target_sqlite=target_db_path,
        report_path=report_path,
        tables=(
            "tb_index_base",
            "tb_asset",
            "tb_asset_fund",
            "tb_asset_fund_etf",
            "tb_grid",
            "tb_grid_type",
            "tb_record",
            "tb_trade_reference",
            "tb_trade_analysis_data",
            "tb_grid_trade_analysis_data",
            "tb_amount_trade_analysis_data",
            "tb_notification",
            "system_settings",
        ),
        batch_size=2,
    )

    report = MysqlToSqliteBusinessMigrationService(config).run()

    assert report["status"] == "success"
    assert report_path.exists() is True

    target_engine = create_engine(f"sqlite:///{target_db_path}", future=True)
    target_metadata = MetaData()
    target_metadata.reflect(
        bind=target_engine,
        only=["tb_amount_trade_analysis_data", "system_settings", "tb_trade_reference"],
    )
    tables = target_metadata.tables

    with target_engine.connect() as connection:
        amount_row = connection.execute(
            select(tables["tb_amount_trade_analysis_data"]).where(
                tables["tb_amount_trade_analysis_data"].c.id == 601
            )
        ).mappings().one()
        business_setting = connection.execute(
            select(tables["system_settings"]).where(
                tables["system_settings"].c.key == "mail.smtp_host"
            )
        ).mappings().one()
        runtime_setting = connection.execute(
            select(tables["system_settings"]).where(
                tables["system_settings"].c.key == "version:enum"
            )
        ).mappings().one()
        trade_ref = connection.execute(
            select(tables["tb_trade_reference"]).where(
                tables["tb_trade_reference"].c.id == 500
            )
        ).mappings().one()

    target_engine.dispose()

    assert amount_row["dividend_yield"] == 3333
    assert business_setting["value"] == "smtp.example.com"
    assert json.loads(runtime_setting["value"])["global"] != 1
    assert trade_ref["group_id"] == 300

    persisted_report = json.loads(report_path.read_text(encoding="utf-8"))
    assert persisted_report["status"] == "success"
    assert len(persisted_report["migration"]["tables"]) == 13


def test_execute_with_retries_recovers_from_retryable_operational_error():
    attempts = {"count": 0}
    retry_delays: list[float] = []

    def _operation():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise OperationalError("SELECT 1", None, OSError("Lost connection to MySQL server"))
        return "ok"

    result = execute_with_retries(
        "source batch",
        _operation,
        max_retries=3,
        initial_delay_seconds=0.2,
        backoff_multiplier=2.0,
        is_retryable=is_retryable_source_error,
        on_retry=lambda retry_index, delay_seconds, exc: retry_delays.append(delay_seconds),
        sleep=lambda _: None,
    )

    assert result == "ok"
    assert attempts["count"] == 3
    assert retry_delays == [0.2, 0.4]


def test_migration_service_persists_precheck_progress_before_failure(tmp_path):
    source_db_path = tmp_path / "source.db"
    target_db_path = tmp_path / "target.db"
    report_path = tmp_path / "failed-precheck-report.json"
    _seed_source_database(source_db_path)

    config = MigrationConfig(
        source_url=f"sqlite:///{source_db_path}",
        target_sqlite=target_db_path,
        report_path=report_path,
        tables=("tb_index_base", "tb_asset"),
    )
    service = MysqlToSqliteBusinessMigrationService(config)
    original_run_orphan_checks = service._run_orphan_checks

    def _failing_run_orphan_checks(side: str, table_name: str):
        if side == "source" and table_name == "tb_asset":
            raise RuntimeError("simulated precheck failure")
        return original_run_orphan_checks(side, table_name)

    service._run_orphan_checks = _failing_run_orphan_checks  # type: ignore[method-assign]

    with pytest.raises(RuntimeError, match="simulated precheck failure"):
        service.run()

    persisted_report = json.loads(report_path.read_text(encoding="utf-8"))
    assert persisted_report["status"] == "failed"
    assert persisted_report["phase"] == "precheck"
    assert persisted_report["current_table"] == "tb_asset"
    assert [row["table"] for row in persisted_report["precheck"]["tables"]] == ["tb_index_base"]


def test_migration_service_marks_keyboard_interrupt_as_interrupted(tmp_path):
    source_db_path = tmp_path / "source.db"
    target_db_path = tmp_path / "target.db"
    report_path = tmp_path / "interrupted-report.json"
    _seed_source_database(source_db_path)

    config = MigrationConfig(
        source_url=f"sqlite:///{source_db_path}",
        target_sqlite=target_db_path,
        report_path=report_path,
        tables=("tb_index_base",),
    )
    service = MysqlToSqliteBusinessMigrationService(config)

    def _raise_interrupt(selected_tables):
        raise KeyboardInterrupt()

    service._run_precheck = _raise_interrupt  # type: ignore[method-assign]

    with pytest.raises(KeyboardInterrupt):
        service.run()

    persisted_report = json.loads(report_path.read_text(encoding="utf-8"))
    assert persisted_report["status"] == "interrupted"
    assert persisted_report["phase"] == "precheck"
    assert persisted_report["error"]["type"] == "KeyboardInterrupt"


def test_migration_service_replaces_reserved_runtime_system_settings_before_copy(tmp_path):
    source_db_path = tmp_path / "source.db"
    target_db_path = tmp_path / "target.db"
    report_path = tmp_path / "system-settings-report.json"
    _seed_source_database(source_db_path)

    source_engine = create_engine(f"sqlite:///{source_db_path}", future=True)
    with source_engine.begin() as connection:
        connection.execute(text("DELETE FROM system_settings WHERE key = 'version:enum'"))
        connection.execute(
            text(
                """
                UPDATE system_settings
                SET id = 1
                WHERE key = 'mail.smtp_host'
                """
            )
        )
    source_engine.dispose()

    config = MigrationConfig(
        source_url=f"sqlite:///{source_db_path}",
        target_sqlite=target_db_path,
        report_path=report_path,
        tables=("system_settings",),
    )

    report = MysqlToSqliteBusinessMigrationService(config).run()

    assert report["status"] == "success"

    target_engine = create_engine(f"sqlite:///{target_db_path}", future=True)
    with target_engine.connect() as connection:
        migrated_rows = connection.execute(
            text(
                """
                SELECT id, key, "group"
                FROM system_settings
                ORDER BY id
                """
            )
        ).mappings().all()
    target_engine.dispose()

    by_key = {row["key"]: row for row in migrated_rows}
    assert by_key["mail.smtp_host"]["id"] == 1
    assert by_key["version:enum"]["group"] == "runtime_version"
