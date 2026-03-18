from __future__ import annotations

import json
import threading
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import xalpha as xa
from sqlalchemy import create_engine

from web import create_app, models
from web.common.cons import webcons
from web.databox.base import databox as global_databox
from web.databox.data_box import DataBox
from web.databox.adapter.data.xa_data_adapter import XaDataAdapter
from web.databox.adapter.data.xa_service import XaServiceAdapter
from xalpha.info import fundinfo as fundinfo_cls
from xalpha.universal import cachedio


@pytest.fixture(autouse=True)
def _lite_runtime_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("LITE_DB_PATH", str(tmp_path / "snowball_lite.db"))
    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", str(tmp_path / "lite_xalpha_cache"))
    monkeypatch.setenv("LITE_XALPHA_CACHE_BACKEND", "csv")
    yield


def test_cachedio_sql_backend_bootstraps_missing_sqlite_table(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'xalpha_cache.db'}")
    calls = {"count": 0}

    @cachedio(backend="sql", path=engine)
    def fetch(code, start=None, end=None):
        calls["count"] += 1
        return pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                "close": [1.01, 1.02],
            }
        )

    try:
        first = fetch("demo_daily", start="20240101", end="20240102")
        second = fetch("demo_daily", start="20240101", end="20240102")

        assert calls["count"] == 1
        pd.testing.assert_frame_equal(
            first.reset_index(drop=True),
            second.reset_index(drop=True),
            check_dtype=False,
        )
    finally:
        engine.dispose()


def test_fundinfo_sql_backend_reads_existing_sqlite_cache(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'fundinfo_cache.db'}")
    cache_table = pd.DataFrame(
        [
            {
                "date": "1990-01-01",
                "netvalue": 0,
                "comment": json.dumps(
                    {
                        "feeinfo": ["buy"],
                        "name": "测试基金",
                        "rate": 0.15,
                        "segment": [],
                    }
                ),
                "totvalue": 0,
            },
            {
                "date": "2024-01-01",
                "netvalue": 1.01,
                "comment": 0,
                "totvalue": 1.01,
            },
            {
                "date": "2024-01-02",
                "netvalue": 1.02,
                "comment": 0,
                "totvalue": 1.02,
            },
        ]
    )
    cache_table.to_sql("xa000001", engine, if_exists="replace", index=False)

    try:
        with patch.object(
            fundinfo_cls,
            "_basic_init",
            side_effect=AssertionError("should read from sqlite cache instead of falling back"),
        ), patch.object(fundinfo_cls, "update", return_value=None):
            fund = xa.fundinfo("000001", fetch=True, save=False, path=engine, form="sql")

        assert fund.name == "测试基金"
        assert len(fund.price) == 2
        assert pd.api.types.is_datetime64_any_dtype(fund.price["date"])
        assert list(fund.price["netvalue"]) == [1.01, 1.02]
    finally:
        engine.dispose()


def test_lite_xa_service_adapter_prefers_csv_cache_backend(tmp_path):
    app = create_app("lite")
    cache_dir = (tmp_path / "lite_xalpha_cache").resolve()
    app.config["XALPHA_CACHE_BACKEND"] = "csv"
    app.config["XALPHA_CACHE_DIR"] = str(cache_dir)

    with app.app_context():
        fake_xa = patch("web.databox.adapter.data.xa_service.xa").start()
        try:
            adapter = XaServiceAdapter()
            adapter.xa = fake_xa

            adapter.init_adapter({"xq_a_token": "token", "u": "1"})

            fake_xa.universal.set_token.assert_called_once_with(
                {"xq_a_token": "token", "u": "1"}
            )
            backend_kwargs = fake_xa.set_backend.call_args.kwargs
            assert backend_kwargs["backend"] == "csv"
            assert backend_kwargs["path"] == str(cache_dir)
            assert adapter.fund_info_db_setting == {
                "save": True,
                "fetch": True,
                "form": "csv",
                "path": str(cache_dir / "INFO-"),
            }
        finally:
            patch.stopall()


def test_lite_databox_fund_info_uses_configured_cache_backend():
    app = create_app("lite")

    with app.app_context():
        data_box = DataBox()

        with patch(
            "web.databox.adapter.data.xa_service.xa.fundinfo",
            return_value=SimpleNamespace(
                price=pd.DataFrame(),
                rate=0.15,
                feeinfo=["buy"],
            ),
        ) as mock_fundinfo:
            fund = data_box.fund_info("000001")

        assert fund is not None
        assert mock_fundinfo.call_args.args == ("000001",)
        assert mock_fundinfo.call_args.kwargs == {
            "save": True,
            "fetch": True,
            "form": "csv",
            "path": app.config["XALPHA_CACHE_DIR"] + "/INFO-",
        }


def test_lite_xa_data_adapter_get_daily_uses_configured_cache_backend():
    app = create_app("lite")

    with app.app_context():
        adapter = XaDataAdapter(code_ttjj="000001")
        adapter.init_adapter({"xq_a_token": "token", "u": "1"})

        with patch(
            "web.databox.adapter.data.xa_data_adapter.xa.fundinfo",
            return_value=SimpleNamespace(
                price=pd.DataFrame(
                    {
                        "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
                        "netvalue": [1.01, 1.02],
                        "totvalue": [1.01, 1.02],
                        "comment": [0, 0],
                    }
                )
            ),
        ) as mock_fundinfo:
            result = adapter.get_daily(
                start_date=pd.Timestamp("2024-01-01"),
                end_date=pd.Timestamp("2024-01-02"),
            )

        assert len(result) == 2
        assert mock_fundinfo.call_args.kwargs == {
            "code": "000001",
            "save": True,
            "fetch": True,
            "form": "csv",
            "path": app.config["XALPHA_CACHE_DIR"] + "/INFO-",
        }


def test_global_databox_refreshes_cache_backend_between_lite_apps(
    monkeypatch, tmp_path
):
    cache_one = str((tmp_path / "cache-one").resolve())
    cache_two = str((tmp_path / "cache-two").resolve())
    original_local = dict(global_databox.xa_service.fund_info_db_setting)
    original_global = dict(webcons.XaFundInfoSetting.DB_SETTING)

    try:
        global_databox.xa_service.fund_info_db_setting = {}

        monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", cache_one)
        app_one = create_app("lite")
        with app_one.app_context():
            with patch(
                "web.databox.adapter.data.xa_service.xa.fundinfo",
                return_value=SimpleNamespace(
                    price=pd.DataFrame(),
                    rate=0.15,
                    feeinfo=["buy"],
                ),
            ) as first_call:
                global_databox.fund_info("000001")

            assert first_call.call_args.kwargs["path"] == cache_one + "/INFO-"

        monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", cache_two)
        app_two = create_app("lite")
        with app_two.app_context():
            with patch(
                "web.databox.adapter.data.xa_service.xa.fundinfo",
                return_value=SimpleNamespace(
                    price=pd.DataFrame(),
                    rate=0.15,
                    feeinfo=["buy"],
                ),
            ) as second_call:
                global_databox.fund_info("000001")

            assert second_call.call_args.kwargs["path"] == cache_two + "/INFO-"
    finally:
        global_databox.xa_service.fund_info_db_setting = original_local
        webcons.XaFundInfoSetting.DB_SETTING = original_global


def test_disable_xalpha_sql_cache_forces_memory_backend():
    app = create_app("lite")
    app.config["ENABLE_XALPHA_SQL_CACHE"] = False
    app.config["XALPHA_CACHE_BACKEND"] = "sql"

    with app.app_context():
        fake_xa = Mock()

        cache_settings = webcons.apply_xalpha_cache_settings(
            fake_xa,
            default_engine=object(),
        )

        assert cache_settings["backend_name"] == "memory"
        assert fake_xa.set_backend.call_args.kwargs["backend"] == "memory"


def test_lite_xa_service_get_daily_refreshes_backend_between_lite_apps(
    monkeypatch, tmp_path
):
    cache_one = str((tmp_path / "daily-cache-one").resolve())
    cache_two = str((tmp_path / "daily-cache-two").resolve())

    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", cache_one)
    app_one = create_app("lite")

    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", cache_two)
    app_two = create_app("lite")

    adapter = XaServiceAdapter()

    with app_two.app_context(), patch.object(
        adapter,
        "execute_xa",
        return_value=pd.DataFrame(),
    ):
        adapter.get_daily("SZ000001")
        assert xa.universal.ioconf["path"] == cache_two

    with app_one.app_context(), patch.object(
        adapter,
        "execute_xa",
        return_value=pd.DataFrame(),
    ):
        adapter.get_daily("SZ000001")
        assert xa.universal.ioconf["path"] == cache_one


def test_cachedio_invalid_backend_fails_fast():
    @cachedio(backend="bogus", path="unused")
    def fetch(code, start=None, end=None):
        return pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-01"]),
                "close": [1.0],
            }
        )

    with pytest.raises(ValueError, match="no bogus option for backend"):
        fetch("demo", start="20240101", end="20240101")


def test_lite_xa_service_get_daily_serializes_backend_refresh(
    monkeypatch, tmp_path
):
    cache_one = str((tmp_path / "race-cache-one").resolve())
    cache_two = str((tmp_path / "race-cache-two").resolve())

    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", cache_one)
    app_one = create_app("lite")

    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", cache_two)
    app_two = create_app("lite")

    adapter = XaServiceAdapter()
    first_entered = threading.Event()
    allow_first_finish = threading.Event()
    second_entered = threading.Event()
    results = {}
    errors = []

    def fake_execute_xa(callable_name=None, *args, **kwargs):
        thread_name = threading.current_thread().name
        if thread_name == "app-one-thread":
            first_entered.set()
            assert allow_first_finish.wait(timeout=5)
        else:
            second_entered.set()

        results[thread_name] = xa.universal.ioconf["path"]
        return pd.DataFrame()

    adapter.execute_xa = fake_execute_xa

    def run_in_app(name, app):
        try:
            with app.app_context():
                adapter.get_daily("SZ000001")
        except Exception as exc:  # pragma: no cover - test failure path
            errors.append(exc)

    first_thread = threading.Thread(
        target=run_in_app,
        args=("app-one-thread", app_one),
        name="app-one-thread",
    )
    second_thread = threading.Thread(
        target=run_in_app,
        args=("app-two-thread", app_two),
        name="app-two-thread",
    )

    first_thread.start()
    assert first_entered.wait(timeout=5)

    second_thread.start()
    assert not second_entered.wait(timeout=0.5)

    allow_first_finish.set()
    first_thread.join(timeout=5)
    second_thread.join(timeout=5)

    assert not errors
    assert not first_thread.is_alive()
    assert not second_thread.is_alive()
    assert results == {
        "app-one-thread": cache_one,
        "app-two-thread": cache_two,
    }


def test_apply_xalpha_cache_settings_serializes_with_get_daily_scope(
    monkeypatch, tmp_path
):
    cache_one = str((tmp_path / "lock-gap-cache-one").resolve())
    cache_two = str((tmp_path / "lock-gap-cache-two").resolve())

    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", cache_one)
    app_one = create_app("lite")

    monkeypatch.setenv("LITE_XALPHA_CACHE_DIR", cache_two)
    app_two = create_app("lite")

    adapter = XaServiceAdapter()
    first_entered = threading.Event()
    allow_first_finish = threading.Event()
    second_applied = threading.Event()
    results = {}
    errors = []

    def fake_execute_xa(callable_name=None, *args, **kwargs):
        first_entered.set()
        assert allow_first_finish.wait(timeout=5)
        results["path_seen"] = xa.universal.ioconf["path"]
        return pd.DataFrame()

    adapter.execute_xa = fake_execute_xa

    def run_get_daily():
        try:
            with app_one.app_context():
                adapter.get_daily("SZ000001")
        except Exception as exc:  # pragma: no cover - test failure path
            errors.append(exc)

    def run_apply():
        try:
            with app_two.app_context():
                webcons.apply_xalpha_cache_settings(
                    xa,
                    default_engine=models.db.engine,
                )
                results["path_after_apply"] = xa.universal.ioconf["path"]
                second_applied.set()
        except Exception as exc:  # pragma: no cover - test failure path
            errors.append(exc)

    first_thread = threading.Thread(target=run_get_daily, name="app-one-thread")
    second_thread = threading.Thread(target=run_apply, name="app-two-thread")

    first_thread.start()
    assert first_entered.wait(timeout=5)

    second_thread.start()
    assert not second_applied.wait(timeout=0.5)

    allow_first_finish.set()
    first_thread.join(timeout=5)
    second_thread.join(timeout=5)

    assert not errors
    assert not first_thread.is_alive()
    assert not second_thread.is_alive()
    assert results == {
        "path_seen": cache_one,
        "path_after_apply": cache_two,
    }
