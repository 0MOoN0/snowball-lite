from __future__ import annotations

from sqlalchemy import inspect, text

from web.lite_bootstrap import LITE_STAGE5_REQUIRED_TABLES, get_lite_head_revision
from web.models import db


def test_lite_app_fixture_bootstraps_stage5_schema(lite_app):
    with lite_app.app_context():
        engine = db.engines["snowball"]
        table_names = set(inspect(engine).get_table_names())

        with engine.connect() as conn:
            version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()

        assert version == get_lite_head_revision()
        assert LITE_STAGE5_REQUIRED_TABLES.issubset(table_names)
