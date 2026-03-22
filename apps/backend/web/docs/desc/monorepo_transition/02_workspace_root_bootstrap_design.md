# Task 02：根工作区与 apps/frontend 建立（归档）

## 任务状态

- 状态：已完成
- 优先级：高
- 前置：Task 01 已完成
- 目标：把前端正式放进 monorepo 工作区
- 最终落点：前端当前已经位于 `apps/frontend/`

## 归档结论

- 仓库根目录已经建立 `pnpm-workspace.yaml`
- 前端已经从 `snow_view/` 迁入 `apps/frontend/`
- 根目录 `.gitignore` 和 README 已补齐 workspace 口径
- 这一步收口后，前端不再以嵌套独立仓库方式存在
- 该任务的正式状态和评审结论见：
  - `web/docs/review/monorepo_transition/02_workspace_root_bootstrap/task-status.md`
  - `web/docs/review/monorepo_transition/02_workspace_root_bootstrap/round-02-review.md`

## 1. 原始目标

这一步要完成的是：

- 建立仓库根工作区
- 把前端从 `snow_view/` 收到 `apps/frontend`
- 让前端成为主仓正式子项目，而不是临时拷贝目录

## 2. 原始目标结构

```text
/
  apps/
    frontend/
  web/
  xalpha/
  tests/
  docs/   # 可先只建空目录，详细收口交给 Task 05
```

## 3. 原始范围

### 3.1 要处理的内容

- 新建 `apps/`
- 将 `snow_view/` 移动到 `apps/frontend/`
- 根目录新增 `pnpm-workspace.yaml`
- 统一根目录 `.gitignore` 对前端产物的处理
- 约定前端工作区的安装与运行命令

### 3.2 建议新增

- `pnpm-workspace.yaml`
- 根目录前端开发说明
- `apps/frontend/README.md` 或对现有 README 做工作区化改写

## 4. 非目标

- 这一步不改后端目录位置
- 这一步不改 `xalpha`
- 这一步不处理前端接口是否已经完全可用
- 这一步不建立 `apps/backend`

## 5. 关键改造点

### 5.1 工作区边界清晰

完成后应该能一眼看出：

- `apps/frontend` 是前端
- 根目录当前仍承载后端和 `xalpha`

### 5.2 根配置只放“仓库级”内容

根工作区新增的配置，只处理：

- workspace 包发现
- 统一忽略规则
- 顶层开发入口

不要在这一步把前端内部 ESLint / Vite / TS 配置都拉到根目录。

## 6. 原始验收标准

- `snow_view/` 已不存在
- 前端已位于 `apps/frontend/`
- 根目录 workspace 配置可识别前端包
- 根目录忽略规则能覆盖前端依赖和构建产物
- 前端依赖安装命令可以从 monorepo 口径执行

## 7. 初始风险点

- 如果这一步顺手动后端，会把问题面扩大
- 如果把前端内部配置过度上提到根目录，后续前端升级会变难
