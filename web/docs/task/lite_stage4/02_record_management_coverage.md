# 任务 2：交易记录管理能力覆盖

## 当前状态

- 状态：待开始
- 任务定位：补齐 lite 在 SQLite 下的交易记录管理能力覆盖

## 目标

把交易记录相关能力从“只验证新增和详情”推进到“lite 主线记录管理可验证”。

这一任务要回答的问题是：

- lite 下记录的新增、读取、列表、筛选是否都能在 SQLite 下跑通
- 交易记录与业务关联对象的关系，是否已经能在 SQLite 下稳定工作

## 当前基础

目前已经有的基础主要是：

- `POST /api/record`
- `GET /api/record/<record_id>`

这两条最小 smoke 已经有了，见 `tests/test_lite_smoke_validation_and_decision.py`。

但现在还缺：

- 交易记录列表查询
- 典型筛选条件验证
- 交易记录与 `TradeReference` 的关系验证
- 更新路径或关联更新路径的代表性覆盖

## 建议范围

- 交易记录新增
- 交易记录详情读取
- 交易记录列表分页查询
- 资产名 / 别名 / 时间范围 / 交易方向中的代表性筛选
- `groupType` / `groupId` 对应的关联关系验证
- 至少一条更新或关联替换路径

## 建议优先覆盖的入口

- `POST /api/record`
- `GET /api/record/<record_id>`
- `GET /api/record_list`
- `PUT /api/record`

## 建议落点

- `web/routers/record/record_routers.py`
- `web/routers/record/record_list_routers.py`
- `web/models/record/*`
- `web/models/grid/*`
- 建议新增测试：`web/webtest/stage4/test_task02_record_management_sqlite.py`

## 建议实施方式

1. 先把现有 smoke 扩成失败测试
2. 再补列表和筛选能力
3. 最后补一条带 `TradeReference` 的记录关系路径

## 验收标准

- SQLite 下能完成记录新增、详情读取和列表查询
- 至少一组代表性筛选条件能稳定工作
- 记录与 `TradeReference` 的关联在 SQLite 下可写、可读、可更新
- 至少形成一条“新增 -> 详情 -> 列表 -> 更新”的稳定验证路径

## 非目标

- 不要求现在处理 `record_file` 导入导出能力
- 不要求现在处理 `IRecord` 相关路径
- 不要求现在覆盖所有记录筛选组合
- 不要求现在做批量同步类接口
