# 任务 3：Lite 测试基建收敛

## 目标

把阶段一新增的 lite 测试再收敛一层，减少环境耦合和重复设置，让后续验证更稳定。

## 任务范围

- 收敛 lite 测试的环境变量设置
- 明确哪些测试应该走 `tmp_path`
- 明确哪些测试属于“纯单测”、哪些属于“受控集成验证”

## 当前问题

- lite 测试已经能避免污染仓库根目录，但测试入口还比较分散
- 真实网络验证和本地打桩验证的边界还不够清晰
- 还没有形成“第二阶段推荐怎么跑”的固定说明

## 关键文件

- `tests/conftest.py`
- `tests/test_lite_bootstrap_review.py`
- `tests/test_lite_sqlite_minimal_path.py`
- `tests/test_xalpha_databox_compat.py`
- `tests/test_lite_smoke_validation_and_decision.py`

## 执行步骤

1. 统一 lite 测试环境准备逻辑
2. 区分纯本地测试和外部依赖测试
3. 固定推荐执行命令
4. 补一份简短测试说明

## 验收标准

- lite 测试环境准备不再重复散落
- 测试分类清晰
- 推荐执行命令明确

## 非目标

- 不重建整个测试体系
- 不把所有历史测试都改成 lite 兼容

## 任务完成产物

- 一份 lite 测试运行说明
- 一组更清晰的 lite 测试边界
