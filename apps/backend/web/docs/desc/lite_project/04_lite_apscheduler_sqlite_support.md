# lite 下 APScheduler SQLite 显式支持（归档）

## 归档状态

- 状态：已完成
- 原任务文档：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/lite_apscheduler_sqlite_support_design.md`
- 对应状态：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/review/lite_apscheduler_sqlite_support_design/task-status.md`
- 对应评审：
  - `round-01-review.md`
  - `round-02-review.md`
- 关键边界：这份文档记录的是“lite 默认仍关闭 scheduler、只支持显式开启”的那个阶段
- 后续更新：当前默认口径已经切到“lite 默认开启 scheduler”，见 [07_lite_scheduler_integration_strategy.md](07_lite_scheduler_integration_strategy.md)

## 结论

- 在这个阶段，lite 开始支持显式开启的 APScheduler + SQLite 路径。
- 在这个阶段，`SNOW_APP_STATUS=lite` 下仍然默认关闭 scheduler。
- 在这个阶段，lite 支持两种显式模式：
  - 内存模式：只解决“能调度”，不保留重启后的 job
  - 持久化模式：使用独立 SQLite 文件保存 APScheduler jobstore

## 实际落地

- 已新增 `LITE_ENABLE_SCHEDULER` 运行时收口
- 已新增 `LITE_ENABLE_PERSISTENT_JOBSTORE` 运行时收口
- 已新增 `LITE_SCHEDULER_DB_PATH` 运行时收口
- 已实现独立 SQLite jobstore 配置生成
- 已阻断 jobstore 与业务库共用同一 SQLite 文件
- 已把 lite 持久化模式预检查调整为“检查路径和连通性”，允许空库首次启动自动建表
- 已统一 `SCHEDULER_AVAILABLE` 的设置时机，只在初始化成功后标记为可用
- 已把 scheduler 路由注册条件改成按实际可用状态决定
- 已更新 README 中 lite + scheduler 的说明

## 主要代码落点

- `apps/backend/web/settings.py`
- `apps/backend/web/__init__.py`
- `apps/backend/web/routers/__init__.py`
- `apps/backend/web/scheduler/__init__.py`
- `apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py`
- `README.md`

## 启动契约

### 默认模式（阶段事实）

- `LITE_ENABLE_SCHEDULER=false`
- 跳过 scheduler 初始化
- 跳过 scheduler 路由注册

### lite 内存模式（阶段事实）

- `LITE_ENABLE_SCHEDULER=true`
- `LITE_ENABLE_PERSISTENT_JOBSTORE=false`
- 启动 scheduler，使用默认 `MemoryJobStore`

### lite 持久化模式（阶段事实）

- `LITE_ENABLE_SCHEDULER=true`
- `LITE_ENABLE_PERSISTENT_JOBSTORE=true`
- `LITE_SCHEDULER_DB_PATH=/path/to/lite_scheduler.db`

约束：

- `LITE_SCHEDULER_DB_PATH` 必须和 `LITE_DB_PATH` 不同
- jobstore 必须使用独立 SQLite 文件，不能和业务库共用
- 首次启动允许目标文件为空库，由 `SQLAlchemyJobStore` 在启动阶段自动建表

## 非法状态

下面这些情况会在启动阶段直接失败：

- 开启持久化 JobStore，但没提供 `LITE_SCHEDULER_DB_PATH`
- `LITE_SCHEDULER_DB_PATH` 与 `LITE_DB_PATH` 指向同一个文件
- lite 下 scheduler 初始化失败，但仍试图继续启动
- scheduler 未成功初始化，但仍试图注册 scheduler 路由

## 测试与评审

新增和回归验证覆盖了这些点：

1. 在该阶段的默认模式下，scheduler 不初始化，也不注册相关路由
2. lite 内存模式下，scheduler 可以启动，且不依赖 `SCHEDULER_JOBSTORES`
3. lite 持久化模式下，独立 SQLite jobstore 可在空库首次启动并自动建表
4. `LITE_SCHEDULER_DB_PATH == LITE_DB_PATH` 时启动直接失败
5. scheduler 初始化失败时，`SCHEDULER_AVAILABLE` 不会被误标成 `True`
6. scheduler 测试清理不会因为 listener 累积而串状态

定向验证结果：

- `pytest apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py -q` -> `6 passed, 1 warning`
- `pytest apps/backend/web/webtest/stage3/test_task03_runtime_mysql_specific_sql_cleanup.py -q` -> `3 passed, 1 warning`
- `pytest apps/backend/web/webtest/lite/test_lite_bootstrap_review.py -q` -> `5 passed, 1 warning`

评审结果：

- round-01 抓到 1 条测试隔离问题，已修复
- round-02 无新发现

## Checklist

- [x] 为 lite 增加 `LITE_ENABLE_SCHEDULER` 运行时收口
- [x] 为 lite 增加 `LITE_ENABLE_PERSISTENT_JOBSTORE` 运行时收口
- [x] 为 lite 增加 `LITE_SCHEDULER_DB_PATH` 运行时收口
- [x] 实现独立 SQLite jobstore 配置生成
- [x] 阻断 jobstore 与业务库共用同一文件
- [x] 调整 lite 持久化模式预检查，允许空库首次建表
- [x] 统一 `SCHEDULER_AVAILABLE` 的设置时机
- [x] 调整 scheduler 路由注册条件
- [x] 补默认模式回归测试
- [x] 补内存模式回归测试
- [x] 补持久化模式首次启动建表测试
- [x] 补非法同路径失败测试
- [x] 更新 README 中 lite + scheduler 的说明
- [x] 落地后补一份归档或阶段结论文档

## 保留边界

- 这次完成的是 lite 下“显式开启”的 APScheduler 支持路径；后续版本已经在新任务里把 scheduler 升格成 lite 默认主链路。
- `dev/stg/test` 现有 MySQL 口径和历史兼容路径没有被改成 SQLite。
- 测试隔离仍然依赖 APScheduler 私有 `_listeners` 结构；如果上游库内部实现变化，这部分测试清理逻辑可能需要跟着调整。
