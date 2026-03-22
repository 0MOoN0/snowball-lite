# 任务 3：继续收口 lite 主线路径里的 MySQL 专有逻辑（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 5 任务 3 MySQL 专有逻辑收口（原 task 文档已清理）
- 当前状态：已完成
- 代码审查：已完成

## 实际结果

- `web/models/__init__.py` 和 `web/scheduler/__init__.py` 已把 `pymysql` 改成可选导入，lite 路径不再把安装 `pymysql` 当成前提
- 两处模块都新增了 `_mysql_operational_errors()`，MySQL 异常捕获现在只在 `pymysql` 可用时才追加 MySQL 专属异常类型
- `web/scheduler/__init__.py` 的 APScheduler 表检查已经改成 SQLAlchemy inspector，不再对 SQLite 执行 `SHOW TABLES LIKE`
- 已补充 `web/webtest/stage3/test_task03_runtime_mysql_specific_sql_cleanup.py` 的无 `pymysql` reload 回归，直接验证 lite 模式能在阻断 `pymysql` 导入时继续工作

## 主要落点

- `web/models/__init__.py`
- `web/scheduler/__init__.py`
- `web/webtest/stage3/test_task03_runtime_mysql_specific_sql_cleanup.py`

## 主要验证

```bash
pytest web/webtest/stage3/test_task03_runtime_mysql_specific_sql_cleanup.py -q
pytest tests/test_lite_bootstrap_fixture_path.py tests/test_lite_sqlite_minimal_path.py tests/test_lite_sqlite_high_risk_models.py -q
```

## 保留边界

- `web/webtest/conftest.py` 这类历史 MySQL 测试夹具里的 `CREATE DATABASE IF NOT EXISTS ...` 仍然存在，但它们不在 lite 主线启动链路上
- 这一步没有尝试删光仓库里所有 MySQL 分支，只把 lite 实际会经过的运行时路径收干净
