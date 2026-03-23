# lite 分析链路 AssetCode 查询 SQLite 兼容修复（归档）

- [x] 修复 `XaDataAdapter.trade(...)` 在 SQLite 下用 `numpy.int64` 查询 `AssetCode` 失败的问题
- [x] 收口分析链路的异常透传，避免把根因吞成 `trade_id=-1`
- [x] 为 amount / grid type / grid strategy 三条分析链路补 SQLite 回归测试
- [x] 通过共享 service 链路验证手动刷新网格类型 / 网格策略分析入口核心能力恢复可用
- [x] 明确修复后分析数据补跑口径

## 归档状态
- 类型：项目级单任务归档文档
- 状态：已完成
- 原任务路径：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/lite_analysis_asset_code_lookup_sqlite_fix.md`
- 文档目的：直接指导本次 lite / SQLite 分析链路缺陷修复，不拆父任务
- 目标：修复分析链路在 SQLite 下查不到 `AssetCode` 的问题，并恢复受影响分析任务和手动刷新入口
- 完成边界：只处理分析链路的 `AssetCode` 查询、异常语义和对应测试，不把 `xalpha` 外部网络异常一起并入本任务
- review 产物：已按归档规则删除，不再长期保留
- 实现结果：`asset_id` 查询前已显式转原生 `int`，缺失 `code_xq` 时直接抛出带 `asset_id` 的 `WebAnalyzerException`
- 验证结果：`apps/backend/web/webtest/stage4/test_task03_analysis_capability_sqlite.py` 6 项通过，`tests/test_xalpha_databox_compat.py` 16 项通过
- 残余风险：未单独补 HTTP 路由层对 `WebAnalyzerException` 响应体的断言，但不影响本次 service / scheduler 修复闭环

## 1. 问题定义
`2026-03-23 21:00:00` 的 `analysis_scheduler.to_analysis_all_transaction` 已实际报错。日志表象是 `WebAnalyzerException('交易记录不存在')`，但根因更早：

1. `apps/backend/web/databox/adapter/data/xa_data_adapter.py` 用 `record_df.asset_id.unique()` 的 `numpy.int64` 直接做 `AssetCode.asset_id.in_(...)`
2. lite / SQLite 下这条查询返回 0 行，导致所有 `code_xq` 映射成 `NaN`
3. `xalpha.multiple` 对 `NaN` 调 `startswith()`，抛出 `'numpy.float64' object has no attribute 'startswith'`
4. `DataBox.trade()` 把原始异常吞掉后返回 `-1`
5. 后续 `summary(trade_id=-1)` 再报“交易记录不存在”，把根因盖住

这个问题不是只影响 21:00 任务。网格类型分析、网格策略分析和对应手动刷新接口共用同一条分析基类链路，都会踩中这段查询。

## 2. 完成定义
本任务完成后，必须同时满足下面几条：

- lite / SQLite 下，分析链路查询 `AssetCode` 前会把 `asset_id` 收口成原生 `int`
- `AmountTransactionAnalysisService`、`GridTypeTransactionAnalysisService`、`GridStrategyTransactionAnalysisService` 三条链路都能正常拿到 `code_xq`
- `DataBox.trade()` 不再把这类根因吞成“交易记录不存在”；日志里能直接看到真实异常
- 21:00、16:00、16:15 三类分析任务对应的 service 级调用在 SQLite 下可执行
- 手动刷新网格类型 / 网格策略分析接口在 SQLite 下不再因为这条缺陷失败
- 不新增 migration，不改 lite / MySQL 业务 schema

## 3. 范围
本任务只覆盖下面这些内容：

- `apps/backend/web/databox/adapter/data/xa_data_adapter.py`
- 必要时调整 `apps/backend/web/databox/data_box.py` 的异常处理语义
- 与分析链路直接相关的 SQLite 回归测试
- 受影响任务和接口的验证说明

## 4. 非目标
本任务不做下面这些事情：

- 不处理 `xalpha` / 雪球实时接口返回 `KeyError('data')`、`RecursionError` 这类外部网络问题
- 不补分析结果表的历史回填脚本
- 不重构整个 DataBox / xalpha 适配层
- 不把 MySQL 环境兼容结论当作本任务完成条件
- 不顺手修改与本缺陷无关的 scheduler 持久化策略

## 5. 选定方案
采用“查询前显式类型收口 + 缺失映射显式失败”方案。

规则：

1. `record_df.asset_id.unique()` 在参与 `IN` 查询前，统一转成原生 `int` 列表
2. `AssetCode` 查询结果用于构造 `asset_id -> code_xq` 映射时，只接受非空 `code_xq`
3. 如果记录里的 `asset_id` 经过收口后仍有缺失映射，不继续把 `NaN` 喂给 `xalpha`
4. 这类缺失映射要直接抛出带 `asset_id` 信息的异常，不能先吞掉再返回 `-1`
5. `DataBox.trade()` 只保留能帮助定位根因的异常日志，不把本缺陷重新包装成“交易记录不存在”

## 6. 数据与存储影响

- 不改 `tb_record`、`tb_asset_code`、`tb_trade_analysis_data`、`tb_grid_trade_analysis_data`、`tb_amount_trade_analysis_data` 表结构
- 不新增 migration
- 不改 lite bootstrap 和既有 SQLite 基线
- 修复前已经写入的分析数据保持原状；修复后只允许通过重新执行分析任务生成新数据

## 7. API 与交互影响
直接受影响的入口：

- `analysis_scheduler.to_analysis_all_transaction`
- `GridTypeScheduler.grid_type_trade_analysis`
- `GridStrategyScheduler.grid_strategy_trade_analysis`
- `PUT /api/analysis/grid-type-result/:grid_type_id`
- `PUT /api/analysis/grid-result/`

间接受影响的读接口：

- `/api/dashboard/overall-trade-analysis`
- `/api/dashboard/grid-strategy-summary`
- `/api/charts/transaction/summary`
- `/api/analysis/grid-type-result/:grid_type_id`
- `/api/analysis/grid-result/:grid_id`

修复完成后，上述读接口不需要改协议，但会在补跑分析后重新拿到更新后的数据。

## 8. 生命周期与状态约定
分析链路的运行约定改成下面这样：

1. 先从 `Record` 生成 DataFrame
2. 再把参与查询的 `asset_id` 收口为原生 `int`
3. 用 `AssetCode` 查出 `code_xq` 并回填 `code`
4. 只有 `code` 全部可用时才进入 `xalpha.mul(...)`
5. 如果 `AssetCode` 缺失或映射不完整，直接在 trade 阶段失败并暴露真实原因
6. 只有 trade 阶段成功拿到有效 `trade_id` 后，才继续走 `summary()` 和持久化

这里要明确：

- “查不到分析缓存” 和 “前置代码映射失败” 不是一回事
- 不能再把前置映射失败伪装成 `trade_id=-1` 的缓存缺失

## 9. 旧数据与补跑处理

- 当前库里总体交易分析最新数据停在 `2026-03-19`
- 网格类型 / 网格策略分析最新数据停在 `2026-03-20`
- 本任务不自动删除旧分析数据
- 代码修复后，需要按当前 lite 运行库手动补跑受影响分析任务，至少覆盖：
  - 1 次总体交易分析
  - 1 次网格类型分析
  - 1 次网格策略分析
- 如果补跑要追平停更窗口，执行口径单独记录在实现说明或 review 文档，不把脚本开发并入本任务

## 10. 验收标准

- 在 SQLite 下复现当前 `229` 条记录、`6` 个资产的分析场景时，`AssetCode.query.filter(AssetCode.asset_id.in_(...)).all()` 不再返回 0 行
- `AmountTransactionAnalysisService.trade_analysis(...)` 不再因为 `numpy.float64.startswith` 失败
- `GridTypeTransactionAnalysisService` 对任一已有 `grid_type_id` 可正常完成一次分析
- `GridStrategyTransactionAnalysisService.trade_analysis(...)` 可正常完成一次分析
- 缺失 `code_xq` 的场景下，异常信息能直接指出缺失 `asset_id`，不再落成“交易记录不存在”
- 相关 SQLite 回归测试通过，且不引入 migration 变更

## 11. 验证要求
至少补下面三类验证：

1. `xa_data_adapter.trade(...)` 在 SQLite 下使用 `numpy.int64` 输入时，查询前转 `int` 后能拿到正确 `AssetCode`
2. amount / grid type / grid strategy 三条 service 级分析链路各有 1 条 SQLite 回归
3. 缺失 `code_xq` 时，抛出的异常是映射缺失，而不是 `trade_id=-1` 后的二次异常

优先落点：

- `apps/backend/web/webtest/stage4/test_task03_analysis_capability_sqlite.py`
- `apps/backend/web/webtest/services/analysis/`
- 如需覆盖适配层，可补 `apps/backend/web/webtest/lite/` 下的 SQLite 兼容验证

## 12. 风险点

- 如果只把 `numpy.int64` 转型修掉，但继续吞异常，后续类似问题仍会被伪装成缓存缺失
- 如果只验证 amount 链路，不验证 grid type / grid strategy，16:00 和 16:15 任务仍可能漏回归
- 如果补跑口径不明确，前台会继续读到旧分析数据，容易误判成修复未生效
