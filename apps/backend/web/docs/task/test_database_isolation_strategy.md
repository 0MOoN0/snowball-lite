# 测试库隔离方案任务设计

- [x] `tests/` 已统一走 lite 临时 SQLite 测试库
- [x] `web/webtest` 的 lite fixtures 已统一走临时 SQLite，并接入路径保护
- [x] 历史 MySQL fixtures 增加“禁止连接业务库”的硬保护
- [x] 历史 MySQL 测试加 `mysql_integration` 标记并从默认 pytest 中排除
- [x] README 默认测试命令改成 SQLite 默认层优先
- [ ] CI 测试 job 按 SQLite 默认层 / MySQL 兼容层拆分

## 任务状态

- 状态：核心规则已完成
- 选定方案：方案 4，分层策略
- 目标：业务库和测试库彻底分开，默认跑测试不触碰业务库
- 已完成范围：lite / SQLite 测试隔离、历史 MySQL 测试收口、README 默认执行口径收口
- 剩余范围：CI job 拆分、按价值继续把老 MySQL `webtest` 迁到 SQLite

## 0. 先说当前结论

这份任务现在已经不是“SQLite 完成、MySQL 未完成”，而是“核心隔离规则已落地，剩下的是 CI 和逐步迁移”。

当前可以明确分成两部分：

1. 已完成
   - `tests/` 已复用 lite runtime fixtures，使用 pytest 临时目录下的 SQLite 文件
   - `web/webtest` 的 lite fixtures 已改成临时 SQLite
   - pytest 下的 lite 启动入口已接入 `LITE_DB_PATH` 隔离保护，不能指向长期业务库
   - 历史 MySQL fixtures 已接入测试库名保护，误配成业务库名时直接失败
   - 依赖 MySQL fixtures 的 `webtest` 现在会自动打上 `mysql_integration` 标记
   - 默认 pytest 收集会把这批 MySQL 测试排除；显式 `pytest -m mysql_integration` 时才会收集
   - 这部分落地情况已经归档到 `apps/backend/web/docs/desc/lite_migration/project/05_lite_database_layering_strategy.md`

2. 未完成
   - 仓库还没有把 SQLite 默认层 / MySQL 兼容层拆成单独 CI job
   - 历史 `web/webtest` 仍有不少老用例继续依赖 MySQL 测试库，还没有逐步迁完

## 1. 任务目标

这次任务只解决一件事：

- 测试运行时必须使用专用测试库或临时库，不能和业务库混用

同时保留两个前提：

- lite 主线继续优先走 SQLite
- 少量确实需要 MySQL 行为验证的测试，可以保留专用 MySQL 测试库

## 2. 当前现状

当前仓库已经有三条测试路径：

1. `tests/`
   - 走 lite
   - 使用 pytest 临时目录下的 SQLite 文件
   - 已接入路径校验，默认不会碰长期 lite 业务库

2. `web/webtest` 的 lite fixture
   - `lite_webtest_app`
   - `lite_rollback_session`
   - 也是临时 SQLite
   - 已接入路径校验

3. `web/webtest` 的历史 fixture
   - `app`
   - `rollback_session`
   - `test_db_app`
   - `test_db_session`
   - 仍然使用 MySQL 测试库

当前问题不是“完全没隔离”，而是只完成了 lite / SQLite 这条线，历史 MySQL 这条线还没有统一成项目规则。

当前主要缺口是：

1. CI 还没有按 SQLite 默认层 / MySQL 兼容层拆 job
2. 历史 `web/webtest` 还没有按功能价值逐步迁到 SQLite

## 3. 选定方案

采用方案 4：分层策略。

规则如下：

1. 默认测试层统一走 SQLite 临时库
2. 只有明确标记为 MySQL 集成测试的用例，才允许使用 MySQL 测试库
3. MySQL 测试也只能连接专用测试库，不能连接业务库
4. 默认 `pytest` 不跑 MySQL 集成测试

## 4. 目标状态

改造完成后，测试分成两层。

### 4.1 默认层

- 覆盖范围：单元测试、lite 主线回归、绝大多数 `web/webtest`
- 数据库：pytest 临时 SQLite 文件
- 期望：本地开发和默认 CI 都跑这一层

### 4.2 MySQL 兼容层

- 覆盖范围：少量必须验证 MySQL 行为的集成测试
- 数据库：专用 MySQL 测试库
- 期望：单独命令、单独标记、可单独跑

## 5. 改造重点

### 5.1 夹具收口

当前测试夹具已经基本分成两套入口，但项目规则还没完全收口：

- SQLite 入口
  - `tests/conftest.py`
  - `web/webtest/conftest.py` 中的 lite fixtures
  - 当前状态：已落地

- MySQL 入口
  - `web/webtest/conftest.py` 中的历史 test fixtures
  - 当前状态：已补环境保护，且会自动加 `mysql_integration` 标记

后续新增测试默认只能使用 SQLite 入口。

### 5.2 标记收口

新增明确标记 `mysql_integration`。

规则：
- 使用 MySQL 测试库的测试必须显式打标
- 不带标记的默认测试不能走 MySQL fixture

当前状态：
- 已落地
- 当前通过 MySQL fixture 自动加标，不再依赖逐文件手写标记

### 5.3 环境保护

这部分要分开看：

- `LITE_DB_PATH` 的 pytest 隔离保护：已完成
- MySQL 测试库名保护：已完成

保护规则：

- `LITE_DB_PATH` 不允许指向正式业务库路径
- `TEST_DB_TESTDB`、`TEST_DB_DATABASE` 不允许等于业务库名
- fixture 初始化时发现目标库名明显不是测试库，直接报错
- 可以约定测试库名必须带 `_test`，SQLite 文件名必须带 `pytest-` 或位于 pytest 临时目录

### 5.4 默认执行策略

默认 `pytest` 只跑 SQLite 层。
MySQL 层单独执行，例如 `pytest -m mysql_integration`。
后续 CI 也拆成两个 job：默认 job 跑 SQLite，可选 job 跑 MySQL 兼容层。

当前状态：
- README 默认口径已收口
- 默认 pytest 现在不会收集依赖 MySQL fixtures 的 `webtest`
- CI job 还没有单独拆层

## 6. 实施步骤

后续建议只做剩余缺口，不重复做已完成的 SQLite / MySQL 隔离规则：

1. 先把 CI 拆成 SQLite 默认层 / MySQL 兼容层
2. 再按功能价值，逐步把能迁到 SQLite 的老 `web/webtest` 迁走
3. 最后收缩 MySQL 兼容层的范围，只保留必须验证方言行为的测试

## 7. 验收标准

核心规则完成后至少满足这些条件：

- 默认跑测试不会连接业务库
- 默认测试命令只使用临时 SQLite
- 所有依赖 MySQL fixtures 的测试都会带 `mysql_integration` 标记
- MySQL 测试只能连接专用测试库
- 故意把测试库变量配成业务库名时，fixture 会直接失败

## 8. 风险点

- 一部分老 `web/webtest` 仍然依赖 MySQL 行为，不能一步全迁
- 如果只更新文档，不补 MySQL 硬保护，仍然可能误连业务库
- 如果不先做标记收口，后面很难知道哪些测试还依赖 MySQL
- 如果 README 继续保留“直接 `pytest -q`”的泛化说法，容易误导日常使用
- 如果后续只停在“排除默认运行”，但一直不迁老 `webtest`，MySQL 兼容层会长期偏大

## 9. 推荐落地顺序

当前推荐顺序：

1. 先把 CI 按 SQLite 默认层 / MySQL 兼容层拆开
2. 再逐步把高价值、低方言依赖的老 `webtest` 迁到 SQLite

核心规则已经完成；后面的重点不再是“防误连”，而是“继续缩小 MySQL 兼容层”。
