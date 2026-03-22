# 轻量版第四阶段规划（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 4 任务目录（原 task 文档已清理）
- 当前状态：已完成
- 阶段结论：lite 主线业务覆盖已经完成阶段 4 收口，建议进入阶段 5
- 阶段收口：已完成，review 工件已清理

## 本阶段实际结果

- 已补齐资产基础管理、交易记录管理、基础分析能力三条 SQLite 业务闭环
- 已补齐 `xalpha` / DataBox 的 cache 复用与近真实验证边界
- 已形成 lite 查询 API 覆盖矩阵和固定回归命令
- 已完成阶段回归、final review、缺陷修复和 round-02 复审

## 本阶段归档文档

- `01_asset_management_coverage.md`
- `02_record_management_coverage.md`
- `03_analysis_capability_coverage.md`
- `04_xalpha_databox_lite_coverage.md`
- `05_query_api_coverage_matrix.md`
- `06_stage4_acceptance_and_decision.md`

## 当前背景

阶段 1 到阶段 3 已经证明了四件事：

1. lite 模式本身能跑
2. SQLite 最小链路已经稳定
3. 一批高风险模型和两条更业务化的服务链路已经通过 SQLite 验证
4. lite 已经有自己的 `migrations_snowball_lite` 和 `bootstrap_lite_database`

但在阶段 4 开始前，还不能直接说“lite 主线已经脱离 MySQL”。

当时真正缺的，不是再补几个零散模型测试，而是把 lite 目标能力按业务域补齐。

## 第四阶段目标

第四阶段解决的是：

- lite 不能只靠局部样例证明自己可用
- 需要按 lite 的核心能力清单补齐 SQLite 下的业务闭环验证
- 要开始更系统地回答“lite 主线能不能脱离 MySQL”

这一阶段只关注 lite 主线，不要求把全仓库一起推进。

## 第四阶段验收结果

- lite 核心目标能力都已经至少有一条明确、可重复的 SQLite 验证路径
- 不再只靠模型级测试或少数样例服务支撑结论
- 已形成“已覆盖 / 未覆盖”的能力清单
- 已能明确说明：阶段 4 结束后，lite 主线距离“脱离 MySQL”还差初始化、运行时和 schema 收口

## 保留边界

- 阶段 4 仍然只是范围化扩展，不是完整 lite schema 结论
- `web/webtest` 和 `tests/` 仍然不能在同一个 pytest 进程里混跑
- 真实第三方链路仍要保留单独的手工 / 环境验收
