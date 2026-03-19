from __future__ import annotations

from pathlib import Path


REAL_DATABOX_EXTERNAL_ENV = "external_env"
REAL_DATABOX_CODE = "code"

_EXTERNAL_ENV_KEYWORDS = (
    "timed out",
    "timeout",
    "temporarily unavailable",
    "temporary failure",
    "name or service not known",
    "connection refused",
    "connection aborted",
    "connection reset",
    "remote disconnected",
    "proxyerror",
    "ssl",
    "certificate",
    "network is unreachable",
    "max retries exceeded",
    "eastmoney",
)


def classify_real_databox_failure(exc: BaseException) -> str:
    module_name = getattr(exc.__class__, "__module__", "")
    message = f"{exc.__class__.__name__}: {exc}".lower()

    if module_name.startswith(("requests", "urllib3", "httpx")):
        return REAL_DATABOX_EXTERNAL_ENV

    if any(keyword in message for keyword in _EXTERNAL_ENV_KEYWORDS):
        return REAL_DATABOX_EXTERNAL_ENV

    return REAL_DATABOX_CODE


def get_fundinfo_cache_file(cache_dir: str | Path, code: str) -> Path:
    return Path(cache_dir) / f"INFO-{code}.csv"
