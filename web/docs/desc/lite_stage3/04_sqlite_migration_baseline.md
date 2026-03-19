# 任务 4：SQLite 迁移基线

## 归档状态

- 状态：已完成
- 已落地方案：方案 A，新建 `migrations_snowball_lite`
- 主要实现：`web/lite_bootstrap.py`、`migrations_snowball_lite/`
- 默认验证命令：`pytest web/webtest/stage3 -q`

## 目标

给 lite 建一个比 `db.create_all()` 更正式、也更容易解释的初始化基线。

## 为什么这一项要做

当前最大的问题不是 SQLite 完全不能用，而是初始化口径太弱：

- 现在主要靠 `db.create_all()`
- 这能证明“当前模型能建表”
- 但不能证明“后续版本怎么稳定初始化”

如果第三阶段想继续往前走，这件事必须补上。

## 推荐方向

第三阶段更适合做“lite 专用基线”，不适合重写全部历史迁移。

更务实的选择是：

### 方案 A：新增 lite 专用迁移基线

例如：

- `migrations_snowball_lite`

思路：

- 以当前已经验证过的 lite 模式为基准
- 从“现在的可用模型集合”出发做一份 SQLite 初始化基线
- 不追求回放历史 MySQL 演进过程

### 方案 B：明确文档化的 lite bootstrap 方案

如果这轮还不想马上引入独立迁移目录，至少也要把：

- 哪些表属于 lite 核心集合
- 初始化顺序是什么
- 为什么当前先接受这条路径

写成清楚的基线说明，并配套验证脚本或测试。

## 我的建议

优先倾向方案 A。

原因：

- 方案 B 解释成本低，但还是偏临时
- 方案 A 更像后续能维护下去的正式入口
- 同时又避免了“把全部历史迁移都改成 SQLite”的过大范围

## 验收标准

- 阶段三结束时，lite 不再只靠 `db.create_all()` 作为唯一初始化方式
- 选定方案有明确文档
- 至少有一条自动化验证，能证明这条初始化路径在 SQLite 下可用

## 非目标

- 不重写 `migrations_snowball_dev/stg/test` 的全部历史
- 不要求 dev/stg/test/prod 全部同步切换到新迁移目录
