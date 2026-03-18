# Changelog

## Unreleased

- 完善日历检查提醒

## [0.1.0] - 2026-03-19

- 建立 `snowball-lite` 独立仓库基线
- 收口阶段一 lite 启动、SQLite 最小链路、`xalpha` / DataBox 初步兼容
- 整理阶段一和阶段二文档到 `web/docs/desc/lite_stage1`、`web/docs/desc/lite_stage2`
- 调整版本和发布配置，使 lite 项目从 `main` / `v0.1.0` 开始独立演进

## Lite 基线说明

从这一版开始，`snowball-lite` 作为独立项目维护。

- 来源仓库：`snowball`
- 来源分支：`codex/lite-spike`
- 来源提交：`8d803c37fd1d689aca862348814b34addc892967`
- 下方保留的历史记录主要用于追溯原仓库演进，不再作为 lite 项目的正式版本序列

## v0.12.3 - 2026.12.17

- 更新 2026 交易日历

- 增加网格的回测模板类

- 通过 `cftable` 更加灵活的生成 `trade` `itrade` 类

## [1.16.0](https://github.com/0MOoN0/snowball/compare/snowball-v1.15.0...snowball-v1.16.0) (2025-12-24)


### Features

* **record:** 新增交易记录导入功能 ([d96493e](https://github.com/0MOoN0/snowball/commit/d96493eda27e344d4c98af49fef54a8258d61284))
* **record:** 添加交易记录文件导出功能并重构相关代码 ([0e3abca](https://github.com/0MOoN0/snowball/commit/0e3abca71d9c3b3b773e5c2f9a51601723b31b12))
* **record:** 添加导出前检查接口并优化导出功能 ([59d2239](https://github.com/0MOoN0/snowball/commit/59d2239803bfca146fc792e593bed27cde61b440))
* **record:** 添加资产别名查询功能及显示主要别名信息 ([a13e6be](https://github.com/0MOoN0/snowball/commit/a13e6bedb05551a6ba5c5b210f17ec3517728ad9))
* 新增交易记录导入服务、数据模型、相关枚举和测试。 ([3bfed73](https://github.com/0MOoN0/snowball/commit/3bfed7330ad7a9bdbd186a725918346d395f6f2e))
* 新增记录导入服务及相关模型、枚举、路由和测试，支持多种导入模式。 ([f91a8c7](https://github.com/0MOoN0/snowball/commit/f91a8c77730432cc930eb03fe2dc65681692b6ff))
* 新增记录文件导入功能，支持CSV/XLSX格式及追加、覆盖、替换等多种导入模式。 ([6b7b5c9](https://github.com/0MOoN0/snowball/commit/6b7b5c98dd9d8e3b4ccb32b4308521ed7b539437))
* 新增记录文件导入导出功能，包括API路由、数据模型、业务逻辑和测试。 ([a16ee4e](https://github.com/0MOoN0/snowball/commit/a16ee4e09878f91091bdc2bc7608804a3953c085))
* 更新Record模型，调整了tb_asset_alias和tb_record表的列注释，为tb_trade_reference表添加了唯一约束，并新增record.csv和record.xlsx数据文件。 ([6b90c9f](https://github.com/0MOoN0/snowball/commit/6b90c9fdcb02f0c2d7bde7d92068c06ba8f35fdd))
* 添加 record.xlsx 和 record.csv 数据文件，并更新 .gitignore 忽略 .task 文件 ([4136dd5](https://github.com/0MOoN0/snowball/commit/4136dd5fceeac1951913b2903ed996c76dbbbaf5))
* 添加网格交易相关路由、调度模块、示例数据和项目规则文档，并更新依赖。 ([8c90cd3](https://github.com/0MOoN0/snowball/commit/8c90cd332b752cc84d3c792012e22547010f44bc))
* 添加记录导入服务及相关数据文件 ([ce20b97](https://github.com/0MOoN0/snowball/commit/ce20b97a46e6b6de10fdd1aaf56cc545881f2cfc))
* 添加调度器模块、初始数据文件并更新依赖。 ([97166b7](https://github.com/0MOoN0/snowball/commit/97166b7b65d735750b303f60783dddfc9446c239))

## [1.15.0](https://github.com/0MOoN0/snowball/compare/snowball-v1.14.0...snowball-v1.15.0) (2025-12-07)


### Features

* **record:** 重构交易记录关联功能，实现通用关联模型 ([8b3f590](https://github.com/0MOoN0/snowball/commit/8b3f590002a52507fa3564cd052f3632cf9d2822))
* 新增交易参考记录模型和枚举，并调整tb_trade_reference表group_type字段默认值和注释 ([c54df92](https://github.com/0MOoN0/snowball/commit/c54df92e7e8e863087a66a0cfe14bf20e0f6d65a))
* 新增通用交易关联表 `tb_trade_reference` 模型及其迁移脚本、注册和相关分析数据模型与测试文件，并更新文档 ([832b0d8](https://github.com/0MOoN0/snowball/commit/832b0d8d95b75ab9c763c78c9a9ab39d36a4d1d8))

## [1.14.0](https://github.com/0MOoN0/snowball/compare/snowball-v1.13.0...snowball-v1.14.0) (2025-12-07)


### Features

* 新增交易记录扩展分析功能及其相关模型、数据适配器和测试。 ([3d8d689](https://github.com/0MOoN0/snowball/commit/3d8d6891ac98b8cec23275add1a8078bff282c41))

## [1.13.0](https://github.com/0MOoN0/snowball/compare/snowball-v1.12.0...snowball-v1.13.0) (2025-11-30)


### Features

* **record:** 新增交易记录列表路由和测试用例 ([f4df029](https://github.com/0MOoN0/snowball/commit/f4df029c1b003d7e2300862c8b61aec6b482b3be))


### Bug Fixes

* **conftest:** 指定query_cls以支持paginate方法 ([f4df029](https://github.com/0MOoN0/snowball/commit/f4df029c1b003d7e2300862c8b61aec6b482b3be))

## [1.12.0](https://github.com/0MOoN0/snowball/compare/snowball-v1.11.0...snowball-v1.12.0) (2025-11-29)


### Features

* **migration:** 添加年化收益率字段的数据库迁移脚本 ([da1962d](https://github.com/0MOoN0/snowball/commit/da1962ddbe1ebdba6e763cc95d1730413f195ff3))
* **model:** 在TradeAnalysisData模型添加annualized_return字段 ([da1962d](https://github.com/0MOoN0/snowball/commit/da1962ddbe1ebdba6e763cc95d1730413f195ff3))
* **router:** 新增仪表板路由和交易图表路由 ([da1962d](https://github.com/0MOoN0/snowball/commit/da1962ddbe1ebdba6e763cc95d1730413f195ff3))
* **transaction-charts:** 新增交易收益排名图表功能 ([df75fad](https://github.com/0MOoN0/snowball/commit/df75fad5d4c45608b86b5dee58443a6ca021b04e))
* **仪表板:** 添加总体交易分析数据接口及测试 ([be34ebb](https://github.com/0MOoN0/snowball/commit/be34ebb070b589b42b46e21a790e07f6f0f99b31))
* 添加年化收益率字段并重构交易图表路由 ([da1962d](https://github.com/0MOoN0/snowball/commit/da1962ddbe1ebdba6e763cc95d1730413f195ff3))

## [1.11.0](https://github.com/0MOoN0/snowball/compare/snowball-v1.10.0...snowball-v1.11.0) (2025-11-26)


### Features

* **asset:** 添加资产名称字段到别名查询结果并新增资产选择器接口 ([cbddda0](https://github.com/0MOoN0/snowball/commit/cbddda0333c247ff50f1081a7756dcb33d3398d3))
* **指数别名:** 新增指数别名管理功能 ([a13b5a7](https://github.com/0MOoN0/snowball/commit/a13b5a73aa4f64a5fb1a419c107273e3b451ca23))
* 改进资产列表的数据模型和接口处理。 ([26d9b51](https://github.com/0MOoN0/snowball/commit/26d9b517d25fccb226b090bbd4bfea4bcba232de))
* 更新资产路由的请求和响应数据模型定义 ([5cb33d5](https://github.com/0MOoN0/snowball/commit/5cb33d51b1984e8a2eeeffbd7dc8392b3867e04d))
* **资产别名:** 新增资产别名单条和批量操作接口 ([120c5be](https://github.com/0MOoN0/snowball/commit/120c5beb04f9b436edde004aafc72f11365dcc53))

## [1.10.0](https://github.com/0MOoN0/snowball/compare/snowball-v1.9.0...snowball-v1.10.0) (2025-11-15)


### Features

* **通知:** 支持按业务类型批量标记通知为已读 ([ff4d228](https://github.com/0MOoN0/snowball/commit/ff4d228356c7f74ce60fda2a5c00bcb5a7bd1058))
* **通知:** 添加批量已读和未读分组统计功能 ([ec52828](https://github.com/0MOoN0/snowball/commit/ec528282b967d0b412f8ecfb4f35d044740da8df))

## [1.9.0](https://github.com/0MOoN0/snowball/compare/snowball-v1.8.0...snowball-v1.9.0) (2025-11-08)


### Features

* **notification:** 添加通知相关枚举并优化日报内容结构 ([04e0391](https://github.com/0MOoN0/snowball/commit/04e03910688a1cdfee3f0e2b878d38f19a85eb26))

## [1.8.0](https://github.com/0MOoN0/snowball/compare/snowball-v1.7.3...snowball-v1.8.0) (2025-11-08)


### Features

* **scheduler:** 添加任务运行日志缓冲和持久化功能 ([adb98bf](https://github.com/0MOoN0/snowball/commit/adb98bf4a205a207eba244079630a043e12e994d))

## [1.7.3](https://github.com/0MOoN0/snowball/compare/snowball-v1.7.2...snowball-v1.7.3) (2025-11-07)


### Bug Fixes

* **notice_scheduler:** 修复未处理通知统计和异常任务查询逻辑 ([b013603](https://github.com/0MOoN0/snowball/commit/b01360335893e103f9b142602a1fd663bbe08761))

## [1.7.2](https://github.com/0MOoN0/snowball/compare/snowball-v1.7.1...snowball-v1.7.2) (2025-11-07)


### Bug Fixes

* 调整发布说明以验证 release-please 流水线 ([fe9556c](https://github.com/0MOoN0/snowball/commit/fe9556cd9bca994ab4beb4d11e8e5649da8e8300))

## [1.7.1](https://github.com/0MOoN0/snowball/compare/snowball-v1.7.0...snowball-v1.7.1) (2025-11-07)


### Bug Fixes

* 调整发布说明以验证 release-please 流水线 ([60d5cb8](https://github.com/0MOoN0/snowball/commit/60d5cb874a90bc1874bbdc5336c3ce6ad7154dbe))

## [1.7.0](https://github.com/0MOoN0/snowball/compare/snowball-v1.6.0...snowball-v1.7.0) (2025-11-07)


### Features

* **analysis:** 实现AmountTradeAnalysisData和服务类的功能扩展 ([5aa3aa2](https://github.com/0MOoN0/snowball/commit/5aa3aa24d28f6405237297c5deecdae47401954d))
* **analysis:** 新增金额交易分析数据模型及相关功能 ([f9893dd](https://github.com/0MOoN0/snowball/commit/f9893ddbfd934835f3c642a4c34d9d38120cdafb))
* **API:** 实现原始数据优先的API格式规范 ([1ba59d7](https://github.com/0MOoN0/snowball/commit/1ba59d78ad2c8b4e23732da19bdfa9b672fa1d54))
* **api:** 重构Flask-RESTX API实现并添加响应模型 ([087beae](https://github.com/0MOoN0/snowball/commit/087beae4f63d195ad68f5d431fe66e300a9cc035))
* **asset:** 优化资产列表接口代码格式和查询逻辑 ([c5848ee](https://github.com/0MOoN0/snowball/commit/c5848eecf2d2ea364e6d49ea829255c6538e3441))
* **asset:** 实现资产列表管理接口及批量删除功能 ([be50f0f](https://github.com/0MOoN0/snowball/commit/be50f0fcefd53c340d99689b3d323b46bcc798b5))
* **asset:** 实现资产多态更新功能及类型转换逻辑 ([323f17e](https://github.com/0MOoN0/snowball/commit/323f17eefbb88e106a833e88a70ed541f3ddf55e))
* **asset:** 新增资产管理接口路由及响应模型 ([40beb05](https://github.com/0MOoN0/snowball/commit/40beb05fd23286f3d3edf7d3e92d1a727a969cd6))
* **asset:** 添加场内基金模型并重构为联合表继承 ([49012a9](https://github.com/0MOoN0/snowball/commit/49012a984ca089c8bb629495982d9da397e69ab6))
* **asset:** 添加资产别名功能支持多数据提供商代码映射 ([bd2ccc2](https://github.com/0MOoN0/snowball/commit/bd2ccc2391e09fbefcdfff0a6d318e7f0d6e402a))
* **asset:** 添加资产状态枚举及相关字段 ([6a52f53](https://github.com/0MOoN0/snowball/commit/6a52f53b945668333173580501707928099997fc))
* **asset:** 重构资产列表查询逻辑并新增前端管理页面 ([ec73320](https://github.com/0MOoN0/snowball/commit/ec73320eac8ae41d682224214f03a556c54510e3))
* **decorator:** 添加scheduler_timeout装饰器用于APScheduler任务超时控制 ([97efc4a](https://github.com/0MOoN0/snowball/commit/97efc4aab0b2186c35aa7b9ac0074dfaa796a72b))
* **deploy:** 添加snow_view服务的nginx配置和docker部署文件 ([26a21d3](https://github.com/0MOoN0/snowball/commit/26a21d3bebe10e7555f624ebb8704a2944d9cf4a))
* **enum:** 添加动态枚举路由和枚举注册表 ([4fb0f45](https://github.com/0MOoN0/snowball/commit/4fb0f45479816f8b73621fa573c056f627d3aa7a))
* **enum:** 添加枚举版本管理功能 ([15ccf5c](https://github.com/0MOoN0/snowball/commit/15ccf5c030860ac820ba5d040433fb72c9becd25))
* **index:** 重构指数模块并添加详情功能 ([8477640](https://github.com/0MOoN0/snowball/commit/8477640fe0fc55b45897d57b911602d02cd643a6))
* **index:** 重构股票指数模型并更新相关文档 ([96bab98](https://github.com/0MOoN0/snowball/commit/96bab98029bffbb8bcc872956b4a0eac9ebde794))
* **migrations:** 为测试环境添加独立的数据库迁移配置 ([a10e3d3](https://github.com/0MOoN0/snowball/commit/a10e3d3cf28daeaf218e03f030c40b47f4dad078))
* **migrations:** 同步dev环境交易分析表结构到test环境 ([3298fa8](https://github.com/0MOoN0/snowball/commit/3298fa8dfdf15089595585bf75226b5918fe1520))
* **migrations:** 添加交易分析数据表迁移脚本 ([3389309](https://github.com/0MOoN0/snowball/commit/3389309a25b398521a49df99d2c2d34db83394af))
* **migrations:** 添加通知模型注释更新的迁移文件 ([a3ea9c3](https://github.com/0MOoN0/snowball/commit/a3ea9c3e683a62dafeba285df152b8718718c213))
* **models:** 添加指数模型模块，包含基础模型、股票指数模型和别名模型 ([f8fa5d9](https://github.com/0MOoN0/snowball/commit/f8fa5d9d6b1c0070b6352c216c6e18e68cbd036e))
* **notice:** 增强通知服务功能并添加集成测试 ([96435eb](https://github.com/0MOoN0/snowball/commit/96435eb4e8b2884d010daa6363b859d2a304598b))
* **notice:** 新增可转债申购通知功能 ([0048888](https://github.com/0MOoN0/snowball/commit/0048888bea6a67e9893a1146324d6b6215188333))
* **notice:** 添加调度器状态监控和异常任务报告功能 ([e085d06](https://github.com/0MOoN0/snowball/commit/e085d0685e8e3140bc60dbd8d22ccb8b81f03244))
* **notice:** 重构通知分析器并更新文档 ([f84d72f](https://github.com/0MOoN0/snowball/commit/f84d72f6aca246bb5a50e2c6bd95414685b94757))
* **notification:** 添加DataBox功能测试调度器及通知处理 ([4dfbc90](https://github.com/0MOoN0/snowball/commit/4dfbc901915d86206a6eba3b3aa64756e9a81011))
* **scheduler:** 添加手动任务包装函数实现任务隔离 ([488a961](https://github.com/0MOoN0/snowball/commit/488a9619f05195b19513332a38e2b6ab07a0df5c))
* **schema:** 统一字段命名规范并改进反序列化处理 ([b595e4c](https://github.com/0MOoN0/snowball/commit/b595e4c32c733b4f808a132d8d952e6808c573cb))
* **test:** 添加网格类型交易分析服务测试用例 ([c5155eb](https://github.com/0MOoN0/snowball/commit/c5155eb13779253be38ce4dd9e3a024602b219ee))
* **transaction_analysis:** 为网格交易分析添加业务类型参数 ([0af2ff4](https://github.com/0MOoN0/snowball/commit/0af2ff4ba0e5a47b6c008ecc8d4484ffb279892f))
* **基金模型:** 添加基金相关模型及数据库迁移 ([cb9dfab](https://github.com/0MOoN0/snowball/commit/cb9dfabe083b3275f1a2167be880ddfab294cc2d))
* **指数:** 实现指数多态转换与ORM级联删除功能 ([5ffc1a2](https://github.com/0MOoN0/snowball/commit/5ffc1a2f8410a7d01b4e25f8edd1739a5fac8649))
* **指数:** 新增指数列表管理接口及相关测试 ([1ab5cfa](https://github.com/0MOoN0/snowball/commit/1ab5cfa86760b13c602cbe9c87155cfc1eac1f46))
* **数据库:** 实现多数据库迁移支持并优化模型定义 ([a38e4ba](https://github.com/0MOoN0/snowball/commit/a38e4ba1197e03740bb77dc9043f937f40adfa7d))
* **数据库:** 添加可配置的数据库引擎日志和慢查询阈值 ([2188339](https://github.com/0MOoN0/snowball/commit/2188339bed2e38994f915e22147316876c5d35b2))
* **数据库迁移:** 添加通知模板键字段到通知表 ([7e4a4ce](https://github.com/0MOoN0/snowball/commit/7e4a4ce475a707a972fd0a137b7892751518e7d5))
* **数据库:** 重构网格交易分析数据模型为继承关系 ([a5bb9c5](https://github.com/0MOoN0/snowball/commit/a5bb9c5fdf099f46fb2b6dc5ebf9b19c5c1cc9e5))
* **数据服务:** 实现指数股息率数据获取功能 ([d47288b](https://github.com/0MOoN0/snowball/commit/d47288b07e47b6365c4b7e772548c03221207ab5))
* **数据迁移:** 添加TransactionAnalysisData关联修正的迁移脚本 ([de8ce0a](https://github.com/0MOoN0/snowball/commit/de8ce0a4a520694591f8a063deb6870425679f31))
* **日志:** 添加APScheduler日志配置支持 ([29c3dd2](https://github.com/0MOoN0/snowball/commit/29c3dd20eec95f7fe3ebe05e19d5e44350f5bfd6))
* **枚举路由:** 添加批量获取枚举数据接口 ([453e052](https://github.com/0MOoN0/snowball/commit/453e052fb5211ea24d7e855d87548d80b9a387c2))
* 添加测试环境数据库迁移配置及通知功能优化 ([e67c044](https://github.com/0MOoN0/snowball/commit/e67c044ab75dd45e3b51ac685221869b38279e47))
* 添加通知序列化和集成测试 ([9af4ec7](https://github.com/0MOoN0/snowball/commit/9af4ec7987edac908833b2a177dcee5c497eb4dc))
* **系统设置:** 增强系统设置API功能并完善文档 ([4789801](https://github.com/0MOoN0/snowball/commit/4789801d6337f839e51e5ddc2a1a3b13b5e9b857))
* **系统设置:** 实现批量更新系统设置功能 ([71c177b](https://github.com/0MOoN0/snowball/commit/71c177bc57599641bdfa68ec661019f251d22f4d))
* **系统设置:** 扩展系统设置更新接口支持更多字段 ([ca36a14](https://github.com/0MOoN0/snowball/commit/ca36a1401048c30fe9113bc9dd57254b403ccc83))
* **系统设置:** 添加批量更新接口并重构路由结构 ([a662c74](https://github.com/0MOoN0/snowball/commit/a662c74ff1c42ad202e7dd46fc585ec28b23a283))
* **系统设置:** 添加系统设置API模型和测试 ([fe4b7e1](https://github.com/0MOoN0/snowball/commit/fe4b7e15c0dd936cc173b31b0601d11b874f20ef))
* **系统设置:** 添加系统设置模型及相关功能 ([c5ba928](https://github.com/0MOoN0/snowball/commit/c5ba928580acc4c2a16cb7f67f9630eae80db7ce))
* **系统设置:** 添加系统设置模型和路由接口 ([fe7a954](https://github.com/0MOoN0/snowball/commit/fe7a954bb66ddde6d682c3d92488de95ba3e3cdf))
* **系统设置:** 添加系统设置模型用于统一管理配置参数 ([805d2d5](https://github.com/0MOoN0/snowball/commit/805d2d5a992516e4bd66ba6818953b4a8a400103))
* **网格交易分析:** 添加股息率字段并清理无效数据 ([c691eee](https://github.com/0MOoN0/snowball/commit/c691eee4fcc146b89e0346cb154e10e775c800c3))
* **适配器:** 实现基于注册表的适配器选择机制 ([7c64f4a](https://github.com/0MOoN0/snowball/commit/7c64f4ab6b2a9990607f8b07f81100caf3cacf70))
* **通知:** 实现多模板选择机制 ([92b0359](https://github.com/0MOoN0/snowball/commit/92b03594366bf37d3ac6d7b98c22b2be9bddfddf))
* **通知:** 添加系统每日报告功能 ([3124f26](https://github.com/0MOoN0/snowball/commit/3124f26900d21eed13cd0669165ff9b3e06812fd))
* **通知系统:** 实现多渠道通知系统支持 ([95d4942](https://github.com/0MOoN0/snowball/commit/95d4942abf48ae88ed35692a690d08e8d4a2a60c))
* **通知:** 重构通知渲染策略使用Jinja2模板 ([55ef8a5](https://github.com/0MOoN0/snowball/commit/55ef8a53632fd00ce814b9b26891b2ecdce81578))
* **配置:** 添加APScheduler日志级别配置 ([1e7b2cc](https://github.com/0MOoN0/snowball/commit/1e7b2cc54e525f6af1012f3543ca1ef7436f1690))


### Bug Fixes

* **analysis:** 修复AmountTransactionAnalysisService批量保存参数问题 ([25e6aa9](https://github.com/0MOoN0/snowball/commit/25e6aa9fee67d7aa21edd263b00d81505638cc23))
* **analysis:** 统一IRR字段单位为百倍并更新相关文档 ([45aa3b4](https://github.com/0MOoN0/snowball/commit/45aa3b4f3db4644befd907c92ee0b788fe232bf6))
* **Base.py:** 修正retry_when参数签名 ([9af4ec7](https://github.com/0MOoN0/snowball/commit/9af4ec7987edac908833b2a177dcee5c497eb4dc))
* **ci:** 移除临时测试文件与已删除脚本 ([ceb5fa8](https://github.com/0MOoN0/snowball/commit/ceb5fa8d6d1985a848373c3bb925d15680abf837))
* **data_box:** 修正error调用参数从exec改为exc_info ([7dc9547](https://github.com/0MOoN0/snowball/commit/7dc9547157007e665645397166f0142eb22d55ed))
* **deploy:** 修正docker-compose.yml中build路径格式 ([444cb34](https://github.com/0MOoN0/snowball/commit/444cb34eb4896b495a335b0d4d664c2f0e991afd))
* **deploy:** 修正Dockerfile中COPY命令的路径问题 ([abba0a9](https://github.com/0MOoN0/snowball/commit/abba0a9463ecc231faa2fb522ef2779c7d3b0c12))
* **deploy:** 修正docker构建时的文件复制路径问题 ([426b808](https://github.com/0MOoN0/snowball/commit/426b8084b62443b125c7151d9b1fd99c57a36af7))
* **docker:** 将SNOW_APP_STATUS环境变量从dev改为default ([1cf6152](https://github.com/0MOoN0/snowball/commit/1cf6152c4e553ef6e0eccbd719269db713d07474))
* **enum:** 更新枚举接口响应格式和消息文本 ([ff346ec](https://github.com/0MOoN0/snowball/commit/ff346ec64824add291a55a0954bf6811ad635533))
* **notification:** 添加已发送状态并清理无用代码 ([8f7af57](https://github.com/0MOoN0/snowball/commit/8f7af5753d934ecaef7a317ecaffebcd93edfb49))
* **RecordAdapter:** 修复交易日期列数据处理错误 ([86fdcbb](https://github.com/0MOoN0/snowball/commit/86fdcbb6d0a4fed37c1e3586bb27661beef686cb))
* **scheduler:** 为可转债申购提醒任务添加容错配置 ([ac00207](https://github.com/0MOoN0/snowball/commit/ac002071a6d365422881ec4f6f259133ef04b42f))
* **scheduler:** 修复scheduler_timeout装饰器导入错误 ([238282e](https://github.com/0MOoN0/snowball/commit/238282e86e318b39e5c645c28c78babcb23b5800))
* **test_system_settings_routers.py:** 更新错误消息断言 ([9af4ec7](https://github.com/0MOoN0/snowball/commit/9af4ec7987edac908833b2a177dcee5c497eb4dc))
* trigger release-please PR (temporary) ([3d5e2ab](https://github.com/0MOoN0/snowball/commit/3d5e2ab282c0095bc9375d08db086b7b92b1ef6d))
* **web/decorator:** 修复任务超时处理中的返回值获取问题 ([ff6e117](https://github.com/0MOoN0/snowball/commit/ff6e117d825482f4665bda9722a582d019160734))
* **任务调度:** 支持字符串形式的函数引用解析 ([84887bf](https://github.com/0MOoN0/snowball/commit/84887bfb9f2172bb0b9cd192d1f723a0fb3c4cb4))
* 修复GridStrategyTransactionAnalysisService和GridTransactionAnalysisService中的数据处理问题 ([db14b13](https://github.com/0MOoN0/snowball/commit/db14b1388196ede18a13ffa15832fae6029336bc))
* 修正交易接口错误信息格式化问题 ([a634180](https://github.com/0MOoN0/snowball/commit/a63418010dd1363a91a8323c42ea938c1d6fbd3f))
* **数据库:** 移除up_sold_percent和down_bought_percent的默认值 ([99a24cb](https://github.com/0MOoN0/snowball/commit/99a24cb45305a44b94727f93c593af357ae3a8fd))
* **数据库:** 设置up_sold_percent和down_bought_percent字段默认值为NULL ([f23170d](https://github.com/0MOoN0/snowball/commit/f23170d30d4524c6f5ca6463432f8f2317225430))
* **测试:** 修复测试文件中的资源清理和警告过滤问题 ([936a5d4](https://github.com/0MOoN0/snowball/commit/936a5d4e9156cdfd75c2275b00081a21f8ce258b))

## [1.6.0](https://github.com/0MOoN0/snowball/compare/snowball-v1.5.1...snowball-v1.6.0) (2025-11-07)


### Features

* **analysis:** 实现AmountTradeAnalysisData和服务类的功能扩展 ([5aa3aa2](https://github.com/0MOoN0/snowball/commit/5aa3aa24d28f6405237297c5deecdae47401954d))
* **analysis:** 新增金额交易分析数据模型及相关功能 ([f9893dd](https://github.com/0MOoN0/snowball/commit/f9893ddbfd934835f3c642a4c34d9d38120cdafb))
* **API:** 实现原始数据优先的API格式规范 ([1ba59d7](https://github.com/0MOoN0/snowball/commit/1ba59d78ad2c8b4e23732da19bdfa9b672fa1d54))
* **api:** 重构Flask-RESTX API实现并添加响应模型 ([087beae](https://github.com/0MOoN0/snowball/commit/087beae4f63d195ad68f5d431fe66e300a9cc035))
* **asset:** 优化资产列表接口代码格式和查询逻辑 ([c5848ee](https://github.com/0MOoN0/snowball/commit/c5848eecf2d2ea364e6d49ea829255c6538e3441))
* **asset:** 实现资产列表管理接口及批量删除功能 ([be50f0f](https://github.com/0MOoN0/snowball/commit/be50f0fcefd53c340d99689b3d323b46bcc798b5))
* **asset:** 实现资产多态更新功能及类型转换逻辑 ([323f17e](https://github.com/0MOoN0/snowball/commit/323f17eefbb88e106a833e88a70ed541f3ddf55e))
* **asset:** 新增资产管理接口路由及响应模型 ([40beb05](https://github.com/0MOoN0/snowball/commit/40beb05fd23286f3d3edf7d3e92d1a727a969cd6))
* **asset:** 添加场内基金模型并重构为联合表继承 ([49012a9](https://github.com/0MOoN0/snowball/commit/49012a984ca089c8bb629495982d9da397e69ab6))
* **asset:** 添加资产别名功能支持多数据提供商代码映射 ([bd2ccc2](https://github.com/0MOoN0/snowball/commit/bd2ccc2391e09fbefcdfff0a6d318e7f0d6e402a))
* **asset:** 添加资产状态枚举及相关字段 ([6a52f53](https://github.com/0MOoN0/snowball/commit/6a52f53b945668333173580501707928099997fc))
* **asset:** 重构资产列表查询逻辑并新增前端管理页面 ([ec73320](https://github.com/0MOoN0/snowball/commit/ec73320eac8ae41d682224214f03a556c54510e3))
* **decorator:** 添加scheduler_timeout装饰器用于APScheduler任务超时控制 ([97efc4a](https://github.com/0MOoN0/snowball/commit/97efc4aab0b2186c35aa7b9ac0074dfaa796a72b))
* **deploy:** 添加snow_view服务的nginx配置和docker部署文件 ([26a21d3](https://github.com/0MOoN0/snowball/commit/26a21d3bebe10e7555f624ebb8704a2944d9cf4a))
* **enum:** 添加动态枚举路由和枚举注册表 ([4fb0f45](https://github.com/0MOoN0/snowball/commit/4fb0f45479816f8b73621fa573c056f627d3aa7a))
* **enum:** 添加枚举版本管理功能 ([15ccf5c](https://github.com/0MOoN0/snowball/commit/15ccf5c030860ac820ba5d040433fb72c9becd25))
* **index:** 重构指数模块并添加详情功能 ([8477640](https://github.com/0MOoN0/snowball/commit/8477640fe0fc55b45897d57b911602d02cd643a6))
* **index:** 重构股票指数模型并更新相关文档 ([96bab98](https://github.com/0MOoN0/snowball/commit/96bab98029bffbb8bcc872956b4a0eac9ebde794))
* **migrations:** 为测试环境添加独立的数据库迁移配置 ([a10e3d3](https://github.com/0MOoN0/snowball/commit/a10e3d3cf28daeaf218e03f030c40b47f4dad078))
* **migrations:** 同步dev环境交易分析表结构到test环境 ([3298fa8](https://github.com/0MOoN0/snowball/commit/3298fa8dfdf15089595585bf75226b5918fe1520))
* **migrations:** 添加交易分析数据表迁移脚本 ([3389309](https://github.com/0MOoN0/snowball/commit/3389309a25b398521a49df99d2c2d34db83394af))
* **migrations:** 添加通知模型注释更新的迁移文件 ([a3ea9c3](https://github.com/0MOoN0/snowball/commit/a3ea9c3e683a62dafeba285df152b8718718c213))
* **models:** 添加指数模型模块，包含基础模型、股票指数模型和别名模型 ([f8fa5d9](https://github.com/0MOoN0/snowball/commit/f8fa5d9d6b1c0070b6352c216c6e18e68cbd036e))
* **notice:** 增强通知服务功能并添加集成测试 ([96435eb](https://github.com/0MOoN0/snowball/commit/96435eb4e8b2884d010daa6363b859d2a304598b))
* **notice:** 新增可转债申购通知功能 ([0048888](https://github.com/0MOoN0/snowball/commit/0048888bea6a67e9893a1146324d6b6215188333))
* **notice:** 添加调度器状态监控和异常任务报告功能 ([e085d06](https://github.com/0MOoN0/snowball/commit/e085d0685e8e3140bc60dbd8d22ccb8b81f03244))
* **notice:** 重构通知分析器并更新文档 ([f84d72f](https://github.com/0MOoN0/snowball/commit/f84d72f6aca246bb5a50e2c6bd95414685b94757))
* **notification:** 添加DataBox功能测试调度器及通知处理 ([4dfbc90](https://github.com/0MOoN0/snowball/commit/4dfbc901915d86206a6eba3b3aa64756e9a81011))
* **scheduler:** 添加手动任务包装函数实现任务隔离 ([488a961](https://github.com/0MOoN0/snowball/commit/488a9619f05195b19513332a38e2b6ab07a0df5c))
* **schema:** 统一字段命名规范并改进反序列化处理 ([b595e4c](https://github.com/0MOoN0/snowball/commit/b595e4c32c733b4f808a132d8d952e6808c573cb))
* **test:** 添加网格类型交易分析服务测试用例 ([c5155eb](https://github.com/0MOoN0/snowball/commit/c5155eb13779253be38ce4dd9e3a024602b219ee))
* **transaction_analysis:** 为网格交易分析添加业务类型参数 ([0af2ff4](https://github.com/0MOoN0/snowball/commit/0af2ff4ba0e5a47b6c008ecc8d4484ffb279892f))
* **基金模型:** 添加基金相关模型及数据库迁移 ([cb9dfab](https://github.com/0MOoN0/snowball/commit/cb9dfabe083b3275f1a2167be880ddfab294cc2d))
* **指数:** 实现指数多态转换与ORM级联删除功能 ([5ffc1a2](https://github.com/0MOoN0/snowball/commit/5ffc1a2f8410a7d01b4e25f8edd1739a5fac8649))
* **指数:** 新增指数列表管理接口及相关测试 ([1ab5cfa](https://github.com/0MOoN0/snowball/commit/1ab5cfa86760b13c602cbe9c87155cfc1eac1f46))
* **数据库:** 实现多数据库迁移支持并优化模型定义 ([a38e4ba](https://github.com/0MOoN0/snowball/commit/a38e4ba1197e03740bb77dc9043f937f40adfa7d))
* **数据库:** 添加可配置的数据库引擎日志和慢查询阈值 ([2188339](https://github.com/0MOoN0/snowball/commit/2188339bed2e38994f915e22147316876c5d35b2))
* **数据库迁移:** 添加通知模板键字段到通知表 ([7e4a4ce](https://github.com/0MOoN0/snowball/commit/7e4a4ce475a707a972fd0a137b7892751518e7d5))
* **数据库:** 重构网格交易分析数据模型为继承关系 ([a5bb9c5](https://github.com/0MOoN0/snowball/commit/a5bb9c5fdf099f46fb2b6dc5ebf9b19c5c1cc9e5))
* **数据服务:** 实现指数股息率数据获取功能 ([d47288b](https://github.com/0MOoN0/snowball/commit/d47288b07e47b6365c4b7e772548c03221207ab5))
* **数据迁移:** 添加TransactionAnalysisData关联修正的迁移脚本 ([de8ce0a](https://github.com/0MOoN0/snowball/commit/de8ce0a4a520694591f8a063deb6870425679f31))
* **日志:** 添加APScheduler日志配置支持 ([29c3dd2](https://github.com/0MOoN0/snowball/commit/29c3dd20eec95f7fe3ebe05e19d5e44350f5bfd6))
* **枚举路由:** 添加批量获取枚举数据接口 ([453e052](https://github.com/0MOoN0/snowball/commit/453e052fb5211ea24d7e855d87548d80b9a387c2))
* 添加测试环境数据库迁移配置及通知功能优化 ([e67c044](https://github.com/0MOoN0/snowball/commit/e67c044ab75dd45e3b51ac685221869b38279e47))
* 添加通知序列化和集成测试 ([9af4ec7](https://github.com/0MOoN0/snowball/commit/9af4ec7987edac908833b2a177dcee5c497eb4dc))
* **系统设置:** 增强系统设置API功能并完善文档 ([4789801](https://github.com/0MOoN0/snowball/commit/4789801d6337f839e51e5ddc2a1a3b13b5e9b857))
* **系统设置:** 实现批量更新系统设置功能 ([71c177b](https://github.com/0MOoN0/snowball/commit/71c177bc57599641bdfa68ec661019f251d22f4d))
* **系统设置:** 扩展系统设置更新接口支持更多字段 ([ca36a14](https://github.com/0MOoN0/snowball/commit/ca36a1401048c30fe9113bc9dd57254b403ccc83))
* **系统设置:** 添加批量更新接口并重构路由结构 ([a662c74](https://github.com/0MOoN0/snowball/commit/a662c74ff1c42ad202e7dd46fc585ec28b23a283))
* **系统设置:** 添加系统设置API模型和测试 ([fe4b7e1](https://github.com/0MOoN0/snowball/commit/fe4b7e15c0dd936cc173b31b0601d11b874f20ef))
* **系统设置:** 添加系统设置模型及相关功能 ([c5ba928](https://github.com/0MOoN0/snowball/commit/c5ba928580acc4c2a16cb7f67f9630eae80db7ce))
* **系统设置:** 添加系统设置模型和路由接口 ([fe7a954](https://github.com/0MOoN0/snowball/commit/fe7a954bb66ddde6d682c3d92488de95ba3e3cdf))
* **系统设置:** 添加系统设置模型用于统一管理配置参数 ([805d2d5](https://github.com/0MOoN0/snowball/commit/805d2d5a992516e4bd66ba6818953b4a8a400103))
* **网格交易分析:** 添加股息率字段并清理无效数据 ([c691eee](https://github.com/0MOoN0/snowball/commit/c691eee4fcc146b89e0346cb154e10e775c800c3))
* **适配器:** 实现基于注册表的适配器选择机制 ([7c64f4a](https://github.com/0MOoN0/snowball/commit/7c64f4ab6b2a9990607f8b07f81100caf3cacf70))
* **通知:** 实现多模板选择机制 ([92b0359](https://github.com/0MOoN0/snowball/commit/92b03594366bf37d3ac6d7b98c22b2be9bddfddf))
* **通知:** 添加系统每日报告功能 ([3124f26](https://github.com/0MOoN0/snowball/commit/3124f26900d21eed13cd0669165ff9b3e06812fd))
* **通知系统:** 实现多渠道通知系统支持 ([95d4942](https://github.com/0MOoN0/snowball/commit/95d4942abf48ae88ed35692a690d08e8d4a2a60c))
* **通知:** 重构通知渲染策略使用Jinja2模板 ([55ef8a5](https://github.com/0MOoN0/snowball/commit/55ef8a53632fd00ce814b9b26891b2ecdce81578))
* **配置:** 添加APScheduler日志级别配置 ([1e7b2cc](https://github.com/0MOoN0/snowball/commit/1e7b2cc54e525f6af1012f3543ca1ef7436f1690))


### Bug Fixes

* **analysis:** 修复AmountTransactionAnalysisService批量保存参数问题 ([25e6aa9](https://github.com/0MOoN0/snowball/commit/25e6aa9fee67d7aa21edd263b00d81505638cc23))
* **analysis:** 统一IRR字段单位为百倍并更新相关文档 ([45aa3b4](https://github.com/0MOoN0/snowball/commit/45aa3b4f3db4644befd907c92ee0b788fe232bf6))
* **Base.py:** 修正retry_when参数签名 ([9af4ec7](https://github.com/0MOoN0/snowball/commit/9af4ec7987edac908833b2a177dcee5c497eb4dc))
* **ci:** 移除临时测试文件与已删除脚本 ([ceb5fa8](https://github.com/0MOoN0/snowball/commit/ceb5fa8d6d1985a848373c3bb925d15680abf837))
* **data_box:** 修正error调用参数从exec改为exc_info ([7dc9547](https://github.com/0MOoN0/snowball/commit/7dc9547157007e665645397166f0142eb22d55ed))
* **deploy:** 修正docker-compose.yml中build路径格式 ([444cb34](https://github.com/0MOoN0/snowball/commit/444cb34eb4896b495a335b0d4d664c2f0e991afd))
* **deploy:** 修正Dockerfile中COPY命令的路径问题 ([abba0a9](https://github.com/0MOoN0/snowball/commit/abba0a9463ecc231faa2fb522ef2779c7d3b0c12))
* **deploy:** 修正docker构建时的文件复制路径问题 ([426b808](https://github.com/0MOoN0/snowball/commit/426b8084b62443b125c7151d9b1fd99c57a36af7))
* **docker:** 将SNOW_APP_STATUS环境变量从dev改为default ([1cf6152](https://github.com/0MOoN0/snowball/commit/1cf6152c4e553ef6e0eccbd719269db713d07474))
* **enum:** 更新枚举接口响应格式和消息文本 ([ff346ec](https://github.com/0MOoN0/snowball/commit/ff346ec64824add291a55a0954bf6811ad635533))
* **notification:** 添加已发送状态并清理无用代码 ([8f7af57](https://github.com/0MOoN0/snowball/commit/8f7af5753d934ecaef7a317ecaffebcd93edfb49))
* **RecordAdapter:** 修复交易日期列数据处理错误 ([86fdcbb](https://github.com/0MOoN0/snowball/commit/86fdcbb6d0a4fed37c1e3586bb27661beef686cb))
* **scheduler:** 为可转债申购提醒任务添加容错配置 ([ac00207](https://github.com/0MOoN0/snowball/commit/ac002071a6d365422881ec4f6f259133ef04b42f))
* **scheduler:** 修复scheduler_timeout装饰器导入错误 ([238282e](https://github.com/0MOoN0/snowball/commit/238282e86e318b39e5c645c28c78babcb23b5800))
* **test_system_settings_routers.py:** 更新错误消息断言 ([9af4ec7](https://github.com/0MOoN0/snowball/commit/9af4ec7987edac908833b2a177dcee5c497eb4dc))
* trigger release-please PR (temporary) ([3d5e2ab](https://github.com/0MOoN0/snowball/commit/3d5e2ab282c0095bc9375d08db086b7b92b1ef6d))
* **web/decorator:** 修复任务超时处理中的返回值获取问题 ([ff6e117](https://github.com/0MOoN0/snowball/commit/ff6e117d825482f4665bda9722a582d019160734))
* **任务调度:** 支持字符串形式的函数引用解析 ([84887bf](https://github.com/0MOoN0/snowball/commit/84887bfb9f2172bb0b9cd192d1f723a0fb3c4cb4))
* 修复GridStrategyTransactionAnalysisService和GridTransactionAnalysisService中的数据处理问题 ([db14b13](https://github.com/0MOoN0/snowball/commit/db14b1388196ede18a13ffa15832fae6029336bc))
* 修正交易接口错误信息格式化问题 ([a634180](https://github.com/0MOoN0/snowball/commit/a63418010dd1363a91a8323c42ea938c1d6fbd3f))
* **数据库:** 移除up_sold_percent和down_bought_percent的默认值 ([99a24cb](https://github.com/0MOoN0/snowball/commit/99a24cb45305a44b94727f93c593af357ae3a8fd))
* **数据库:** 设置up_sold_percent和down_bought_percent字段默认值为NULL ([f23170d](https://github.com/0MOoN0/snowball/commit/f23170d30d4524c6f5ca6463432f8f2317225430))
* **测试:** 修复测试文件中的资源清理和警告过滤问题 ([936a5d4](https://github.com/0MOoN0/snowball/commit/936a5d4e9156cdfd75c2275b00081a21f8ce258b))

## [1.5.1](https://github.com/0MOoN0/snowball/compare/v1.5.0...v1.5.1) (2025-11-02)


### Docs

* 更新README文档为Snowball项目内容 ([17ce1fb](https://github.com/0MOoN0/snowball/commit/17ce1fb9c7e9416f744fe03d347a07c30f04d6f5))


### CI

* **workflow:** 更新自动合并发布PR的工作流配置 ([f73a683](https://github.com/0MOoN0/snowball/commit/f73a68386cf3191c49e1c22b1eb277382261a391))
* **workflow:** 更新自动合并发布PR的工作流配置 ([1ba4eea](https://github.com/0MOoN0/snowball/commit/1ba4eeaa54ff7190038d6b50f6ea7e4a6ced77de))
* 修复 GitHub Actions 工作流中的语法错误和参数名称 ([8bd2726](https://github.com/0MOoN0/snowball/commit/8bd272610587045c941af867c4674490bf853a1c))
* 将automerge条件从job级别移至step级别 ([7d2d221](https://github.com/0MOoN0/snowball/commit/7d2d221901726ed5c6e93f5c419331ff5b39be55))

## [1.5.0](https://github.com/0MOoN0/snowball/compare/v1.4.0...v1.5.0) (2025-11-02)


### Features

* **notice:** 新增可转债申购通知功能 ([0048888](https://github.com/0MOoN0/snowball/commit/0048888bea6a67e9893a1146324d6b6215188333))


### CI

* 添加自动合并发布PR和工作流配置文件 ([9ddc0f5](https://github.com/0MOoN0/snowball/commit/9ddc0f57298617e19af39e6807ed4fc2b693bdcf))

## v0.12.2 - 2025.01.01

- 固定 numpy 版本小于 2

- 彻底修复雪球数据获取

## v0.12.1 - 2025.01.02

- 更新 2025 国际市场休息日

- 更新 2025 A 股交易日历

- 增加外部设置 token 的方式，修复雪球数据获取

## v0.12.0 - 2024.04.02

- 增加 2024 国际市场休息日

- 修复中间价 API

- 修复标普 API

- 修复新浪实时 API

- 重定向 indexinfo API，尽量兼容之前代码

- 修复中证指数日线 API

- 修复华证日线 API

- 修复 ycharts 实时 API

- 增加 ycharts 宏观数据源支持

- 修复可转债 API

## v0.11.11 - 2024.02.19

### fixed

- 将除夕改为非交易日

## v0.11.10 - 2023.12.04

### updated

- 更新 2024 交易日历

## v0.11.9 - 2023.07.11

### fixed

- 添加基金号检查，防止 rce 漏洞

- 固定 sqlalchemy 版本

## v0.11.8 -2023.06.04

### fixed

- 将 pandas 固定在 v1

## v0.11.7 - 2022.12.20

### updated

- 更新 2023 交易日历

### fixed

- 二进制表示十进制造成的分位误差

- 修复 `v_tradecost` 显示分红再投为交易点的 bug

## v0.11.6 - 2022.03.01

### fixed

- 网易数据源 encoding 修复

- 回测 cashobj 起始日期修复

## v0.11.5 - 2021.12.10

### added

- 更新 2022 A 股交易日历

### fixed

- 修复货币基金实时数据中的估值抓取处理报错

- 增加了场内账单默认净值的支持

- 可转债赎回价接口解析调整

## v0.11.4 - 2021.06.12

### added

- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- get_daily 增加富途数据源，包括了港股和美股的日线数据

- 增加 xa.cons.avail_dates 函数，用来将日期列表转变为最近的 A 股交易日列表

### fixed

- 实现 rget 状态码非 200 的自动重连

- 修复了波动率计算的乘数 typo

- 修复了 backtest 休市日期操作无法顺延的 bug

- 调整了 backtest 动态平衡类的赎回逻辑

- 修复了指数历史估值计算的除 0 bug

- 修复了 mul 类 tot 日期未传入的 bug

## v0.11.3 - 2021.01.31

### added

- 场内账单增加忽略基金的 # 前缀支持

- 增加了日历检查提醒

- 更新了主流国际市场 2021 休市日

- 增加了可转债工具箱对 B 评级可转债的支持

### fixed

- 进一步修改申购费自定义的小数点错误：第一笔申购情形

- 修复了 \_float 中遇到百分数的 bug

- 转 2 修正为可转债类型

## v0.11.2 - 2021.01.01

### added

- 修复了 `get_rt` 获取基金实时净值

- `fundinfo` 增加 `set_price` 方法用来临时改正基金的价格和分红等信息

### fixed

- 修复了申购费自定义的小数点位置错误处理

- 修复了日期检查 2020->2021

## v0.11.1 - 2020.12.12

### added

- k 线图可视化支持颜色和边框颜色自定义

- k 线图支持显示多个技术指标曲线

- vinfo 增加不归一选项

- 增添可转债计算器的属性信息

- 增加 2021 A 股交易日历数据

### fixed

- 修复了 k 线图可视化图标最高价和最低价标记顺序的错误

- 修复工银传媒基金转型后，申购费率数据差异造成的测试失败

- 修复投资组合类 `mul` 同时 fundtradobj 和账单共存时的 bug

## v0.11.0 - 2020.10.11

### added

- `get_rt` 现在支持中港互认基金元数据

- `get_daily` 支持中港互认基金日线数据

- `fundinfo` 支持中港互认基金交易 （高阶功能可能暂时不可用）

### fixed

- 修复记账单.005 表记 0 申购费可能出现的 bug

## v0.10.3 - 2020.09.17

### added

- 增加动态平衡回测类

### fixed

- 修改 fundreport 类兼容新版本网站源

## v0.10.2 - 2020.08.20

### added

- 添加了 a 股股票行业判断 API, 由此支持查看基金持仓的各行业占比， `fundinfo.get_industry_holdings()`
- 在 get_daily 之外，添加了 `fundinfo.get_portfolio_holdings()` API，查看底层股债占比的逻辑更自然
- 增加基金基于持仓的行业自动判定（实验性支持）： `fundinfo.which_industry()`
- 增加 `mul.get_industry` 支持组合的行业透视

## v0.10.1 - 2020.08.10

### added

- 场外账单支持日期乱序记录（但每天仍必须严格一行）

### fixed

- 兼容天天基金 API 增量更新出现的累计净值空白
- 修复当日开仓的重计 bug
- 修复标普数据源表格包含 nan 行的 bug

## v0.10.0 - 2020.07.06

### fixed

- 修复 info 类兼容 set_backend 指定数据库后端的 bug

### added

- 增加全新的动态回测引擎模块 xa.backtest
- 为了兼容动态回测，trade 支持增量更新账单的交易处理

## v0.9.4 - 2020.07.02

### added

- record 可以直接处理内存中的 DataFrame 账单。
- ioconf 增加自定义 key_func, 兼容缓存层对 key 支持不够的情况 （大小写不敏感，特殊字符等）

### fixed

- evaluate 类的可视化函数补充 rendered 选项
- 修正了 tradevolume 周数和 pandas 给出的 iso 周数不一定对应的问题
- 修复了超高价转债债券收益率求解的 runtimeerror，直接返回 None

## v0.9.3 - 2020.06.20

### added

- get_rt 字典增加 time_ext 盘外数据时间
- 账单代码自动补全 6 位，前边智能补零

## v0.9.2 - 2020.06.08

### added

- 账单上自定义单项交易的申购赎回费用
- mulfix 添加了 v_tradecost(), 可视化显示买卖点

### fixed

- pyecharts 再次引入 breaking API，这样的上游显得有些不负责任，跟进过于麻烦，若无其他情况，将永久将 pyecharts 版本 pin 到 1.7.1，其他版本 pyecharts 不再支持

## v0.9.1 - 2020.05.31

### added

- get_daily 增加国债和企业债利率历史数据

### fixed

- 修复 value_label=1 时，-0.005 代表的全部赎回逻辑
- 修复了当日新开仓基金，当日 trade 出现的报错
- 优化了 v_tradevolume 柱形图的显示效果

## v0.9.0 - 2020.05.17

### added

- get_rt 增加货币基金元信息支持
- mul 增加资产分类扇形图， mul.v_category_positions()
- 基金组合分析增加了股票透视功能，mul.get_stock_holdings(2020, 1) 直接看穿底层持仓股票及比例
- 基金组合分析增加了股债比例穿透 mul.get_portfolio()
- 可转债价值全能计算器移入 toolbox，公开 API 进入主线支持

### fixed

- 完成了可转债定价工具的全面基准测试，并完善了几个数据细节

## v0.8.11 - 2020.05.15

### fixed

- xirrrate 支持调整时间起点，并修改内部 bug
- 允许账单的 date 不出现在第一列
- 修复了 trade 不支持按周计价净值基金的 bug

## v0.8.10 - 2020.05.01

### added

- 增加场内账单分红派息合拆送股的处理，支持特定行跳过
- 为 trade.v_tradecost() 增加买卖点标记（类似蚂蚁财富显示效果）
- 场内交易类也支持 tradecost 和 totvalue 可视化
- 指标类增加 pct_chg 方法，可以比较每年度的涨幅
- 股票日线数据除默认的前复权外，增加了后复权和不复权数据
- get_bar 支持 wsj 数据源（不保证连续的官方支持）
- 增加 mul 类 trade 覆盖逻辑，可同时提供部分 trade obj 和账单了

### fixed

- 继续完善 QDII 原油展期实时估值处理逻辑
- 优化 mul 的扇形图和 trade 折线图的显示效果
- 修正 get_bar 中的错误

## v0.8.9 - 2020.04.26

### fixed

- 中证数据源 dataframe close 列保证是 float
- 增加了原油期货交割日带来的 QDII 实时预测困难解决

### added

- 增加国证指数数据源
- 增加易盛商品指数系列数据源
- 增加基金大类资产持仓比例，通过 xa.get_daily("pt-F100032") 调取
- 增加 default_end, 用户可选择改变默认的 end 行为（今天，通常可改为昨天）
- 增加 ycharts 数据源

## v0.8.8 - 2020.04.16

### added

- get_rt 新浪源，A 股标的增加买卖前 5 手数据，可通过添加选项 \_from="sina" 调用
- 增加根据持仓的基金历史估值分析，同时使 PEBHistory 可以 dispatch 到指数，申万行业，个股和基金估值系统
- 工具箱增加 TEBHistory 可以估算拟合指数的资产和利润增速并可视化
- get_daily 增加中证指数源
- 增加 Overpriced 类工具，可以观察基金历史折溢价情况并分析

### fixed

- 修复 get_peb 的分流
- 继续完善 QDII 净值预测的跨市场逻辑处理

## v0.8.7 - 2020.04.10

### added

- 增加了基金详细股票和债券持仓的信息，可以通过 `fundinfo.get_holdings(year, season)` 调用

### fixed

- 修复了基金信息爬取的大量 corner cases, 包括 .5 年的记法，定开和封闭基金赎回费率的特殊写法，已终止基金的赎回费率处理，净值为空基金的报错，js 页面有大量换行的正则兼容

## v0.8.6 - 2020.04.09

### added

- mulfix 增加 istatus 账单读入
- get_rt 针对基金扩充更多元数据

### fixed

- 修复雪球实时 HK 开始的可能 bug
- 今日交易记录的 trade bug

## v0.8.5 - 2020.04.08

### added

- get_bar 增加聚宽源
- get_daily 支持基金累计净值
- get_rt 返回增加时间属性
- 日线增加成交量数据（注意缓存兼容性）
- 直接将绘制 k 线图 hack 到 df 上，df.v_kline()
- 支持 dataframe web 级的显示，可用 set_display 开关
- 增加 StockPEBHistory 类可以查看个股估值历史
- 对 get_daily 增加 fetchonly 更精细的控制缓存

### fixed

- 进一步完善跨市场休市日不同时的净值预测逻辑

## v0.8.4 - 2020.04.06

### added

- 增加 vinfo 类，使得任何 get_daily 可以拿到的标的都可以进行交易。
- 增加主流市场节假日信息
- 为 get 函数增加 handler 选项，方便钩子函数嵌套
- 增加非 QDII 的溢价实时预测类 RTPredict

### changed

- xa.set_backend 也可影响 fundinfo 的缓存设定

### fixed

- 进一步完善缓存刷新掉最后一天和节假日的处理逻辑

## v0.8.3 - 2020.04.04

### added

- get_bar 增加雪球源
- 增加 set_handler
- 增加更多 FT 数据
- 增加 lru_cache_time，带 ttl 的缓存更好的防止重复爬取

### fixed

- 防止 precached 之前的日线数据无法抓取
- 为 imul 增加 istatus 关键字参数作为冗余防止误输入
- predict 对于跨市场休市更完善的考虑

## v0.8.2 - 2020.04.02

### added

- 增加聚宽宏观数据到 get_daily
- QDIIPredict 实时预测支持不同时间片混合涨幅计算
- 增加 get_bar
- 英为实时增加 app 源
- 增加日志系统，可以打印网络爬虫的详细信息

### fixed

- 增加 daily_increment 的过去选项，防止假期阻止严格检查。
- get_daily 同时兼容双向人民币中间价

## v0.8.1 - 2020.04.01

### added

- 日线增加英为 app 源备份
- 增加 QDII 预测的日期返回, 增加溢价率估计，增加 t1 计算状态
- `set_proxy()` 空时添加取消代理功能，和 socks5 代理支持
- `set_holdings()` 允许外部导入数据 py
- 增加标的对应 id 的缓存

### fixed

- 改进为实时的新浪港股 API，之前 API 存在 15 分延时
- read excel 和网络下载部分解耦，增加稳定性和模块化

## v0.8.0 - 2020.03.30

### added

- 添加 ft 日线数据源和实时数据
- 将净值预测的基础设施迁移重构进 xalpha，并封装成面向对象

### fixed

- 天天基金总量 API 中，累计净值里可能存在 null
- 港股新浪实时数据现价抓取错位

## v0.7.1 - 2020.03.29

### added

- 申万行业指数历史估值情况
- cachedio 缓存器增加周末校验，周末区间自动不爬取数据
- 为 Compare 增加 col 选项，支持 close 之外的列的比较
- `get_daily` 新增指数总利润和净资产查看，用于更准确的刻画宏观经济
- 增加雅虎财经日线数据获取

## v0.7.0 - 2020.03.27

### changed

- 将面向对象封装的工具箱从 universal 模块移到单独的 toolbox 模块。

### added

- 增加内存缓存作为 IO 缓存的双重缓存层，提高数据读写速度。
- `get_daily` 增加彭博的日线数据获取。
- `mul` 增加 istatus 选项，可以场内外账单同时统计。
- `get_rt` 增加新浪实时数据源，同时增加 double_check 选项确保实时数据稳定无误。

### fixed

- 完善聚宽云平台使用的导入。

## v0.6.2 - 2020.03.25

### added

- `set_backend` 增加 `precached` 预热选项，可以一次性缓存数据备用。
- 增加 `Compare` 类进行不同日线的比较。

## v0.6.1 - 2020.03.25

### added

- `get_daily` 增加聚宽数据源的场内基金每日份额数据
- `get_daily` 增加标普官网数据源的各种小众标普指数历史数据

## v0.6.0 - 2020.03.24

### added

- 增加了持久化的透明缓存装饰器，用于保存平时的数据 `cachedio`，同时支持 csv，数据库或内存缓存。
- 增加了数据源提供商抽象层，并加入 jqdata 支持。
- 提供了基于 jqdata 的指数历史估值系统，和估值总结类 `PEBHistory`。

## v0.5.0 - 2020.03.21

### added

- 增加了场内数据记账单和交易的分析处理
- 增加了查看基金报告的类 FundReport

### fixed

- 爬取人民币中间价增加 UA，因为不加还是偶尔会被反爬

## v0.4.0 - 2020.03.12

### fixed

- 雪球数据获取，设定 end 之后的问题造成起点偏移，已解决。

### added

- 全新的基金特性设定接口，包括四舍五入机制，按金额赎回记录，和分红默认行为切换，均可以通过记账单第一行或 mul 类传入 property 字典来设定，且完全向后兼容。

## v0.3.2 - 2020.03.11

### fixed

- 通过 get_daily 获取的基金和雪球数据日线，不包括 end 和 start 两天，已修正为包括。

### changed

- 增加 rget 和 rpost 容错，使得 universal 部分的下载更稳定。

## v0.3.1 - 2020.03.09

### added

- 增加了 `get_daily` 的缓存装饰器，可以轻松无缝的缓存所有日线数据，防止反复下载

## v0.3.0 - 2020.03.08

### added

- 重磅增加几乎万能的日线数据获取器 `get_daily`
- 增加几乎万能的实时数据获取器 `get_rt`

### fixed

- pandas 1.0+ 的 `pandas.Timestamp` API 要求更严，bs 的 NavigableString 不被接受，需要先用 `str` 转回 python str
- day gap when incremental update: if today's data is published, add logic to avoid this

### changed

- `fundinfo` 解析网页逻辑重构，直接按字符串解析，不再引入 js parser，更加简洁, 依赖更少。

## v0.2.0 - 2020.02.19

### fixed

- 调整到支持 pyecharts 1.0+ 的可视化 API，部分可视化效果有待进一步调整
- 调整 v_tradevolume 语句顺序，避免无卖出时可视化空白的问题
- 暂时限制 pandas 为 0.x 版本，1.x 版本暂时存在时间戳转化的不兼容问题待解决
- 基金增量更新调整，防止更新区间过长时，更新数据不全的问题
- 解决 list 格式账单一天单个基金多次购买的计算 bug
- 将工作日 csv 本地化，从而绕过 tushare PRO API 需要 token 的缺点（普通 API 尚未支持 2020 年交易日数据）

## v0.1.2 - 2019.05.29

### added

- 增加了 fundinfo 和 mfundinfo 的自动选择逻辑
- 增加了新格式交易单的读取接口
- 增加了统一的异常接口

### fixed

- 暂时固定 pyecharts 为老版本（将在下一次发布时修改为支持 pyecharts 1.0+）
- fundinfo 增量更新，指定为货币基金代码的时候，可以妥善地报异常

## v0.1.1 - 2018.12.29

### changed

- 更简洁的底层逻辑，用来处理多个基金日期不完全相同的情形

### fixed

- 对于基金类增量更新的 API 中注释栏的处理进行了完善

## v0.1.0 - 2018.08.20

### added

- record 类增加 save_csv 函数，将账单一键保存
- info 各个类增加了增量更新的逻辑，可以将数据本地化到 csv 文件，大幅提升了速度
- info 类的增量更新亦可选择任意 sqlalchemy 支持连接的数据库，将数据本地化

### fixed

- 进一步校正 trade 类 dailyreport 在未发生过交易时的展示逻辑

## v0.0.7 - 2018.08.17

### added

- indicator 模块增加了大量技术面指标的计算工具，并针对性的设计了新的可视化函数
- 增加了基于不同技术指标交叉或点位触发的交易策略

### fixed

- 将时间常量修改为函数
- 注意到 QDII 基金可能在美国节假日无净值，从而造成和国内基金净值天数不同的问题，修复了在 evaluate 模块这部分的处理逻辑
- 解决部分可视化函数字典参数传入不到位问题

## v0.0.6 - 2018.08.14

### added

- 新增真实的货币基金类 mfundinfo，与虚拟货币基金类 cashinfo 互为补充
- 新增了 realtime 模块，可以根据存储制定的策略，提供实时的投资建议，并自动发送邮件通知

### fixed

- info 类赎回逻辑的进一步完善，未来赎回则视为最后一个有记录的净值日赎回
- info 类故意屏蔽掉今天的净值，即使净值已更新，防止出现各种逻辑错误
- 完善 policy 的各个子类，使其对未来测试兼容

## v0.0.5 - 2018.08.12

### added

- mul 类增加返回 evaluate 对象的函数
- 增加了新的模块 evaluate 类，可以作为多净值系统的比较分析工具，现在提供净值可视化与相关系数分析的功能

### fixed

- 基金组合总收益率展示改为以百分之一为单位
- 交易类的成本曲线可视化改为自有交易记录开始
- 对于 fundinfo 的处理逻辑更加完善，进一步扩大了对各种情形处理的考量
- 完善 trade 类中各量计算时，早于基金成立日的处理逻辑

## v0.0.4 - 2018.08.09

### added

- policy 模块增加网格交易类，以进行波段网格交易的回测分析和指导
- 更直接的一键虚拟清仓功能添加到 record 类，并将具有 status 的类都视为有 record 的 MixIn
- v_tradevolume() 这一基于现金表的可视化函数，增加了 freq ＝ 的关键字参数，可选 D，W，M，从而直接展示不同时间为单位的交易总量柱形图

### changed

- 修改了基金收益率的计算逻辑，大幅重构了 dailyreport 的内容和计算，并引入了简单的换手率指标估算

### deprecated

- 鉴于 mul 类中 combsummary 函数展示数据的完整度很高，tot 函数不再推荐使用

## v0.0.3 - 2018.08.06

### added

- 增加基于现金流量表的成交量柱形图可视化
- 增加 mul 类的 combsummary 展示总结函数
- policy 增加了可以定期不定额投资的 scheduled_tune 类

### fixed

- 可视化函数绘图关键词传入的修正
- policy 类生成投资 status 时遍历所有时间而非只交易日
- 注意了 fundinfo 类中时间戳读取的时区问题，使得程序可以在不同系统时间得到正确结果

## v0.0.2 - 2018.08.03

### added

- 配置 setup.py，使得通过 pip 安装可以自动安装依赖，注意 ply 库采用了老版本 3.4，这是为了防止调用 slimit 库时不必要的报 warning
