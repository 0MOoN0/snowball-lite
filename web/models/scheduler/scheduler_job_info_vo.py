from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class SchedulerJobInfo:
    id: int | None = None
    name: str | None = None
    func: str | None = None
    args: list | None = None
    kwargs: dict | None = None
    trigger: str | None = None
    next_run_time: datetime | None = None
