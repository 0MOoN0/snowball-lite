# lite_stage4 查询 API 覆盖矩阵（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 4 任务 5 查询 API 覆盖矩阵（原 task 文档已清理）
- 当前状态：已完成
- 对应聚合测试：`tests/test_lite_stage4_query_api_matrix.py`
- 代码审查：已完成

## 结论

stage4 目前已经把这几条查询面跑通了：

- 资产列表 / 资产详情
- 交易记录详情 / 交易记录列表的代表性筛选
- 分析结果详情
- `token_test` 系统入口 smoke
- `DataBox.fund_info`、`XaDataAdapter.get_daily`、`XaServiceAdapter.get_daily` 和跨 app cache 读取路径的辅助/兼容验证

这里不把没跑到的东西写成“已覆盖”。当前还没纳入的扩展查询，下面单独列出来。

## 覆盖矩阵

| 能力 | 入口接口或服务 | 自动化测试位置 | 是否需要手工验收 | 当前覆盖状态 | 固定回归命令 |
| --- | --- | --- | --- | --- | --- |
| 资产查询 | `GET /api/asset/list/`，`GET /api/asset/<asset_id>` | `web/webtest/stage4/test_task01_asset_management_sqlite.py`，`tests/test_lite_stage4_query_api_matrix.py` | 否 | 已覆盖，只有列表 / 详情；`select`、`alias` 列表等扩展查询未纳入这轮矩阵 | 见文末 |
| 交易记录查询 | `GET /api/record/<record_id>`，`GET /api/record_list` | `web/webtest/stage4/test_task02_record_management_sqlite.py`，`tests/test_lite_stage4_query_api_matrix.py` | 否 | 已覆盖代表性筛选；不是全部筛选组合 | 见文末 |
| 分析结果查询 | `GET /api/analysis/grid-result/<grid_id>`，`GET /api/analysis/grid-type-result/<grid_type_id>` | `web/webtest/stage4/test_task03_analysis_capability_sqlite.py`，`tests/test_lite_stage4_query_api_matrix.py` | 否 | 已覆盖 | 见文末 |
| 系统查询入口 smoke | `GET /token_test/result` | `tests/test_lite_smoke_validation_and_decision.py`，`tests/test_lite_stage4_query_api_matrix.py` | 否 | 已覆盖，聚合测试里也有真实请求，但只算 smoke，不算业务查询主面 | 见文末 |
| 查询读路径辅助链路 | `DataBox.fund_info`，`XaDataAdapter.get_daily`，`XaServiceAdapter.get_daily`，跨 app cache 读取路径 | `tests/test_lite_databox_stage4_coverage.py`，`tests/test_xalpha_databox_compat.py` | 是，建议只做缓存和运行时抽查 | 已覆盖，包含 xalpha compat 读取路径，不放进 HTTP 主表 | 见文末 |

## 固定回归命令

这条命令必须拆成两个 pytest 进程，不能把 `web/webtest` 和 `tests/` 混在同一个 pytest 里。

```bash
pytest web/webtest/stage4/test_task01_asset_management_sqlite.py web/webtest/stage4/test_task02_record_management_sqlite.py web/webtest/stage4/test_task03_analysis_capability_sqlite.py -q && pytest tests/test_lite_stage4_query_api_matrix.py tests/test_lite_databox_stage4_coverage.py tests/test_lite_smoke_validation_and_decision.py tests/test_xalpha_databox_compat.py -q
```

## 这轮没纳入的内容

- `GET /api/asset/list/select`
- `GET /api/asset/alias/list`
- `GET /api/record_list` 的更多筛选组合和分页边界
- 其他没被 task01 到 task04 明确覆盖的分析查询入口
- 真行情、真缓存后端、手工环境核验的完整验收
- `XaServiceAdapter` 之外的更多 xalpha 兼容行为
