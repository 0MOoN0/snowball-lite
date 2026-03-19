# 轻量版第三阶段规划（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 3 任务目录（原 task 文档已清理）
- 当前状态：已完成
- 阶段结论：继续推进，但只建议做受控范围内的 SQLite 扩圈，不建议现在就宣称“全仓库 SQLite 化”
- 代码审查：已完成，review 工件已清理

## 本阶段实际结果

- 已给 `web/webtest` 增加 stage3 专用 SQLite fixture
- 已完成 2 条业务链路 SQLite 集成验证
- 已清理阶段三范围内会直接挡路的 MySQL 专有 SQL
- 已新增 `migrations_snowball_lite` 和 `bootstrap_lite_database`

## 当前背景

阶段二已经证明了三件事：

1. lite 模式本身能跑
2. `xalpha` / DataBox 的真实链路可以单独验收
3. 一批高风险 SQLite 模型已经能在 lite 路径下工作

但第三阶段不能简单理解成“继续多补几个测试”。

当前真正卡住 SQLite 迁移判断的，还是这几类问题：

- 旧测试体系还站在 MySQL 上
- 运行时代码里还有 MySQL 专有 SQL
- lite 的可信度仍然大量依赖 `db.create_all()`

## 第三阶段目标

第三阶段更适合做“SQLite 兼容基线 + 业务链路验证”，不适合直接冲“全仓库 SQLite 化”。

更具体一点，就是把当前结论从：

- “lite 最小链路能跑”

推进到：

- “选定的业务链路可以在 SQLite 下稳定跑”
- “一批旧测试可以脱离 MySQL server”
- “lite 至少有一条比 `db.create_all()` 更像正式初始化的路径”

## 适合放进第三阶段的任务

### 1. 先做选定范围的 SQLite 测试夹具桥接

优先级：最高

原因：

- `web/webtest/conftest.py` 现在还直接连 MySQL 并执行 `CREATE DATABASE IF NOT EXISTS ...`
- 如果不先解决这一层，后面的业务链路验证还是只能留在 lite 自建测试里，无法吃到旧测试资产

### 2. 选 1 到 2 条高频业务链路做 SQLite 集成验证

优先级：高

原因：

- 阶段二已经明确建议第三阶段补“更业务化的高频链路”
- 这一步比继续堆模型测试更能说明 lite 对实际使用有没有价值

### 3. 清理会直接挡住 SQLite 的 MySQL 专有 SQL

优先级：中高

原因：

- `show variables like 'long_query_time'`
- `SHOW TABLES LIKE 'apscheduler_jobs'`

这类写法继续留着，后面只会不断碰壁。

### 4. 给 lite 建一个可解释的迁移基线

优先级：中

原因：

- 现在主要靠 `db.create_all()`
- 这能证明“能建表”，但还证明不了“初始化路径是可维护的”

### 5. 做阶段三收口判断

优先级：最后

原因：

- 阶段三不是最终发布
- 但做完以后，要能回答“是否值得进入更大范围的 SQLite 迁移”

## 不适合放进第三阶段的任务

- 不做全仓库 dev/stg/test/prod 配置统一迁 SQLite
- 不重写全部历史 Alembic 迁移
- 不把整个 `web/webtest/` 一次性迁完
- 不把 scheduler 全量恢复成 SQLite 持久化模式
- 不做所有外部依赖链路的真机回归

这些事要么范围太大，要么和 lite 当前目标不一致。

## 任务拆分

- `01_sqlite_fixture_bridge.md`
- `02_business_chain_analysis_validation.md`
- `03_runtime_mysql_specific_sql_cleanup.md`
- `04_sqlite_migration_baseline.md`
- `05_stage3_acceptance_and_decision.md`

## 第三阶段验收标准

- 选定范围的旧测试夹具可以在 SQLite 下跑起来
- 至少 1 到 2 条业务链路在 SQLite 下完成集成验证
- 阶段三选定范围内不再直接依赖 MySQL 专有 SQL
- lite 不再只靠 `db.create_all()` 作为唯一初始化口径
- 能输出明确结论：继续推进 / 暂停 / 转向更小范围维护

## 推荐顺序

1. 先做 SQLite 测试夹具桥接
2. 再补业务链路验证
3. 再收口 MySQL 专有 SQL
4. 再做 lite 迁移基线
5. 最后输出阶段三结论
