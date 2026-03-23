# Staged Code Review Report

- Generated At: `2026-03-23T09:36:25+08:00`
- Reviewer: `Codex`
- Repo Root: `/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence`
- HEAD: `286812e6ec01310f2df3ec265888f5088ceef5c4`
- Snapshot Source: `/private/tmp/codex-staged-review-1774229718/snapshot.json`

## Scope

- Staged file count: `6`
- Added lines: `341`
- Removed lines: `72`
- Diff artifact: `/private/tmp/codex-staged-review-1774229718/staged_diff.patch`

### Staged Files

- `apps/frontend/src/api/snow/Scheduler/index.ts`
- `apps/frontend/src/api/snow/Scheduler/job/types.ts`
- `apps/frontend/src/api/snow/Scheduler/types.ts`
- `apps/frontend/src/views/Snow/Setting/Scheduler/JobDetailDialog.vue`
- `apps/frontend/src/views/Snow/Setting/Scheduler/JobPolicyDialog.vue`
- `apps/frontend/src/views/Snow/Setting/Scheduler/Scheduler.vue`

## Review Protocol (TDD + Evidence)

1. Write a failing test before claiming any business-logic defect.
2. Treat business and production code as read-only during review unless the user explicitly requests a fix.
3. Keep review test edits inside repository `test/` paths and write them to commit-ready repository quality.
4. Run targeted commands and record exact outputs.
5. Keep each finding mapped to a test case and file scope.
6. Attach evidence snippets that can be reproduced by another engineer.
7. If no findings exist, provide regression command evidence anyway.

## Fix Verification

- Previous Findings Source: none, this is the first review round for Task 5
- Verification Scope: staged diff only
- Verification Commands: `git diff --cached --check`; `git diff --cached --stat`; `sed -n '1,240p' /Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/task/scheduler_execution_persistence/05_frontend_settings.md`; `sed -n '1,220p' /Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_persistence_policy_routers.py`
- Result: no prior findings to verify
- Notes: the staged frontend changes match the task doc and the backend persistence-policy contract, and the staged patch itself is clean under `git diff --cached --check`

## New Risk Scan

- Scan Scope: current staged diff only
- Risk Focus Areas: policy columns, read-only policy dialog gating, save-and-refresh flow, API typing shape, task detail view simplification
- Commands: `git diff --cached -- apps/frontend/src/api/snow/Scheduler/index.ts apps/frontend/src/api/snow/Scheduler/job/types.ts apps/frontend/src/api/snow/Scheduler/types.ts apps/frontend/src/views/Snow/Setting/Scheduler/JobDetailDialog.vue apps/frontend/src/views/Snow/Setting/Scheduler/JobPolicyDialog.vue apps/frontend/src/views/Snow/Setting/Scheduler/Scheduler.vue`; `rg -n "persistence-policies|supportedPolicies|effectivePolicy|defaultPolicy|policySource|updateJobPersistencePolicy|SchedulerPersistencePolicy" /Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence`
- Result: no new findings
- New Findings: none
- Residual Risk: this review was source-level only; no browser E2E or frontend typecheck was run in this session, so Vue runtime/compiler issues still need a separate regression pass when dependencies are available

## Findings Summary

| ID | Severity | File:Line | Finding | Risk | Test Before Fix | Evidence Command | Recommendation | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| None | none | - | No critical, high, medium, or low findings in the staged diff | - | - | `git diff --cached --check` | Keep the new scheduler settings UI and API typings in the repo as regression coverage | Closed |

## No Findings Evidence (Use only when there are no findings)

- Command Set: `git diff --cached --check`; `git diff --cached --stat`; `git diff --cached -- apps/frontend/src/api/snow/Scheduler/index.ts apps/frontend/src/api/snow/Scheduler/job/types.ts apps/frontend/src/api/snow/Scheduler/types.ts apps/frontend/src/views/Snow/Setting/Scheduler/JobDetailDialog.vue apps/frontend/src/views/Snow/Setting/Scheduler/JobPolicyDialog.vue apps/frontend/src/views/Snow/Setting/Scheduler/Scheduler.vue`; `sed -n '1,240p' /Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/task/scheduler_execution_persistence/05_frontend_settings.md`; `sed -n '1,220p' /Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_persistence_policy_routers.py`
- Evidence: the staged diff adds 6 frontend files with policy columns, a dedicated policy dialog, a read-only detail dialog, and an update API call; the backend contract already exposes `defaultPolicy`, `effectivePolicy`, `policySource`, `supportedPolicies`, and `PUT /scheduler/persistence-policies`, so the frontend wiring stays aligned
- Residual Risk: no browser-level interaction or frontend typecheck was executed in this session, so that runtime layer should still be covered once dependencies are installed

## Evidence Appendix

```text
$ git diff --cached --check

$ git diff --cached --stat
 apps/frontend/src/api/snow/Scheduler/index.ts      |  20 ++-
 apps/frontend/src/api/snow/Scheduler/job/types.ts  |  35 ++--
 apps/frontend/src/api/snow/Scheduler/types.ts      |  19 +++
 .../Snow/Setting/Scheduler/JobDetailDialog.vue     |  57 ++-----
 .../Snow/Setting/Scheduler/JobPolicyDialog.vue     | 178 +++++++++++++++++++++
 .../src/views/Snow/Setting/Scheduler/Scheduler.vue | 104 ++++++++++--
 6 files changed, 341 insertions(+), 72 deletions(-)

$ rg -n "persistence-policies|supportedPolicies|effectivePolicy|defaultPolicy|policySource|updateJobPersistencePolicy|SchedulerPersistencePolicy" /Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_persistence_policy_routers.py:17:    url_prefix="/scheduler/persistence-policies",
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_persistence_policy_routers.py:22:class SchedulerPersistencePolicyListRouter(Resource):
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_persistence_policy_routers.py:51:class SchedulerPersistencePolicyBatchRouter(Resource):
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_persistence_policy_routers.py:70:class SchedulerPersistencePolicyDetailRouter(Resource):
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_job_list_routers.py:71:                lambda job_id: policy_view_map.get(job_id, {}).get("defaultPolicy")
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_job_list_routers.py:74:                lambda job_id: policy_view_map.get(job_id, {}).get("effectivePolicy")
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_job_list_routers.py:77:                lambda job_id: policy_view_map.get(job_id, {}).get("policySource")
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_job_list_routers.py:80:                lambda job_id: policy_view_map.get(job_id, {}).get("supportedPolicies")
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_job_list_routers.py:138:                'default_policy': 'defaultPolicy',
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_job_list_routers.py:139:                'effective_policy': 'effectivePolicy',
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_job_list_routers.py:140:                'policy_source': 'policySource',
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_job_list_routers.py:141:                'supported_policies': 'supportedPolicies',
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/services/scheduler/scheduler_persistence_service.py:36:            "defaultPolicy": self.default_policy,
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/services/scheduler/scheduler_persistence_service.py:37:            "effectivePolicy": self.effective_policy,
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/services/scheduler/scheduler_persistence_service.py:38:            "policySource": self.policy_source,
/Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/services/scheduler/scheduler_persistence_service.py:39:            "supportedPolicies": self.supported_policies,
$ sed -n '1,240p' /Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/docs/task/scheduler_execution_persistence/05_frontend_settings.md
# scheduler 前端单任务策略设置任务
- [ ] 在 scheduler 页面展示任务当前生效策略
- [ ] 提供单任务策略设置入口和表单交互
- [ ] 只允许选择后端返回的 `supportedPolicies`
- [ ] 保存后刷新当前任务行数据
- [ ] 明确“默认值 / 覆盖值 / 生效值”的展示口径

...

$ sed -n '1,220p' /Users/leon/projects/snowball-lite-codex-scheduler-execution-persistence/apps/backend/web/routers/scheduler/scheduler_persistence_policy_routers.py
class SchedulerPersistencePolicyListRouter(Resource):
    def put(self):
        payload = request.get_json(silent=True) or {}
        job_id = payload.get("jobId")
        policy = payload.get("policy")
        ...
        return R.ok(data=data, msg="策略覆盖更新成功")
```
