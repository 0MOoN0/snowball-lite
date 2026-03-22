# scheduler_execution_persistence execution plan

- requirement doc: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/task/scheduler_execution_persistence/requirement.md`
- artifact root: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/review/scheduler_execution_persistence`
- orchestration mode: requirement
- execution policy: 顺序实现，允许并行做只读分析，不允许并行改共享 scheduler 写路径

## task lanes

| task_id | task_type | preconditions | deliverables | depends_on | write_scope | test_scope | can_analyze_with | can_implement_with | cannot_run_with | review_after | done_when |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01_runtime_core | runtime + tests | requirement 已确认，listener/outbox 现状已摸清 | 策略注册表、listener 落库判定、outbox `signal_only` 接入、回归测试 | - | `apps/backend/web/scheduler/__init__.py`, `apps/backend/web/scheduler/async_task_scheduler.py`, `apps/backend/web/webtest/lite/*`, `apps/backend/web/webtest/scheduler/*` | lite scheduler、listener、outbox | 02,03,04,05 | none | 02,03,04,05 | round-01 | 空轮询不写成功日志，异常和手动触发不回归 |
| 02_task_classification | runtime + docs + tests | 01 已提供策略框架 | lite 主线任务默认策略归类、非 outbox 任务接入、归类说明和测试 | 01 | `apps/backend/web/scheduler/*.py`, `apps/backend/web/scheduler/__init__.py`, `apps/backend/web/webtest/lite/*`, `apps/backend/web/webtest/scheduler/*`, requirement docs if needed | lite scheduler、任务分类回归 | 03,04,05 | none | 03,04,05 | round-01 | lite 主线常驻任务全部归类且至少一个扩面任务落地 |
| 03_state_storage_optimization | model + migration + router + tests | 01 已稳定事件落库策略 | `tb_apscheduler_job_state` 模型/迁移、listener 双写、列表/防重改读状态表、测试 | 01 | `apps/backend/web/models/scheduler/*`, `apps/backend/web/migrations/lite/*`, `apps/backend/web/migrations/dev/*`, `apps/backend/web/migrations/stg/*`, `apps/backend/web/routers/scheduler/*`, `apps/backend/web/services/scheduler/*`, `apps/backend/web/scheduler/__init__.py`, tests | migration、router、manual run、日报回归 | 04,05 | none | 04,05 | round-01 | `/scheduler/jobs` 和防重不再依赖扫历史日志 |
| 04_persistence_api | backend api + settings + tests | 02 已完成默认策略归类；03 最好已完成读路径稳定化 | `system_settings` 覆盖存储、策略查询/更新接口、列表扩展字段、测试 | 02 | `apps/backend/web/models/setting/*`, `apps/backend/web/services/system/*`, `apps/backend/web/services/scheduler/*`, `apps/backend/web/routers/scheduler/*`, tests | setting 读写、router、策略校验 | 05 | none | 05 | round-01 | 后端能返回默认/生效/来源/候选策略并安全更新覆盖值 |
| 05_frontend_settings | frontend ui + api + tests | 04 已提供后端字段和接口 | 列表新增策略展示、单任务设置弹窗、API 类型和页面测试 | 04 | `apps/frontend/src/views/Snow/Setting/Scheduler/*`, `apps/frontend/src/api/snow/Scheduler/*` | frontend API、交互逻辑 | none | none | none | round-01 | 页面能展示并修改单任务策略，且只允许后端支持的选项 |

## orchestration notes

- 实现顺序：`01 -> 02 -> 03 -> 04 -> 05`
- 只读分析可以并行做，但真正实现不能并行，因为 5 个 task 都会碰 scheduler 核心或其上游接口。
- 每个 task 都用独立 implementer 和 reviewer，review 报告单独落到各自子目录。
- 任务级 review scope 用 worktree 当前 diff 隔离，不把别的 task 的半成品混入评审。

## first dispatch

1. implementer 先做 `01_runtime_core` 的测试目标拆解和最小 failing test。
2. reviewer 在实现完成后只审 `01_runtime_core` 的 diff 和回归证据。
3. 01 通过后，再更新 requirement status 并派发 02。
