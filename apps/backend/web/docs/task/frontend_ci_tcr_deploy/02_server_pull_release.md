# 服务器侧前端拉取部署与回滚入口任务
- [x] 给服务器补一个前端 `image` 模式部署入口
- [x] 保持本地开发 compose 和服务器发布入口解耦
- [x] 部署脚本改成 `pull + up`，不再默认 `--build`
- [x] 保留首页和 `/dev/docs` 健康检查
- [x] 明确前端镜像 tag 回滚路径

## 任务状态
- 类型：子任务文档
- 父任务：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/frontend_ci_tcr_deploy/requirement.md`
- 依赖：`/Users/leon/projects/snowball-lite/apps/backend/web/docs/task/frontend_ci_tcr_deploy/01_frontend_image_pipeline.md`
- 状态：已实现，待服务器真实环境验证
- 目标：让服务器默认只拉取前端镜像并启动容器，不再承担前端源码构建职责

## 1. 问题定义
当前根目录 `docker-compose.yml` 里的 `frontend` 还是 `build` 模式，部署脚本默认也会跑 `docker compose up -d --build`。

如果 workflow 已经能把前端镜像推到 TCR，但服务器发布入口还保留成默认本机构建，那前面的迁移就只完成了一半。

## 2. 完成定义
本任务完成后，必须同时满足下面几条：
- 服务器有单独的前端镜像部署入口
- 这个入口默认从 TCR 拉取前端镜像，不再构建前端源码
- 本地开发入口仍可继续使用现有 compose 构建方式
- 前端部署后首页和 `/dev/docs` 健康检查仍可通过
- 回滚时可以指定上一个前端镜像 tag 重新部署

## 3. 范围
本任务只覆盖下面这些内容：
- 服务器专用 compose 入口或 override 文件
- 前端部署脚本和镜像 tag 传参方式
- 服务器登录 TCR、拉取镜像和健康检查说明

## 4. 非目标
本任务不做下面这些事情：
- 不重写后端部署方式
- 不改前端容器内 Nginx 配置语义
- 不删除本地开发用的 compose build 能力
- 不做自动 SSH 发布闭环

## 5. 选定方案
采用“保留现有本地 compose，额外增加服务器专用 overlay”的方案。

推荐落地方式：
1. 根目录现有 `docker-compose.yml` 保持本地开发/手工构建口径
2. 服务器新增一个 overlay 文件，把 `frontend` 从 `build` 改成 `image`
3. 部署脚本在服务器使用 `docker compose -f docker-compose.yml -f docker-compose.server.yml`

前端镜像规则：
- 镜像地址来自环境变量或脚本参数
- 默认可用 `main` 标签
- 回滚时允许显式传入某个 `sha-*` 标签

部署顺序：
1. 登录 TCR
2. 拉取目标前端镜像
3. 仅更新 `frontend` 服务
4. 运行首页和代理健康检查

## 6. 数据与运行影响
- 后端命名卷 `backend_runtime` 和 `backend_logs` 保持不变
- lite SQLite 数据文件不搬迁
- 前端运行端口仍保持现有对外口径
- 服务器减少的是前端构建负担，不是前端运行负担

## 7. 生命周期与回滚处理
切换步骤：
1. 先保留旧入口，补齐新入口
2. 用新入口完成一次真实部署
3. 验证稳定后，把新入口作为默认发布方式

回滚规则：
- 回滚时不回退服务器源码
- 直接指定上一版 `sha-*` 镜像 tag 重新 `pull + up`
- 回滚完成后仍按同一套健康检查判断是否成功

## 8. 验收标准
- 服务器默认发布前端时不再执行本地前端 build
- 前端首页可访问
- `/dev/docs` 到后端的代理链路正常
- 指定历史镜像 tag 时能完成前端回滚
- 本地开发 compose 行为不被这次改动破坏

## 9. 验证要求
- 至少完成一次从 TCR 拉取 `main` 或 `sha-*` 标签的真实部署
- 部署后验证 `http://127.0.0.1:8080`
- 部署后验证 `http://127.0.0.1:8080/dev/docs`
- 至少演练一次回滚命令或回滚脚本参数

## 10. 风险点
- 如果服务器不能稳定访问 TCR，新入口会卡在登录或拉取阶段
- 如果把服务器入口直接改死为远端镜像而不保留过渡期，排障会变窄
- 如果健康检查只测首页，不测 `/dev/` 代理，前端可能看起来正常但实际不可用

## 11. 后续动作
本任务完成后，如果还要继续做发布自动化，另开任务处理：
1. GitHub Actions 自动 SSH 发布
2. TCR Webhook 触发服务器更新
3. 多环境前端镜像发布策略
