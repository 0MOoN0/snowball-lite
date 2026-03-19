# 任务 1：扩展 lite schema 到主线所需范围（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 5 任务 1 lite schema 扩展（原 task 文档已清理）
- 当前状态：已完成
- 代码审查：已完成，round-02 复审已通过

## 实际结果

- `migrations_snowball_lite/versions/lite_stage3_baseline.py` 已补齐 `tb_category`、`tb_asset_category`、`tb_index_base`、`tb_index_stock`、`tb_index_alias`、`system_settings`、`tb_notification`
- `tb_asset_fund_etf.index_id` 和 `tb_asset_fund_lof.index_id` 已补到 `tb_index_base.id` 的外键约束，SQLite 不会再把错误索引关系静默写入
- `tb_index_base` 的建表顺序已经前置到依赖表之前，lite baseline 建库顺序和约束关系已经对齐
- `web/lite_bootstrap.py` 已把完成判断收口到 `LITE_STAGE5_REQUIRED_TABLES`，旧的 `LITE_STAGE3_REQUIRED_TABLES` 只保留兼容别名
- 已新增 `tests/test_lite_stage5_schema_expansion.py`，直接验证 stage5 schema 建库和无效 `index_id` 提交失败场景

## 主要落点

- `migrations_snowball_lite/versions/lite_stage3_baseline.py`
- `web/lite_bootstrap.py`
- `tests/test_lite_stage5_schema_expansion.py`

## 主要验证

```bash
pytest tests/test_lite_stage5_schema_expansion.py -q
pytest web/webtest/stage3/test_task01_sqlite_fixture_bridge.py web/webtest/stage3/test_task04_lite_migration_baseline.py -q
```

## 保留边界

- 当前扩展的是 lite 主线路径所需 schema，不等于把全仓库所有历史表都并进 `migrations_snowball_lite`
- `alembic_version` 仍然使用 `lite_stage3_baseline` 这一版号，阶段 5 收口的是内容口径，不是另起一套迁移编号
