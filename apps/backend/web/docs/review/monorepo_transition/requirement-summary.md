# monorepo_transition 阶段总结

- 需求入口：`/Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition`
- 当前结论：Task 01 到 Task 05 已全部完成实现与正式评审；当前 monorepo 已形成 `apps/frontend` + `apps/backend/web` 的双工作区结构，根目录 `web` 保留为兼容符号链接，`xalpha/` 继续保留在仓库根目录
- 当前状态：已完成

## 已完成任务

1. Task 01：前端源码收编与仓清洗
   - `snow_view/` 已清理独立仓库残留
   - 对应状态：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/task-status.md`
   - 对应评审：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/round-01-review.md`
2. Task 02：根工作区与 `apps/frontend` 建立
   - 前端已迁到 `apps/frontend/`
   - 根目录已建立 `pnpm-workspace.yaml`
   - 对应状态：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/02_workspace_root_bootstrap/task-status.md`
   - 对应评审：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/02_workspace_root_bootstrap/round-02-review.md`
3. Task 03：前端与当前后端运行口径对齐
   - lite/dev 双口径已拆分
   - lite 本地会话引导已补齐
   - `/system/settings/` 和 `/api/asset/list/` 已经通过 Vite 代理实测打通
   - 对应状态：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/03_runtime_alignment/task-status.md`
   - 对应评审：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/03_runtime_alignment/round-01-review.md`
4. Task 05：根目录 `docs/` 建立与长期文档收口
   - 根目录长期文档入口已建立
   - `web/docs/task`、`web/docs/review`、`doc/` 边界已写清楚
   - 对应状态：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/05_docs_bootstrap/task-status.md`
   - 对应评审：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/05_docs_bootstrap/round-02-review.md`
5. Task 04：后端应用工作区物理迁移
   - 真实后端代码已迁到 `apps/backend/web/`
   - 根目录 `web` 保留兼容符号链接，`apps/backend/xalpha` 保持对根目录 `xalpha/` 的兼容导入
   - `apps/backend` 口径下的 lite 入口、backend path 回归、Gunicorn 配置检查和 Task 01/03/04/05 定向回归均已通过
   - 对应状态：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/04_backend_workspace_relocation/task-status.md`
   - 对应评审：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/04_backend_workspace_relocation/round-01-review.md`

## 当前基线

- 前端目录：`/Users/leon/projects/snowball-lite/apps/frontend`
- 后端目录：`/Users/leon/projects/snowball-lite/apps/backend/web`
- 根 backend 兼容入口：`/Users/leon/projects/snowball-lite/web`
- 根 workspace：`/Users/leon/projects/snowball-lite/pnpm-workspace.yaml`
- 前端默认运行口径：lite
- 后端推荐运行口径：`cd /Users/leon/projects/snowball-lite/apps/backend && python -m web.lite_application`

## 残余风险

- 如果后续把“前端构建通过”也纳入这轮 requirement 的硬验收，需要单独处理前端已有的 TypeScript 存量错误；当前没有证据表明这些错误是 monorepo_transition 新引入的

## 建议下一步

1. 如果你要先收这轮 monorepo 改造，可以直接以当前 requirement 完整状态提交
2. 如果你要继续扩验收范围，建议单独拆前端 TypeScript 存量清理任务，不和本轮 monorepo 结构迁移混在一起
