<div align="center">
  <img width="100" src="./public/logo.png" />
<h1 align="center">Snow View</h1>
  <p>这是 monorepo 里的前端工作区，当前位于 `apps/frontend/`，保留 Vue3 + Element Plus + TypeScript + Vite 的业务界面和工程配置。</p>
</div>

## 项目简介

Snow View 最初基于开源后台框架改造而来，当前只保留前端源码、构建配置和业务模块代码，独立仓库痕迹已经清理掉。业务模块仍然包括资产管理、分类管理、指数管理、网格分析、作业调度与日志、通知管理等（见 `src/views/Snow/` 目录）。

本项目强调简洁与必要性（KISS / YAGNI），现在按 monorepo 工作区方式维护，不再作为独立发布仓库使用。

## 技术栈与规范

- 框架：`Vue 3 (Composition API)`
- 构建：`Vite 3`
- 语言：`TypeScript`
- UI：`Element Plus 2.2.28`
- 路由：`Vue Router 4`
- 状态管理：`Pinia`
- 样式：`Less + WindiCSS`
- 图标：`@iconify/iconify`
- 国际化：`Vue I18n`
- 代码规范：`ESLint + Prettier + Stylelint`
- 提交规范：`Commitlint`

## 功能特性

- 业务模块：资产、分类、指数、网格、作业调度、通知等常用后台业务
- 权限体系：动态路由与菜单权限控制
- 国际化：内置中英文语言包
- 主题与样式：主题色配置、暗黑模式、全局 Less 变量、WindiCSS 原子化样式
- 组件库：二次封装常用组件（表单、表格、对话框、描述列表、图表等）
- 工程能力：按需加载、代码分割、Mock（可选）、静态资源优化

## 运行环境

- Node.js `>= 14.18.0`
- 推荐使用 `pnpm`

## 快速开始

先在仓库根目录执行一次 `pnpm install`，然后按你要对齐的后端口径启动前端。

```bash
# 安装依赖：在仓库根目录执行 `pnpm install`

# lite 主线：推荐默认口径
pnpm run dev
python -m web.lite_application

# 历史 dev 口径：只在需要兼容旧环境时使用
pnpm run dev:dev
# SNOW_APP_STATUS=dev python web/application.py

# 构建（产物在不同目录）
pnpm run build:lite  # dist-lite
pnpm run build:dev   # dist-dev
pnpm run build:test  # dist-test（如配置）
pnpm run build:pro   # dist-pro

# 预览构建产物（不带代理能力）
pnpm run serve:pro
```

## 环境与配置

项目使用多环境配置文件：`.env.base`、`.env.lite`、`.env.dev`、`.env.test`、`.env.pro`、`.env.gitee`。

- 通用配置（`.env.base`）：
  - `VITE_BASE_PATH`：打包基础路径，默认 `/`
  - `VITE_API_BASEPATH`：接口前缀键，默认 `base`
  - `VITE_APP_TITLE`：页面标题
- lite 口径（`.env.lite`）：
  - `VITE_RUNTIME_PROFILE=lite`
  - `VITE_PROXY_TARGET=http://127.0.0.1:5001`
  - `VITE_ENABLE_SCHEDULER=true`
  - `VITE_ENABLE_SYSTEM_TOKEN=true`
- 开发环境（`.env.dev`）：
  - `VITE_RUNTIME_PROFILE=dev`
  - `VITE_PROXY_TARGET=http://127.0.0.1:15000`
  - `VITE_OUT_DIR=dist-dev`
- 生产环境（`.env.pro`）：
  - 【已统一】`VITE_API_BASEPATH=dev`，与 Nginx 的 `/dev/` 代理保持一致
  - `VITE_OUT_DIR=dist-pro`
  - 关闭 `sourcemap`，移除 `debugger`

### 接口前缀与请求说明

Axios 基础路径来源于 `src/config/axios/service.ts`：

```ts
// 根据环境变量选择 base_url
export const PATH_URL = base_url[import.meta.env.VITE_API_BASEPATH]

// 开发环境（dev） => '/dev'，生产环境也统一为 '/dev'
const service = axios.create({ baseURL: PATH_URL, timeout: 60000 })
```

对应的 `src/config/axios/config.ts` 中的映射：

```ts
base_url: { base: '', dev: 'dev', pro: '', test: '' }
```

由于前端统一使用 `/dev` 作为代理前缀，所以真正的后端入口通过 `VITE_PROXY_TARGET` 决定。lite 默认对齐 `python -m web.lite_application` 的 `5001`，历史 dev 口径对齐 `DEV_FLASK_PORT` 默认 `15000`。

## 构建与部署

### 本地开发代理（Vite）

`vite.config.ts` 中通过 `VITE_PROXY_TARGET` 切换代理目标：

```ts
server: {
  port: 4000,
  proxy: {
    '/dev': {
      target: env.VITE_PROXY_TARGET || 'http://127.0.0.1:5001',
      changeOrigin: true,
      rewrite: path => path.replace(/^\/dev/, '')
    }
  }
}
```

## lite / dev 边界

- lite 前端会直接注入本地会话，只为绕开当前仓库缺失的 `/user/login`、`/role/list` 等 auth 接口，不代表后端已经补齐登录能力
- lite 下优先验证：系统设置、系统 token、资产列表、记录列表、指数列表、grid / grid-type 分析结果、通知列表、scheduler 任务列表
- lite 下默认把 scheduler 页面当成主链路；如果需要临时关闭后端 scheduler，可以显式设置 `LITE_ENABLE_SCHEDULER=false`
- lite 下默认开放系统 token 页面，后端持久化已切到 SQLite `system_settings`
- 如果要验证旧 dev 环境，再切 `pnpm run dev:dev`，不要把 lite 与 dev 混成一套口径

### 部署说明

当前 monorepo 根目录已经补了统一的 Docker 部署口径：

- 根目录 `docker-compose.yml`：启动前端静态站点和 lite 后端
- `docker/frontend/Dockerfile`：前端构建和 Nginx 运行镜像
- `docker/backend/Dockerfile`：lite 后端运行镜像

如果直接走容器部署，建议从仓库根目录执行：

```bash
docker compose up -d --build
```

如果前端镜像已经由 GitHub Actions 推到 TCR，服务器发布可以改成：

```bash
FRONTEND_IMAGE=example.tencentcloudcr.com/snowball/frontend:main \
scripts/deploy-lite-docker.sh
```

这个入口会优先拉取远端前端镜像，不在服务器本地重新执行前端 `vite build`。

默认对外端口：

- 前端：`8080`
- 后端：`5001`

## 目录结构

```
src/
├── api/              # API接口（按模块拆分）
├── components/       # 全局与二次封装组件
├── config/           # 全局配置（axios、app、locale）
├── hooks/            # 组合式函数
├── layout/           # 布局组件
├── locales/          # 国际化
├── router/           # 路由与权限
├── store/            # Pinia 状态管理
├── styles/           # 全局样式与主题变量
├── utils/            # 工具函数
└── views/            # 页面与业务模块
    └── Snow/         # 业务模块入口
        ├── Asset/            # 资产管理
        ├── Category/         # 分类管理
        ├── Index/            # 指数管理
        ├── Grid/             # 网格分析
        ├── Scheduler/        # 作业调度
        └── Notification/     # 通知管理
```

## 开发约定与最佳实践

- 遵循 KISS / YAGNI 原则，仅实现必要功能
- 组件使用 Composition API 与 TypeScript；明确 Props 类型
- 全局数据（枚举、字典）在 `App.vue` 的 `onMounted` 中异步加载，避免阻塞首屏
- 用户与权限相关数据在 `router.beforeEach` 中处理，确保动态路由正确
- Store 按模块拆分，统一使用 Actions 修改 State，必要时开启持久化
- 样式使用 Less + WindiCSS，组件样式使用 `scoped`
- 路由懒加载与代码分割，提升性能

## 常见问题

- 生产环境接口前缀为何是 `/dev`？
  - 这和后端当前路由口径保持一致，避免前端和后端地址再多出一套专用映射。
- 本地预览构建（`serve:pro`）接口报错？
  - `vite preview` 不带代理，请使用开发模式或接后端服务一起调试。
- 包管理器选择？
  - 这份工作区只走 `pnpm`。
- 为什么 lite 现在可以开放系统 token？
  - 当前 lite 后端虽然仍默认关闭 `ENABLE_REDIS`，但 `/system/token` 已经切到 SQLite `system_settings`，前端不需要再把这页当成 Redis 专属能力。

## 变更日志与许可证

- 变更日志：见 `CHANGELOG.md`
- 许可证：`MIT`（见 `LICENSE`）

---

如需扩展或定制，请在现有模块基础上遵循上述约定进行开发。欢迎提出建议与 Issue，共同完善项目。
