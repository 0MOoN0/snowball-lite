from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="session", autouse=True)
def _lite_default_runtime_paths(tmp_path_factory):
    root = tmp_path_factory.mktemp("lite-runtime")
    old_env = {
        "LITE_DB_PATH": os.environ.get("LITE_DB_PATH"),
        "LITE_XALPHA_CACHE_DIR": os.environ.get("LITE_XALPHA_CACHE_DIR"),
        "LITE_XALPHA_CACHE_BACKEND": os.environ.get("LITE_XALPHA_CACHE_BACKEND"),
    }

    os.environ["LITE_DB_PATH"] = str(root / "snowball_lite.db")
    os.environ["LITE_XALPHA_CACHE_DIR"] = str(root / "lite_xalpha_cache")
    os.environ["LITE_XALPHA_CACHE_BACKEND"] = "csv"

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
    db_path = tmp_path / "snowball_lite.db"
    cache_dir = tmp_path / "lite_xalpha_cache"

    monkeypatch.setenv("LITE_DB_PATH", str(db_path))
    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", str(cache_dir))
    monkeypatch.setenv("LITE_XALPHA_CACHE_BACKEND", "csv")

    return {
        "db_path": db_path,
        "cache_dir": cache_dir,
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
