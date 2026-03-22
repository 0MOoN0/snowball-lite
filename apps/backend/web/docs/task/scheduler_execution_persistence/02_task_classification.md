# scheduler 执行持久化策略归类与扩面任务
- [ ] 盘点 lite 主线已注册 scheduler 任务
- [ ] 为每个任务给出 `full`、`signal_only`、`error_only` 的归类结果
- [ ] 为可收口任务补业务信号判定或错误优先规则
- [ ] 调整回归测试，覆盖至少 1 个 `signal_only` 和 1 个 `error_only`/`full` 边界
- [ ] 形成“任务 -> 默认策略 -> 原因”的文档化结果

## 任务状态
- 类型：子任务文档
- 父任务：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/scheduler_execution_persistence/requirement.md`
- 依赖：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/scheduler_execution_persistence/01_runtime_core.md`
- 状态：待开始
- 目标：把 lite 主线常驻任务从“统一默认 full”推进到“有明确归类结果”

## 1. 问题定义
只完成首个 outbox 试点还不够。

如果其它 lite 主线任务没有明确归类，这个完整需求仍然只算局部验证，不能算真正收口。当前缺口是：
1. 哪些任务应该继续 `full` 还没有结论
2. 哪些任务可以转 `signal_only` 还没有信号定义
3. 哪些任务只关心错误还没有被明确标记

## 2. 完成定义
本任务完成后，必须同时满足下面几条：
- lite 主线已注册常驻任务都出现在归类清单里
- 每个任务都有明确默认策略和选择理由
- 至少完成一轮从 `full` 收口到 `signal_only` / `error_only` 的代码接入
- 没有信号判定方法的任务不会被硬切成 `signal_only`
- 现有任务列表、异常日报和手动触发不因扩面回归

## 3. 范围
本任务只覆盖 lite 主线常驻 scheduler 任务：
- `apps/backend/web/scheduler/async_task_scheduler.py`
- `apps/backend/web/scheduler/notice_scheduler.py`
- `apps/backend/web/scheduler/asset_scheduler.py`
- `apps/backend/web/scheduler/analysis_scheduler.py`
- 其它实际在 lite 主线启用的注册任务

## 4. 非目标
本任务不做下面这些事情：
- 不做前端页面配置
- 不做数据库持久化覆盖
- 不处理历史 MySQL 环境专用任务
- 不把 `tb_apscheduler_log` 拆表

## 5. 选定方案
采用“先归类，再有限扩面”的方式。

规则：
1. 先列出 lite 主线常驻任务清单
2. 逐个判断其成功执行是否有可测试业务信号
3. 有明确信号的任务，允许切 `signal_only`
4. 只关心异常、不需要成功轨迹的任务，允许切 `error_only`
5. 信号不清楚、依赖方风险高的任务，保留 `full`

交付物必须至少包含一张结果表：
- `job_id`
- 默认策略
- 是否支持切换
- 原因

## 6. 数据与存储影响
- 不新增表结构
- 只改变任务默认策略和对应新写入行为
- 归类结果优先保存在代码和任务文档里，不要求此时持久化到 `system_settings`

## 7. API 与交互影响
- `/scheduler/jobs` 和 `/scheduler/job_log/<job_id>` 继续工作
- 任务列表里的“最近一次执行时间”会更接近“最近一次有意义的已持久化记录”
- 依赖方不能再默认把“没有新成功记录”解释为“任务没跑”

## 8. 生命周期与旧数据处理
本任务只影响新写入规则：
1. 旧日志不改
2. 新默认策略从接入时刻开始生效
3. 如果某个任务后续需要重新调整策略，算后续配置或新任务，不在本任务里动态热改

## 9. 验收标准
- lite 主线常驻任务全部完成归类
- 至少新增 1 个非 outbox 任务的策略判断结论
- 所有被切换策略的任务都有测试或明确理由
- 扩面后 `ERROR` / `MISSED` 落库能力不回归

## 10. 验证要求
- 更新或新增对应任务的 lite / scheduler 回归测试
- 至少验证一个保留 `full` 的任务和一个收口任务
- 如策略影响任务列表时间戳口径，补接口层断言

## 11. 风险点
- 如果为了“全量归类”强行给任务定义信号，会把隐含语义写错
- 如果没有文档化归类结果，后面再做前端配置会失去边界
- 如果把历史环境任务也一起算进来，范围会被拉散

## 12. 后续动作
本任务完成后继续做：
1. 策略覆盖持久化与后端接口
2. 前端单任务策略设置
