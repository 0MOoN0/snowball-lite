# Task 01 前端源码收编与仓清洗 状态

- 原任务文档：`/Users/leon/projects/snowball-lite/web/docs/desc/monorepo_transition/01_frontend_source_intake_design.md`
- 所属 requirement：`/Users/leon/projects/snowball-lite/web/docs/desc/monorepo_transition`
- 当前状态：已完成
- 当前轮次：round-01
- 当前结论：`snow_view/` 已收成前端工作区口径，独立仓库目录、构建垃圾、旧 Docker/nginx/husky/CI 痕迹已清理，`package.json` 已切到 workspace 口径；round-01 正式评审无 finding

## 当前影响面

- `/Users/leon/projects/snowball-lite/snow_view/`
- `/Users/leon/projects/snowball-lite/.gitignore`（如需补主仓忽略规则）
- `/Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py`
- `/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/`

## 已知验收点

- `snow_view/` 下不再包含 `.git`
- `snow_view/` 下不再包含 `node_modules` 和 `dist-*`
- `snow_view/` 下不再包含独立仓库级 CI / husky 目录
- 前端源码与构建配置继续保留
- `snow_view/package.json` 调整为适合主仓工作区使用

## 已执行命令

- `find /Users/leon/projects/snowball-lite/snow_view -maxdepth 2 \\( -name '.git' -o -name '.github' -o -name '.husky' -o -name 'node_modules' -o -name 'dist-dev' -o -name 'dist-pro' -o -name '.vscode' -o -name '.cursor' -o -name '.trae' \\) | sort`
- `find /Users/leon/projects/snowball-lite/snow_view -maxdepth 1 -mindepth 1 | sort`
- `find /Users/leon/projects/snowball-lite/snow_view -maxdepth 1 -type f \\( -name '.env*' -o -name 'README*' -o -name '.gitignore' \\) | sort`
- `sed -n '1,220p' /Users/leon/projects/snowball-lite/snow_view/package.json`
- `python -m py_compile /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py`
- `python -m json.tool /Users/leon/projects/snowball-lite/snow_view/package.json > /dev/null`
- `pytest /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py -q`
- `git status --short`
- `git add /Users/leon/projects/snowball-lite/snow_view/package.json /Users/leon/projects/snowball-lite/snow_view/README.md /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/task-status.md`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/capture_staged_snapshot.py --output-dir /private/tmp/codex-staged-review-1774015254`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/create_review_report.py --snapshot /private/tmp/codex-staged-review-1774015254/snapshot.json --output /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/round-01-review.md`
- `python3 -m json.tool /Users/leon/projects/snowball-lite/snow_view/package.json > /dev/null`
- `pytest /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py -q`
- `python3 /Users/leon/.codex/skills/staged-code-review-tdd/scripts/validate_review_report.py --report /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/round-01-review.md`
- `git reset HEAD -- /Users/leon/projects/snowball-lite/snow_view/package.json /Users/leon/projects/snowball-lite/snow_view/README.md /Users/leon/projects/snowball-lite/tests/test_monorepo_transition_task01.py /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/task-status.md`

## 当前 blocker

- 无

## 下一步

1. 启动 Task 02，把前端从 `snow_view/` 正式收进 `apps/frontend/`
2. Task 02 时同步处理目录名硬编码测试和 README 中与 `snow_view` 绑定的结构说明

## Review 结果

- 评审报告：`/Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/round-01-review.md`
- 评审结论：无 finding
- 校验结果：`[OK] Report passed validation: /Users/leon/projects/snowball-lite/web/docs/review/monorepo_transition/01_frontend_source_intake/round-01-review.md`
