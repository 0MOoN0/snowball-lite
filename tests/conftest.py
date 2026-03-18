from __future__ import annotations

import os

import pytest


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
