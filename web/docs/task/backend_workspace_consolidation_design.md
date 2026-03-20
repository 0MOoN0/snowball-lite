# 后端目录收口与 monorepo 预留任务设计

## 任务状态

- 状态：待开始
- 优先级：中
- 目标阶段：lite 主线后续收敛任务
- 当前产物：任务设计文档

## 1. 一句话结论

- 可以把后端相关资产继续收紧，但不应该把所有 Python 内容一股脑塞进 `web/`。
- `web` 是后端应用包，`xalpha` 是下层能力库，这两个边界要保留。
- 这次任务的真正目标是：把“属于后端工作区但散落在仓库根目录的内容”逐步收口，为未来前后端 monorepo 预留一个清晰的 backend workspace。

## 2. 当前现状

### 2.1 目前仓库里混着三类内容

1. 后端应用代码
   - `web/`

2. 下层能力库
   - `xalpha/`
   - `extends/`

3. 散落在仓库根目录的后端附属物
   - `migrations_snowball_dev/`
   - `migrations_snowball_stg/`
   - `migrations_snowball_test/`
   - `migrations_snowball_lite/`
   - `py_script/`
   - `db/`
   - 根目录 `tests/` 中的一部分 lite / backend 测试

### 2.2 当前依赖方向

- `web` 依赖 `xalpha`
  - 例如 `web/databox/adapter/data/xa_data_adapter.py`
  - 例如 `web/databox/adapter/data/xa_service.py`
  - 例如 `web/common/utils/WebUtils.py`
- `xalpha` 当前没有反向依赖 `web`
- `extends` 主要依赖 `xalpha`，还依赖少量 `py_script`
- 根目录 `tests/` 里既有 `xalpha` 测试，也有 lite/backend 测试

### 2.3 当前已经暴露出来的问题

- 后端相关目录不集中，长期维护成本会上升。
- `LiteConfig` 默认用 `os.getcwd()` 推导 `snowball_lite.db`，容易在仓库根目录生成运行文件。
- 迁移目录目前按仓库根目录命名和定位，不利于后续目录重排。
- 根目录 `tests/` 的职责不够清晰，后端和 `xalpha` 测试混放。
- 如果未来把前端迁进来，根目录会继续变重，backend / frontend / library 的边界会更难收。

## 3. 任务目标

- 明确后端工作区的边界，收口散落在仓库根目录的后端资产。
- 为未来 `frontend + backend + shared packages` 的 monorepo 结构预留空间。
- 保持 `xalpha` 作为独立下层能力库，不把它直接并进 `web`。
- 降低“当前工作目录决定运行路径”的隐式行为。
- 给后续目录迁移和配置调整提供统一口径。

## 4. 非目标

- 不把 `xalpha/` 移进 `web/`。
- 不把 `extends/` 直接改造成 `web` 子目录。
- 不在这次任务里引入前端工程。
- 不一次性重写整个打包体系。
- 不把所有测试在一轮里全部重排。
- 不改变 lite 主线“默认 SQLite、最小依赖”的基本方向。

## 5. 设计原则

### 5.1 保留边界

- `web` 继续代表后端应用包。
- `xalpha` 继续代表下层能力库。
- `extends` 优先视为 `xalpha` 生态扩展，不默认收进 `web`。

### 5.2 收口的是“后端工作区”，不是“所有 Python 代码”

- 可以收进 backend workspace 的内容：
  - 迁移目录
  - 后端脚本
  - 后端初始化 SQL
  - 后端专属测试
  - 后端运维辅助文件
- 不应该顺手收进去的内容：
  - `xalpha`
  - `extends`
  - 仓库级打包、CI、发布配置

### 5.3 运行路径不能继续依赖 `cwd`

- lite 默认 SQLite 路径不应再隐式落在仓库根目录。
- 迁移目录和 bootstrap 路径不应依赖“仓库根目录里刚好有某个目录名”。
- 所有 backend 路径都应该从明确的 backend 根路径推导。

### 5.4 先做可控收口，再做 monorepo 物理重排

- 先把边界和路径收稳。
- 再做目录迁移。
- 最后再引入真正的 `apps/backend`、`apps/frontend` 结构。

## 6. 选定方案

采用“两阶段收口”方案。

### 6.1 第一阶段：当前仓库内收口

不立即引入 `apps/`，先在现有仓库里把后端附属物往 `web` 周边收。

建议目标结构：

- `web/`
  - `application.py`
  - `lite_application.py`
  - `models/`
  - `routers/`
  - `services/`
  - `scheduler/`
  - `task/`
  - `common/`
  - `docs/`
  - `webtest/`
  - `migrations/`
    - `lite/`
    - `dev/`
    - `stg/`
    - `test/`
  - `scripts/`
  - `dev_support/`

第一阶段收口目标：

- `migrations_snowball_lite/` -> `web/migrations/lite/`
- `migrations_snowball_dev/` -> `web/migrations/dev/`
- `migrations_snowball_stg/` -> `web/migrations/stg/`
- `migrations_snowball_test/` -> `web/migrations/test/`
- `py_script/` 中明确属于后端运行的脚本 -> `web/scripts/`
- `db/dev/init.sql` -> `web/dev_support/db/dev/init.sql`
- 根目录 `tests/` 中明确属于后端的 lite 测试 -> `web/webtest/` 下新的 lite 分组目录

### 6.2 第二阶段：演进到 monorepo

在第一阶段已经把边界收清楚的前提下，再升级成真正的 monorepo 目录。

建议目标结构：

```text
/apps
  /backend
    /web
    /migrations
    /scripts
    /tests
  /frontend
/packages
  /xalpha
  /xalpha_ext
/docs
/ops
```

第二阶段不要求现在立刻开工，但第一阶段所有路径调整都应避免堵死这条路。

## 7. 第一阶段建议迁移范围

### 7.1 建议纳入收口的内容

- 所有 Alembic 迁移目录
- lite bootstrap 依赖的迁移配置
- 明确服务于后端运行或迁移的脚本
  - 例如 `py_script/mysql_to_sqlite_lite_migration.py`
- 后端初始化或本地开发辅助 SQL
- 根目录 `tests/` 中的 backend / lite 测试

### 7.2 暂不纳入本任务

- `xalpha/`
- `extends/`
- `jupyter_notebook/`
- `doc/`
- 根目录与包发布直接相关的元数据
  - `pyproject.toml`
  - `setup.py`
  - `Dockerfile`
  - `.github/`

### 7.3 需要先拆分判断的内容

- `py_script/` 不是所有脚本都属于后端
- 根目录 `tests/` 不是所有测试都属于后端

当前可以先按下面口径判断：

- `web` only 测试：迁到 `web/webtest/` 体系
- `xalpha` only 测试：继续留在根目录 `tests/`
- `web + xalpha` 混合测试：先保留原位，后续单独再拆

## 8. 关键实现点

### 8.1 路径解析层收口

要先补一个统一的 backend 路径解析层，集中解决这些路径：

- backend 根路径
- migration 根路径
- lite runtime 数据目录
- 默认 SQLite 路径
- 默认 xalpha cache 路径
- 脚本和 dev_support 路径

第一阶段里，不建议继续在业务代码里直接写：

- `os.getcwd()`
- `Path(__file__).resolve().parents[n]` 到处散落
- 根目录硬编码字符串如 `migrations_snowball_lite`

### 8.2 Lite 默认运行文件路径调整

当前 `web/settings.py` 里 lite 默认 SQLite 路径是：

- `os.path.join(os.getcwd(), "snowball_lite.db")`

这会让根目录不停冒出运行文件。

第一阶段建议改成：

- 显式要求 `LITE_DB_PATH`，或者
- 回退到 backend 约定 runtime 目录，例如 `data/` 下固定位置

同时保持：

- 文档口径一致
- 测试 fixture 可覆盖
- 不影响现有 `LITE_DB_PATH` 显式传参

### 8.3 迁移目录解析改造

当前需要改造的核心点：

- `web/models/__init__.py`
- `web/lite_bootstrap.py`

目标不是只改目录名，而是让这两处都通过统一路径工具获取 migration 目录。

### 8.4 测试目录收口

根目录 `tests/` 目前至少分成三类：

1. 后端 lite / bootstrap / runtime 测试
2. `xalpha` 独立测试
3. `web` 与 `xalpha` 的桥接测试

第一阶段建议只迁第 1 类：

- `test_lite_bootstrap_fixture_path.py`
- `test_lite_bootstrap_review.py`
- `test_lite_real_databox_validation.py`
- `test_lite_runtime_dependency_boundary.py`
- `test_lite_smoke_validation_and_decision.py`
- `test_lite_sqlite_high_risk_models.py`
- `test_lite_sqlite_minimal_path.py`
- `test_lite_stage4_query_api_matrix.py`
- `test_lite_stage5_schema_expansion.py`
- `test_mysql_to_sqlite_business_migration.py`

第 2 类继续留根目录 `tests/`。

第 3 类先不动，等边界再清一轮。

## 9. 推荐实施顺序

1. 先新增统一 backend 路径工具
2. 改 lite 默认 SQLite / cache 路径，去掉 `cwd` 依赖
3. 改造 migration 目录解析
4. 迁 `migrations_snowball_*`
5. 迁后端脚本到 `web/scripts/`
6. 迁 backend 专属测试到 `web/webtest/`
7. 更新 README、任务文档和相关运行说明
8. 最后做一轮 lite 启动、迁移、测试回归

## 10. 风险点

### 10.1 最大风险不是目录移动本身，而是路径硬编码

- 迁移目录一动，Alembic 和 bootstrap 很容易断。
- 默认 SQLite 路径一动，启动脚本和测试 fixture 很容易受影响。

### 10.2 `xalpha` 边界被打穿

如果为了“看起来都在一起”，把 `xalpha` 直接并进 `web`：

- 后端和底层能力库会耦合得更紧
- 后续 monorepo 反而更难拆
- 当前 `web -> xalpha` 的单向依赖关系会被破坏

### 10.3 `py_script/` 和 `tests/` 不能整包平移

- 两者都不是纯后端目录
- 必须先按职责拆分，再迁移

### 10.4 文档与运行命令会一起受影响

- README
- `web/docs/环境变量配置指南.md`
- `web/docs/系统说明.md`
- lite bootstrap 相关任务文档

这些都要同步，否则后续维护者会继续按旧路径操作。

## 11. 验收标准

完成后至少满足这些条件：

- 后端运行和迁移所需的核心附属物已不再散落在仓库根目录
- lite 默认启动不再因为 `cwd` 在根目录生成 `snowball_lite.db`
- `web/models/__init__.py` 和 `web/lite_bootstrap.py` 不再直接依赖旧的根目录迁移路径
- 明确属于后端的脚本已经收进 `web` 周边
- 明确属于后端的 lite 测试已经从根目录 `tests/` 收口
- `xalpha` 仍保持独立目录和独立边界
- README 和相关文档已更新到新路径
- lite 启动、bootstrap、迁移脚本、关键测试都能通过

## 12. 本任务完成标准

- 有统一的 backend 路径解析口径
- 完成第一阶段目录收口
- 文档和命令已同步
- 不引入 `xalpha -> web` 反向依赖
- 为未来 `apps/backend + apps/frontend + packages/xalpha` 的 monorepo 结构留出明确演进路径
