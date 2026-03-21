# Snowball Lite Web应用

从 `snowball` 拆出的轻量版后台服务基线。当前以 SQLite 单机链路和最小依赖运行能力为主，lite 阶段 1 到阶段 3 已完成，阶段 4 还没开始。

**关键词**：Flask、SQLAlchemy、SQLite、Flask-RESTX、Jinja2、Akshare、xalpha

## Lite 项目基线

- 基线来源：原仓库 `snowball` 的 `codex/lite-spike`
- 来源提交：`8d803c37fd1d689aca862348814b34addc892967`
- 当前版本：`0.1.0`
- 默认分支：`main`
- 当前目标：继续沿 lite 主线做收敛，但不把当前结果误写成“全仓库 SQLite 迁移完成”

详细说明见 `docs/architecture/repo-baseline.md`。

## 前端工作区

前端代码现在位于 `apps/frontend/`，并由根目录的 `pnpm-workspace.yaml` 纳入 monorepo。

在仓库根目录执行 `pnpm install` 后：

- 默认 lite 口径：`pnpm --dir apps/frontend run dev`，后端先 `cd apps/backend && python -m web.lite_application`，默认对齐 `5001`
- 历史 dev 口径：`pnpm --dir apps/frontend run dev:dev`，后端先 `cd apps/backend && SNOW_APP_STATUS=dev python -m web.application`，默认对齐 `15000`

前端自己的说明见 `apps/frontend/README.md`。lite 下 `scheduler` 和 `/system/token` 相关页面会显式降级，不按“全量可用”口径说明。

## 后端工作区

后端工作区现在从 `apps/backend/` 进入。真实后端代码位于 `apps/backend/web/`，常用启动、调试和文档入口都以这个工作区为准。

在仓库根目录执行 `cd apps/backend` 之后，再跑这些命令：

- `python -m web.lite_application`
- `SNOW_APP_STATUS=dev python -m web.application`
- `flask --app web.application:app run --host 0.0.0.0 --port 5001`
- `gunicorn -c web/gunicorn.config.py web.application:app`
- `gunicorn -c web/gunicorn_lite.config.py web.lite_application:app`

## 文档入口

仓库级长期文档入口见 [docs/README.md](docs/README.md)。

- `[docs/](docs)`：仓库级长期文档
- `[docs/backend/system-overview.md](docs/backend/system-overview.md)`：后端系统总览
- `[docs/backend/runtime-config.md](docs/backend/runtime-config.md)`：后端运行配置
- `[docs/backend/api-and-service-conventions.md](docs/backend/api-and-service-conventions.md)`：接口和服务写法
- `[docs/backend/lite-mysql-matrix.md](docs/backend/lite-mysql-matrix.md)`：lite 与 MySQL 对照
- `[docs/architecture/repo-baseline.md](docs/architecture/repo-baseline.md)`：仓库基线
- `[docs/architecture/lite-boundary.md](docs/architecture/lite-boundary.md)`：lite 边界
- `[apps/backend/web/docs/task/](apps/backend/web/docs/task)` 和 `[apps/backend/web/docs/review/](apps/backend/web/docs/review)`：执行文档
- `[apps/backend/web/docs/desc/](apps/backend/web/docs/desc)`：阶段归档和结论文档
- `[doc/](doc)`：`xalpha` 旧 Sphinx 文档区

## 技术栈与架构

- 技术栈：`Flask 2.2`、`SQLAlchemy 1.4`、`APScheduler`、`Redis`、`Jinja2`、`Flask-RESTX 1.3.0`、`Dramatiq`
- 核心模块：`apps/backend/web/models` | `apps/backend/web/routers` | `apps/backend/web/services` | `apps/backend/web/scheduler` | `apps/backend/web/task` | `apps/backend/web/common`
- 多数据库：使用 `__bind_key__` 绑定不同库；默认数据源用于数据存放，业务库用于业务实体
- 日志与规范：统一使用 `web.weblogger`，异常日志统一 `error(msg, exc_info=True)`
- 文档与约定：API 响应统一为 `{"code": xxx, "success": boolean, "message": "信息", "data": object}`

## 功能特性

- 数据盒（DataBox）：统一外部数据适配与指标能力扩展（Akshare 等），返回轻量 DTO
- 分析与网格：资产与网格策略分析、记录与可视化导出
- 通知与渠道：支持 `pushplus`、`Telegram` 等通知渠道，模板化输出
- 任务调度：`APScheduler` 定时任务，`Dramatiq` 异步任务与队列
- 多环境配置：`dev/stg/test` 独立配置、数据库与迁移目录
- API 文档：`Flask-RESTX` 文档挂载在 `RESTX_DOC=/docs`

## 快速开始

### 本地运行

1) 安装依赖：

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) 设置环境变量（推荐先走 `lite`）：

```bash
export SNOW_APP_STATUS=lite
export LITE_DB_PATH=/absolute/path/to/snowball_lite.db
```

3) 启动应用：

```bash
cd apps/backend
SNOW_APP_STATUS=dev python -m web.application
```

如果你就是要跑 lite 主线，推荐直接用专用入口，它会在启动前自动完成 SQLite bootstrap：

```bash
cd apps/backend
python -m web.lite_application
```

或使用 Flask CLI：

```bash
cd apps/backend
flask --app web.application:app run --host 0.0.0.0 --port 5001
```

4) 生产启动（Gunicorn）：

```bash
cd apps/backend
gunicorn -c web/gunicorn.config.py web.application:app
```

如果要用 lite 专用 Gunicorn 配置：

```bash
export LITE_DB_PATH=/absolute/path/to/snowball_lite.db
export LITE_XALPHA_CACHE_DIR=/absolute/path/to/lite_xalpha_cache
cd apps/backend
gunicorn -c web/gunicorn_lite.config.py web.lite_application:app
```

- 这份配置固定 `SNOW_APP_STATUS=lite`
- 单 worker
- 默认监听 `5002`，可用 `LITE_FLASK_PORT` 覆盖

### 使用 uv 启动 lite

如果本地使用 `uv`，推荐直接跑 lite 专用入口：

```bash
export LITE_DB_PATH=/absolute/path/to/snowball_lite.db
export LITE_XALPHA_CACHE_DIR=/absolute/path/to/lite_xalpha_cache
cd apps/backend
uv run --no-dev python -m web.lite_application
```

- `apps/backend/web/lite_application.py` 会自动固定 `SNOW_APP_STATUS=lite`
- 启动前会自动执行 `bootstrap_lite_database(...)`
- `--no-dev` 只安装运行应用所需依赖，不把 pytest 这类开发依赖一并拉进来
- 当前仓库的 `.python-version` 还是旧的 pyenv 虚拟环境名，`uv` 可能会提示一个 warning，但不影响 lite 启动
- 如果你要走 Gunicorn，改用 `cd apps/backend && gunicorn -c web/gunicorn_lite.config.py web.lite_application:app`

### Docker 启动

`docker-compose.yml` 已配置 `gunicorn` 与端口映射：

```bash
docker-compose up -d
```

注意将 `pushplus/telegram/chat_id` 与数据库、Redis 等环境变量在 shell 或 `.env` 中正确传递。

## 配置与环境变量

- 环境选择：`SNOW_APP_STATUS=dev|stg|test|lite`
- 开发环境端口：`DEV_FLASK_PORT`（默认 `15000`）
- 数据库：`DEV_DB_*` / `STG_DB_*`（见 `apps/backend/web/settings.py`）
- Redis：`DEV_REDIS_*` / `STG_REDIS_*`
- RESTX 文档路径：`RESTX_DOC=/docs`
- APScheduler：`SCHEDULER_API_ENABLED`、`SCHEDULER_TIMEZONE` 等

### Lite 模式

Lite 模式是这个仓库当前的默认验证入口，默认走 SQLite，并跳过 Redis、Dramatiq、APScheduler、flask-profiler。

```bash
export SNOW_APP_STATUS=lite
export LITE_DB_PATH=/absolute/path/to/snowball_lite.db
cd apps/backend
uv run --no-dev python -m web.lite_application
```

- `LITE_DB_PATH` 不传时，默认写到 `apps/backend/web/data/lite_runtime/snowball_lite.db`
- `apps/backend/web/data/lite_runtime/snowball_lite.db` 是 lite 的 stable/prod 长期业务库默认路径
- `apps/backend/web/data/lite_runtime/snowball_lite_dev.db` 是 lite 的 dev 长期开发库推荐路径
- `test` 口径默认使用 pytest 临时路径里的 SQLite 文件，文件名建议带 `pytest-` 前缀
- `stg` 不建议长期常驻；只在发版前演练或数据检查时，从 stable 复制快照，例如 `apps/backend/web/data/lite_runtime/snowball_lite_stg_YYYYMMDD.db`
- `LITE_XALPHA_CACHE_DIR` 不传时，默认写到 `apps/backend/web/data/lite_runtime/lite_xalpha_cache`
- 如果仓库根目录还留着旧的 `data/*.db` 或 `data/lite_xalpha_cache`，lite 启动时会自动迁到 `apps/backend/web/data/lite_runtime/`
- Lite 模式只保证最小启动链路，不等同于完整生产能力
- lite 默认关闭 scheduler；如果只是临时验证，可设置 `LITE_ENABLE_SCHEDULER=true`
- 如果需要持久化 jobstore，再加 `LITE_ENABLE_PERSISTENT_JOBSTORE=true` 和 `LITE_SCHEDULER_DB_PATH=/absolute/path/to/lite_scheduler.db`
- `LITE_SCHEDULER_DB_PATH` 不能和 `LITE_DB_PATH` 指向同一个 SQLite 文件
- 如果后续需要完整验证 scheduler 或异步任务，仍优先用 `dev/stg/test`
- 如果你本地创建了 `.vscode/launch.json`，可以直接使用 `Snowball Lite` 或 `Snowball Lite (Gunicorn)` 启动项

更多配置说明见 `docs/backend/runtime-config.md` 与 `apps/backend/web/settings.py` 注释。

## 数据库迁移

后端工作区的迁移目录已经收口到 `apps/backend/web/migrations/`：

- `apps/backend/web/migrations/dev/`
- `apps/backend/web/migrations/stg/`
- `apps/backend/web/migrations/test/`
- `apps/backend/web/migrations/lite/`

```bash
cd apps/backend
SNOW_APP_STATUS=dev flask --app web.application:app db migrate -m "迁移描述" --directory web/migrations/dev
SNOW_APP_STATUS=dev flask --app web.application:app db upgrade --directory web/migrations/dev
SNOW_APP_STATUS=dev flask --app web.application:app db history --directory web/migrations/dev
SNOW_APP_STATUS=dev flask --app web.application:app db downgrade --directory web/migrations/dev
```

Lite SQLite bootstrap 走 `bootstrap_lite_database(...)`，对应迁移基线在 `apps/backend/web/migrations/lite/`。
MySQL 到 Lite SQLite 的迁移脚本现在位于 `apps/backend/web/scripts/mysql_to_sqlite_lite_migration.py`。

## API 文档与约定

- 文档路径：访问 `http://localhost:5001/docs`
- 请求校验：采用 `Marshmallow Schema`；`@api_ns.expect(...)` 仅用于文档展示
- 响应格式：统一使用 `R.ok(...)` / `R.fail(...)` 包装
- 文档规范：详细写在接口 `docstring`，不直接返回 HTTP 状态码说明

更多规范见 `docs/backend/system-overview.md` 与 `apps/backend/web/docs/技术总结.md`。

## 测试

后端和 lite 主线测试现在统一收口到 `apps/backend/web/webtest/`，其中 lite 回归位于 `apps/backend/web/webtest/lite/`。
根目录 `tests/` 主要保留 `xalpha` 独立测试和 `web + xalpha` 混合测试。

当前测试口径分两层：

- `apps/backend/web/webtest/lite/` 和根目录 `tests/` 默认走 pytest 临时 SQLite 文件，不连接长期 lite 业务库
- 历史 `apps/backend/web/webtest/` 里仍有依赖 MySQL 测试库的老用例，当前应按文件范围单独执行，不建议直接全量 `pytest -q`

日常做 lite 回归时，先按范围拆开跑：

```bash
pytest apps/backend/web/webtest/lite -m "not manual" -q
pytest tests -m "not manual" -q
```

如果需要运行历史 MySQL 兼容层，显式执行：

```bash
pytest apps/backend/web/webtest -m mysql_integration -q
```

## 目录结构（关键模块）

- `apps/backend/web/application.py`：应用入口，按 `SNOW_APP_STATUS` 加载配置
- `apps/backend/web/models` | `apps/backend/web/services` | `apps/backend/web/routers`：数据模型、业务逻辑、API 路由
- `apps/backend/web/scheduler` | `apps/backend/web/task`：定时任务与异步任务
- `apps/backend/web/common`：工具、日志、配置与通用能力
- `apps/frontend`：前端工作区
- `apps/backend/web/migrations`：backend workspace 下的 Alembic 迁移目录
- `apps/backend/web/scripts`：backend workspace 下的后端脚本入口
- `apps/backend/web/dev_support`：本地开发辅助 SQL 和运维附属物
- `apps/backend/web/docs`：后端执行文档、任务设计和阶段归档
- `pnpm-workspace.yaml`：monorepo workspace 入口
- `docker-compose.yml`：容器化启动配置

## 发布与版本

- 分支策略：`main`（基线与发布） | `feature/*` | `fix/*` | `codex/*`
- 提交规范：`类型(范围): 描述`，如 `feat(api): 添加用户认证接口`
- 版本号与标签：当前从 `v0.1.0` 起步
- 自动发布：已配置 GitHub Actions：
  - `Release`（`push` 到 `main` 触发）：生成/更新发布 PR、合并后自动打标签并创建 Release
  - `Auto Merge Release PR`：当 PR 作者为 `github-actions[bot]` 且带有 `autorelease: pending` 标签时自动合并


查看最新标签：

```bash
git fetch --tags
git tag --sort=-version:refname | head -1
```

## 扩展指引（DataBox 简版）

- 新增能力：在 `interfaces/` 定义接口 → `models/` 定义最小 DTO → 适配器实现映射与异常处理 → 在 `registry/` 注册 provider
- 服务层与门面：严格模式校验能力，不返回 DataFrame，返回 DTO 或列表
- 日志：统一使用 `weblogger`；严格模式抛 `WebBaseException`

详细流程见项目内置规范说明。

## 许可证

本项目遵循 MIT License。详情见 `LICENSE`。
