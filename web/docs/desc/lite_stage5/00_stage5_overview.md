# 轻量版第五阶段规划（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 5 任务目录（原 task 文档已清理）
- 当前状态：已完成
- 阶段结论：lite 主线的 SQLite 初始化、schema 和运行时边界已经完成阶段 5 收口，建议进入阶段 6
- 阶段收口：已完成，review 工件已清理

## 本阶段实际结果

- lite migration baseline 已扩到主线所需范围，补齐了分类、指数、系统设置和通知相关 schema
- lite bootstrap 已统一到 `bootstrap_lite_database(...)`，`lite_app` 不再靠 `db.create_all()` 兜底
- lite 启动链路里对 `pymysql` 的依赖已经改成可选，SQLite 分支不再把 MySQL 异常类型当硬前提
- `/system/token` 和 `/api/enums/versions` 在 lite 下已经改成显式不支持，而不是隐式 500
- 阶段 5 的综合定向回归已通过，结果是 `23 passed, 30 warnings`

## 本阶段归档文档

- `00_stage5_overview.md`
- `01_lite_schema_expansion.md`
- `02_lite_bootstrap_and_create_all_cleanup.md`
- `03_runtime_mysql_specific_sql_cleanup.md`
- `04_lite_runtime_dependency_boundary.md`
- `05_stage5_acceptance_and_decision.md`

## 当前背景

阶段 4 已经把 lite 主线业务覆盖补到了可重复验证的程度，但当时还不能直接说 lite 已经形成正式主线口径。

真正还缺的是三层收口：

1. `migrations_snowball_lite` 还是阶段 3 baseline，不是 lite 主线完整建库口径。
2. lite 初始化链路里还有 `db.create_all()` 在做兜底。
3. 运行时和外围依赖边界还没有完全改成 lite 能解释清楚的正式行为。

## 第五阶段目标

第五阶段解决的是：

- 把 SQLite 从“已经能跑”收口成“lite 主线正式口径”
- 把 lite 初始化、建库、迁移和运行时边界统一到可重复验证的路径
- 把仍然留在仓库里的 MySQL / Redis 历史假设压回非 lite 路径

## 第五阶段验收结果

- lite 主线路径已经不再把 MySQL 当成初始化和运行前提
- lite 所需核心 schema 已能通过统一 migration / bootstrap 路径准备完成
- lite 主线路径里的剩余 MySQL 专有逻辑已经继续收口，并且有显式方言判断
- lite 对 Redis、scheduler、task queue、profiler 的默认关闭边界已经能写成明确口径

## 保留边界

- 历史 MySQL 测试夹具仍然保留 `db.create_all()` 和 `pymysql` 假设，但它们已经不属于 lite 正式路径
- 其他 Redis 相关外围接口还没有在这一阶段全部做成显式 lite 降级
- SQLite 下的 Decimal、pandas、akshare 等既有 warning 仍然存在，但当前不阻塞进入阶段 6
