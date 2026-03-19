from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config


LITE_STAGE3_REQUIRED_TABLES = {
    "tb_asset",
    "tb_asset_code",
    "tb_asset_fund_daily_data",
    "tb_asset_fund_fee_rule",
    "tb_asset_holding_data",
    "tb_grid",
    "tb_grid_type",
    "tb_grid_type_detail",
    "tb_grid_type_record",
    "tb_record",
    "tb_trade_analysis_data",
    "tb_grid_trade_analysis_data",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_lite_migration_directory() -> Path:
    return _repo_root() / "migrations_snowball_lite"


def ensure_lite_runtime_paths(app) -> dict[str, Path]:
    db_path = Path(app.config["LITE_DB_PATH"]).resolve()
    cache_dir = Path(app.config["XALPHA_CACHE_DIR"]).resolve()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    return {
        "db_path": db_path,
        "cache_dir": cache_dir,
    }


def build_lite_alembic_config(app) -> Config:
    migration_directory = get_lite_migration_directory()
    config = Config(str(migration_directory / "alembic.ini"))
    config.set_main_option("script_location", str(migration_directory))
    config.set_main_option("sqlalchemy.url", app.config["LITE_DB_URI"])
    return config


def bootstrap_lite_database(app, revision: str = "head") -> None:
    if app.config.get("_config_name") != "lite":
        raise ValueError("bootstrap_lite_database 只支持 lite 配置")

    ensure_lite_runtime_paths(app)
    command.upgrade(build_lite_alembic_config(app), revision)
