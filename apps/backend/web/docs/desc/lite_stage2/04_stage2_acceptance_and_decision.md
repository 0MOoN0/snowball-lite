# 任务 4：第二阶段收口与决策

## 结论

继续推进。

当前没有证据表明应该暂停，也不建议现在就拆成独立项目。

## 已验证通过

### 1. 真实 DataBox 链路

- `fundinfo + get_daily` 已真实跑通
- 真实链路验证入口已单独落成 manual test

### 2. 高风险 SQLite 模型

- `IndexBase/StockIndex + IndexAlias + AssetFundETF + AssetAlias` 已完成专项验证
- `TradeAnalysisData + GridTradeAnalysisData` 已完成专项验证
- 外键和唯一约束已确认生效

### 3. lite 测试基建

- `tests/conftest.py` 已统一 lite 夹具
- 默认回归命令已固定
- 本地测试和真实外部依赖验证已分层

## 增量验收

2026-03-19 按阶段二变更范围做过一轮增量 gate。

执行命令：

```bash
PYTHONPATH=. pytest -q \
  tests/test_lite_bootstrap_review.py \
  tests/test_lite_sqlite_minimal_path.py \
  tests/test_xalpha_databox_compat.py \
  tests/test_lite_smoke_validation_and_decision.py \
  tests/test_lite_sqlite_high_risk_models.py \
  tests/test_lite_real_databox_validation.py \
  -m "not manual"
```

结果：

- `23 passed, 1 deselected`

真实链路验收命令：

```bash
PYTHONPATH=. LITE_RUN_REAL_DATABOX=1 pytest -q tests/test_lite_real_databox_validation.py
```

结果：

- `4 passed`

结论：

- 当前阶段二增量 gate 结果为 `incremental-pass-only`

## 代码审查结果

阶段二相关改动已经做过一次针对性 code review。

审查范围包括：

- lite 测试夹具
- lite smoke / sqlite / databox 测试
- `web/lite_validation.py`
- 阶段二归档文档

审查结论：

- 当前没有 medium 或 high 等级问题
- 已知残余风险仍然集中在第三方链路波动和 SQLite Decimal warning

## 主要 blocker

### 1. 历史迁移链路仍未验证

当前仍主要依赖 `db.create_all()`，不能说明 Alembic 历史迁移可直接迁到 SQLite。

### 2. 真实第三方链路仍受外部环境影响

真实 DataBox 链路已经跑通，但仍依赖第三方站点和网络状态。

### 3. 历史测试体系没有整体切到 lite

阶段二收敛的是 lite 入口，不是整个历史测试体系。

## SQLite 迁移状态判断

目前还不能说“SQLite 迁移已经完成”。

更准确的说法是：

- lite 模式下的 SQLite 最小链路已经跑通
- 高风险模型验证已经补到第二阶段要求
- 但仓库层面的完整 SQLite 迁移还没有完成

原因：

1. lite 仍主要依赖 `db.create_all()` 验证，不是完整迁移历史
2. 没有 `migrations_snowball_lite` 这类独立迁移目录
3. 非 lite 配置仍然默认走 `mysql+pymysql`
4. 历史测试和 scheduler 路径里仍有 MySQL 专有逻辑

## 建议下一步

1. 继续留在当前仓库推进，不建议现在拆独立项目
2. 阶段三优先补 1 到 2 条更业务化的高频链路
3. 不要现在就承诺“全量 SQLite 化”
