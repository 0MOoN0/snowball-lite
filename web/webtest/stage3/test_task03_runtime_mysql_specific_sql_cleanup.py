from __future__ import annotations

from types import SimpleNamespace

import sqlalchemy

import web.models as models_module
from web.models import db
from web.scheduler import verify_apscheduler_database


def test_register_engine_log_skips_mysql_specific_probe_for_sqlite(lite_webtest_app, monkeypatch):
    with lite_webtest_app.app_context():
        original_text = models_module.sqlalchemy.text

        def guarded_text(statement, *args, **kwargs):
            if "show variables like 'long_query_time'" in str(statement).lower():
                raise AssertionError("SQLite 分支不应该再执行 MySQL 慢查询变量 SQL")
            return original_text(statement, *args, **kwargs)

        monkeypatch.setattr(models_module.sqlalchemy, "text", guarded_text)
        models_module.register_engine_log(db.engines["snowball"])


def test_verify_apscheduler_database_uses_sqlite_table_inspection(tmp_path, monkeypatch):
    scheduler_db_path = tmp_path / "apscheduler.sqlite"
    scheduler_url = f"sqlite:///{scheduler_db_path}"
    engine = sqlalchemy.create_engine(scheduler_url)

    with engine.begin() as conn:
        conn.execute(
            sqlalchemy.text(
                "CREATE TABLE apscheduler_jobs (id VARCHAR(191) NOT NULL PRIMARY KEY, next_run_time FLOAT, job_state BLOB NOT NULL)"
            )
        )

    original_text = sqlalchemy.text

    def guarded_text(statement, *args, **kwargs):
        if "show tables like 'apscheduler_jobs'" in str(statement).lower():
            raise AssertionError("SQLite 分支不应该再执行 SHOW TABLES LIKE")
        return original_text(statement, *args, **kwargs)

    monkeypatch.setattr(sqlalchemy, "text", guarded_text)

    app = SimpleNamespace(
        config={
            "SCHEDULER_JOBSTORES": {
                "default": {
                    "backend": "sqlalchemy",
                    "url": scheduler_url,
                }
            }
        }
    )

    try:
        assert verify_apscheduler_database(app) is True
    finally:
        engine.dispose()
