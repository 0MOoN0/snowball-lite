# Repo Baseline

这份文档是 `snowball-lite` 当前仓库基线的长期版本，吸收了历史 baseline 文档中仍然有效的内容。

## 项目定位

- 这是 `snowball-lite`，不是原始 `snowball` 主线仓库
- 默认分支是 `main`
- `monorepo_transition` 已完成，当前目录口径以 `apps/frontend/` + `apps/backend/web/` 为准
- 当前主方向是 lite 轻量化收敛，不是完整生产能力补齐

## 当前阶段状态

- lite 阶段 1 到阶段 3 已完成
- 阶段 4 还没开始
- 当前能说“lite 的 SQLite 可信度已经明显提升”
- 不能说“全仓库已经完成 SQLite 迁移”

## 默认工作口径

除非任务明确要求走旧环境，否则默认按 lite 主线处理：

- `SNOW_APP_STATUS=lite`
- SQLite
- 本地单机、弱依赖、最小可运行链路
- 默认不依赖 Redis、Dramatiq、APScheduler 持久化、`flask-profiler`

改动时要先区分三类路径：

1. lite 主线路径
2. 历史 MySQL / 多环境兼容路径
3. 明确依赖 Redis、scheduler、task queue 的非 lite 能力

## 仓库结构

| 路径 | 说明 |
| --- | --- |
| `apps/backend/web/` | 后端真实目录，包含模型、路由、服务、调度、任务、模板、迁移和项目文档 |
| `apps/frontend/` | 前端工作区 |
| `xalpha/` | 独立能力层和兼容适配代码 |
| `tests/` | lite 运行链路、bootstrap、兼容验证 |
| `apps/backend/web/webtest/` | Web 层、服务层、模型层、路由层集成测试 |
| `docs/` | 仓库级长期文档入口 |
| `apps/backend/web/docs/` | 后端执行文档和阶段归档区，不是新的长期文档根 |

## 文档边界

backend 文档采用“长期说明上收、执行档案原地保留”的口径：

- `docs/backend/`：后端长期说明
- `docs/architecture/`：仓库边界、基线和目录职责
- `apps/backend/web/docs/task/`：任务设计
- `apps/backend/web/docs/review/`：执行记录和评审产物
- `apps/backend/web/docs/desc/`：阶段归档和结论文档
- `doc/`：`xalpha` legacy Sphinx 文档区

## Git 基线

- 默认分支：`main`
- 当前版本：`0.1.0`
- 建议工作分支：`feature/*`、`fix/*`、`codex/*`
- 当前仓库启用了 release-please，发布基于 `main` 自动推进

## 当前不做的事

- 不继续复用原仓库的 `master/dev` 分支语义
- 不把历史 MySQL 能力直接等同成 lite 主线能力
- 不把历史阶段归档文档误写成当前正式说明
- 不把 `apps/backend/web/docs/task/`、`review/`、`desc/` 直接搬到根目录长期文档区

## 相关文档

- [Architecture Docs README](README.md)
- [Backend System Overview](../backend/system-overview.md)
- [Runtime Config](../backend/runtime-config.md)
- 历史归档：`apps/backend/web/docs/desc/lite_migration/project/00_repo_baseline.md`
