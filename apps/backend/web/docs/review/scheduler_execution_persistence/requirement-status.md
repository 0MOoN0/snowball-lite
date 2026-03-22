# scheduler_execution_persistence requirement status

- source doc: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/task/scheduler_execution_persistence/requirement.md`
- current status: in_progress
- current round: 1
- current task: `02_task_classification`
- report root: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence`

## task status

| task_id | status | depends_on | summary |
| --- | --- | --- | --- |
| 01_runtime_core | completed | - | 运行时策略基座与 outbox 首个接入 |
| 02_task_classification | in_progress | 01_runtime_core | lite 主线任务策略归类与扩面 |
| 03_state_storage_optimization | pending | 01_runtime_core | 状态表与事件日志分层 |
| 04_persistence_api | pending | 02_task_classification | 策略覆盖持久化与后端接口 |
| 05_frontend_settings | pending | 04_persistence_api | 前端单任务策略设置 |

## files touched

- `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/scheduler/__init__.py`
- `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/webtest/lite/test_lite_notification_outbox.py`
- `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/webtest/scheduler/test_scheduler_listener.py`
- `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence/requirement-status.md`
- `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence/execution-plan.md`
- `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence/01_runtime_core/task-status.md`
- `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence/01_runtime_core/round-01-review.md`

## commands run

- `git status --short --branch`
- `git diff -- AGENTS.md`
- `git diff -- apps/backend/web/docs/task/scheduler_execution_persistence_policy.md apps/backend/web/docs/task/scheduler_execution_persistence_requirement.md`
- `git commit -m "docs(task): 重组 scheduler 执行持久化任务文档"`
- `git worktree add -b codex/scheduler-execution-persistence ../snowball-lite-codex-scheduler-execution-persistence dev`
- `rg --files ...`
- `sed -n ...`
- `pytest apps/backend/web/webtest/lite/test_lite_notification_outbox.py -q`
- `pytest apps/backend/web/webtest/scheduler/test_scheduler_listener.py -q`
- `pytest apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py -q`

## latest blockers

- Task 2 要先把 lite 主线任务归类结果落清楚，再决定是否真的要扩 `signal_only` / `error_only`，不能为了“扩面”硬切策略。
- Task 3 之后的 `/scheduler/jobs`、手动触发防重和策略展示仍会依赖旧日志表口径，状态表设计时必须保留最近提交时间语义。

## next action

- 派新的 implementer 做 `02_task_classification`：固化 lite 主线任务归类表，并只对已有明确信号的任务做最小扩面。
- Task 2 完成后再做独立 review，随后进入状态表拆分任务。
