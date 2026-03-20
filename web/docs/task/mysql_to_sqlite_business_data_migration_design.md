# lite 业务数据 MySQL -> SQLite 迁移任务设计
## 任务状态

- 状态：待开始
- 优先级：中
- 目标阶段：lite 主线后续扩圈任务
- 当前产物：任务设计文档

## 1. 一句话结论

- 这不是把 `dev/stg/test` 三套环境一起迁到 SQLite。
- 这也不是把 `migrations_snowball_dev/`、`migrations_snowball_stg/`、`migrations_snowball_test/` 改造成 SQLite 可回放。
- 这次任务的真正目标是：从一套选定的 MySQL 业务库实例迁业务数据，到一个全新的 lite SQLite 文件。

## 2. 源库和目标库

### 2.1 源库

- 源库是 MySQL 的业务主库 `snowball` 这一层，不是缓存库，也不是 profiler 库。
- 具体迁哪一套实例，由脚本参数决定，不在文档里默认钉死。
- 实际运行时，源库通常是下面三选一：
  - `snowball_dev`
  - `snowball_stg`
  - `snowball_test`
- 脚本应通过 `--source-url` 明确指定源库 URL，而不是靠“当前环境”猜。

### 2.2 不作为第一阶段源库的数据

- `snowball_data*`：xalpha / DataBox SQL 缓存、数据落盘，默认不迁，按 lite 当前口径重建或继续用目录缓存。
- `snowball_profiler*`：性能分析库，默认不迁。

### 2.3 目标库

- 目标库是 lite 的单文件 SQLite。
- 路径由 `--target-sqlite` 或 `LITE_DB_PATH` 指定。
- 目标库 schema 不靠旧 MySQL 迁移历史回放生成，而是先用 lite baseline 建库：
  - `web/lite_bootstrap.py`
  - `migrations_snowball_lite/versions/lite_stage3_baseline.py`

## 3. 任务目标

- 定义一条可重复、可审计的 MySQL 业务数据 -> lite SQLite 迁移路径。
- 明确哪些表迁、哪些表重建、哪些表先不迁。
- 提供仓库内可维护的一次性 ETL 脚本方案。
- 给后续实现、验收、重跑提供统一口径。

## 4. 非目标

- 不把 `dev/stg/test/prod` 全部切换到 SQLite。
- 不重写 `migrations_snowball_dev/`、`migrations_snowball_stg/`、`migrations_snowball_test/` 的历史迁移。
- 不处理 Redis、scheduler、task queue、profiler 的迁移。
- 不做双写、增量同步、CDC。
- 不把缓存库强行当业务主数据全量搬迁。

## 5. 迁移范围

### 5.1 第一阶段建议迁移的业务表

- 资产主链：`tb_asset`、`tb_asset_exchange_fund`、`tb_asset_fund`、`tb_asset_fund_etf`、`tb_asset_fund_lof`
- 资产补充：`tb_asset_alias`、`tb_asset_code`、`tb_asset_fund_daily_data`、`tb_asset_fund_fee_rule`、`tb_asset_holding_data`
- 分类和指数：`tb_category`、`tb_asset_category`、`tb_index_base`、`tb_index_stock`、`tb_index_alias`
- 网格和记录：`tb_grid`、`tb_grid_type`、`tb_grid_type_detail`、`tb_record`、`tb_trade_reference`、`tb_grid_type_record`
- 分析数据：`tb_trade_analysis_data`、`tb_grid_trade_analysis_data`、`tb_amount_trade_analysis_data`
- 运行期业务数据：`tb_notification`、`system_settings`

### 5.2 第一阶段默认不迁

- `tb_apscheduler_log`
- `tb_notification_log`
- `tb_task`、`tb_task_asset`、`tb_task_log`
- `menu`、`irecord`
- `grid_detail`、`grid_record`、`stock_fund`
- `tb_grid_type_grid_analysis_data`
- `tb_grid_grid_analysis_data`
- profiler 相关库和表

### 5.3 特殊处理

- `system_settings` 正常业务配置项可以迁。
- `tb_amount_trade_analysis_data` 纳入第一阶段，但前提是先扩 lite baseline 支持该表，再按 `tb_trade_analysis_data -> tb_amount_trade_analysis_data` 顺序迁移。
- `system_settings` 里的 `version:enum` 和 lite runtime 自动生成键不覆盖。
- 迁移完成后，再跑一次 lite runtime version 写入。

## 6. 设计原则

- 目标 schema 以 lite baseline 为准，不以旧 MySQL 迁移历史为准。
- 保留原主键 ID，不重新编号，不做 ID 映射表。
- 以一次性 ETL 为主，不做实时同步。
- 优先用 SQLAlchemy Core 做表级迁移，不以 ORM 实例搬运为主。
- 默认 fail-fast：主键冲突、外键失败、关键列缺失时直接停。

## 7. 推荐流程

1. 用 `create_app("lite")` + `bootstrap_lite_database(...)` 创建全新目标 SQLite。
2. 连接一个 MySQL 源库和一个 SQLite 目标库。
3. 先做预检查：源表、目标表、列、行数、主键范围、孤儿引用。
4. 按依赖顺序迁移，分批写入，尽量使用 keyset pagination。
5. 每张表完成后做行数和关键字段校验。
6. 全量完成后跑 lite 回归和抽样业务验收。
7. 生成迁移报告，决定该 SQLite 文件是否可作为正式 lite 数据库。

## 8. 建议脚本

- 落点：`py_script/mysql_to_sqlite_lite_migration.py`
- 必要参数：
  - `--source-url`：MySQL 源库 URL
  - `--target-sqlite`：目标 SQLite 文件路径
  - `--tables`：只迁指定表
  - `--batch-size`：批量大小
  - `--dry-run`：只做预检查
  - `--resume-from-table`：从指定表继续
  - `--truncate-target`：迁当前表前先清空目标表
  - `--report-path`：输出迁移报告

## 9. 推荐迁移顺序

1. `tb_category`
2. `tb_index_base`
3. `tb_asset`
4. 资产子表和资产补充表
5. 分类关联和指数关联表
6. `tb_grid`、`tb_grid_type`、`tb_grid_type_detail`
7. `tb_record`、`tb_trade_reference`、`tb_grid_type_record`
8. `tb_trade_analysis_data`
9. `tb_grid_trade_analysis_data`、`tb_amount_trade_analysis_data`
10. `tb_notification`
11. `system_settings`

## 10. 验收标准

- 已纳入范围的表，源库和目标库行数一致。
- 主键最小值 / 最大值与源库一致。
- 关键唯一键无重复。
- 外键关系无孤儿记录。
- 资产、记录、grid/grid-type/amount 分析、通知、系统设置至少完成一轮抽样读取验证。
- 迁移完成后，至少补跑一组 lite 启动、bootstrap、资产、记录、分析、查询 smoke 回归。

## 11. 回滚和重跑

- 默认总是迁到一个全新的 SQLite 文件，不在已有目标库上覆盖。
- 失败后直接废弃本次目标库，重新 bootstrap 再跑。
- 断点续跑优先支持“从某张表开始重跑”，不做复杂的跨表细粒度恢复。

## 12. 本任务完成标准

- 迁移脚本已实现。
- 预检查结果可输出。
- 第一阶段业务表可以从一套 MySQL `snowball_*` 业务库成功迁到 lite SQLite。
- 有迁移报告。
- 有一组迁后验证命令或自动化测试。
