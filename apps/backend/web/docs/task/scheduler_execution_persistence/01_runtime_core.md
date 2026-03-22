# scheduler 执行持久化策略运行时基座任务
- [ ] 引入按 `job_id` 解析的执行持久化策略注册表
- [ ] 收口 listener 对 `SUBMITTED`、`EXECUTED`、`ERROR`、`MISSED` 的落库判定
- [ ] 将 `AsyncTaskScheduler.consume_notification_outbox` 切到 `signal_only`
- [ ] 保持手动触发防重、异常日报和任务列表最小兼容
- [ ] 为“空轮询不落库 / 有信号才落库 / 错误必落库”补回归测试

## 任务状态
- 类型：子任务文档
- 父任务：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/scheduler_execution_persistence/requirement.md`
- 状态：待开始
- 目标：先把策略能力真正跑起来，并用 outbox 轮询任务验证 `signal_only`
- 完成边界：只交付运行时策略基座和首个接入点

## 1. 问题定义
当前共享 listener 对所有任务统一按 `SUBMITTED`、`EXECUTED`、`ERROR`、`MISSED` 全量落库。

这对 `consume_notification_outbox` 这类每分钟轮询任务会造成两类噪音：
1. 本次没有领取任何 outbox，也会留下成功执行记录
2. 任务是否“真正处理了业务”无法在落库前被区分

## 2. 完成定义
本任务完成后，必须同时满足下面几条：
- listener 在落库前能按解析后的 `job_id` 命中策略
- 默认策略继续是 `full`，不把其它任务一起改坏
- `consume_notification_outbox` 在 `claimed=0` 时不再写成功记录
- `consume_notification_outbox` 在 `claimed>0` 或进入错误路径时仍会留下记录
- `ERROR` / `MISSED` 继续稳定落库
- 手动触发的一次性 job 仍保留当前防重能力

## 3. 范围
本任务只覆盖下面这些内容：
- `apps/backend/web/scheduler/__init__.py`
- 新增代码侧策略注册表和信号判定逻辑
- `apps/backend/web/scheduler/async_task_scheduler.py`
- 对应 lite / scheduler 回归测试

## 4. 非目标
本任务不做下面这些事情：
- 不为所有现有任务一次性补齐策略
- 不引入数据库持久化覆盖
- 不改前端 scheduler 页面
- 不清理历史 `tb_apscheduler_log`
- 不处理 `tb_notification_outbox` 保留期

## 5. 选定方案
采用“代码侧注册表 + 任务显式信号判定”方案。

规则：
1. 先按 `_resolve_job_id(...)` 结果匹配策略
2. 默认策略为 `full`
3. 首批支持 `signal_only`
4. `signal_only` 下：
   - `ERROR` / `MISSED` 继续落库
   - 手动触发保留 `SUBMITTED`
   - `EXECUTED` 只有本次运行带来业务信号时才落库
5. `consume_notification_outbox` 的业务信号定义为：
   - `stats.claimed > 0`
   - 或进入异常路径

## 6. 数据与存储影响
- `tb_apscheduler_log` 不改表结构，只改何时写入
- `tb_notification_outbox` 继续承担业务事件生命周期
- 本任务不新增 migration，不改 `__bind_key__`

## 7. API 与交互影响
- `/scheduler/jobs` 继续可用，但不再承诺 outbox 任务每分钟都刷新“最近一次执行时间”
- `/scheduler/job_log/<job_id>` 继续返回最近一次已持久化记录
- 手动触发防重逻辑保持现状
- 异常日报继续只看 `ERROR` / `MISSED`

## 8. 生命周期与旧数据处理
本任务只处理新写入规则，不处理历史回填：
1. 已存在的 `tb_apscheduler_log` 保持原状
2. 接入 `signal_only` 后，空轮询不再新增成功记录
3. 旧成功记录不删除

## 9. 验收标准
- lite 下连续执行 `consume_notification_outbox()`，当 `claimed=0` 时不新增 `EXECUTED` 记录
- 当 `claimed>0` 时仍新增对应执行记录
- 当任务抛异常时，`ERROR` 记录仍能写入 SQLite
- 手动提交同一个任务后，15 分钟内再次提交仍会被防重拦住

## 10. 验证要求
- `apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py`
- `apps/backend/web/webtest/lite/test_lite_notification_outbox.py`
- 如有必要，补 `apps/backend/web/webtest/scheduler/test_scheduler_listener.py`

至少覆盖三类断言：
1. `signal_only` 任务空轮询不落库
2. `signal_only` 任务有信号执行会落库
3. `ERROR` / 手动触发防重不回归

## 11. 风险点
- 如果只改 `EXECUTED`，忽略 `SUBMITTED`，可能误伤手动触发防重
- 如果把“正常返回”错当成“有业务信号”，就还是会持续写入
- 如果直接把更多任务一起切策略，回归面会不受控

## 12. 后续动作
本任务完成后，后续继续做：
1. lite 主线任务策略归类与扩面
2. 策略覆盖持久化与后端接口
3. 前端单任务策略设置
