# 任务 4：收口 lite 运行时外部依赖边界（归档）

## 归档说明

- 归档时间：`2026-03-19`
- 归档来源：阶段 5 任务 4 lite 运行时边界收口（原 task 文档已清理）
- 当前状态：已完成
- 代码审查：已完成

## 实际结果

- `web/routers/system/system_data_routers.py` 已为 `/system/token` 的 GET / PUT 增加显式 Redis 边界判断，lite 下会返回“明确不支持”，不再隐式报 500
- `web/routers/system/enum_version_routers.py` 已为 `/api/enums/versions` 增加同样的 lite 边界分支，Redis 未启用时会返回可解释的失败消息
- 已新增 `tests/test_lite_runtime_dependency_boundary.py`，固定验证上述两个接口在 lite 下的降级行为
- 这一步把 lite 的外部依赖口径继续收清楚了：默认关闭 Redis、scheduler、task queue、profiler 时，主线启动和已有业务 smoke 仍应稳定；依赖 Redis 的系统接口则明确列为 lite 不支持

## 主要落点

- `web/routers/system/system_data_routers.py`
- `web/routers/system/enum_version_routers.py`
- `tests/test_lite_runtime_dependency_boundary.py`

## 主要验证

```bash
pytest tests/test_lite_runtime_dependency_boundary.py -q
pytest tests/test_lite_bootstrap_review.py tests/test_lite_smoke_validation_and_decision.py -q
```

## 保留边界

- 当前只把 lite 主线已经碰到的 Redis 依赖接口改成显式边界，不等于所有外围接口都已完成同等级降级
- 这一阶段没有尝试在 lite 下恢复完整 scheduler / task queue 功能，口径仍然是默认关闭并明确不支持相关外围能力
