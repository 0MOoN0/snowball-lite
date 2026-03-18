# -*- coding: UTF-8 -*-
"""
@File    ：scheduler_service.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/10/9 15:21
"""
from sqlalchemy import func

from web.models import db
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


scheduler_service = SchedulerService()
