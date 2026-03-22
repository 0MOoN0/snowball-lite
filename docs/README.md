# Snowball Lite Docs

这里是仓库级长期文档入口。

## 目录分工

- `docs/architecture/`：仓库边界、目录约定、模块关系
- `docs/backend/`：后端长期说明、运行、配置、数据库、接口规范
- `docs/frontend/`：前端长期说明、构建、接入、发布
- `docs/xalpha/`：`xalpha` 的协作文档入口
- `docs/adr/`：架构决策记录
- `docs/ops/`：部署、运维、值守说明

## 当前边界

- `[apps/backend/web/docs/task/](../apps/backend/web/docs/task)` 和 `[apps/backend/web/docs/review/](../apps/backend/web/docs/review)` 继续作为执行文档区，不搬到这里
- `[apps/backend/web/docs/desc/](../apps/backend/web/docs/desc)` 继续保留阶段归档和结论文档，后续再按主题逐步收口
- `[doc/](../doc)` 继续作为 `xalpha` 的旧 Sphinx 文档区
- 前端工作区说明见 `[apps/frontend/README.md](../apps/frontend/README.md)`

## 当前入口

- 后端长期说明入口：`[docs/backend/](backend)`
- 后端系统总览：`[docs/backend/system-overview.md](backend/system-overview.md)`
- 后端运行配置：`[docs/backend/runtime-config.md](backend/runtime-config.md)`
- 后端接口和服务约定：`[docs/backend/api-and-service-conventions.md](backend/api-and-service-conventions.md)`
- 后端 lite/MySQL 对照：`[docs/backend/lite-mysql-matrix.md](backend/lite-mysql-matrix.md)`
- 前端长期说明入口：`[docs/frontend/](frontend)`
- 架构入口：`[docs/architecture/](architecture)`
- 仓库基线：`[docs/architecture/repo-baseline.md](architecture/repo-baseline.md)`
- lite 边界：`[docs/architecture/lite-boundary.md](architecture/lite-boundary.md)`
- `xalpha` 入口：`[docs/xalpha/](xalpha)`

## 归档与历史指针

- 后端旧系统说明：`[apps/backend/web/docs/系统说明.md](../apps/backend/web/docs/系统说明.md)`
- 后端旧环境说明：`[apps/backend/web/docs/环境变量配置指南.md](../apps/backend/web/docs/环境变量配置指南.md)`
- lite 仓库旧 baseline：`[apps/backend/web/docs/desc/lite_migration/project/00_repo_baseline.md](../apps/backend/web/docs/desc/lite_migration/project/00_repo_baseline.md)`
- lite 改造方案：`[apps/backend/web/docs/轻量版分支改造方案.md](../apps/backend/web/docs/轻量版分支改造方案.md)`
- 前端工作区说明：`[apps/frontend/README.md](../apps/frontend/README.md)`
- `xalpha` 文档入口：`[doc/source/index.rst](../doc/source/index.rst)`
