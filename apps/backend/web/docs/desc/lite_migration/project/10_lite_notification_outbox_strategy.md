# lite 通知 SQLite outbox 接入（归档）

## 归档说明

- 归档时间：`2026-03-22`
- 归档来源：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/lite_dramatiq_legacy_business_inventory.md`
- 当前状态：已完成
- 说明：原实现任务文档已归档到 `desc/lite_migration/project/`

## 实际结果

- lite 首批“网格策略监控确认通知”已经从“直接 `dispatch_notification(...)`”切成“先写 SQLite outbox，再由 APScheduler 消费”
- 新增 `tb_notification_outbox`，状态流转覆盖 `pending`、`processing`、`retry_waiting`、`succeeded`、`failed`
- 新增通知 outbox 服务层，负责入队、领取、重试和失败落点
- 新增 APScheduler 周期消费器，继续复用 `dispatch_notification(...)` 做真正发送
- 非 lite 的 actor / sync fallback 路径保持不变
- lite 其它通知路径暂时不跟着扩改，继续保留原来的同步或 fallback 行为

## 主要落点

- `apps/backend/web/common/enum/task/notification_outbox_enum.py`
- `apps/backend/web/models/async_task/notification_outbox.py`
- `apps/backend/web/services/async_task/notification_outbox_service.py`
- `apps/backend/web/scheduler/async_task_scheduler.py`
- `apps/backend/web/scheduler/asset_scheduler.py`
- `apps/backend/web/migrations/lite/versions/lite_add_notification_outbox_table.py`
- `apps/backend/web/webtest/lite/test_lite_notification_outbox.py`

## 当前设计结论

### 1. 业务入口

- 首批接入点是 `asset_scheduler.py` 里的网格策略监控确认通知
- lite 下通知对象持久化后，不再立刻发送，而是写入一条 outbox 记录
- 当前 `event_key` 口径收口到 `notification-dispatch:{notification.id}`

### 2. 调度与执行

- APScheduler 每分钟扫描一批到期 outbox 记录
- 消费器先把记录切到 `processing`，再调用 `dispatch_notification(...)`
- 发送成功后记为 `succeeded`

### 3. 重试策略

- 默认 `max_retry_count = 3`
- 固定重试间隔 `60` 秒
- 可重试失败会进入 `retry_waiting`
- 超过重试上限或出现明确不可继续的问题时进入 `failed`

## 主要验证

```bash
cd apps/backend
pytest web/webtest/lite/test_lite_notification_outbox.py -q
pytest web/webtest/lite/test_lite_notification_outbox.py web/webtest/lite/test_lite_stage5_schema_expansion.py web/webtest/lite/test_lite_scheduler_sqlite_support.py web/webtest/scheduler/test_notification_dispatch.py -q
```

## 保留边界

- 这次只解决 lite 首批通知异步解耦，不扩到全部通知场景
- 本任务没有引入新的外部 MQ，也没有恢复 Redis / Dramatiq 作为 lite 默认前提
- `succeeded` / `failed` outbox 记录当前只保留，不做自动清理
- 本轮验证范围只覆盖 lite 主线，不覆盖 MySQL `dev/stg/test` 迁移回归
