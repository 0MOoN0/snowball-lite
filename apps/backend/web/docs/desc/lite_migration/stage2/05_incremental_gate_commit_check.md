# 阶段二增量验收与提交前检查

## 检查范围

本次只检查当前工作区里和 lite stage2 直接相关的改动：

- `tests/conftest.py`
- `tests/test_lite_bootstrap_review.py`
- `tests/test_lite_smoke_validation_and_decision.py`
- `tests/test_lite_sqlite_minimal_path.py`
- `tests/test_xalpha_databox_compat.py`
- `tests/test_lite_sqlite_high_risk_models.py`
- `tests/test_lite_real_databox_validation.py`
- `web/lite_validation.py`
- `web/docs/desc/lite_migration/project/00_repo_baseline.md`
- `web/docs/desc/lite_migration/stage2/*.md`
- `web/docs/轻量版分支改造方案.md`

## 参考文档

- `web/docs/desc/lite_migration/stage2/00_stage2_overview.md`
- `web/docs/desc/lite_migration/stage2/02_sqlite_blockers.md`
- `web/docs/desc/lite_migration/stage2/04_stage2_acceptance_and_decision.md`

## 执行命令

```bash
rg -n "web/docs/task/lite_stage2|web/docs/review|2026-03-19_lite_stage2_incremental_gate|2026-03-19_stage2_code_review" web/docs -g '*.md'
git diff --check
PYTHONPATH=. pytest -q tests/test_lite_bootstrap_review.py tests/test_lite_sqlite_minimal_path.py tests/test_xalpha_databox_compat.py tests/test_lite_smoke_validation_and_decision.py tests/test_lite_sqlite_high_risk_models.py tests/test_lite_real_databox_validation.py -m "not manual"
PYTHONPATH=. LITE_RUN_REAL_DATABOX=1 pytest -q tests/test_lite_real_databox_validation.py
```

## 执行结果

- 文档里已经没有残留的 `task` / `review` 路径引用
- `git diff --check` 通过
- 默认回归：`23 passed, 1 deselected`
- 真实 DataBox 验收：`4 passed`

## 最小代码生成

没有使用。

## 结果标签

`incremental-pass-only`

## 提交前结论

按当前变更范围看，这个工作区可以提交。

这里的结论是增量范围内成立，不代表全仓库已经完成最终 gate。

## 残余风险

- 真实 DataBox 链路仍依赖第三方站点和网络状态
- SQLite Decimal warning 仍然存在，但本轮没有发现功能性失败
- 仓库级 SQLite 迁移仍未完成，当前仍主要验证 lite 路径

## 延后到后续阶段的事

- 如果后面要做“全量可发布”判断，仍需要更大范围的最终 gate
- 如果后面要宣称“SQLite 迁移完成”，仍需要补历史迁移链路和 MySQL 专有逻辑收口
