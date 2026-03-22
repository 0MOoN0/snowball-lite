# 任务 1：真实 DataBox 验证结果

## 结论

阶段二真实链路选择了 `fundinfo + get_daily`，没有继续把 `token_test/result` 当作第一优先。

原因很直接：

- 这条链路不依赖雪球 token，更适合做可重复验证
- 它同样覆盖了真实的 `DataBox -> xalpha` 过程
- 在 lite 模式下更稳定，也更容易区分代码问题和第三方环境问题

## 本轮实现

- 新增测试：`tests/test_lite_real_databox_validation.py`
- 新增辅助模块：`web/lite_validation.py`

真实验证覆盖：

- `DataBox.fund_info("000001")`
- `data_box.xa_adapter.get_daily(start_date=datetime(2024, 1, 1), end_date=datetime(2024, 1, 5))`

## 推荐运行方式

默认不自动执行，避免把第三方网络波动混进本地回归：

```bash
PYTHONPATH=. pytest -q tests/test_lite_real_databox_validation.py
```

2026-03-19 结果：

- `3 passed, 1 skipped`

真实验收：

```bash
PYTHONPATH=. LITE_RUN_REAL_DATABOX=1 pytest -q tests/test_lite_real_databox_validation.py
```

2026-03-19 结果：

- `4 passed`

## 已验证通过

- `fund_info("000001")` 能真实返回基金信息
- `get_daily()` 能真实返回日线数据
- lite 默认 CSV cache 会落地缓存文件
- 第二次读取能够复用同一份基金信息缓存

## 失败分类

本轮把真实链路失败分成两类：

- `external_env`：第三方站点或网络问题
- `code`：代码逻辑问题、断言失败、参数错误

这样做的目的，是避免把外部波动误报成 lite 代码失败。

## 当前边界

- `XaDataAdapter.get_daily()` 需要传 `datetime`
- 真实链路依然依赖第三方可用性

## 结论

任务 1 已完成。
