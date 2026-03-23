from __future__ import annotations

from flask import Blueprint, request
from flask_restful import Api, Resource

from web.common.utils import R
from web.services.scheduler.scheduler_persistence_service import (
    SchedulerPersistenceValidationError,
    scheduler_persistence_service,
)
from web.weblogger import error


scheduler_persistence_policy_bp = Blueprint(
    "scheduler_persistence_policy",
    __name__,
    url_prefix="/scheduler/persistence-policies",
)
scheduler_persistence_policy_api = Api(scheduler_persistence_policy_bp)


class SchedulerPersistencePolicyListRouter(Resource):
    def get(self):
        return R.ok(
            data={
                "items": scheduler_persistence_service.get_policy_views(),
            }
        )

    def put(self):
        payload = request.get_json(silent=True) or {}
        job_id = payload.get("jobId")
        policy = payload.get("policy")

        if not isinstance(job_id, str) or not job_id:
            return R.fail(msg="jobId 不能为空")
        if not isinstance(policy, str) or not policy:
            return R.fail(msg="policy 不能为空")

        try:
            data = scheduler_persistence_service.update_policy(job_id, policy)
        except SchedulerPersistenceValidationError as exc:
            return R.fail(msg=str(exc))
        except Exception as exc:
            error(f"更新 scheduler persistence policy 失败: {exc}", exc_info=True)
            return R.fail(msg=f"更新失败：{exc}")

        return R.ok(data=data, msg="策略覆盖更新成功")


class SchedulerPersistencePolicyBatchRouter(Resource):
    def put(self):
        payload = request.get_json(silent=True) or {}
        items = payload.get("items")

        if not isinstance(items, list) or not items:
            return R.fail(msg="items 不能为空")

        try:
            data = scheduler_persistence_service.batch_update_policies(items)
        except SchedulerPersistenceValidationError as exc:
            return R.fail(msg=str(exc))
        except Exception as exc:
            error(f"批量更新 scheduler persistence policy 失败: {exc}", exc_info=True)
            return R.fail(msg=f"批量更新失败：{exc}")

        return R.ok(data={"items": data}, msg="策略覆盖批量更新成功")


class SchedulerPersistencePolicyDetailRouter(Resource):
    def delete(self, job_id: str):
        if not job_id:
            return R.fail(msg="jobId 不能为空")

        try:
            data = scheduler_persistence_service.delete_policy_override(job_id)
        except SchedulerPersistenceValidationError as exc:
            return R.fail(msg=str(exc))
        except Exception as exc:
            error(f"删除 scheduler persistence policy override 失败: {exc}", exc_info=True)
            return R.fail(msg=f"删除失败：{exc}")

        return R.ok(data=data, msg="策略覆盖删除成功")


scheduler_persistence_policy_api.add_resource(
    SchedulerPersistencePolicyListRouter,
    "",
)
scheduler_persistence_policy_api.add_resource(
    SchedulerPersistencePolicyBatchRouter,
    "/batch",
)
scheduler_persistence_policy_api.add_resource(
    SchedulerPersistencePolicyDetailRouter,
    "/<path:job_id>",
)
