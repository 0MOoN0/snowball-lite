# lite 业务数据 MySQL -> SQLite 迁移（归档）

## 归档状态

- 状态：已完成
- 原任务文档：`/Users/leon/projects/snowball-lite/web/docs/task/mysql_to_sqlite_business_data_migration_design.md`
- 对应状态：`/Users/leon/projects/snowball-lite/web/docs/review/mysql_to_sqlite_business_data_migration_design/task-status.md`
- 对应评审：`/Users/leon/projects/snowball-lite/web/docs/review/mysql_to_sqlite_business_data_migration_design/round-01-review.md`
- 稳定交付物：`/Users/leon/projects/snowball-lite/data/stg_lite.db`
- 对应提交：`d78fbd1`

## 结论

- 这次完成的不是“把整个仓库切到 SQLite”。
- 完成的是一条可重复、可审计的业务库 MySQL -> lite SQLite 迁移链路。
- 已经用真实 `stg` 业务库跑通，并沉淀出可直接给 lite 使用的 SQLite 文件。

## 实际落地范围

本次按任务设计完成的是第一阶段业务表迁移：

- 资产主链和资产补充表
- 分类和指数表
- 网格、记录和交易引用表
- 分析数据表
- `tb_notification`
- `system_settings`

明确不在这次归档范围里的内容：

- `snowball_data*` 这类 xalpha / DataBox SQL 缓存库
- `snowball_profiler*`
- Redis、scheduler、task queue、profiler 迁移
- `dev/stg/test` 历史 MySQL 迁移目录重写

## 已落地实现

- 补齐了 lite baseline 对 `tb_amount_trade_analysis_data` 的支持
- 实现了业务数据迁移 service 和 CLI
- 支持预检查、分表顺序迁移、重试、断点续跑和 JSON 报告
- 对远程 MySQL 不稳定链路做了短超时 + 源操作重试处理
- 对 `system_settings` 的 runtime key 冲突做了专门修复

## 真实 stg 迁移结果

- 已完成真实 `stg` 源库的分段 `dry-run`
- 已完成真实 `stg` -> SQLite 正式迁移
- 迁移后的稳定库保留为 `data/stg_lite.db`

关键核对结果：

- `tb_asset = 5460`
- `tb_trade_analysis_data = 7484`
- `tb_amount_trade_analysis_data = 736`
- `system_settings = 9`

这里的 `system_settings = 9` 含义是：

- 业务配置 8 条
- lite runtime 自动写入的 `version:enum` 1 条

## 验收结果

已经完成的验收包括：

- 迁移链路自动化测试
- lite baseline / bootstrap 回归
- 真实迁移后的后端接口验收

后端接口验收已覆盖：

- 资产列表和资产详情
- 记录详情和记录列表
- grid / grid-type 分析结果
- 系统设置列表
- 通知列表和通知详情

这些接口都已经在真实迁移产物上返回 `200`。

## 边界说明

- 这份归档只说明“第一阶段业务数据迁移链路已经完成”
- 不等于整个 lite 项目已经完成全量历史数据迁移
- 也不等于整个仓库已经完成 SQLite 化

## 后续如果继续推进

后续更适合接着做的是：

1. 前端页面抽样验收
2. 后端目录收口和 monorepo 预留整理
3. 文档根目录统一收口
