# lite 下 APScheduler SQLite 支持任务设计
## 任务状态
- 状态：待开始
- 优先级：中
- 目标：让 lite 支持显式开启的 APScheduler + SQLite 模式
- 关键边界：lite 默认仍关闭 scheduler，不把重环境能力顺手并进来
## 1. 任务目标
这次任务只解决一件事：
- 在 `SNOW_APP_STATUS=lite` 下，给 APScheduler 增加一条正式、可重复、可验证的 SQLite 支持路径
同时保留三个前提：
- lite 默认行为继续保持 `ENABLE_SCHEDULER = False`
- 不要求引入 Redis、Dramatiq、profiler
- 不把 `dev/stg/test` 的 MySQL 运行口径改成 SQLite
## 2. 当前现状
当前仓库已经具备一部分基础能力：
- APScheduler 代码仍在仓库里，传统环境默认启用
- lite 下启动时会跳过 scheduler 初始化和 scheduler 路由注册
- APScheduler 的数据库检查逻辑已经改成 SQLAlchemy 通用表检查，不再写死 MySQL `SHOW TABLES`
- lite 当前阶段结论明确把 scheduler 排除在主线保证范围之外
当前缺的不是“库本身是否支持 SQLite”，而是“项目是否给 lite 提供正式支持入口”。
## 3. 核心判断
- APScheduler 配合 `SQLAlchemyJobStore` 可以使用 SQLite
- 当前仓库里真正的问题是 lite 运行边界和稳定性边界，不是功能完全不可用
- 因为 SQLite 写锁更敏感，不能默认把 scheduler 持久化直接压到 lite 业务库上
所以这次任务的正确目标不是“lite 默认开启 scheduler”，而是：
- 新增显式开启的 lite scheduler 模式
- 把默认内存模式和可选持久化模式区分清楚
- 为持久化模式加独立 SQLite 文件和 fail-fast 保护
## 4. 选定方案
采用“默认关闭 + 显式开启 + 独立持久化文件”的方案。
### 4.1 默认模式
- `LITE_ENABLE_SCHEDULER=false`
- 继续跳过 scheduler 初始化
- 继续不注册 scheduler 相关路由
### 4.2 lite 可选内存模式
- `LITE_ENABLE_SCHEDULER=true`
- `LITE_ENABLE_PERSISTENT_JOBSTORE=false`
- 启动 scheduler，但只使用 `MemoryJobStore`
这个模式的定位是：
- 先解决 lite 下“能调度”
- 不承诺重启后 job 保留
### 4.3 lite 可选持久化模式
- `LITE_ENABLE_SCHEDULER=true`
- `LITE_ENABLE_PERSISTENT_JOBSTORE=true`
- `LITE_SCHEDULER_DB_PATH=/path/to/lite_scheduler.db`
这个模式下，APScheduler 的 JobStore 必须使用单独 SQLite 文件，不能和 `LITE_DB_PATH` 共用同一个库文件。
## 5. 非法状态
下面这些状态必须直接失败，不能静默兜底：
- 开启持久化 JobStore，但没提供 `LITE_SCHEDULER_DB_PATH`
- `LITE_SCHEDULER_DB_PATH` 与 `LITE_DB_PATH` 指向同一个文件
- lite 下关闭 scheduler，却仍尝试注册 scheduler 路由
- lite 下配置了持久化 JobStore，但数据库检查失败时仍继续启动
## 6. 配置设计
建议新增或正式收口这些 lite 配置：
- `LITE_ENABLE_SCHEDULER`
  - 默认 `false`
  - 控制 lite 是否初始化 scheduler
- `LITE_ENABLE_PERSISTENT_JOBSTORE`
  - 默认 `false`
  - 只在 scheduler 已开启时生效
- `LITE_SCHEDULER_DB_PATH`
  - 默认空
  - 仅在持久化模式下必填
  - 指向独立 SQLite 文件
## 7. 代码改动点
### 7.1 `web/settings.py`
需要补两部分：
- `LiteConfig` 的 lite scheduler 配置读取
- `apply_runtime_overrides()` 对 `LITE_ENABLE_SCHEDULER`、`LITE_ENABLE_PERSISTENT_JOBSTORE`、`LITE_SCHEDULER_DB_PATH` 的运行时收口
### 7.2 `web/__init__.py`
需要确保 lite 下的 scheduler 初始化逻辑按新配置生效：
- 默认仍跳过
- 显式开启时才初始化
- 持久化模式失败时直接 fail fast
### 7.3 `web/routers/__init__.py`
保持现有按 `ENABLE_SCHEDULER` 控制的路由注册逻辑，但要确认 lite 显式开启时可以正常注册。
### 7.4 `web/scheduler/`
需要补两类保护：
- 为 lite 持久化模式构造独立 SQLite jobstore 配置
- 在数据库检查阶段明确阻断“jobstore 与业务库共用同一路径”
## 8. 测试要求
至少补四类测试：
1. lite 默认模式下，scheduler 仍然不初始化
2. lite 内存模式下，scheduler 可以启动，且不依赖 `SCHEDULER_JOBSTORES`
3. lite 持久化模式下，独立 SQLite jobstore 可以通过检查并完成初始化
4. `LITE_SCHEDULER_DB_PATH == LITE_DB_PATH` 时直接失败
如果后续要开放 job 读写接口，还要补 scheduler 路由注册和基本 API smoke。
## 9. 验收标准
完成后至少满足这些条件：
- lite 默认行为完全不变
- 显式开启后，lite 可以运行 APScheduler
- 持久化模式不会和业务库共用 SQLite 文件
- 非法配置会在启动阶段直接报错
- 新增测试可以稳定复现默认、内存、持久化三种状态
## 10. 风险点
- 如果把 JobStore 直接放进业务库，Web 和 Scheduler 共写更容易放大 SQLite 锁竞争
- 如果只开能力不加 fail-fast，最容易出现“看起来能跑，实际配置混乱”
- 如果把 scheduler 默认纳入 lite 主线，会扩大当前 lite 的验证边界
## 11. 推荐实施顺序
建议按下面顺序做：
1. 先补配置收口和非法状态保护
2. 再支持 lite 内存模式
3. 再支持独立 SQLite 持久化模式
4. 最后补 README 和任务归档文档
