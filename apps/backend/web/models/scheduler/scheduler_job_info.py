from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from apscheduler.job import Job
from flask_marshmallow import Schema
from marshmallow import fields


@dataclass
class SchedulerJobInfo:
    job_id: int | None = None
    name: str | None = None
    func: str | None = None
    args: list | None = None
    kwargs: dict | None = None
    trigger: str | None = None
    next_run_time: datetime | None = None

    @staticmethod
    def from_apscheduler_job_list(jobs: list[Job]):
        scheduler_job_list = []
        for job in jobs:
            scheduler_job = SchedulerJobInfo()
            scheduler_job.job_id = getattr(job, 'id', None)
            scheduler_job.kwargs = getattr(job, 'kwargs', {})
            scheduler_job.func = getattr(job, 'func_ref', None)
            scheduler_job.next_run_time = getattr(job, 'next_run_time', None)
            trigger = getattr(job, 'trigger', None)
            scheduler_job.trigger = str(trigger) if trigger else None
            scheduler_job.name = getattr(job, 'name', None)
            scheduler_job_list.append(scheduler_job)
        return scheduler_job_list


class SchedulerJobInfoSchema(Schema):
    job_id = fields.String()
    name = fields.String()
    func = fields.String()
    args = fields.List(fields.String())
    kwargs = fields.Dict()
    trigger = fields.String()
    next_run_time = fields.DateTime()

