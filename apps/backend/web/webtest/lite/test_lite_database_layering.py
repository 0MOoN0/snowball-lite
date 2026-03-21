from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from web import create_app
from web.common.utils.backend_paths import (
    get_default_lite_db_path,
    get_default_lite_dev_db_path,
)
from web.webtest.lite_runtime_guard import ensure_test_lite_db_path_isolated


def test_pytest_lite_db_guard_accepts_tmp_path(tmp_path):
    db_path = tmp_path / "pytest-snowball-lite.db"

    assert ensure_test_lite_db_path_isolated(db_path) == db_path.resolve()


def test_pytest_lite_db_guard_rejects_long_lived_runtime_paths():
    with pytest.raises(ValueError, match="长期 lite 业务库"):
        ensure_test_lite_db_path_isolated(get_default_lite_db_path())

    with pytest.raises(ValueError, match="长期 lite 业务库"):
        ensure_test_lite_db_path_isolated(get_default_lite_dev_db_path())


def test_pytest_lite_db_guard_rejects_manual_non_pytest_path():
    with TemporaryDirectory(prefix="lite-manual-") as root:
        db_path = Path(root) / "snowball_lite.db"

        with pytest.raises(ValueError, match="pytest 临时路径"):
            ensure_test_lite_db_path_isolated(db_path)


def test_lite_runtime_paths_fixture_uses_pytest_prefixed_database_name(
    lite_runtime_paths,
):
    assert lite_runtime_paths["db_path"].name.startswith("pytest-")


def test_create_app_rejects_long_lived_lite_db_path_under_pytest(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("LITE_DB_PATH", str(get_default_lite_db_path()))
    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", str(tmp_path / "pytest-lite_xalpha_cache"))
    monkeypatch.setenv("LITE_XALPHA_CACHE_BACKEND", "csv")

    with pytest.raises(ValueError, match="长期 lite 业务库"):
        create_app("lite")
