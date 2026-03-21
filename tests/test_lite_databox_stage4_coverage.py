from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
import pytest
from flask import current_app

from web import create_app
from web.databox.adapter.data.xa_data_adapter import XaDataAdapter
from web.databox.data_box import DataBox
from web.lite_validation import get_fundinfo_cache_file

pytestmark = [pytest.mark.local, pytest.mark.usefixtures("lite_runtime_paths")]


def _make_fundinfo_payload():
    return SimpleNamespace(
        price=pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                "netvalue": [1.01, 1.02],
                "totvalue": [1.01, 1.02],
                "comment": [0, 0],
            }
        ),
        rate=0.15,
        feeinfo={"buy": 0.0, "sell": 0.0},
    )


def test_lite_databox_fund_info_writes_and_reuses_csv_cache(monkeypatch, tmp_path):
    monkeypatch.setenv("LITE_DB_PATH", str(tmp_path / "pytest-snowball-lite.db"))
    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", str(tmp_path / "pytest-lite_xalpha_cache"))
    monkeypatch.setenv("LITE_XALPHA_CACHE_BACKEND", "csv")
    app = create_app("lite")

    with app.app_context():
        data_box = DataBox()
        cache_file = get_fundinfo_cache_file(
            current_app.config["XALPHA_CACHE_DIR"],
            "000001",
        )
        cache_file.unlink(missing_ok=True)

        cache_file.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            [
                {
                    "comment": 0,
                    "date": json.dumps(
                        {
                            "feeinfo": {"buy": 0.0, "sell": 0.0},
                            "name": "测试基金",
                            "rate": 0.15,
                            "segment": [],
                        }
                    ),
                    "netvalue": 0.0,
                    "totvalue": 0.0,
                },
                {
                    "comment": 0,
                    "date": "2024-01-01 00:00:00",
                    "netvalue": 1.01,
                    "totvalue": 1.01,
                },
                {
                    "comment": 0,
                    "date": "2024-01-02 00:00:00",
                    "netvalue": 1.02,
                    "totvalue": 1.02,
                },
            ]
        ).to_csv(cache_file, index=False)

        with patch("xalpha.cons.rget_json", side_effect=AssertionError("cached CSV should short-circuit network access")):
            first_fund = data_box.fund_info("000001")

        assert first_fund is not None
        assert cache_file.exists()
        assert not first_fund.price.empty
        assert first_fund.rate == 0.15
        assert first_fund.fee_info == {"buy": 0.0, "sell": 0.0}

        with patch("xalpha.cons.rget_json", side_effect=AssertionError("cached CSV should short-circuit network access")):
            second_fund = data_box.fund_info("000001")

        assert second_fund is not None
        assert len(second_fund.price) == len(first_fund.price)
        assert second_fund.rate == first_fund.rate
        assert second_fund.fee_info == first_fund.fee_info


def test_lite_xa_data_adapter_get_daily_reuses_fundinfo_cache_for_same_range():
    app = create_app("lite")

    with app.app_context():
        adapter = XaDataAdapter(code_ttjj="000001", code_xq=None)
        adapter.init_adapter({"xq_a_token": "token", "u": "1"})

        payload = _make_fundinfo_payload()
        with patch.object(adapter, "fundinfo", return_value=payload) as fundinfo_call:
            first_daily = adapter.get_daily(
                start_date=pd.Timestamp("2024-01-01"),
                end_date=pd.Timestamp("2024-01-02"),
            )
            second_daily = adapter.get_daily(
                start_date=pd.Timestamp("2024-01-01"),
                end_date=pd.Timestamp("2024-01-02"),
            )

        assert fundinfo_call.call_count == 1
        assert len(first_daily) == 2
        assert len(second_daily) == 2
