from __future__ import annotations

import pytest

from web.webtest.mysql_test_guard import (
    mysql_business_db_names,
    should_run_mysql_integration,
    uses_mysql_test_fixtures,
    validate_mysql_test_database_names,
)


def test_uses_mysql_test_fixtures_detects_legacy_webtest_entrypoints():
    assert uses_mysql_test_fixtures(["rollback_session"])
    assert uses_mysql_test_fixtures(["client", "mocker"])
    assert not uses_mysql_test_fixtures(["lite_webtest_app", "lite_rollback_session"])


def test_validate_mysql_test_database_names_rejects_business_database_names(monkeypatch):
    monkeypatch.setenv("PROD_DB_DATABASE", "snowball")

    with pytest.raises(ValueError, match="不能指向业务库"):
        validate_mysql_test_database_names("snowball", "snowball_data_test")

    with pytest.raises(ValueError, match="不能指向业务库"):
        validate_mysql_test_database_names("snowball_test", "snowball_data")


def test_validate_mysql_test_database_names_requires_test_suffix():
    with pytest.raises(ValueError, match="必须包含 _test"):
        validate_mysql_test_database_names("snowball_ci", "snowball_data_test")


def test_mysql_business_db_names_collects_runtime_overrides(monkeypatch):
    monkeypatch.setenv("LOCAL_DEV_DB_DATABASE", "snowball_local")

    assert "snowball_local" in mysql_business_db_names()


def test_should_run_mysql_integration_only_on_explicit_request():
    assert not should_run_mysql_integration(None)
    assert not should_run_mysql_integration("integration and not manual")
    assert not should_run_mysql_integration("not mysql_integration")
    assert should_run_mysql_integration("mysql_integration")
    assert should_run_mysql_integration("mysql_integration and not manual")
