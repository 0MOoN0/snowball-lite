# 任务 02：零 MySQL 环境下的 lite 核心业务验收（归档）

## 完成状态

- 已完成
- 结论：资产、记录、分析、查询、DataBox 和 xalpha 这批 lite 主线能力已经在纯 SQLite 环境下通过

## 实际覆盖面

- `web/webtest/stage4/` 下的资产、记录、分析 3 条核心业务闭环
- `tests/test_lite_smoke_validation_and_decision.py`
- `tests/test_lite_stage4_query_api_matrix.py`
- `tests/test_lite_databox_stage4_coverage.py`
- `tests/test_xalpha_databox_compat.py`
- `web/webtest/stage3/test_task03_runtime_mysql_specific_sql_cleanup.py`

## 验证结果

- 核心业务固定命令：
  `python -m pytest web/webtest/stage4/test_task01_asset_management_sqlite.py web/webtest/stage4/test_task02_record_management_sqlite.py web/webtest/stage4/test_task03_analysis_capability_sqlite.py -q`
  结果：`5 passed, 30 warnings`
- 查询 / smoke / DataBox / xalpha / runtime cleanup 固定命令：
  `python -m pytest tests/test_lite_smoke_validation_and_decision.py tests/test_lite_stage4_query_api_matrix.py tests/test_lite_databox_stage4_coverage.py tests/test_xalpha_databox_compat.py web/webtest/stage3/test_task03_runtime_mysql_specific_sql_cleanup.py -q`
  结果：`24 passed, 120 warnings`

## 运行事实

- 资产管理的 fund 数据初始化、明细查询和最新数据读取已经能在 SQLite 下闭环
- 记录管理、分析能力和查询 API 组合矩阵已经能在 lite 环境下重复通过
- DataBox / xalpha 仍有 pandas、BeautifulSoup 和 SQLite Decimal 相关 warning，但当前只属于已知 warning，不构成阶段 6 blocker

## 本任务结论

- lite 主线核心业务已经不再依赖 MySQL server
- 查询主面和近真实数据链路已经纳入纯 SQLite 口径
- 当前仍保留的 warning 不影响“lite 主线已脱离 MySQL”的阶段判断
