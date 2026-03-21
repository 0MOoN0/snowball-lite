# 移除根目录 web 兼容入口总览（归档）

## 当前状态

- 状态：已完成
- 类型：requirement
- 归档位置：`apps/backend/web/docs/desc/monorepo_transition/06_remove_root_web_compat_entry/`
- 目标：移除仓库根目录 `web` 兼容符号链接，统一后端真实路径口径到 `apps/backend/web`
- 当前事实：仓库根目录 `web` 兼容符号链接已移除

## 一句话结论

这组 requirement 已按 `4` 个任务完成：

1. 运行与导入解耦
2. 活跃路径与工具链迁移
3. 测试与验收口径更新
4. 删除根目录 `web` 兼容入口并做最终清扫

## 为什么要拆成 requirement

根目录 `web` 现在同时承担了三层职责：

1. 文件系统兼容路径
   - `web/docs`
   - `web/migrations`
   - `web/scripts`
   - `web/data`

2. Python 包与启动入口
   - `python -m web.application`
   - `python -m web.lite_application`
   - `web.application:app`
   - `import web`

3. 文档与测试里的兼容事实
   - README、环境说明、VS Code 启动项、compose
   - monorepo 阶段测试和阶段归档

这三层如果一起改，很容易出现：

- 删掉符号链接后，命令还没迁完
- 测试还在断言 `REPO_ROOT / "web"` 必须存在
- 文档还在把 `web` 当作稳定事实

所以必须拆任务，先解耦，再迁移，再改验收，最后删除。

## 当前现状

已经确认的事实：

- `apps/backend/web` 是后端真实目录
- 仓库根目录 `web` 兼容符号链接已删除
- 当前活跃运行命令、工具配置、文档和测试已切到 `apps/backend` / `apps/backend/web`
- 当前 monorepo 验收口径不再把根目录 `web` 当成基线事实

## 任务拆分

### Task 01：运行与导入解耦

目标：

- 让仓库在不依赖根目录 `web` 符号链接的前提下，仍然可以正常导入 `web` 包并执行现有启动入口

边界：

- 不改包名 `web`
- 只解决导入链路和运行入口，不做大规模文档替换

### Task 02：活跃路径与工具链迁移

目标：

- 把 README、compose、launch、活跃脚本中的根目录 `web/...` 路径迁到真实后端路径口径

边界：

- 只动仍在使用中的入口与工具
- 不顺手重写历史归档文档

### Task 03：测试与验收口径更新

目标：

- 把当前仍然把“根目录 `web` 必须存在”写成验收事实的测试和阶段口径改掉

边界：

- 只改当前仍被执行或仍作为基线使用的测试与说明
- 不删除 task/review 体系本身

### Task 04：删除根目录 `web` 兼容入口并做最终清扫

目标：

- 前面三步都完成后，删除仓库根目录 `web` 符号链接
- 做最后一轮 grep、定向测试和归档

边界：

- 这一步才允许真正删除 `web`
- 如果前面任务未完成，不应提前执行

## 推荐顺序

必须按下面顺序推进：

1. Task 01
2. Task 02
3. Task 03
4. Task 04

其中：

- Task 01 是阻塞任务
- Task 02 和 Task 03 可以在 Task 01 完成后交错推进
- Task 04 必须最后执行

## done_when

这组 requirement 完成时，至少要满足：

- 仓库根目录不再保留 `web` 符号链接
- 日常运行和测试不再依赖根目录 `web/...` 兼容路径
- Python 代码仍可以继续使用现有包名 `web`
- README、工具配置、阶段测试和基线文档不再把根目录 `web` 当成当前事实

## 非目标

- 不在这组任务里把 Python 包名 `web` 改成别的名字
- 不在这组任务里把 `apps/backend/web/docs` 一次性迁到根目录 `docs`
- 不在这组任务里重做前后端 workspace 结构
