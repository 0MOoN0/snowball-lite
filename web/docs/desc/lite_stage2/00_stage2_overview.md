# 轻量版第二阶段规划

## 当前背景

阶段一已经完成，当前已经具备：

- Lite 启动骨架
- SQLite 最小可用链路
- `xalpha` / DataBox 最小兼容链路
- 2 到 3 条核心接口 smoke 验证

但这些结果还更偏“spike 可行”，还不能直接等同于“轻量版可以长期稳定使用”。

## 第二阶段目标

第二阶段的目标不是继续铺更多功能，而是把已经验证过的最小链路往“更真实、更稳定、更可维护”推进一步。

重点收口 3 件事：

1. 补一条更真实的 DataBox / 第三方数据验证链路
2. 扩大 SQLite 覆盖到高风险模型，而不是只停留在最小 happy path
3. 把 lite 测试和验证方式再收敛，降低后续维护成本

## 第二阶段不做什么

- 不做全量 SQLite 迁移
- 不整理完整 Alembic 历史
- 不追求全接口、全测试覆盖
- 不马上拆成独立项目

## 任务拆分

- `01_real_databox_validation.md`
- `02_sqlite_high_risk_models.md`
- `03_lite_test_fixture_convergence.md`
- `04_stage2_acceptance_and_decision.md`

## 第二阶段验收标准

- 至少 1 条更真实的 DataBox 链路被验证
- 至少 1 组高风险 SQLite 模型完成专项验证
- lite 测试入口和运行环境进一步收敛
- 形成第二阶段结论：继续推进 / 暂停 / 转向拆分项目

## 推荐节奏

建议按这个顺序做：

1. 先做真实 DataBox 验证
2. 再补高风险 SQLite 模型
3. 再收敛测试基建
4. 最后输出第二阶段结论

## 预期产物

- 一份更真实的 DataBox 验证记录
- 一份高风险 SQLite 模型验证记录
- 一份 lite 测试收敛说明
- 一份第二阶段收口结论
