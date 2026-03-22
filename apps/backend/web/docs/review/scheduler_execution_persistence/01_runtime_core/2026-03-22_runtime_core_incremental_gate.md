# 01_runtime_core incremental gate

- validated scope: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/scheduler/__init__.py`, `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/webtest/lite/test_lite_notification_outbox.py`, `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py`, `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/webtest/scheduler/test_scheduler_listener.py`
- design doc consulted: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/task/scheduler_execution_persistence/01_runtime_core.md`
- report type: incremental only
- minimal code generation used: no

## commands run

- `pytest apps/backend/web/webtest/scheduler/test_scheduler_listener.py -q`
- `pytest apps/backend/web/webtest/lite/test_lite_notification_outbox.py -q`
- `pytest apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py -q`
- `pytest apps/backend/web/webtest/lite/test_lite_notification_outbox.py -q`  # rerun after splitting SUBMITTED handling
- `pytest apps/backend/web/webtest/scheduler/test_scheduler_listener.py -q`
- `pytest apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py -q`

## result

- result label: `incremental-pass-only`

## residual risks

- `signal_only` 目前只覆盖 `AsyncTaskScheduler.consume_notification_outbox`，后续如果再加别的高频任务，需要补各自的 signal 判定。
- 常规调度和手动触发已经分流，`signal_only` 常规执行在 `claimed=0` 时不会留下任何日志；后续若要扩展别的任务，仍要单独确认它们是否也应跳过 `SUBMITTED`。
- 当前验证覆盖了 listener 和 lite 集成面，没有做仓库级回归，这是按 incremental gate 的范围刻意保留给后续任务的。
