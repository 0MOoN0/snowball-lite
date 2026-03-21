# xalpha 独立 SQLite cache 任务设计

## Checklist

- [x] 把 lite 默认 xalpha cache 切到独立 SQLite 文件
- [x] 保留显式切回 CSV cache 的能力
- [x] 阻断 SQL cache 回落到业务库 engine
- [x] 补默认 SQLite、CSV fallback、非法配置三类回归
- [x] 更新运行说明和环境变量文档

## 任务状态

- 状态：已完成
- 目标：让 lite 默认使用独立 SQLite cache
- 关键边界：cache 必须使用单独 SQLite 文件，不能落到业务库
- 决策补充：不迁移旧 CSV cache，历史 CSV 文件继续视为可丢弃缓存

## 1. 任务目标

这次任务要把 lite 的 xalpha cache 口径收成下面这套：

1. lite 默认切到独立 SQLite cache
2. 旧 CSV cache 不做迁移，不作为切换阻塞项
3. 仍然保留显式切回 CSV cache 的能力，方便排障和兼容
4. SQL cache 绝不能回落到业务库 engine

这里的重点已经不是“新增一个 opt-in SQLite 模式”，而是“把 lite 默认口径正式切到独立 SQLite”。

## 2. 选定方案

采用下面这套收口方案：

1. lite 默认使用独立 SQLite cache
2. 继续支持显式 `csv` backend
3. 默认切换后按新 cache 冷启动，不迁移旧 CSV cache
4. SQL cache 必须显式绑定独立 SQLite 文件，禁止回落到业务库 engine

## 3. 当前现状

当前仓库已经具备这些基础能力：

- `web/common/cons/webcons.py` 已支持 `csv` / `sql` / `memory` 三种 backend
- 已支持通过 `XALPHA_CACHE_SQLITE_PATH` 创建单独的 SQLite cache engine
- `xalpha` SQL backend 的最小读写兼容已经有单测覆盖

但现在离“默认切到独立 SQLite”还差几步：

- `LiteConfig` 仍是 `ENABLE_XALPHA_SQL_CACHE = False`
- lite 默认 `XALPHA_CACHE_BACKEND` 仍是 `csv`
- `apply_runtime_overrides()` 还没读取 `LITE_ENABLE_XALPHA_SQL_CACHE`
- SQL backend 在未提供独立 cache path 时，仍可能回落到业务库 engine
- lite 运行时路径、bootstrap、测试夹具现在还是按 CSV cache 目录做默认约定

所以当前代码还不能直接安全地把 lite 默认切到独立 SQLite。

## 4. 目标状态

改造完成后，lite 下的 xalpha cache 只有两种正式状态。

### 4.1 默认独立 SQLite 状态

- `LITE_ENABLE_XALPHA_SQL_CACHE=true`
- `LITE_XALPHA_CACHE_BACKEND=sql`
- `LITE_XALPHA_CACHE_SQLITE_PATH` 默认落到 lite runtime 目录下的独立 cache 文件
- cache 只写入该独立 SQLite 文件
- 旧 `lite_xalpha_cache/` 目录不做迁移，可继续留在本地但默认不再使用

### 4.2 显式 CSV fallback 状态

- `LITE_XALPHA_CACHE_BACKEND=csv`
- cache 写入 `LITE_XALPHA_CACHE_DIR`
- 主要用于兼容、排障或需要回退时的显式选择

## 5. 非法状态

下面这些配置必须直接失败，不能静默兜底：

- `backend=sql` 但最终没有可用的 `LITE_XALPHA_CACHE_SQLITE_PATH`
- `LITE_XALPHA_CACHE_SQLITE_PATH` 指向业务库文件
- lite 下关闭 SQL cache 却仍要求 `backend=sql`
- SQL backend 未拿到独立 SQLite engine，却继续回落到 `default_engine`

核心原则只有一条：

- 要么明确走独立 SQLite
- 要么明确走 CSV
- 不能模糊地回退到业务库

## 6. 配置设计

建议按下面口径收口配置。

- `LITE_XALPHA_CACHE_BACKEND`
  - 默认 `sql`
  - 可选 `sql` / `csv`

- `LITE_ENABLE_XALPHA_SQL_CACHE`
  - 默认 `true`
  - 只在 `backend=sql` 时参与校验

- `LITE_XALPHA_CACHE_SQLITE_PATH`
  - `backend=sql` 时使用
  - 默认指向 lite runtime 下的独立 cache SQLite 文件
  - 允许显式覆盖

- `LITE_XALPHA_CACHE_DIR`
  - 只在 `backend=csv` 时使用
  - 不再承担默认主路径语义

## 7. 代码改动点

### 7.1 `web/settings.py`

需要补这些收口动作：

1. 为 lite 增加 `LITE_ENABLE_XALPHA_SQL_CACHE` 的读取逻辑
2. 在 `apply_runtime_overrides()` 中写回 `app.config`
3. 把 lite 默认 backend 从 `csv` 调整为 `sql`
4. 给 lite 默认 SQLite cache path 一个稳定默认值
5. 保留 `LITE_XALPHA_CACHE_DIR`，但只给显式 CSV fallback 使用

### 7.2 `web/common/utils/backend_paths.py` 与 lite 运行时路径

需要补一层默认路径约定：

1. 增加 lite 默认 SQLite cache 文件路径 helper
2. 确保默认 cache 文件父目录存在
3. 不为这次切换新增旧 CSV cache 迁移逻辑
4. 旧 `lite_xalpha_cache/` 目录继续按“历史可丢弃缓存”处理

### 7.3 `web/common/cons/webcons.py`

需要补保护逻辑：

1. lite 下如果 `backend=sql` 且没有可用的 SQLite cache path，直接报错
2. lite 下如果 `XALPHA_CACHE_SQLITE_PATH` 与 `LITE_DB_PATH` 相同，直接报错
3. lite 下如果 `ENABLE_XALPHA_SQL_CACHE=false` 但仍要求 `backend=sql`，直接报错
4. SQL cache 创建时始终使用独立 SQLite engine，不允许回退到 `default_engine`
5. 显式 CSV backend 的现有逻辑保持不变

### 7.4 测试

至少补下面几类测试：

1. lite 默认启动后，backend 实际落到独立 SQLite 文件
2. 显式切回 CSV backend 后，仍然按目录 cache 工作
3. 缺少 SQLite cache path 时 fail fast
4. cache path 指向业务库时 fail fast
5. 旧 CSV cache 不迁移也不影响默认 SQLite 启动

## 8. 实施步骤

建议按下面顺序做：

1. 先补 lite 默认 SQLite path 和配置读取
2. 再补 `webcons.py` 的 fail-fast 保护，彻底去掉业务库回落
3. 再补默认 SQLite / CSV fallback / 非法配置测试
4. 最后补 README / 环境变量说明

## 9. 验收标准

完成后至少满足这些条件：

- lite 默认走独立 SQLite cache
- 显式切回 CSV 时，行为仍然可用
- SQL cache 不会和业务库共用同一个 SQLite 文件
- 非法配置会在初始化阶段直接失败
- 旧 CSV cache 不迁移，不影响默认 SQLite 启动
- 默认 SQLite 回归和 CSV fallback 回归都通过

## 10. 风险点

- 默认切换后，首次冷启动会失去旧 CSV cache 命中，首轮请求成本会上升
- 如果只改默认值，不去掉 SQL backend 对 `default_engine` 的回落，最容易污染业务库
- 现有 fixture、脚本和文档里有不少 CSV 默认假设，需要同步改
- `xa.set_backend()` 是全局状态，默认模式切换后仍要继续依赖现有锁保护

## 11. 推荐落地顺序

推荐先做三件事：

1. 禁止 SQL cache 回落到业务库
2. 再把 lite 默认 backend 切到独立 SQLite
3. 最后收口 CSV fallback、测试和文档

这样切默认值时，风险最小，也不会额外引入 CSV cache 迁移负担。
