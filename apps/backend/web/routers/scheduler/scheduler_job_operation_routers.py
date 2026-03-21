# -*- coding: UTF-8 -*-
"""
@File    ：scheduler_job_operation_routers.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/10/7 15:19
"""

import uuid
from datetime import datetime, timedelta

from flask import Blueprint
from flask_restful import Resource, Api, reqparse
from pytz import timezone

from web import weblogger
from web.common.cache import cache
from web.common.cons import webcons
from web.common.utils import R
from web.models.scheduler.scheduler_log import SchedulerLog
from web.scheduler.base import scheduler

scheduler_job_operation_bp = Blueprint(
    "scheduler_job_operation", __name__, url_prefix="/scheduler/job"
)
scheduler_job_operation_api = Api(scheduler_job_operation_bp)


def manual_job_wrapper(original_func, *args, **kwargs):
    """
    手动任务包装函数，用于隔离手动执行任务和定时任务的函数引用

    Args:
        original_func: 原始任务函数引用（可能是字符串或可调用对象）
        *args: 传递给原始函数的位置参数
        **kwargs: 传递给原始函数的关键字参数

    Returns:
        原始函数的执行结果
    """
    # 如果 original_func 是字符串引用，需要转换为可调用对象
    if isinstance(original_func, str):
        from apscheduler.util import ref_to_obj
        try:
            actual_func = ref_to_obj(original_func)
        except Exception as e:
            weblogger.error(f"无法解析函数引用 {original_func}: {e}")
            raise
    else:
        actual_func = original_func
    
    return actual_func(*args, **kwargs)


class SchedulerJobRunRouters(Resource):
    def put(self):
        """
        @@@
        将任务放入队列中等待执行

        Body:
            jobId: str, 任务ID

        Returns:
            Union[dict, None]: 返回一个字典，包含任务执行的结果信息；如果任务不存在或已提交，则返回None

        Raises:
            无
        @@@
        """
        # 查询任务状态
        parse = _get_parse()
        args = parse.parse_args().copy()
        job_id = args["job_id"]
        job_args = []
        kwargs = {}
        if args.get("args", None):
            # 去除两边空白字符并使用&分割
            job_args = " ".join(
                [arg.strip() for arg in args["args"].split("&")]
            ).split()
        if args.get("kwargs", None):
            # 加载JSON
            try:
                kwargs = eval(args["kwargs"])
            except Exception as e:
                weblogger.error(f"参数错误: {e}")
                return R.fail(msg="参数错误")
        # 获取任务
        job = scheduler.get_job(args["job_id"])
        if job is None:
            return R.fail(msg="任务不存在")
        # 查询最近一次的执行状态
        job_log: SchedulerLog = (
            SchedulerLog.query.filter(SchedulerLog.job_id == job_id)
            .order_by(
                SchedulerLog.scheduler_run_time.desc(),
                SchedulerLog.execution_state.desc(),
            )
            .first()
        )
        # 如果最新提交的任务距离当前不超过15分钟，则返回失败
        if (
            job_log is not None
            and job_log.execution_state == job_log.get_scheduler_state_enum().SUBMITTED
            and (datetime.now() - job_log.create_time).total_seconds()
            < webcons.SchedulerConstants.JOB_RESUBMIT_DELAY
        ):
            return R.fail(msg="存在已经提交的相同任务，无法重新提交")
        redis = cache.get_redis_client()
        new_job_id = str(uuid.uuid4())
        key = webcons.RedisKeyPrefix.DYNAMIC_JOB + new_job_id
        redis.set(key, job_id, ex=900)
        scheduler.add_job(
            id=new_job_id,
            func=manual_job_wrapper,
            trigger="date",
            run_date=datetime.now(tz=timezone("Asia/Shanghai"))
            + timedelta(seconds=1),  # 延迟 1 秒,
            args=[job.func_ref] + job_args,  # 将原始函数引用作为第一个参数传递
            kwargs=kwargs,
            misfire_grace_time=3600,
        )  # 显式设置错过执行宽限时间为1小时
        return R.ok(msg="任务提交成功，正在执行")


class SchedulerPauseRouters(Resource):
    def put(self):
        """
        @@@
        暂停指定任务

        Body:
            jobId: str, 任务ID

        Returns:
            Union[dict, None]: 返回一个字典，包含任务暂停的结果信息；如果任务不存在或已经被暂停，则返回None
        @@@
        """
        parse = _get_parse()
        args = parse.parse_args().copy()
        job_id = args["job_id"]
        # 获取任务
        job = scheduler.get_job(job_id)
        if not job:
            return R.fail(msg="任务不存在")
        if job.next_run_time is None:
            return R.fail(msg="该任务已经被暂停了")
        scheduler.pause_job(job_id)
        return R.ok(msg="任务暂停成功")


class SchedulerResumeRouters(Resource):
    def put(self):
        """
        @@@
        恢复指定任务

        Body:
            jobId: str, 任务ID

        Returns:
            Union[dict, None]: 返回一个字典，包含任务恢复的结果信息；如果任务不存在或已经被恢复，则返回None
        @@@
        """
        parse = _get_parse()
        args = parse.parse_args().copy()
        job_id = args["job_id"]
        # 获取任务
        job = scheduler.get_job(job_id)
        if not job:
            return R.fail(msg="任务不存在")
        if job.next_run_time is not None:
            return R.fail(msg="该任务已经被恢复了")
        scheduler.resume_job(job_id)
        return R.ok(msg="任务恢复成功")


def _get_parse(parse=None):
    if not parse:
        parse = reqparse.RequestParser()
    parse.add_argument(
        "jobId", type=str, required=True, help="jobId is required", dest="job_id"
    )
    parse.add_argument("args", location="json", required=False)
    parse.add_argument("kwargs", location="json", required=False)
    return parse


scheduler_job_operation_api.add_resource(SchedulerJobRunRouters, "/run")
scheduler_job_operation_api.add_resource(SchedulerPauseRouters, "/pause")
scheduler_job_operation_api.add_resource(SchedulerResumeRouters, "/resume")
