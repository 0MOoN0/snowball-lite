from __future__ import annotations

import json
from datetime import datetime, timedelta
from unittest.mock import patch

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
