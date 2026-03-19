# 任务 4：xalpha / DataBox lite 能力覆盖

## 当前状态

- 状态：待开始
- 任务定位：补齐 lite 在 SQLite 下对 `xalpha` / DataBox 的目标能力覆盖

## 目标

把 `xalpha` / DataBox 从“有最小 smoke 和手工真实验证”推进到“lite 目标范围内更系统的可验证状态”。

这一任务要回答的问题是：

- lite 下 DataBox 的关键能力，是否已经不只是单点打桩 smoke
- lite 缓存路径和真实链路验收，是否已经形成清楚的边界

## 当前基础

目前已经有的基础主要是：

- `token_test/result` 已有最小 smoke
- `fund_info + get_daily` 已有手工真实链路验收
- 一些 DataBox / `xalpha` 兼容逻辑已经有单测

但现在还缺：

- 自动化近真实覆盖和手工真实覆盖之间的分层说明
- lite 目标范围内更清楚的 DataBox 能力边界
- 缓存写入、读取、复用行为的系统化验证

## 建议范围

- `get_rt` 的 lite 路径验证
- `fund_info` 的 lite 路径验证
- `get_daily` 的 lite 路径验证
- lite cache 目录下的写入与复用验证
- 自动化近真实验证和手工真实验收命令整理

## 建议优先覆盖的入口

- `GET /token_test/result`
- `DataBox.get_rt`
- `DataBox.fund_info`
- `XaDataAdapter.get_daily`

## 建议落点

- `web/databox/data_box.py`
- `web/databox/adapter/data/*`
- `web/routers/system/token_test_routers.py`
- `web/lite_validation.py`
- `tests/test_xalpha_databox_compat.py`
- `tests/test_lite_real_databox_validation.py`
- 建议新增测试：`tests/test_lite_databox_stage4_coverage.py`

## 建议实施方式

1. 先整理自动化近真实验证的失败测试
2. 再保留手工真实链路作为单独验收入口
3. 明确哪些异常属于第三方环境问题，哪些属于代码问题

## 验收标准

- 至少一条自动化近真实链路能覆盖 DataBox 的关键读取能力
- lite cache 写入和复用行为有明确验证
- 手工真实验收命令和判断口径清楚
- 不再只靠最底层单点打桩 smoke 支撑 DataBox 结论

## 非目标

- 不要求现在覆盖所有第三方 provider
- 不要求现在做大规模真实网络回归
- 不要求现在保证第三方环境始终稳定
