# 任务 05：阶段 6 验收与最终结论（归档）

## 最终结论

可以正式认定：

- lite 主线已经完成脱离 MySQL server 的阶段 6 收口
- lite 主线现在可以按 SQLite 独立运行

## 结论依据

### 1. lite 已经不再以 MySQL server 为前提

- `create_app("lite")`
- `bootstrap_lite_database(...)`
- `web.lite_application`
- lite Gunicorn 配置

这些路径都已经在零 MySQL 口径下通过。

### 2. lite 核心业务已经能在纯 SQLite 环境下完成

- 资产、记录、分析三条主面回归通过
- 查询 API、smoke、DataBox 和 xalpha 回归通过
- lite 枚举版本查询已经可以直接从 SQLite 返回

### 3. 剩余 MySQL 依赖已经能解释清楚

当前仍然保留的 MySQL 相关路径主要是：

- 非 lite 的 `dev/stg/test/prod` 配置
- 历史 `web/webtest` MySQL 夹具和旧测试基类

它们属于历史兼容路径，不再阻断 lite 主线结论。

### 4. 阶段 6 的问题已经复验收口

- Gunicorn 下的重复 bootstrap 已修复并复验
- lite 下的枚举版本查询已切到 SQLite 并复验
- 当前没有继续阻断最终结论的 stage6 blocker

## 仍然保留的边界

- 这个结论只覆盖 `lite` 主线，不等于整个仓库的所有环境都已经完成 SQLite 迁移
- Redis、scheduler、task queue、profiler 仍然默认不属于 lite 主线保证范围
- pandas、akshare、BeautifulSoup、SQLite Decimal 相关 warning 仍在，但当前不是 blocker

## 后续建议

如果继续推进，建议优先做两件事里的一个：

1. 继续收缩历史 MySQL 测试夹具和非 lite 路径里的默认 MySQL 假设
2. 继续扩大 lite 在资产扩展查询、记录筛选和外围接口上的覆盖面
