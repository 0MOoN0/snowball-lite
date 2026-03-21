# lite scheduler 接入收口（归档）

## 归档状态

- 状态：已完成
- 原任务路径：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/lite_scheduler_integration_strategy.md`
- 说明：这份文档已从 `task/` 归档到 `desc/lite_project/`，保留完整设计、实现和验收结论

## Checklist

- [x] 明确 lite 下 scheduler 的正式边界，默认开启并保留显式关闭能力
- [x] 去掉 `/scheduler/job/run` 对 Redis 的硬依赖
- [x] 去掉 scheduler 任务对 Dramatiq actor 的硬依赖，补同步 fallback
- [x] 收口 lite 持久化 jobstore 到独立 SQLite 文件
- [x] 补 lite 内存模式、持久化模式、无 Redis、无 task queue 四类回归
- [x] 收口前端 lite 口径和运行文档，避免前后端状态不一致

## 任务状态

- 状态：已完成
- 目标：把 lite 下 APScheduler 从“能显式打开”收口成“默认开启、边界清楚、依赖明确、运行稳定”的能力
- 当前默认：lite 默认开启 scheduler
- 数据库决策：持久化 jobstore 使用独立 SQLite 文件，不接入 lite 业务库
- 依赖决策：lite 下 scheduler 不能再强依赖 Redis、Dramatiq
- 范围补充：当前任务不考虑 MySQL 版本的 scheduler 持久化收口，只按 lite / SQLite 单机运行口径推进

## 0. 先说当前结论

当前仓库不是“没有接 APScheduler”，而是已经做到了下面这一步：

1. lite 默认开启 scheduler
2. 显式设置 `LITE_ENABLE_SCHEDULER=false` 后可以关闭
3. 显式设置 `LITE_ENABLE_PERSISTENT_JOBSTORE=true` 后可以把 jobstore 落到独立 SQLite 文件

这条链路这次已经收口成“可放心接入”的状态，前提和边界也已经固定下来：

- 手动运行任务接口不再依赖 Redis
- scheduler 任务不再强依赖 Dramatiq actor，task queue 不可用时会自动 fallback
- 前端 lite 默认开放 scheduler 页面和能力入口
- 持久化 jobstore 继续使用独立 SQLite 文件，不接入 lite 业务库

剩下要持续记住的只有一条运行建议：

- scheduler 底层还是 gevent，长期运行仍优先建议走 `gunicorn -c web/gunicorn_lite.config.py web.lite_application:app`

## 1. 任务目标

这次任务只解决一件事：

- 让 lite 下 scheduler 成为默认开启、可运行、可回归、可解释的正式主链路能力

这次任务没有改下面两件事：

- 没把 Redis、Dramatiq、通知全链路重新拉回 lite 主线必备组件
- 没把 scheduler 持久化默认改成开启，默认仍是内存 jobstore

## 2. 当前现状

当前代码已经具备这些基础能力：

1. `web/settings.py` 已支持
   - `LITE_ENABLE_SCHEDULER`
   - `LITE_ENABLE_PERSISTENT_JOBSTORE`
   - `LITE_SCHEDULER_DB_PATH`
2. `web/scheduler/base.py` 已接入
   - `flask_apscheduler.APScheduler`
   - `apscheduler.schedulers.gevent.GeventScheduler`
   - `apscheduler.executors.gevent.GeventExecutor`
3. lite 持久化模式已经明确禁止 `LITE_SCHEDULER_DB_PATH` 和 `LITE_DB_PATH` 指向同一个 SQLite 文件
4. `apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py` 已覆盖默认开启、显式关闭、内存模式、持久化模式和非法同路径失败

当前这轮真正收掉的点是：

1. `/scheduler/job/run` 已经去掉 Redis 临时映射，改成可解析的 manual job id
2. `notice_scheduler.py`、`databox_test_scheduler.py`、`asset_scheduler.py` 都统一走通知出口，task queue 不可用时会同步 fallback
3. 前端 `.env.lite` 和 `runtimeProfile.ts` 已改成 scheduler 默认开启
4. README、环境变量说明和长期文档已经统一成“lite 默认开启 scheduler，默认内存模式”的口径

## 3. 选定方案

这次按下面这套口径收口：

1. lite 默认开启 scheduler
2. lite 允许两种模式
   - 内存模式：只保证运行，不保留重启后的 job
   - 持久化模式：jobstore 使用独立 SQLite 文件
3. lite 默认开启 scheduler 后，不要求 Redis 和 Dramatiq 一起开启
4. 所有 scheduler 相关链路都必须在“无 Redis、无 task queue”前提下可降级运行
5. 持久化 jobstore 不接入业务库

## 4. 数据库方案

### 4.1 推荐方案

推荐把 scheduler 的持久化 jobstore 放到独立数据库。

如果是 lite / SQLite，推荐独立 SQLite 文件。

当前任务不考虑 MySQL 版本的持久化方案。

这个项目当前目标是从历史 MySQL 运行方式里脱离出来，收口成可单独使用 SQLite 运行的 lite 版本，所以这里先只定义 SQLite 口径：

1. lite 内存模式：不需要数据库
2. lite 持久化模式：独立 SQLite 文件

### 4.2 不推荐接入业务库的原因

不推荐把 scheduler jobstore 直接接到业务库，主要因为这几件事：

1. 业务表和调度元数据边界不同，生命周期也不同
2. jobstore 表是 APScheduler 自己管理的，不应该混进 lite 业务 schema 演进
3. lite 当前已经明确把业务库 bootstrap、迁移基线和 scheduler jobstore 分开
4. 独立库更容易清空、重建、排障和迁移
5. 可以减少“调度状态污染业务库”这类低级事故
6. SQLite 下共用同一个文件更容易把锁竞争、文件损坏、职责耦合揉到一起

### 4.3 当前仓库里的明确推荐

对这个仓库当前口径，当前决策就是：

1. lite 内存模式：不需要数据库
2. lite 持久化模式：独立 SQLite 文件
3. 历史 MySQL 环境：这次不考虑，不作为本任务设计前提

一句话结论：

- 如果你要正式接入 scheduler，数据库单独放更好，不要接入 lite 业务库

### 4.4 环境级约定

这次再把 `prod/dev/test` 的口径写死：

1. `stable/prod`：业务库单独；如果启用 scheduler 持久化，jobstore 再单独一份 SQLite 文件
2. `dev`：业务库单独；如果启用 scheduler 持久化，jobstore 也单独一份 SQLite 文件
3. `test`：默认使用内存 jobstore，不额外落文件
4. `test` 只有在验证 scheduler 持久化行为时，才额外启用独立的 pytest 临时 scheduler SQLite 文件
5. 所有环境里，scheduler jobstore 都不和业务库共用同一个 SQLite 文件

## 5. 改造重点

### 5.1 手动运行任务链路去 Redis

当前手动运行任务接口的动态 job 映射依赖 Redis，这和 lite 默认边界冲突。

推荐收口成“不依赖 Redis 的 job_id 编码方案”：

1. 手动触发 job 使用可解析前缀，例如 `manual::<origin_job_id>::<uuid>`
2. listener 直接从 job_id 解析原始 job_id
3. 不再通过 Redis 临时 key 保存映射

这样最直接，改动也最小。

### 5.2 调度任务去 Dramatiq 硬依赖

lite 下 scheduler 任务不能假设 task queue 一定可用。

推荐统一成这条规则：

1. task queue 可用时，优先走 actor
2. task queue 不可用时，自动回退到同步发送或仅落库
3. 不能因为 actor 不可用就让整个 scheduler 任务失败

`notice_scheduler.py` 已经接近这套口径，其他任务文件对齐它就行。

### 5.3 前后端口径收口

如果后端默认开启 scheduler，而前端 lite 仍强制隐藏页面，就会出现“后端可用、前端看不到”的状态。

这里至少要二选一：

1. 继续隐藏前端页面，但文档里明确写“lite 只支持后端调度，不开放前端管理页”
2. 前端根据运行配置显式开放 scheduler 页面

当前这次任务最后选的是第 2 条：

1. 后端 lite 默认开启 scheduler
2. 前端 scheduler 管理页进入 lite 默认主链路
3. README、前端说明、长期文档和环境变量文档都按这个口径统一描述

### 5.4 启动路径收口

当前 scheduler 底层是 gevent 调度器。

所以这次任务里需要把运行建议写清楚：

1. lite 开启 scheduler 时，优先走 `gunicorn -c web/gunicorn_lite.config.py web.lite_application:app`
2. 直接 `python -m web.lite_application` 仅作为开发验证，不当成正式运行口径

## 6. 代码改动点

建议优先看这些文件：

- `apps/backend/web/routers/scheduler/scheduler_job_operation_routers.py`
- `apps/backend/web/scheduler/__init__.py`
- `apps/backend/web/scheduler/databox_test_scheduler.py`
- `apps/backend/web/scheduler/asset_scheduler.py`
- `apps/backend/web/scheduler/notice_scheduler.py`
- `apps/backend/web/settings.py`
- `apps/frontend/.env.lite`
- `apps/frontend/src/config/runtimeProfile.ts`
- `README.md`
- `apps/backend/web/docs/环境变量配置指南.md`

## 7. 实施步骤

建议按这个顺序做：

1. 先收口手动运行任务链路，拔掉 Redis 依赖
2. 再统一 scheduler 任务里的通知发送 fallback
3. 再补无 Redis、无 task queue 的回归测试
4. 再把 lite 默认值和前端默认入口切到开启
5. 最后更新 README、长期文档和环境变量说明

## 8. 验收标准

完成后至少满足这些条件：

1. lite 默认开启 scheduler，默认使用内存 jobstore
2. `LITE_ENABLE_SCHEDULER=false` 时可以关闭 scheduler；默认开启时，在 `ENABLE_REDIS=false`、`ENABLE_TASK_QUEUE=false` 下也能正常启动
3. 手动运行、暂停、恢复任务接口不再依赖 Redis
4. lite 持久化模式下，jobstore 继续使用独立 SQLite 文件
5. `LITE_SCHEDULER_DB_PATH == LITE_DB_PATH` 时初始化直接失败
6. 调度任务在 task queue 不可用时不会因为 actor 失败而整任务报错
7. 前后端与文档对 scheduler 的能力描述一致
8. 本任务不新增 MySQL 持久化兼容要求

## 9. 风险点

- 手动运行任务的 job_id 映射逻辑调整后，历史日志展示可能要一起核对
- 某些任务虽然能调度，但业务本身仍可能依赖 databox、通知渠道或外部服务
- gevent 路径和普通 Flask 启动路径的行为差异，如果不写清楚，后续排障会反复绕回来
- scheduler 默认开启后，前端和后端的默认口径必须持续保持一致，否则后续很容易再出现“页面能看到但后端没开”或反过来的回归

## 10. 推荐落地顺序

这次实际落地顺序就是三步：

1. 先把 Redis / Dramatiq 的硬依赖收掉
2. 再把持久化 jobstore 的独立 SQLite 口径写死
3. 最后把 lite 默认值和前端默认入口一起切到开启

现在这三步都已经完成。
