# Task 05：根目录 docs 建立与长期文档收口（归档）

## 任务状态

- 状态：已完成
- 优先级：中
- 前置：Task 02 已完成，建议在 Task 03 之后执行
- 目标：建立根目录 `docs/`，让 monorepo 有统一文档入口

## 归档结论

- 根目录 `docs/` 总入口和分区目录已经建立
- `README.md` 已明确长期文档、执行文档和 `xalpha` legacy 文档的边界
- 活跃任务文档继续放在 `web/docs/task/`，本组 `monorepo_transition` 设计文档已经在 requirement 收口后归档到 `web/docs/desc/monorepo_transition`
- 该任务的正式状态和评审结论见：
  - `web/docs/review/monorepo_transition/05_docs_bootstrap/task-status.md`
  - `web/docs/review/monorepo_transition/05_docs_bootstrap/round-02-review.md`

## 1. 原始目标

这一步要解决的是：

- 仓库级长期文档统一有落点
- 前端、后端、`xalpha` 的文档入口关系明确

## 2. 初始现状

当前文档分布是：

- 后端主文档在 `web/docs/`
- `xalpha` 旧文档在 `doc/`
- 目前没有 monorepo 的总文档根

## 3. 原始目标结构

```text
/docs
  /architecture
  /backend
  /frontend
  /xalpha
  /adr
  /ops
```

## 4. 原始范围

### 4.1 要处理的内容

- 新建根目录 `docs/`
- 建立总入口文档
- 迁移长期稳定文档
- 更新 `README.md` 文档入口

### 4.2 暂时保留原位的内容

- `web/docs/task/` 中的活跃任务文档
- `web/docs/review/`
- `doc/`

原因是这些要么属于执行文档，要么属于 `xalpha` 旧 Sphinx 文档区；本组 requirement 文档在任务完成后单独归档到 `web/docs/desc/monorepo_transition`。

## 5. 非目标

- 不重写 `doc/` 的 Sphinx 体系
- 不一次性迁走所有 `web/docs/`
- 不把 task / review 文档强行提到根目录

## 6. 关键改造点

### 6.1 文档分层要清楚

- `docs/`：仓库长期说明
- `web/docs/task` / `web/docs/review`：活跃执行文档
- `doc/`：`xalpha` legacy docs
- `web/docs/desc/monorepo_transition`：本 requirement 已完成归档

### 6.2 前端文档要预留，不必一步写满

当前即使前端文档内容不多，也应该先留出：

- `docs/frontend/`

避免后续继续把前端文档散写在别处。

## 7. 原始验收标准

- 根目录存在 `docs/`
- `README.md` 已能指向根目录文档入口
- 后续新增长期文档有明确落点
- `web/docs/task` 和 `web/docs/review` 继续可用
- `doc/` 被明确标注成 `xalpha` 旧文档区

## 8. 初始风险点

- 如果太早迁 task / review，执行流会被打断
- 如果直接把所有文档塞进 `doc/`，新旧体系会继续混在一起
