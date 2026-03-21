# backend_workspace_consolidation_design 任务状态

- 原任务文档：`/Users/leon/projects/snowball-lite/web/docs/task/backend_workspace_consolidation_design.md`
- 归档文档：`/Users/leon/projects/snowball-lite/web/docs/desc/lite_project/03_backend_workspace_consolidation.md`
- 当前状态：已完成
- 当前轮次：round-01
- 当前结论：已完成路径工具、目录收口、文档同步和定向回归；round-01 评审无 finding，报告已通过校验

## 已确认范围

- 迁移目录：`migrations_snowball_dev/`、`migrations_snowball_stg/`、`migrations_snowball_test/`、`migrations_snowball_lite/`
- 后端脚本：`py_script/mysql_to_sqlite_lite_migration.py`
- dev support：`db/dev/init.sql`
- backend/lite 测试：根目录 `tests/` 中明确只服务 lite/backend 的测试

## 暂不迁移

- `xalpha/`
- `extends/`
- `py_script/` 中与 backend workspace 无法明确绑定的脚本
- `tests/test_xalpha_databox_compat.py`
- `tests/test_lite_databox_stage4_coverage.py`

## 当前影响面

- `/Users/leon/projects/snowball-lite/README.md`
- `/Users/leon/projects/snowball-lite/tests/conftest.py`
- `/Users/leon/projects/snowball-lite/web/settings.py`
- `/Users/leon/projects/snowball-lite/web/lite_bootstrap.py`
- `/Users/leon/projects/snowball-lite/web/models/__init__.py`
- `/Users/leon/projects/snowball-lite/web/common/utils/backend_paths.py`
- `/Users/leon/projects/snowball-lite/web/migrations/`
- `/Users/leon/projects/snowball-lite/web/scripts/mysql_to_sqlite_lite_migration.py`
- `/Users/leon/projects/snowball-lite/web/dev_support/db/dev/init.sql`
- `/Users/leon/projects/snowball-lite/web/webtest/lite/`
- `/Users/leon/projects/snowball-lite/web/webtest/lite_runtime_fixtures.py`
- `/Users/leon/projects/snowball-lite/web/docs/环境变量配置指南.md`
- `/Users/leon/projects/snowball-lite/web/docs/系统说明.md`

## 已执行命令

- `sed -n '1,240p' /Users/leon/.codex/skills/team-work/SKILL.md`
- `sed -n '1,520p' web/docs/task/backend_workspace_consolidation_design.md`
- `rg -n "os\\.getcwd\\(|migrations_snowball_(lite|dev|stg|test)|LITE_DB_PATH|bootstrap_lite_database|alembic|migration" web tests xalpha py_script`
- `sed -n '1,260p' web/settings.py`
- `sed -n '1,240p' web/lite_bootstrap.py`
- `sed -n '1,240p' web/models/__init__.py`
- `find . -maxdepth 2 \\( -type d -o -type f \\) | sort | rg '^\\./(migrations_snowball|migrations_snowball_dev|migrations_snowball_stg|migrations_snowball_test|migrations_snowball_lite|py_script|db)(/|$)'`
- `rg -n "\\blite_app\\b|create_app\\(\"lite\"\\)|bootstrap_lite_database\\(|LITE_DB_PATH|LITE_XALPHA_CACHE_DIR" tests/*.py`
- `pytest web/webtest/lite/test_backend_workspace_paths.py -q`
- `python web/scripts/mysql_to_sqlite_lite_migration.py --help`
- `python -m py_compile web/common/utils/backend_paths.py web/settings.py web/lite_bootstrap.py web/models/__init__.py web/scripts/mysql_to_sqlite_lite_migration.py web/webtest/lite_runtime_fixtures.py web/webtest/lite/conftest.py web/webtest/lite/test_backend_workspace_paths.py web/webtest/lite/test_lite_bootstrap_review.py web/webtest/lite/test_lite_stage4_query_api_matrix.py tests/conftest.py`
- `pytest web/webtest/lite web/webtest/stage3/test_task01_sqlite_fixture_bridge.py web/webtest/stage3/test_task04_lite_migration_baseline.py tests/test_lite_databox_stage4_coverage.py tests/test_xalpha_databox_compat.py -q`
- `git add -A README.md tests/conftest.py tests/test_lite_* tests/test_mysql_to_sqlite_business_migration.py db/dev/init.sql py_script/mysql_to_sqlite_lite_migration.py migrations_snowball_dev migrations_snowball_stg migrations_snowball_test migrations_snowball_lite web/common/utils/backend_paths.py web/dev_support web/docs/review/backend_workspace_consolidation_design web/lite_bootstrap.py web/migrations web/models/__init__.py web/scripts web/settings.py web/webtest/lite web/webtest/lite_runtime_fixtures.py 'web/docs/环境变量配置指南.md' 'web/docs/系统说明.md'`
- `git add -u tests`

## 当前 blocker

- 无

## 下一步

- 如需继续推进，可单独补外部脚本 / CI 对旧根目录路径的引用清理
- 如需进入第二阶段，可再单独拆 monorepo 物理重排任务

## Review 结果

- 评审报告：`/Users/leon/projects/snowball-lite/web/docs/review/backend_workspace_consolidation_design/round-01-review.md`
- 评审结论：无 critical/high finding
- 校验结果：`[OK] Report passed validation: /Users/leon/projects/snowball-lite/web/docs/review/backend_workspace_consolidation_design/round-01-review.md`
