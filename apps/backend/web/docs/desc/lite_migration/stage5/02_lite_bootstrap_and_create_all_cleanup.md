# 任务 2：统一 lite bootstrap 口径并收缩 `db.create_all()`（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 5 任务 2 lite bootstrap 收口（原 task 文档已清理）
- 当前状态：已完成
- 代码审查：已完成

## 实际结果

- `tests/conftest.py` 里的 `lite_app` 夹具已经改成调用 `bootstrap_lite_database(app)`，lite 主线测试入口不再靠 `db.create_all()`
- `tests/test_lite_sqlite_minimal_path.py` 已去掉重复的 `db.create_all()`，最小链路验证现在直接复用统一 bootstrap
- 已新增 `tests/test_lite_bootstrap_fixture_path.py`，直接断言 `lite_app` 夹具会准备 stage5 schema 和 `alembic_version`
- lite 阶段结论现在可以明确写成“主线入口走 bootstrap / migration”，剩下的 `create_all()` 只留在历史 MySQL 测试夹具范围

## 主要落点

- `tests/conftest.py`
- `tests/test_lite_sqlite_minimal_path.py`
- `tests/test_lite_bootstrap_fixture_path.py`

## 主要验证

```bash
pytest tests/test_lite_bootstrap_fixture_path.py tests/test_lite_sqlite_minimal_path.py tests/test_lite_smoke_validation_and_decision.py tests/test_lite_sqlite_high_risk_models.py tests/test_lite_stage4_query_api_matrix.py -q
```

## 保留边界

- `web/webtest/TestModelsClass.py`、`web/webtest/BasicRouterTestClass.py`、`web/webtest/conftest.py` 里的历史 `create_all()` 入口还在，但已经不再代表 lite 正式初始化口径
- 这一步没有试图统一 `tests/` 和 `web/webtest/` 的运行方式，阶段回归仍按既有约束拆 pytest 进程执行
