# -*- coding: UTF-8 -*-
"""
@File    ：scheduler_service.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/10/9 15:21
"""
from sqlalchemy import func

from web.models import db
from web.models.scheduler.scheduler_job_state import SchedulerJobState
from web.models.scheduler.scheduler_log import SchedulerLog


class SchedulerService:

    def get_job_counts(self, state):
        """
        获取指定状态下的任务数量。

        Args:
            state: 任务的执行状态，字符串类型。

        Returns:
            返回一个包含两个元素的元组列表，每个元组包含任务的ID和对应状态下的任务数量。

        """
        return db.session.query(SchedulerLog.job_id, func.count(SchedulerLog.id).label('count')) \
            .filter(SchedulerLog.execution_state == state) \
            .group_by(SchedulerLog.job_id) \
            .all()

    def get_job_states_by_ids(self, job_ids: list[str]):
        if not job_ids:
            return []
        return (
            db.session.query(SchedulerJobState)
            .filter(SchedulerJobState.job_id.in_(job_ids))
            .all()
        )

    def get_job_state(self, job_id: str):
        if not job_id:
            return None
        return (
            db.session.query(SchedulerJobState)
            .filter(SchedulerJobState.job_id == job_id)
            .first()
        )

    def get_latest_job_log(self, job_id: str):
        if not job_id:
            return None
        return (
            db.session.query(SchedulerLog)
            .filter(SchedulerLog.job_id == job_id)
            .order_by(
                SchedulerLog.scheduler_run_time.desc(),
                SchedulerLog.execution_state.desc(),
            )
            .first()
        )

    def get_latest_job_logs_by_ids(self, job_ids: list[str]):
        if not job_ids:
            return []
        ranked_logs = (
            db.session.query(
                SchedulerLog.id.label("id"),
                SchedulerLog.job_id.label("job_id"),
                SchedulerLog.execution_state.label("execution_state"),
                SchedulerLog.scheduler_run_time.label("scheduler_run_time"),
                SchedulerLog.exception.label("exception"),
                SchedulerLog.traceback.label("traceback"),
                SchedulerLog.create_time.label("create_time"),
                SchedulerLog.update_time.label("update_time"),
                func.row_number()
                .over(
                    partition_by=SchedulerLog.job_id,
                    order_by=(
                        SchedulerLog.scheduler_run_time.desc(),
                        SchedulerLog.execution_state.desc(),
                        SchedulerLog.id.desc(),
                    ),
                )
                .label("row_number"),
            )
            .filter(SchedulerLog.job_id.in_(job_ids))
            .subquery()
        )
        return (
            db.session.query(ranked_logs)
            .filter(ranked_logs.c.row_number == 1)
            .all()
        )


scheduler_service = SchedulerService()
