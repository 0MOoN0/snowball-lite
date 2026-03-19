# 第二阶段 SQLite blocker 更新

## 结论

阶段二完成后，可以明确说：

- lite 的 SQLite 验证范围已经明显扩大
- 但“SQLite 迁移已经完成”这个结论仍然不能成立

## 已关闭项

### 1. 复杂模型只验证了建表，没做业务级 CRUD 验证

这一项可以关闭。

本轮已经验证：

- `IndexBase/StockIndex + IndexAlias + AssetFundETF + AssetAlias`
- `TradeAnalysisData + GridTradeAnalysisData`

对应测试：

- `tests/test_lite_sqlite_high_risk_models.py`

## 仍然保留的 blocker

### 1. Alembic 历史迁移未适配 SQLite

当前 lite 验证仍然主要依赖 `db.create_all()`。

影响：

- 不能说明历史 `migrations_snowball_*` 可以直接迁到 SQLite
- 如果后续要继续推进完整 SQLite 化，迁移目录仍需要单独梳理

### 2. 历史测试体系仍有 MySQL 默认路径

`web/webtest/conftest.py` 里仍然默认走 MySQL，并直接执行 `CREATE DATABASE IF NOT EXISTS ...`。

影响：

- lite 测试入口已经收敛
- 但整个历史测试体系并没有完成 SQLite 化

### 3. 非 lite 路径还有 MySQL 专有 SQL

例如：

- `web/scheduler/__init__.py` 里仍有 `SHOW TABLES LIKE 'apscheduler_jobs'`
- `web/models/__init__.py` 里仍保留 `pymysql` 异常分支和 `show variables like 'long_query_time'`

影响：

- lite 模式可以跑
- 但主仓库并没有完成数据库方言收口

### 4. SQLite 下 Decimal 仍有方言 warning

当前没有暴露功能性错误，但如果后续扩大金额精度场景，仍需要继续关注。

## 当前判断依据

这次之所以仍然不能说“SQLite 迁移已经完成”，关键不是 lite 能不能跑，而是仓库里还有一批明显只按 MySQL 思路写的路径。

### 1. 配置层还是双轨

- `web/settings.py` 里的 `LiteConfig` 确实已经默认走 SQLite
- 但 `DevConfig`、`StgConfig`、`TestingConfig` 等仍然默认走 `mysql+pymysql`

这说明现在完成的是 lite 路径切换，不是全仓库配置切换。

### 2. 迁移目录没有 SQLite 独立链路

- `web/models/__init__.py` 里的迁移目录映射仍然只指向 `migrations_snowball_dev`
- `migrations_snowball_stg`
- `migrations_snowball`
- `migrations_snowball_test`

仓库里现在也没有 `migrations_snowball_lite` 这一类独立目录。

这说明历史迁移链路还没有按 SQLite 重新梳理。

### 3. 测试体系没有整体迁过去

- `tests/conftest.py` 里的 lite 夹具是通过 `db.create_all()` 直接建表
- `web/webtest/conftest.py` 仍然直接执行 `CREATE DATABASE IF NOT EXISTS ...`

这说明 lite 测试入口已经能跑，但旧测试体系仍然默认站在 MySQL 上。

### 4. 运行时还有 MySQL 专有 SQL

- `web/scheduler/__init__.py` 仍然有 `SHOW TABLES LIKE 'apscheduler_jobs'`
- `web/models/__init__.py` 仍然有 `show variables like 'long_query_time'`

这些语句本身就说明，主路径还没有彻底收口到 SQLite 兼容写法。
