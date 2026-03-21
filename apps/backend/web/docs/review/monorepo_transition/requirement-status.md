# monorepo_transition 需求状态

- 需求入口：`/Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition`
- 总览文档：`/Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition/00_overview.md`
- 当前状态：已完成
- 当前轮次：requirement-round-01
- 当前结论：Task 01 到 Task 05 已全部完成实现与正式评审；前端已进入 `apps/frontend/`，后端真实代码已进入 `apps/backend/web/`，根目录 `web` 保留为兼容符号链接；monorepo_transition requirement 已按当前设计文档收口

## 已确认范围

- 本轮 requirement 包含 `monorepo_transition` 目录下 Task 01 到 Task 05
- 本轮明确不动：`xalpha/`、`extends/`
- 当前前端入口是 `/Users/leon/projects/snowball-lite/apps/frontend`
- 当前 review 根目录：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition`

## 当前任务状态

| Task | 文档 | 状态 | 备注 |
| --- | --- | --- | --- |
| Task 01 | `01_frontend_source_intake_design.md` | 已完成 | `snow_view/` 已收成 workspace 口径，定向验证与正式评审均通过 |
| Task 02 | `02_workspace_root_bootstrap_design.md` | 已完成 | 前端已搬到 `apps/frontend/`，workspace 和根入口已建立 |
| Task 03 | `03_frontend_backend_runtime_alignment_design.md` | 已完成 | lite/dev 口径已拆分，最小读链路联调通过，正式评审通过 |
| Task 04 | `04_backend_app_workspace_relocation_design.md` | 已完成 | 真实后端代码已迁到 `apps/backend/web/`，根目录 `web` 保留兼容入口，正式评审通过 |
| Task 05 | `05_documentation_root_bootstrap_design.md` | 已完成 | 根 docs 入口、长期文档落点与 README 边界说明已建立，并通过正式评审 |

## 当前影响面

- `/Users/leon/projects/snowball-lite/apps/frontend/`
- `/Users/leon/projects/snowball-lite/apps/backend/`
- `/Users/leon/projects/snowball-lite/web`
- `/Users/leon/projects/snowball-lite/pnpm-workspace.yaml`
- `/Users/leon/projects/snowball-lite/pnpm-lock.yaml`
- `/Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py`
- `/Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task03.py`
- `/Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task04.py`
- `/Users/leon/projects/snowball-lite/README.md`
- `/Users/leon/projects/snowball-lite/Dockerfile`
- `/Users/leon/projects/snowball-lite/docker-compose.yml`
- `/Users/leon/projects/snowball-lite/docs/`
- `/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/`

## 已执行命令

- `sed -n '1,420p' /Users/leon/.codex/skills/team-work/SKILL.md`
- `sed -n '1,260p' /Users/leon/projects/snowball-lite/AGENTS.md`
- `sed -n '1,260p' /Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition/00_overview.md`
- `sed -n '1,260p' /Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition/01_frontend_source_intake_design.md`
- `sed -n '1,260p' /Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition/02_workspace_root_bootstrap_design.md`
- `sed -n '1,260p' /Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition/03_frontend_backend_runtime_alignment_design.md`
- `sed -n '1,260p' /Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition/04_backend_app_workspace_relocation_design.md`
- `sed -n '1,260p' /Users/leon/projects/snowball-lite/web/docs/task/monorepo_transition/05_documentation_root_bootstrap_design.md`
- `git status --short`
- `ls -la /Users/leon/projects/snowball-lite`
- `find /Users/leon/projects/snowball-lite/snow_view -maxdepth 2 \\( -name '.git' -o -name '.github' -o -name '.husky' -o -name 'node_modules' -o -name 'dist-dev' -o -name 'dist-pro' -o -name '.vscode' -o -name '.cursor' -o -name '.trae' \\) | sort`
- `find /Users/leon/projects/snowball-lite -maxdepth 2 \\( -name 'pnpm-workspace.yaml' -o -name 'pnpm-lock.yaml' -o -name 'package.json' -o -name 'docs' \\) | sort`
- `sed -n '1,220p' /Users/leon/projects/snowball-lite/snow_view/package.json`
- `sed -n '1,220p' /Users/leon/projects/snowball-lite/.gitignore`
- `sed -n '1,220p' /Users/leon/projects/snowball-lite/web/docs/review/backend_workspace_consolidation_design/task-status.md`
- `sed -n '1,220p' /Users/leon/projects/snowball-lite/web/docs/review/backend_workspace_consolidation_design/round-01-review.md`
- `python -m py_compile /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py`
- `python -m json.tool /Users/leon/projects/snowball-lite/apps/frontend/package.json > /dev/null`
- `pytest /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py -q`
- `git status --short`
- `pnpm --dir /Users/leon/projects/snowball-lite/apps/frontend exec node -p "require('./package.json').name"`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/capture_staged_snapshot.py --output-dir /private/tmp/codex-staged-review-1774015663`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/create_review_report.py --snapshot /private/tmp/codex-staged-review-1774015663/snapshot.json --output /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/02_workspace_root_bootstrap/round-01-review.md`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/validate_review_report.py --report /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/02_workspace_root_bootstrap/round-01-review.md`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/create_review_report.py --snapshot /private/tmp/codex-staged-review-1774015663/snapshot.json --output /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/02_workspace_root_bootstrap/round-02-review.md`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/validate_review_report.py --report /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/02_workspace_root_bootstrap/round-02-review.md`
- `git reset HEAD`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/capture_staged_snapshot.py --output-dir /private/tmp/codex-staged-review-1774015254`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/create_review_report.py --snapshot /private/tmp/codex-staged-review-1774015254/snapshot.json --output /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/round-01-review.md`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/validate_review_report.py --report /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/round-01-review.md`
- `git reset HEAD -- /Users/leon/projects/snowball-lite/snow_view/package.json /Users/leon/projects/snowball-lite/snow_view/README.md /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/task-status.md`
- `python -m py_compile /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task03.py`
- `pytest /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task03.py -q`
- `export LITE_DB_PATH=/Users/leon/projects/snowball-lite/.tmp/task03_lite.db && export LITE_XALPHA_CACHE_DIR=/Users/leon/projects/snowball-lite/.tmp/task03_xalpha && export LITE_FLASK_PORT=5001 && python -m web.lite_application`
- `pnpm --dir /Users/leon/projects/snowball-lite/apps/frontend run dev:lite --host 127.0.0.1 --port 4000`
- `curl -sS -D - http://127.0.0.1:4000/dev/system/settings/ -o /tmp/task03_system_settings.json`
- `curl -sS -D - 'http://127.0.0.1:4000/dev/api/asset/list/?page=1&pageSize=20' -o /tmp/task03_asset_list_paged.json`
- `pnpm --dir /Users/leon/projects/snowball-lite/apps/frontend run build:lite`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/validate_review_report.py --report /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/03_runtime_alignment/round-01-review.md`
- `git reset HEAD`
- `pytest /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task05.py -q`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/validate_review_report.py --report /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/05_docs_bootstrap/round-02-review.md`
- `rm /Users/leon/projects/snowball-lite/apps/backend/web && mv /Users/leon/projects/snowball-lite/web /Users/leon/projects/snowball-lite/apps/backend/web && ln -s apps/backend/web /Users/leon/projects/snowball-lite/web`
- `test -e /Users/leon/projects/snowball-lite/apps/backend/xalpha || ln -s ../../xalpha /Users/leon/projects/snowball-lite/apps/backend/xalpha`
- `pytest /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task04.py -q`
- `cd /Users/leon/projects/snowball-lite/apps/backend && pytest web/webtest/lite/test_backend_workspace_paths.py -q`
- `cd /Users/leon/projects/snowball-lite/apps/backend && export LITE_DB_PATH=/Users/leon/projects/snowball-lite/.tmp/task04_lite.db && export LITE_XALPHA_CACHE_DIR=/Users/leon/projects/snowball-lite/.tmp/task04_xalpha && python -m gunicorn.app.wsgiapp --check-config -c web/gunicorn_lite.config.py web.lite_application:app`
- `pytest /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task03.py /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task04.py /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task05.py -q`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/validate_review_report.py --report /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/04_backend_workspace_relocation/round-01-review.md`

## 当前 blocker

- 无 requirement 内 blocker
- 残余风险：如果后续把“前端构建通过”也纳入 monorepo_transition 的硬验收，需要单独处理前端已有的 TypeScript 存量错误；这不是本轮 Task 01 到 Task 05 新引入的问题

## 下一步

1. requirement 已完成，后续如需提交可作为 monorepo_transition 完整阶段提交
2. 如果要继续扩验收范围，可单独拆前端 TypeScript 存量清理任务

## 已完成评审

- Task 01 评审报告：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/round-01-review.md`
- Task 01 评审结论：无 finding，`validate_review_report.py` 已通过
- Task 02 评审报告：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/02_workspace_root_bootstrap/round-02-review.md`
- Task 02 评审结论：无 finding，`validate_review_report.py` 已通过
- Task 03 评审报告：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/03_runtime_alignment/round-01-review.md`
- Task 03 评审结论：无 finding，`validate_review_report.py` 已通过
- Task 05 评审报告：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/05_docs_bootstrap/round-02-review.md`
- Task 05 评审结论：无 finding，`validate_review_report.py` 已通过
- Task 04 评审报告：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/04_backend_workspace_relocation/round-01-review.md`
- Task 04 评审结论：无 finding，`validate_review_report.py` 已通过
