from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import sqlalchemy

from web.models import db
from web.models.setting.system_settings import Setting
from web.weblogger import error, warning


SCHEDULER_EXECUTION_PERSISTENCE_SETTING_KEY = (
    "scheduler.execution_persistence_policies"
)


class SchedulerPersistenceValidationError(ValueError):
    pass


@dataclass(frozen=True)
class SchedulerExecutionPersistenceView:
    job_id: str
    default_policy: str
    effective_policy: str
    policy_source: str
    supported_policies: list[str]
    switchable: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "jobId": self.job_id,
            "defaultPolicy": self.default_policy,
            "effectivePolicy": self.effective_policy,
            "policySource": self.policy_source,
            "supportedPolicies": self.supported_policies,
            "switchable": self.switchable,
            "reason": self.reason,
        }


class SchedulerPersistenceService:
    def _load_registry(self):
        from web.scheduler import _get_registered_execution_persistence_profiles

        return _get_registered_execution_persistence_profiles()

    def _load_profile(self, job_id: str):
        from web.scheduler import _get_execution_persistence_profile

        return _get_execution_persistence_profile(job_id)

    def _get_available_policies(self) -> tuple[str, ...]:
        from web.scheduler import _EXECUTION_PERSISTENCE_AVAILABLE_STRATEGIES

        return _EXECUTION_PERSISTENCE_AVAILABLE_STRATEGIES

    def _load_setting(self) -> Setting | None:
        try:
            return Setting.query.filter_by(
                key=SCHEDULER_EXECUTION_PERSISTENCE_SETTING_KEY
            ).first()
        except sqlalchemy.exc.OperationalError:
            return None

    def _load_override_mapping(self) -> dict[str, str]:
        setting = self._load_setting()
        if setting is None or not setting.value:
            return {}

        try:
            payload = json.loads(setting.value)
        except Exception as exc:
            warning(
                f"读取 scheduler execution persistence overrides 失败，按空配置回退: {exc}"
            )
            return {}

        if not isinstance(payload, dict):
            warning("scheduler execution persistence overrides 不是 JSON 对象，按空配置回退")
            return {}

        result: dict[str, str] = {}
        for job_id, policy in payload.items():
            if isinstance(job_id, str) and isinstance(policy, str):
                result[job_id] = policy
        return result

    def _persist_override_mapping(self, overrides: dict[str, str]) -> None:
        setting = self._load_setting()

        if not overrides:
            if setting is not None:
                db.session.delete(setting)
            return

        payload = json.dumps(overrides, ensure_ascii=False, sort_keys=True)
        if setting is None:
            setting = Setting(
                key=SCHEDULER_EXECUTION_PERSISTENCE_SETTING_KEY,
                value=payload,
                setting_type="json",
                group="system",
                description="scheduler execution persistence policy overrides",
            )
            db.session.add(setting)
            return

        setting.value = payload
        setting.setting_type = "json"
        setting.group = setting.group or "system"
        if not setting.description:
            setting.description = "scheduler execution persistence policy overrides"

    def _get_known_profile_or_raise(self, job_id: str):
        registry = self._load_registry()
        profile = registry.get(job_id)
        if profile is None:
            raise SchedulerPersistenceValidationError(
                f"未知 scheduler 任务: {job_id}"
            )
        return profile

    def _validate_policy_for_update(self, job_id: str, policy: str):
        profile = self._get_known_profile_or_raise(job_id)

        if policy not in self._get_available_policies():
            raise SchedulerPersistenceValidationError(
                f"非法策略: {policy}"
            )

        if not profile.switchable:
            raise SchedulerPersistenceValidationError(
                f"任务不支持切换执行持久化策略: {job_id}"
            )

        if policy not in profile.supported_policies:
            raise SchedulerPersistenceValidationError(
                f"任务 {job_id} 不支持策略 {policy}"
            )

        return profile

    def _build_view(
        self,
        job_id: str,
        overrides: dict[str, str] | None = None,
        *,
        known_only: bool,
    ) -> SchedulerExecutionPersistenceView:
        if known_only:
            profile = self._get_known_profile_or_raise(job_id)
        else:
            profile = self._load_profile(job_id)

        if overrides is None:
            overrides = self._load_override_mapping()

        effective_policy = profile.default_policy
        policy_source = "default"
        override_policy = overrides.get(job_id)

        if (
            override_policy is not None
            and profile.switchable
            and override_policy in profile.supported_policies
        ):
            effective_policy = override_policy
            policy_source = "override"

        return SchedulerExecutionPersistenceView(
            job_id=job_id,
            default_policy=profile.default_policy,
            effective_policy=effective_policy,
            policy_source=policy_source,
            supported_policies=list(profile.supported_policies),
            switchable=profile.switchable,
            reason=profile.reason,
        )

    def get_effective_policy(self, job_id: str | None) -> str:
        if not job_id:
            return self._load_profile(job_id).default_policy
        return self._build_view(job_id, known_only=False).effective_policy

    def get_policy_view(self, job_id: str) -> dict[str, Any]:
        return self._build_view(job_id, known_only=True).to_dict()

    def get_policy_views(self) -> list[dict[str, Any]]:
        overrides = self._load_override_mapping()
        return [
            self._build_view(job_id, overrides, known_only=True).to_dict()
            for job_id in self._load_registry()
        ]

    def get_policy_view_map(self, job_ids: list[str]) -> dict[str, dict[str, Any]]:
        overrides = self._load_override_mapping()
        return {
            job_id: self._build_view(job_id, overrides, known_only=False).to_dict()
            for job_id in job_ids
        }

    def update_policy(self, job_id: str, policy: str) -> dict[str, Any]:
        profile = self._validate_policy_for_update(job_id, policy)
        overrides = self._load_override_mapping()

        if policy == profile.default_policy:
            overrides.pop(job_id, None)
        else:
            overrides[job_id] = policy

        try:
            self._persist_override_mapping(overrides)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            error(f"更新 scheduler execution persistence policy 失败: {exc}", exc_info=True)
            raise

        return self._build_view(job_id, overrides, known_only=True).to_dict()

    def batch_update_policies(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        overrides = self._load_override_mapping()
        profiles: dict[str, Any] = {}

        for item in items:
            job_id = item.get("jobId")
            policy = item.get("policy")
            if not isinstance(job_id, str) or not job_id:
                raise SchedulerPersistenceValidationError("jobId 不能为空")
            if not isinstance(policy, str) or not policy:
                raise SchedulerPersistenceValidationError(
                    f"任务 {job_id} 的 policy 不能为空"
                )
            profiles[job_id] = self._validate_policy_for_update(job_id, policy)

        for item in items:
            job_id = item["jobId"]
            policy = item["policy"]
            if policy == profiles[job_id].default_policy:
                overrides.pop(job_id, None)
            else:
                overrides[job_id] = policy

        try:
            self._persist_override_mapping(overrides)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            error(
                f"批量更新 scheduler execution persistence policy 失败: {exc}",
                exc_info=True,
            )
            raise

        return [
            self._build_view(item["jobId"], overrides, known_only=True).to_dict()
            for item in items
        ]

    def delete_policy_override(self, job_id: str) -> dict[str, Any]:
        self._get_known_profile_or_raise(job_id)
        overrides = self._load_override_mapping()
        overrides.pop(job_id, None)

        try:
            self._persist_override_mapping(overrides)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            error(f"删除 scheduler execution persistence override 失败: {exc}", exc_info=True)
            raise

        return self._build_view(job_id, overrides, known_only=True).to_dict()


scheduler_persistence_service = SchedulerPersistenceService()
