# -*- coding: UTF-8 -*-
"""
@File    ：scheduler_job_log_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/2/16 11:24
"""
from flask import Blueprint
from flask_restful import Resource, Api

from web.common.utils import R
from web.models.scheduler.scheduler_log import SchedulerLog, SchedulerLogVOSchema
from web.weblogger import debug

scheduler_job_log_bp = Blueprint("scheduler_job_log_list", __name__, url_prefix="/scheduler/job_log")
scheduler_job_log_api = Api(scheduler_job_log_bp)


class SchedulerJobLogRouters(Resource):

    def get(self, job_id: str):
        """
        @@@
        根据任务ID获取最新的任务执行日志信息。

        该方法通过查询数据库中与给定任务ID相关联的最新日志条目，来获取任务的执行信息，并以HTTP响应的形式返回。

        Args:
        - job_id (str): 任务的唯一标识符，用于查询特定任务的执行日志。

        Returns:
        - R.ok(data=SchedulerLogSchema().dump(latest_log)): 返回一个HTTP响应对象，包含序列化的最新任务执行日志信息。
          如果没有找到相关日志，将返回一个空的数据结构。
        @@@
        """
        # 记录日志
        debug(f'根据任务ID获取最新的任务执行日志信息，参数：{job_id}')
        latest_log: SchedulerLog = SchedulerLog.query.order_by(SchedulerLog.scheduler_run_time.desc(),
                                                               SchedulerLog.execution_state.desc()).filter(
            SchedulerLog.job_id == job_id).first()
        res = SchedulerLogVOSchema().dump(latest_log)
        debug(f'根据任务ID获取最新的任务执行日志信息，结果：{res}')
        return R.ok(data=res)


scheduler_job_log_api.add_resource(SchedulerJobLogRouters, '/<job_id>')
