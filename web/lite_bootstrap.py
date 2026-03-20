from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows 下没有 fcntl
    fcntl = None

from alembic import command
from alembic.config import Config

from web.common.enum.version_enum import VersionKeyEnum
from web.common.utils.backend_paths import get_migration_directory_by_env
from web.common.utils.enum_utils import record_enum_version_to_sqlite


LITE_BASELINE_REVISION = "lite_stage3_baseline"
LITE_STAGE5_REQUIRED_TABLES = {
    "tb_asset",
    "tb_asset_code",
    "tb_asset_fund_daily_data",
    "tb_asset_fund_fee_rule",
    "tb_asset_holding_data",
    "tb_asset_category",
    "tb_amount_trade_analysis_data",
    "tb_category",
    "tb_grid",
    "tb_grid_type",
    "tb_grid_type_detail",
    "tb_grid_type_record",
    "tb_record",
    "tb_trade_analysis_data",
    "tb_grid_trade_analysis_data",
    "tb_index_base",
    "tb_index_stock",
    "tb_index_alias",
    "tb_notification",
    "system_settings",
}

# 阶段 3 的旧名字保留兼容，实际口径已经收口到阶段 5。
LITE_STAGE3_REQUIRED_TABLES = LITE_STAGE5_REQUIRED_TABLES

def get_lite_migration_directory() -> Path:
    return get_migration_directory_by_env("lite")


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


def _get_expected_revision(revision: str) -> str:
    return LITE_BASELINE_REVISION if revision == "head" else revision


def _get_sqlite_table_names(db_path: Path) -> set[str]:
    if not db_path.exists():
        return set()

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    return {row[0] for row in rows}


def _get_sqlite_revision(db_path: Path) -> str | None:
    table_names = _get_sqlite_table_names(db_path)
    if "alembic_version" not in table_names:
        return None

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT version_num FROM alembic_version LIMIT 1"
        ).fetchone()

    return row[0] if row else None


def _lite_schema_ready(db_path: Path, revision: str) -> bool:
    table_names = _get_sqlite_table_names(db_path)
    if not LITE_STAGE5_REQUIRED_TABLES.issubset(table_names):
        return False

    return _get_sqlite_revision(db_path) == _get_expected_revision(revision)


@contextmanager
def _lite_bootstrap_lock(db_path: Path):
    lock_path = db_path.with_suffix(f"{db_path.suffix}.bootstrap.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    with lock_path.open("w", encoding="utf-8") as lock_file:
        if fcntl is not None:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def bootstrap_lite_database(app, revision: str = "head") -> None:
    if app.config.get("_config_name") != "lite":
        raise ValueError("bootstrap_lite_database 只支持 lite 配置")

    runtime_paths = ensure_lite_runtime_paths(app)
    db_path = runtime_paths["db_path"]

    with _lite_bootstrap_lock(db_path):
        if not _lite_schema_ready(db_path, revision):
            command.upgrade(build_lite_alembic_config(app), revision)

        record_enum_version_to_sqlite(
            key=VersionKeyEnum.ENUM.value,
            logger=app.logger,
            merge=False,
        )
