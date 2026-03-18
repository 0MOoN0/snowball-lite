import numpy as np
import pandas as pd
from flask import Blueprint
from flask_restful import Resource, Api
from pandas import DataFrame

from web.common.utils import R
from web.models import db
from web.models.scheduler.scheduler_job_info import SchedulerJobInfo, SchedulerJobInfoSchema
from web.models.scheduler.scheduler_log import SchedulerLog, SchedulerLogSchema
from web.scheduler import scheduler
from web.services.scheduler.scheduler_service import scheduler_service

scheduler_job_list_bp = Blueprint("scheduler_job_list", __name__, url_prefix="/scheduler/jobs")
scheduler_job_list_api = Api(scheduler_job_list_bp)


class SchedulerJobListRouter(Resource):

    def get(self):
        """
        @@@
        ```
        获取所有作业信息及其执行日志。

        Args:
            无参数。

        Returns:
            Response: 包含所有作业信息及其执行日志的响应对象。
        ```
        @@@
        """
        scheduler_job_list = SchedulerJobInfo.from_apscheduler_job_list(scheduler.get_jobs())
        jobs_df = DataFrame(SchedulerJobInfoSchema().dump(scheduler_job_list, many=True))
        # 查询最新的任务日志执行数据
        sub_query = SchedulerLog.query.order_by(SchedulerLog.scheduler_run_time.desc(),
                                                SchedulerLog.execution_state.desc()).limit(1000).subquery()
        latest_log: list[SchedulerLog] = db.session.query(sub_query).group_by(sub_query.c.job_id).all()
        if latest_log:
            latest_log_df = DataFrame(SchedulerLogSchema().dump(latest_log, many=True))
            # 根据job_id进行左外连接
            jobs_df: DataFrame = pd.merge(left=jobs_df, right=latest_log_df, how='left', on='job_id')
            # 查询计算各个任务的成功率
            success_count_res = scheduler_service.get_job_counts(SchedulerLog.get_scheduler_state_enum().EXECUTED.value)
            failed_count_res = scheduler_service.get_job_counts(SchedulerLog.get_scheduler_state_enum().ERROR.value)
            success_count_df = DataFrame(columns=['job_id', 'count']) if not success_count_res else (
                DataFrame([dict(zip(row.keys(), row)) for row in success_count_res]))
            failed_count_df = DataFrame(columns=['job_id', 'count']) if not failed_count_res else (
                DataFrame([dict(zip(row.keys(), row)) for row in failed_count_res]))
            success_count_df.rename(columns={'count': 'success_count'}, inplace=True)
            failed_count_df.rename(columns={'count': 'failed_count'}, inplace=True)

            count_merge_df = pd.merge(left=success_count_df, right=failed_count_df, how='outer', on='job_id')
            count_merge_df.fillna(0, inplace=True)
            # 计算成功率
            count_merge_df['success_rate'] = count_merge_df['success_count'].div(
                count_merge_df['failed_count'] + count_merge_df['success_count'], fill_value=None)
            count_merge_df = count_merge_df[['job_id', 'success_rate']]
            jobs_df = jobs_df.merge(count_merge_df, how='left', on='job_id')
            jobs_df.drop([SchedulerLog.create_time.key, SchedulerLog.update_time.key, 'id'], axis=1, inplace=True)
            jobs_df['success_rate'].fillna(0, inplace=True)
            jobs_df['success_rate'] = jobs_df['success_rate'].apply(lambda x: '{:.2%}'.format(x))
            # 需要考虑处理nan问题，否则序列化时字符会被转义
            jobs_df.replace({np.nan: None}, inplace=True)
            jobs_df.rename(columns={
                'job_id': 'jobId',
                'next_run_time': 'nextRunTime',
                'scheduler_run_time': 'schedulerRunTime',
                'execution_state': 'executionState',
                'success_rate': 'successRate'
            }, inplace=True)
        data = jobs_df.to_dict(orient='records')
        return R.ok(data=data)


scheduler_job_list_api.add_resource(SchedulerJobListRouter, '')
