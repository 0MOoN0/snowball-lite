# 前端 GitHub Actions 构建并推送 TCR 部署需求
- [x] 明确前端从“服务器本机构建”切换到“GitHub Actions 构建镜像”的边界
- [x] 明确 TCR 仓库、访问凭证和镜像标签口径
- [x] 明确服务器侧改为拉取前端镜像而不是本机构建
- [x] 保持前端 Nginx 静态服务和 `/dev/` 反代后端链路不变
- [x] 保留可回滚的镜像版本与发布操作路径
- [x] 明确不纳入本需求的后端与严格类型检查收口边界

## 任务状态
- 类型：完整需求文档
- 状态：已实现，待 TCR 与服务器真实环境验收
- 交付方式：分阶段
- 当前阶段：两个 Task 已落地，下一步是联调与回滚演练
- 当前主任务：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/frontend_ci_tcr_deploy/02_server_pull_release.md`
- 最终目标：让前端镜像在 CI 预构建并推送到 TCR，服务器只负责拉取镜像和启动容器

## 0. 先说当前结论
当前真正增加服务器负担的不是前端运行容器，而是部署时在服务器直接执行前端 Docker build，并在镜像构建阶段跑 `vite build`。

现状里有三件事是绑在一起的：
1. 前端镜像由 `docker/frontend/Dockerfile` 在部署机本地构建
2. 部署脚本默认走 `docker compose up -d --build`
3. 前端容器内部 Nginx 还承担 `/dev/` 到 lite 后端的反代

这份需求的完成口径是：
- GitHub Actions 能构建当前 lite 前端镜像并推送到 TCR
- 服务器部署前端时不再执行本地前端 build
- 前端访问地址、Nginx 静态服务和 `/dev/` 反代行为保持不变
- 前端部署具备按镜像 tag 回滚的明确路径

## 1. 问题定义
当前根目录 compose 把 `frontend` 定义成 `build` 模式，部署脚本也默认会触发镜像重建。

这会带来三个直接问题：
1. 前端每次发布都要在服务器消耗 CPU、内存和磁盘 IO 跑一次 Vite 打包
2. 生产部署是否成功，和部署机当时的 Node/Docker 构建状态强绑定
3. 镜像版本没有天然和 Git 提交绑定，回滚粒度不够清晰

根因不是“前端必须放在服务器上”，而是当前把“构建”和“运行”都压在了同一台机器上。

## 2. 完成定义
这份需求完成后，必须同时满足下面几条：
- 仓库内有可执行的 GitHub Actions workflow，能构建前端镜像并推送到 TCR
- TCR 使用独立的自动化访问凭证，不继续依赖个人账号密码
- 前端镜像至少具备 `sha-提交号` 和稳定发布标签两类可用 tag
- 服务器部署前端时改成 `pull + up`，不再执行前端本地 build
- 前端首页和 `/dev/docs` 代理健康检查仍可通过
- 回滚时可以直接切换到上一个可用镜像 tag，而不是回退服务器源码后重新 build

## 3. 范围
本需求只覆盖下面这些内容：
- 前端镜像的 GitHub Actions 构建与推送流程
- TCR 命名空间、仓库和自动化访问凭证口径
- 服务器侧前端部署方式切换
- 对应的部署脚本、compose 入口和操作文档

## 4. 非目标
本需求不把下面这些事情算进完成条件：
- 不把后端镜像一并迁到 GitHub Actions
- 不把前端部署改成 COS/CDN 或纯静态托管
- 不重写前端运行方式，继续保留 Nginx 容器和 `/dev/` 反代
- 不在本需求里清理前端现有 TypeScript 存量报错
- 不在本需求里引入 Kubernetes、TKE 或完整灰度发布体系

## 5. 选定方案
采用“GitHub Actions 预构建前端镜像 + 推送 TCR + 服务器拉取镜像部署”的方案。

关键决策：
1. 构建入口继续复用现有 `docker/frontend/Dockerfile`
2. 构建参数继续保持 lite 口径，避免把运行环境一并改掉
3. CI 先按 Dockerfile 当前行为执行 `vite build --mode lite`
4. 服务器只切前端服务到 `image` 模式，后端保持现有部署方式

这里要明确一个边界：
- 当前 `pnpm --dir apps/frontend run build:lite` 会先跑 `vue-tsc --noEmit`，仓库里还有存量报错
- 但 Dockerfile 当前实际执行的是 `pnpm --dir apps/frontend exec vite build --mode lite`
- 所以本需求要先把 CI 构建语义和现网镜像语义对齐，不能在迁移时顺手升级成更严格的构建门禁

## 6. 数据与存储影响
- 不涉及业务库 schema 变更
- 不涉及 lite SQLite 运行数据迁移
- 新增的持久化对象是 TCR 前端镜像仓库
- 服务器本地只保留 Docker 镜像缓存，不再承担前端源码构建产物生成职责

凭证归属边界：
- GitHub 侧保存 TCR 登录所需 secrets
- TCR 侧使用服务级账号或等效自动化凭证
- 服务器只需要拉取镜像的访问能力，不需要前端源码构建环境

## 7. API 与交互影响
- 用户访问前端入口仍是现有站点地址
- 前端容器仍通过 Nginx 提供静态资源
- `/dev/` 到后端 `5001` 的代理链路保持不变
- 前后端接口前缀、Vite `lite` 构建模式和运行页面行为不因本需求改变

这里要明确：
- 这次迁移改变的是“镜像从哪儿构建、怎么发布”
- 不是“接口怎么走”或“页面如何访问”

## 8. 生命周期与迁移处理
本需求按下面顺序切换：
1. 先补齐 TCR 仓库和 GitHub Actions workflow，让 CI 能独立产出前端镜像
2. 再让服务器增加镜像拉取部署入口，与现有本机构建入口并存一个短暂过渡期
3. 验证新入口稳定后，前端默认部署路径切到 pull 模式

迁移原则：
- 过渡期允许保留旧入口，但旧入口不再作为默认发布路径
- 最终验收时，前端默认发布不能再依赖服务器本地 build
- 后端命名卷、日志目录和 SQLite 数据文件不因本需求搬迁

## 9. 分阶段计划
- Task 1：GitHub Actions 前端镜像构建与推送
  `/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/frontend_ci_tcr_deploy/01_frontend_image_pipeline.md`
- Task 2：服务器侧前端拉取部署与回滚入口
  `/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/frontend_ci_tcr_deploy/02_server_pull_release.md`

顺序要求：
1. 先完成 Task 1，确认 TCR 中能稳定产出可运行镜像
2. 再完成 Task 2，把服务器部署默认路径切到镜像拉取模式

## 10. 验收标准
- GitHub Actions 能在 `main` 更新或手动触发时成功构建并推送前端镜像
- TCR 中能看到按提交生成的前端镜像 tag
- 服务器部署前端时不再执行本地 `vite build`
- 前端首页可访问，`/dev/docs` 代理后端仍正常
- 回滚到上一版前端镜像时不需要重新在服务器构建源码

## 11. 风险点
- 如果 TCR 访问控制要求固定公网出口，普通 GitHub-hosted runner 可能不适合作为最终推送入口
- 如果把服务器本机构建入口继续保留成默认路径，需求不能算真正完成
- 如果 CI 构建时偷偷切到 `build:lite`，会被现有 TypeScript 存量问题阻塞

## 12. 后续边界
下面这些问题需要另开任务，不能混进本需求验收：
1. 后端镜像也迁到 GitHub Actions
2. 前端严格类型检查和构建门禁清零
3. 基于 TCR Webhook 或 SSH 的自动发布闭环
4. 更细的灰度发布、环境分层和多版本保活
