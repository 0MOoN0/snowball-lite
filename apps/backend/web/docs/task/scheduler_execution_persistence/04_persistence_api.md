# scheduler 策略覆盖持久化与后端接口任务
- [ ] 定义策略覆盖在 `system_settings` 中的存储结构
- [ ] 实现代码默认值与持久化覆盖值的合并规则
- [ ] 为任务列表和详情接口补策略字段
- [ ] 提供安全的策略查询与更新接口
- [ ] 覆盖未知任务、非法策略、不支持切换等校验场景

## 任务状态
- 类型：子任务文档
- 父任务：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/scheduler_execution_persistence/requirement.md`
- 依赖：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/scheduler_execution_persistence/02_task_classification.md`
- 状态：待开始
- 目标：把策略从“纯代码默认值”扩展成“代码默认值 + 持久化覆盖值”

## 1. 问题定义
只有代码默认策略还不够。

如果后面要让前端按任务单独设置策略，后端必须先解决三件事：
1. 覆盖值存哪里
2. 默认值和覆盖值怎么合并
3. 前端通过什么接口拿到“可选策略”和“当前生效策略”

## 2. 完成定义
本任务完成后，必须同时满足下面几条：
- scheduler 策略覆盖值会持久化到 `system_settings`
- 没有覆盖值时，系统继续使用代码默认策略
- 任务列表接口会返回策略相关字段
- 后端提供单任务或批量策略更新接口
- 不支持切换的任务、未知任务、非法策略值都会被拒绝

## 3. 范围
本任务只覆盖下面这些内容：
- `system_settings` 中的 scheduler 策略配置
- scheduler 侧的策略查询和更新接口
- 任务列表接口返回值扩展
- 后端校验、合并和测试

## 4. 非目标
本任务不做下面这些事情：
- 不实现前端页面
- 不把系统设置通用页面直接改造成 scheduler 专属页面
- 不做历史日志清理
- 不引入数据库级动态热更新要求

## 5. 选定方案
采用“单个 JSON 配置项 + scheduler 专属接口”的方案。

存储规则：
1. 使用 `system_settings` 持久化覆盖值
2. 单个配置项 key 建议为 `scheduler.execution_persistence_policies`
3. `settingType` 使用 `json`
4. `group` 使用 `system`

JSON 结构只保存覆盖值，例如：
```json
{
  "AsyncTaskScheduler.consume_notification_outbox": "signal_only",
  "notice_scheduler.daily_report": "error_only"
}
```

合并规则：
1. 先读取代码默认策略
2. 再叠加持久化覆盖值
3. 如果任务不存在、策略非法、任务不支持该策略，则拒绝写入

## 6. 数据与存储影响
- 新增或复用 `system_settings` 中的一个 JSON 配置项
- 该配置项归 scheduler 策略覆盖拥有
- 删除该配置项等价于“回退到全部代码默认值”
- 本任务不改 `tb_apscheduler_log` 表结构

## 7. API 与交互影响
任务列表接口至少补下面几个字段：
- `defaultPolicy`
- `effectivePolicy`
- `policySource`
- `supportedPolicies`

后端至少提供两类能力：
1. 查询当前所有任务的策略视图
2. 更新单任务或批量任务的策略覆盖

这里不要求前端直接调用通用 `system_settings` 接口拼 JSON。
前端应该调用 scheduler 专属接口，由后端负责把覆盖值映射到 `system_settings`。

## 8. 生命周期与旧数据处理
策略覆盖的生命周期要明确：
1. 代码默认值永远存在
2. 持久化覆盖值是可选层
3. 删除覆盖值后，任务回退到代码默认策略
4. 如果任务从代码里被移除，后续需要由清理任务处理遗留覆盖值，不在本任务里自动清扫

## 9. 验收标准
- 后端能正确读写 `scheduler.execution_persistence_policies`
- 任务列表返回有效策略字段
- 非法策略值、未知任务、不支持切换的任务会被拒绝
- 删除覆盖值后任务恢复代码默认策略
- 没有覆盖配置时系统行为与 Task 1 / Task 2 保持一致

## 10. 验证要求
- `system_settings` 读写测试
- scheduler 策略合并逻辑测试
- scheduler 任务列表接口测试
- scheduler 策略更新接口测试

## 11. 风险点
- 如果直接把前端暴露给通用 `system_settings` JSON，会把校验压力丢给 UI
- 如果不区分默认值和覆盖值，前端很难解释“当前为什么是这个策略”
- 如果任务删除后不处理遗留 key，配置会逐步累积，但这属于后续清理任务

## 12. 后续动作
本任务完成后继续做前端单任务策略设置。
