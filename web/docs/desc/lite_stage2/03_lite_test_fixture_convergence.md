# 任务 3：Lite 测试基建收敛结果

## 本轮做了什么

阶段二把 lite 相关测试的公共环境准备收敛到了 `tests/conftest.py`。

统一入口：

- `lite_runtime_paths`
- `lite_runtime_env`
- `lite_app`

## 当前测试边界

### 本地可重复验证

- `tests/test_lite_bootstrap_review.py`
- `tests/test_lite_sqlite_minimal_path.py`
- `tests/test_xalpha_databox_compat.py`
- `tests/test_lite_smoke_validation_and_decision.py`
- `tests/test_lite_sqlite_high_risk_models.py`

特点：

- 不依赖外部网络
- 默认可重复执行
- 适合作为阶段二默认回归

### 真实外部依赖验证

- `tests/test_lite_real_databox_validation.py`

特点：

- 依赖真实第三方站点
- 默认不执行
- 需要显式设置 `LITE_RUN_REAL_DATABOX=1`
- 已标记为 `manual`

## 推荐命令

### 1. 阶段二默认回归

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

2026-03-19 结果：

- `23 passed, 1 deselected`

### 2. 真实 DataBox 验收

```bash
PYTHONPATH=. LITE_RUN_REAL_DATABOX=1 pytest -q tests/test_lite_real_databox_validation.py
```

2026-03-19 结果：

- `4 passed`

## 结论

- lite 测试环境变量设置不再散落
- 本地回归和真实外部依赖验证边界已经清楚
- 阶段二推荐怎么跑，已经固定下来

任务 3 已完成。
