# Snowball Lite Web应用

从 `snowball` 拆出的轻量版后台服务基线。当前以 SQLite 单机链路和最小依赖运行能力为主，保留阶段一验证结果，并继续推进阶段二收敛工作。

**关键词**：Flask、SQLAlchemy、SQLite、Flask-RESTX、Jinja2、Akshare、xalpha

## Lite 项目基线

- 基线来源：原仓库 `snowball` 的 `codex/lite-spike`
- 来源提交：`8d803c37fd1d689aca862348814b34addc892967`
- 当前版本：`0.1.0`
- 默认分支：`main`
- 当前目标：继续完成 lite 项目的阶段二验证和收敛

详细说明见 `web/docs/desc/lite_project/00_repo_baseline.md`。

## 技术栈与架构

- 技术栈：`Flask 2.2`、`SQLAlchemy 1.4`、`APScheduler`、`Redis`、`Jinja2`、`Flask-RESTX 1.3.0`、`Dramatiq`
- 核心模块：`web/models` | `web/routers` | `web/services` | `web/scheduler` | `web/task` | `web/common`
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
python web/application.py
```

如果你就是要跑 lite 主线，推荐直接用专用入口，它会在启动前自动完成 SQLite bootstrap：

```bash
python -m web.lite_application
```

或使用 Flask CLI：

```bash
flask --app web.application:app run --host 0.0.0.0 --port 5001
```

4) 生产启动（Gunicorn）：

```bash
gunicorn -c web/gunicorn.config.py web.application:app
```

如果要用 lite 专用 Gunicorn 配置：

```bash
export LITE_DB_PATH=/absolute/path/to/snowball_lite.db
export LITE_XALPHA_CACHE_DIR=/absolute/path/to/lite_xalpha_cache
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
uv run --no-dev python -m web.lite_application
```

- `web/lite_application.py` 会自动固定 `SNOW_APP_STATUS=lite`
- 启动前会自动执行 `bootstrap_lite_database(...)`
- `--no-dev` 只安装运行应用所需依赖，不把 pytest 这类开发依赖一并拉进来
- 当前仓库的 `.python-version` 还是旧的 pyenv 虚拟环境名，`uv` 可能会提示一个 warning，但不影响 lite 启动
- 如果你要走 Gunicorn，改用 `gunicorn -c web/gunicorn_lite.config.py web.lite_application:app`

### Docker 启动

`docker-compose.yml` 已配置 `gunicorn` 与端口映射：

```bash
docker-compose up -d
```

注意将 `pushplus/telegram/chat_id` 与数据库、Redis 等环境变量在 shell 或 `.env` 中正确传递。

## 配置与环境变量

- 环境选择：`SNOW_APP_STATUS=dev|stg|test|lite`
- 开发环境端口：`DEV_FLASK_PORT`（默认 `15000`）
- 数据库：`DEV_DB_*` / `STG_DB_*`（见 `web/settings.py`）
- Redis：`DEV_REDIS_*` / `STG_REDIS_*`
- RESTX 文档路径：`RESTX_DOC=/docs`
- APScheduler：`SCHEDULER_API_ENABLED`、`SCHEDULER_TIMEZONE` 等

### Lite 模式

Lite 模式是这个仓库当前的默认验证入口，默认走 SQLite，并跳过 Redis、Dramatiq、APScheduler、flask-profiler。

```bash
export SNOW_APP_STATUS=lite
export LITE_DB_PATH=/absolute/path/to/snowball_lite.db
uv run --no-dev python -m web.lite_application
```

- `LITE_DB_PATH` 不传时，默认写到当前工作目录下的 `snowball_lite.db`
- Lite 模式只保证最小启动链路，不等同于完整生产能力
- 如果后续需要验证 scheduler 或异步任务，请切回 `dev/stg/test`
- 如果你本地创建了 `.vscode/launch.json`，可以直接使用 `Snowball Lite` 或 `Snowball Lite (Gunicorn)` 启动项

更多配置说明见 `web/docs/环境变量配置指南.md` 与 `web/settings.py` 注释。

## 数据库迁移

按环境使用独立迁移目录：`migrations_snowball_dev/`、`migrations_snowball_stg/`、`migrations_snowball_test/`。

```bash
export SNOW_APP_STATUS=dev
flask --app web.application:app db migrate -m "迁移描述" --directory migrations_snowball_dev
flask --app web.application:app db upgrade --directory migrations_snowball_dev
flask --app web.application:app db history --directory migrations_snowball_dev
flask --app web.application:app db downgrade --directory migrations_snowball_dev
```

最佳实践：确保模型注册到 `db`，迁移前在测试环境验证，必要时通过 MCP 服务检查 `alembic_version`。

## API 文档与约定

- 文档路径：访问 `http://localhost:5001/docs`
- 请求校验：采用 `Marshmallow Schema`；`@api_ns.expect(...)` 仅用于文档展示
- 响应格式：统一使用 `R.ok(...)` / `R.fail(...)` 包装
- 文档规范：详细写在接口 `docstring`，不直接返回 HTTP 状态码说明

更多规范见 `web/docs/技术总结.md` 与 `web/docs/系统说明.md`。

## 测试

测试位于 `web/webtest/`，使用 `pytest` 与标准 fixtures。回滚会话默认开启。

```bash
pytest -q
```

## 目录结构（关键模块）

- `web/application.py`：应用入口，按 `SNOW_APP_STATUS` 加载配置
- `web/models` | `web/services` | `web/routers`：数据模型、业务逻辑、API 路由
- `web/scheduler` | `web/task`：定时任务与异步任务
- `web/common`：工具、日志、配置与通用能力
- `web/docs`：业务与技术文档
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
