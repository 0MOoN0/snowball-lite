# 后端目录收口与 monorepo 预留（归档）

## 归档状态

- 状态：已完成
- 原任务文档：`/Users/leon/projects/snowball-lite/web/docs/task/backend_workspace_consolidation_design.md`
- 对应状态：`/Users/leon/projects/snowball-lite/web/docs/review/backend_workspace_consolidation_design/task-status.md`
- 对应评审：`/Users/leon/projects/snowball-lite/web/docs/review/backend_workspace_consolidation_design/round-01-review.md`
- 对应提交：`cd0efb7`

## 结论

- 这次完成的不是把仓库直接改成完整 monorepo。
- 完成的是第一阶段 backend workspace 收口：把散落在仓库根目录的后端附属资产收回到 `web/` 周边，并统一 backend 路径口径。
- `web` 和 `xalpha` 的边界继续保留，真正的 `/apps/backend`、`/apps/frontend`、`/packages/xalpha` 物理重排还没开始。

## 实际落地范围

- 新增统一路径工具 `web/common/utils/backend_paths.py`
- 把 lite 默认 SQLite 和 xalpha cache 路径从 `cwd` 切到 backend workspace 约定路径
- 把 migration 目录统一收口到 `web/migrations/lite/`、`web/migrations/dev/`、`web/migrations/stg/`、`web/migrations/test/`
- 把后端迁移脚本收口到 `web/scripts/`
- 把开发初始化 SQL 收口到 `web/dev_support/db/dev/init.sql`
- 把明确属于 lite/backend 的测试收口到 `web/webtest/lite/`
- 同步更新 README 和 backend 相关说明文档

## 明确保留边界

- `xalpha/` 继续作为独立下层能力库
- `extends/` 这次没有并入 backend workspace
- 根目录 mixed/xalpha 测试这次没有整体迁移

## 验收结果

- `python -m py_compile web/common/utils/backend_paths.py web/settings.py web/lite_bootstrap.py web/models/__init__.py web/scripts/mysql_to_sqlite_lite_migration.py web/webtest/lite_runtime_fixtures.py web/webtest/lite/conftest.py web/webtest/lite/test_backend_workspace_paths.py web/webtest/lite/test_lite_bootstrap_review.py web/webtest/lite/test_lite_stage4_query_api_matrix.py tests/conftest.py`
- `python web/scripts/mysql_to_sqlite_lite_migration.py --help`
- `pytest web/webtest/lite web/webtest/stage3/test_task01_sqlite_fixture_bridge.py web/webtest/stage3/test_task04_lite_migration_baseline.py tests/test_lite_databox_stage4_coverage.py tests/test_xalpha_databox_compat.py -q`
- 结果：`50 passed, 1 skipped`

## 边界说明

- 这份归档只说明第一阶段 backend workspace 收口已经完成。
- 不等于 lite stage 4 已经启动。
- 也不等于整个仓库已经完成 monorepo 物理改造。

## 后续如果继续推进

1. 清理仓库外部脚本或 CI 对旧根目录路径的引用。
2. 单独拆第二阶段 monorepo 物理重排任务。
