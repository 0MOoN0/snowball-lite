# 轻量版第六阶段规划（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 6 任务目录（原 `web/docs/task/lite_stage6/` 已清理）
- 当前状态：已完成
- 阶段结论：lite 主线已经完成“脱离 MySQL server”的阶段 6 收口，可以按 SQLite 主线运行

## 本阶段实际结果

- lite 启动、bootstrap、schema 初始化已经在零 MySQL 口径下跑通
- 资产、记录、分析、查询、DataBox 和 xalpha 这批 lite 主线能力已经在纯 SQLite 环境下通过回归
- lite 专用入口已经补齐：`web.lite_application`、`web/gunicorn_lite.config.py`、VS Code 本地启动项、`uv` 启动链路
- lite 下的 `/api/enums/versions` 已改成 SQLite 版本源，不再依赖 Redis
- Gunicorn 下的 lite bootstrap 已补齐幂等保护，不会因为重复 upgrade 把已有 SQLite 表再建一遍

## 本阶段归档文档

- `00_stage6_overview.md`
- `01_zero_mysql_startup_and_bootstrap_validation.md`
- `02_zero_mysql_core_business_validation.md`
- `03_zero_mysql_blocker_cleanup.md`
- `04_stage6_final_review_and_rereview.md`
- `05_stage6_acceptance_and_decision.md`

## 本阶段固定验收结果

- 启动 / 初始化回归：
  `python -m pytest tests/test_lite_bootstrap_review.py tests/test_lite_bootstrap_fixture_path.py tests/test_lite_sqlite_minimal_path.py tests/test_lite_stage5_schema_expansion.py web/webtest/stage3/test_task01_sqlite_fixture_bridge.py web/webtest/stage3/test_task04_lite_migration_baseline.py -q`
  结果：`12 passed, 1 warning`
- 核心业务回归：
  `python -m pytest web/webtest/stage4/test_task01_asset_management_sqlite.py web/webtest/stage4/test_task02_record_management_sqlite.py web/webtest/stage4/test_task03_analysis_capability_sqlite.py -q`
  结果：`5 passed, 30 warnings`
- 查询 / smoke / DataBox / xalpha / runtime cleanup 回归：
  `python -m pytest tests/test_lite_smoke_validation_and_decision.py tests/test_lite_stage4_query_api_matrix.py tests/test_lite_databox_stage4_coverage.py tests/test_xalpha_databox_compat.py web/webtest/stage3/test_task03_runtime_mysql_specific_sql_cleanup.py -q`
  结果：`24 passed, 120 warnings`
- lite 运行时边界回归：
  `python -m pytest tests/test_lite_runtime_dependency_boundary.py -q`
  结果：`2 passed, 1 warning`
- lite Gunicorn 配置检查：
  `python -m gunicorn.app.wsgiapp --check-config -c web/gunicorn_lite.config.py web.lite_application:app`
  在 lite 环境变量下通过

## 保留边界

- 非 lite 的 `dev/stg/test/prod` 配置仍然保留 MySQL 兼容路径
- `web/webtest` 里历史 MySQL 夹具和旧基类还在，但它们不再作为 lite 阶段结论的阻断项
- lite 仍然默认关闭 Redis、scheduler、task queue、profiler，这些能力不是当前主线保证范围
