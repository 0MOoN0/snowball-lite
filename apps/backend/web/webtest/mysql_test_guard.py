from __future__ import annotations

import os
import re
from collections.abc import Iterable

MYSQL_INTEGRATION_MARK = "mysql_integration"
MYSQL_FIXTURE_NAMES = frozenset(
    {
        "app",
        "client",
        "session",
        "rollback_session",
        "setup_test_database",
        "test_db_app",
        "test_db_session",
    }
)

MYSQL_BUSINESS_DB_ENV_KEYS = (
    "DB_DATABASE",
    "DEV_DB_DATABASE",
    "STG_DB_DATABASE",
    "STG_DB_DATA",
    "LOCAL_DEV_DB_DATABASE",
    "LOCAL_DEV_DB_DATA",
    "PROD_DB_DATABASE",
)

MYSQL_DEFAULT_BUSINESS_DB_NAMES = {
    "snowball",
    "snowball_data",
    "snowball_dev",
    "snowball_data_dev",
    "snowball_stg",
    "snowball_data_stg",
}


def uses_mysql_test_fixtures(fixturenames: Iterable[str]) -> bool:
    return bool(MYSQL_FIXTURE_NAMES.intersection(fixturenames))


def mysql_business_db_names() -> set[str]:
    names = set(MYSQL_DEFAULT_BUSINESS_DB_NAMES)
    names.update(
        value.strip()
        for key in MYSQL_BUSINESS_DB_ENV_KEYS
        if (value := os.environ.get(key))
    )
    return {name for name in names if name}


def validate_mysql_test_database_names(test_db_name: str, data_db_name: str) -> None:
    business_names = {name.lower() for name in mysql_business_db_names()}
    candidates = {
        "TEST_DB_TESTDB": test_db_name.strip(),
        "TEST_DB_DATABASE": data_db_name.strip(),
    }

    for env_name, db_name in candidates.items():
        normalized_name = db_name.lower()

        if "_test" not in normalized_name:
            raise ValueError(f"{env_name} 必须包含 _test，不能指向业务库")

        if normalized_name in business_names:
            raise ValueError(f"{env_name} 不能指向业务库 {db_name}")


def should_run_mysql_integration(markexpr: str | None) -> bool:
    if not markexpr:
        return False

    normalized = " ".join(markexpr.lower().split())
    if MYSQL_INTEGRATION_MARK not in normalized:
        return False

    has_positive_match = re.search(
        rf"(^|[\s(]){MYSQL_INTEGRATION_MARK}(?=$|[\s)])",
        normalized,
    )
    has_negative_only_match = re.search(
        rf"(^|[\s(])not\s+{MYSQL_INTEGRATION_MARK}(?=$|[\s)])",
        normalized,
    )
    return bool(has_positive_match and not has_negative_only_match)
