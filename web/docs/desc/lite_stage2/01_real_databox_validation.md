# 任务 1：真实 DataBox 验证

## 目标

把阶段一里“最小 DataBox 运行路径”再往前推进一层，补一条更真实的验证链路。

这里的“更真实”指的是：

- 不再只停留在接口入口和 adapter 边界
- 至少让一次真实的 `DataBox -> XaDataAdapter -> xalpha` 过程跑通

## 任务范围

- 选择 1 条最适合验证的 DataBox 链路
- 确定是走手工脚本、集成测试，还是受控网络验证
- 记录真实链路里遇到的 token、网络、缓存问题

## 推荐优先链路

优先看这两条：

1. `token_test/result` 对应的实时数据链路
2. 一条 `fundinfo` / 日线缓存链路

## 关键文件

- `web/routers/system/token_test_routers.py`
- `web/databox/data_box.py`
- `web/databox/adapter/data/xa_data_adapter.py`
- `web/databox/adapter/data/xa_service.py`
- `tests/test_lite_smoke_validation_and_decision.py`

## 执行步骤

1. 选定一条真实链路
2. 明确 token 和外部依赖的准备方式
3. 增加一份手工验证脚本或受控测试
4. 记录真实失败点和回退策略

## 验收标准

- 至少 1 条真实 DataBox 链路跑通
- 能明确区分“代码问题”和“第三方环境问题”
- 有一份可重复执行的验证说明

## 非目标

- 不要求所有数据源都验证
- 不要求把网络依赖完全自动化

## 任务完成产物

- 一份真实 DataBox 验证记录
- 一份失败点和回退策略说明
