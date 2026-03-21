# Task 05：根目录 docs 建立与长期文档收口

## 任务状态

- 状态：待开始
- 优先级：中
- 前置：Task 02 已完成，建议在 Task 03 之后执行
- 目标：建立根目录 `docs/`，让 monorepo 有统一文档入口

## 1. 任务目标

这一步要解决的是：

- 仓库级长期文档统一有落点
- 前端、后端、`xalpha` 的文档入口关系明确

## 2. 当前现状

当前文档分布是：

- 后端主文档在 `web/docs/`
- `xalpha` 旧文档在 `doc/`
- 目前没有 monorepo 的总文档根

## 3. 推荐目标结构

```text
/docs
  /architecture
  /backend
  /frontend
  /xalpha
  /adr
  /ops
```

## 4. 任务范围

### 4.1 要处理的内容

- 新建根目录 `docs/`
- 建立总入口文档
- 迁移长期稳定文档
- 更新 `README.md` 文档入口

### 4.2 暂时保留原位的内容

- `web/docs/task/`
- `web/docs/review/`
- `doc/`

原因是这些要么属于执行文档，要么属于 `xalpha` 旧 Sphinx 文档区。

## 5. 非目标

- 不重写 `doc/` 的 Sphinx 体系
- 不一次性迁走所有 `web/docs/`
- 不把 task / review 文档强行提到根目录

## 6. 关键改造点

### 6.1 文档分层要清楚

- `docs/`：仓库长期说明
- `web/docs/task` / `web/docs/review`：后端执行文档
- `doc/`：`xalpha` legacy docs

### 6.2 前端文档要预留，不必一步写满

当前即使前端文档内容不多，也应该先留出：

- `docs/frontend/`

避免后续继续把前端文档散写在别处。

## 7. 验收标准

- 根目录存在 `docs/`
- `README.md` 已能指向根目录文档入口
- 后续新增长期文档有明确落点
- `web/docs/task` 和 `web/docs/review` 继续可用
- `doc/` 被明确标注成 `xalpha` 旧文档区

## 8. 风险点

- 如果太早迁 task / review，执行流会被打断
- 如果直接把所有文档塞进 `doc/`，新旧体系会继续混在一起
