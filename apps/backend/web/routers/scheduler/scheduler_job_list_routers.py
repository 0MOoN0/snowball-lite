import numpy as np
import pandas as pd
from flask import Blueprint
from flask_restful import Resource, Api
from pandas import DataFrame

from web.common.utils import R
from web.models.scheduler.scheduler_job_info import SchedulerJobInfo, SchedulerJobInfoSchema
from web.models.scheduler.scheduler_log import SchedulerLog, SchedulerLogSchema
from web.models.scheduler.scheduler_job_state import SchedulerJobStateSchema
from web.scheduler import scheduler
from web.services.scheduler.scheduler_persistence_service import (
    scheduler_persistence_service,
)
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
        job_ids = jobs_df["job_id"].tolist() if not jobs_df.empty else []
        policy_view_map = scheduler_persistence_service.get_policy_view_map(job_ids)
        latest_states = scheduler_service.get_job_states_by_ids(job_ids)
        latest_logs = scheduler_service.get_latest_job_logs_by_ids(job_ids)

        if latest_states:
            latest_state_df = DataFrame(
                SchedulerJobStateSchema().dump(latest_states, many=True)
            ).rename(
                columns={
                    "last_execution_state": "state_execution_state",
                    "last_scheduler_run_time": "state_scheduler_run_time",
                }
            )
            jobs_df = pd.merge(
                left=jobs_df,
                right=latest_state_df,
                how="left",
                on="job_id",
            )

        if latest_logs:
            latest_log_df = DataFrame(SchedulerLogSchema().dump(latest_logs, many=True)).rename(
                columns={
                    "execution_state": "log_execution_state",
                    "scheduler_run_time": "log_scheduler_run_time",
                }
            )
            jobs_df = pd.merge(left=jobs_df, right=latest_log_df, how='left', on='job_id')

        if not jobs_df.empty:
            jobs_df["default_policy"] = jobs_df["job_id"].apply(
                lambda job_id: policy_view_map.get(job_id, {}).get("defaultPolicy")
            )
            jobs_df["effective_policy"] = jobs_df["job_id"].apply(
                lambda job_id: policy_view_map.get(job_id, {}).get("effectivePolicy")
            )
            jobs_df["policy_source"] = jobs_df["job_id"].apply(
                lambda job_id: policy_view_map.get(job_id, {}).get("policySource")
            )
            jobs_df["supported_policies"] = jobs_df["job_id"].apply(
                lambda job_id: policy_view_map.get(job_id, {}).get("supportedPolicies")
            )
            jobs_df["policy_switchable"] = jobs_df["job_id"].apply(
                lambda job_id: policy_view_map.get(job_id, {}).get("switchable")
            )
            jobs_df["policy_reason"] = jobs_df["job_id"].apply(
                lambda job_id: policy_view_map.get(job_id, {}).get("reason")
            )
            jobs_df["execution_state"] = jobs_df.get("state_execution_state")
            jobs_df["scheduler_run_time"] = jobs_df.get("state_scheduler_run_time")
            if "log_execution_state" in jobs_df:
                jobs_df["execution_state"] = jobs_df["execution_state"].fillna(
                    jobs_df["log_execution_state"]
                )
            if "log_scheduler_run_time" in jobs_df:
                jobs_df["scheduler_run_time"] = jobs_df["scheduler_run_time"].fillna(
                    jobs_df["log_scheduler_run_time"]
                )
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
            drop_columns = [
                "id",
                SchedulerLog.create_time.key,
                SchedulerLog.update_time.key,
                "state_execution_state",
                "state_scheduler_run_time",
                "log_execution_state",
                "log_scheduler_run_time",
                "last_submitted_time",
                "last_finished_time",
                "last_signal_run_time",
                "last_error",
                "last_error_time",
            ]
            jobs_df.drop(
                [column for column in drop_columns if column in jobs_df.columns],
                axis=1,
                inplace=True,
            )
            jobs_df['success_rate'].fillna(0, inplace=True)
            jobs_df['success_rate'] = jobs_df['success_rate'].apply(lambda x: '{:.2%}'.format(x))
            # 需要考虑处理nan问题，否则序列化时字符会被转义
            jobs_df.replace({np.nan: None}, inplace=True)
            jobs_df.rename(columns={
                'job_id': 'jobId',
                'next_run_time': 'nextRunTime',
                'scheduler_run_time': 'schedulerRunTime',
                'execution_state': 'executionState',
                'success_rate': 'successRate',
                'default_policy': 'defaultPolicy',
                'effective_policy': 'effectivePolicy',
                'policy_source': 'policySource',
                'supported_policies': 'supportedPolicies',
                'policy_switchable': 'policySwitchable',
                'policy_reason': 'policyReason',
            }, inplace=True)
        data = jobs_df.to_dict(orient='records')
        return R.ok(data=data)


scheduler_job_list_api.add_resource(SchedulerJobListRouter, '')
