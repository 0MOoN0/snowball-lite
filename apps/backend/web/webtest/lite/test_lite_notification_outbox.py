from __future__ import annotations

import json
from datetime import datetime, timedelta
from unittest.mock import patch

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_SUBMITTED, JobExecutionEvent, JobSubmissionEvent
from flask import Flask

from web import create_app
from web.common.enum.asset_enum import AssetTypeEnum
from web.lite_bootstrap import bootstrap_lite_database
from web.models import db
from web.models.asset.asset import Asset
from web.models.grid.Grid import Grid
from web.models.grid.GridType import GridType
from web.models.grid.GridTypeDetail import GridTypeDetail
from web.models.notice.Notification import Notification
from web.scheduler.asset_scheduler import (
    _deliver_grid_monitor_notification,
    _make_grid_monitor_notification,
)
from web.scheduler.async_task_scheduler import consume_notification_outbox
from web.scheduler import scheduler_listener
from web.scheduler.manual_job_id import build_manual_job_id
from web.services.async_task.notification_outbox_service import notification_outbox_service
from web.services.notice.notification_service import notification_service


def _dispose_app(app) -> None:
    with app.app_context():
        db.session.remove()

    for engine in db.engines.values():
        engine.dispose()


def _create_lite_app_without_scheduler(monkeypatch, lite_runtime_paths):
    monkeypatch.setenv("LITE_ENABLE_SCHEDULER", "false")
    app = create_app("lite")
    with app.app_context():
        bootstrap_lite_database(app)
    return app


def _seed_grid_monitor_graph() -> GridTypeDetail:
    asset = Asset(
        asset_name="测试资产",
        asset_type=AssetTypeEnum.FUND.value,
        asset_status=0,
        currency=0,
        market=0,
    )
    db.session.add(asset)
    db.session.flush()

    grid = Grid(asset_id=asset.id, grid_name="测试网格", grid_status=0)
    db.session.add(grid)
    db.session.flush()

    grid_type = GridType(
        grid_id=grid.id,
        asset_id=asset.id,
        type_name="测试策略",
        grid_type_status=0,
    )
    db.session.add(grid_type)
    db.session.flush()

    detail = GridTypeDetail(
        grid_type_id=grid_type.id,
        grid_id=grid.id,
        gear="1",
        trigger_purchase_price=10000,
        purchase_price=10000,
        purchase_amount=100000,
        purchase_shares=100,
        trigger_sell_price=11000,
        sell_price=11000,
        sell_shares=100,
        actual_sell_shares=100,
        sell_amount=110000,
        profit=10000,
        save_share_profit=0,
        save_share=0,
        is_current=True,
        monitor_type=0,
    )
    db.session.add(detail)
    db.session.commit()
    return detail


def test_lite_grid_monitor_notification_writes_notification_outbox(
    lite_runtime_paths,
    monkeypatch,
):
    app = _create_lite_app_without_scheduler(monkeypatch, lite_runtime_paths)

    try:
        with app.app_context():
            detail = _seed_grid_monitor_graph()

            with patch(
                "web.scheduler.asset_scheduler.dispatch_notification",
                side_effect=AssertionError("lite 首批链路不应该直接 dispatch"),
            ):
                _make_grid_monitor_notification(
                    [{"trade_list": [detail.id], "current_change": []}]
                )

            outbox_record = notification_outbox_service.get_latest_record()
            notification = (
                db.session.query(Notification).order_by(Notification.id.desc()).first()
            )

            assert notification is not None
            assert outbox_record is not None
            assert (
                outbox_record.status
                == outbox_record.get_status_enum().PENDING.value
            )
            assert outbox_record.event_key == f"notification-dispatch:{notification.id}"
            assert json.loads(outbox_record.payload) == {
                "notification_id": notification.id
            }
    finally:
        _dispose_app(app)


def test_notification_outbox_consumer_retries_and_marks_succeeded(
    lite_runtime_paths,
    monkeypatch,
):
    app = _create_lite_app_without_scheduler(monkeypatch, lite_runtime_paths)

    try:
        with app.app_context():
            notification = notification_service.make_notification(
                business_type=Notification.get_business_type_enum().SYSTEM_RUNNING.value,
                notice_type=Notification.get_notice_type_enum().INFO_MESSAGE.value,
                content={"title": "outbox test", "content": "retry then success"},
                title="outbox test",
            )
            outbox_record = notification_outbox_service.enqueue_notification(
                notification,
                event_key="notification-dispatch:test-retry",
                max_retry_count=2,
            )

            with patch(
                "web.services.async_task.notification_outbox_service.dispatch_notification",
                return_value=(False, "failed"),
            ) as failed_dispatch:
                consume_notification_outbox()

            db.session.refresh(outbox_record)
            assert failed_dispatch.call_count == 1
            assert (
                outbox_record.status
                == outbox_record.get_status_enum().RETRY_WAITING.value
            )
            assert outbox_record.retry_count == 1
            assert outbox_record.next_run_at > datetime.now() - timedelta(seconds=1)
            assert "dispatch_notification returned failed" in (outbox_record.last_error or "")

            outbox_record.next_run_at = datetime.now() - timedelta(seconds=1)
            db.session.commit()

            with patch(
                "web.services.async_task.notification_outbox_service.dispatch_notification",
                return_value=(True, "sync"),
            ) as success_dispatch:
                consume_notification_outbox()

            db.session.refresh(outbox_record)
            assert success_dispatch.call_count == 1
            assert (
                outbox_record.status
                == outbox_record.get_status_enum().SUCCEEDED.value
            )
            assert outbox_record.retry_count == 1
            assert outbox_record.last_error is None
    finally:
        _dispose_app(app)


def test_notification_outbox_signal_only_skips_empty_poll_all_logs(lite_app):
    job_id = "AsyncTaskScheduler.consume_notification_outbox"
    scheduled_run_time = datetime(2026, 3, 22, 16, 1, 44)
    empty_stats = {
        "claimed": 0,
        "succeeded": 0,
        "retried": 0,
        "failed": 0,
        "skipped": 0,
    }

    with lite_app.app_context(), patch("web.scheduler.db.session.add") as mock_add, patch(
        "web.scheduler.db.session.commit"
    ) as mock_commit:
        scheduler_listener(
            JobSubmissionEvent(
                EVENT_JOB_SUBMITTED,
                job_id,
                "default",
                [scheduled_run_time],
            )
        )
        scheduler_listener(
            JobExecutionEvent(
                EVENT_JOB_EXECUTED,
                job_id,
                "default",
                scheduled_run_time,
                retval=empty_stats,
            )
        )

    assert mock_add.call_count == 0
    assert mock_commit.call_count == 0


def test_notification_outbox_signal_only_persists_executed_log_when_claimed(
    lite_app,
):
    job_id = "AsyncTaskScheduler.consume_notification_outbox"
    scheduled_run_time = datetime(2026, 3, 22, 16, 1, 44)
    claimed_stats = {
        "claimed": 2,
        "succeeded": 2,
        "retried": 0,
        "failed": 0,
        "skipped": 0,
    }

    with lite_app.app_context(), patch("web.scheduler.db.session.add") as mock_add, patch(
        "web.scheduler.db.session.commit"
    ) as mock_commit:
        scheduler_listener(
            JobSubmissionEvent(
                EVENT_JOB_SUBMITTED,
                job_id,
                "default",
                [scheduled_run_time],
            )
        )
        scheduler_listener(
            JobExecutionEvent(
                EVENT_JOB_EXECUTED,
                job_id,
                "default",
                scheduled_run_time,
                retval=claimed_stats,
            )
        )

    assert mock_add.call_count == 1
    assert mock_commit.call_count == 1


def test_manual_notification_outbox_retains_submitted_log(lite_app):
    original_job_id = "AsyncTaskScheduler.consume_notification_outbox"
    manual_job_id = build_manual_job_id(original_job_id, "manual-run")
    scheduled_run_time = datetime(2026, 3, 22, 16, 1, 44)

    with lite_app.app_context(), patch("web.scheduler.db.session.add") as mock_add, patch(
        "web.scheduler.db.session.commit"
    ) as mock_commit:
        scheduler_listener(
            JobSubmissionEvent(
                EVENT_JOB_SUBMITTED,
                manual_job_id,
                "default",
                [scheduled_run_time],
            )
        )

    assert mock_add.call_count == 1
    assert mock_commit.call_count == 1


def test_non_lite_grid_monitor_notification_keeps_direct_dispatch():
    app = Flask(__name__)
    app.config["_config_name"] = "test"

    notification = Notification(
        id=1001,
        business_type=Notification.get_business_type_enum().GRID_TRADE.value,
        notice_type=Notification.get_notice_type_enum().CONFIRM_MESSAGE.value,
        notice_status=Notification.get_notice_status_enum().NOT_SENT.value,
        title="网格交易确认通知",
        content=json.dumps({"title": "网格交易确认通知", "grid_info": []}, ensure_ascii=False),
        timestamp=datetime.now(),
    )

    with app.app_context():
        with patch(
            "web.scheduler.asset_scheduler.dispatch_notification",
            return_value=(True, "actor"),
        ) as mock_dispatch, patch(
            "web.scheduler.asset_scheduler.notification_outbox_service.enqueue_notification"
        ) as mock_enqueue:
            result = _deliver_grid_monitor_notification(notification)

    assert result == (True, "actor")
    mock_dispatch.assert_called_once_with(notification)
    mock_enqueue.assert_not_called()
