# Lite 与 MySQL 运行组件对照

> 归档说明
>
> 当前长期版本见 [docs/backend/lite-mysql-matrix.md](../../../../../../docs/backend/lite-mysql-matrix.md)。
> 这份文档保留阶段对照记录，后续正式维护以根目录 `docs/` 下的长期文档为准。
> 其中 scheduler 默认值已经在后续任务里调整；当前 scheduler 口径以 `docs/backend/lite-mysql-matrix.md` 和 [07_lite_scheduler_integration_strategy.md](07_lite_scheduler_integration_strategy.md) 为准。

## 结论先看

- lite 主线不是只把数据库从 MySQL 换成 SQLite。
- 在这个阶段里，lite 真正做的是把一批重运行时组件从“默认必须有”改成“默认关闭”或“明确不支持”。
- 当前 lite 主线保留的是本地单机、弱依赖下的核心业务链路，不承诺覆盖传统多环境部署的整套运行前提。

## 组件对照表

| 组件 / 能力 | MySQL 版 / 传统环境口径 | lite 当前口径 | 说明 |
|---|---|---|---|
| 数据库形态 | 3 个 MySQL 库：`snowball`、`snowball_data`、`snowball_profiler` | 1 个 SQLite 文件，默认库和 `snowball` bind 收口到同一文件 | lite 主线已经不再以 MySQL server 为前提 |
| MySQL server 依赖 | 默认存在 | 默认不存在 | lite 已完成“脱离 MySQL server”的主线收口 |
| Redis 缓存 | 默认启用 | 默认关闭 | `LiteConfig.ENABLE_REDIS = False`，启动时直接跳过缓存初始化 |
| Dramatiq 异步任务队列 | 默认启用，Broker 依赖 Redis | 默认关闭 | `LiteConfig.ENABLE_TASK_QUEUE = False`，不启动异步任务队列 |
| Dramatiq 常驻 worker | 默认需要 | 不属于 lite 主线 | 代码还在仓库里，但不是 lite 默认运行前提 |
| APScheduler 调度器 | 默认启用 | 当时默认关闭 | 当时 `LiteConfig.ENABLE_SCHEDULER = False`，启动时跳过调度器初始化 |
| APScheduler 持久化 JobStore | 默认启用，使用 SQLAlchemy JobStore | 默认关闭 | lite 不保证持久化 scheduler 能力 |
| scheduler 相关路由 | 会注册 | 当时不注册 | `web/routers/__init__.py` 里按 `ENABLE_SCHEDULER` 控制 |
| flask-profiler | 可启用，带独立 profiler 存储 | 默认关闭 | `LiteConfig.ENABLE_PROFILER = False` |
| xalpha SQL 缓存 | 默认走 SQL 缓存库 | 改成目录型 `csv` 缓存 | lite 不再把 `snowball_data` 这类 SQL 缓存库当主线前提 |
| databox 启动期初始化 | 缓存可用时初始化 | 默认跳过启动期初始化 | 因为 lite 默认不开 Redis，启动时会跳过 `databox.init_app(app)` |
| DataBox / xalpha 拉数能力 | 保留 | 保留 | lite 保留拉数和查询主线，但不等于保留 Redis 依赖的外围配套 |
| `/system/token` | 走 Redis 读写 token | lite 下明确不支持 | 现在会返回可解释的失败消息，不再隐式 500 |
| `/api/enums/versions` | 传统路径从 Redis 读 | lite 下改从 SQLite 读 | 这是“保留能力但换实现”，不是直接删除 |
| 多环境部署前提 | `dev/stg/test/prod` + MySQL/Redis/队列/调度 | lite 只保证本地单机、弱依赖主线 | lite 不承诺传统重环境的整套运行条件 |
| 数据库引擎日志 | 默认可开 | 默认关闭 | lite 收口到更轻的本地运行口径 |

## lite 仍然保留的主线能力

- 资产基础管理
- 交易记录管理
- 基础分析能力
- 必要的查询类 API
- `xalpha` / DataBox 拉数

## 不要误解成这几件事

- “lite 默认没有” 不等于 “仓库里已经删掉代码”。
- `dev/stg/test/prod` 这些传统环境和历史 MySQL 兼容路径还在，只是不属于 lite 主线结论。
- lite 当前能保证的是 SQLite、本地单机、弱依赖下的主线能力，不是完整生产形态的一比一替代。

## 主要依据

- `README.md`
- `web/settings.py`
- `web/__init__.py`
- `web/routers/__init__.py`
- `web/docs/轻量版分支改造方案.md`
- `web/docs/desc/lite_migration/stage5/04_lite_runtime_dependency_boundary.md`
- `web/docs/desc/lite_migration/stage6/00_stage6_overview.md`
- `web/docs/desc/lite_migration/stage6/05_stage6_acceptance_and_decision.md`
- `web/docs/mysql_to_sqlite_analysis.md`
