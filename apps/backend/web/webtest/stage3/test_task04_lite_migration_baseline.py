from __future__ import annotations

from sqlalchemy import inspect, text

from web.lite_bootstrap import LITE_STAGE3_REQUIRED_TABLES, bootstrap_lite_database
from web.models import db


def test_lite_bootstrap_runs_stage3_migration_baseline_idempotently(lite_webtest_app):
    with lite_webtest_app.app_context():
        bootstrap_lite_database(lite_webtest_app)

        engine = db.engines["snowball"]
        table_names = set(inspect(engine).get_table_names())

        with engine.connect() as conn:
            version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()

        assert version == "lite_stage3_baseline"
        assert LITE_STAGE3_REQUIRED_TABLES.issubset(table_names)

        bootstrap_lite_database(lite_webtest_app)

        with engine.connect() as conn:
            rerun_version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()

        assert rerun_version == "lite_stage3_baseline"
