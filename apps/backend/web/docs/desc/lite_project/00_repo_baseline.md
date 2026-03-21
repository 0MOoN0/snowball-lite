# Snowball Lite 仓库基线

## 当前定位

`snowball-lite` 是从原始 `snowball` 仓库拆出的轻量版项目基线，目标是继续沿着 SQLite、本地运行和弱依赖方向推进。

## 基线来源

- 来源仓库：`/Users/leon/projects/snowball`
- 来源分支：`codex/lite-spike`
- 来源提交：`8d803c37fd1d689aca862348814b34addc892967`
- 建基时间：`2026-03-19`

## 这次基线包含什么

- 阶段一已完成的 lite 启动骨架
- SQLite 最小可用链路
- `xalpha` / DataBox 第一阶段兼容处理
- 阶段一验收文档
- 阶段二归档文档
- 阶段三归档文档与实现结果

## 当前状态

- 阶段一已完成
- 阶段二已完成
- 阶段三已完成并归档
- 当前还不能说“整个仓库已经完成 SQLite 迁移”

## 阶段三当前结论

- 已补齐 stage3 专用 SQLite 测试夹具
- 已验证两条更业务化的 SQLite 集成链路
- 已新增 `migrations_snowball_lite`
- 已清理阶段三范围内会直接挡路的 MySQL 专有 SQL
- 当前建议继续推进，但只建议做“受控扩圈”，不建议宣称全仓库 SQLite 已完成

## 当前文档结构

- 阶段二归档文档：`web/docs/desc/lite_stage2/`
- 阶段三归档文档：`web/docs/desc/lite_stage3/`

## 当前 Git 约定

- 默认分支：`main`
- 基线版本：`0.1.0`
- 建议分支：`feature/*`、`fix/*`、`codex/*`
- 基线标签：`v0.1.0`

## 当前不做的事

- 不继续复用原仓库的 `master/dev` 分支语义
- 不把原仓库历史版本号直接平移到 lite 项目
- 不承诺现阶段已经具备完整生产能力

## 下一步建议

1. 继续把更多高价值、低外部依赖的旧测试逐步接到 lite 的 SQLite fixtures。
2. 扩展 `migrations_snowball_lite`，但不要把阶段三结果误读成“全仓库已经迁完”。
3. 按运行路径继续清理剩余 MySQL 专有逻辑，再决定是否进入更大范围改造。
