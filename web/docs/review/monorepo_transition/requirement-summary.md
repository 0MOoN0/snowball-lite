# monorepo_transition 阶段总结

- 需求入口：`/Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition`
- 当前结论：Task 01 到 Task 03 已完成实现与正式评审；Task 05 与 Task 04 因 requirement 模式所需子代理连续命中额度限制而暂时阻塞
- 当前状态：部分完成，后续阻塞

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

## 当前基线

- 前端目录：`/Users/leon/projects/snowball-lite/apps/frontend`
- 根 workspace：`/Users/leon/projects/snowball-lite/pnpm-workspace.yaml`
- 前端默认运行口径：lite
- 后端 lite 联调入口：`LITE_FLASK_PORT=5001 python -m web.lite_application`
- 前端 lite 联调入口：`pnpm --dir /Users/leon/projects/snowball-lite/apps/frontend run dev:lite`

## 当前阻塞

- Task 05 需要新的实现代理，创建时连续返回额度限制错误
- Task 04 需要新的实现或探索代理，同样连续返回额度限制错误
- 阻塞原文：`You've hit your usage limit. To get more access now, send a request to your admin or try again at Mar 21st, 2026 2:23 AM.`

## 建议续跑顺序

1. 子代理额度恢复后，先继续 Task 05，建立根目录 `docs/` 和长期文档入口
2. Task 05 完成后，再推进 Task 04 的后端物理迁移
3. 如果要把“前端构建通过”纳入验收，再单独拆前端存量 TypeScript 错误清理任务
