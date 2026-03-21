# 任务 03：收口零 MySQL 验收暴露出的 lite 主线 blocker（归档）

## 完成状态

- 已完成
- 结论：阶段 6 零 MySQL 验收里暴露出的 lite 主线 blocker 已经收口，剩余 MySQL 相关代码都能归回历史路径或非 lite 范围

## 本阶段实际清理的 blocker

### 1. Gunicorn 下的 SQLite 重复 upgrade

- 问题：Gunicorn 导入 `web.lite_application:app` 时，lite bootstrap 可能在已有 SQLite 库上重复跑 Alembic，触发“已有表重复建表”
- 处理：
  - 在 [web/lite_bootstrap.py](/Users/leon/projects/snowball-lite/web/lite_bootstrap.py) 增加 SQLite schema 就绪判断
  - 增加 bootstrap 锁，避免并发或重复导入下的冲突
- 结果：lite Gunicorn 配置检查已通过

### 2. lite 下的枚举版本查询仍然绑 Redis

- 问题：`/api/enums/versions` 在 lite 下原来会直接返回“不支持”，这会把一个本来可以本地化的运行时信息继续绑在 Redis 上
- 处理：
  - 在 [web/common/utils/enum_utils.py](/Users/leon/projects/snowball-lite/web/common/utils/enum_utils.py) 新增 SQLite 版枚举版本读写
  - 在 [web/routers/system/enum_version_routers.py](/Users/leon/projects/snowball-lite/web/routers/system/enum_version_routers.py) 把 lite 分支改成从 SQLite 的 `system_settings` 读取
  - 在 [web/lite_bootstrap.py](/Users/leon/projects/snowball-lite/web/lite_bootstrap.py) 里于 bootstrap 后写入 `version:enum`
- 结果：lite 运行时边界测试已更新为“成功从 SQLite 读版本”

### 3. VS Code / Gunicorn 本地启动路径分裂

- 问题：lite 本地运行之前只有历史入口，VS Code 单文件启动也容易因为模块路径和解释器不一致而失败
- 处理：
  - 新增 [web/lite_application.py](/Users/leon/projects/snowball-lite/web/lite_application.py)
  - 新增 [web/gunicorn_lite.config.py](/Users/leon/projects/snowball-lite/web/gunicorn_lite.config.py)
  - README 和环境变量指南同步补齐 lite / uv / Gunicorn 启动说明
- 结果：lite 本地入口已经形成统一口径

## 仍然保留但不属于 lite blocker 的路径

- `web/settings.py` 里的 `dev/stg/test/prod` 仍然保留 `mysql+pymysql`
- `web/webtest/conftest.py` 里的历史 MySQL 建库夹具还在
- 旧的 Web 测试基类和少量非 lite 路由仍然保留历史兼容行为

## 本任务结论

- 当前剩余的 MySQL 相关代码已经不再阻断 lite 主线
- lite 阶段 6 的最终结论可以建立在这些 blocker 已经被修掉的前提下
