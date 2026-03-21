from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest
import sqlalchemy

import web
from web import create_app
from web.models import db


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


def test_lite_scheduler_disabled_by_default_skips_runtime_and_routes(lite_runtime_paths):
    app = create_app("lite")

    try:
        assert app.config["ENABLE_SCHEDULER"] is False
        assert app.config["SCHEDULER_AVAILABLE"] is False
        assert _scheduler_routes(app) == set()
    finally:
        _dispose_app(app)


def test_lite_scheduler_memory_mode_starts_without_jobstores(lite_runtime_paths, monkeypatch):
    monkeypatch.setenv("LITE_ENABLE_SCHEDULER", "true")
    monkeypatch.delenv("LITE_ENABLE_PERSISTENT_JOBSTORE", raising=False)
    monkeypatch.delenv("LITE_SCHEDULER_DB_PATH", raising=False)

    app = create_app("lite")

    try:
        assert app.config["ENABLE_SCHEDULER"] is True
        assert app.config["ENABLE_PERSISTENT_JOBSTORE"] is False
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
