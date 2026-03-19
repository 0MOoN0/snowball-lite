# lite_stage3 Requirement Summary

## 结论

第三阶段目标已在选定范围内完成，结论是：`继续推进`，但只建议进入“更大一点、仍然受控的 SQLite 覆盖面”，不建议马上按“全仓库 SQLite 化”去做。

## 本阶段已验证通过

- `web/webtest` 已增加 stage3 专用 SQLite fixture，不再依赖 MySQL server，也不会走 `CREATE DATABASE IF NOT EXISTS ...`
- 两条业务链路都已在 SQLite 下完成集成验证：
  - `AssetService.init_fund_asset_data`
  - `GridTransactionAnalysisService.trade_analysis`
- 两处会直接挡住 stage3 的 MySQL 专有 SQL 已收口成方言安全分支：
  - `show variables like 'long_query_time'`
  - `SHOW TABLES LIKE 'apscheduler_jobs'`
- 已新增 `migrations_snowball_lite` 和 `bootstrap_lite_database`，lite 不再只有 `db.create_all()` 一条初始化口径
- 自动化验证已覆盖：
  - `pytest web/webtest/stage3 -q`
  - `pytest tests/test_lite_sqlite_minimal_path.py tests/test_lite_sqlite_high_risk_models.py tests/test_lite_bootstrap_review.py -q`

## 仍然保留的 blocker

- stage3 的 SQLite bridge 目前只覆盖选定测试，不代表整个 `web/webtest/` 都已经脱离 MySQL
- `migrations_snowball_lite` 目前是 stage3 核心表基线，不是完整 lite schema
- 仓库里其他 MySQL 相关路径还没做系统排查，这轮只处理了会直接卡住 stage3 的那一批

## 不建议现在做的事

- 不建议立刻把全部旧测试统一切到 SQLite
- 不建议现在重写 dev/stg/test/prod 的历史迁移
- 不建议把“stage3 通过”误读成“全仓库 SQLite 已经可用”

## 是否进入下一阶段

建议进入下一阶段，但范围要控制住：

1. 继续把更多高价值、低外部依赖的旧测试接到 `lite_webtest_*` fixtures
2. 扩展 `migrations_snowball_lite`，让更多 router/service 能走同一套 bootstrap
3. 按运行路径继续清理剩余 MySQL 专有 SQL，而不是一次性全仓库大扫除

## Review

- review report: `docs/review/team-work/lite_stage3/round-01-review.md`
- recommendation: `continue_with_scoped_sqlite_expansion`
