# 02_task_classification task status

- source doc: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/task/scheduler_execution_persistence/02_task_classification.md`
- current status: completed
- current round: 2
- report root: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence/02_task_classification`

## classification table

| job_id | default_policy | switchable | reason |
| --- | --- | --- | --- |
| `AsyncTaskScheduler.consume_notification_outbox` | `signal_only` | `yes` | `stats.claimed` 可以稳定代表是否真的处理了业务信号，空轮询不应写成功日志 |
| `notice_scheduler.cb_subscribe_today` | `full` | `no` | 成功与否依赖发行列表和通知发送链路，当前没有结构化业务信号 |
| `notice_scheduler.cb_subscribe_tomorrow` | `full` | `no` | 成功与否依赖发行列表和通知发送链路，当前没有结构化业务信号 |
| `notice_scheduler.daily_report` | `full` | `no` | 报告任务是聚合输出，当前只具备日志语义，没有稳定可测的业务信号 |
| `DataboxTestScheduler.test_databox_get_rt` | `full` | `no` | 成功只记日志，失败才发通知；还没有足够证据把它安全收口成 `error_only` |
| `analysis_scheduler.to_analysis_all_transaction` | `full` | `no` | 分析任务只写过程日志，没有稳定返回值供 listener 判断信号 |
| `analysis_scheduler.analysis_all_the_time` | `full` | `no` | 一次性全量分析更适合保留完整轨迹，当前没有收口依据 |
| `AssetScheduler.update_asset_holding` | `full` | `no` | 任务内部有处理数量日志，但没有稳定返回值供 listener 判断信号 |
| `AssetScheduler.update_fund_daily_data` | `full` | `no` | 任务内部有新增记录数日志，但没有稳定返回值供 listener 判断信号 |
| `AssetScheduler.update_stock_asset` | `full` | `no` | 任务内部有新增股票代码数日志，但没有稳定返回值供 listener 判断信号 |
| `AssetScheduler.monitor_grid_type_detail` | `full` | `no` | 监控任务会产生命中/未命中变化，但当前不返回可测试的结构化结果 |
| `GridTypeScheduler.grid_type_trade_analysis` | `full` | `no` | 分析任务只写日志，没有结构化成功信号 |
| `GridStrategyScheduler.grid_strategy_trade_analysis` | `full` | `no` | 分析任务只写日志，没有结构化成功信号 |
| `AssetScheduler.complement_asset_data` | `full` | `no` | 补全任务只写日志，没有结构化成功信号 |

## files touched

- `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/scheduler/__init__.py`
- `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/webtest/scheduler/test_scheduler_listener.py`
- `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence/02_task_classification/task-status.md`
- `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence/02_task_classification/round-01-review.md`

## commands run

- `sed -n '1,220p' apps/backend/web/docs/task/scheduler_execution_persistence/02_task_classification.md`
- `sed -n '1,260p' apps/backend/web/scheduler/__init__.py`
- `sed -n '1,220p' apps/backend/web/scheduler/async_task_scheduler.py`
- `sed -n '1,220p' apps/backend/web/scheduler/notice_scheduler.py`
- `sed -n '1,260p' apps/backend/web/scheduler/analysis_scheduler.py`
- `sed -n '1,260p' apps/backend/web/scheduler/databox_test_scheduler.py`
- `sed -n '1,260p' apps/backend/web/scheduler/asset_scheduler.py`
- `rg -n "consume_notification_outbox|cb_subscribe_today|cb_subscribe_tomorrow|daily_report|test_databox_get_rt|to_analysis_all_transaction|analysis_all_the_time|update_asset_holding|update_fund_daily_data|update_stock_asset|monitor_grid_type_detail|grid_type_trade_analysis|grid_strategy_trade_analysis|complement_asset_data" apps/backend/web/webtest apps/backend/web/scheduler -g '*.py'`
- `pytest apps/backend/web/webtest/scheduler/test_scheduler_listener.py -q`
- `pytest apps/backend/web/webtest/lite/test_lite_notification_outbox.py -q`
- `pytest apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py -q`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/capture_staged_snapshot.py --output-dir /private/tmp/codex-staged-review-1774188582`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/create_review_report.py --snapshot /private/tmp/codex-staged-review-1774188582/snapshot.json --output /Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence/02_task_classification/round-01-review.md`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/validate_review_report.py --report /Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence/02_task_classification/round-01-review.md`

## latest blockers

- 没有功能性 blocker。
- 当前任务只做分类目录和最小复用结构，不再扩大成更多运行时策略切换，避免把未结构化的任务硬切成 `signal_only` / `error_only`。

## next action

- Task 2 已完成，进入 Task 3：`03_state_storage_optimization`。
