# monorepo 改造总览（归档）

## 当前状态

- 状态：已完成
- 归档位置：`apps/backend/web/docs/desc/monorepo_transition`
- 当前结构：仓库已形成 `apps/frontend` + `apps/backend/web` 双工作区结构
- 当前验收口径：真实后端目录是 `apps/backend/web`，不再依赖仓库根目录 `web` 符号链接
- 当前边界：`xalpha/` 和 `extends/` 本轮仍保持原位

## 归档结论

这轮 `monorepo_transition` 已按 5 个任务收口：

1. 前端源码收编与仓清洗
2. 根工作区与 `apps/frontend` 建立
3. 前端与当前后端运行口径对齐
4. 后端应用工作区物理迁移
5. 根目录文档入口建立与长期文档收口

当前结果是：

- 前端真实代码已经位于 `apps/frontend/`
- 后端真实代码已经位于 `apps/backend/web/`
- 根目录已建立 `pnpm-workspace.yaml`
- 根目录已建立统一长期文档入口 `docs/`
- lite 主链路已经完成前后端联调
- 本组 requirement 设计文档已经从 `apps/backend/web/docs/task/monorepo_transition` 归档到 `apps/backend/web/docs/desc/monorepo_transition`

## 最终基线

- 前端目录：`/Users/leon/projects/snowball-lite/apps/frontend`
- 后端目录：`/Users/leon/projects/snowball-lite/apps/backend/web`
- 后端代码目录：`/Users/leon/projects/snowball-lite/apps/backend/web`
- 根 workspace 配置：`/Users/leon/projects/snowball-lite/pnpm-workspace.yaml`
- 长期文档入口：`/Users/leon/projects/snowball-lite/docs/README.md`
- requirement 状态文档：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/review/monorepo_transition/requirement-status.md`

## 任务收口结果

| 任务 | 文档 | 收口结果 | 依赖 |
| --- | --- | --- | --- |
| Task 01 | `01_frontend_source_intake_design.md` | 已清理 `snow_view/` 的独立仓库残留，为前端进入 workspace 做好准备 | 无 |
| Task 02 | `02_workspace_root_bootstrap_design.md` | 已建立根工作区，并把前端迁到 `apps/frontend/` | Task 01 |
| Task 03 | `03_frontend_backend_runtime_alignment_design.md` | 已完成 lite/dev 运行口径对齐，核心读链路联调通过 | Task 02 |
| Task 04 | `04_backend_app_workspace_relocation_design.md` | 已把真实后端迁到 `apps/backend/web/`，当前验收不再依赖根目录 `web` | Task 03 + backend 收口归档 |
| Task 05 | `05_documentation_root_bootstrap_design.md` | 已建立根目录 `docs/`，并明确长期文档、执行文档、legacy 文档边界 | Task 02，建议在 Task 03 之后收口 |

## 本轮边界

- 不迁移 `xalpha/`
- 不迁移 `extends/`
- 不在本轮里把 Python 代码拆成多包发布
- 不在本轮里顺手解决全部前端历史接口差异

## 相关归档

- 执行计划：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/review/monorepo_transition/execution-plan.md`
- requirement 状态：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/review/monorepo_transition/requirement-status.md`
- requirement 总结：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/review/monorepo_transition/requirement-summary.md`
- 后续收尾归档：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/desc/monorepo_transition/06_remove_root_web_compat_entry/`
