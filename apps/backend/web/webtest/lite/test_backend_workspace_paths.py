from __future__ import annotations

from pathlib import Path

from flask import Flask

from web import settings
from web.lite_bootstrap import get_lite_migration_directory, migrate_legacy_repo_data
from web.models import get_migration_directory
from web.common.utils.backend_paths import (
    get_backend_root,
    get_default_lite_db_path,
    get_default_lite_dev_db_path,
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


def test_lite_runtime_recommends_separate_stable_and_dev_databases():
    assert get_default_lite_db_path().name == "snowball_lite.db"
    assert get_default_lite_dev_db_path().name == "snowball_lite_dev.db"
    assert get_default_lite_db_path().parent == get_default_lite_dev_db_path().parent


def test_lite_and_dev_migration_directories_resolve_under_web_workspace():
    assert get_lite_migration_directory() == get_backend_root() / "migrations" / "lite"
    assert Path(get_migration_directory("LiteConfig")) == get_backend_root() / "migrations" / "lite"
    assert Path(get_migration_directory("DevConfig")) == get_backend_root() / "migrations" / "dev"


def test_config_class_migration_mapping_uses_backend_workspace_paths():
    assert get_migration_directory_by_config_class("TestingConfig") == get_backend_root() / "migrations" / "test"
    assert get_migration_directory_by_config_class("StgConfig") == get_backend_root() / "migrations" / "stg"
    assert get_migration_directory_by_config_class("LocalDevTest") == get_backend_root() / "migrations" / "dev"


def test_migrate_legacy_repo_data_moves_sqlite_files_and_cache_dir(tmp_path):
    legacy_data_root = tmp_path / "data"
    runtime_root = tmp_path / "web" / "data" / "lite_runtime"
    cache_dir = runtime_root / "lite_xalpha_cache"

    legacy_data_root.mkdir(parents=True)
    (legacy_data_root / "snowball_lite.db").write_bytes(b"sqlite-main")
    (legacy_data_root / "snowball_lite.db-wal").write_bytes(b"sqlite-wal")
    (legacy_data_root / "stg_lite.db").write_bytes(b"stg-main")
    (legacy_data_root / "notes.txt").write_text("keep", encoding="utf-8")
    (legacy_data_root / "lite_xalpha_cache").mkdir()
    (legacy_data_root / "lite_xalpha_cache" / "fund.csv").write_text(
        "code,name\n000001,demo\n",
        encoding="utf-8",
    )

    result = migrate_legacy_repo_data(
        legacy_data_root=legacy_data_root,
        runtime_root=runtime_root,
        target_cache_dir=cache_dir,
    )

    moved_sources = {src.name for src, _ in result["moved"]}

    assert moved_sources == {
        "snowball_lite.db",
        "snowball_lite.db-wal",
        "stg_lite.db",
        "lite_xalpha_cache",
    }
    assert not (legacy_data_root / "snowball_lite.db").exists()
    assert not (legacy_data_root / "stg_lite.db").exists()
    assert not (legacy_data_root / "lite_xalpha_cache").exists()
    assert (runtime_root / "snowball_lite.db").read_bytes() == b"sqlite-main"
    assert (runtime_root / "snowball_lite.db-wal").read_bytes() == b"sqlite-wal"
    assert (runtime_root / "stg_lite.db").read_bytes() == b"stg-main"
    assert (cache_dir / "fund.csv").read_text(encoding="utf-8") == "code,name\n000001,demo\n"
    assert (legacy_data_root / "notes.txt").read_text(encoding="utf-8") == "keep"


def test_migrate_legacy_repo_data_does_not_overwrite_existing_targets(tmp_path):
    legacy_data_root = tmp_path / "data"
    runtime_root = tmp_path / "web" / "data" / "lite_runtime"
    cache_dir = runtime_root / "lite_xalpha_cache"

    legacy_data_root.mkdir(parents=True)
    runtime_root.mkdir(parents=True)
    cache_dir.mkdir(parents=True)

    (legacy_data_root / "snowball_lite.db").write_bytes(b"legacy-main")
    (legacy_data_root / "lite_xalpha_cache").mkdir()
    (legacy_data_root / "lite_xalpha_cache" / "legacy.csv").write_text(
        "legacy\n",
        encoding="utf-8",
    )
    (runtime_root / "snowball_lite.db").write_bytes(b"current-main")
    (cache_dir / "current.csv").write_text("current\n", encoding="utf-8")

    result = migrate_legacy_repo_data(
        legacy_data_root=legacy_data_root,
        runtime_root=runtime_root,
        target_cache_dir=cache_dir,
    )

    skipped_sources = {src.name for src, _ in result["skipped"]}

    assert skipped_sources == {"snowball_lite.db", "lite_xalpha_cache"}
    assert (legacy_data_root / "snowball_lite.db").read_bytes() == b"legacy-main"
    assert (runtime_root / "snowball_lite.db").read_bytes() == b"current-main"
    assert (legacy_data_root / "lite_xalpha_cache" / "legacy.csv").read_text(
        encoding="utf-8"
    ) == "legacy\n"
    assert (cache_dir / "current.csv").read_text(encoding="utf-8") == "current\n"
