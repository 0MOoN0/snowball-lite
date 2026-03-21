# Lite and MySQL Matrix

这份文档只保留 lite 和传统 MySQL 运行口径的长期对照，方便后续判断一项能力该放哪边。

## 结论先看

- lite 主线不是只换数据库，而是把一批重运行时组件改成默认关闭、明确不支持，或收口成弱依赖下可默认运行
- 传统 MySQL 口径还在，但它不是 lite 的默认前提
- 当前 lite 只保证本地单机、弱依赖下的核心业务链路

## 组件对照表

| 组件 / 能力 | 传统 MySQL 口径 | lite 当前口径 | 说明 |
| --- | --- | --- | --- |
| 数据库形态 | 多个 MySQL 库 | 单个 SQLite 文件 | 默认库和 `snowball` bind 收口到同一文件 |
| MySQL server 依赖 | 默认存在 | 默认不存在 | lite 主线已经脱离 MySQL server |
| Redis 缓存 | 默认启用 | 默认关闭 | 由 `LiteConfig.ENABLE_REDIS = False` 控制 |
| Dramatiq 任务队列 | 默认启用 | 默认关闭 | lite 默认不启动异步任务队列 |
| APScheduler 调度器 | 默认启用 | 默认启用（默认内存模式） | 可显式关闭 `LITE_ENABLE_SCHEDULER=false` |
| APScheduler 持久化 JobStore | 默认启用 | 默认关闭 | lite scheduler 默认只跑内存模式，持久化仍需显式开启 |
| flask-profiler | 可启用 | 默认关闭 | lite 默认不跑性能分析工具 |
| xalpha SQL 缓存 | 默认走 SQL 缓存库 | 改成目录型 `csv` 缓存 | 不再把 `snowball_data` 这类 SQL 缓存库当主线前提 |
| `databox` 启动初始化 | 视缓存而定 | 默认跳过 | 因为 lite 默认不开 Redis |
| `/system/token` | 走 Redis 读写 token | 明确不支持 | lite 下直接给可解释失败 |
| `/api/enums/versions` | 读 Redis | 读 SQLite | 这是保留能力但换实现 |
| 多环境部署前提 | `dev/stg/test/prod` + MySQL/Redis/队列/调度 | 本地单机、弱依赖主线 | lite 不承诺整套重环境前提 |
| 数据库引擎日志 | 默认可开 | 默认关闭 | lite 收口到更轻的运行口径 |

## lite 仍然保留的主线能力

- 资产基础管理
- 交易记录管理
- 基础分析能力
- 必要的查询类 API
- `xalpha` / DataBox 拉数

## 不要误解成这几件事

- `lite` 默认不依赖某项能力，不等于仓库里已经删掉代码
- 传统 `dev/stg/test/prod` 路径还在，只是不属于 lite 主线结论
- lite 当前保证的是能跑、能测、能收敛，不是完整生产形态的一比一替代

## 相关文档

- [Backend Docs README](README.md)
- [Backend System Overview](system-overview.md)
- [Repo Baseline](../architecture/repo-baseline.md)
