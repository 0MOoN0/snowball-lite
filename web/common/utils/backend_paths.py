from __future__ import annotations

from pathlib import Path


def get_backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_repo_root() -> Path:
    return get_backend_root().parent


def get_legacy_repo_data_root() -> Path:
    return get_repo_root() / "data"


def get_backend_data_root() -> Path:
    return get_backend_root() / "data"


def get_lite_runtime_root() -> Path:
    return get_backend_data_root() / "lite_runtime"


def get_default_lite_db_path() -> Path:
    return get_lite_runtime_root() / "snowball_lite.db"


def get_default_lite_xalpha_cache_dir() -> Path:
    return get_lite_runtime_root() / "lite_xalpha_cache"


def get_default_xalpha_cache_dir() -> Path:
    return get_backend_data_root() / "xalpha_cache"


def get_migrations_root() -> Path:
    return get_backend_root() / "migrations"


def get_migration_directory_by_env(env_name: str) -> Path:
    normalized = env_name.lower()
    if normalized == "prod":
        legacy_prod_dir = get_repo_root() / "migrations_snowball"
        if legacy_prod_dir.exists():
            return legacy_prod_dir
        return get_migrations_root() / "prod"

    migration_dirnames = {
        "dev": "dev",
        "stg": "stg",
        "test": "test",
        "lite": "lite",
    }
    return get_migrations_root() / migration_dirnames.get(normalized, "dev")


def get_migration_directory_by_config_class(config_class_name: str) -> Path:
    config_to_env = {
        "DevConfig": "dev",
        "StgConfig": "stg",
        "ProdConfig": "prod",
        "LocalDevTest": "dev",
        "TestingConfig": "test",
        "LiteConfig": "lite",
    }
    env_name = config_to_env.get(config_class_name, "dev")
    return get_migration_directory_by_env(env_name)


def get_backend_scripts_root() -> Path:
    return get_backend_root() / "scripts"


def get_backend_dev_support_root() -> Path:
    return get_backend_root() / "dev_support"


def get_dev_init_sql_path() -> Path:
    return get_backend_dev_support_root() / "db" / "dev" / "init.sql"
