# Staged Code Review Report

- Generated At: `2026-03-22T22:37:09+08:00`
- Reviewer: `Codex`
- Repo Root: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence`
- HEAD: `da1c1299729804975c223a6ae7d380558daea2fd`
- Snapshot Source: `/private/tmp/codex-staged-review-1774190225/snapshot.json`

## Scope

- Staged file count: `15`
- Added lines: `662`
- Removed lines: `127`
- Diff artifact: `/private/tmp/codex-staged-review-1774190225/staged_diff.patch`

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

1. 写出会失败的测试，再确认 defect。
2. 只把业务代码和生产代码当只读对象，review 期间不修实现。
3. 证据测试只放在仓库自己的 `test/` 路径里。
4. 记录精确的命令和失败输出。
5. 每条 finding 都要对应具体文件行号和一个可复现的测试。
6. 找不到 finding 时，也要给出回归命令和剩余风险。
7. 这次 review 只看 staged diff，不看未 staged 的内容。

## Fix Verification

- Previous Findings Source: `round-01-review.md` had no findings to verify.
- Verification Scope: not applicable.
- Verification Commands:
  - `python3 -m py_compile apps/backend/web/migrations/lite/versions/lite_add_scheduler_job_state_table.py apps/backend/web/migrations/dev/versions/eaacb86c18ae_add_scheduler_job_state_table.py apps/backend/web/migrations/stg/versions/f3be15f09486_add_scheduler_job_state_table.py apps/backend/web/migrations/test/versions/62a7afd16eeb_add_scheduler_job_state_table.py apps/backend/web/models/scheduler/scheduler_job_state.py apps/backend/web/services/scheduler/scheduler_service.py apps/backend/web/routers/scheduler/scheduler_job_list_routers.py apps/backend/web/routers/scheduler/scheduler_job_operation_routers.py apps/backend/web/lite_bootstrap.py apps/backend/web/scheduler/__init__.py apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py apps/backend/web/webtest/routers/scheduler/test_scheduler_job_operation_routers.py`
- Result: passed.
- Notes: no prior defect was available for fix verification in this round.

## New Risk Scan

- Scan Scope: staged Task 3 diff only.
- Risk Focus Areas: job-state read path, state sync timestamps, and listener persistence behavior.
- Commands:
  - `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense`
  - `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_records_actual_finished_time_for_error_event`
  - `python3 -m py_compile apps/backend/web/migrations/lite/versions/lite_add_scheduler_job_state_table.py apps/backend/web/migrations/dev/versions/eaacb86c18ae_add_scheduler_job_state_table.py apps/backend/web/migrations/stg/versions/f3be15f09486_add_scheduler_job_state_table.py apps/backend/web/migrations/test/versions/62a7afd16eeb_add_scheduler_job_state_table.py apps/backend/web/models/scheduler/scheduler_job_state.py apps/backend/web/services/scheduler/scheduler_service.py apps/backend/web/routers/scheduler/scheduler_job_list_routers.py apps/backend/web/routers/scheduler/scheduler_job_operation_routers.py apps/backend/web/lite_bootstrap.py apps/backend/web/scheduler/__init__.py apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py apps/backend/web/webtest/routers/scheduler/test_scheduler_job_operation_routers.py`
- Result: 2 findings.
- New Findings:
  - `F-001`: dense log histories can drop requested jobs from the `/scheduler/jobs` fallback log query.
  - `F-002`: `last_finished_time` and `last_error_time` are written from the scheduled run time instead of the actual event time.
- Residual Risk: the new state table path is covered, but the fallback log query still depends on historical-log shape and the migration path has only been exercised through lite bootstrap, not a live already-populated production-like Alembic replay.

## Findings Summary

| ID | Severity | File:Line | Finding | Risk | Test Before Fix | Evidence Command | Recommendation | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F-001 | medium | `apps/backend/web/services/scheduler/scheduler_service.py:67-77` | `get_latest_job_logs_by_ids()` caps the history scan with `limit(max(len(job_ids) * 5, 100))`, so dense histories can silently drop some requested jobs and `/scheduler/jobs` no longer has a complete fallback. | `medium` | `apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense` | `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense` | Remove the arbitrary cap and fetch the latest log per job deterministically, or only query logs for jobs that still have no `job_state` row. | Open |
| F-002 | medium | `apps/backend/web/scheduler/__init__.py:415-425` | `last_finished_time` and `last_error_time` are filled from `scheduler_run_time`, so the new state table stores the planned run time instead of the actual completion/error time. | `medium` | `apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_records_actual_finished_time_for_error_event` | `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_records_actual_finished_time_for_error_event` | Use the listener's current timestamp for finish/error times and keep `scheduler_run_time` only for the scheduled time. | Open |

## Finding Details

### Finding F-001
- Severity: medium
- File: `apps/backend/web/services/scheduler/scheduler_service.py:67-77`
- Hypothesis: the fallback log query should return the newest row for every requested `job_id`, because `/scheduler/jobs` still needs it when a state row is missing.
- Test Added Before Fix: `apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py` (test name: `test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense`)
- Test Command: `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense`
- Failing Evidence:
  - The test creates 30 jobs with 10 log rows each, then asks the service for the latest log for all 30 jobs.
  - The assertion fails because only a subset of job IDs comes back from the capped subquery.
- Passing Evidence: `Not Applicable`
- Root Cause: the query orders the whole history, applies a fixed limit, then groups by `job_id`. Once the history is dense enough, some requested jobs never make it into the limited subquery.
- Recommendation: replace the capped subquery with a deterministic per-job latest-row query, or skip the log query entirely for jobs that already have a `job_state` row.
- Status: Open

```text
E       AssertionError: assert {'dense-job-1...-job-20', ...} == {'dense-job-0...-job-13', ...}
E         Extra items in the right set:
E         'dense-job-13'
E         'dense-job-3'
E         'dense-job-12'
E         'dense-job-1'
E         'dense-job-14'...
```

### Finding F-002
- Severity: medium
- File: `apps/backend/web/scheduler/__init__.py:415-425`
- Hypothesis: the state table should record when execution actually finished or errored, not the scheduled run time.
- Test Added Before Fix: `apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py` (test name: `test_lite_scheduler_listener_records_actual_finished_time_for_error_event`)
- Test Command: `pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_records_actual_finished_time_for_error_event`
- Failing Evidence:
  - The test freezes `datetime.now()` to `2026-03-22 18:00:00` and sends an error event whose scheduled run time is `2026-03-22 16:01:44`.
  - The stored `last_finished_time` and `last_error_time` still come back as `2026-03-22 16:01:44`.
- Passing Evidence: `Not Applicable`
- Root Cause: `_sync_job_state()` writes both fields from `scheduler_run_time`, so it persists the planned run time instead of the actual event time.
- Recommendation: use the listener's current timestamp for completion and error timestamps, and keep `last_scheduler_run_time` for the planned execution time only.
- Status: Open

```text
E           assert datetime.datetime(2026, 3, 22, 16, 1, 44) == datetime.datetime(2026, 3, 22, 18, 0)
E            +  where datetime.datetime(2026, 3, 22, 16, 1, 44) = <SchedulerJobState demo-job-finished-time>.last_finished_time
```

## Evidence Appendix

```text
python3 -m py_compile ... => success
pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense => failed with AssertionError showing missing job IDs
pytest -q apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py::test_lite_scheduler_listener_records_actual_finished_time_for_error_event => failed with AssertionError showing stored finished time equals scheduled run time
```
