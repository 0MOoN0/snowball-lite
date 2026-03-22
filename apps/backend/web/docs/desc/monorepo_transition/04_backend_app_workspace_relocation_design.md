# Task 04：后端应用工作区物理迁移（归档）

## 任务状态

- 状态：已完成
- 优先级：中
- 前置：
  - Task 03 已完成
  - `web/docs/desc/lite_migration/project/03_backend_workspace_consolidation.md` 已完成
- 目标：把当前后端从“根目录承载”迁成 `apps/backend`

## 归档结论

- 真实后端代码已经迁到 `apps/backend/web/`
- 根目录 `web` 已保留为兼容符号链接，现有 `from web...` 导入不需要整体改名
- `apps/backend` 口径下的启动、Gunicorn 配置检查、路径回归和定向 pytest 已通过
- `apps/backend/xalpha` 继续兼容根目录 `xalpha/`
- 该任务的正式状态和评审结论见：
  - `web/docs/review/monorepo_transition/04_backend_workspace_relocation/task-status.md`
  - `web/docs/review/monorepo_transition/04_backend_workspace_relocation/round-01-review.md`

## 1. 原始目标

这一步才处理后端的物理位置变化：

- 后端入口进入 `apps/backend`
- 根目录不再同时承担“仓库根”和“后端工作区根”两个角色

## 2. 原始目标结构

```text
/
  apps/
    backend/
    frontend/
  docs/
  xalpha/
  tests/
```

其中 `apps/backend/` 里建议至少包含：

- `web/`
- 后端运行说明
- 必要的后端工作区入口文件

## 3. 初始前提

后端第一阶段目录收口已经完成，当前已具备：

- `web/migrations/`
- `web/scripts/`
- `web/dev_support/`
- `web/webtest/lite/`
- 统一 backend path 工具

这意味着本任务不再是“边收口边迁目录”，而是“在已收口的基线上做物理迁移”。

## 4. 原始范围

### 4.1 要处理的内容

- `web/` 进入 `apps/backend/`
- 后端运行入口路径调整
- README 和开发命令调整
- Python 路径和导入方式验证
- 与根目录 `xalpha/` 的兼容验证

### 4.2 暂不处理

- `xalpha/` 不迁
- `extends/` 不迁
- 不做 Python 多包发布重构

## 5. 关键改造点

### 5.1 根目录与后端工作区解耦

完成后应该满足：

- 根目录负责 monorepo 协调
- `apps/backend` 才是后端运行区

### 5.2 保持 `xalpha` 临时独立

本轮里后端迁移后，仍然允许：

- `apps/backend/web` 依赖根目录 `xalpha/`

但要把这种依赖关系写清楚，不要假装已经完成 package 化。

## 6. 原始验收标准

- 后端代码已位于 `apps/backend`
- 后端主入口可运行
- lite 启动、bootstrap、迁移脚本、关键测试可继续通过
- 前端联调命令不因后端搬家而失效
- `xalpha/` 保持原位且不需要跟着迁

## 7. 初始风险点

- 这是整轮改造里对 Python 路径最敏感的一步
- 如果在 Task 03 之前做，很难分清是“目录问题”还是“联调问题”
