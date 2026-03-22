# 任务 2：SQLite 最小可用链路

## 目标

验证项目是否能在 SQLite 下完成最小数据库能力，包括建表、写入、查询和基础更新时间字段处理。

本任务只做最小闭环，不做全量 SQLite 迁移。

## 任务范围

- 建立 SQLite engine 初始化方式
- 选最小一组核心模型验证 SQLite
- 修复最容易阻塞建表和写入的兼容问题
- 使用 `db.create_all()` 完成本轮验证

## 关键文件

- `web/models/__init__.py`
- `web/models/base.py`
- `web/models/setting/system_settings.py`
- `web/models/asset/asset.py`
- `web/models/notice/Notification.py`

## 推荐验证模型

建议优先选这 3 个模型：

- `Setting`：简单、主键是 `Integer`
- `Asset`：覆盖 `BigInteger` 自增主键和时间字段
- `Notification`：覆盖 `TINYINT` 和时间字段

## 必须处理的兼容点

- `BigInteger` 自增主键
- `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`
- `TINYINT`
- SQLite 的 `PRAGMA foreign_keys=ON`
- SQLite 的 `PRAGMA journal_mode=WAL`
- SQLite 的 `PRAGMA busy_timeout`

## 设计选择

- 本轮不迁移旧 MySQL 数据
- 本轮不接入完整 Alembic 历史
- 优先保证“能用”，不是“全量兼容”
- 如模型兼容范围扩大过快，应立即止损并记录 blocker

## 执行步骤

1. 配置 SQLite 数据库文件
2. 在 engine 初始化时补齐 SQLite PRAGMA
3. 修复所选模型的关键方言问题
4. 使用 `db.create_all()` 建表
5. 对所选模型执行插入、更新、查询验证

## 验收标准

- 应用能连接 SQLite
- 至少 2 个核心模型可以建表成功
- 至少 2 个核心模型可以完成插入和查询
- 更新时间字段不会因 MySQL 专有语法阻塞
- 文档中能明确记录仍未解决的模型兼容点

## 非目标

- 不要求全部模型兼容 SQLite
- 不要求所有迁移脚本可直接复用
- 不要求完整测试通过

## 风险提示

- `BigInteger` 自增主键可能带出一串父子表/外键链路问题
- 如果直接扩展到太多模型，本任务会迅速失控

## 任务完成产物

- 一套可运行的最小 SQLite 配置
- 一组通过验证的核心模型
- 一份 SQLite blocker 清单

## 当前状态

- 已完成（阶段一）

## 本轮结果

- 已补齐 SQLite engine 的最小运行参数：
  - `PRAGMA foreign_keys=ON`
  - `PRAGMA journal_mode=WAL`
  - `PRAGMA busy_timeout=30000`
- 已补齐 `BigInteger` 自增主键在 SQLite 下的兼容处理。
- 已将 `Asset`、`Notification` 等模型中的更新时间语义改成兼容 SQLite 的写法。
- 已验证 `Setting`、`Asset`、`Notification` 这 3 个模型的最小建表、插入、更新、查询闭环。
- 本任务的未解决项已经单独整理到 `02_sqlite_blockers.md`。

## 对应验证

- `tests/test_lite_sqlite_minimal_path.py`
- 验证重点：
  - `db.create_all()` 可执行
  - 3 个核心模型可完成最小 CRUD
  - SQLite PRAGMA 配置已实际生效
