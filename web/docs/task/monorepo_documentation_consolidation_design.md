# monorepo 文档收口任务设计

## 任务状态

- 状态：待开始
- 优先级：中
- 目标阶段：目录收口和 monorepo 预留任务
- 当前产物：任务设计文档

## 1. 一句话结论

- 长期看，仓库文档应该统一到根目录。
- 但不应该直接统一到当前的 `doc/`。
- 更合理的目标是：新增根目录 `docs/` 作为 monorepo 总文档根，后端、前端、`xalpha` 分区收口；现有 `web/docs/` 和 `doc/` 先按职责分流，再逐步迁移。

## 2. 当前现状

### 2.1 现在其实有两套文档体系

1. `web/docs/`
   - 当前仓库最活跃的业务、技术、阶段、任务、评审文档都在这里
   - 典型内容：
     - `web/docs/task/`
     - `web/docs/review/`
     - `web/docs/desc/`
     - `web/docs/环境变量配置指南.md`
     - `web/docs/系统说明.md`
     - `web/docs/轻量版分支改造方案.md`

2. `doc/`
   - 明显是旧 `xalpha` 的 Sphinx 文档体系
   - 典型内容：
     - `doc/source/index.rst`
     - `doc/source/quickstart.rst`
     - `doc/source/demo.rst`
     - `doc/source/xalpha.rst`
     - `doc/samples/`

### 2.2 当前引用关系

- `README.md` 现在大量引用 `web/docs/`
- `doc/source/index.rst` 仍然是 `xalpha` 的文档入口
- 当前没有一个“仓库总入口文档目录”
- 这意味着：
  - 后端文档在 `web/docs/`
  - `xalpha` 文档在 `doc/`
  - 仓库级文档入口缺位

### 2.3 现状带来的问题

- 文档分散，后续再加前端会更乱。
- `web/docs/` 名字上像“后端内部文档”，但实际上已经承载了项目级信息。
- `doc/` 名字太泛，但内容其实偏 `xalpha`，不适合作为整个 monorepo 的总文档根。
- 如果以后把前端迁进来，没有统一文档根，前后端规范、架构、运维、接入说明会继续分叉。

## 3. 任务目标

- 为未来 monorepo 建立统一的仓库文档根。
- 把“仓库级长期文档”和“组件级执行文档”分开。
- 保留 `xalpha` 现有文档边界，不强行把它并进 `web/docs/`。
- 给后端、前端、`xalpha` 三类文档建立统一收口规则。
- 让 README 和后续新文档有稳定落点。

## 4. 非目标

- 不在本任务里一次性迁完所有历史文档。
- 不在本任务里重写 `doc/` 的 Sphinx 体系。
- 不在本任务里把所有 `web/docs/task/`、`web/docs/review/` 全部挪走。
- 不要求当前就引入前端文档。
- 不要求当前就把所有文档站点统一生成。

## 5. 设计原则

### 5.1 仓库文档根和组件文档目录分层

- 根目录 `docs/` 负责长期、跨组件、面向协作的文档。
- 组件内文档目录负责执行中的任务、评审、临时阶段资料。

### 5.2 不直接拿 `doc/` 当总文档根

原因有三个：

1. `doc/` 当前内容明显偏 `xalpha`
2. `doc/` 是 `rst + Sphinx` 体系，和当前主流 `Markdown` 文档风格不同
3. 如果硬把后端和前端文档也塞进去，只会把旧体系和新体系混在一起

### 5.3 先建立新入口，再逐步迁移

- 先建立根目录 `docs/`
- 再逐步迁长期文档
- 最后再决定 `doc/` 是否整体迁成 `docs/xalpha/`，还是继续保留为 `legacy` 文档构建目录

### 5.4 执行文档继续就近放

短期内这些内容不建议直接迁到根目录：

- `web/docs/task/`
- `web/docs/review/`

原因：

- 它们和具体代码迭代强绑定
- 路径稳定、现有流程已跑通
- 大量任务状态和评审文档已经按 `web/docs/review/` 收口

## 6. 选定方案

采用“新建根目录 `docs/` + 分阶段迁移”的方案。

### 6.1 目标结构

建议长期结构：

```text
/docs
  /architecture
  /backend
  /frontend
  /xalpha
  /adr
  /ops
```

各目录职责：

- `docs/architecture/`
  - 系统边界
  - 模块关系
  - monorepo 目录约定

- `docs/backend/`
  - 后端长期说明
  - 运行、配置、数据库、接口规范

- `docs/frontend/`
  - 前端架构、接入、构建、发布
  - 当前可先空置

- `docs/xalpha/`
  - `xalpha` 面向仓库协作的说明
  - 不要求立刻替代 `doc/`

- `docs/adr/`
  - 架构决策记录

- `docs/ops/`
  - 部署、运维、环境、值守说明

### 6.2 保留区

短期内继续保留：

- `web/docs/task/`
- `web/docs/review/`
- `doc/`

它们分别承担：

- `web/docs/task/`：执行前设计
- `web/docs/review/`：执行过程和评审产物
- `doc/`：旧 `xalpha` Sphinx 文档

## 7. 第一阶段迁移建议

### 7.1 优先迁移到根目录 `docs/` 的文档

这些文档属于“长期说明”，适合先迁：

- `web/docs/系统说明.md`
- `web/docs/环境变量配置指南.md`
- `web/docs/技术总结.md`
- `web/docs/轻量版分支改造方案.md`
- `web/docs/desc/lite_project/00_repo_baseline.md`
- `web/docs/desc/lite_project/01_lite_vs_mysql_component_matrix.md`

建议落点：

- `docs/backend/`
- `docs/architecture/`

### 7.2 暂时保留在 `web/docs/` 的文档

- `web/docs/task/`
- `web/docs/review/`
- 阶段性归档 `web/docs/desc/lite_stage*/`

原因：

- 它们和当前后端任务流、review 流绑定较深
- 短期直接迁移会带来大量路径修正
- 这些文档更接近“执行档案”，不是“仓库说明书”

### 7.3 `doc/` 的处理方式

`doc/` 先定义为：

- `xalpha` 旧文档区
- 或 `legacy xalpha docs`

短期建议：

- 不挪
- 不混入后端和前端文档
- 只在根目录 `docs/` 建一个指向说明，说明 `xalpha` 历史文档当前仍位于 `doc/`

## 8. 推荐实施顺序

1. 新建根目录 `docs/`
2. 新建根目录文档索引
3. 在 `docs/` 下建立 `architecture/`、`backend/`、`frontend/`、`xalpha/`、`adr/`、`ops/`
4. 先迁长期稳定文档，不动 task/review
5. 更新 `README.md` 的主要文档入口
6. 给 `doc/` 明确补一条“当前是 xalpha legacy docs”的说明
7. 等前端进仓后，再补 `docs/frontend/`
8. 最后再评估是否把 `doc/` 迁到 `docs/xalpha/`

## 9. 风险点

### 9.1 最大风险是“一把梭迁文档”

如果一次性把 `web/docs/` 和 `doc/` 全搬走：

- README 链接会大量失效
- 任务、评审、阶段归档路径会全部变化
- 当前协作流程会被打断

### 9.2 直接把所有文档塞进 `doc/`

这会带来几个问题：

- `xalpha` 文档和后端文档混在一起
- `rst/Sphinx` 和 `Markdown` 风格混杂
- 路径名失去语义，后续继续扩会更难维护

### 9.3 根目录 `docs/` 过早承接执行文档

如果把 task/review 也直接统一到根目录：

- 路径会很长
- 执行文档和项目说明文档会混放
- 日常开发改动噪音会变大

## 10. 验收标准

完成后至少满足这些条件：

- 仓库存在统一的根目录文档入口 `docs/`
- `README.md` 能清楚区分仓库级文档入口、后端执行文档入口、`xalpha` 旧文档入口
- 新增长期文档默认不再放到 `web/docs/` 或 `doc/` 的模糊位置
- `web/docs/task/` 和 `web/docs/review/` 继续可用，不被本次迁移打断
- `doc/` 的角色被明确成 `xalpha` 旧文档区，而不是仓库总文档根
- 为未来前端接入预留 `docs/frontend/`

## 11. 本任务完成标准

- 建立文档收口口径
- 明确 `docs/`、`web/docs/`、`doc/` 三者分工
- 给出第一阶段迁移顺序
- 后续新增文档能按新规则落点
