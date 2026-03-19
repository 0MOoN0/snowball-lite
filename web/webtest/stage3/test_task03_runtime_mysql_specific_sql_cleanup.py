from __future__ import annotations

import builtins
import importlib
from types import SimpleNamespace

import sqlalchemy

import web.models as models_module
import web.scheduler as scheduler_module
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


def test_lite_modules_import_without_pymysql_dependency(lite_webtest_app, monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pymysql" or name.startswith("pymysql."):
            raise ImportError("pymysql intentionally blocked for lite test")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    reloaded_models = importlib.reload(models_module)
    reloaded_scheduler = importlib.reload(scheduler_module)

    with lite_webtest_app.app_context():
        assert reloaded_models.register_engine_log(db.engines["snowball"]) is None
        assert reloaded_scheduler.verify_apscheduler_database(
            SimpleNamespace(
                config={
                    "SCHEDULER_JOBSTORES": {
                        "default": {
                            "backend": "sqlalchemy",
                            "url": "sqlite:///:memory:",
                        }
                    }
                }
            )
        ) is True


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
