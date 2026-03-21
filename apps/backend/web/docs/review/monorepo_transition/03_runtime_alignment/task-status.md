# Task 03 前端与当前后端运行口径对齐 状态

- 原任务文档：`/Users/leon/projects/snowball-lite/web/docs/desc/monorepo_transition/03_frontend_backend_runtime_alignment_design.md`
- 所属 requirement：`/Users/leon/projects/snowball-lite/web/docs/desc/monorepo_transition`
- 当前状态：已完成
- 当前轮次：round-01
- 当前结论：已完成 lite/dev 运行口径拆分、lite 本地会话引导和 scheduler/token 显式降级文案；通过 Vite 代理实测打通了 `/system/settings/` 与 `/api/asset/list/`；round-01 正式评审无 finding，但 `build:lite` 仍被前端存量 TypeScript 错误阻塞

## 当前影响面

- `/Users/leon/projects/snowball-lite/apps/frontend/`
- `/Users/leon/projects/snowball-lite/README.md`
- `/Users/leon/projects/snowball-lite/tests/`
- `/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/03_runtime_alignment/`

## 已知验收点

- `apps/frontend` 可以在主仓里本地启动
- 前端能稳定请求当前后端
- 至少一组核心页面完成联调
- 已知不兼容点有文档记录
- lite / dev 运行说明能让别人照着起

## 已执行命令

- `sed -n '100,180p' /Users/leon/projects/snowball-lite/apps/frontend/vite.config.ts`
- `sed -n '1,220p' /Users/leon/projects/snowball-lite/apps/frontend/src/config/axios/config.ts`
- `rg -n "15000|5001|5002|LITE_FLASK_PORT|/dev|/system/token|ENABLE_" /Users/leon/projects/snowball-lite/README.md /Users/leon/projects/snowball-lite/web /Users/leon/projects/snowball-lite/tests`
- `sed -n '1,220p' /Users/leon/projects/snowball-lite/apps/frontend/.env.dev`
- `sed -n '1,220p' /Users/leon/projects/snowball-lite/apps/frontend/.env.pro`
- `sed -n '1,240p' /Users/leon/projects/snowball-lite/apps/frontend/README.md`
- `sed -n '1,220p' /Users/leon/projects/snowball-lite/apps/frontend/src/router/index.ts`
- `sed -n '1,220p' /Users/leon/projects/snowball-lite/apps/frontend/src/store/modules/app.ts`
- `python -m py_compile /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task03.py`
- `pytest /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task03.py -q`
- `test -d /Users/leon/projects/snowball-lite/apps/frontend/node_modules && echo NODE_MODULES_OK || echo NODE_MODULES_MISSING`
- `pnpm --dir /Users/leon/projects/snowball-lite/apps/frontend exec vite --version`
- `pnpm --dir /Users/leon/projects/snowball-lite/apps/frontend exec node -p "require('./package.json').scripts['dev:lite']"`
- `export LITE_DB_PATH=/Users/leon/projects/snowball-lite/.tmp/task03_lite.db && export LITE_XALPHA_CACHE_DIR=/Users/leon/projects/snowball-lite/.tmp/task03_xalpha && export LITE_FLASK_PORT=5001 && python -m web.lite_application`
- `pnpm --dir /Users/leon/projects/snowball-lite/apps/frontend run dev:lite --host 127.0.0.1 --port 4000`
- `curl -sS -D - http://127.0.0.1:4000/dev/system/settings/ -o /tmp/task03_system_settings.json`
- `curl -sS -D - 'http://127.0.0.1:4000/dev/api/asset/list/?page=1&pageSize=20' -o /tmp/task03_asset_list_paged.json`
- `curl -sS http://127.0.0.1:4000/`
- `pnpm --dir /Users/leon/projects/snowball-lite/apps/frontend run build:lite`
- `git add /Users/leon/projects/snowball-lite/README.md /Users/leon/projects/snowball-lite/apps/frontend/.env.lite /Users/leon/projects/snowball-lite/apps/frontend/.env.dev /Users/leon/projects/snowball-lite/apps/frontend/README.md /Users/leon/projects/snowball-lite/apps/frontend/package.json /Users/leon/projects/snowball-lite/apps/frontend/src/config/runtimeProfile.ts /Users/leon/projects/snowball-lite/apps/frontend/src/config/runtimeSession.ts /Users/leon/projects/snowball-lite/apps/frontend/src/main.ts /Users/leon/projects/snowball-lite/apps/frontend/src/views/Snow/Setting/Scheduler/Scheduler.vue /Users/leon/projects/snowball-lite/apps/frontend/src/views/Snow/Setting/Data/DataSetting.vue /Users/leon/projects/snowball-lite/apps/frontend/vite.config.ts /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task03.py /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/03_runtime_alignment/task-status.md`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/capture_staged_snapshot.py --output-dir /private/tmp/codex-staged-review-task03`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/create_review_report.py --snapshot /private/tmp/codex-staged-review-task03/snapshot.json --output /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/03_runtime_alignment/round-01-review.md`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/validate_review_report.py --report /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/03_runtime_alignment/round-01-review.md`
- `git reset HEAD`

## 当前 blocker

- `pnpm --dir /Users/leon/projects/snowball-lite/apps/frontend run build:lite` 失败，原因是前端已有多处存量 TypeScript 错误，主要分布在通知、指数、grid、setting 和 mock 目录，不是这次 Task 03 新引入的问题
- 如果下一轮要把“前端构建通过”也收进验收，需要单独拆前端 TS 存量清理任务

## 下一步

1. 进入 Task 05，建立根目录 `docs/` 并收口长期文档入口
2. 如需把“前端构建通过”也纳入 monorepo 改造验收，单独拆前端 TS 存量清理任务

## Review 结果

- 评审报告：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/03_runtime_alignment/round-01-review.md`
- 评审结论：无 finding
- 校验结果：`[OK] Report passed validation: /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/03_runtime_alignment/round-01-review.md`
