# 任务 2：高风险 SQLite 模型验证结果

## 本轮选择

阶段二没有优先碰 scheduler，而是先验证两组风险更高的模型：

1. `IndexBase/StockIndex + IndexAlias + AssetFundETF + AssetAlias`
2. `TradeAnalysisData + GridTradeAnalysisData`

原因：

- 第一组同时覆盖联合表继承、额外外键、关联查询、唯一约束
- 第二组覆盖另一套 joined-table inheritance 和多态回读
- 这两组更能说明 SQLite 不是只跑通了最小模型

## 本轮实现

- 新增测试：`tests/test_lite_sqlite_high_risk_models.py`

## 推荐运行方式

```bash
PYTHONPATH=. pytest -q tests/test_lite_sqlite_high_risk_models.py
```

2026-03-19 结果：

- `3 passed`

## 已验证通过

### 1. 资产 / 指数继承链

- `StockIndex` 可以完成建表、插入、查询
- `IndexAlias` 关系查询正常
- `AssetFundETF` 可以通过 `index_id` 关联 `StockIndex`
- 用 `Asset.query` 查询时，能正确多态回读到 `AssetFundETF`
- 更新基类字段和子类字段后，都能正确持久化

### 2. 约束生效

- 重复的 `IndexAlias(provider_code, provider_symbol)` 会触发 `IntegrityError`
- 无效的 `AssetFundETF.index_id` 会触发 `IntegrityError`

### 3. 分析模型继承链

- `GridTradeAnalysisData` 可以正常写入 SQLite
- 用 `TradeAnalysisData.query` 回读时，多态装载正常
- 子类字段更新后再次查询能正确返回

## 结论

任务 2 已完成。
