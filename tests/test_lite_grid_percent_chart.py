from __future__ import annotations

import pytest


pytestmark = [pytest.mark.local, pytest.mark.integration]


def test_grid_percent_chart_returns_success_when_no_analysis_data(lite_app):
    client = lite_app.test_client()

    response = client.get("/charts/grid/percent")

    assert response.status_code == 200

    result = response.get_json()
    assert result["code"] == 20000
    assert result["success"] is True
