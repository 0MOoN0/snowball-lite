# 任务 01：零 MySQL 环境下的启动与初始化验收（归档）

## 完成状态

- 已完成
- 结论：lite 主线路径的 app 创建、SQLite bootstrap、fixture 初始化和最小启动链路已经不再依赖 MySQL server

## 实际改动

- 在 [tests/test_lite_bootstrap_review.py](/Users/leon/projects/snowball-lite/tests/test_lite_bootstrap_review.py) 增补了零 MySQL 启动验证
- 新增 [web/lite_application.py](/Users/leon/projects/snowball-lite/web/lite_application.py)，把 lite app 创建和 `bootstrap_lite_database(...)` 固定成正式入口
- 在 [web/lite_bootstrap.py](/Users/leon/projects/snowball-lite/web/lite_bootstrap.py) 补了 SQLite schema 就绪判断和 bootstrap 锁，保证 Gunicorn / 重复导入下也是幂等的
- 补了 [web/gunicorn_lite.config.py](/Users/leon/projects/snowball-lite/web/gunicorn_lite.config.py) 作为 lite 专用单 worker Gunicorn 配置

## 验证结果

- 启动 / 初始化固定命令：
  `python -m pytest tests/test_lite_bootstrap_review.py tests/test_lite_bootstrap_fixture_path.py tests/test_lite_sqlite_minimal_path.py tests/test_lite_stage5_schema_expansion.py web/webtest/stage3/test_task01_sqlite_fixture_bridge.py web/webtest/stage3/test_task04_lite_migration_baseline.py -q`
  结果：`12 passed, 1 warning`
- 其中重点覆盖了：
  - 阻断 `pymysql`、`mysql`、`MySQLdb`、`redis`、`apscheduler`、`dramatiq` 等可选依赖后，`create_app("lite")` 和 `bootstrap_lite_database(...)` 仍能通过
  - lite fixture、最小 SQLite 链路、stage5 schema 和 migration baseline 都能重复通过
- lite Gunicorn 配置检查：
  `python -m gunicorn.app.wsgiapp --check-config -c web/gunicorn_lite.config.py web.lite_application:app`
  在 lite 环境变量下通过

## 本任务结论

- lite 主线路径已经形成正式的 SQLite 启动入口
- 零 MySQL 环境下不会因为隐式 MySQL import、默认 URL 或建库逻辑而阻断启动
- 这一组命令已经可以作为阶段 6 后续业务回归和最终收口的固定前置口径
