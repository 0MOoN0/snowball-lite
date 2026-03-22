# 任务 5：阶段 5 验收与进入阶段 6 的决策（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 5 任务 5 收口与决策（原 task 文档已清理）
- 当前状态：已完成
- 最终结论：建议进入阶段 6
- 代码审查：已完成，最终复审已通过

## 结论

- 结论：建议进入阶段 6
- 推进方式：继续做 lite 主线的零 MySQL 环境最终验收
- 不建议现在做的事：不要把阶段 5 解读成全仓库 SQLite 迁移完成，也不要说所有历史路径都已经脱离 MySQL

阶段 5 的收口重点不是继续扩业务面，而是把 lite 主线路径的初始化、schema 和运行时边界收成正式口径。当前这一步已经完成，说明 lite 主线已经从“SQLite 可以跑”推进到“SQLite 作为默认主线口径可解释、可回归、可继续验收”。

## 本阶段已验证通过

- lite migration baseline 已补齐分类、指数、系统设置和通知相关核心 schema，并补上 ETF / LOF 到指数表的外键约束
- `lite_app` 和 lite 最小链路验证已经改成统一走 `bootstrap_lite_database(...)`，不再依赖 `db.create_all()` 兜底
- lite 启动链路不再把 `pymysql` 当硬依赖，SQLite 分支不会再误走 MySQL 专有表检查
- `/system/token` 和 `/api/enums/versions` 在 lite 下已经改成显式不支持，Redis 边界可以直接解释
- 阶段 5 综合定向回归已经通过，结果是 `23 passed, 30 warnings`

## 仍然保留的边界

- 历史 MySQL 测试夹具里还保留 `db.create_all()` 和 `pymysql` 假设，但它们已经不在 lite 正式路径里
- 其他 Redis 相关外围接口还没有在这一阶段全部补成显式 lite 边界
- SQLite 下仍然有 Decimal、pandas、akshare 等既有 warning，但当前不构成 blocker

## 不建议现在做的事

- 不要把 stage5 说成“全仓库 SQLite 迁移完成”
- 不要把 lite 说成“所有历史路径都已经零 MySQL”
- 不要在进入 stage6 前再把目标扩成全量旧测试体系重构

## 是否进入阶段 6

建议进入阶段 6。

接下来的重点应该是基于已经收好的 stage5 口径，在没有 MySQL server 的前提下完成 lite 的最终环境级验收，而不是回头重新定义 stage5 的范围。

## 验收记录

执行了以下综合定向回归命令：

```bash
pytest tests/test_lite_stage5_schema_expansion.py tests/test_lite_bootstrap_fixture_path.py tests/test_lite_sqlite_minimal_path.py tests/test_lite_smoke_validation_and_decision.py tests/test_lite_sqlite_high_risk_models.py tests/test_lite_stage4_query_api_matrix.py tests/test_lite_runtime_dependency_boundary.py web/webtest/stage3/test_task01_sqlite_fixture_bridge.py web/webtest/stage3/test_task03_runtime_mysql_specific_sql_cleanup.py web/webtest/stage3/test_task04_lite_migration_baseline.py -q
```

结果：

- `23 passed, 30 warnings`

## 关联结论

- 这份收口只覆盖 lite stage5 的阶段判断
- 它不替代全仓库最终 gate
- 它也不改变当前仓库仍然存在历史 MySQL 兼容路径这一事实
