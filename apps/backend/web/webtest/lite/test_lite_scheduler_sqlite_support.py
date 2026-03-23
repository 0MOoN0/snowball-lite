from __future__ import annotations

import json
from datetime import datetime, timedelta
import sys
from types import SimpleNamespace
from unittest.mock import patch

from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_SUBMITTED,
    JobExecutionEvent,
    JobSubmissionEvent,
)
import pytest
import sqlalchemy

import web
from web import create_app
from web.common.utils.backend_paths import get_default_lite_scheduler_db_path
from web.lite_bootstrap import bootstrap_lite_database
from web.models import db
from web.models.scheduler.scheduler_log import SchedulerLog
from web.models.scheduler.scheduler_job_state import SchedulerJobState
from web.models.setting.system_settings import Setting
from web.scheduler import scheduler_listener
from web.services.scheduler.scheduler_service import scheduler_service


def _cleanup_scheduler_singleton() -> None:
    scheduler_module = sys.modules.get("web.scheduler")
    base_module = sys.modules.get("web.scheduler.base")

    if base_module is not None:
        scheduler_instance = getattr(base_module, "scheduler", None)
        if scheduler_instance is not None:
            try:
                if getattr(scheduler_instance, "running", False):
                    scheduler_instance.shutdown(wait=False)
            except Exception:
                pass
            internal_scheduler = getattr(scheduler_instance, "_scheduler", None)
            listeners = getattr(internal_scheduler, "_listeners", None)
            if hasattr(listeners, "clear"):
                listeners.clear()

    if scheduler_module is not None:
        scheduler_module._scheduler_initialized = False


def _dispose_app(app) -> None:
    with app.app_context():
        db.session.remove()

    for engine in db.engines.values():
        engine.dispose()


def _scheduler_routes(app) -> set[str]:
    return {rule.rule for rule in app.url_map.iter_rules() if rule.rule.startswith("/scheduler")}


@pytest.fixture(autouse=True)
def reset_scheduler_runtime():
    _cleanup_scheduler_singleton()
    yield
    _cleanup_scheduler_singleton()


def test_lite_scheduler_enabled_by_default_starts_runtime_and_routes(lite_runtime_paths):
    app = create_app("lite")

    try:
        assert app.config["ENABLE_SCHEDULER"] is True
        assert app.config["ENABLE_PERSISTENT_JOBSTORE"] is True
        assert app.config["SCHEDULER_AVAILABLE"] is True
        assert app.config["LITE_SCHEDULER_DB_PATH"] == str(
            get_default_lite_scheduler_db_path(lite_runtime_paths["db_path"])
        )
        assert "/scheduler" in _scheduler_routes(app)

        engine = sqlalchemy.create_engine(
            f"sqlite:///{app.config['LITE_SCHEDULER_DB_PATH']}"
        )
        try:
            inspector = sqlalchemy.inspect(engine)
            assert inspector.has_table("apscheduler_jobs") is True
        finally:
            engine.dispose()
    finally:
        _dispose_app(app)


def test_lite_scheduler_can_be_disabled_explicitly(lite_runtime_paths, monkeypatch):
    monkeypatch.setenv("LITE_ENABLE_SCHEDULER", "false")

    app = create_app("lite")

    try:
        assert app.config["ENABLE_SCHEDULER"] is False
        assert app.config["SCHEDULER_AVAILABLE"] is False
        assert _scheduler_routes(app) == set()
    finally:
        _dispose_app(app)


def test_lite_scheduler_memory_mode_starts_without_jobstores(lite_runtime_paths, monkeypatch):
    monkeypatch.setenv("LITE_ENABLE_SCHEDULER", "true")
    monkeypatch.setenv("LITE_ENABLE_PERSISTENT_JOBSTORE", "false")
    monkeypatch.delenv("LITE_SCHEDULER_DB_PATH", raising=False)

    app = create_app("lite")

    try:
        assert app.config["ENABLE_SCHEDULER"] is True
        assert app.config["ENABLE_PERSISTENT_JOBSTORE"] is False
        assert app.config["LITE_SCHEDULER_DB_PATH"] == str(
            get_default_lite_scheduler_db_path(lite_runtime_paths["db_path"])
        )
        assert "SCHEDULER_JOBSTORES" not in app.config
        assert app.config["SCHEDULER_AVAILABLE"] is True
        assert "/scheduler" in _scheduler_routes(app)
    finally:
        _dispose_app(app)


def test_lite_scheduler_persistent_mode_bootstraps_empty_sqlite_jobstore(
    lite_runtime_paths,
    monkeypatch,
    tmp_path,
):
    scheduler_db_path = tmp_path / "scheduler" / "jobs.sqlite"
    monkeypatch.setenv("LITE_ENABLE_SCHEDULER", "true")
    monkeypatch.setenv("LITE_ENABLE_PERSISTENT_JOBSTORE", "true")
    monkeypatch.setenv("LITE_SCHEDULER_DB_PATH", str(scheduler_db_path))

    app = create_app("lite")

    try:
        assert app.config["ENABLE_SCHEDULER"] is True
        assert app.config["ENABLE_PERSISTENT_JOBSTORE"] is True
        assert app.config["LITE_SCHEDULER_DB_PATH"] == str(scheduler_db_path.resolve())
        assert app.config["SCHEDULER_AVAILABLE"] is True

        engine = sqlalchemy.create_engine(f"sqlite:///{scheduler_db_path}")
        try:
            inspector = sqlalchemy.inspect(engine)
            assert inspector.has_table("apscheduler_jobs") is True
        finally:
            engine.dispose()
    finally:
        _dispose_app(app)


def test_lite_scheduler_persistent_mode_rejects_same_sqlite_file(
    lite_runtime_paths,
    monkeypatch,
):
    monkeypatch.setenv("LITE_ENABLE_SCHEDULER", "true")
    monkeypatch.setenv("LITE_ENABLE_PERSISTENT_JOBSTORE", "true")
    monkeypatch.setenv("LITE_SCHEDULER_DB_PATH", str(lite_runtime_paths["db_path"]))

    with pytest.raises(ValueError, match="LITE_SCHEDULER_DB_PATH 不能与 LITE_DB_PATH 指向同一个文件"):
        create_app("lite")


def test_lite_scheduler_jobs_route_handles_empty_scheduler_log_table(
    lite_runtime_paths,
):
    app = create_app("lite")

    try:
        with app.app_context():
            bootstrap_lite_database(app)

        response = app.test_client().get("/scheduler/jobs")

        assert response.status_code == 200
        payload = response.get_json()
        assert payload["success"] is True
        assert isinstance(payload["data"], list)
    finally:
        _dispose_app(app)


def test_lite_scheduler_jobs_route_prefers_job_state_over_event_log(lite_runtime_paths):
    scheduled_run_time = datetime(2026, 3, 22, 16, 1, 44)
    app = create_app("lite")

    try:
        fake_job = SimpleNamespace(
            id="AsyncTaskScheduler.consume_notification_outbox",
            kwargs={},
            func_ref="web.scheduler.async_task_scheduler:consume_notification_outbox_job",
            next_run_time=scheduled_run_time,
            trigger="interval[0:01:00]",
            name="lite 通知 outbox 消费（每分钟）",
        )
        fake_state = SchedulerJobState(
            job_id="AsyncTaskScheduler.consume_notification_outbox",
            last_execution_state=SchedulerLog.get_scheduler_state_enum().EXECUTED.value,
            last_scheduler_run_time=scheduled_run_time,
            last_finished_time=scheduled_run_time,
        )
        fake_log = SchedulerLog(
            job_id="AsyncTaskScheduler.consume_notification_outbox",
            execution_state=SchedulerLog.get_scheduler_state_enum().ERROR.value,
            scheduler_run_time=datetime(2026, 3, 22, 15, 1, 44),
            exception="old error",
        )

        with patch(
            "web.routers.scheduler.scheduler_job_list_routers.scheduler.get_jobs",
            return_value=[fake_job],
        ), patch(
            "web.routers.scheduler.scheduler_job_list_routers.scheduler_service.get_job_states_by_ids",
            return_value=[fake_state],
        ), patch(
            "web.routers.scheduler.scheduler_job_list_routers.scheduler_service.get_latest_job_logs_by_ids",
            return_value=[fake_log],
        ), patch(
            "web.routers.scheduler.scheduler_job_list_routers.scheduler_service.get_job_counts",
            return_value=[],
        ):
            response = app.test_client().get("/scheduler/jobs")

        assert response.status_code == 200
        payload = response.get_json()
        target_row = payload["data"][0]
        assert target_row["jobId"] == "AsyncTaskScheduler.consume_notification_outbox"
        assert target_row["executionState"] == SchedulerLog.get_scheduler_state_enum().EXECUTED.value
        assert target_row["schedulerRunTime"].startswith("2026-03-22T16:01:44")
    finally:
        _dispose_app(app)


def test_lite_scheduler_jobs_route_returns_execution_persistence_fields(
    lite_runtime_paths,
):
    scheduled_run_time = datetime(2026, 3, 22, 16, 1, 44)
    app = create_app("lite")

    try:
        fake_job = SimpleNamespace(
            id="AsyncTaskScheduler.consume_notification_outbox",
            kwargs={},
            func_ref="web.scheduler.async_task_scheduler:consume_notification_outbox_job",
            next_run_time=scheduled_run_time,
            trigger="interval[0:01:00]",
            name="lite 通知 outbox 消费（每分钟）",
        )

        with patch(
            "web.routers.scheduler.scheduler_job_list_routers.scheduler.get_jobs",
            return_value=[fake_job],
        ), patch(
            "web.routers.scheduler.scheduler_job_list_routers.scheduler_service.get_job_states_by_ids",
            return_value=[],
        ), patch(
            "web.routers.scheduler.scheduler_job_list_routers.scheduler_service.get_latest_job_logs_by_ids",
            return_value=[],
        ), patch(
            "web.routers.scheduler.scheduler_job_list_routers.scheduler_service.get_job_counts",
            return_value=[],
        ):
            response = app.test_client().get("/scheduler/jobs")

        assert response.status_code == 200
        payload = response.get_json()
        target_row = payload["data"][0]
        assert target_row["jobId"] == "AsyncTaskScheduler.consume_notification_outbox"
        assert target_row["defaultPolicy"] == "signal_only"
        assert target_row["effectivePolicy"] == "signal_only"
        assert target_row["policySource"] == "default"
        assert target_row["supportedPolicies"] == ["full", "signal_only"]
    finally:
        _dispose_app(app)


def test_lite_scheduler_listener_uses_persisted_execution_policy_override(lite_app):
    scheduled_run_time = datetime(2026, 3, 22, 16, 1, 44)
    actual_finished_time = datetime(2026, 3, 22, 18, 0, 0)

    with lite_app.app_context():
        db.session.add(
            Setting(
                key="scheduler.execution_persistence_policies",
                value=json.dumps(
                    {
                        "AsyncTaskScheduler.consume_notification_outbox": "full",
                    },
                    ensure_ascii=False,
                ),
                setting_type="json",
                group="system",
                description="scheduler execution persistence overrides",
            )
        )
        db.session.commit()

    with patch("web.scheduler.datetime", new=SimpleNamespace(now=lambda: actual_finished_time)):
        scheduler_listener(
            JobSubmissionEvent(
                EVENT_JOB_SUBMITTED,
                "AsyncTaskScheduler.consume_notification_outbox",
                "default",
                [scheduled_run_time],
            )
        )
        scheduler_listener(
            JobExecutionEvent(
                EVENT_JOB_EXECUTED,
                "AsyncTaskScheduler.consume_notification_outbox",
                "default",
                scheduled_run_time,
                retval={
                    "claimed": 0,
                    "succeeded": 0,
                    "retried": 0,
                    "failed": 0,
                    "skipped": 0,
                },
            )
        )

    with lite_app.app_context():
        job_state = (
            db.session.query(SchedulerJobState)
            .filter(
                SchedulerJobState.job_id
                == "AsyncTaskScheduler.consume_notification_outbox"
            )
            .one()
        )
        event_log = (
            db.session.query(SchedulerLog)
            .filter(
                SchedulerLog.job_id
                == "AsyncTaskScheduler.consume_notification_outbox"
            )
            .order_by(SchedulerLog.id.desc())
            .first()
        )

        assert job_state.last_signal_run_time == actual_finished_time
        assert event_log is not None
        assert event_log.execution_state == SchedulerLog.get_scheduler_state_enum().EXECUTED.value


def test_lite_scheduler_execution_policy_routes_support_upsert_batch_and_delete(
    lite_app,
):
    client = lite_app.test_client()

    update_response = client.put(
        "/scheduler/persistence-policies/batch",
        data=json.dumps(
            {
                "items": [
                    {
                        "jobId": "AsyncTaskScheduler.consume_notification_outbox",
                        "policy": "full",
                    }
                ]
            }
        ),
        content_type="application/json",
    )

    assert update_response.status_code == 200
    update_payload = update_response.get_json()
    assert update_payload["success"] is True

    with lite_app.app_context():
        setting = Setting.query.filter_by(
            key="scheduler.execution_persistence_policies"
        ).first()
        assert setting is not None
        assert json.loads(setting.value) == {
            "AsyncTaskScheduler.consume_notification_outbox": "full"
        }

    query_response = client.get("/scheduler/persistence-policies")
    assert query_response.status_code == 200
    query_payload = query_response.get_json()
    assert query_payload["success"] is True
    target_view = next(
        item
        for item in query_payload["data"]["items"]
        if item["jobId"] == "AsyncTaskScheduler.consume_notification_outbox"
    )
    assert target_view["defaultPolicy"] == "signal_only"
    assert target_view["effectivePolicy"] == "full"
    assert target_view["policySource"] == "override"

    delete_response = client.delete(
        "/scheduler/persistence-policies/AsyncTaskScheduler.consume_notification_outbox"
    )
    assert delete_response.status_code == 200
    delete_payload = delete_response.get_json()
    assert delete_payload["success"] is True

    with lite_app.app_context():
        setting = Setting.query.filter_by(
            key="scheduler.execution_persistence_policies"
        ).first()
        assert setting is None

    query_response = client.get("/scheduler/persistence-policies")
    query_payload = query_response.get_json()
    target_view = next(
        item
        for item in query_payload["data"]["items"]
        if item["jobId"] == "AsyncTaskScheduler.consume_notification_outbox"
    )
    assert target_view["effectivePolicy"] == "signal_only"
    assert target_view["policySource"] == "default"


def test_lite_scheduler_execution_policy_routes_reject_invalid_requests(lite_app):
    client = lite_app.test_client()

    unknown_job_response = client.put(
        "/scheduler/persistence-policies",
        data=json.dumps({"jobId": "unknown.job", "policy": "full"}),
        content_type="application/json",
    )
    assert unknown_job_response.status_code == 200
    unknown_job_payload = unknown_job_response.get_json()
    assert unknown_job_payload["success"] is False
    assert "unknown.job" in unknown_job_payload["message"]

    invalid_policy_response = client.put(
        "/scheduler/persistence-policies",
        data=json.dumps(
            {
                "jobId": "AsyncTaskScheduler.consume_notification_outbox",
                "policy": "drop_all",
            }
        ),
        content_type="application/json",
    )
    assert invalid_policy_response.status_code == 200
    invalid_policy_payload = invalid_policy_response.get_json()
    assert invalid_policy_payload["success"] is False
    assert "drop_all" in invalid_policy_payload["message"]

    unswitchable_job_response = client.put(
        "/scheduler/persistence-policies",
        data=json.dumps(
            {
                "jobId": "notice_scheduler.daily_report",
                "policy": "full",
            }
        ),
        content_type="application/json",
    )
    assert unswitchable_job_response.status_code == 200
    unswitchable_job_payload = unswitchable_job_response.get_json()
    assert unswitchable_job_payload["success"] is False
    assert "notice_scheduler.daily_report" in unswitchable_job_payload["message"]


def test_lite_scheduler_service_latest_logs_by_ids_returns_every_requested_job_when_logs_are_dense(
    lite_app,
):
    base_time = datetime(2026, 3, 22, 10, 0, 0)
    job_ids = [f"dense-job-{index}" for index in range(30)]

    with lite_app.app_context():
        for job_index, job_id in enumerate(job_ids):
            for run_index in range(10):
                db.session.add(
                    SchedulerLog(
                        job_id=job_id,
                        execution_state=SchedulerLog.get_scheduler_state_enum().EXECUTED.value,
                        scheduler_run_time=base_time
                        + timedelta(minutes=job_index * 10 + run_index),
                    )
                )
        db.session.commit()

        latest_logs = scheduler_service.get_latest_job_logs_by_ids(job_ids)

        assert len(latest_logs) == len(job_ids)
        assert {row.job_id for row in latest_logs} == set(job_ids)
        latest_log_by_job_id = {row.job_id: row for row in latest_logs}
        for job_index, job_id in enumerate(job_ids):
            assert latest_log_by_job_id[job_id].scheduler_run_time == base_time + timedelta(
                minutes=job_index * 10 + 9
            )


def test_lite_scheduler_listener_persists_error_exception_as_text(lite_app):
    event = JobExecutionEvent(
        EVENT_JOB_ERROR,
        "demo-job",
        "default",
        datetime(2026, 3, 22, 16, 1, 44),
        exception=TimeoutError("boom"),
        traceback="traceback text",
    )

    scheduler_listener(event)

    with lite_app.app_context():
        record = (
            db.session.query(SchedulerLog)
            .filter(SchedulerLog.job_id == "demo-job")
            .order_by(SchedulerLog.id.desc())
            .first()
        )

        assert record is not None
        assert record.exception == "boom"
        assert record.traceback == "traceback text"


def test_lite_scheduler_listener_records_actual_finished_time_for_error_event(lite_app):
    scheduled_run_time = datetime(2026, 3, 22, 16, 1, 44)
    actual_finished_time = datetime(2026, 3, 22, 18, 0, 0)
    event = JobExecutionEvent(
        EVENT_JOB_ERROR,
        "demo-job",
        "default",
        scheduled_run_time,
        exception=TimeoutError("boom"),
        traceback="traceback text",
    )

    with patch("web.scheduler.datetime", new=SimpleNamespace(now=lambda: actual_finished_time)):
        scheduler_listener(event)

    with lite_app.app_context():
        job_state = (
            db.session.query(SchedulerJobState)
            .filter(SchedulerJobState.job_id == "demo-job")
            .one()
        )

        assert job_state.last_execution_state == SchedulerLog.get_scheduler_state_enum().ERROR.value
        assert job_state.last_scheduler_run_time == scheduled_run_time
        assert job_state.last_finished_time == actual_finished_time
        assert job_state.last_error == "boom"
        assert job_state.last_error_time == actual_finished_time


def test_lite_scheduler_listener_keeps_job_state_for_signal_only_empty_poll(lite_app):
    scheduled_run_time = datetime(2026, 3, 22, 16, 1, 44)
    actual_finished_time = datetime(2026, 3, 22, 18, 0, 0)
    with patch("web.scheduler.datetime", new=SimpleNamespace(now=lambda: actual_finished_time)):
        scheduler_listener(
            JobSubmissionEvent(
                EVENT_JOB_SUBMITTED,
                "AsyncTaskScheduler.consume_notification_outbox",
                "default",
                [scheduled_run_time],
            )
        )
        scheduler_listener(
            JobExecutionEvent(
                EVENT_JOB_EXECUTED,
                "AsyncTaskScheduler.consume_notification_outbox",
                "default",
                scheduled_run_time,
                retval={
                    "claimed": 0,
                    "succeeded": 0,
                    "retried": 0,
                    "failed": 0,
                    "skipped": 0,
                },
            )
        )

    with lite_app.app_context():
        job_state = (
            db.session.query(SchedulerJobState)
            .filter(
                SchedulerJobState.job_id
                == "AsyncTaskScheduler.consume_notification_outbox"
            )
            .one()
        )
        event_log = (
            db.session.query(SchedulerLog)
            .filter(
                SchedulerLog.job_id
                == "AsyncTaskScheduler.consume_notification_outbox"
            )
            .order_by(SchedulerLog.id.desc())
            .first()
        )

        assert job_state.last_execution_state == SchedulerLog.get_scheduler_state_enum().EXECUTED.value
        assert job_state.last_scheduler_run_time == scheduled_run_time
        assert job_state.last_finished_time == actual_finished_time
        assert job_state.last_signal_run_time is None
        assert event_log is None


def test_lite_scheduler_init_failure_does_not_mark_scheduler_available(
    lite_runtime_paths,
    monkeypatch,
):
    monkeypatch.setenv("LITE_ENABLE_SCHEDULER", "true")
    captured: dict[str, object] = {}
    original_import = web._import_web_module

    def fake_import(module_name: str):
        if module_name == "scheduler":
            return SimpleNamespace(init_app=lambda app: captured.setdefault("app", app) and False)
        return original_import(module_name)

    monkeypatch.setattr(web, "_import_web_module", fake_import)

    with pytest.raises(Exception, match="调度器初始化失败"):
        web.create_app("lite")

    app = captured["app"]
    try:
        assert app.config["SCHEDULER_AVAILABLE"] is False
    finally:
        _dispose_app(app)


def test_lite_scheduler_test_cleanup_keeps_listener_count_stable(
    lite_runtime_paths,
    monkeypatch,
):
    monkeypatch.setenv("LITE_ENABLE_SCHEDULER", "true")

    app_one = create_app("lite")
    try:
        from web.scheduler.base import scheduler as scheduler_instance

        listener_count_one = len(getattr(scheduler_instance._scheduler, "_listeners", []))
    finally:
        _dispose_app(app_one)

    _cleanup_scheduler_singleton()

    app_two = create_app("lite")
    try:
        from web.scheduler.base import scheduler as scheduler_instance

        listener_count_two = len(getattr(scheduler_instance._scheduler, "_listeners", []))
        assert listener_count_one >= 1
        assert listener_count_two == listener_count_one
    finally:
        _dispose_app(app_two)
