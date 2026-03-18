# Snowball 应用 MySQL → SQLite 迁移可行性分析

## 一、当前数据库架构概览

| 维度 | 详情 |
|------|------|
| **数据库数量** | 3 个 MySQL 数据库（`snowball` 业务库、`snowball_data` 数据存放库、`snowball_profiler` 性能分析库） |
| **模型数量** | 30+ 个 SQLAlchemy 模型，业务模型基本都绑定到 `snowball` |
| **默认库职责** | 默认库 `snowball_data` 主要用于 xalpha / DataBox 的 SQL 缓存与数据落盘，不是当前业务 ORM 主表的主要承载库 |
| **驱动** | `pymysql`，不仅在代码里引用，也在多环境配置中硬编码了 `mysql+pymysql://` |
| **连接池** | `pool_size=5`, `max_overflow=15`, `pool_recycle=1200`, `pool_pre_ping=True` |
| **其他中间件** | Redis（缓存 + Dramatiq 消息队列）、APScheduler（定时任务，使用 SQLAlchemy JobStore） |

---

## 二、不兼容项清单

### 🔴 高影响 — 必须修改

#### 1. `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`（模型定义约 14 处，迁移脚本更多）

MySQL 独有语法，SQLite 不支持。

```python
# 当前写法（MySQL专用）
update_time = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

# SQLite兼容写法
update_time = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
```

涉及文件包括：`asset.py`, `asset_alias.py`, `asset_code.py`, `AssetFundDailyData.py`, `AssetFundFeeRule.py`, `stock_fund.py`, `index_base.py`, `index_alias.py`, `Notification.py`, `notification_log.py`, `scheduler_log.py`, `system_settings.py`, `Task.py`, `trade_analysis_data.py`

#### 2. `BigInteger` 自增主键在 SQLite 下会出实质性故障（高风险）

项目大量主键使用 `db.BigInteger(primary_key=True, autoincrement=True)`。

在当前 `SQLAlchemy 1.4.x + SQLite` 组合下，只有 `INTEGER PRIMARY KEY` 才能稳定获得 SQLite 的 rowid 自增语义；直接使用 `BigInteger` 可能在插入时触发 `NOT NULL constraint failed: <table>.id`。

这不是性能问题，而是建表后插入数据就可能失败的结构性问题。

建议处理方式：

- 统一将 SQLite 下的自增主键映射为 `Integer`
- 或为主键封装自定义跨方言类型，在 MySQL 使用 `BigInteger`，在 SQLite 编译为 `Integer`
- 所有联合表继承链上的外键/主键类型要一起校正，避免父子表类型不一致

#### 3. `TINYINT` 方言类型（1 文件，4 处）

```python
# 当前（错误引用了 mssql 方言）
from sqlalchemy.dialects.mssql import TINYINT

# 应改为
db.SmallInteger
```

文件：`web/models/notice/Notification.py`

#### 4. `pymysql` 不是只有 import 依赖，配置层也深度绑定 MySQL

- `web/models/__init__.py` — `import pymysql` + 异常捕获
- `web/scheduler/__init__.py` — `import pymysql`
- `web/settings.py` — `dev/stg/prod/test/local_dev_test` 多套配置直接拼接 `mysql+pymysql://...`
- `web/webtest/conftest.py` — 测试库初始化默认驱动仍为 `pymysql`

#### 5. MySQL 特有 SQL 查询不止 1 处

```python
# web/models/__init__.py:191
conn.execute(sqlalchemy.text("show variables like 'long_query_time'"))
```

还包括：

```python
# web/scheduler/__init__.py:379
conn.execute(text("SHOW TABLES LIKE 'apscheduler_jobs'"))
```

#### 6. 连接池配置不兼容

`SQLALCHEMY_ENGINE_OPTIONS` 中的 `pool_size`, `max_overflow`, `pool_recycle`, `connect_args` 等对 SQLite 无意义或报错。

#### 7. SQLite 运行时参数需要补齐

当前代码中没有看到面向 SQLite 的运行时初始化，例如：

- `PRAGMA foreign_keys=ON`
- `PRAGMA journal_mode=WAL`
- `PRAGMA busy_timeout`
- 视线程/协程模型调整 `check_same_thread`

不补这层，即使模型能建表，也可能出现：

- 外键不生效
- 并发写入更容易锁库
- 运行行为与 MySQL 明显漂移

#### 8. 多数据库绑定架构需要重新设计，但不一定必须合并为 1 个文件

现有方案中：

- `snowball`：业务实体主库
- `snowball_data`：xalpha / DataBox 数据缓存与数据落盘
- `snowball_profiler`：性能分析数据

SQLite 迁移时有两种可行路线：

- 保留多文件：`snowball.db` + `snowball_data.db` + `snowball_profiler.db`
- 统一单文件：减少配置复杂度，但会增加表混杂度与锁竞争面

因此，“必须合并为 1 个 SQLite 文件”并不是唯一选项。

---

### 🟡 中影响

| 项目 | 说明 |
|------|------|
| APScheduler JobStore | MySQL URL 需改为 SQLite URL |
| Flask-Migrate 迁移脚本 | 现有迁移目录中大量脚本包含 MySQL 方言、`mysql.TINYINT`、`CURRENT_TIMESTAMP ON UPDATE ...`，基本需要重新梳理或重建 |
| 测试初始化方式 | `web/webtest/conftest.py` 直接连接 MySQL root engine 并执行 `CREATE DATABASE`，SQLite 需完全改写 |
| 并发写入 | SQLite 文件锁，APScheduler + Dramatiq + Web 同时写入可能 `database is locked` |
| xalpha / DataBox 默认库 | 目前默认库 `snowball_data` 主要承载第三方库的 SQL 缓存表，迁移时需明确是迁移历史缓存还是允许重建 |
| 数值语义 | 金融类数据里存在 `DECIMAL`、`Float` 字段；SQLite 类型亲和性更弱，需验证精度与序列化行为 |

### 🟢 低影响 — 无需修改

ORM 查询全部使用 SQLAlchemy ORM ✅ | 无 `ON DUPLICATE KEY` ✅ | 无 MySQL 专有函数 ✅ | UniqueConstraint/Index 标准兼容 ✅

---

## 三、迁移成本评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 代码修改量 | 高 | 不仅是模型字段，`settings`、初始化逻辑、APScheduler 校验逻辑、测试夹具都需要修改 |
| 技术风险 | 高 | SQLite 并发写入 + `BigInteger` 主键语义 + 外键/锁行为是核心风险 |
| 数据迁移 | 中 | 如果 `snowball_data` 视为缓存可降低；业务库仍需认真迁移 |
| 迁移脚本 | 高 | 现有迁移文件带有明显 MySQL 方言，不能直接复用 |
| 测试回归 | 高 | 当前测试体系对 MySQL 建库方式和多库连接有显式依赖 |

**更新后的预估工作量：**

- **POC / 本地单机可用版**：中，约 3～5 天
- **完整替换现有 MySQL、保持现有调度/异步/测试能力**：高，约 1～2 周

### 难度与工作量（按高中低）

| 项目 | 难度 | 工作量 | 说明 |
|------|------|--------|------|
| 模型与表结构兼容 | 高 | 高 | 时间字段、`TINYINT`、`BigInteger` 自增主键、联合表继承都要处理 |
| 配置与启动链路 | 中 | 中 | 多环境配置、engine options、异常处理、默认库初始化要调整 |
| APScheduler 与并发稳定性 | 高 | 高 | Web + Scheduler + Dramatiq 共享 SQLite 写路径风险较高 |
| 数据迁移 | 中 | 中 | 业务库为主，缓存库可按需决定是否重建 |
| 测试体系改造 | 高 | 高 | 现有测试中有显式 `CREATE DATABASE` 和 MySQL 连接假设 |
| 整体评估 | 高 | 高 | 若目标是完整替代 MySQL，不建议低估工作量 |

---

## 四、推荐方案对比

| 方案 | 难度 | 资源节省 | 推荐度 |
|------|------|----------|--------|
| **A. 全量迁移 SQLite** | 高 | 最大（去掉 MySQL） | 中 |
| **B. 优化 MySQL 配置** | 低 | 中等（降至~100MB） | 高 |
| **C. 保持 MySQL 业务库，仅压缩数据/缓存库** | 中 | 中等 | 中高 |
| **D. 迁移 PostgreSQL** | 高 | 无 | 低 |

### 方案 B（推荐先尝试）

零代码修改，调低 MySQL 内存参数即可：

```ini
# my.cnf
innodb_buffer_pool_size = 64M
key_buffer_size = 8M
max_connections = 10
table_open_cache = 64
```

MySQL 8.0 默认 ~400MB，优化后可降至 ~100MB。

### 方案 A（如果仍需迁移）

建议分阶段执行，而不是一次性切换：

1. 先抽象数据库 URL / driver / engine options，去掉对 `mysql+pymysql` 的硬编码
2. 修复模型层兼容项，尤其是 `BigInteger` 自增主键与时间字段默认值
3. 为 SQLite 增加专用 engine 初始化：WAL、foreign_keys、busy_timeout
4. 改造 APScheduler 校验逻辑，去掉 `SHOW TABLES`
5. 改写测试夹具，移除 `CREATE DATABASE`
6. 决定 `snowball_data` 是否作为缓存库重建，而不是做全量数据迁移
7. 最后再处理迁移历史与数据导入

---

## 五、最终判断

### 1. 如果目标是“本地单机开发版，减少资源占用”

- **可行性**：高
- **难度**：中
- **工作量**：中

适合接受以下前提：

- 单 worker
- 低并发
- 测试先做最小改造
- `snowball_data` 允许作为缓存重建

### 2. 如果目标是“完整替换现有 MySQL，保持现有能力不降级”

- **可行性**：中
- **难度**：高
- **工作量**：高

主要原因：

- 当前项目并非只有 ORM 层依赖 MySQL
- 配置、测试、调度器、迁移脚本都带有 MySQL 假设
- `BigInteger` 自增主键在 SQLite 下会直接触发插入失败
- APScheduler + Dramatiq + Web 共用 SQLite 写路径存在天然锁竞争

**核心风险提示**：SQLite 并发写入限制仍是最大隐患，但真正会首先阻塞迁移落地的，往往是 `BigInteger` 主键语义、测试夹具、配置硬编码和迁移脚本兼容性。

**建议**：先尝试方案 B（优化 MySQL）。如果仍需迁移 SQLite，建议以“本地单机版/开发版”为第一阶段目标，不建议直接把生产形态一步切过去。
