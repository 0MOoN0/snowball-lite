# 任务 3：基础分析能力覆盖

## 当前状态

- 状态：待开始
- 任务定位：补齐 lite 在 SQLite 下的基础分析能力覆盖

## 目标

把分析能力从“已有一条服务级证明”推进到“分析生成和分析结果查询都可验证”。

这一任务要回答的问题是：

- lite 下基础分析结果能不能在 SQLite 中正确生成
- 生成后的结果能不能通过对外查询接口稳定读出

## 当前基础

目前已经有的基础主要是：

- `GridTransactionAnalysisService.trade_analysis` 已有 SQLite 集成验证，见 `web/webtest/stage3/test_task02_grid_transaction_analysis_sqlite.py`

但现在还缺：

- 分析结果查询接口的覆盖
- 网格类型分析结果的覆盖
- “先生成，再查询”的完整闭环验证

## 建议范围

- 单网格分析结果生成
- 单网格分析结果读取
- 网格类型分析结果读取
- 如成本可控，可补一条“更新分析结果”路径

## 建议优先覆盖的入口

- `GridTransactionAnalysisService.trade_analysis`
- `GET /api/analysis/grid-result/<grid_id>`
- `GET /api/analysis/grid-type-result/<grid_type_id>`
- 如有必要：对应的 `PUT` 更新入口

## 建议落点

- `web/services/analysis/transaction_analysis_service.py`
- `web/routers/analysis/grid_analysis_result_routers.py`
- `web/routers/analysis/grid_type_analysis_result_routers.py`
- `web/models/analysis/*`
- 建议新增测试：`web/webtest/stage4/test_task03_analysis_capability_sqlite.py`

## 建议实施方式

1. 先补“服务生成分析数据”的失败测试
2. 再补“分析结果接口读取”的失败测试
3. 最后把两部分收成一条闭环

## 验收标准

- SQLite 下能完成至少一条单网格分析结果生成
- 生成后的结果能通过 `grid-result` 接口稳定读出
- 至少一类网格类型分析结果能通过 `grid-type-result` 接口稳定读出
- 至少形成一条“生成 -> 查询”的稳定验证路径

## 非目标

- 不要求现在覆盖所有分析类型
- 不要求现在把 scheduler 驱动的分析任务一起纳入
- 不要求现在处理通知、报表等分析结果的外围消费链路
