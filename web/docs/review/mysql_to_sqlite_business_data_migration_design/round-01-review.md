# Staged Code Review Report

- Generated At: `2026-03-20T18:45:49+08:00`
- Reviewer: `Codex`
- Repo Root: `/Users/leon/projects/snowball-lite`
- HEAD: `4f5b650b2ca9a1685d6222480a8be271886f36d2`
- Snapshot Source: `/private/tmp/codex-staged-review-snowball-lite/snapshot.json`

## Scope

- Staged file count: `8`
- Added lines: `1530`
- Removed lines: `0`
- Diff artifact: `/private/tmp/codex-staged-review-snowball-lite/staged_diff.patch`

### Staged Files

- `migrations_snowball_lite/versions/lite_stage3_baseline.py`
- `py_script/mysql_to_sqlite_lite_migration.py`
- `tests/test_lite_stage5_schema_expansion.py`
- `tests/test_mysql_to_sqlite_business_migration.py`
- `web/docs/review/mysql_to_sqlite_business_data_migration_design/task-status.md`
- `web/lite_bootstrap.py`
- `web/services/migration/__init__.py`
- `web/services/migration/mysql_to_sqlite_business_migration_service.py`

## Review Protocol (TDD + Evidence)

1. Write a failing test before claiming any business-logic defect.
2. Treat business and production code as read-only during review unless the user explicitly requests a fix.
3. Keep review test edits inside repository `test/` paths and write them to commit-ready repository quality.
4. Run targeted commands and record exact outputs.
5. Keep each finding mapped to a test case and file scope.
6. Attach evidence snippets that can be reproduced by another engineer.
7. If no findings exist, provide regression command evidence anyway.

## Fix Verification

- Previous Findings Source: 首轮评审，当前任务没有历史 finding 需要回归确认
- Verification Scope: 新增的 lite baseline 扩表、迁移 service、CLI 入口和本地回归测试
- Verification Commands: `pytest tests/test_mysql_to_sqlite_business_migration.py tests/test_lite_stage5_schema_expansion.py tests/test_lite_bootstrap_fixture_path.py -q`
- Result: 通过
- Notes: 这一步主要确认 staged 变更自己补进去的 schema、迁移和测试链路没有立即回归

## New Risk Scan

- Scan Scope: `migrations_snowball_lite/versions/lite_stage3_baseline.py`、`web/lite_bootstrap.py`、`web/services/migration/mysql_to_sqlite_business_migration_service.py`、`py_script/mysql_to_sqlite_lite_migration.py` 和配套测试
- Risk Focus Areas: `tb_amount_trade_analysis_data` 是否真正纳入 baseline；远程源库断线重试是否只重试可恢复错误；`system_settings` 的 runtime key 是否被覆盖；CLI 是否能直接从仓库根目录启动
- Commands: `pytest tests/test_mysql_to_sqlite_business_migration.py tests/test_lite_stage5_schema_expansion.py tests/test_lite_bootstrap_fixture_path.py -q`；`pytest tests/test_lite_bootstrap_review.py::test_lite_bootstrap_survives_blocked_mysql_and_optional_infra_packages -q`；`python py_script/mysql_to_sqlite_lite_migration.py --help`
- Result: 通过，当前 staged diff 没扫出需要开新 finding 的逻辑问题
- New Findings: 0
- Residual Risk: 自动化验证目前只覆盖了 SQLite 源库模拟，真实远程 MySQL stg 还需要在有网络和凭据的环境里至少跑一次 `--dry-run`

## Findings Summary

| ID | Severity | File:Line | Finding | Risk | Test Before Fix | Evidence Command | Recommendation | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None | none | `-` | 本轮未发现需要阻断合并的新增问题 | 当前风险主要是缺少真实 stg 远端演练 | `-` | `pytest ...` | 保持实现不变，后续补一次 stg dry-run | Closed |

## No Findings Evidence (Use only when there are no findings)

- Command Set: `pytest tests/test_mysql_to_sqlite_business_migration.py tests/test_lite_stage5_schema_expansion.py tests/test_lite_bootstrap_fixture_path.py -q`；`pytest tests/test_lite_bootstrap_review.py::test_lite_bootstrap_survives_blocked_mysql_and_optional_infra_packages -q`；`python py_script/mysql_to_sqlite_lite_migration.py --help`
- Evidence: 迁移链路测试 `6 passed`，受限依赖 bootstrap 回归 `1 passed`，CLI `--help` 可直接输出完整参数说明且退出码为 0
- Residual Risk: 还没有对真实远程 MySQL stg 跑端到端 dry-run；`truncate-target` 在复杂半成品目标库上的重跑策略只做了设计约束，没有额外自动化覆盖

## Evidence Appendix

```text
$ pytest tests/test_mysql_to_sqlite_business_migration.py tests/test_lite_stage5_schema_expansion.py tests/test_lite_bootstrap_fixture_path.py -q
......                                                                   [100%]
6 passed, 2 warnings in 2.52s

$ pytest tests/test_lite_bootstrap_review.py::test_lite_bootstrap_survives_blocked_mysql_and_optional_infra_packages -q
.                                                                        [100%]
1 passed, 1 warning in 4.07s

$ python py_script/mysql_to_sqlite_lite_migration.py --help
usage: mysql_to_sqlite_lite_migration.py [-h] --source-url SOURCE_URL ...
将业务库数据按 lite baseline 迁移到新的 SQLite 文件

$ git diff --cached --stat
.../versions/lite_stage3_baseline.py               |   7 +
py_script/mysql_to_sqlite_lite_migration.py        | 141 +++
tests/test_lite_stage5_schema_expansion.py         |   1 +
tests/test_mysql_to_sqlite_business_migration.py   | 359 ++++++++
.../task-status.md                                 |  34 +
web/lite_bootstrap.py                              |   1 +
web/services/migration/__init__.py                 |  15 +
.../mysql_to_sqlite_business_migration_service.py  | 972 +++++++++++++++++++++
8 files changed, 1530 insertions(+)
```
