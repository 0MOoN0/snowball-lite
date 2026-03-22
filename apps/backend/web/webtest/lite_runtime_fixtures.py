from __future__ import annotations

import os

import pytest

from web.webtest.lite_runtime_guard import ensure_test_lite_db_path_isolated


@pytest.fixture(scope="session", autouse=True)
def _lite_default_runtime_paths(tmp_path_factory):
    root = tmp_path_factory.mktemp("pytest-lite-runtime")
    db_path = ensure_test_lite_db_path_isolated(root / "pytest-snowball-lite.db")
    cache_sqlite_path = root / "pytest-lite_xalpha_cache.db"
    old_env = {
        "LITE_DB_PATH": os.environ.get("LITE_DB_PATH"),
        "LITE_ENABLE_PERSISTENT_JOBSTORE": os.environ.get(
            "LITE_ENABLE_PERSISTENT_JOBSTORE"
        ),
        "LITE_ENABLE_SCHEDULER": os.environ.get("LITE_ENABLE_SCHEDULER"),
        "LITE_SCHEDULER_DB_PATH": os.environ.get("LITE_SCHEDULER_DB_PATH"),
        "LITE_XALPHA_CACHE_DIR": os.environ.get("LITE_XALPHA_CACHE_DIR"),
        "LITE_XALPHA_CACHE_BACKEND": os.environ.get("LITE_XALPHA_CACHE_BACKEND"),
        "LITE_XALPHA_CACHE_SQLITE_PATH": os.environ.get("LITE_XALPHA_CACHE_SQLITE_PATH"),
        "LITE_ENABLE_XALPHA_SQL_CACHE": os.environ.get("LITE_ENABLE_XALPHA_SQL_CACHE"),
    }

    os.environ["LITE_DB_PATH"] = str(db_path)
    os.environ["LITE_ENABLE_PERSISTENT_JOBSTORE"] = "true"
    os.environ["LITE_ENABLE_SCHEDULER"] = "true"
    os.environ.pop("LITE_SCHEDULER_DB_PATH", None)
    os.environ["LITE_XALPHA_CACHE_DIR"] = str(root / "pytest-lite_xalpha_cache")
    os.environ["LITE_XALPHA_CACHE_BACKEND"] = "sql"
    os.environ["LITE_XALPHA_CACHE_SQLITE_PATH"] = str(cache_sqlite_path)
    os.environ["LITE_ENABLE_XALPHA_SQL_CACHE"] = "true"

    try:
        yield
    finally:
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@pytest.fixture()
def lite_runtime_paths(tmp_path, monkeypatch):
    db_path = ensure_test_lite_db_path_isolated(tmp_path / "pytest-snowball-lite.db")
    cache_dir = tmp_path / "pytest-lite_xalpha_cache"
    cache_sqlite_path = tmp_path / "pytest-lite_xalpha_cache.db"

    monkeypatch.setenv("LITE_DB_PATH", str(db_path))
    monkeypatch.setenv("LITE_ENABLE_PERSISTENT_JOBSTORE", "true")
    monkeypatch.setenv("LITE_ENABLE_SCHEDULER", "true")
    monkeypatch.delenv("LITE_SCHEDULER_DB_PATH", raising=False)
    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("LITE_XALPHA_CACHE_BACKEND", "sql")
    monkeypatch.setenv("LITE_XALPHA_CACHE_SQLITE_PATH", str(cache_sqlite_path))
    monkeypatch.setenv("LITE_ENABLE_XALPHA_SQL_CACHE", "true")

    return {
        "db_path": db_path,
        "cache_dir": cache_dir,
        "cache_sqlite_path": cache_sqlite_path,
    }


@pytest.fixture()
def lite_runtime_env(lite_runtime_paths):
    return lite_runtime_paths


@pytest.fixture()
def lite_app(lite_runtime_paths):
    from web import create_app
    from web.lite_bootstrap import bootstrap_lite_database
    from web.models import db

    app = create_app("lite")

    with app.app_context():
        bootstrap_lite_database(app)

    yield app

    with app.app_context():
        db.session.remove()

    for engine in db.engines.values():
        engine.dispose()
