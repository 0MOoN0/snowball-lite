# 任务 3：收口运行时 MySQL 专有 SQL

## 归档状态

- 状态：已完成
- 主要实现：`web/models/__init__.py`、`web/scheduler/__init__.py`
- 已收口路径：
  - `show variables like 'long_query_time'`
  - `SHOW TABLES LIKE 'apscheduler_jobs'`
- 默认验证命令：`pytest web/webtest/stage3 -q`

## 目标

把当前会直接挡住 SQLite 的 MySQL 专有 SQL，收口成方言可判断、可降级的实现。

## 当前最明显的问题

### 1. 慢查询阈值读取仍然写死 MySQL 语法

位置：

- `web/models/__init__.py`

当前问题：

- 直接执行 `show variables like 'long_query_time'`

这在 SQLite 下没有意义，也会让日志注册逻辑一直走异常分支。

### 2. scheduler 表检查仍然写死 MySQL 语法

位置：

- `web/scheduler/__init__.py`

当前问题：

- 直接执行 `SHOW TABLES LIKE 'apscheduler_jobs'`

虽然在这个阶段 lite 还默认关闭 scheduler，但这类写法继续留着，后面只要触发相关路径还是会出问题。

## 任务范围

- 把上面这些逻辑改成“先判断方言，再走对应实现”
- 能用 SQLAlchemy inspector 的地方尽量用 inspector
- 在 SQLite 下明确采用默认值或通用分支，不再靠抛异常兜底

## 推荐优先级判断

这一项比业务链路稍后一点，但不要拖到太晚。

原因：

- 业务链路测试迟早会碰到这些运行时逻辑
- 越晚处理，越容易在后面反复返工

## 验收标准

- 阶段三选中范围内，不再直接执行 MySQL 专有 SQL
- SQLite 下相关逻辑能走清晰的兼容分支
- MySQL 现有行为不被明显破坏

## 非目标

- 不要求把 scheduler 完整迁成 SQLite 持久化 JobStore
- 不要求现在就清理仓库里所有 MySQL 相关代码
- 只处理会挡住阶段三目标的那一批路径
