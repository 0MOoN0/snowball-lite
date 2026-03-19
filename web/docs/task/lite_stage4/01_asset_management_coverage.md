# 任务 1：资产基础管理能力覆盖

## 当前状态

- 状态：待开始
- 任务定位：补齐 lite 在 SQLite 下的资产基础管理能力覆盖

## 目标

把资产相关能力从“局部服务验证”推进到“lite 主线资产能力可验证”。

这一任务要回答的问题是：

- lite 下的资产基础管理，是否已经不仅能建表和写样例数据
- 资产相关查询和核心同步链路，是否已经能在 SQLite 下闭环

## 当前基础

目前已经有的基础主要是：

- 资产列表 smoke 已覆盖，见 `tests/test_lite_smoke_validation_and_decision.py`
- `AssetService.init_fund_asset_data` 已有一条 SQLite 服务级验证，见 `web/webtest/stage3/test_task02_asset_service_sqlite.py`

但现在还缺：

- 资产详情类接口覆盖
- 资产代码 / 别名 / 日线 / 费用 / 持仓关系的系统化验证
- 一条更像 lite 日常使用面的资产能力闭环

## 建议范围

- 资产列表查询
- 资产详情查询
- 资产代码 / 主别名读取
- 基金资产初始化后的日线、费用、持仓读取验证
- 至少一条“服务更新后再通过 API 查询”的闭环路径

## 建议优先覆盖的入口

- `GET /api/asset/list/`
- `GET /api/asset/<asset_id>`
- `AssetService.init_fund_asset_data`

## 建议落点

- `web/services/asset/asset_service.py`
- `web/routers/asset/asset_list_routers.py`
- `web/routers/asset/asset_routers.py`
- `web/models/asset/*`
- 建议新增测试：`web/webtest/stage4/test_task01_asset_management_sqlite.py`

## 建议实施方式

1. 先补失败测试
2. 先验证资产查询面，再补服务更新后的闭环
3. 如果遇到 SQLite 方言差异，只处理 lite 主线路径会真正经过的那部分

## 验收标准

- SQLite 下能完成资产列表查询
- SQLite 下能完成资产详情查询
- `AssetService.init_fund_asset_data` 跑完后，相关资产衍生数据能被正确读出
- 至少形成一条“服务写入 -> API 查询”的稳定验证路径

## 非目标

- 不要求现在覆盖全部资产子类型
- 不要求现在处理老的 `/asset` Blueprint 全量写入路径
- 不要求现在处理依赖异步 actor 的旧初始化流程
- 不要求现在做资产导入类文件接口
