from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pytest
from flask import current_app

from web.databox.data_box import DataBox
from web.lite_validation import (
    REAL_DATABOX_CODE,
    REAL_DATABOX_EXTERNAL_ENV,
    classify_real_databox_failure,
    get_fundinfo_cache_file,
)

_ENABLE_ENV = "LITE_RUN_REAL_DATABOX"


def test_classify_real_databox_failure_distinguishes_external_env_errors():
    exc = RuntimeError("HTTPSConnectionPool(host='fund.eastmoney.com'): Read timed out")

    assert classify_real_databox_failure(exc) == REAL_DATABOX_EXTERNAL_ENV


def test_classify_real_databox_failure_keeps_code_errors_separate():
    exc = TypeError("unexpected response payload")

    assert classify_real_databox_failure(exc) == REAL_DATABOX_CODE


def test_get_fundinfo_cache_file_uses_lite_cache_prefix():
    cache_file = get_fundinfo_cache_file("/tmp/lite-cache", "000001")

    assert cache_file == Path("/tmp/lite-cache/INFO-000001.csv")


@pytest.mark.manual
@pytest.mark.integration
def test_lite_real_databox_fund_info_chain_writes_default_sqlite_cache(lite_app):
    if os.environ.get(_ENABLE_ENV) != "1":
        pytest.skip(f"需要显式设置 {_ENABLE_ENV}=1 才执行真实 DataBox 验证")

    with lite_app.app_context():
        data_box = DataBox()
        cache_file = Path(current_app.config["XALPHA_CACHE_SQLITE_PATH"])
        assert not cache_file.exists()

        try:
            fund = data_box.fund_info("000001")
            data_box.xa_adapter.code_ttjj = "000001"
            daily = data_box.xa_adapter.get_daily(
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 1, 5),
            )
        except Exception as exc:  # pragma: no cover - 真实链路只在人工验收时触发
            failure_kind = classify_real_databox_failure(exc)
            if failure_kind == REAL_DATABOX_EXTERNAL_ENV:
                pytest.skip(f"第三方环境问题，跳过真实链路验收：{exc}")
            raise

        assert fund is not None
        assert fund.rate is not None
        assert not fund.price.empty
        assert cache_file.exists()
        assert len(daily) >= 1

        second_fund = data_box.fund_info("000001")
        assert second_fund is not None
        assert len(second_fund.price) == len(fund.price)
