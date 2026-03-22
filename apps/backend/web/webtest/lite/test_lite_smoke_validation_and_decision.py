from __future__ import annotations

from unittest.mock import patch

import pytest

from web.models import db
from web.models.asset.asset import Asset
from web.models.asset.asset_alias import AssetAlias
from web.models.record.record import Record

pytestmark = [pytest.mark.local, pytest.mark.integration]


def _seed_asset(asset_name: str = "Lite 冒烟资产") -> int:
    asset = Asset(
        asset_name=asset_name,
        asset_type=2,
        asset_status=0,
        currency=0,
        market=0,
    )
    db.session.add(asset)
    db.session.flush()

    db.session.add(
        AssetAlias(
            asset_id=asset.id,
            provider_code="manual",
            provider_symbol="SH600000",
            provider_name="manual",
            is_primary=True,
            status=1,
        )
    )
    db.session.commit()
    return asset.id


def test_lite_asset_list_smoke_returns_pagination_and_seeded_asset(lite_app):
    with lite_app.app_context():
        _seed_asset()

    client = lite_app.test_client()
    response = client.get("/api/asset/list/?page=1&pageSize=20&assetName=Lite")

    assert response.status_code == 200
    payload = response.get_json()

    assert payload["success"] is True
    assert payload["message"] == "查询成功"
    assert payload["data"]["total"] == 1
    assert payload["data"]["page"] == 1
    assert payload["data"]["size"] == 20
    assert payload["data"]["items"][0]["assetName"] == "Lite 冒烟资产"
    assert payload["data"]["items"][0]["assetCode"] == "SH600000"


def test_lite_record_smoke_persists_and_reads_record(lite_app):
    with lite_app.app_context():
        asset_id = _seed_asset(asset_name="记录冒烟资产")

    client = lite_app.test_client()
    create_response = client.post(
        "/api/record",
        json={
            "assetId": asset_id,
            "transactionsShare": 100,
            "transactionsPrice": 1234,
            "transactionsFee": 5,
            "transactionsDirection": 1,
            "transactionsDate": "2024-01-02 10:00:00",
        },
    )

    assert create_response.status_code == 200
    assert create_response.get_json()["success"] is True

    with lite_app.app_context():
        record = Record.query.one()
        record_id = record.id
        assert record.asset_id == asset_id
        assert record.transactions_amount == 123400

    detail_response = client.get(f"/api/record/{record_id}")

    assert detail_response.status_code == 200
    payload = detail_response.get_json()

    assert payload["success"] is True
    assert payload["data"]["recordId"] == record_id
    assert payload["data"]["assetId"] == asset_id
    assert payload["data"]["assetName"] == "记录冒烟资产"
    assert payload["data"]["transactionsAmount"] == "123400"
    assert payload["data"]["transactionsDate"] == "2024-01-02 10:00:00"


def test_lite_token_test_smoke_traverses_databox_runtime_path(lite_app):
    client = lite_app.test_client()

    with patch(
        "web.databox.adapter.data.xa_data_adapter.xa.get_rt",
        return_value={
            "name": "Lite Smoke Asset",
            "current": 1.23,
            "market": None,
            "currency": None,
        },
    ) as mock_xalpha_get_rt:
        response = client.get("/token_test/result")

    assert response.status_code == 200
    assert response.get_json() == {
        "code": 20000,
        "data": True,
        "message": "成功",
        "success": True,
    }
    mock_xalpha_get_rt.assert_called_once_with(code="SH501018")
