# 任务 6：第四阶段收口与决策（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 4 任务 6 收口与决策（原 task 文档已清理）
- 当前状态：已完成
- 最终结论：建议进入阶段 5
- 代码审查：已完成，最终复审已通过

## 结论

- 结论：建议进入阶段 5
- 推进方式：继续做 lite 主线的初始化和运行时收口
- 不建议现在做的事：不要把阶段 4 解读成全仓库 SQLite 迁移完成，也不要说 lite 已完全脱离 MySQL

stage4 的实际结果已经超过“局部样例可跑”的水平，说明 lite 主线能力覆盖有实质提升。当前更合理的下一步不是继续扩散业务面，而是把已经验证过的覆盖面收成稳定的初始化、运行时和 schema 口径。

## 本阶段已验证通过

- `web/webtest/stage4/test_task01_asset_management_sqlite.py web/webtest/stage4/test_task02_record_management_sqlite.py web/webtest/stage4/test_task03_analysis_capability_sqlite.py -q` 通过，结果是 `4 passed`
- `tests/test_lite_stage4_query_api_matrix.py tests/test_lite_databox_stage4_coverage.py tests/test_lite_smoke_validation_and_decision.py tests/test_xalpha_databox_compat.py -q` 通过，结果是 `21 passed`
- 资产、记录、分析三条主业务链路已经从单点样例推进到受控的 SQLite 覆盖
- 查询 API 覆盖矩阵已经落地，能直接复用固定回归命令
- DataBox / xalpha 兼容链路已经有了明确的覆盖边界和可重复验证结果
- task01~task05 的 round-01 review 和 task06 的 final staged review round-02 都已通过，当前没有中等或以上问题残留

## 仍然保留的 blocker

- stage4 只证明了 lite 主线的范围化扩展，不代表完整 lite schema 结论
- `web/webtest` 和 `tests/` 不能在同一个 pytest 进程里混跑，阶段回归必须拆命令执行
- 真实第三方链路仍然依赖单独的手工 / 环境验收，不能只靠本地自动化闭环
- SQLite 的 Decimal 警告和部分上游 deprecation 警告仍然存在，但当前不构成阻塞

## 不建议现在做的事

- 不要把 stage4 说成“全仓库 SQLite 迁移完成”
- 不要把 lite 说成“已经完全脱离 MySQL”
- 不要在 stage 5 里直接追求全量历史迁移，先把已经验证过的 lite 路径收口

## 是否进入阶段 5

建议进入阶段 5。

阶段 5 更应该接手的是初始化和运行时收口，而不是重新扩一轮业务覆盖。当前 stage4 已经给出足够证据，说明 lite 主线的核心能力覆盖确实比 stage3 更完整，也更适合继续往稳定收口推进。

## 验收记录

执行了以下最小验收命令：

```bash
pytest web/webtest/stage4/test_task01_asset_management_sqlite.py web/webtest/stage4/test_task02_record_management_sqlite.py web/webtest/stage4/test_task03_analysis_capability_sqlite.py -q
pytest tests/test_lite_stage4_query_api_matrix.py tests/test_lite_databox_stage4_coverage.py tests/test_lite_smoke_validation_and_decision.py tests/test_xalpha_databox_compat.py -q
```

结果：

- 第一条命令：`4 passed`
- 第二条命令：`21 passed`

## 关联结论

- 这份收口只覆盖 lite stage4 的阶段判断
- 它不替代全仓库最终 gate
- 它也不改变 stage4 仍然是范围化扩展、不是完整 SQLite 迁移结论 这个事实
