from __future__ import annotations

import base64
import uuid

MANUAL_JOB_ID_PREFIX = "manual::"


def _encode_job_id(job_id: str) -> str:
    encoded = base64.urlsafe_b64encode(job_id.encode("utf-8")).decode("ascii")
    return encoded.rstrip("=")


def _decode_job_id(encoded_job_id: str) -> str:
    padding = "=" * (-len(encoded_job_id) % 4)
    return base64.urlsafe_b64decode(f"{encoded_job_id}{padding}").decode("utf-8")


def build_manual_job_id(original_job_id: str, run_id: str | None = None) -> str:
    if not original_job_id:
        raise ValueError("original_job_id is required")

    manual_run_id = run_id or uuid.uuid4().hex
    return f"{MANUAL_JOB_ID_PREFIX}{manual_run_id}::{_encode_job_id(original_job_id)}"


def decode_manual_job_id(job_id: str) -> str | None:
    if not isinstance(job_id, str) or not job_id.startswith(MANUAL_JOB_ID_PREFIX):
        return None

    parts = job_id.split("::", 2)
    if len(parts) != 3:
        return None

    _, manual_run_id, encoded_job_id = parts
    if not manual_run_id or not encoded_job_id:
        return None

    try:
        return _decode_job_id(encoded_job_id)
    except Exception:
        return None
