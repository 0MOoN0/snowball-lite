# SQLite 最小链路 blocker 清单

## 当前状态

- 已作为任务 2 的产物保留
- 本文档记录的是“SQLite 最小链路已经跑通后，仍然没解决的问题”

## 本轮已验证

- `lite` 模式可以连接 SQLite 文件库
- engine 初始化已补齐：
  - `PRAGMA foreign_keys=ON`
  - `PRAGMA journal_mode=WAL`
  - `PRAGMA busy_timeout=30000`
- `db.create_all()` 已能在当前模型集上完成建表
- 已完成最小增改查验证的模型：
  - `Setting`
  - `Asset`
  - `Notification`

## 当前仍未解决

### 1. Alembic 历史迁移未适配 SQLite

本轮仍然依赖 `db.create_all()` 验证最小闭环，没有接入完整迁移历史。

影响：

- 不能说明现有 `migrations_snowball_*` 可以直接迁到 SQLite
- 后续若要支持真实迁移，还需要单独梳理方言差异

### 2. 测试基建仍然默认走 MySQL

`web/webtest/conftest.py` 里仍然有 `CREATE DATABASE IF NOT EXISTS ...` 这一类 MySQL 初始化路径。

影响：

- 当前 SQLite 验证是新增的最小专项测试
- 现有大部分数据库测试夹具还不能直接复用到 SQLite

### 3. 非 lite 路径里还有 MySQL 专有 SQL

例如：

- `web/scheduler/__init__.py` 中的 `SHOW TABLES LIKE ...`
- `web/models/__init__.py` 里仍保留了 `pymysql` 异常分支

影响：

- lite 最小链路已经能跑
- 但如果继续推进“全面 SQLite 化”，这些路径还要继续清理

### 4. 复杂模型只验证了建表，没做业务级 CRUD 验证

本轮重点只放在最小闭环，没有继续扩到所有模型，尤其是这些高风险链路：

- 联合表继承相关模型
- 多外键关联模型
- 分析类数据模型

影响：

- 现在能说明“最小链路可用”
- 还不能说明“全部业务模型已兼容 SQLite”

### 5. xalpha / databox 的 SQLite 兼容已单独在任务 3 验证

影响：

- `xalpha` 的 SQLite 兼容补丁已经补上
- 但轻量模式默认仍然选择 CSV 缓存，不把 SQLite 当默认缓存后端
- 因此这部分不再是阶段一 blocker，但仍然是后续“全面 SQLite 化”时需要重新评估的点

## 建议下一步

1. 如果要扩大 SQLite 覆盖范围，优先挑联合表继承模型做第二批验证
2. 在决定全面切 SQLite 前，再统一处理测试夹具和迁移脚本
3. 如果后续想让 lite 默认走 SQLite 缓存，再单独评估 `xalpha` / DataBox 的维护成本
