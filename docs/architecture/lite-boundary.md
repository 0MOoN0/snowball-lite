# Lite Boundary

这份文档只保留 lite 的边界口径，主要说清楚什么是 lite 主线，什么不是。

## 当前定位

- lite 是从原始 `snowball` 拆出来的轻量版主线
- 当前目标是本地单机、弱依赖、最小可运行链路
- lite 已经完成阶段 1 到阶段 3 的主线收口，阶段 4 还没开始

## lite 主线保留什么

- SQLite 本地运行链路
- 资产、记录、基础分析这些核心业务
- `xalpha` / DataBox 拉数
- 必要的查询类 API

## lite 主线默认不依赖什么

- Redis
- Dramatiq 常驻 worker
- APScheduler 持久化 JobStore
- `flask-profiler`

## 需要特别分清的三类路径

1. lite 主线路径
2. 历史 MySQL / 多环境兼容路径
3. 明确依赖 Redis、scheduler、task queue 的非 lite 能力

处理代码时的原则很简单：

- 第 1 类先保证 lite 可跑、可测、可迁移
- 第 2 类不要顺手改坏
- 第 3 类要写清楚是跳过、降级还是不支持

## 目录边界

- `docs/architecture/` 放仓库边界和基线
- `docs/backend/` 放后端长期说明
- `apps/backend/web/docs/task/`、`review/`、`desc/` 继续放执行档案

## 相关文档

- [Architecture Docs README](README.md)
- [Repo Baseline](repo-baseline.md)
- [Backend System Overview](../backend/system-overview.md)
