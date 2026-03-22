# lite 迁移归档总览

## 这是什么

这里收的是 `snowball-lite` 从历史多环境 / MySQL 口径收口到 lite 主线过程中的归档文档。

如果你只是想看“现在应该怎么跑”，优先看这些长期文档：

- `README.md`
- `docs/backend/runtime-config.md`
- `apps/backend/web/docs/环境变量配置指南.md`

这里的 `desc/` 更偏向“当时为什么这么改、分几步改完、每一阶段验收了什么”。

## 目录怎么找

- `project/`
  - 跨阶段的长期归档，比如仓库基线、数据库分层、scheduler 接入、xalpha cache 收口
- `stage1/` 到 `stage6/`
  - 按 lite 改造阶段归档，每个目录下保留该阶段的设计、验证和验收结论

## 建议阅读顺序

1. 先看 `project/00_repo_baseline.md`
2. 再按需要看 `stage1/` 到 `stage6/`
3. 如果只关心某个专题，直接进 `project/` 找对应收口文档

## 和别的目录怎么区分

- `desc/lite_migration/`：lite 迁移和收口过程的归档
- `desc/monorepo_transition/`：仓库从旧目录结构迁到 monorepo 的归档
- `task/`：当前还在执行中的任务文档
