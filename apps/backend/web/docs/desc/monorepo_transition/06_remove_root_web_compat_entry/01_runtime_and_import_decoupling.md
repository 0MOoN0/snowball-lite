# Task 01：运行与导入解耦（归档）

## 任务状态

- 状态：已完成
- 优先级：高
- 目标：让后端运行和 Python 导入不再依赖仓库根目录 `web` 符号链接
- 完成结果：根目录 `pytest` 入口和 `apps/backend` 工作区入口都已直接解析到 `apps/backend/web`

## 任务目标

这次任务只解决一件事：

- 在不删除 `web` 包名的前提下，先去掉“必须依赖仓库根目录 `web` 符号链接”这层运行依赖

## 当前问题

当前真实代码已经在 `apps/backend/web/`，但还有一个隐含前提没有拆掉：

- 有些启动方式、测试方式、导入方式默认把根目录 `web` 当成存在前提

如果不先做这一步，后面一旦删掉根目录 `web`，最容易直接炸的是：

- `import web`
- `python -m web.application`
- `python -m web.lite_application`
- 依赖 `web.application:app` 的运行入口

## 任务范围

优先检查和处理这些点：

1. Python 路径引导
   - `apps/backend/sitecustomize.py`
   - 其他启动时自动补 `sys.path` 的入口

2. 根目录启动与测试时的导入口径
   - 从仓库根目录运行 pytest
   - 从 `apps/backend` 运行 Python 模块

3. 保留 `web` 作为包名的实现方式
   - 目标是“继续 `import web`”
   - 不是“把全仓 import 都改成别的包名”

## 推荐方案

采用“保留包名 `web`，去掉根目录路径别名”的方案。

建议实现方向：

- 把 Python 导入基线明确固定到 `apps/backend`
- 让运行入口和测试入口都能找到 `apps/backend/web`
- 不再把根目录 `web` 当成包发现入口

## 明确不做

- 不改包名
- 不大规模改 README 和工具文档
- 不删除根目录 `web`

## 验收标准

完成后至少满足：

- 从仓库根目录运行核心 pytest 子集时，`import web` 仍可用
- 从 `apps/backend` 运行 `python -m web.lite_application` 仍可用
- 不依赖仓库根目录 `web` 符号链接也能完成上述导入与启动

## 风险点

- 如果误把“去掉根目录 `web`”理解成“改 Python 包名”，改动面会急剧放大
- 如果只改 `apps/backend` 的启动口径，不改仓库根目录测试入口，后续删链接仍会有遗漏

## 推荐测试

- 一条从 `apps/backend` 启动 lite 的 smoke
- 一条从仓库根目录导入 `web` 的 smoke
- 一条最小 pytest 导入链路验证
