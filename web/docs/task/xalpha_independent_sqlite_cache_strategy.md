# xalpha 独立 SQLite cache 任务设计

## 任务状态

- 状态：待开始
- 目标：让 lite 支持 xalpha 独立 SQLite cache
- 关键边界：cache 必须使用单独 SQLite 文件，不能落到业务库

## 1. 任务目标

这次任务只解决一件事：在 lite 模式下，为 xalpha 增加“显式开启的独立 SQLite cache 模式”。

同时保留两个前提：

- lite 默认行为继续保持 CSV cache
- 未显式配置独立 SQLite cache 时，不改变现有 lite 默认口径

## 2. 选定方案

采用之前确认的推荐方案：

1. 默认继续使用 CSV cache
2. 增加可选的独立 SQLite cache 模式
3. 独立 SQLite cache 必须显式配置
4. SQL cache 禁止回落到业务库 engine

这不是“把默认值改成 sql”，而是“新增一种正式支持的 opt-in 模式”。

## 3. 当前现状

当前仓库已经具备两部分基础能力：

- `web/common/cons/webcons.py` 已支持 `csv` / `sql` / `memory` 三种 backend
- 已支持通过 `XALPHA_CACHE_SQLITE_PATH` 创建单独的 SQLite cache engine

但 lite 还缺两件事：

- `LiteConfig` 默认把 `ENABLE_XALPHA_SQL_CACHE` 关掉了
- SQL backend 在未提供独立 cache path 时，仍可能回落到业务库 engine

所以现在不能直接把 lite 安全地切到独立 SQLite cache。

## 4. 目标状态

改造完成后，lite 下的 xalpha cache 只有两种合法状态：

### 4.1 默认状态

- `XALPHA_CACHE_BACKEND=csv`
- cache 写入 `LITE_XALPHA_CACHE_DIR`
- 行为与当前一致

### 4.2 显式独立 SQLite 状态

- `LITE_ENABLE_XALPHA_SQL_CACHE=true`
- `LITE_XALPHA_CACHE_BACKEND=sql`
- `LITE_XALPHA_CACHE_SQLITE_PATH=/path/to/xalpha_cache.db`
- cache 只写入该独立 SQLite 文件

## 5. 非法状态

下面这些配置必须直接失败，不能静默兜底：

- `backend=sql` 但没有 `LITE_XALPHA_CACHE_SQLITE_PATH`
- `LITE_XALPHA_CACHE_SQLITE_PATH` 指向业务库文件
- lite 下关闭 SQL cache 却仍强行要求 SQL backend 生效

核心原则只有一条：

- 要么明确走 CSV
- 要么明确走独立 SQLite
- 不能模糊地回退到业务库

## 6. 配置设计

建议新增或正式收口这些配置：

- `LITE_XALPHA_CACHE_BACKEND`
  - 默认 `csv`
  - 可选 `sql`

- `LITE_ENABLE_XALPHA_SQL_CACHE`
  - 默认 `false`
  - 只有为 `true` 时，lite 才允许 SQL cache 生效

- `LITE_XALPHA_CACHE_SQLITE_PATH`
  - 仅在 `backend=sql` 时必填
  - 指向独立 cache SQLite 文件

## 7. 代码改动点

### 7.1 `web/settings.py`

需要补三件事：

1. 为 lite 增加 `LITE_ENABLE_XALPHA_SQL_CACHE` 的读取逻辑
2. 在 `apply_runtime_overrides()` 中写回 `app.config`
3. 保持默认值仍然是 CSV 模式

### 7.2 `web/common/cons/webcons.py`

需要补保护逻辑：

1. lite 下如果 `backend=sql` 且未提供 `XALPHA_CACHE_SQLITE_PATH`，直接报错
2. lite 下如果 `XALPHA_CACHE_SQLITE_PATH` 与 `LITE_DB_PATH` 相同，直接报错
3. SQL cache 创建时始终使用独立 SQLite engine，不允许回退到 `default_engine`

### 7.3 测试

至少补三类测试：

1. 显式开启独立 SQLite cache 后，backend 实际落到独立文件
2. 缺少 `LITE_XALPHA_CACHE_SQLITE_PATH` 时 fail fast
3. cache path 指向业务库时 fail fast

现有 CSV 默认行为测试要继续保留。

## 8. 实施步骤

建议按下面顺序做：

1. 先补配置读取和 app.config 收口
2. 再补 `webcons.py` 的 fail-fast 保护
3. 再补独立 SQLite cache 的专项测试
4. 最后补 README / 环境变量说明

## 9. 验收标准

完成后至少满足这些条件：

- lite 默认仍然走 CSV cache
- 显式开启后，xalpha cache 会写入独立 SQLite 文件
- SQL cache 不会和业务库共用同一个 SQLite 文件
- 非法配置会在初始化阶段直接失败
- 现有 CSV 回归和新增 SQLite cache 回归都通过

## 10. 风险点

- 如果只打开 SQL backend，不加 fail-fast，最容易误落到业务库
- 如果不保留 CSV 默认值，会扩大 lite 当前运行边界
- `xa.set_backend()` 是全局状态，新增模式后仍要继续依赖现有锁保护

## 11. 推荐落地顺序

推荐先做两件事：

1. 禁止 SQL cache 回落到业务库
2. 再开放独立 SQLite cache 的显式配置入口

这样即使实现还没完全铺开，也不会先把业务库污染掉。
