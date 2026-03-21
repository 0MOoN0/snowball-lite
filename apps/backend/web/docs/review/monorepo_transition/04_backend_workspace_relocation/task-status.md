# Task 04 后端应用工作区物理迁移 状态

- 原任务文档：`/Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition/04_backend_app_workspace_relocation_design.md`
- 所属 requirement：`/Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition`
- 当前状态：已完成
- 当前轮次：round-01
- 当前结论：真实后端代码已迁到 `apps/backend/web/`；根目录 `web` 保留为兼容符号链接；`apps/backend/xalpha` 保留对根目录 `xalpha/` 的兼容入口；后端 README、Docker、docker-compose 和环境变量文档已切到 `apps/backend` 工作区口径；Task 04 定向测试、backend path 回归、Gunicorn 配置检查和 monorepo 定向回归已通过；round-01 正式评审无 finding

## 当前影响面

- `/Users/leon/projects/snowball-lite/apps/backend/`
- `/Users/leon/projects/snowball-lite/web`
- `/Users/leon/projects/snowball-lite/README.md`
- `/Users/leon/projects/snowball-lite/Dockerfile`
- `/Users/leon/projects/snowball-lite/docker-compose.yml`
- `/Users/leon/projects/snowball-lite/.gitignore`
- `/Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task04.py`
- `/Users/leon/projects/snowball-lite/web/docs/环境变量配置指南.md`
- `/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/04_backend_workspace_relocation/`

## 已知验收点

- 后端代码物理位置已进入 `apps/backend/web`
- 根目录 `web` 仍可作为兼容入口访问 `docs`、`webtest` 和模块导入
- 从 `apps/backend` 进入后端工作区可以直接启动 lite/dev 入口
- `xalpha/` 仍保持根目录原位
- lite 启动、bootstrap、迁移路径和 Gunicorn 配置仍可用

## 已执行命令

- `rm /Users/leon/projects/snowball-lite/apps/backend/web && mv /Users/leon/projects/snowball-lite/web /Users/leon/projects/snowball-lite/apps/backend/web && ln -s apps/backend/web /Users/leon/projects/snowball-lite/web`
- `test -e /Users/leon/projects/snowball-lite/apps/backend/xalpha || ln -s ../../xalpha /Users/leon/projects/snowball-lite/apps/backend/xalpha`
- `pytest /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task04.py -q`
- `cd /Users/leon/projects/snowball-lite/apps/backend && pytest web/webtest/lite/test_backend_workspace_paths.py -q`
- `cd /Users/leon/projects/snowball-lite/apps/backend && export LITE_DB_PATH=/Users/leon/projects/snowball-lite/.tmp/task04_lite.db && export LITE_XALPHA_CACHE_DIR=/Users/leon/projects/snowball-lite/.tmp/task04_xalpha && python -m gunicorn.app.wsgiapp --check-config -c web/gunicorn_lite.config.py web.lite_application:app`
- `pytest /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task03.py /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task04.py /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task05.py -q`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/validate_review_report.py --report /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/04_backend_workspace_relocation/round-01-review.md`

## 当前 blocker

- 无

## 下一步

1. Task 04 已收口，等待和 requirement 总状态一起提交或继续后续非 monorepo 任务

## Review 结果

- 评审报告：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/04_backend_workspace_relocation/round-01-review.md`
- 评审结论：无 finding
- 校验结果：`[OK] Report passed validation: /Users/leon/projects/snowball-lite/apps/backend/web/docs/review/monorepo_transition/04_backend_workspace_relocation/round-01-review.md`
