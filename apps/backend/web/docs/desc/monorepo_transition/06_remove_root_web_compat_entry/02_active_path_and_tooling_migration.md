# Task 02：活跃路径与工具链迁移（归档）

## 任务状态

- 状态：已完成
- 优先级：高
- 目标：把仍在使用中的根目录 `web/...` 路径口径迁到真实后端目录
- 完成结果：README、backend README、docs 入口、环境说明和系统说明已切到 `apps/backend` / `apps/backend/web`

## 任务目标

这次任务只解决一件事：

- 把运行命令、工具配置、活跃说明文档中的根目录 `web/...` 路径迁到 `apps/backend/web/...` 或新的稳定入口

## 当前问题

当前还在用根目录 `web/...` 的地方不少，主要集中在：

- `README.md`
- `docker-compose.yml`
- `.vscode/launch.json`
- `apps/backend/README.md`
- 一部分仍在持续使用的后端说明文档

这些地方如果不先迁：

- 后面删掉根目录 `web` 后，开发者入口会直接失效
- 新人会继续把 `web/...` 当成真实路径

## 任务范围

优先改这些活跃入口：

1. 根 README
2. backend README
3. Docker / Compose 启动命令
4. VS Code 启动配置
5. 仍然被日常使用的环境和运行说明

## 迁移原则

- 路径说明优先写真实路径：`apps/backend/web/...`
- 命令说明优先写从 `apps/backend` 启动的口径
- 文档里不要再把根目录 `web` 写成当前事实
- 如果必须保留兼容说明，要明确写“历史兼容口径”，不能写成主路径

## 明确不做

- 不改历史归档文档里的全部旧路径
- 不处理所有低频历史脚本
- 不删除根目录 `web`

## 验收标准

完成后至少满足：

- README 和 backend README 不再把根目录 `web` 当成主路径
- compose / launch 的关键命令不再依赖根目录 `web/...`
- 日常启动和调试口径统一到 `apps/backend` 工作区

## 风险点

- 如果一把梭全改历史文档，会把任务拖成“大规模文档重写”
- 如果只改 README，不改 compose/launch，实际运行还是会卡

## 推荐测试

- 检查 README 中关键命令
- 检查 compose / launch 的关键字段
- 跑一条最小启动 smoke
