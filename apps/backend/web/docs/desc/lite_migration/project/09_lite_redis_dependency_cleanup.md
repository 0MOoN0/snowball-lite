# lite 去 Redis 收口（归档）

## 归档状态

- 状态：已完成
- 原任务路径：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/lite_redis_dependency_cleanup_strategy.md`
- 说明：这份文档已从 `task/` 归档到 `desc/lite_migration/project/`，保留完整设计、实现和验收结论
- 当前事实：lite 主线在本任务范围内已经完成 Redis 收口；`/system/token`、databox token 注入、通知发送、资产初始化和 scheduler 手动任务解析都不再把 Redis 当默认前提

## Checklist

- [x] lite 默认禁用 Redis 和 Dramatiq
- [x] `/api/enums/versions` 已切到 SQLite
- [x] lite 启动已验证不依赖 `redis` 包
- [x] `/system/token` 改成 SQLite 持久化
- [x] databox 启动期 token 注入去 Redis
- [x] lite 下的通知、资产初始化完成无 Redis 收口
- [x] scheduler 历史 Redis 映射兼容尾巴清理
- [x] lite 文档、依赖和回归测试同步收口

## 任务状态
- 状态：已完成
- 目标：让 lite 主线在代码、配置、文档、测试四个层面都不再以 Redis 为前提
- 边界：不删除历史 `dev/stg/test/prod` 的 Redis 能力，但 lite 不再读写 Redis
- 当前判断：lite 主线在本任务范围内已经完成 Redis 收口，历史环境 Redis / Dramatiq 路径继续保留
## 1. 任务目标
1. lite 主线不再初始化、读取、写入 Redis
2. lite 继续保留 SQLite、本地 scheduler、xalpha cache 和核心业务链路
3. 历史环境继续可用，不顺手改坏旧的 Redis 路径
4. 接口和文档明确说明 lite 下哪些能力降级、哪些能力改走替代实现
## 2. 当前现状
- `LiteConfig` 已设置 `ENABLE_REDIS=False`、`ENABLE_TASK_QUEUE=False`
- `create_app("lite")` 启动时会跳过 cache 和 task queue 初始化
- `/api/enums/versions` 在 lite 已改从 SQLite 读取
- `/system/token` 在 lite 直接失败，说明系统 token 读写还绑在 Redis
- `databox.init_app()` 仍会从 Redis 读取 `XQ_TOKEN`
- `task/` 下的 Dramatiq broker 仍然依赖 Redis
- `scheduler._resolve_job_id()` 仍保留 `DYNAMIC_JOB:*` 的 Redis 兼容读取
- `requirements.txt`、`docker-compose.yml` 和部分文档还保留 Redis 口径
## 3. 任务边界
### 3.1 在范围内
- lite 下 Redis 直接读写点清理
- lite 下队列型调用的替代实现
- lite 长期文档、运行说明和测试收口
- lite 下无 Redis 的启动和接口回归
### 3.2 不在范围内
- 删除传统环境 Redis 配置
- 重做 `dev/stg/test/prod` 的部署方案
- 把所有异步能力整体替换成全新框架
## 4. 选定方案
采用“按用途拆替代方案”的收口方式，不再找一个组件硬替 Redis 全部职责。
1. 小体量键值状态
   - 选 SQLite `system_settings`
   - 适用对象：`XQ_TOKEN`、`SERVERCHAN_SENDKEY`、运行时版本号
   - 原因：lite 现在本来就只有单机 SQLite 主线，这类配置数据不需要 Redis
2. 查询和拉数缓存
   - 继续沿用现有 `xalpha` cache backend
   - 默认使用独立 SQLite cache
   - 保留显式 `csv` 和 `memory` fallback
3. 轻量异步或延迟任务
   - lite 下优先同步执行
   - 必须延迟或重试时，改走 APScheduler 的单机一次性 job
   - 持久化仍落独立 SQLite jobstore
4. 手动调度任务映射
   - 不再依赖 Redis 临时映射
   - 统一依赖 `manual_job_id` 内嵌原始 job id
5. 历史环境兼容
   - 非 lite 环境继续保留 Redis + Dramatiq
   - lite 分支通过配置和代码分支显式走替代实现
## 5. 组件级改造内容
### 5.1 系统 token 与发送配置
需要把 `/system/token` 的两类数据从 Redis 移到 SQLite：
1. `XQ_TOKEN`
2. `SERVERCHAN_SENDKEY`
落地要求：
- lite 下 `GET /system/token` 和 `PUT /system/token` 不再返回“Redis 不支持”
- token 持久化统一写到 `system_settings`
- 读写结构保持现有接口格式，避免前端额外改协议
- 如需脱敏或加密，放在服务层处理，不把逻辑继续堆在 router
### 5.2 databox 启动期 token 注入
当前 `databox.init_app()` 还是从 Redis 拉 `XQ_TOKEN`。
需要改成下面口径：
1. lite 下改从 SQLite 配置读取 token
2. 读不到 token 时保持可启动，不报 Redis 相关错误
3. `token_test` 的临时注入能力继续保留，作为无持久化调试入口
### 5.3 枚举版本
这一块已经完成 SQLite 替代，不再作为主改造项。
本任务只做两件事：
1. 保持 lite 路径只读写 SQLite
2. 文档里明确这是已完成基线，不再回退 Redis
### 5.4 通知与任务队列
lite 下不再启动 Dramatiq worker，通知链路按下面口径收口：
1. 通知发送保留“优先 actor、失败回退 sync”的现状
2. lite 下直接走同步发送，不再把 Redis broker 当运行前提
3. 需要重试或延迟的通知任务，改由 scheduler 负责补位，不重新引入 Redis
### 5.5 资产初始化链路
资产新增后现在还有 `init_asset.send_with_options(...)` 这类队列型调用。
lite 下选定方案：
1. 保留旧环境 actor 路径
2. lite 下改成显式分支
3. 默认优先同步服务调用
4. 如果同步执行成本过高，再落到 APScheduler 一次性 job，而不是 Redis 队列
### 5.6 scheduler 历史兼容尾巴
需要清理 `_resolve_job_id()` 中对 `DYNAMIC_JOB:*` 的 Redis fallback。
收口条件：
1. 新手动任务统一只走 `manual_job_id`
2. lite 下不再尝试取 Redis 映射
3. 保留是否继续兼容旧环境 Redis fallback 的显式判断，不把 lite 和历史环境混在一起
## 6. 代码落点
- `apps/backend/web/routers/system/system_data_routers.py`
- `apps/backend/web/databox/data_box.py`
- `apps/backend/web/services/system/`
- `apps/backend/web/common/utils/enum_utils.py`
- `apps/backend/web/scheduler/notification_dispatch.py`
- `apps/backend/web/scheduler/__init__.py`
- `apps/backend/web/routers/asset/AssetRouters.py`
- `apps/backend/web/task/`
- `docs/backend/runtime-config.md`
- `docs/backend/system-overview.md`
- `docs/backend/lite-mysql-matrix.md`
- `README.md`
## 7. 实施步骤
1. 先补 lite 下 token / sendkey 的 SQLite 存储服务
2. 再改 `/system/token` 和 databox token 读取路径
3. 再把 lite 下通知、资产初始化的 Redis 队列依赖改成同步或 scheduler 分支
4. 再清理 scheduler 的 Redis 历史兼容读取
5. 最后收口 README、backend 长期文档、依赖说明和回归测试
## 8. 验收标准
- lite 启动、bootstrap、关键接口不依赖 Redis
- lite 下 `/system/token` 可正常读写，且数据落 SQLite
- lite 下 databox 读取 token 不再访问 Redis
- lite 下通知发送不要求 Redis broker
- lite 下资产初始化链路不要求 Redis broker
- lite 下 scheduler 手动任务不再读取 Redis 动态映射
- lite 的运行文档不再把 Redis 说成默认前提
- 无 Redis 回归测试覆盖启动、token、enum version、通知和 scheduler 关键路径
## 9. 风险点
- `/system/token` 改存储位置后，如果不处理旧值迁移，历史 Redis 里的 token 不会自动带过来
- 资产初始化如果直接改同步执行，接口耗时可能变长
- 通知从 actor 改为 lite 下默认同步后，失败重试策略要补清楚
- 如果只改代码不改文档，用户仍会被旧环境变量说明误导
- 如果只停在“lite 不初始化 Redis”，但不清理调用点，后续功能回归还会反复踩到旧路径
## 10. 推荐落地顺序
1. 先解决 `/system/token` 和 databox token，这是最直接的 Redis 读写点
2. 再解决 lite 下的队列型调用，这是最容易变成隐性 Redis 依赖的部分
3. 最后清理 scheduler 兼容尾巴、依赖说明和文档口径
这次任务的重点不是“把 Redis 换成另一个中间件”，而是把 lite 真正收成单机 SQLite 主线。
