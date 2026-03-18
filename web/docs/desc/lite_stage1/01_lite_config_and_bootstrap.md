# 任务 1：LiteConfig 与轻量启动骨架

## 目标

在不影响现有 `dev/stg/test` 运行方式的前提下，为项目增加一个可独立启动的轻量模式。

本任务完成后，应用应能在 `lite` 配置下启动，并允许跳过 Redis、Dramatiq、APScheduler 持久化 JobStore、profiler 等非核心依赖。

## 任务范围

- 新增 `LiteConfig`
- 为轻量模式增加显式开关
- 调整启动链路，让非核心组件支持“按配置跳过”
- 保持现有主线配置行为不变

## 关键文件

- `web/settings.py`
- `web/__init__.py`
- `web/common/cache/base.py`
- `web/task/__init__.py`
- `web/scheduler/__init__.py`

## 设计原则

- 先做“可关闭”，不先做“彻底删除”
- 轻量模式以单机、单进程、低并发为目标
- 数据库仍是核心依赖，其余基础设施先降级为可选
- 不在本任务里处理 SQLite 的全部兼容细节

## 配置建议

建议增加以下开关：

- `ENABLE_REDIS`
- `ENABLE_TASK_QUEUE`
- `ENABLE_SCHEDULER`
- `ENABLE_PERSISTENT_JOBSTORE`
- `ENABLE_PROFILER`
- `ENABLE_XALPHA_SQL_CACHE`

建议默认值：

- Lite 模式下 Redis 关闭
- Lite 模式下 Dramatiq 关闭
- Lite 模式下 Scheduler 关闭，或仅允许内存模式
- Lite 模式下 profiler 关闭

## 执行步骤

1. 在 `web/settings.py` 新增 `LiteConfig`
2. 在 `web/__init__.py` 为缓存、调度器、任务队列、profiler 增加条件初始化
3. 将当前“初始化失败直接终止”的路径拆成“核心依赖”和“可选依赖”
4. 明确 Lite 模式的环境变量入口
5. 补一份轻量模式启动说明

## 验收标准

- `lite` 模式下应用可以启动
- 启动时不会因为 Redis / Dramatiq / profiler / 持久化 JobStore 缺失而失败
- `dev/stg/test` 行为不被改变
- 启动日志能明确显示哪些组件被跳过

## 非目标

- 不在本任务里迁移数据库到 SQLite
- 不在本任务里修改完整测试体系
- 不在本任务里整理 Alembic 迁移历史
- 不追求轻量模式功能完整

## 风险提示

- 如果启动逻辑改动过深，可能影响主线环境
- 如果条件化初始化做得不清晰，后续排查问题会更困难

## 任务完成产物

- `LiteConfig`
- 一套可工作的轻量启动路径
- 一份简短的启动说明

## 当前状态

- 已完成（阶段一）

## 本轮结果

- 已新增 `LiteConfig`，并支持通过 `SNOW_APP_STATUS=lite` 启动轻量模式。
- Lite 启动链路已经拆成“数据库必须成功，其他组件按配置可跳过”。
- Redis、Dramatiq、APScheduler、flask-profiler 在 lite 模式下都可以不作为必选依赖。
- 可选基础设施相关导入已经改成按配置延迟加载，不会在模块 import 阶段就把 lite 启动卡死。
- 轻量模式入口和环境变量说明已经补到 README 和系统文档。

## 对应验证

- `tests/test_lite_bootstrap_review.py`
- 验证重点：
  - 阻断 `apscheduler`、`redis`、`dramatiq`、`flask_profiler` 导入后，`create_app("lite")` 仍可启动
  - scheduler 在 cache 未初始化时可以回退到原始 `job_id`
