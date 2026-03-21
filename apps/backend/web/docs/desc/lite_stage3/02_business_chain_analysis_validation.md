# 任务 2：业务链路 SQLite 集成验证

## 归档状态

- 状态：已完成
- 已验证链路：
  - `AssetService.init_fund_asset_data`
  - `GridTransactionAnalysisService.trade_analysis`
- 主要测试：`web/webtest/stage3/test_task02_asset_service_sqlite.py`、`web/webtest/stage3/test_task02_grid_transaction_analysis_sqlite.py`
- 默认验证命令：`pytest web/webtest/stage3 -q`

## 目标

选 1 到 2 条真正贴近日常使用的业务链路，在 SQLite 下做集成验证。

第三阶段不应该再停留在“模型能插能查”，而要验证“业务流程能不能走完”。

## 推荐优先选择

### 1. AssetService.init_fund_asset_data

理由：

- 这条链路比阶段二 smoke 更像真实“资产初始化”
- 会碰到 `DataBox.fund_info`
- 会写入 `AssetFundDailyData`、`AssetFundFeeRule`、`AssetHoldingData`
- 能把 DataBox、业务服务和 SQLite 持久化真正串起来

对应参考位置：

- `web/services/asset/asset_service.py`
- `web/webtest/services/asset/AssetServiceTest.py`

### 2. GridTransactionAnalysisService.trade_analysis

理由：

- 这条链路串起了 `Record`、`Grid`、`GridType`、`GridTypeDetail`、`TradeAnalysisData`
- 既有业务关系，又有分析结果持久化
- 仓库里已经有现成的历史测试资产可参考

对应参考测试：

- `web/webtest/services/analysis/test_grid_transaction_analysis_service.py`

## 任务范围

- 为上面 1 到 2 条链路建立 SQLite 版集成测试
- 优先使用 mock/stub 控住第三方行情依赖
- 验证核心结果不是“函数返回不报错”，而是：
  - 数据能落库
  - 分析结果能回读
  - 更新后结果一致

## 推荐做法

- 尽量复用现有测试数据组织方式
- 把外部行情依赖 mock 掉，避免阶段三又被第三方环境波动干扰
- `AssetService.init_fund_asset_data` 里涉及持仓查询和 `time.sleep`，默认回归应通过 patch/stub 去掉这些不稳定因素
- 如果历史测试太重，可以先抽出更小的 stage3 专项测试文件，不强行硬改原文件

## 验收标准

- 至少 1 条业务链路在 SQLite 下完整通过
- 更理想的结果是 2 条链路都通过
- 测试里能明确看到业务结果已经写入 SQLite，并能正确回读
- 相关测试被纳入阶段三默认回归命令

## 非目标

- 不要求所有 analysis service 都迁完
- 不要求所有 router 都补成 SQLite 集成测试
- 不要求真实第三方数据源参与这一步默认回归
