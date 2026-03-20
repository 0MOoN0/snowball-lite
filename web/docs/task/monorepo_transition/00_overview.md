# monorepo 改造总览

## 当前状态

- 状态：待开始
- 总目标：把当前仓库收成可维护的 monorepo 形态
- 当前前提：`snow_view/` 已搬入仓库，但还保留独立仓库痕迹
- 当前边界：`xalpha/` 和 `extends/` 本轮不动

## 一句话结论

这轮 monorepo 改造建议按 5 个任务推进：

1. 前端源码收编与仓清洗
2. 根工作区与 `apps/frontend` 建立
3. 前端与当前后端运行口径对齐
4. 后端应用工作区物理迁移
5. 根目录文档入口建立与长期文档收口

## 当前已知前提

- 前端当前位于 `snow_view/`
- 后端目录收口第一阶段已经完成归档：
  - `web/docs/desc/lite_project/03_backend_workspace_consolidation.md`
- 这意味着当前不需要再重复做“后端目录先收口到 `web` 周边”这一步
- 后续可以直接在这个基线上推进 monorepo 物理重排

## 明确不做的事

- 不迁移 `xalpha/`
- 不迁移 `extends/`
- 不在本轮里把所有 Python 包重新拆成多包发布
- 不在本轮里解决所有前端历史接口与 lite 差异

## 任务拆分

| 任务 | 文档 | 目标 | 依赖 |
| --- | --- | --- | --- |
| Task 01 | `01_frontend_source_intake_design.md` | 把 `snow_view/` 清理成可纳入主仓的前端源码工作区 | 无 |
| Task 02 | `02_workspace_root_bootstrap_design.md` | 建立根工作区和 `apps/frontend` 结构 | Task 01 |
| Task 03 | `03_frontend_backend_runtime_alignment_design.md` | 让前端在当前仓库里和后端跑通主链路 | Task 02 |
| Task 04 | `04_backend_app_workspace_relocation_design.md` | 把后端从当前根目录形态迁到 `apps/backend` | Task 03 + backend 收口归档 |
| Task 05 | `05_documentation_root_bootstrap_design.md` | 建根目录 `docs/` 并收口长期文档 | Task 02，建议在 Task 03 之后收口 |

## 推荐顺序

1. 先做 Task 01，清掉前端独立仓库包袱
2. 再做 Task 02，把前端正式纳入 monorepo 工作区
3. 接着做 Task 03，把前端和当前后端先跑通
4. 等运行口径稳定后，再做 Task 04，把后端物理迁到 `apps/backend`
5. Task 05 放在后半段做，避免文档路径在前几轮频繁变化

## 完成标准

完成这 5 个任务后，仓库应当至少满足：

- 前端是正式的 workspace，不再是嵌套独立仓库
- 根目录具备 monorepo 工作区入口
- 前端和后端可以在同仓协同运行
- 后端有明确的 `apps/backend` 位置
- 根目录有统一的 `docs/` 文档入口
- `xalpha/` 仍保持独立，不被这轮改造打穿
