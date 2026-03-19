# 任务 04：阶段 6 正式代码审查、修复与再审查（归档）

## 完成状态

- 已完成
- 结论：阶段 6 相关改动已经经过问题修复和复验，当前没有继续阻断最终结论的 stage6 blocker

## 这一轮实际 review 关注点

- 零 MySQL 启动和 bootstrap 是否真的幂等
- lite 本地入口、Gunicorn 入口、`uv` 启动口径是否一致
- lite 运行时边界是否还有不必要的 Redis / MySQL 强依赖
- 新增测试是否把关键问题卡住，而不是只验证最顺的 happy path

## review 里实际收掉的问题

- Gunicorn 检查时 SQLite 已有表重复建表
- lite 下的 `/api/enums/versions` 仍然依赖 Redis 语义
- 本地启动链路的入口和文档口径不统一

## 复验结果

- `python -m pytest tests/test_lite_bootstrap_review.py -q`
  结果：`5 passed, 1 warning`
- `python -m pytest tests/test_lite_runtime_dependency_boundary.py -q`
  结果：`2 passed, 1 warning`
- `python -m gunicorn.app.wsgiapp --check-config -c web/gunicorn_lite.config.py web.lite_application:app`
  在 lite 环境变量下通过
- 阶段 6 的启动 / 初始化 / 核心业务固定命令已重新通过，见前 3 份归档文档

## 再审查结论

- 当前没有继续影响 stage6 结论的中等或以上问题
- 剩余 warning 主要来自 pandas、akshare、BeautifulSoup 和 SQLite Decimal 行为，不属于“lite 仍依赖 MySQL”这一类 blocker
- 因此可以进入阶段 6 的最终验收与结论文档
