# 任务 1：SQLite 测试夹具桥接

## 归档状态

- 状态：已完成
- 主要实现：`web/webtest/conftest.py`、`web/webtest/test_base.py`
- 新增内容：`lite_webtest_app`、`lite_webtest_client`、`lite_rollback_session`
- 默认验证命令：`pytest web/webtest/stage3 -q`

## 目标

让第三阶段选中的旧测试，不再强依赖 MySQL server，而是能在临时 SQLite 文件库上跑。

## 为什么这一项优先级最高

当前最直接的阻塞点就在测试夹具：

- `web/webtest/conftest.py` 默认走 `test` 配置
- `setup_test_database()` 会直接连 MySQL
- 里面还有 `CREATE DATABASE IF NOT EXISTS ...`
- `rollback_session` 也默认绑在 `db.engines["snowball"]`

这意味着只要沿用旧夹具，阶段三任何“更业务化”的验证都会被 MySQL 前置条件卡住。

## 任务范围

- 给 `web/webtest/` 增加一组只服务第三阶段的 SQLite 夹具
- 允许选定测试模块使用 lite 或 stage3 专用配置启动
- 给事务回滚、临时库文件、环境变量初始化提供统一入口
- 明确哪些旧基类能直接复用，哪些需要单独补 bridge fixture

## 推荐落点

- `web/webtest/conftest.py`
- `web/webtest/test_base.py`
- `tests/conftest.py`

必要时可以新增一组更明确的 fixture 名称，例如：

- `lite_webtest_app`
- `lite_webtest_client`
- `lite_rollback_session`

## 验收标准

- 选中的 stage3 测试不再要求本地 MySQL server 存在
- 选中的 stage3 测试不再执行 `CREATE DATABASE IF NOT EXISTS ...`
- SQLite 临时库和缓存路径都由 fixture 统一提供
- 有一条固定命令，能跑阶段三选中的 SQLite 集成测试

## 非目标

- 不要求一次改完全部 `web/webtest/`
- 不要求所有旧测试基类都兼容 SQLite
- 不要求现在就处理外部依赖类 manual test
