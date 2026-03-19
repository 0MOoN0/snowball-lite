from __future__ import annotations

import time
from datetime import datetime

import pytest
from sqlalchemy import text

from web.models import db
from web.models.asset.asset import Asset
from web.models.notice.Notification import Notification
from web.models.setting.system_settings import Setting

pytestmark = [pytest.mark.local, pytest.mark.integration]

def test_lite_sqlite_minimal_path(lite_app):
    with lite_app.app_context():
        default_engine = db.engine
        snowball_engine = db.engines["snowball"]

        for engine in (default_engine, snowball_engine):
            with engine.connect() as conn:
                assert conn.execute(text("PRAGMA foreign_keys")).scalar() == 1
                assert str(conn.execute(text("PRAGMA journal_mode")).scalar()).lower() == "wal"
                assert int(conn.execute(text("PRAGMA busy_timeout")).scalar()) == 30000

        setting = Setting(
            key="lite.sqlite.enabled",
            value="true",
            setting_type="bool",
            group="lite",
            description="SQLite 最小链路验证",
        )
        asset = Asset(asset_name="SQLite 测试资产")
        notification = Notification(
            title="SQLite 验证通知",
            content="最小链路验证",
            timestamp=datetime.utcnow(),
        )

        db.session.add_all([setting, asset, notification])
        db.session.commit()

        assert setting.id is not None
        assert asset.id is not None
        assert notification.id is not None

        saved_asset = Asset.query.filter_by(id=asset.id).one()
        first_update_time = saved_asset.update_time

        time.sleep(1.1)
        saved_asset.asset_name = "SQLite 测试资产-已更新"
        db.session.commit()
        db.session.refresh(saved_asset)

        assert Setting.query.filter_by(key="lite.sqlite.enabled").one().value == "true"
        assert Asset.query.filter_by(id=asset.id).one().asset_name == "SQLite 测试资产-已更新"
        assert Notification.query.filter_by(id=notification.id).one().title == "SQLite 验证通知"
        assert saved_asset.update_time is not None
        assert first_update_time is not None
        assert saved_asset.update_time >= first_update_time

    db.session.remove()
    for engine in db.engines.values():
        engine.dispose()
