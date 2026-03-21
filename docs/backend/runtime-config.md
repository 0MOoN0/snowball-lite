# Runtime Config

这份文档只保留当前还有效的运行配置口径。默认先按 lite 主线看，再看历史多环境兼容路径。

## 默认口径

- 默认环境：`SNOW_APP_STATUS=lite`
- 默认数据库：SQLite
- 默认目标：本地单机、弱依赖、最小可运行链路
- 默认不依赖 Redis、Dramatiq、APScheduler 持久化、`flask-profiler`

## lite 快速启动

推荐命令：

```bash
export SNOW_APP_STATUS=lite
export LITE_DB_PATH=/absolute/path/to/snowball_lite.db
cd apps/backend
python -m web.lite_application
```

如果本地使用 `uv`：

```bash
export LITE_DB_PATH=/absolute/path/to/snowball_lite.db
export LITE_XALPHA_CACHE_DIR=/absolute/path/to/lite_xalpha_cache
cd apps/backend
uv run --no-dev python -m web.lite_application
```

## lite 关键变量

| 变量 | 作用 | 默认/约束 |
| --- | --- | --- |
| `SNOW_APP_STATUS` | 选择运行环境 | lite 主线固定为 `lite` |
| `LITE_DB_PATH` | lite SQLite 文件路径 | 默认落到 `apps/backend/web/data/lite_runtime/snowball_lite.db` |
| `LITE_XALPHA_CACHE_DIR` | lite 下 `xalpha` CSV 缓存目录 | 默认落到 `apps/backend/web/data/lite_runtime/lite_xalpha_cache` |
| `LITE_XALPHA_CACHE_BACKEND` | lite 下缓存后端 | 默认 `csv` |
| `LITE_XALPHA_CACHE_SQLITE_PATH` | lite 下 SQL cache 路径 | 仅在特殊场景需要 |
| `LITE_FLASK_PORT` | lite 入口监听端口 | 默认 `5001` |
| `LITE_ENABLE_SCHEDULER` | 是否临时启用 scheduler | 默认关闭 |
| `LITE_ENABLE_PERSISTENT_JOBSTORE` | 是否启用持久化 JobStore | 默认关闭 |
| `LITE_SCHEDULER_DB_PATH` | lite scheduler SQLite 路径 | 只有启用持久化 JobStore 时才需要，且不能与 `LITE_DB_PATH` 指向同一文件 |

补充说明：

- lite 入口会自动把 `SNOW_APP_STATUS` 固定成 `lite`
- lite 启动前会执行 `bootstrap_lite_database(...)`，不要把 `db.create_all()` 当迁移替代方案
- 如果仓库根目录还有旧的 `data/*.db` 或 `data/lite_xalpha_cache`，lite 启动时会自动迁到 `apps/backend/web/data/lite_runtime/`
- test 口径默认应使用 pytest 临时路径里的 SQLite 文件，不要直接指向 stable/prod 或 dev 长期库

## 历史多环境变量

lite 之外，仓库仍保留传统环境配置：

| 环境 | 主要数据库变量 | 主要 Redis/端口变量 |
| --- | --- | --- |
| `dev` | `DEV_DB_USERNAME`、`DEV_DB_PASSWORD`、`DEV_DB_HOST`、`DEV_DB_PORT`、`DEV_DB_DATABASE`、`DEV_DB_PROFILER` | `DEV_REDIS_*`、`DEV_FLASK_PORT` |
| `stg` | `STG_DB_USERNAME`、`STG_DB_PASSWORD`、`STG_DB_HOST`、`STG_DB_PORT`、`STG_DB_DATABASE`、`STG_DB_PROFILER`、`STG_DB_DATA` | `STG_REDIS_*` |
| `prod` | `PROD_DB_USERNAME`、`PROD_DB_PASSWORD`、`PROD_DB_HOST`、`PROD_DB_PORT`、`PROD_DB_DATABASE` | `PROD_REDIS_*` |
| `local_dev_test` | `LOCAL_DEV_DB_USERNAME`、`LOCAL_DEV_DB_PASSWORD`、`LOCAL_DEV_DB_HOST`、`LOCAL_DEV_DB_PORT`、`LOCAL_DEV_DB_DATABASE`、`LOCAL_DEV_DB_PROFILER`、`LOCAL_DEV_DB_DATA` | `LOCAL_DEV_REDIS_*` |

这些环境仍然默认走 MySQL + Redis 组合，不属于 lite 的默认承诺范围。

## 通用注意事项

- 数据库密码里如果有 `@`、`%`、`/` 之类特殊字符，配置层会做 `quote_plus(...)` 编码，不需要手动转义
- lite 如果临时启用 scheduler 但不启用持久化 JobStore，调度器会退回内存模式
- lite 下明确不支持或默认跳过的能力，要按开关理解，不要按“和传统环境完全等价”理解
- 完整变量清单和默认值以 `apps/backend/web/settings.py` 为准

## 相关文档

- [Backend System Overview](system-overview.md)
- [Repo Baseline](../architecture/repo-baseline.md)
