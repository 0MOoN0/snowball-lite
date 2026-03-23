from __future__ import annotations

import json

import pytest
from unittest.mock import patch

from web.common.enum.version_enum import VersionKeyEnum
from web.models.setting.system_settings import Setting


pytestmark = [pytest.mark.local, pytest.mark.integration]


def test_lite_system_token_route_persists_to_sqlite(lite_app):
    client = lite_app.test_client()

    put_payload = {
        "xq_a_token": "token",
        "u": "u",
        "serverchen_sendkey": "sendkey",
    }

    put_response = client.put(
        "/system/token",
        json=put_payload,
    )
    get_response = client.get("/system/token")

    assert put_response.status_code == 200
    assert get_response.status_code == 200
    assert put_response.get_json()["success"] is True
    assert get_response.get_json()["success"] is True
    assert get_response.get_json()["data"] == put_payload

    with lite_app.app_context():
        xq_token_setting = Setting.query.filter_by(key="XQ_TOKEN").one()
        sendkey_setting = Setting.query.filter_by(key="SERVERCHAN_SENDKEY").one()

    assert json.loads(xq_token_setting.value) == {
        "xq_a_token": "token",
        "u": "u",
    }
    assert sendkey_setting.value == "sendkey"


def test_lite_enum_versions_route_reads_from_sqlite(lite_app):
    client = lite_app.test_client()

    with lite_app.app_context():
        enum_version_setting = Setting.query.filter_by(
            key=VersionKeyEnum.ENUM.value
        ).one()
        expected_payload = json.loads(enum_version_setting.value)

    response = client.get("/api/enums/versions")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["message"] == "获取枚举版本成功"
    assert payload["data"] == expected_payload
    assert isinstance(payload["data"]["global"], int)


def test_lite_system_token_refresh_route_fetches_and_persists_to_sqlite(lite_app):
    client = lite_app.test_client()

    with patch(
        "web.routers.system.system_data_routers.xueqiu_token_service.fetch_xq_token",
        return_value={"xq_a_token": "auto-token", "u": "auto-user"},
    ):
        response = client.post("/system/token/refresh")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["message"] == "自动获取雪球 token 成功"
    assert payload["data"]["xq_a_token"] == "auto-token"
    assert payload["data"]["u"] == "auto-user"
    assert payload["data"]["serverchen_sendkey"] is None

    with lite_app.app_context():
        xq_token_setting = Setting.query.filter_by(key="XQ_TOKEN").one()

    assert json.loads(xq_token_setting.value) == {
        "xq_a_token": "auto-token",
        "u": "auto-user",
    }


def test_lite_system_token_refresh_route_keeps_existing_sendkey(lite_app):
    client = lite_app.test_client()

    client.put(
        "/system/token",
        json={
            "xq_a_token": "manual-token",
            "u": "manual-user",
            "serverchen_sendkey": "sendkey",
        },
    )

    with patch(
        "web.routers.system.system_data_routers.xueqiu_token_service.fetch_xq_token",
        return_value={"xq_a_token": "refreshed-token", "u": "refreshed-user"},
    ):
        response = client.post("/system/token/refresh")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"] == {
        "xq_a_token": "refreshed-token",
        "u": "refreshed-user",
        "serverchen_sendkey": "sendkey",
    }
