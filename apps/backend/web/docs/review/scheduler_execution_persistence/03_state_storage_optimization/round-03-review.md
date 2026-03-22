# Staged Code Review Report

- Generated At: `2026-03-22T22:50:13+08:00`
- Reviewer: `Codex`
- Repo Root: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence`
- HEAD: `da1c1299729804975c223a6ae7d380558daea2fd`
- Snapshot Source: `/private/tmp/codex-staged-review-1774190887/snapshot.json`

## Scope

- Staged file count: `15`
- Added lines: `714`
- Removed lines: `128`
- Diff artifact: `git diff --cached`

### Staged Files

- `apps/backend/web/lite_bootstrap.py`
- `apps/backend/web/migrations/dev/versions/eaacb86c18ae_add_scheduler_job_state_table.py`
- `apps/backend/web/migrations/lite/versions/lite_add_scheduler_job_state_table.py`
- `apps/backend/web/migrations/stg/versions/f3be15f09486_add_scheduler_job_state_table.py`
- `apps/backend/web/migrations/test/versions/62a7afd16eeb_add_scheduler_job_state_table.py`
- `apps/backend/web/models/registry.py`
- `apps/backend/web/models/scheduler/scheduler_job_state.py`
- `apps/backend/web/routers/scheduler/scheduler_job_list_routers.py`
- `apps/backend/web/routers/scheduler/scheduler_job_operation_routers.py`
- `apps/backend/web/scheduler/__init__.py`
- `apps/backend/web/services/scheduler/scheduler_service.py`
- `apps/backend/web/webtest/lite/test_lite_bootstrap_review.py`
- `apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py`
- `apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py`
- `apps/backend/web/webtest/routers/scheduler/test_scheduler_job_operation_routers.py`

## Review Protocol (TDD + Evidence)

1. 先复核上一轮 findings 是否真的修完，再看新的 staged diff 有没有引入新问题。
2. 业务代码和生产代码只读，不做修复性改动。
3. 证据测试放在仓库自己的 `test/` 路径里，命令和输出都要可复现。
4. 结论必须能回溯到具体文件行和具体命令输出。
5. 如果没有 findings，也要写出回归命令和残余风险。

## Fix Verification

- Previous Findings Source: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence/03_state_storage_optimization/round-02-review.md`
- Verification Scope: 复核上一轮的两个问题，分别是 `/scheduler/jobs` fallback 取数完整性和 listener 记录 finished/error 时间是否使用实际事件时间。
- Verification Commands:
  - `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense`
  - `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_records_actual_finished_time_for_error_event`
- Result: passed
- Notes: 上一轮的两个复现用例都已通过，说明密集日志 fallback 和错误事件时间戳问题没有在当前 staged diff 里复现出来。

## New Risk Scan

- Scan Scope: 仅看当前 staged diff，不看未 staged 内容。
- Risk Focus Areas: `job_state` 写入同步、`/scheduler/jobs` 读取合并、手动触发防重、lite bootstrap 与 migration 落表。
- Commands:
  - `python3 -m py_compile apps/backend/web/migrations/lite/versions/lite_add_scheduler_job_state_table.py apps/backend/web/migrations/dev/versions/eaacb86c18ae_add_scheduler_job_state_table.py apps/backend/web/migrations/stg/versions/f3be15f09486_add_scheduler_job_state_table.py apps/backend/web/migrations/test/versions/62a7afd16eeb_add_scheduler_job_state_table.py apps/backend/web/models/scheduler/scheduler_job_state.py apps/backend/web/services/scheduler/scheduler_service.py apps/backend/web/routers/scheduler/scheduler_job_list_routers.py apps/backend/web/routers/scheduler/scheduler_job_operation_routers.py apps/backend/web/lite_bootstrap.py apps/backend/web/scheduler/__init__.py apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py apps/backend/web/webtest/routers/scheduler/test_scheduler_job_operation_routers.py`
  - `pytest -q apps/backend/web/webtest/lite/test_lite_bootstrap_review.py::test_lite_bootstrap_survives_blocked_mysql_and_optional_infra_packages apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py::test_lite_bootstrap_stage5_builds_core_schema apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py::test_lite_bootstrap_upgrades_existing_stage3_baseline_to_current_head`
  - `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_records_actual_finished_time_for_error_event apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_keeps_job_state_for_signal_only_empty_poll apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_jobs_route_prefers_job_state_over_event_log apps/backend/web/webtest/routers/scheduler/test_scheduler_job_operation_routers.py::TestSchedulerJobRunRouters::test_put_method_rejects_recent_submitted_job_state`
- Result: no findings
- New Findings: none
- Residual Risk: 这次回归覆盖了 lite bootstrap、schema expansion、listener、service 和 router 的关键路径；仍然没有做“已存在生产库上完整 Alembic 回放”的实机演练，所以迁移在存量库上的边界只剩静态检查和 bootstrap 级验证。

## Findings Summary

No findings.

## No Findings Evidence

- Command Set:
  - `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense`
  - `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_records_actual_finished_time_for_error_event`
  - `python3 -m py_compile apps/backend/web/migrations/lite/versions/lite_add_scheduler_job_state_table.py apps/backend/web/migrations/dev/versions/eaacb86c18ae_add_scheduler_job_state_table.py apps/backend/web/migrations/stg/versions/f3be15f09486_add_scheduler_job_state_table.py apps/backend/web/migrations/test/versions/62a7afd16eeb_add_scheduler_job_state_table.py apps/backend/web/models/scheduler/scheduler_job_state.py apps/backend/web/services/scheduler/scheduler_service.py apps/backend/web/routers/scheduler/scheduler_job_list_routers.py apps/backend/web/routers/scheduler/scheduler_job_operation_routers.py apps/backend/web/lite_bootstrap.py apps/backend/web/scheduler/__init__.py apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py apps/backend/web/webtest/routers/scheduler/test_scheduler_job_operation_routers.py`
  - `pytest -q apps/backend/web/webtest/lite/test_lite_bootstrap_review.py::test_lite_bootstrap_survives_blocked_mysql_and_optional_infra_packages apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py::test_lite_bootstrap_stage5_builds_core_schema apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py::test_lite_bootstrap_upgrades_existing_stage3_baseline_to_current_head`
  - `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_records_actual_finished_time_for_error_event apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_keeps_job_state_for_signal_only_empty_poll apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_jobs_route_prefers_job_state_over_event_log apps/backend/web/webtest/routers/scheduler/test_scheduler_job_operation_routers.py::TestSchedulerJobRunRouters::test_put_method_rejects_recent_submitted_job_state`
- Evidence: `py_compile` 通过；lite bootstrap / schema expansion 的回归通过；scheduler 相关 5 个定点测试也通过，未看到失败断言。
- Residual Risk: 仍建议后续在有真实存量库的环境里补一次 Alembic 回放验证，但这不影响当前 staged diff 的 no-findings 结论。

## Evidence Appendix

```text
pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense => passed
pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_records_actual_finished_time_for_error_event => passed
python3 -m py_compile apps/backend/web/migrations/lite/versions/lite_add_scheduler_job_state_table.py apps/backend/web/migrations/dev/versions/eaacb86c18ae_add_scheduler_job_state_table.py apps/backend/web/migrations/stg/versions/f3be15f09486_add_scheduler_job_state_table.py apps/backend/web/migrations/test/versions/62a7afd16eeb_add_scheduler_job_state_table.py apps/backend/web/models/scheduler/scheduler_job_state.py apps/backend/web/services/scheduler/scheduler_service.py apps/backend/web/routers/scheduler/scheduler_job_list_routers.py apps/backend/web/routers/scheduler/scheduler_job_operation_routers.py apps/backend/web/lite_bootstrap.py apps/backend/web/scheduler/__init__.py apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py apps/backend/web/webtest/routers/scheduler/test_scheduler_job_operation_routers.py => success
pytest -q apps/backend/web/webtest/lite/test_lite_bootstrap_review.py::test_lite_bootstrap_survives_blocked_mysql_and_optional_infra_packages apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py::test_lite_bootstrap_stage5_builds_core_schema apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py::test_lite_bootstrap_upgrades_existing_stage3_baseline_to_current_head => passed
pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_records_actual_finished_time_for_error_event apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_keeps_job_state_for_signal_only_empty_poll apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_jobs_route_prefers_job_state_over_event_log apps/backend/web/webtest/routers/scheduler/test_scheduler_job_operation_routers.py::TestSchedulerJobRunRouters::test_put_method_rejects_recent_submitted_job_state => passed
```
