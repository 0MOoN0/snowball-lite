from __future__ import annotations

from unittest.mock import patch

import pytest

from web.common.enum.asset_enum import AssetCurrencyEnum, AssetTypeEnum
from web.models.asset.asset import Asset
from web.models.asset.asset_code import AssetCode


pytestmark = [pytest.mark.local, pytest.mark.integration]


@patch("web.services.asset.asset_service.asset_service.init_fund_asset_data")
@patch("web.task.actors.AssetActors.init_asset.send_with_options")
def test_lite_asset_create_runs_sync_init_without_actor(
    mock_send_with_options,
    mock_init_fund_asset_data,
    lite_app,
):
    client = lite_app.test_client()

    response = client.post(
        "/asset/",
        json={
            "assetName": "Lite Asset Init",
            "currency": AssetCurrencyEnum.CNY.value,
            "assetType": AssetTypeEnum.FUND.value,
            "codeTTJJ": "990001",
            "codeXQ": "SH990001",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True

    mock_init_fund_asset_data.assert_called_once()
    mock_send_with_options.assert_not_called()

    asset_code = mock_init_fund_asset_data.call_args.args[0]
    assert isinstance(asset_code, AssetCode)
    assert asset_code.code_ttjj == "990001"
    assert asset_code.code_xq == "SH990001"

    with lite_app.app_context():
        assert Asset.query.filter_by(asset_name="Lite Asset Init").count() == 1
        assert AssetCode.query.filter_by(code_ttjj="990001").count() == 1
