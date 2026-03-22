# lite 数据库分层策略（归档）

## 归档状态

- 状态：已完成
- 原任务文档：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/lite_database_layering_strategy.md`
- 对应状态：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/review/lite_database_layering_strategy/task-status.md`
- 对应评审：
  - `round-01-review.md`
  - `round-02-review.md`
- 选定方案：`2 + 1` 分层

## 结论

- lite 继续只保留一个运行模式，不新增 `LiteDevConfig` / `LiteStgConfig` / `LiteTestConfig`
- 长期保留两类业务库：
  - `stable/prod`：`snowball_lite.db`
  - `dev`：`snowball_lite_dev.db`
- `test` 继续使用 pytest 临时 SQLite 文件，不保留长期固定库
- `stg` 只保留按需快照口径，不维护常驻 `lite_stg.db`

## 实际落地

- 已在 `backend_paths.py` 中补充 lite 的长期库默认命名：
  - `snowball_lite.db`
  - `snowball_lite_dev.db`
- 已把 pytest 下的 lite 测试库隔离规则收口到公共 helper
- 已把这层校验接入 `create_app("lite")`，pytest 运行时不能再把 `LITE_DB_PATH` 指到长期 lite 业务库
- 已统一 lite fixtures 的测试库命名，改成 `pytest-` 前缀
- 已更新 README 和环境变量指南，把 `stable/dev/test/stg` 的路径口径写清楚

## 主要代码落点

- `apps/backend/web/common/utils/backend_paths.py`
- `apps/backend/web/settings.py`
- `apps/backend/web/__init__.py`
- `apps/backend/web/webtest/lite_runtime_fixtures.py`
- `apps/backend/web/webtest/conftest.py`
- `apps/backend/web/webtest/lite/test_backend_workspace_paths.py`
- `apps/backend/web/webtest/lite/test_lite_database_layering.py`
- `README.md`
- `apps/backend/web/docs/环境变量配置指南.md`

## 启动与测试口径

### stable/prod

- 默认路径：`apps/backend/web/data/lite_runtime/snowball_lite.db`
- 用于长期正式业务数据
- 默认不作为开发实验库

### dev

- 推荐路径：`apps/backend/web/data/lite_runtime/snowball_lite_dev.db`
- 用于本地开发、联调、手工验证

### test

- 默认路径：pytest 临时目录中的 `pytest-*.db`
- 默认测试命令不能连接长期 lite 业务库

### stg

- 不维护长期常驻库
- 只在发版前演练或数据检查时，从 stable 派生临时快照，例如 `snowball_lite_stg_YYYYMMDD.db`

## 验证结果

- `pytest apps/backend/web/webtest/lite/test_lite_database_layering.py -q` -> `5 passed`
- `pytest apps/backend/web/webtest/lite/test_backend_workspace_paths.py -q` -> `6 passed`
- `pytest apps/backend/web/webtest/stage3/test_task01_sqlite_fixture_bridge.py -q` -> `1 passed, 1 warning`
- `pytest apps/backend/web/webtest/lite/test_lite_stage5_schema_expansion.py::test_lite_bootstrap_stage5_builds_core_schema -q` -> `1 passed, 1 warning`
- `pytest apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py -q` -> `6 passed, 1 warning`

## Checklist

- [x] 明确 lite 采用 `2 + 1` 分层，不新增 lite 多环境矩阵
- [x] 固定 stable/prod 的默认 SQLite 命名
- [x] 固定 dev 的推荐 SQLite 命名
- [x] 明确 test 继续使用 pytest 临时 SQLite
- [x] 明确 stg 只保留按需快照口径
- [x] 更新 README 中的 lite 数据库分层说明
- [x] 更新环境变量指南中的 lite 数据库分层说明
- [x] 增加“pytest 禁止连接长期 lite 业务库”的公共校验
- [x] 把校验接入 `create_app("lite")` 的 pytest 运行入口
- [x] 调整 lite runtime fixtures 的测试库命名
- [x] 调整 stage3 lite webtest fixtures 的测试库命名
- [x] 补长期库命名回归测试
- [x] 补测试库隔离回归测试
- [x] 完成 review-fix-rereview 并落状态文档

## 保留边界

- 这次完成的是 lite 的数据库分层和测试隔离，不等于把历史 `dev/stg/test` MySQL 口径移除
- `stg` 仍然只是约定，不包含自动快照生成与恢复工具
- 如果后面新增了不经过 `create_app(...)` 的 lite 启动方式，测试库隔离规则需要额外接入
