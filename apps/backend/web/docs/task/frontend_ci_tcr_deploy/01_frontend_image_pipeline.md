# GitHub Actions 前端镜像构建与推送任务
- [x] 新增前端镜像 workflow，支持 `main` 推送和手动触发
- [x] 使用 TCR 自动化凭证登录镜像仓库
- [x] 复用当前前端 Dockerfile 和 lite 构建参数
- [x] 产出可追踪的镜像标签与 digest
- [x] 明确 workflow 失败时的排查口径

## 任务状态
- 类型：子任务文档
- 父任务：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/frontend_ci_tcr_deploy/requirement.md`
- 状态：已实现，待真实 TCR 环境验证
- 目标：把前端镜像构建从部署服务器搬到 GitHub Actions，但不顺手改变当前镜像运行语义

## 1. 问题定义
当前仓库还没有 `.github/workflows/` 下的前端发布流水线。

如果只说“以后用 GitHub Actions 构建”，但不明确构建入口、凭证和标签规则，最后很容易又退回到服务器本机构建。

另外，当前前端有一个不能忽略的事实：
- `build:lite` 会先跑 `vue-tsc --noEmit`
- 仓库里仍有 TypeScript 存量报错
- 当前 Dockerfile 的真实构建入口是 `vite build --mode lite`

所以这个任务必须先把 CI 行为和当前镜像行为对齐。

## 2. 完成定义
本任务完成后，必须同时满足下面几条：
- 仓库新增可执行的前端镜像 workflow
- workflow 能登录 TCR 并推送前端镜像
- workflow 使用当前前端 Dockerfile 构建镜像
- 镜像至少具备 `sha-提交号` 和稳定标签两类 tag
- workflow 日志里能看到镜像 digest，便于后续部署和回滚

## 3. 范围
本任务只覆盖下面这些内容：
- `.github/workflows/` 下的前端镜像 workflow
- workflow 所需的 secrets 命名和使用方式
- 前端镜像的 tag、触发条件和 build args

## 4. 非目标
本任务不做下面这些事情：
- 不直接从 workflow SSH 登录服务器发布
- 不迁移后端镜像构建
- 不修复前端全部 TypeScript 存量问题
- 不新增和现有 Dockerfile 不一致的第二套前端构建入口

## 5. 选定方案
采用 GitHub 官方推荐的 Docker workflow 组合：
1. `actions/checkout`
2. `docker/login-action`
3. `docker/metadata-action`
4. `docker/build-push-action`

构建口径：
- `context` 继续用仓库根目录
- `file` 指向 `docker/frontend/Dockerfile`
- `VITE_BUILD_MODE=lite`
- `VITE_SOURCEMAP=false`
- `NODE_OPTIONS=--max-old-space-size=1536`

标签规则：
1. `sha-<short_sha>` 作为精确回滚标签
2. `main` 作为主线最新标签
3. 如后续需要版本号标签，再单独扩展，不并入本任务

凭证规则：
- 优先使用 TCR 服务级账号
- GitHub secrets 至少包括 registry、username、password、image 名称
- 不在 workflow 里写死真实仓库地址和账号明文

## 6. 数据与凭证影响
- 不改业务数据
- 新增 GitHub 仓库 secrets
- 新增 TCR 命名空间和前端镜像仓库

建议 secrets 口径：
- `TCR_REGISTRY`
- `TCR_USERNAME`
- `TCR_PASSWORD`
- `TCR_FRONTEND_IMAGE`

## 7. 生命周期与失败处理
workflow 运行顺序：
1. 检出代码
2. 登录 TCR
3. 生成标签和 labels
4. 构建并推送镜像
5. 输出镜像 digest

失败处理边界：
- 登录失败先查 secrets 和 TCR 访问控制
- build 失败先按当前 Dockerfile 路径排查，不先改成 `build:lite`
- 推送失败先查仓库权限和命名空间授权

## 8. 验收标准
- 手动触发 workflow 能成功推送前端镜像
- 推送到 `main` 时 workflow 能自动运行
- TCR 中能看到 `sha-*` 和 `main` 标签
- 产出的镜像仍可用于现有 Nginx 前端容器

## 9. 验证要求
- 至少完成一次 `workflow_dispatch` 手动验证
- 记录一次成功推送后的镜像 tag 与 digest
- 确认镜像 tag 可以被服务器部署脚本引用

## 10. 风险点
- 如果 TCR 公网访问控制只接受固定出口 IP，普通 GitHub-hosted runner 可能被拦住
- 如果 workflow 和 Dockerfile 构建参数不一致，CI 成功不代表线上可用
- 如果直接切严格类型检查，构建会被现有前端存量问题阻塞

## 11. 后续动作
本任务完成后，如果还要继续增强 CI，另开任务处理：
1. 构建缓存优化
2. 镜像签名或制品证明
3. 多分支、多环境标签策略
