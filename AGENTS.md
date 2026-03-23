# Snowball Lite 项目补充规则

本文件只写 `snowball-lite` 自己的事实、边界和目录约束。

- 生效范围：仓库根目录及全部子目录。
- 通用协作、表达方式、改动方式、提交格式等，沿用 Codex 全局规则，不在这里重复。
- `.agent/rules/project-rules.md` 只算历史参考，不再作为当前标准。

## 1. 项目定位

- 这是 `snowball-lite`，不是原始 `snowball` 主线仓库。
- 默认分支是 `main`，不要再按旧的 `master/dev` 语义理解项目流程。
- 当前主方向是 lite 轻量化收敛，不是完整生产能力补齐。
- `monorepo_transition` 已完成，当前目录口径以 `apps/frontend/` + `apps/backend/web/` 为准。
- lite 已完成阶段 1 到阶段 3，阶段 4 还没开始。
- 当前能说“lite 的 SQLite 可信度已经明显提升”，不能说“全仓库已经完成 SQLite 迁移”。

项目定位和阶段状态以这些文档为准：

- `README.md`
- `apps/backend/web/docs/轻量版分支改造方案.md`
- `apps/backend/web/docs/desc/lite_project/00_repo_baseline.md`
- `apps/backend/web/docs/desc/monorepo_transition/00_overview.md`
- `apps/backend/web/docs/task/lite_stage4/`

## 2. 默认工作口径

除非任务明确要求走旧环境，否则默认按 lite 主线处理。

- 默认运行环境：`SNOW_APP_STATUS=lite`
- 默认数据库：SQLite
- 默认目标：本地单机、弱依赖、最小可运行链路
- 默认不依赖 Redis、Dramatiq、APScheduler 持久化、flask-profiler

改动时先区分三类路径：

1. lite 主线路径
2. 历史 MySQL / 多环境兼容路径
3. 明确依赖 Redis、scheduler、task queue 的非 lite 能力

涉及第 1 类时，优先保证 lite 可跑、可测、可迁移。
涉及第 2 类时，不要顺手把历史能力改坏。
涉及第 3 类时，要写清楚 lite 下是跳过、降级还是不支持。

## 3. 关键目录

- `apps/backend/web/`：后端真实目录，包含模型、路由、服务、调度、任务、模板、迁移和项目文档。
- `apps/backend/weblogs/`：后端运行日志目录；当前应用日志和 gunicorn 日志都落在这里，不按 `apps/backend/web/logs/` 口径找日志。
- `apps/frontend/`：前端工作区。
- `xalpha/`：独立能力层和兼容适配代码。
- `tests/`：lite 运行链路、bootstrap、兼容验证。
- `apps/backend/web/webtest/`：Web 层、服务层、模型层、路由层集成测试。
- `apps/backend/web/migrations/lite/`：lite 的 SQLite 迁移基线。
- `apps/backend/web/migrations/dev/`、`apps/backend/web/migrations/stg/`、`apps/backend/web/migrations/test/`：历史多环境迁移目录。
- `docs/`：仓库级长期文档入口。
- `apps/backend/web/docs/desc/`：阶段归档和结论文档。
- `apps/backend/web/docs/task/`：当前阶段任务文档。
- `apps/backend/web/docs/review/`：评审、审查、阶段状态记录。

没有明确任务时，不要改这些协作目录：

- `.agent/`
- `.auto-claude/`
- `.cursor/`
- `.trae/`

## 4. 代码收敛方向

- 新增业务逻辑优先放 `apps/backend/web/services/`，不要继续往 router 里堆。
- 新增接口优先沿用 Flask-RESTX `Namespace` + Marshmallow `Schema`。
- 仓库里还有旧的 Blueprint / Flask-RESTful / `reqparse` 写法；兼容改老代码可以，但不要给新功能继续扩这种写法。
- 接口响应继续沿用 `R.ok(...)`、`R.fail(...)`、`R.paginate(...)`。
- 日志继续沿用 `web.weblogger`。

## 5. 数据库与 lite 约束

- 这个仓库现在是 SQLite / MySQL 双轨并存，触及 lite 主线路径时优先避免新增 MySQL 专有 SQL。
- 能用 SQLAlchemy 表达式就不要手写方言 SQL。
- 必须分方言处理时，要把 SQLite 和 MySQL 分支都写清楚。
- 模型仍按现有 `__bind_key__` 体系工作，不要随意改绑库方式。
- 影响 lite schema 的改动，要评估 `apps/backend/web/migrations/lite/` 是否需要同步。
- 影响 dev/stg/test 传统环境的改动，也要评估 `apps/backend/web/migrations/dev/`、`apps/backend/web/migrations/stg/`、`apps/backend/web/migrations/test/` 是否需要同步。
- lite 主线的 schema 演进优先走 `apps/backend/web/migrations/lite/` 和 `bootstrap_lite_database(...)`，不要把 `db.create_all()` 当迁移替代方案。
- 触及 Redis、scheduler、task queue、profiler 的代码时，先看 `ENABLE_*` 开关。
- lite 下明确不支持的能力，要在代码分支和文档里写清楚。

## 6. 测试与文档落点

- lite 运行链路、bootstrap、xalpha 兼容优先看 `tests/`。
- Flask 接口、服务、模型集成优先看 `apps/backend/web/webtest/`。
- lite 主线路径新增能力，优先补 SQLite 下可重复执行的测试。
- 牵涉 migration、lite bootstrap、阶段性结论时，优先补 `test_lite_*` 或 `apps/backend/web/webtest/` 下的对应验证。

## 7. Git 与规则冲突

- Git 基线分支是 `main`。
- 建议工作分支：`feature/*`、`fix/*`、`codex/*`。
- 当前仓库启用了 release-please，发布基于 `main` 自动推进。

## 8. Worktree 与依赖初始化

- 这个仓库允许用 `git worktree` 做隔离开发，但默认只共享 Git 对象库和包管理缓存，不共享 worktree 级安装结果。
- 默认 bootstrap 入口是仓库内的 `scripts/bootstrap-worktree.sh`；它只初始化“当前 worktree”，不会替别的 worktree 安装依赖。
- 后端默认使用 `uv` 管理当前 worktree 的 `.venv`，不要再按 `pyenv` 虚拟环境名来维护项目运行环境。
- `scripts/bootstrap-worktree.sh` 默认会执行：
  - `uv sync --python 3.11 --frozen --group dev`
  - `pnpm install --frozen-lockfile --prefer-offline`
- 仓库根目录的 `.python-version` 固定为 `3.11`，目的是让 `uv` 和本地解释器选择更稳定，不代表要使用 `pyenv virtualenv`。
- 允许共享的层级：
  - `pnpm` store
  - `uv` / `pip` 下载缓存
  - 其它只读或可重建缓存
- 默认不要手工共享这些 worktree 级状态：
  - `.venv`
  - `node_modules`
  - SQLite 运行库文件
  - 本地日志、测试缓存、临时输出
- 如果只需要一侧依赖，可用：
  - `scripts/bootstrap-worktree.sh --skip-frontend`
  - `scripts/bootstrap-worktree.sh --skip-backend`
- 本地个性化自动激活配置放本机，不进仓库主线；仓库只提供 `.envrc.example` 作为参考，真实 `.envrc` 保持未跟踪。

## 9. MCP 与浏览器联调

- 需要连接、检查或操作浏览器时，优先使用 `chrome devtools mcp`。
- 只有 `chrome devtools mcp` 明确不可用，或者当前目标必须依赖它不支持的能力时，才改用其他浏览器相关 MCP 或工具，并在过程说明里写清原因。

遇到规则冲突时，按下面顺序判断：

1. 当前代码和运行事实
2. `README.md`
3. lite 阶段文档和仓库基线文档
4. 本文件
5. `.agent/rules/project-rules.md` 历史内容
