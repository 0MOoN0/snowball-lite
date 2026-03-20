from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from web.services.migration import (
    FIRST_PHASE_TABLE_NAMES,
    MigrationConfig,
    MysqlToSqliteBusinessMigrationService,
)


def _parse_tables(raw_values: list[str] | None) -> tuple[str, ...] | None:
    if not raw_values:
        return None

    tables: list[str] = []
    for raw_value in raw_values:
        tables.extend(
            table_name.strip()
            for table_name in raw_value.split(",")
            if table_name.strip()
        )
    return tuple(dict.fromkeys(tables)) or None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="将业务库数据按 lite baseline 迁移到新的 SQLite 文件",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--source-url",
        required=True,
        help="源库 SQLAlchemy URL，stg 库请显式传 mysql+pymysql://.../snowball_stg",
    )
    parser.add_argument(
        "--target-sqlite",
        default=os.environ.get("LITE_DB_PATH"),
        help="目标 SQLite 文件路径；未传时回退到 LITE_DB_PATH",
    )
    parser.add_argument(
        "--tables",
        action="append",
        help="仅迁指定表，支持重复传参或逗号分隔",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="单批搬运行数；单主键表使用 keyset，复合主键表退回 offset 分页",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只做预检查并输出报告，不实际搬运数据",
    )
    parser.add_argument(
        "--resume-from-table",
        help="从指定表开始继续，要求目标 SQLite 已存在",
        choices=FIRST_PHASE_TABLE_NAMES,
    )
    parser.add_argument(
        "--truncate-target",
        action="store_true",
        help="迁表前先清空目标表中的可迁移数据",
    )
    parser.add_argument(
        "--report-path",
        required=True,
        help="迁移报告输出路径，推荐使用 .json",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=5,
        help="源库重试次数，主要用于远程 MySQL 网络抖动",
    )
    parser.add_argument(
        "--retry-delay-seconds",
        type=float,
        default=2.0,
        help="首次重试等待秒数",
    )
    parser.add_argument(
        "--retry-backoff",
        type=float,
        default=1.5,
        help="每次重试的退避倍率",
    )
    parser.add_argument(
        "--source-connect-timeout-seconds",
        type=int,
        default=5,
        help="源库连接超时秒数，网络不稳时建议保持较小值配合重试",
    )
    parser.add_argument(
        "--source-read-timeout-seconds",
        type=int,
        default=10,
        help="源库读取超时秒数，避免单次失败卡太久",
    )
    parser.add_argument(
        "--source-write-timeout-seconds",
        type=int,
        default=10,
        help="源库写入超时秒数，虽然 dry-run 不写源库，这里仍保持对称配置",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.target_sqlite:
        parser.error("必须传 --target-sqlite，或者在环境变量里提供 LITE_DB_PATH")

    config = MigrationConfig(
        source_url=args.source_url,
        target_sqlite=Path(args.target_sqlite),
        report_path=Path(args.report_path),
        tables=_parse_tables(args.tables),
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        resume_from_table=args.resume_from_table,
        truncate_target=args.truncate_target,
        max_retries=args.max_retries,
        retry_delay_seconds=args.retry_delay_seconds,
        retry_backoff=args.retry_backoff,
        source_connect_timeout_seconds=args.source_connect_timeout_seconds,
        source_read_timeout_seconds=args.source_read_timeout_seconds,
        source_write_timeout_seconds=args.source_write_timeout_seconds,
    )

    service = MysqlToSqliteBusinessMigrationService(config)
    try:
        report = service.run()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        print(f"report: {config.report_path}", file=sys.stderr)
        return 1

    summary = {
        "status": report["status"],
        "report_path": str(config.report_path),
        "table_count": len(report.get("table_order", [])),
        "retry_events": len(report.get("retry_events", [])),
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
