from __future__ import annotations

from pathlib import Path

from flask import Flask

from web import settings
from web.lite_bootstrap import get_lite_migration_directory
from web.models import get_migration_directory
from web.common.utils.backend_paths import (
    get_backend_root,
    get_default_lite_db_path,
    get_default_lite_xalpha_cache_dir,
    get_migration_directory_by_config_class,
)


def test_lite_runtime_defaults_do_not_follow_cwd(tmp_path, monkeypatch):
    app = Flask("backend-workspace-paths")

    app.config.from_object(settings.config["lite"])
    monkeypatch.delenv("LITE_DB_PATH", raising=False)
    monkeypatch.delenv("LITE_XALPHA_CACHE_DIR", raising=False)
    monkeypatch.chdir(tmp_path)

    settings.apply_runtime_overrides(app, "lite")

    assert Path(app.config["LITE_DB_PATH"]) == get_default_lite_db_path()
    assert Path(app.config["XALPHA_CACHE_DIR"]) == get_default_lite_xalpha_cache_dir()
    assert Path(app.config["LITE_DB_PATH"]).is_relative_to(get_backend_root())
    assert Path(app.config["XALPHA_CACHE_DIR"]).is_relative_to(get_backend_root())


def test_lite_and_dev_migration_directories_resolve_under_web_workspace():
    assert get_lite_migration_directory() == get_backend_root() / "migrations" / "lite"
    assert Path(get_migration_directory("LiteConfig")) == get_backend_root() / "migrations" / "lite"
    assert Path(get_migration_directory("DevConfig")) == get_backend_root() / "migrations" / "dev"


def test_config_class_migration_mapping_uses_backend_workspace_paths():
    assert get_migration_directory_by_config_class("TestingConfig") == get_backend_root() / "migrations" / "test"
    assert get_migration_directory_by_config_class("StgConfig") == get_backend_root() / "migrations" / "stg"
    assert get_migration_directory_by_config_class("LocalDevTest") == get_backend_root() / "migrations" / "dev"
