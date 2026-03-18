# 任务 3：xalpha / DataBox 兼容验证

## 目标

验证 `xalpha` 与 DataBox 在轻量模式下至少具备一种稳定的缓存后端，并能跑通一条最小数据链路。

优先验证 SQLite；如果 SQLite 路径成本明显过高，则退回 CSV 缓存作为轻量版 v1 方案。

## 任务范围

- 检查 `xalpha` 的 SQL backend 在 SQLite 下的行为
- 修复最小必要兼容点
- 为 DataBox 增加轻量模式下的缓存策略选择
- 形成“SQLite 继续 / CSV 兜底”的结论

## 关键文件

- `xalpha/universal.py`
- `xalpha/info.py`
- `web/databox/adapter/data/xa_service.py`
- `web/databox/adapter/data/xa_data_adapter.py`
- `web/common/cons/webcons.py`

## 当前已知问题

- `cachedio()` 在 SQLite 缺表时可能抛 `OperationalError`
- `pd.read_sql(table_name, engine)` 的行为在 SQLite 下不够稳
- 当前项目默认把 engine 直接注入 `xalpha` SQL backend

## 设计原则

- 先保证一条稳定链路，不追求全场景覆盖
- 先选一种后端跑通，再考虑保留多种后端
- 如 SQLite 路径成本偏高，CSV 缓存是合理退路

## 推荐技术方向

优先级建议：

1. SQLite backend 可用性修补
2. 如果修补范围过大，切换为 CSV backend
3. 保留后续再回到独立 SQLite cache 的可能

## 执行步骤

1. 复现 `xalpha` 在 SQLite 下的最小失败路径
2. 修复缺表、缓存 miss、表读取方式等核心问题
3. 为 DataBox 增加轻量模式缓存后端选择
4. 跑一次“写缓存 -> 读缓存”验证
5. 跑一次最小 DataBox 查询链路

## 验收标准

- 至少一种缓存后端可在轻量模式下稳定工作
- 至少一次缓存写入和读取成功
- 至少一条 DataBox 最小链路返回结果
- 能明确记录 SQLite 方案是继续还是降级到 CSV

## 非目标

- 不追求 xalpha 全功能兼容
- 不重构整个 DataBox 架构
- 不保证所有数据源都适配轻量模式

## 风险提示

- 如果 `xalpha` SQLite 兼容需要修改过深，后续维护成本会明显上升
- 如果缓存策略不收口，轻量版边界会再次变重

## 任务完成产物

- 一条最小可用的 `xalpha` / DataBox 数据链路
- 一份缓存后端选择结论
- 一份待后续处理的问题清单

## 本轮结论

- `xalpha` 的 SQLite 缓存兼容已经补上，最小读写路径也已经用单测验证过了。
- 但轻量版默认还是走 CSV，不把 SQLite 当默认后端。
- 原因很简单：轻量版现在更看重稳定、简单、好排查，而 CSV 比 SQLite 更少方言约束，也更容易把缓存当成可重建数据来处理。
- SQLite 现在保留为可切换选项，后续如果真有必要，再单独切过去，不影响当前轻量版先跑起来。

## 当前状态

- 已完成（阶段一）

## 对应验证

- `tests/test_xalpha_databox_compat.py`
- 验证重点：
  - SQLite SQL backend 的最小读写和缓存 miss 兼容
  - lite 模式默认 CSV backend 的配置和 DataBox 适配行为
  - 多个 lite app 之间的缓存配置刷新与并发串行化
