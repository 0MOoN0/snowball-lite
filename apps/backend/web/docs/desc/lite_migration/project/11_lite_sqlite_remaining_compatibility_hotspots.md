# lite 主线剩余 SQLite 兼容热点收口（归档）

- [x] 盘点 lite 主线已暴露的 SQLite 兼容问题和仓库剩余 MySQL 痕迹
- [x] 修复 scheduler 日志把异常对象直接写入 SQLite 的问题
- [x] 复查并收口其余“非基础类型直接入库”的高风险热点
- [x] 为高风险链路补 lite 回归测试
- [x] 将历史 MySQL 兼容债和 lite 主线问题分层归档，避免继续混淆

## 归档状态

- 类型：子任务归档文档
- 父任务：lite 主线 SQLite 兼容收口
- 状态：已完成
- 原任务路径：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/lite_sqlite_remaining_compatibility_hotspots.md`
- 已完成范围：关闭 scheduler 错误日志入库的 SQLite blocker，补 lite 回归测试，完成独立评审，并把历史 MySQL 残留与 lite 主线问题拆开记录
- review 产物：已按归档规则删除，不再长期保留
- 保留范围：只保留 `1~3` 个待复查热点作为后续候选，不把“全仓 MySQL 痕迹清零”混入本轮完成条件

## 0. 先说当前结论

当前不能把“全仓还有大量 MySQL 遗留”和“lite 主线还有很多运行时 blocker”混为一谈。

截至 `2026-03-22`，本轮完成后更接近下面这个判断：

1. 本轮唯一明确未修的同类 blocker 已关闭，也就是 `scheduler save_logs` 不再把异常对象直接写给 SQLite
2. lite 主线同类问题当前更接近 `0 个已确认未修 + 1~3 个待复查热点`
3. 全仓历史 MySQL 兼容债仍然明显存在，但大部分不在 lite 主线运行时

当前 evidence：

- `scheduler/__init__.py` 现在会先把 `JobExecutionEvent.exception` 转成字符串再写入 `tb_apscheduler_log.exception`
- `apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py` 已补错误事件入库的 lite 回归
- `PYTHONPATH=apps/backend pytest apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py -q` 当前通过，结果是 `9 passed`
- 独立评审已完成，结果无新发现；对应 review 中间产物已按归档规则删除
- `apps/backend/web` 下仍有 `53` 个 Python 文件包含 `mysql.` 或 `mysql+pymysql`

## 1. 问题定义

当前问题不是“lite 完全不能跑”，而是：

- 少数老路径仍按 MySQL 驱动的容错习惯写代码，SQLite 在绑定参数时会直接失败
- 当前排查过程里，历史 MySQL 遗留和 lite 主线现存问题容易被混在一起，导致任务边界失焦

## 2. 完成定义

本轮完成后，已满足下面几条：

- lite 主线运行时不再把当前已确认的 `Decimal`、异常对象等非基础类型直接写入高风险 SQLite 路径
- scheduler 错误日志写库链路在 lite 下可重复通过
- 已确认高风险热点至少补齐一轮显式 lite 回归测试
- 历史 MySQL 残留被明确标记为“非本轮范围”，不再混入本轮验收

## 3. 范围

本轮只覆盖 lite 主线运行时和其直接回归验证：

- 通知确认、scheduler 日志保存这类直接写库链路
- 由 Marshmallow / 业务拼装结果直接落 ORM 的老路径
- lite 回归测试和对应归档说明

## 4. 非目标

本轮不做下面这些事情：

- 不重写 `migrations/dev`、`migrations/stg`、`migrations/test` 的历史 MySQL 迁移脚本
- 不移除 `settings.py` 里的全部 MySQL 配置
- 不要求本轮把整个 `web/webtest` 迁成 SQLite
- 不把“全仓 MySQL 痕迹清零”当作本轮完成条件

## 5. 数据与存储影响

- 本轮新增修复直接影响 lite 运行时写入的 `tb_apscheduler_log.exception`
- `tb_record` 的 `Decimal` 入库问题已经在本轮前序修复中处理完成，本轮只要求保住这条已关闭路径的结论，不再重复改字段定义
- 当前改动范围只包含“写库前的类型归一化”，不新增表、不改字段类型、不调整 `__bind_key__` 绑定关系
- 本轮不新增 `lite/dev/stg/test` 迁移脚本；如果后面要改字段类型或历史表结构，另开迁移任务
- 数据归属只覆盖当前应用自己产生的 lite 运行时记录，不处理历史 MySQL 环境已有数据

## 6. API 与交互影响

- `/api/notification/<id>` 的对外接口契约保持不变，请求体、响应结构和调用方式都不因为本轮改变
- scheduler 侧不新增对外 API，本轮只修内部日志持久化，避免运行时报错后连错误日志都落不进去
- 本轮不引入新的前端交互，不新增开关，不改变现有日志目录口径

## 7. 生命周期与旧数据处理

- 本轮只保证修复后的新写入链路：后续再出现 scheduler 异常时，异常对象会先转成文本再写入 SQLite
- 对于修复前已经写失败的 scheduler 日志，本轮不做补写、不做历史回填，也不把“补历史数据”算进完成条件
- 现有 lite SQLite 数据、历史 MySQL 数据和迁移目录都保持原状，不做清理、删除或归档迁移
- 如果后续需要统一修历史脏数据、补写失败日志或继续清理 MySQL 遗留，单独拆后续任务，不混入本轮验收

## 8. 当前热点

### 8.1 本轮已关闭热点

- `scheduler/__init__.py`
  - `_get_error_msg()` 不再返回异常对象本体，而是先转成字符串再入库
  - `SchedulerLog.exception` 是文本字段，原先在 SQLite 下报过 `type 'TimeoutError' is not supported`
  - 本轮已用 lite 回归测试覆盖 `TimeoutError("boom")` 这条错误写库路径

### 8.2 后续高优先级复查热点

- 直接由 `fields.Decimal` 反序列化进 ORM 对象、随后写入 `Integer` 字段的路径
- 直接把第三方异常对象、枚举对象或非基础类型塞进 `Text` / `String` 字段的路径
- 没有 SQLite 专项回归，但运行时会直接写库的老 router / scheduler 代码

### 8.3 只记录、不纳入本轮完成条件的历史兼容债

- `settings.py` 中多套 `mysql+pymysql` 配置
- `web/webtest/conftest.py` 中历史 MySQL 默认夹具
- `migrations/dev|stg|test` 中大量 `mysql.*` 方言内容

## 9. 方案

这轮实际采用“先修必修热点，再补最小回归”的做法。

规则：

1. 写 `Integer` 前统一转成 `int`
2. 写文本字段前，异常对象、traceback、其它 Python 对象统一转成字符串
3. 只在 SQLite 需要额外处理的情况，优先收敛成小 helper，不把兼容逻辑散在多个调用点
4. 每修一个运行时热点，都补一条可以在 lite 下重复执行的回归

## 10. 验收与验证结果

- `PYTHONPATH=apps/backend pytest apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py -q -k 'listener_persists_error_exception_as_text'` 通过
- `PYTHONPATH=apps/backend pytest apps/backend/web/webtest/lite/test_lite_scheduler_sqlite_support.py -q` 通过，结果是 `9 passed`
- 独立评审结果为 `0 critical / 0 high / 0 medium / 0 low`
- 本轮已经能明确回答“lite 主线剩余兼容坑有哪些，哪些不属于本轮范围”

## 11. 风险点

- 如果只修 scheduler，不补同类复查和测试，后面仍可能在其它老路径重现同类报错
- 如果把 `53` 个 MySQL 引用文件都算成本轮 blocker，会高估 lite 主线风险并拉散任务边界
- 如果以后上游异常对象变成更复杂的包装类型，当前样例还需要再补一条回归

## 12. 后续动作

1. 如果继续推进，优先按 `8.2` 的热点再拆新的子任务
2. 历史 MySQL 残留继续按 legacy 口径处理，不并入本轮完成判断
3. 后续继续把“lite 主线 blocker”和“历史 MySQL 残留”分开记账，不再混成一个任务
