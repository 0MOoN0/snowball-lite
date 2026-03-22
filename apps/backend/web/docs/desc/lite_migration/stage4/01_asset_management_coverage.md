# 任务 1：资产基础管理能力覆盖（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 4 任务 1 资产基础管理能力覆盖（原 task 文档已清理）
- 当前状态：已完成
- 代码审查：已完成

## 实际结果

- 已补齐 `GET /api/asset/list/` 和 `GET /api/asset/<asset_id>` 的 SQLite 集成验证
- 已补齐 `AssetService.init_fund_asset_data` 写入后再通过 API 读取的闭环
- 已覆盖资产代码、主别名、基金日线、费用规则和持仓读取
- 在阶段收口时额外补上了 `fetch_online_daily_data()` 返回 `None` 时继续走 TTJJ fallback 的回归

## 主要落点

- `migrations_snowball_lite/versions/lite_stage3_baseline.py`
- `web/services/asset/asset_service.py`
- `web/webtest/stage4/test_task01_asset_management_sqlite.py`

## 主要验证

```bash
pytest web/webtest/stage4/test_task01_asset_management_sqlite.py -q
pytest web/webtest/stage4/test_task01_asset_management_sqlite.py -q -k 'should_fall_back_to_ttjj_when_xq_fetch_returns_none'
```

## 保留边界

- 当前结论只覆盖 lite 下的资产基础管理闭环
- 它不等于全部资产子类型、全部历史初始化路径或完整 lite schema 都已经收口
