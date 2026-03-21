# backend 长期文档根目录收口（归档）

## 归档状态

- 状态：已完成
- 原任务文档：`apps/backend/web/docs/task/backend_docs_root_consolidation_design.md`
- 目标：明确 backend 长期文档哪些迁到根目录，哪些继续留在 `apps/backend/web/docs/`

## 归档结论

- 根目录 `docs/` 已成为 backend 长期文档的正式入口。
- backend 长期说明已经按“长期说明上收、执行档案原地保留”的口径完成收口。
- `apps/backend/web/docs/task/`、`review/`、`desc/` 继续保留在 backend 工作区，不作为长期文档根。
- 旧 backend 文档已经补上归档说明和新入口链接，避免继续双份正式维护。

## 实际落地范围

### 根目录长期文档

已新增这些长期文档：

- `docs/backend/system-overview.md`
- `docs/backend/runtime-config.md`
- `docs/backend/api-and-service-conventions.md`
- `docs/backend/lite-mysql-matrix.md`
- `docs/architecture/repo-baseline.md`
- `docs/architecture/lite-boundary.md`

### 入口更新

这些入口已经切到新的长期文档：

- `README.md`
- `docs/README.md`
- `docs/backend/README.md`
- `docs/architecture/README.md`

### 旧文档归档指针

这些旧文档顶部已经补了“当前长期版本见哪里”的指针：

- `apps/backend/web/docs/系统说明.md`
- `apps/backend/web/docs/环境变量配置指南.md`
- `apps/backend/web/docs/技术总结.md`
- `apps/backend/web/docs/轻量版分支改造方案.md`
- `apps/backend/web/docs/desc/lite_project/00_repo_baseline.md`
- `apps/backend/web/docs/desc/lite_project/01_lite_vs_mysql_component_matrix.md`

## 明确保留的边界

- `apps/backend/web/docs/task/`：活跃任务设计
- `apps/backend/web/docs/review/`：执行记录和评审产物
- `apps/backend/web/docs/desc/`：阶段归档和结论文档
- `doc/`：`xalpha` legacy 文档区

这次完成的是 backend 长期文档收口，不是把 backend 文档整目录搬出工作区。

## 验收结果

- 根目录 `docs/backend/` 和 `docs/architecture/` 已具备可直接使用的 backend 长期文档
- 新增长期 backend 文档已经切到根目录，不再继续落到 `apps/backend/web/docs/` 根下
- `task/review/desc` 保持原位，没有被错误迁移
- `README.md` 和 `docs/README.md` 已指向新的长期文档入口
- 旧文档和新文档的关系已经明确，不再出现两份同级正式说明并行维护

## 后续约束

1. 后续新增 backend 长期说明，默认放到 `docs/backend/` 或 `docs/architecture/`。
2. 阶段过程、任务设计、评审记录继续留在 `apps/backend/web/docs/` 的执行档案区。
3. 如果再做文档清理，优先继续处理归档价值低、且已经完全被新文档替代的旧文档。
