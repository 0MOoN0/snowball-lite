from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from flask import Flask
from sqlalchemy import MetaData, Table, and_, create_engine, func, or_, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.pool import NullPool

from web import settings
from web.common.enum.business.record.trade_reference_enum import (
    TradeReferenceGroupTypeEnum,
)
from web.common.enum.version_enum import VersionKeyEnum
from web.common.utils.enum_utils import record_enum_version_to_sqlite
from web.lite_bootstrap import bootstrap_lite_database
from web.models import db, ini_app
from web.weblogger import logger_initialize


RESERVED_SYSTEM_SETTING_KEYS = {VersionKeyEnum.ENUM.value}
RESERVED_SYSTEM_SETTING_GROUPS = {"runtime_version"}


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _grid_trade_reference_predicate(child_table: Table):
    return child_table.c.group_type == TradeReferenceGroupTypeEnum.GRID.value


@dataclass(frozen=True)
class RelationshipCheck:
    column: str
    parent_table: str
    parent_column: str = "id"
    predicate_factory: Callable[[Table], Any] | None = None


@dataclass(frozen=True)
class TableSpec:
    name: str
    primary_key: tuple[str, ...]
    relationships: tuple[RelationshipCheck, ...] = ()


FIRST_PHASE_TABLE_SPECS = (
    TableSpec("tb_category", ("id",)),
    TableSpec("tb_index_base", ("id",)),
    TableSpec("tb_asset", ("id",)),
    TableSpec(
        "tb_asset_exchange_fund",
        ("id",),
        relationships=(RelationshipCheck("id", "tb_asset"),),
    ),
    TableSpec(
        "tb_asset_fund",
        ("id",),
        relationships=(RelationshipCheck("id", "tb_asset"),),
    ),
    TableSpec(
        "tb_asset_fund_etf",
        ("id",),
        relationships=(
            RelationshipCheck("id", "tb_asset_fund"),
            RelationshipCheck("index_id", "tb_index_base"),
        ),
    ),
    TableSpec(
        "tb_asset_fund_lof",
        ("id",),
        relationships=(
            RelationshipCheck("id", "tb_asset_fund"),
            RelationshipCheck("index_id", "tb_index_base"),
        ),
    ),
    TableSpec(
        "tb_asset_alias",
        ("id",),
        relationships=(RelationshipCheck("asset_id", "tb_asset"),),
    ),
    TableSpec(
        "tb_asset_code",
        ("id",),
        relationships=(RelationshipCheck("asset_id", "tb_asset"),),
    ),
    TableSpec(
        "tb_asset_fund_daily_data",
        ("id",),
        relationships=(RelationshipCheck("asset_id", "tb_asset"),),
    ),
    TableSpec(
        "tb_asset_fund_fee_rule",
        ("id",),
        relationships=(RelationshipCheck("asset_id", "tb_asset"),),
    ),
    TableSpec(
        "tb_asset_holding_data",
        ("id",),
        relationships=(
            RelationshipCheck("asset_id", "tb_asset"),
            RelationshipCheck("ah_holding_asset_id", "tb_asset"),
        ),
    ),
    TableSpec(
        "tb_asset_category",
        ("asset_id", "category_id"),
        relationships=(
            RelationshipCheck("asset_id", "tb_asset"),
            RelationshipCheck("category_id", "tb_category"),
        ),
    ),
    TableSpec(
        "tb_index_stock",
        ("id",),
        relationships=(RelationshipCheck("id", "tb_index_base"),),
    ),
    TableSpec(
        "tb_index_alias",
        ("id",),
        relationships=(RelationshipCheck("index_id", "tb_index_base"),),
    ),
    TableSpec(
        "tb_grid",
        ("id",),
        relationships=(RelationshipCheck("asset_id", "tb_asset"),),
    ),
    TableSpec(
        "tb_grid_type",
        ("id",),
        relationships=(
            RelationshipCheck("grid_id", "tb_grid"),
            RelationshipCheck("asset_id", "tb_asset"),
        ),
    ),
    TableSpec(
        "tb_grid_type_detail",
        ("id",),
        relationships=(
            RelationshipCheck("grid_type_id", "tb_grid_type"),
            RelationshipCheck("grid_id", "tb_grid"),
        ),
    ),
    TableSpec(
        "tb_record",
        ("id",),
        relationships=(RelationshipCheck("asset_id", "tb_asset"),),
    ),
    TableSpec(
        "tb_trade_reference",
        ("id",),
        relationships=(
            RelationshipCheck("record_id", "tb_record"),
            RelationshipCheck(
                "group_id",
                "tb_grid_type",
                predicate_factory=_grid_trade_reference_predicate,
            ),
        ),
    ),
    TableSpec(
        "tb_grid_type_record",
        ("grid_type_id", "record_id"),
        relationships=(
            RelationshipCheck("grid_type_id", "tb_grid_type"),
            RelationshipCheck("record_id", "tb_record"),
        ),
    ),
    TableSpec(
        "tb_trade_analysis_data",
        ("id",),
        relationships=(RelationshipCheck("asset_id", "tb_asset"),),
    ),
    TableSpec(
        "tb_grid_trade_analysis_data",
        ("id",),
        relationships=(
            RelationshipCheck("id", "tb_trade_analysis_data"),
            RelationshipCheck("grid_type_id", "tb_grid_type"),
            RelationshipCheck("grid_id", "tb_grid"),
        ),
    ),
    TableSpec(
        "tb_amount_trade_analysis_data",
        ("id",),
        relationships=(RelationshipCheck("id", "tb_trade_analysis_data"),),
    ),
    TableSpec("tb_notification", ("id",)),
    TableSpec("system_settings", ("id",)),
)

FIRST_PHASE_TABLE_NAMES = tuple(spec.name for spec in FIRST_PHASE_TABLE_SPECS)
TABLE_SPECS_BY_NAME = {spec.name: spec for spec in FIRST_PHASE_TABLE_SPECS}


@dataclass
class MigrationConfig:
    source_url: str
    target_sqlite: Path | str
    report_path: Path | str
    tables: tuple[str, ...] | None = None
    batch_size: int = 1000
    dry_run: bool = False
    resume_from_table: str | None = None
    truncate_target: bool = False
    max_retries: int = 5
    retry_delay_seconds: float = 2.0
    retry_backoff: float = 1.5
    source_connect_timeout_seconds: int = 5
    source_read_timeout_seconds: int = 10
    source_write_timeout_seconds: int = 10

    def __post_init__(self) -> None:
        self.target_sqlite = Path(self.target_sqlite).expanduser().resolve()
        self.report_path = Path(self.report_path).expanduser().resolve()

        if self.batch_size <= 0:
            raise ValueError("batch_size 必须大于 0")
        if self.max_retries < 0:
            raise ValueError("max_retries 不能小于 0")
        if self.retry_delay_seconds < 0:
            raise ValueError("retry_delay_seconds 不能小于 0")
        if self.retry_backoff < 1:
            raise ValueError("retry_backoff 不能小于 1")
        if self.source_connect_timeout_seconds <= 0:
            raise ValueError("source_connect_timeout_seconds 必须大于 0")
        if self.source_read_timeout_seconds <= 0:
            raise ValueError("source_read_timeout_seconds 必须大于 0")
        if self.source_write_timeout_seconds <= 0:
            raise ValueError("source_write_timeout_seconds 必须大于 0")

        if self.tables:
            normalized = tuple(dict.fromkeys(table.strip() for table in self.tables if table.strip()))
            self.tables = normalized or None


def is_retryable_source_error(exc: BaseException) -> bool:
    if isinstance(exc, OperationalError):
        return True
    if isinstance(exc, DBAPIError) and exc.connection_invalidated:
        return True

    message = str(getattr(exc, "orig", exc)).lower()
    retryable_keywords = (
        "server has gone away",
        "lost connection",
        "connection reset",
        "connection refused",
        "broken pipe",
        "timed out",
        "timeout",
        "temporary failure",
    )
    return any(keyword in message for keyword in retryable_keywords)


def execute_with_retries(
    label: str,
    operation: Callable[[], Any],
    *,
    max_retries: int,
    initial_delay_seconds: float,
    backoff_multiplier: float,
    is_retryable: Callable[[BaseException], bool],
    on_retry: Callable[[int, float, BaseException], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> Any:
    retries_used = 0
    delay_seconds = initial_delay_seconds

    while True:
        try:
            return operation()
        except BaseException as exc:
            if not is_retryable(exc) or retries_used >= max_retries:
                raise

            retries_used += 1
            if on_retry is not None:
                on_retry(retries_used, delay_seconds, exc)
            if delay_seconds > 0:
                sleep(delay_seconds)
            delay_seconds *= backoff_multiplier


class MysqlToSqliteBusinessMigrationService:
    def __init__(self, config: MigrationConfig):
        self.config = config
        self.source_engine: Engine | None = None
        self.target_app: Flask | None = None
        self.target_app_context = None
        self.target_engine: Engine | None = None
        self.source_tables: dict[str, Table] = {}
        self.target_tables: dict[str, Table] = {}
        self.current_table_name: str | None = None
        self.retry_events: list[dict[str, Any]] = []
        self.table_retry_counts: dict[str, int] = {}
        self.report: dict[str, Any] = {
            "status": "running",
            "phase": "pending",
            "current_table": None,
            "started_at": _utcnow_iso(),
            "source_url": self._mask_source_url(config.source_url),
            "target_sqlite": str(self.config.target_sqlite),
            "report_path": str(self.config.report_path),
            "dry_run": self.config.dry_run,
            "batch_size": self.config.batch_size,
            "resume_from_table": self.config.resume_from_table,
            "truncate_target": self.config.truncate_target,
            "retry_policy": {
                "max_retries": self.config.max_retries,
                "retry_delay_seconds": self.config.retry_delay_seconds,
                "retry_backoff": self.config.retry_backoff,
                "source_connect_timeout_seconds": self.config.source_connect_timeout_seconds,
                "source_read_timeout_seconds": self.config.source_read_timeout_seconds,
                "source_write_timeout_seconds": self.config.source_write_timeout_seconds,
            },
            "precheck": {"tables": []},
            "migration": {"tables": []},
            "validation": {},
        }

    def run(self) -> dict[str, Any]:
        try:
            selected_tables = self._resolve_selected_tables()
            self.report["table_order"] = selected_tables

            self.report["phase"] = "prepare_target"
            self._prepare_target_runtime()
            self.report["phase"] = "prepare_source"
            self._prepare_source_engine()
            self.report["phase"] = "reflect"
            self._reflect_required_tables(selected_tables)

            self.report["phase"] = "precheck"
            precheck_rows = self._run_precheck(selected_tables)
            self.report["precheck"]["tables"] = precheck_rows

            if not self.config.dry_run:
                self.report["phase"] = "migrate"
                migration_rows = self._migrate_tables(selected_tables)
                self.report["migration"]["tables"] = migration_rows
                self._refresh_runtime_version()

            self.report["phase"] = "validate"
            self.report["validation"] = self._run_validation(selected_tables)
            self.report["phase"] = "finished"
            self.report["current_table"] = None
            self.report["status"] = "dry_run" if self.config.dry_run else "success"
            return self.report
        except BaseException as exc:
            self.report["status"] = "interrupted" if isinstance(exc, KeyboardInterrupt) else "failed"
            self.report["error"] = {
                "type": exc.__class__.__name__,
                "message": str(exc),
                "table": self.current_table_name,
            }
            raise
        finally:
            self.report["finished_at"] = _utcnow_iso()
            self.report["retry_events"] = self.retry_events
            self._persist_report()
            self._close_resources()

    def _resolve_selected_tables(self) -> list[str]:
        if self.config.tables:
            unknown_tables = [table for table in self.config.tables if table not in TABLE_SPECS_BY_NAME]
            if unknown_tables:
                raise ValueError(f"存在未知表名: {', '.join(unknown_tables)}")
            selected = [name for name in FIRST_PHASE_TABLE_NAMES if name in self.config.tables]
        else:
            selected = list(FIRST_PHASE_TABLE_NAMES)

        if self.config.resume_from_table:
            if self.config.resume_from_table not in selected:
                raise ValueError(
                    f"resume_from_table={self.config.resume_from_table} 不在本次迁移表范围内"
                )
            resume_index = selected.index(self.config.resume_from_table)
            selected = selected[resume_index:]

        if not selected:
            raise ValueError("没有可迁移的表")
        return selected

    def _prepare_target_runtime(self) -> None:
        target_exists = self.config.target_sqlite.exists()
        if self.config.resume_from_table:
            if not target_exists:
                raise RuntimeError(
                    "resume_from_table 只支持已存在的目标 SQLite，请先保留上一次成功的目标文件"
                )
        elif target_exists:
            raise RuntimeError(
                f"目标 SQLite 已存在: {self.config.target_sqlite}。按设计需要使用新文件，或改用 resume_from_table。"
            )

        self.config.target_sqlite.parent.mkdir(parents=True, exist_ok=True)
        self.target_app = self._build_target_app(self.config.target_sqlite)
        self.target_app_context = self.target_app.app_context()
        self.target_app_context.push()

        if not ini_app(self.target_app):
            raise RuntimeError("lite 目标库初始化失败")

        bootstrap_lite_database(self.target_app)
        self.target_engine = db.engines["snowball"]

    def _prepare_source_engine(self) -> None:
        source_options: dict[str, Any] = {
            "future": True,
            "pool_pre_ping": True,
            "pool_recycle": 600,
            "poolclass": NullPool,
        }

        parsed_url = make_url(self.config.source_url)
        if parsed_url.drivername.startswith("mysql+pymysql"):
            source_options["connect_args"] = {
                "connect_timeout": self.config.source_connect_timeout_seconds,
                "read_timeout": self.config.source_read_timeout_seconds,
                "write_timeout": self.config.source_write_timeout_seconds,
            }

        self.source_engine = create_engine(self.config.source_url, **source_options)
        self._execute_source_operation(
            "check source connection",
            lambda: self._execute_scalar(self.source_engine, text("SELECT 1")),
        )

    def _reflect_required_tables(self, selected_tables: list[str]) -> None:
        source_table_names = set(
            self._execute_source_operation(
                "list source tables",
                lambda: self._get_table_names(self.source_engine),
            )
        )
        target_table_names = set(self._get_table_names(self.target_engine))

        required_tables = set(selected_tables)
        for table_name in selected_tables:
            required_tables.update(
                relationship.parent_table
                for relationship in TABLE_SPECS_BY_NAME[table_name].relationships
            )

        missing_source_tables = sorted(required_tables - source_table_names)
        if missing_source_tables:
            raise RuntimeError(f"源库缺少表: {', '.join(missing_source_tables)}")

        missing_target_tables = sorted(required_tables - target_table_names)
        if missing_target_tables:
            raise RuntimeError(f"目标 SQLite 缺少表: {', '.join(missing_target_tables)}")

        for table_name in sorted(required_tables):
            self.source_tables[table_name] = self._execute_source_operation(
                f"reflect source table {table_name}",
                lambda table_name=table_name: Table(
                    table_name,
                    MetaData(),
                    autoload_with=self.source_engine,
                ),
                table_name=table_name,
            )
            self.target_tables[table_name] = Table(
                table_name,
                MetaData(),
                autoload_with=self.target_engine,
            )

    def _run_precheck(self, selected_tables: list[str]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []

        for table_name in selected_tables:
            self.current_table_name = table_name
            self.report["current_table"] = table_name
            source_table = self.source_tables[table_name]
            target_table = self.target_tables[table_name]
            source_column_names = list(source_table.c.keys())
            target_column_names = list(target_table.c.keys())
            missing_target_columns = [
                column for column in source_column_names if column not in target_column_names
            ]
            target_only_columns = [
                column for column in target_column_names if column not in source_column_names
            ]
            if missing_target_columns:
                raise RuntimeError(
                    f"{table_name} 在目标 SQLite 缺少列: {', '.join(missing_target_columns)}"
                )

            source_count = self._count_rows("source", source_table)
            target_count = self._count_rows("target", target_table)
            source_primary_key_summary = self._primary_key_summary("source", source_table)
            target_primary_key_summary = self._primary_key_summary("target", target_table)
            orphan_checks = self._run_orphan_checks("source", table_name)

            if any(check["orphan_count"] for check in orphan_checks):
                raise RuntimeError(f"{table_name} 在源库预检查发现孤儿引用")

            rows.append(
                {
                    "table": table_name,
                    "source_count": source_count,
                    "target_count": target_count,
                    "source_primary_key": source_primary_key_summary,
                    "target_primary_key": target_primary_key_summary,
                    "missing_target_columns": missing_target_columns,
                    "target_only_columns": target_only_columns,
                    "orphan_checks": orphan_checks,
                    "retry_count": self.table_retry_counts.get(table_name, 0),
                }
            )
            self.report["precheck"]["tables"] = list(rows)
            self._persist_report()

        return rows

    def _migrate_tables(self, selected_tables: list[str]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []

        for table_name in selected_tables:
            self.current_table_name = table_name
            self.report["current_table"] = table_name
            source_table = self.source_tables[table_name]
            target_table = self.target_tables[table_name]
            source_count = self._count_rows("source", source_table)

            if table_name == "system_settings":
                self._clear_target_reserved_system_settings(target_table)

            if self.config.truncate_target:
                self._truncate_target_table(target_table)

            existing_target_count = self._count_rows("target", target_table)
            if existing_target_count != 0:
                raise RuntimeError(
                    f"{table_name} 目标表已有 {existing_target_count} 条可迁移数据，请更换目标文件或使用 truncate_target"
                )

            migrated_row_count, batch_count, strategy = self._copy_table_data(
                table_name,
                source_table,
                target_table,
            )
            validation = self._validate_table_after_copy(table_name, source_count)

            rows.append(
                {
                    "table": table_name,
                    "source_count": source_count,
                    "migrated_row_count": migrated_row_count,
                    "batch_count": batch_count,
                    "pagination_strategy": strategy,
                    "validation": validation,
                    "retry_count": self.table_retry_counts.get(table_name, 0),
                }
            )
            self.report["migration"]["tables"] = list(rows)
            self._persist_report()

        return rows

    def _copy_table_data(
        self,
        table_name: str,
        source_table: Table,
        target_table: Table,
    ) -> tuple[int, int, str]:
        column_names = [column_name for column_name in target_table.c.keys() if column_name in source_table.c]
        batch_count = 0
        migrated_row_count = 0
        spec = TABLE_SPECS_BY_NAME[table_name]
        single_primary_key = len(spec.primary_key) == 1
        strategy = "keyset" if single_primary_key else "offset"
        last_primary_key_value = None
        offset = 0

        while True:
            rows = self._fetch_source_batch(
                source_table=source_table,
                spec=spec,
                column_names=column_names,
                last_primary_key_value=last_primary_key_value,
                offset=offset,
            )
            if not rows:
                break

            payload = [{column_name: row[column_name] for column_name in column_names} for row in rows]
            with self.target_engine.begin() as connection:
                connection.execute(target_table.insert(), payload)

            batch_count += 1
            migrated_row_count += len(payload)
            if single_primary_key:
                last_primary_key_value = payload[-1][spec.primary_key[0]]
            else:
                offset += len(payload)

        return migrated_row_count, batch_count, strategy

    def _validate_table_after_copy(self, table_name: str, expected_source_count: int) -> dict[str, Any]:
        target_table = self.target_tables[table_name]
        target_count = self._count_rows("target", target_table)
        if target_count != expected_source_count:
            raise RuntimeError(
                f"{table_name} 迁移后行数不一致: source={expected_source_count}, target={target_count}"
            )

        source_primary_key = self._primary_key_summary("source", self.source_tables[table_name])
        target_primary_key = self._primary_key_summary("target", target_table)
        if source_primary_key != target_primary_key:
            raise RuntimeError(f"{table_name} 主键范围不一致")

        orphan_checks = self._run_orphan_checks("target", table_name)
        if any(check["orphan_count"] for check in orphan_checks):
            raise RuntimeError(f"{table_name} 迁移后仍存在孤儿引用")

        return {
            "target_count": target_count,
            "source_primary_key": source_primary_key,
            "target_primary_key": target_primary_key,
            "orphan_checks": orphan_checks,
        }

    def _run_validation(self, selected_tables: list[str]) -> dict[str, Any]:
        sqlite_foreign_key_violations = self._run_sqlite_foreign_key_check()
        if sqlite_foreign_key_violations:
            raise RuntimeError("SQLite foreign_key_check 未通过")

        logical_orphan_summary = {
            table_name: self._run_orphan_checks("target", table_name)
            for table_name in selected_tables
        }
        if any(
            check["orphan_count"]
            for checks in logical_orphan_summary.values()
            for check in checks
        ):
            raise RuntimeError("迁移后逻辑孤儿校验未通过")

        return {
            "sqlite_foreign_key_check": sqlite_foreign_key_violations,
            "logical_orphan_checks": logical_orphan_summary,
        }

    def _refresh_runtime_version(self) -> None:
        success, payload = record_enum_version_to_sqlite(
            key=VersionKeyEnum.ENUM.value,
            logger=self.target_app.logger if self.target_app else None,
            merge=False,
        )
        if not success:
            raise RuntimeError("lite runtime version 写入失败")
        self.report["runtime_version"] = payload

    def _run_orphan_checks(self, side: str, table_name: str) -> list[dict[str, Any]]:
        spec = TABLE_SPECS_BY_NAME[table_name]
        child_table = self._get_table(side, table_name)
        rows: list[dict[str, Any]] = []

        for relationship in spec.relationships:
            parent_table = self._get_table(side, relationship.parent_table)
            condition = child_table.c[relationship.column] == parent_table.c[relationship.parent_column]
            where_clause = child_table.c[relationship.column].isnot(None)
            if relationship.predicate_factory is not None:
                where_clause = and_(where_clause, relationship.predicate_factory(child_table))

            statement = (
                select(func.count())
                .select_from(child_table.outerjoin(parent_table, condition))
                .where(where_clause)
                .where(parent_table.c[relationship.parent_column].is_(None))
            )
            orphan_count = self._execute_scalar_on_side(
                side,
                f"orphan check {table_name}.{relationship.column}",
                statement,
                table_name=table_name,
            )
            rows.append(
                {
                    "column": relationship.column,
                    "parent_table": relationship.parent_table,
                    "parent_column": relationship.parent_column,
                    "orphan_count": orphan_count,
                }
            )

        return rows

    def _run_sqlite_foreign_key_check(self) -> list[dict[str, Any]]:
        with self.target_engine.connect() as connection:
            result = connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall()

        return [
            {
                "table": row[0],
                "rowid": row[1],
                "parent_table": row[2],
                "foreign_key_index": row[3],
            }
            for row in result
        ]

    def _count_rows(self, side: str, table: Table) -> int:
        statement = select(func.count()).select_from(table)
        filter_clause = self._build_row_filter(table)
        if filter_clause is not None:
            statement = statement.where(filter_clause)
        return self._execute_scalar_on_side(
            side,
            f"count rows for {table.name}",
            statement,
            table_name=table.name,
        )

    def _primary_key_summary(self, side: str, table: Table) -> dict[str, Any]:
        spec = TABLE_SPECS_BY_NAME[table.name]
        filter_clause = self._build_row_filter(table)

        if len(spec.primary_key) == 1:
            primary_key_column = table.c[spec.primary_key[0]]
            statement = select(
                func.min(primary_key_column),
                func.max(primary_key_column),
            ).select_from(table)
            if filter_clause is not None:
                statement = statement.where(filter_clause)
            minimum, maximum = self._execute_row_on_side(
                side,
                f"primary key range for {table.name}",
                statement,
                table_name=table.name,
            )
            return {"type": "single", "min": minimum, "max": maximum}

        ordering_columns = [table.c[column_name] for column_name in spec.primary_key]
        first_statement = select(*ordering_columns).select_from(table).order_by(*ordering_columns).limit(1)
        last_statement = select(*ordering_columns).select_from(table).order_by(
            *[column.desc() for column in ordering_columns]
        ).limit(1)
        if filter_clause is not None:
            first_statement = first_statement.where(filter_clause)
            last_statement = last_statement.where(filter_clause)

        first_row = self._execute_mapping_row_on_side(
            side,
            f"first composite key for {table.name}",
            first_statement,
            table_name=table.name,
        )
        last_row = self._execute_mapping_row_on_side(
            side,
            f"last composite key for {table.name}",
            last_statement,
            table_name=table.name,
        )
        return {
            "type": "composite",
            "first": first_row,
            "last": last_row,
        }

    def _fetch_source_batch(
        self,
        *,
        source_table: Table,
        spec: TableSpec,
        column_names: list[str],
        last_primary_key_value: Any,
        offset: int,
    ) -> list[dict[str, Any]]:
        columns = [source_table.c[column_name] for column_name in column_names]
        statement = select(*columns).select_from(source_table)
        filter_clause = self._build_row_filter(source_table)
        if filter_clause is not None:
            statement = statement.where(filter_clause)

        if len(spec.primary_key) == 1:
            primary_key_column = source_table.c[spec.primary_key[0]]
            if last_primary_key_value is not None:
                statement = statement.where(primary_key_column > last_primary_key_value)
            statement = statement.order_by(primary_key_column)
        else:
            ordering_columns = [source_table.c[column_name] for column_name in spec.primary_key]
            statement = statement.order_by(*ordering_columns).offset(offset)

        statement = statement.limit(self.config.batch_size)
        return self._execute_source_operation(
            f"fetch batch for {source_table.name}",
            lambda: self._fetch_mappings(self.source_engine, statement),
            table_name=source_table.name,
        )

    def _truncate_target_table(self, table: Table) -> None:
        delete_statement = table.delete()
        filter_clause = self._build_row_filter(table)
        if filter_clause is not None and table.name != "system_settings":
            delete_statement = delete_statement.where(filter_clause)

        with self.target_engine.begin() as connection:
            connection.execute(delete_statement)

    def _clear_target_reserved_system_settings(self, table: Table) -> None:
        if table.name != "system_settings":
            return

        with self.target_engine.begin() as connection:
            connection.execute(
                table.delete().where(
                    or_(
                        table.c.key.in_(tuple(RESERVED_SYSTEM_SETTING_KEYS)),
                        table.c["group"].in_(tuple(RESERVED_SYSTEM_SETTING_GROUPS)),
                    )
                )
            )

    def _build_row_filter(self, table: Table):
        if table.name != "system_settings":
            return None

        key_condition = table.c.key.notin_(tuple(RESERVED_SYSTEM_SETTING_KEYS))
        group_column = table.c["group"]
        group_condition = or_(
            group_column.is_(None),
            group_column.notin_(tuple(RESERVED_SYSTEM_SETTING_GROUPS)),
        )
        return and_(key_condition, group_condition)

    def _execute_source_operation(
        self,
        label: str,
        operation: Callable[[], Any],
        *,
        table_name: str | None = None,
    ) -> Any:
        self._log_info(f"[source] start: {label}")

        def _on_retry(retry_index: int, delay_seconds: float, exc: BaseException) -> None:
            if self.source_engine is not None:
                self.source_engine.dispose()
            retry_table = table_name or "__global__"
            self.table_retry_counts[retry_table] = self.table_retry_counts.get(retry_table, 0) + 1
            self.retry_events.append(
                {
                    "table": table_name,
                    "label": label,
                    "retry_index": retry_index,
                    "delay_seconds": delay_seconds,
                    "error_type": exc.__class__.__name__,
                    "error_message": str(exc),
                }
            )
            self._log_warning(
                f"[source] retry {retry_index} for {label} after {delay_seconds}s: {exc.__class__.__name__}: {exc}"
            )

        result = execute_with_retries(
            label,
            operation,
            max_retries=self.config.max_retries,
            initial_delay_seconds=self.config.retry_delay_seconds,
            backoff_multiplier=self.config.retry_backoff,
            is_retryable=is_retryable_source_error,
            on_retry=_on_retry,
        )
        self._log_info(f"[source] done: {label}")
        return result

    def _execute_scalar_on_side(
        self,
        side: str,
        label: str,
        statement,
        *,
        table_name: str | None = None,
    ) -> int:
        result = self._execute_on_side(side, label, statement, table_name=table_name)
        return int(result)

    def _execute_row_on_side(
        self,
        side: str,
        label: str,
        statement,
        *,
        table_name: str | None = None,
    ) -> Any:
        return self._execute_on_side(side, label, statement, table_name=table_name, fetch="row")

    def _execute_mapping_row_on_side(
        self,
        side: str,
        label: str,
        statement,
        *,
        table_name: str | None = None,
    ) -> dict[str, Any] | None:
        return self._execute_on_side(
            side,
            label,
            statement,
            table_name=table_name,
            fetch="mapping_row",
        )

    def _execute_on_side(
        self,
        side: str,
        label: str,
        statement,
        *,
        table_name: str | None = None,
        fetch: str = "scalar",
    ) -> Any:
        engine = self.source_engine if side == "source" else self.target_engine
        if fetch == "scalar":
            runner = lambda: self._execute_scalar(engine, statement)
        elif fetch == "row":
            runner = lambda: self._execute_row(engine, statement)
        elif fetch == "mapping_row":
            runner = lambda: self._execute_mapping_row(engine, statement)
        else:
            raise ValueError(f"未知 fetch 类型: {fetch}")

        if side == "source":
            return self._execute_source_operation(label, runner, table_name=table_name)
        return runner()

    def _execute_scalar(self, engine: Engine, statement) -> Any:
        with engine.connect() as connection:
            return connection.execute(statement).scalar_one()

    def _execute_row(self, engine: Engine, statement) -> Any:
        with engine.connect() as connection:
            return connection.execute(statement).one_or_none()

    def _execute_mapping_row(self, engine: Engine, statement) -> dict[str, Any] | None:
        with engine.connect() as connection:
            row = connection.execute(statement).mappings().one_or_none()
        return dict(row) if row is not None else None

    def _fetch_mappings(self, engine: Engine, statement) -> list[dict[str, Any]]:
        with engine.connect() as connection:
            return [dict(row) for row in connection.execute(statement).mappings().all()]

    def _get_table_names(self, engine: Engine) -> list[str]:
        with engine.connect() as connection:
            if engine.dialect.name == "sqlite":
                rows = connection.exec_driver_sql(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
                return [row[0] for row in rows]

            rows = connection.execute(text("SHOW TABLES")).fetchall()
            return [row[0] for row in rows]

    def _get_table(self, side: str, table_name: str) -> Table:
        if side == "source":
            return self.source_tables[table_name]
        return self.target_tables[table_name]

    def _build_target_app(self, target_sqlite: Path) -> Flask:
        app = Flask("mysql-to-sqlite-business-migration")
        runtime_cache_dir = target_sqlite.parent / "lite_xalpha_cache"
        runtime_cache_sqlite = runtime_cache_dir / "lite_xalpha_cache.db"

        old_env = {
            "LITE_DB_PATH": os.environ.get("LITE_DB_PATH"),
            "LITE_XALPHA_CACHE_DIR": os.environ.get("LITE_XALPHA_CACHE_DIR"),
            "LITE_XALPHA_CACHE_BACKEND": os.environ.get("LITE_XALPHA_CACHE_BACKEND"),
            "LITE_XALPHA_CACHE_SQLITE_PATH": os.environ.get("LITE_XALPHA_CACHE_SQLITE_PATH"),
            "LITE_ENABLE_XALPHA_SQL_CACHE": os.environ.get("LITE_ENABLE_XALPHA_SQL_CACHE"),
        }
        os.environ["LITE_DB_PATH"] = str(target_sqlite)
        os.environ["LITE_XALPHA_CACHE_DIR"] = str(runtime_cache_dir)
        os.environ["LITE_XALPHA_CACHE_BACKEND"] = "sql"
        os.environ["LITE_XALPHA_CACHE_SQLITE_PATH"] = str(runtime_cache_sqlite)
        os.environ["LITE_ENABLE_XALPHA_SQL_CACHE"] = "true"

        try:
            app.config.from_object(settings.config["lite"])
            settings.apply_runtime_overrides(app, "lite")
        finally:
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        app.config["_config_name"] = "lite"
        app.config["_config_class_name"] = settings.config["lite"].__name__
        logger_initialize.init_logger(app)
        return app

    def _mask_source_url(self, source_url: str) -> str:
        return make_url(source_url).render_as_string(hide_password=True)

    def _log_info(self, message: str) -> None:
        if self.target_app is not None:
            self.target_app.logger.info(message)

    def _log_warning(self, message: str) -> None:
        if self.target_app is not None:
            self.target_app.logger.warning(message)

    def _persist_report(self) -> None:
        self.config.report_path.parent.mkdir(parents=True, exist_ok=True)
        self.config.report_path.write_text(
            json.dumps(self.report, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _close_resources(self) -> None:
        if self.target_app_context is not None:
            try:
                db.session.remove()
                for engine in db.engines.values():
                    engine.dispose()
            finally:
                self.target_app_context.pop()
                self.target_app_context = None

        if self.source_engine is not None:
            self.source_engine.dispose()
            self.source_engine = None
