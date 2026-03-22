# scheduler 任务状态表与事件日志分层优化任务
- [ ] 明确复用 `tb_apscheduler_log` 作为 append-only 事件日志
- [ ] 新增 `tb_apscheduler_job_state`
- [ ] 将任务列表查询迁到 `job_state`
- [ ] 将手动触发防重从历史日志读取迁到 `job_state`
- [ ] 保持异常日报继续读取事件日志
- [ ] 补 migration、模型、读写路径和回归测试

## 任务状态
- 类型：子任务文档
- 父任务：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/scheduler_execution_persistence/requirement.md`
- 依赖：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/scheduler_execution_persistence/01_runtime_core.md`
- 状态：待开始
- 目标：把“最新状态”与“历史事件”分开，降低高频任务日志表的语义混乱和查询成本
- 当前交付：新增一张状态表，复用现有日志表

## 1. 问题定义
当前 `tb_apscheduler_log` 一张表同时承担下面几类职责：
1. 历史事件留痕
2. 任务列表最近状态
3. 手动触发防重
4. 异常日报查询

这会带来三个问题：
- 高历史量下，“最新状态”查询容易失真或代价偏高
- “最近一次调度”和“最近一次有意义事件”混在一起
- append-only 历史表被迫承担状态表职责，后续前端配置也难以扩展

## 2. 完成定义
本任务完成后，必须同时满足下面几条：
- 现有 `tb_apscheduler_log` 继续保留，但语义收口为 append-only 事件日志
- 新增 `tb_apscheduler_job_state`，并保证每个 `job_id` 只有一条当前状态记录
- 任务列表优先读取 `job_state`
- 手动触发防重优先读取 `job_state`
- 异常日报继续读取事件日志，不丢历史错误时间线
- 没有要求补齐全历史回填，但新写入路径必须同时维护状态和事件

## 3. 范围
本任务只覆盖下面这些内容：
- `tb_apscheduler_job_state` 的模型、lite migration 和必要的传统环境迁移评估
- scheduler listener 或相关写入链路的状态同步
- 任务列表、手动触发防重、异常日报的读路径调整
- 对应后端回归测试

## 4. 非目标
本任务不做下面这些事情：
- 不清理历史 `tb_apscheduler_log` 数据
- 不要求把历史事件全量回填到 `job_state`
- 不把前端单任务策略设置并入本任务
- 不改 `tb_notification_outbox` 的保留期

## 5. 选定方案
采用“保留事件日志 + 新增状态表”的方案。

规则：
1. `tb_apscheduler_log` 继续 append-only
2. `tb_apscheduler_job_state` 每个 `job_id` 一条
3. 事件日志负责：
   - `ERROR`
   - `MISSED`
   - 有业务信号的 `EXECUTED`
   - 必要的 `SUBMITTED`
4. 状态表负责：
   - 最近执行状态
   - 最近计划运行时间
   - 最近提交时间
   - 最近完成时间
   - 最近错误信息和时间
   - 最近一次有业务信号的执行时间

## 6. 数据与存储影响
新增表建议至少包含下面这些字段：
- `job_id`，唯一键
- `last_execution_state`
- `last_scheduler_run_time`
- `last_submitted_time`
- `last_finished_time`
- `last_signal_run_time`
- `last_error`
- `last_error_time`
- `create_time`
- `update_time`

迁移要求：
- lite 主线必须补 `apps/backend/web/migrations/lite/`
- 如果共享运行路径依赖新表，必须评估 `apps/backend/web/migrations/dev/`、`stg/`、`test/` 是否同步

## 7. API 与交互影响
- `/scheduler/jobs` 改为优先查 `job_state`
- `/scheduler/job_log/<job_id>` 继续查事件日志
- 手动触发防重不再依赖扫历史事件表里的最近 `SUBMITTED`
- 异常日报继续按时间窗口查询事件日志

## 8. 生命周期与旧数据处理
本任务只保证新写入规则，不承诺全历史回填。

规则：
1. 已存在的历史事件日志保持原状
2. `job_state` 初始可按首次新事件写入建立
3. 如果某个任务长期没有新事件，允许状态表暂时缺失，由后续补齐或首次运行时创建
4. 删除任务定义后遗留状态行如何清理，另开任务

## 9. 验收标准
- 新表创建成功且 `job_id` 唯一
- 任务列表在没有扫全历史日志的情况下返回最近状态
- 手动触发防重继续可用
- 异常日报仍能看到最近 24 小时错误事件
- 新写入路径下，状态表和事件日志的职责不再混淆

## 10. 验证要求
- 新状态表模型和 migration 测试
- scheduler listener 状态同步测试
- `/scheduler/jobs` 查询测试
- 手动触发防重测试
- 异常日报查询回归测试

## 11. 风险点
- 如果没有先收口 Task 1 的策略，状态表仍会被空轮询频繁刷新
- 如果状态表字段定义不够清楚，后面前端仍会把“最近状态”和“最近事件”混淆
- 如果实现时只补 lite migration，忽略共享路径对传统环境的影响，后面会埋兼容坑

## 12. 后续动作
本任务完成后，再继续做：
1. 策略覆盖持久化与后端接口
2. 前端单任务策略设置
