# Staged Code Review Report

- Generated At: `2026-03-19T10:15:11+08:00`
- Reviewer: `Codex`
- Repo Root: `/Users/leon/projects/snowball-lite`
- HEAD: `b775da48bc2ed3b90cf7d7dd7a421d360975a154`
- Snapshot Source: `/private/tmp/codex-staged-review-1773886507/snapshot.json`

## Scope

- Staged file count: `16`
- Added lines: `1051`
- Removed lines: `34`
- Diff artifact: `/private/tmp/codex-staged-review-1773886507/staged_diff.patch`

### Staged Files

- `migrations_snowball_lite/README`
- `migrations_snowball_lite/alembic.ini`
- `migrations_snowball_lite/env.py`
- `migrations_snowball_lite/script.py.mako`
- `migrations_snowball_lite/versions/lite_stage3_baseline.py`
- `pytest.ini`
- `web/lite_bootstrap.py`
- `web/models/__init__.py`
- `web/scheduler/__init__.py`
- `web/webtest/conftest.py`
- `web/webtest/stage3/test_task01_sqlite_fixture_bridge.py`
- `web/webtest/stage3/test_task02_asset_service_sqlite.py`
- `web/webtest/stage3/test_task02_grid_transaction_analysis_sqlite.py`
- `web/webtest/stage3/test_task03_runtime_mysql_specific_sql_cleanup.py`
- `web/webtest/stage3/test_task04_lite_migration_baseline.py`
- `web/webtest/test_base.py`

## Review Protocol (TDD + Evidence)

1. Write a failing test before claiming any business-logic defect.
2. Treat business and production code as read-only during review unless the user explicitly requests a fix.
3. Keep review test edits inside repository `test/` paths and write them to commit-ready repository quality.
4. Run targeted commands and record exact outputs.
5. Keep each finding mapped to a test case and file scope.
6. Attach evidence snippets that can be reproduced by another engineer.
7. If no findings exist, provide regression command evidence anyway.

## Fix Verification

- Previous Findings Source: 首轮实现，没有历史 review finding；本轮直接把 stage3 新增改动当作待验证范围。
- Verification Scope: `migrations_snowball_lite`、`web/lite_bootstrap.py`、`web/webtest` stage3 fixture 与专项集成测试、SQLite 方言兼容分支。
- Verification Commands: `pytest web/webtest/stage3 -q`
- Result: 通过。stage3 专项回归 6 项全部通过，没有复现 SQLite bridge、业务链路、方言 SQL、migration baseline 的回归问题。
- Notes: 重点看了三件事：SQLite fixture 是否真的脱离 MySQL、`AssetService` / `GridTransactionAnalysisService` 是否能在 SQLite 下落库、lite bootstrap 是否能重复执行并保留 Alembic 版本号。

## New Risk Scan

- Scan Scope: 当前 staged diff 的 16 个文件，含 migration baseline、运行时代码、fixture、测试和 pytest marker 改动。
- Risk Focus Areas: SQLite bootstrap 是否影响既有 lite 回归；MySQL 分支是否被误伤；stage3 baseline 是否只覆盖文档约定的最小集合；新增 fixture 是否会串扰原有 MySQL webtest。
- Commands: `pytest tests/test_lite_sqlite_minimal_path.py tests/test_lite_sqlite_high_risk_models.py tests/test_lite_bootstrap_review.py -q`
- Result: 通过。既有 lite 回归 6 项全部通过，说明 `LiteConfig -> migrations_snowball_lite` 映射和新的 bootstrap helper 没把现有最小链路打坏。
- New Findings: 无。
- Residual Risk: `migrations_snowball_lite` 当前是 stage3 范围基线，不是全量 lite schema；如果后续要把更多 router/service 纳入 lite 默认启动或默认回归，需要继续扩表并补对应迁移测试。

## Findings Summary

| ID | Severity | File:Line | Finding | Risk | Test Before Fix | Evidence Command | Recommendation | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None | None | None | 本轮 staged scope 未发现需要升级成 defect 的问题。 | 低 | 已有 stage3 回归与既有 lite 回归覆盖 | `pytest web/webtest/stage3 -q` / `pytest tests/test_lite_sqlite_minimal_path.py tests/test_lite_sqlite_high_risk_models.py tests/test_lite_bootstrap_review.py -q` | 继续进入 requirement summary 与状态回写 | Closed |

## No Findings Evidence (Use only when there are no findings)

- Command Set: `pytest web/webtest/stage3 -q`; `pytest tests/test_lite_sqlite_minimal_path.py tests/test_lite_sqlite_high_risk_models.py tests/test_lite_bootstrap_review.py -q`
- Evidence: 两组命令都通过；第一组覆盖 stage3 新增 SQLite fixture、业务链路验证、MySQL 专有 SQL 清理和 migration baseline，第二组覆盖既有 lite 最小链路、高风险模型和可选基础设施隔离回归。
- Residual Risk: 当前 review 证明的是 stage3 选定范围可用，不等于全仓库 webtest 都已经脱离 MySQL，也不等于 lite baseline 已覆盖所有业务表。

## Evidence Appendix

```text
pytest web/webtest/stage3 -q
......                                                                   [100%]
6 passed, 16 warnings in 0.78s

pytest tests/test_lite_sqlite_minimal_path.py tests/test_lite_sqlite_high_risk_models.py tests/test_lite_bootstrap_review.py -q
......                                                                   [100%]
6 passed, 2 warnings in 5.00s
```
