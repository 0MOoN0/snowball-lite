# Task 01：前端源码收编与仓清洗（归档）

## 任务状态

- 状态：已完成
- 优先级：高
- 目标：把当前 `snow_view/` 从“完整独立仓库副本”收成“可纳入主仓的前端源码工作区”
- 最终落点：该任务的产物已经在 Task 02 中并入 `apps/frontend/`

## 归档结论

- `snow_view/` 中的 `.git`、`.github`、`.husky`、`.vscode`、`.cursor`、`.trae`、`node_modules`、`dist-dev`、`dist-pro` 等独立仓库残留已清理
- 前端包配置已经切到适合 monorepo workspace 的口径
- 这一步只负责“收干净再迁”，实际目录迁移由 Task 02 完成
- 该任务的正式状态和评审结论见：
  - `web/docs/review/monorepo_transition/01_frontend_source_intake/task-status.md`
  - `web/docs/review/monorepo_transition/01_frontend_source_intake/round-01-review.md`

## 1. 原始目标

这一步只解决一件事：

- 让 `snow_view/` 变成干净、可迁移、可进入 monorepo 的前端源码目录

## 2. 初始问题

当前 `snow_view/` 里还带着独立仓库痕迹，包括但不限于：

- `.git`
- `.github`
- `.husky`
- `node_modules`
- `dist-dev`
- `dist-pro`
- 独立的 nginx / Docker / CI 配置

这些内容如果不先清掉，后续进入主仓后会出现：

- nested git 仓库
- 重复 CI 和发布入口
- 大量无效构建产物进工作区
- 前端仓和主仓边界混乱

## 3. 原始范围

### 3.1 要处理的内容

- 清理 `snow_view/` 下的仓库级目录
- 清理依赖和构建产物目录
- 统一前端包管理口径
- 明确哪些配置要迁到主仓级，哪些保留在前端工作区

### 3.2 建议保留

- `src/`
- `public/`
- `types/`
- `docs/`
- `mock/`
- `package.json`
- `pnpm-lock.yaml`
- `vite.config.ts`
- `tsconfig.json`
- ESLint / Prettier / Stylelint / WindiCSS 相关配置

### 3.3 建议清理

- `.git`
- `.github`
- `.husky`
- `.vscode`
- `.cursor`
- `.trae`
- `node_modules`
- `dist-dev`
- `dist-pro`

## 4. 非目标

- 这一步不改前端接口逻辑
- 这一步不改前端页面
- 这一步不把目录直接搬到 `apps/frontend`
- 这一步不处理前后端联调

## 5. 关键改造点

### 5.1 包管理口径统一

建议统一用 `pnpm`，并把前端工作区改成：

- `private: true`

避免把 monorepo 里的前端工作区继续当成可独立发布包。

### 5.2 环境文件保留策略

`.env.*` 要区分：

- 示例配置
- 含真实环境信息的本地配置

如果含敏感值，优先转成：

- `.env.example`
- `.env.local` 风格忽略文件

## 6. 原始验收标准

- `snow_view/` 下不再包含 `.git`
- 不再包含 `node_modules` 和 `dist-*`
- 不再包含独立仓库级 CI / husky 目录
- 前端源码和构建配置完整保留
- `package.json` 已调整为适合主仓工作区使用

## 7. 初始风险点

- 如果直接带着 `.git` 进入主仓，后续所有 git 行为都会混乱
- 如果保留 `node_modules` 和 `dist-*`，工作区会被构建垃圾淹没
- 如果不先统一包管理口径，后续 workspace 很容易出现 lockfile 冲突
