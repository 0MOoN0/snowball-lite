# scheduler 执行持久化策略第一阶段任务

- [ ] 引入按 `job_id` 解析的 scheduler 执行持久化策略注册表
- [ ] 收口 listener 对 `SUBMITTED`、`EXECUTED`、`ERROR`、`MISSED` 的落库判定
- [ ] 将 `AsyncTaskScheduler.consume_notification_outbox` 切到 `signal_only`
- [ ] 保持手动触发防重、异常日报和现有任务列表接口在本任务范围内可用
- [ ] 为空轮询不落库、有业务信号才落库、错误必落库补回归测试
- [ ] 明确本任务不包含状态表/事件表拆分和历史数据回收

## 任务状态

- 类型：子任务文档
- 状态：待开始
- 父任务：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/scheduler_execution_persistence_requirement.md`
- 当前阶段：阶段 1，策略基座 + `consume_notification_outbox` 首个接入
- 阶段目标：减少轮询型 scheduler 任务对 `tb_apscheduler_log` 的无效写入，同时保住当前依赖这张表的最小运行能力
- 当前交付：任务级执行持久化策略基座，以及 `consume_notification_outbox` 的首个接入
- 明确不交付：`job_state` / `job_event_log` 拆表、全量任务策略迁移、历史日志表清理任务

## 0. 先说当前结论

当前问题不是“通知 outbox 设计错了”，而是统一 listener 把 scheduler 运行观测和业务事件混在了一张 append-only 表里。

现状：

1. `consume_notification_outbox` 每 60 秒运行一次，即使这分钟没有待消费 outbox，也会触发 `SUBMITTED` 和 `EXECUTED` 两次落库
2. `tb_apscheduler_log` 既被任务列表页当最新状态来源，也被异常日报当错误来源，还被手动触发当防重依据
3. 单纯加清理任务只能控体积，不能减少“空轮询也写库”的根因

本阶段选择的边界是：

- 不重做整套 scheduler 观测模型
- 先补“任务级执行持久化策略”这一层，让 listener 能按任务特征决定是否落库
- 先用 `AsyncTaskScheduler.consume_notification_outbox` 验证 `signal_only` 路径

## 1. 问题定义

当前 listener 对所有任务使用同一套落库规则：

- `SUBMITTED` 全量落库
- `EXECUTED` 全量落库
- `ERROR` 全量落库
- `MISSED` 全量落库

这套规则对低频、人工触发或排障导向的任务还能接受，但对“固定频率轮询、经常什么都没处理”的任务会产生大量无效记录。

根因不是表没有清理，而是系统没有表达“这次运行是否值得持久化”的能力。

## 2. 完成定义

本阶段完成后，必须同时满足下面几条：

- listener 在写 `tb_apscheduler_log` 前，先按解析后的 `job_id` 查询执行持久化策略
- `ERROR` 和 `MISSED` 仍然默认落库，不能因为策略接入而丢掉异常观测
- 手动触发的一次性 job 仍保留当前防重能力，不因为策略接入而失效
- `AsyncTaskScheduler.consume_notification_outbox` 在“本次没有领取任何 outbox”时不再写成功日志到库
- `AsyncTaskScheduler.consume_notification_outbox` 在“本次处理了 outbox 或出现异常”时仍能留下可追踪记录
- 现有接口和日报不能误以为“每次空轮询都会刷新最近执行记录”

## 3. 范围

本阶段只覆盖下面这些内容：

- `apps/backend/web/scheduler/__init__.py` 中的 listener 落库判定
- 新增一个代码侧的 scheduler 执行持久化策略注册表
- `AsyncTaskScheduler.consume_notification_outbox` 的首个策略接入
- 对应的 lite / scheduler 回归测试
- 必要的文档说明

## 4. 非目标

本阶段不做下面这些事情：

- 不把 `tb_apscheduler_log` 直接替换成“状态表 + 事件表”
- 不为所有现有任务一次性补齐策略
- 不新增数据库配置表，不做运行时动态改策略
- 不清理历史 `tb_apscheduler_log` 脏数据
- 不把 `tb_notification_outbox` 的保留期清理混入本任务完成条件

## 5. 选定方案

采用“代码侧任务执行持久化策略注册表”方案。

规则如下：

1. 先按 `_resolve_job_id(...)` 的结果匹配策略，保证手动任务和原始任务 ID 口径一致
2. 默认策略继续保持 `full`，避免这次任务把所有现有 job 行为一起改掉
3. 首批新增 `signal_only`，用于轮询型任务
4. `signal_only` 下：
   - `ERROR` / `MISSED` 仍落库
   - 手动触发的一次性 job 仍保留 `SUBMITTED` 记录
   - `EXECUTED` 只有在本次运行带来业务信号时才落库
5. `consume_notification_outbox` 的“业务信号”定义为：
   - 返回的 `stats` 中 `claimed > 0`
   - 或本次运行进入错误路径

本阶段不引入“数据库配置化策略”，原因是当前需求是代码内可控、可测试、可版本化的收口，不需要在线改策略。

## 6. 数据与存储影响

- `tb_apscheduler_log` 继续保留为 scheduler 运行观测表，不改变表结构
- 本阶段只改变“新记录何时写入”，不改变已有字段语义
- `tb_notification_outbox` 继续保留业务 outbox 身份，不承担 scheduler 运行观测职责
- 本阶段不新增 migration，不改 `__bind_key__`

数据归属要明确分开：

- `tb_notification_outbox` 属于业务通知生命周期
- `tb_apscheduler_log` 属于 scheduler 运行观测生命周期

## 7. API 与交互影响

- `/scheduler/jobs` 继续可用，但对 `signal_only` 任务不再承诺“每次空轮询都刷新最近执行时间”
- `/scheduler/job_log/<job_id>` 继续返回最近一次已持久化记录；如果任务长期空轮询，最近成功记录可能停留在上一次“有业务信号”的执行
- 手动触发接口当前的 15 分钟防重逻辑必须保持可用
- 异常日报继续只关注 `ERROR` / `MISSED` 记录，当前行为不变

## 8. 生命周期与旧数据处理

本阶段只处理“修复后的新写入规则”，不处理历史回填。

具体边界：

- 已存在的 `tb_apscheduler_log` 记录保持原状
- 接入 `signal_only` 后，空轮询不会新增成功记录，但不会删除旧成功记录
- 如果后续需要清理历史日志、增加保留期、拆状态表，另开任务

## 9. 验收标准

- 在 lite 下连续执行 `consume_notification_outbox()`，当返回 `claimed=0` 时，不新增 `EXECUTED` 成功记录
- 当 `consume_notification_outbox()` 返回 `claimed>0` 时，仍会新增对应执行记录
- 当 scheduler 任务抛异常时，`ERROR` 记录仍能正常写入 SQLite
- 手动提交同一个任务后，15 分钟内再次提交仍会被防重拦住
- 现有异常日报查询最近 24 小时 `ERROR` / `MISSED` 的逻辑保持可用

## 10. 验证要求

- `apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py`
- `apps/backend/web/webtest/lite/test_lite_notification_outbox.py`
- 如有必要，补 `apps/backend/web/webtest/scheduler/test_scheduler_listener.py`

至少要覆盖三类断言：

1. `signal_only` 任务空轮询不落库
2. `signal_only` 任务有信号执行会落库
3. `ERROR` / 手动触发防重不回归

## 11. 风险点

- 如果只给 `EXECUTED` 加策略，但忽略 `SUBMITTED`，容易误伤手动触发防重
- 如果把 `signal_only` 定义成“只要函数正常返回就落库”，那和当前行为没有本质区别
- 如果任务列表页仍按“最近一次执行一定每分钟刷新”理解 `signal_only` 任务，会误读旧时间戳

## 12. 后续动作

本阶段完成后，如果还要继续做 scheduler 观测收口，后续优先级如下：

1. 评估是否把 `tb_apscheduler_log` 拆成“最新状态”和“错误事件”两类存储
2. 评估是否给更多轮询型任务补 `signal_only` 或 `error_only`
3. 单独立项处理 `tb_apscheduler_log` 和 `tb_notification_outbox` 的保留期清理
