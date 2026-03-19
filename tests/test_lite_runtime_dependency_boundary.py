from __future__ import annotations

import pytest


pytestmark = [pytest.mark.local, pytest.mark.integration]


def test_lite_system_token_route_returns_explicit_redis_boundary(lite_app):
    client = lite_app.test_client()

    get_response = client.get("/system/token")
    put_response = client.put(
        "/system/token",
        json={
            "xq_a_token": "token",
            "u": "u",
            "serverchen_sendkey": "sendkey",
        },
    )

    assert get_response.status_code == 200
    assert put_response.status_code == 200
    assert get_response.get_json()["success"] is False
    assert put_response.get_json()["success"] is False
    assert "lite 模式下不支持系统 token" in get_response.get_json()["message"]
    assert "lite 模式下不支持系统 token" in put_response.get_json()["message"]


def test_lite_enum_versions_route_returns_explicit_redis_boundary(lite_app):
    client = lite_app.test_client()

    response = client.get("/api/enums/versions")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is False
    assert "lite 模式下不支持枚举版本" in payload["message"]
