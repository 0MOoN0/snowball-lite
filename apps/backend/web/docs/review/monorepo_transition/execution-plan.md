# monorepo_transition 执行计划

- 需求入口：`/Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition`
- 总览文档：`/Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition/00_overview.md`
- 当前模式：requirement
- 当前状态：Task 01 到 Task 05 已全部完成并通过正式评审
- 编排结论：按任务文档推荐顺序顺序推进；Task 05 可提前分析，但实现和收口放在 Task 03 之后，Task 04 继续压后

## 当前仓库事实

- 根目录还没有 `pnpm-workspace.yaml`
- 前端仍位于 `/Users/leon/projects/snowball-lite/snow_view`
- `snow_view/` 仍带有独立仓库痕迹：`.git`、`.github`、`.husky`、`.vscode`、`.cursor`、`.trae`、`node_modules`、`dist-dev`、`dist-pro`
- 根目录已有后端主工程 `web/`、测试目录 `tests/`、`xalpha/`，以及 `doc/` 旧文档目录
- 当前 git 状态里 `snow_view/` 是未跟踪目录，适合先在不打散后端代码的前提下完成前端收编

## 任务编排

| task_id | task_type | preconditions | deliverables | depends_on | write_scope | test_scope | can_analyze_with | can_implement_with | cannot_run_with | review_after | done_when |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Task 01 | repo cleanup | `snow_view/` 目录存在且尚未纳入 workspace | 清理 `snow_view/` 中独立仓库残留；前端 `package.json` 调整为 workspace 口径；必要 `.gitignore` / README / `.env` 示例策略更新 | 无 | `snow_view/**`，必要时根 `.gitignore` | `snow_view/package.json` 结构检查；前端安装脚本静态校验；必要最小命令验证 | Task 05 | 无，作为首个实现任务独立推进 | Task 02-04 | Task 01 staged diff | `snow_view/` 无 nested git / 构建垃圾 / 独立仓库目录，且包配置可被主仓纳入 |
| Task 02 | workspace bootstrap | Task 01 完成 | 根目录 `pnpm-workspace.yaml`；`apps/frontend/` 建立；`snow_view/` 迁入；根目录前端忽略规则和入口说明更新 | Task 01 | `apps/frontend/**`，根目录 `pnpm-workspace.yaml`、`.gitignore`、`README.md` | workspace 发现校验；`pnpm --dir apps/frontend` 或等价说明；路径回归 | Task 05 | Task 05 文档分析可并行；不与 Task 03/04 并行实现 | Task 03，Task 04 | Task 02 staged diff | 仓库能识别 `apps/frontend` 为正式 workspace，`snow_view/` 不再存在 |
| Task 03 | runtime alignment | Task 02 完成，`apps/frontend` 已稳定 | 前端代理 / base path / `.env.*` 工作区化；lite/dev 运行说明；最小联调验证 | Task 02 | `apps/frontend/**` 中运行配置、文档；必要时后端 CORS / 路径兼容点；`README.md` 或前端 README | 前端配置静态检查；能启动到当前后端；至少一组核心读链路验证；lite/dev 说明校验 | Task 05 | 可与 Task 05 文档收口部分并行分析，不能并行改相同 README 文档 | Task 04 | Task 03 staged diff | `apps/frontend` 可在主仓请求当前后端，且 lite/dev 差异有明确文档 |
| Task 04 | backend relocation | Task 03 完成，后端路径和前端联调口径稳定 | `apps/backend/` 建立；`web/` 迁入；后端入口、脚本、README、导入路径、测试路径调整 | Task 03 | `apps/backend/**`，根级 Python 入口，README，测试/脚本中的路径引用 | lite 启动、bootstrap、迁移脚本、关键 pytest 回归；与 `xalpha/` 兼容验证 | Task 05 | 无，路径敏感度最高，必须单独推进 | Task 02，Task 03，Task 05 的实际写入 | Task 04 staged diff | 后端主入口、bootstrap、迁移、关键测试可在 `apps/backend` 位置继续通过 |
| Task 05 | docs bootstrap | Task 02 完成，建议在 Task 03 之后执行 | 根目录 `docs/`；总入口；README 文档入口调整；长期文档落点说明 | Task 02 | `docs/**`，`README.md`，必要时文档索引 | README 链接校验；文档路径存在性检查 | Task 01-03 | 可与 Task 03 做文档分析并行；实现阶段避免与 Task 02/03 同时改同一 README 段落 | Task 02，Task 03，Task 04 | Task 05 staged diff | 根目录长期文档入口成立，且 `web/docs/task` / `web/docs/review` / `doc/` 边界说明清楚 |

## 代理编排

- orchestrator：主线程，负责计划、状态文件、依赖判断、阻塞升级、最终汇总
- implementer：按 task 粒度新起 worker，负责具体代码改动、开发测试和 task 状态更新建议
- reviewer：按 review 轮次新起 worker 或 explorer，负责 review 报告，不改生产代码

## 并行规则

- 当前只允许 Task 05 的分析与 Task 01-03 并行
- Task 02、Task 03、Task 05 都可能改 `README.md`，实现阶段默认串行
- Task 04 会改变后端物理路径，必须等 Task 03 完成后再实现
- 任一 task 的正式评审必须基于隔离好的 staged scope 或等价隔离范围

## 执行顺序

1. Task 01：前端源码收编与仓清洗，已完成
2. Task 02：根工作区与 `apps/frontend` 建立，已完成
3. Task 03：前端与当前后端运行口径对齐，已完成
4. Task 05：根目录 `docs/` 建立与长期文档收口，已完成
5. Task 04：后端应用工作区物理迁移，已完成

## 当前决定

- 已按最小可验证改动完成 Task 01，不提前挪后端目录
- 已在 Task 02 建立 `apps/frontend` workspace，并完成 Task 03 的 lite/dev 运行链路对齐
- 已完成 Task 05 的根 `docs/` 入口与长期文档边界收口
- Task 04 已按单独任务推进完成，真实后端代码进入 `apps/backend/web/`
- 根目录 `web` 保留为兼容符号链接，`apps/backend/xalpha` 保持对根目录 `xalpha/` 的兼容导入
