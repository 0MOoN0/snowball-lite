from __future__ import annotations

from sqlalchemy import inspect

from web.lite_bootstrap import LITE_STAGE3_REQUIRED_TABLES
from web.models import db


def test_stage3_fixture_bridge_bootstraps_sqlite_schema(lite_webtest_app, lite_webtest_runtime):
    with lite_webtest_app.app_context():
        engine = db.engines["snowball"]
        table_names = set(inspect(engine).get_table_names())

        assert lite_webtest_app.config["_config_name"] == "lite"
        assert engine.dialect.name == "sqlite"
        assert lite_webtest_app.config["LITE_DB_PATH"] == str(lite_webtest_runtime["db_path"])
        assert "alembic_version" in table_names
        assert LITE_STAGE3_REQUIRED_TABLES.issubset(table_names)
