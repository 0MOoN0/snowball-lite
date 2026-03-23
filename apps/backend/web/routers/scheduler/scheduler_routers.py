from datetime import datetime, timedelta

import pytz
from flask import Blueprint, current_app
from flask_restful import Resource, Api

from web.common.utils import R
from web.models.scheduler.scheduler_info import SchedulerInfo, SchedulerInfoSchema
from web.scheduler import scheduler
from web.weblogger import warning

scheduler_bp = Blueprint("scheduler", __name__, url_prefix="/scheduler")
scheduler_api = Api(scheduler_bp)
_DEFAULT_OVERDUE_GRACE_SECONDS = 30


class SchedulerRouter(Resource):

    def get(self):
        """
        @@@
        获取调度器信息
        Returns:
        @@@
        """
        scheduler_info = SchedulerInfo()

        if hasattr(scheduler, "running"):
            scheduler_info.running = bool(scheduler.running)
        else:
            warning("APScheduler没有running属性，这可能表明它没有正确初始化")
            scheduler_info.running = False

        scheduler_info.current_host = getattr(scheduler, "host_name", "")
        health_snapshot = self.get_scheduler_health_snapshot()
        scheduler_info.healthy = health_snapshot["healthy"]
        scheduler_info.health_message = health_snapshot["message"]
        scheduler_info.runtime_backend = self.get_scheduler_runtime_backend()

        diagnostic_info = self.get_scheduler_diagnostic_info(health_snapshot)

        result = SchedulerInfoSchema().dump(scheduler_info)
        result["diagnostic_info"] = diagnostic_info

        return R.ok(data=result)

    def get_scheduler_runtime_backend(self):
        runtime_backend = getattr(scheduler, "runtime_backend", None)
        if runtime_backend:
            return runtime_backend

        internal_scheduler = getattr(scheduler, "_scheduler", None)
        if internal_scheduler is None:
            return "unknown"
        return type(internal_scheduler).__name__

    def get_scheduler_health_snapshot(self):
        if not hasattr(scheduler, "running") or not bool(getattr(scheduler, "running", False)):
            return {
                "healthy": False,
                "message": "调度器未运行",
                "overdue_jobs": [],
                "overdue_threshold_seconds": self.get_overdue_grace_seconds(),
            }

        internal_scheduler = getattr(scheduler, "_scheduler", None)
        if internal_scheduler is not None:
            greenlet = getattr(internal_scheduler, "_greenlet", None)
            if greenlet is not None and bool(getattr(greenlet, "dead", False)):
                return {
                    "healthy": False,
                    "message": "gevent 调度循环已停止",
                    "overdue_jobs": [],
                    "overdue_threshold_seconds": self.get_overdue_grace_seconds(),
                }

            scheduler_thread = getattr(internal_scheduler, "_thread", None)
            if scheduler_thread is not None and not scheduler_thread.is_alive():
                return {
                    "healthy": False,
                    "message": "后台调度线程已停止",
                    "overdue_jobs": [],
                    "overdue_threshold_seconds": self.get_overdue_grace_seconds(),
                }

        overdue_jobs = self.get_overdue_jobs()
        if overdue_jobs:
            return {
                "healthy": False,
                "message": f"存在 {len(overdue_jobs)} 个已过期未推进的任务",
                "overdue_jobs": overdue_jobs,
                "overdue_threshold_seconds": self.get_overdue_grace_seconds(),
            }

        return {
            "healthy": True,
            "message": "运行正常",
            "overdue_jobs": [],
            "overdue_threshold_seconds": self.get_overdue_grace_seconds(),
        }

    def get_scheduler_diagnostic_info(self, health_snapshot=None):
        """获取调度器的诊断信息"""
        diagnostic_info = {}

        try:
            diagnostic_info["scheduler_type"] = str(type(scheduler))
            diagnostic_info["runtime_backend"] = self.get_scheduler_runtime_backend()

            if hasattr(scheduler, "_scheduler"):
                internal_scheduler = scheduler._scheduler
                internal_info = {
                    "type": str(type(internal_scheduler)),
                    "state": getattr(internal_scheduler, "state", "Not Found"),
                    "running": getattr(internal_scheduler, "running", False),
                }
                greenlet = getattr(internal_scheduler, "_greenlet", None)
                if greenlet is not None:
                    internal_info["greenlet_dead"] = bool(getattr(greenlet, "dead", False))
                scheduler_thread = getattr(internal_scheduler, "_thread", None)
                if scheduler_thread is not None:
                    internal_info["thread_alive"] = scheduler_thread.is_alive()
                diagnostic_info["internal_scheduler"] = internal_info

            if hasattr(scheduler, "jobstores"):
                diagnostic_info["jobstores"] = str(scheduler.jobstores)

            diagnostic_info["config"] = {
                "SCHEDULER_API_ENABLED": current_app.config.get("SCHEDULER_API_ENABLED", False),
                "SCHEDULER_TIMEZONE": current_app.config.get("SCHEDULER_TIMEZONE", "Not Found"),
                "has_jobstores_config": "SCHEDULER_JOBSTORES" in current_app.config,
            }

            try:
                if hasattr(scheduler, "get_jobs"):
                    jobs = scheduler.get_jobs()
                    diagnostic_info["jobs_count"] = len(jobs) if jobs else 0
            except Exception as e:
                diagnostic_info["jobs_error"] = str(e)

            if health_snapshot is None:
                health_snapshot = self.get_scheduler_health_snapshot()
            diagnostic_info["healthy"] = health_snapshot["healthy"]
            diagnostic_info["health_message"] = health_snapshot["message"]
            diagnostic_info["overdue_threshold_seconds"] = health_snapshot["overdue_threshold_seconds"]
            diagnostic_info["overdue_jobs_count"] = len(health_snapshot["overdue_jobs"])
            if health_snapshot["overdue_jobs"]:
                diagnostic_info["overdue_jobs"] = health_snapshot["overdue_jobs"][:5]
        except Exception as e:
            diagnostic_info["error"] = str(e)

        return diagnostic_info

    def get_overdue_grace_seconds(self):
        return int(
            current_app.config.get(
                "SCHEDULER_HEALTH_OVERDUE_SECONDS",
                _DEFAULT_OVERDUE_GRACE_SECONDS,
            )
        )

    def get_scheduler_now(self):
        timezone_name = current_app.config.get("SCHEDULER_TIMEZONE", "Asia/Shanghai")
        return datetime.now(pytz.timezone(timezone_name))

    def normalize_job_time(self, run_time):
        if run_time is None:
            return None
        if run_time.tzinfo is None:
            return pytz.timezone(
                current_app.config.get("SCHEDULER_TIMEZONE", "Asia/Shanghai")
            ).localize(run_time)
        return run_time

    def get_overdue_jobs(self):
        overdue_jobs = []
        if not hasattr(scheduler, "get_jobs"):
            return overdue_jobs

        now = self.get_scheduler_now()
        overdue_deadline = now - timedelta(seconds=self.get_overdue_grace_seconds())
        for job in scheduler.get_jobs() or []:
            next_run_time = self.normalize_job_time(getattr(job, "next_run_time", None))
            if next_run_time is None:
                continue
            if next_run_time <= overdue_deadline:
                overdue_jobs.append(
                    {
                        "job_id": getattr(job, "id", ""),
                        "name": getattr(job, "name", getattr(job, "id", "")),
                        "next_run_time": next_run_time.isoformat(),
                    }
                )
        return overdue_jobs


scheduler_api.add_resource(SchedulerRouter, '')
