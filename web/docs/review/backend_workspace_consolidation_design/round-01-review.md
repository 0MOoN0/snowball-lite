# Staged Code Review Report

- Generated At: `2026-03-20T20:56:23+08:00`
- Reviewer: `Codex`
- Repo Root: `/Users/leon/projects/snowball-lite`
- HEAD: `d78fbd19bc4bd237e831404e3bcd959145a464c6`
- Snapshot Source: `/private/tmp/codex-staged-review-1774011368/snapshot.json`

## Scope

- Staged file count: `123`
- Added lines: `319`
- Removed lines: `129`
- Diff artifact: `/private/tmp/codex-staged-review-1774011368/staged_diff.patch`

### Staged Files

- `README.md`
- `tests/conftest.py`
- `web/common/utils/backend_paths.py`
- `web/dev_support/db/dev/init.sql`
- `web/docs/review/backend_workspace_consolidation_design/task-status.md`
- `"web/docs/\347\216\257\345\242\203\345\217\230\351\207\217\351\205\215\347\275\256\346\214\207\345\215\227.md"`
- `"web/docs/\347\263\273\347\273\237\350\257\264\346\230\216.md"`
- `web/lite_bootstrap.py`
- `web/migrations/dev/README`
- `web/migrations/dev/alembic.ini`
- `web/migrations/dev/env.py`
- `web/migrations/dev/script.py.mako`
- `web/migrations/dev/sql/migration_sql.sql`
- `"web/migrations/dev/versions/031f14a770ba_\346\267\273\345\212\240\350\265\204\344\272\247\345\210\253\345\220\215\345\212\237\350\203\275.py"`
- `web/migrations/dev/versions/05618f79e538_update_record_model.py`
- `"web/migrations/dev/versions/0680bf732fe0_\345\210\233\345\273\272tb_asset_exchange_fund\350\241\250.py"`
- `web/migrations/dev/versions/08dc0aac9a87_first_migrate.py`
- `web/migrations/dev/versions/167b29892f80_update_notification_model_comments.py`
- `"web/migrations/dev/versions/1dcbb2edf6db_\351\207\215\345\221\275\345\220\215\350\241\250_tb_transaction_analysis_data_tb_.py"`
- `"web/migrations/dev/versions/20f8d5856f04_\346\236\232\344\270\276\346\225\264\345\220\210\350\277\201\347\247\273.py"`
- `web/migrations/dev/versions/22884573bf0c_add_trade_reference_model_verify.py`
- `"web/migrations/dev/versions/2d0a239fa54a_\351\207\215\345\221\275\345\220\215_index_base_\350\241\250\347\232\204_status_\345\255\227\346\256\265\344\270\272_index_.py"`
- `"web/migrations/dev/versions/342798caac94_\346\243\200\346\237\245gridtradeanalysisdata\346\250\241\345\236\213\345\217\230\346\233\264.py"`
- `web/migrations/dev/versions/3f5d97292b88_update_system_settings_model.py`
- `"web/migrations/dev/versions/41b9b658e05a_\351\207\215\346\236\204\344\270\272\350\201\224\345\220\210\350\241\250\347\273\247\346\211\277.py"`
- `web/migrations/dev/versions/43bf5f858a09_add_trade_reference_model.py`
- `web/migrations/dev/versions/43c22021be0e_add_annualized_return_to_trade_analysis_.py`
- `"web/migrations/dev/versions/4ed7a9b69552_\346\211\213\345\212\250\350\256\276\347\275\256up_sold_percent\345\222\214down_bought_.py"`
- `"web/migrations/dev/versions/5576cdcf3211_\344\277\256\346\224\271indexbase\345\255\227\346\256\265nullable\345\261\236\346\200\247.py"`
- `"web/migrations/dev/versions/5bc10b80e688_\350\241\250\345\220\215\344\277\256\346\224\271_tb_stock_index_tb_index_stock.py"`
- `web/migrations/dev/versions/67d15a8a9cd8_add_template_key_field_to_notification_.py`
- `"web/migrations/dev/versions/6d30bad3c539_\346\243\200\346\237\245\346\250\241\345\236\213\345\217\230\346\233\264.py"`
- `"web/migrations/dev/versions/7c3a91f183ac_\345\210\233\345\273\272tb_amount_trade_analysis_data\350\241\250.py"`
- `"web/migrations/dev/versions/9c5ebcd1456e_\351\207\215\345\221\275\345\220\215assetetf\344\270\272assetfundetf_.py"`
- `web/migrations/dev/versions/aeda6ed6bb49_update_trade_reference_group_type_.py`
- `"web/migrations/dev/versions/b36b025a51aa_\346\267\273\345\212\240asset_code_asset_short_code\345\222\214asset_.py"`
- `"web/migrations/dev/versions/caf25000de4f_\346\267\273\345\212\240\345\237\272\351\207\221\346\214\207\346\225\260\345\205\263\350\201\224\345\212\237\350\203\275.py"`
- `"web/migrations/dev/versions/d5473a55937d_\345\260\206dividend_.py"`
- `web/migrations/dev/versions/dd8711649dd9_add_template_key_to_notification.py`
- `web/migrations/dev/versions/e6283c8f40ae_update_notification_model.py`
- `web/migrations/dev/versions/e77d0b0f5f9e_update_notification_log_traceback_info_.py`
- `"web/migrations/dev/versions/f1562e274c1e_\346\267\273\345\212\240index\346\250\241\345\236\213\347\232\204investment_.py"`
- `"web/migrations/dev/versions/f8957aceae8e_\344\277\256\345\244\215\347\273\247\346\211\277\345\205\263\347\263\273\345\222\214\345\255\227\346\256\265\347\261\273\345\236\213.py"`
- `web/migrations/lite/README`
- `web/migrations/lite/alembic.ini`
- `web/migrations/lite/env.py`
- `web/migrations/lite/script.py.mako`
- `web/migrations/lite/versions/lite_stage3_baseline.py`
- `web/migrations/stg/README`
- `web/migrations/stg/alembic.ini`
- `web/migrations/stg/env.py`
- `web/migrations/stg/script.py.mako`
- `web/migrations/stg/versions/02047ee4b143_step2_add_constraints_migrate_data.py`
- `web/migrations/stg/versions/14585fb3eb91_update_notification_model.py`
- `web/migrations/stg/versions/15f1af824347_update_notification_log_traceback_info_.py`
- `"web/migrations/stg/versions/2293dd4539c9_\346\267\273\345\212\240\345\237\272\351\207\221\346\214\207\346\225\260\345\205\263\350\201\224\345\212\237\350\203\275.py"`
- `web/migrations/stg/versions/2cc4ac7aff4f_update_notification_model_comments.py`
- `web/migrations/stg/versions/3d2b55717c58_sync_trade_analysis_data_model_changes.py`
- `"web/migrations/stg/versions/4ed7a9b69552_\346\211\213\345\212\250\350\256\276\347\275\256up_sold_percent\345\222\214down_bought_.py"`
- `web/migrations/stg/versions/51d079f0edee_add_trade_reference_model.py`
- `"web/migrations/stg/versions/528f79f43be0_\345\210\233\345\273\272tb_asset_exchange_fund\350\241\250.py"`
- `"web/migrations/stg/versions/61ba63e90514_\351\207\215\345\221\275\345\220\215_index_base_\350\241\250\347\232\204_status_\345\255\227\346\256\265\344\270\272_index_.py"`
- `"web/migrations/stg/versions/674d60350c6f_\351\207\215\346\236\204\344\270\272\350\201\224\345\220\210\350\241\250\347\273\247\346\211\277.py"`
- `web/migrations/stg/versions/679cbda7e843_step3_rename_tables_create_new.py`
- `web/migrations/stg/versions/6c515d6b0dd0_add_template_key_to_notification.py`
- `web/migrations/stg/versions/6ef5da7324fc_stg_first_migrate.py`
- `"web/migrations/stg/versions/70d9754c5650_\346\267\273\345\212\240\350\265\204\344\272\247\345\210\253\345\220\215\345\212\237\350\203\275.py"`
- `"web/migrations/stg/versions/7b8f16b99fc4_\346\267\273\345\212\240index\346\250\241\345\236\213\347\232\204investment_.py"`
- `"web/migrations/stg/versions/8487ea92cb66_\351\207\215\345\221\275\345\220\215assetetf\344\270\272assetfundetf_.py"`
- `"web/migrations/stg/versions/95531764f175_\344\277\256\346\224\271indexbase\345\255\227\346\256\265nullable\345\261\236\346\200\247.py"`
- `"web/migrations/stg/versions/957e99fa39ba_\345\220\214\346\255\245gridtradeanalysisdata\346\250\241\345\236\213\345\217\230\346\233\264.py"`
- `"web/migrations/stg/versions/99c64d2ea65b_\346\236\232\344\270\276\346\225\264\345\220\210\350\277\201\347\247\273.py"`
- `web/migrations/stg/versions/b15c76ae445d_update_seystem_settings_model.py`
- `web/migrations/stg/versions/c636a53b2986_add_trade_reference_model_verify.py`
- `web/migrations/stg/versions/d41d8cd98f00_step1_modify_fields.py`
- `"web/migrations/stg/versions/dee37ca3ba3a_\346\267\273\345\212\240asset_code_asset_short_code\345\222\214asset_.py"`
- `"web/migrations/stg/versions/e0bea86ab995_\350\241\250\345\220\215\344\277\256\346\224\271_tb_stock_index_tb_index_stock.py"`
- `web/migrations/stg/versions/e70063591675_update_record_model.py`
- `web/migrations/stg/versions/ff7804bc17cc_update_trade_reference_group_type_.py`
- `web/migrations/test/README`
- `web/migrations/test/alembic.ini`
- `web/migrations/test/env.py`
- `web/migrations/test/script.py.mako`
- `"web/migrations/test/versions/008f022f505b_\350\241\250\345\220\215\344\277\256\346\224\271_tb_stock_index_tb_index_stock.py"`
- `web/migrations/test/versions/048d6edf7ea9_add_trade_reference_model_verify.py`
- `web/migrations/test/versions/0b23d505ef04_update_record_model.py`
- `"web/migrations/test/versions/2d42af080195_\346\267\273\345\212\240index\346\250\241\345\236\213\347\232\204investment_.py"`
- `"web/migrations/test/versions/314aa46271a8_\345\210\233\345\273\272tb_asset_exchange_fund\350\241\250.py"`
- `web/migrations/test/versions/457fba4b9e32_add_trade_reference_model.py`
- `web/migrations/test/versions/4c2bc99e0f9b_initial_baseline_for_test_environment.py`
- `web/migrations/test/versions/4c4b4b7b3143_add_template_key_to_notification.py`
- `"web/migrations/test/versions/4ed7a9b69552_\346\211\213\345\212\250\350\256\276\347\275\256up_sold_percent\345\222\214down_bought_.py"`
- `"web/migrations/test/versions/51d513707b7b_\345\220\214\346\255\245gridtradeanalysisdata\346\250\241\345\236\213\345\217\230\346\233\264.py"`
- `"web/migrations/test/versions/5b2472955987_\346\236\232\344\270\276\346\225\264\345\220\210\350\277\201\347\247\273.py"`
- `web/migrations/test/versions/5d3db400c055_sync_trade_analysis_data_model_changes.py`
- `"web/migrations/test/versions/817d8365c3f4_\351\207\215\345\221\275\345\220\215assetetf\344\270\272assetfundetf_.py"`
- `"web/migrations/test/versions/889f7e5d0628_\344\277\256\346\224\271indexbase\345\255\227\346\256\265nullable\345\261\236\346\200\247.py"`
- `web/migrations/test/versions/94d0e7547547_update_notification_model.py`
- `"web/migrations/test/versions/989327955f59_\345\220\214\346\255\245dev\347\216\257\345\242\203\350\277\201\347\247\273\345\210\260test\347\216\257\345\242\203.py"`
- `"web/migrations/test/versions/bd0c465da9d0_\346\267\273\345\212\240asset_code_asset_short_code\345\222\214asset_.py"`
- `"web/migrations/test/versions/c74d79c1a6d7_\351\207\215\346\236\204\344\270\272\350\201\224\345\220\210\350\241\250\347\273\247\346\211\277.py"`
- `"web/migrations/test/versions/cf2693bcc9dc_\346\267\273\345\212\240\350\265\204\344\272\247\345\210\253\345\220\215\345\212\237\350\203\275.py"`
- `web/migrations/test/versions/d9373dde86cc_update_trade_reference_group_type_.py`
- `web/migrations/test/versions/ded7220db81a_update_notification_model_comments.py`
- `"web/migrations/test/versions/e98236b10fb6_\351\207\215\345\221\275\345\220\215_index_base_\350\241\250\347\232\204_status_\345\255\227\346\256\265\344\270\272_index_.py"`
- `"web/migrations/test/versions/ee296701a7a8_\346\267\273\345\212\240\345\237\272\351\207\221\346\214\207\346\225\260\345\205\263\350\201\224\345\212\237\350\203\275.py"`
- `web/models/__init__.py`
- `web/scripts/mysql_to_sqlite_lite_migration.py`
- `web/settings.py`
- `web/webtest/lite/conftest.py`
- `web/webtest/lite/test_backend_workspace_paths.py`
- `web/webtest/lite/test_lite_bootstrap_fixture_path.py`
- `web/webtest/lite/test_lite_bootstrap_review.py`
- `web/webtest/lite/test_lite_grid_percent_chart.py`
- `web/webtest/lite/test_lite_real_databox_validation.py`
- `web/webtest/lite/test_lite_runtime_dependency_boundary.py`
- `web/webtest/lite/test_lite_smoke_validation_and_decision.py`
- `web/webtest/lite/test_lite_sqlite_high_risk_models.py`
- `web/webtest/lite/test_lite_sqlite_minimal_path.py`
- `web/webtest/lite/test_lite_stage4_query_api_matrix.py`
- `web/webtest/lite/test_lite_stage5_schema_expansion.py`
- `web/webtest/lite/test_mysql_to_sqlite_business_migration.py`
- `web/webtest/lite_runtime_fixtures.py`

## Review Protocol (TDD + Evidence)

1. Write a failing test before claiming any business-logic defect.
2. Treat business and production code as read-only during review unless the user explicitly requests a fix.
3. Keep review test edits inside repository `test/` paths and write them to commit-ready repository quality.
4. Run targeted commands and record exact outputs.
5. Keep each finding mapped to a test case and file scope.
6. Attach evidence snippets that can be reproduced by another engineer.
7. If no findings exist, provide regression command evidence anyway.

## Fix Verification

- Previous Findings Source: `None`
- Verification Scope: `web/webtest/lite/`, `web/webtest/stage3/test_task01_sqlite_fixture_bridge.py`, `web/webtest/stage3/test_task04_lite_migration_baseline.py`
- Verification Commands: `pytest web/webtest/lite web/webtest/stage3/test_task01_sqlite_fixture_bridge.py web/webtest/stage3/test_task04_lite_migration_baseline.py tests/test_lite_databox_stage4_coverage.py tests/test_xalpha_databox_compat.py -q`
- Result: Passed
- Notes: `50 passed, 1 skipped`

## New Risk Scan

- Scan Scope: `web/common/utils/backend_paths.py`, `web/settings.py`, `web/lite_bootstrap.py`, `web/models/__init__.py`, `web/scripts/mysql_to_sqlite_lite_migration.py`, `web/migrations/*`, `web/webtest/lite/*`, `README.md`, `web/docs/环境变量配置指南.md`, `web/docs/系统说明.md`
- Risk Focus Areas: backend path resolution, fixture relocation, migration directory mapping, and command/documentation path updates
- Commands: `python -m py_compile web/common/utils/backend_paths.py web/settings.py web/lite_bootstrap.py web/models/__init__.py web/scripts/mysql_to_sqlite_lite_migration.py web/webtest/lite_runtime_fixtures.py web/webtest/lite/conftest.py web/webtest/lite/test_backend_workspace_paths.py web/webtest/lite/test_lite_bootstrap_review.py web/webtest/lite/test_lite_stage4_query_api_matrix.py tests/conftest.py`; `python web/scripts/mysql_to_sqlite_lite_migration.py --help`; `pytest web/webtest/lite/test_backend_workspace_paths.py web/webtest/lite/test_lite_bootstrap_review.py -q`
- Result: Passed
- New Findings: `None`
- Residual Risk: Any external script or CI job still pointing at root-level `migrations_snowball_*` or `py_script/mysql_to_sqlite_lite_migration.py` will need a follow-up update outside this staged diff.

## Findings Summary

| Status | Severity | File:Line | Finding | Risk | Test Before Fix | Evidence Command | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Closed | N/A | N/A | No findings | N/A | N/A | `pytest web/webtest/lite web/webtest/stage3/test_task01_sqlite_fixture_bridge.py web/webtest/stage3/test_task04_lite_migration_baseline.py tests/test_lite_databox_stage4_coverage.py tests/test_xalpha_databox_compat.py -q` | Keep the new backend workspace paths and update any external references that still use the old root-level migration and script paths. |

## No Findings Evidence (Use only when there are no findings)

- Command Set: `python -m py_compile web/common/utils/backend_paths.py web/settings.py web/lite_bootstrap.py web/models/__init__.py web/scripts/mysql_to_sqlite_lite_migration.py web/webtest/lite_runtime_fixtures.py web/webtest/lite/conftest.py web/webtest/lite/test_backend_workspace_paths.py web/webtest/lite/test_lite_bootstrap_review.py web/webtest/lite/test_lite_stage4_query_api_matrix.py tests/conftest.py`; `python web/scripts/mysql_to_sqlite_lite_migration.py --help`; `pytest web/webtest/lite web/webtest/stage3/test_task01_sqlite_fixture_bridge.py web/webtest/stage3/test_task04_lite_migration_baseline.py tests/test_lite_databox_stage4_coverage.py tests/test_xalpha_databox_compat.py -q`
- Evidence: `50 passed, 1 skipped` from the targeted regression run; `python web/scripts/mysql_to_sqlite_lite_migration.py --help` returned the expected CLI usage and exited `0`
- Residual Risk: External callers still using old root-level paths need a separate compatibility update if they exist outside this repo's staged scope

## Evidence Appendix

```text
$ python -m py_compile web/common/utils/backend_paths.py web/settings.py web/lite_bootstrap.py web/models/__init__.py web/scripts/mysql_to_sqlite_lite_migration.py web/webtest/lite_runtime_fixtures.py web/webtest/lite/conftest.py web/webtest/lite/test_backend_workspace_paths.py web/webtest/lite/test_lite_bootstrap_review.py web/webtest/lite/test_lite_stage4_query_api_matrix.py tests/conftest.py
$
$ python web/scripts/mysql_to_sqlite_lite_migration.py --help
usage: mysql_to_sqlite_lite_migration.py [-h] --source-url SOURCE_URL
                                         [--target-sqlite TARGET_SQLITE]
...

$ pytest web/webtest/lite web/webtest/stage3/test_task01_sqlite_fixture_bridge.py web/webtest/stage3/test_task04_lite_migration_baseline.py tests/test_lite_databox_stage4_coverage.py tests/test_xalpha_databox_compat.py -q
50 passed, 1 skipped in 44.73s
```
