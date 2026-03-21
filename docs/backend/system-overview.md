# Backend System Overview

这份文档是 `snowball-lite` 后端长期说明的正式入口，聚焦当前仍然有效的运行口径、目录职责和协作约束。

## 当前定位

- 后端工作区从 `apps/backend/` 进入，真实代码位于 `apps/backend/web/`
- lite 是默认主线，默认运行口径是 `SNOW_APP_STATUS=lite` + SQLite
- MySQL、Redis、Dramatiq、APScheduler 持久化和 profiler 相关能力仍然保留在仓库里，但默认不属于 lite 主线前提
- 当前可以说“lite 的 SQLite 可信度已经明显提升”，不能说“整个仓库已经完成 SQLite 迁移”

## 关键目录

| 路径 | 作用 |
| --- | --- |
| `apps/backend/web/application.py` | 传统环境启动入口，按 `SNOW_APP_STATUS` 选择配置 |
| `apps/backend/web/lite_application.py` | lite 启动入口，固定 `SNOW_APP_STATUS=lite`，并在启动前执行 `bootstrap_lite_database(...)` |
| `apps/backend/web/settings.py` | 各环境配置和 lite 运行时开关入口 |
| `apps/backend/web/models/` | SQLAlchemy 模型，继续沿用 `__bind_key__` 体系 |
| `apps/backend/web/services/` | 业务逻辑主落点，新逻辑优先放这里 |
| `apps/backend/web/routers/` | API 路由层，当前以 Flask-RESTX 为主 |
| `apps/backend/web/scheduler/` | APScheduler 相关能力，lite 默认关闭 |
| `apps/backend/web/task/` | Dramatiq 任务队列相关能力，lite 默认关闭 |
| `apps/backend/web/webtest/` | Web 层、服务层、模型层和 lite 主线集成验证 |
| `tests/` | lite 链路、bootstrap、`xalpha` 兼容和仓库级补充测试 |

## 运行链路

应用初始化走 `web.create_app(...)`，启动顺序以“数据库是核心依赖，其它基础设施按开关启用”为准：

1. 加载 `settings.py` 中对应环境的配置。
2. 初始化数据库模型；数据库失败会直接终止启动。
3. 按 `ENABLE_*` 开关决定是否初始化 Redis、scheduler、task queue、profiler。
4. 初始化 Flask-RESTX API、路由、异常处理和 `xalpha` 相关设置。
5. lite 入口额外执行 `bootstrap_lite_database(...)`，确保 SQLite baseline 先就位。

lite 下默认关闭的能力：

- `ENABLE_REDIS = False`
- `ENABLE_TASK_QUEUE = False`
- `ENABLE_SCHEDULER = False`
- `ENABLE_PERSISTENT_JOBSTORE = False`
- `ENABLE_PROFILER = False`

如果确实要在 lite 下临时打开 scheduler，需要额外设置 `LITE_ENABLE_SCHEDULER=true`；如果还要持久化 JobStore，再加 `LITE_ENABLE_PERSISTENT_JOBSTORE=true` 和独立的 `LITE_SCHEDULER_DB_PATH`。

## API 和代码组织约定

- 新增业务逻辑优先放 `apps/backend/web/services/`，不要继续把逻辑堆进 router
- 新增接口优先沿用 Flask-RESTX `Namespace` + Marshmallow `Schema`
- 接口响应统一使用 `R.ok(...)`、`R.fail(...)`、`R.paginate(...)`
- 日志继续沿用 `web.weblogger`
- 触及 lite 主线路径时，优先保证 SQLite 可跑、可测、可迁移；触及历史 MySQL 兼容路径时，不要顺手改坏旧能力

## 文档边界

长期说明和执行档案已经分开：

- `docs/backend/`：后端长期说明
- `docs/architecture/`：仓库基线、边界和目录职责
- `apps/backend/web/docs/task/`：任务设计
- `apps/backend/web/docs/review/`：执行记录和评审产物
- `apps/backend/web/docs/desc/`：阶段归档和结论文档

## 相关文档

- [Runtime Config](runtime-config.md)
- [Repo Baseline](../architecture/repo-baseline.md)
- [Backend Docs README](README.md)
