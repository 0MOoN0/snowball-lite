from __future__ import annotations

import traceback
import logging
from dataclasses import dataclass
from datetime import datetime

import sqlalchemy
from apscheduler.events import *
from flask import current_app, has_app_context

try:
    import pymysql
except ImportError:  # lite 默认不需要 pymysql，MySQL 相关异常只在可用时处理
    pymysql = None

from web.common.cache import cache
from web.common.cons import webcons
from web.models import db
from web.models.scheduler.scheduler_job_state import SchedulerJobState
from web.models.scheduler.scheduler_log import SchedulerLog
from web.scheduler.base import init_jobstores, resolve_jobstore_config, scheduler
from web.scheduler.manual_job_id import decode_manual_job_id
from web.weblogger import debug, error, info, warning

# 导入所有scheduler模块以注册定时任务
from web.scheduler import asset_scheduler
from web.scheduler import analysis_scheduler
from web.scheduler import async_task_scheduler
from web.scheduler import databox_test_scheduler
from web.scheduler import notice_scheduler

# 全局变量，跟踪调度器是否已经初始化
_scheduler_initialized = False

_EXECUTION_PERSISTENCE_FULL_STRATEGY = "full"
_EXECUTION_PERSISTENCE_SIGNAL_ONLY_STRATEGY = "signal_only"
_EXECUTION_PERSISTENCE_ERROR_ONLY_STRATEGY = "error_only"
_EXECUTION_PERSISTENCE_AVAILABLE_STRATEGIES = (
    _EXECUTION_PERSISTENCE_FULL_STRATEGY,
    _EXECUTION_PERSISTENCE_SIGNAL_ONLY_STRATEGY,
    _EXECUTION_PERSISTENCE_ERROR_ONLY_STRATEGY,
)


@dataclass(frozen=True)
class ExecutionPersistenceProfile:
    default_policy: str
    supported_policies: tuple[str, ...]
    switchable: bool
    reason: str


def _build_execution_persistence_profile(
    default_policy: str,
    supported_policies: tuple[str, ...],
    switchable: bool,
    reason: str,
) -> ExecutionPersistenceProfile:
    return ExecutionPersistenceProfile(
        default_policy=default_policy,
        supported_policies=supported_policies,
        switchable=switchable,
        reason=reason,
    )


_EXECUTION_PERSISTENCE_DEFAULT_PROFILE = _build_execution_persistence_profile(
    default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
    supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
    switchable=False,
    reason="未命中注册任务时继续沿用 full，避免误伤现有 scheduler 行为",
)
_EXECUTION_PERSISTENCE_PROFILE_REGISTRY: dict[str, ExecutionPersistenceProfile] = {
    "AsyncTaskScheduler.consume_notification_outbox": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_SIGNAL_ONLY_STRATEGY,
        supported_policies=(
            _EXECUTION_PERSISTENCE_FULL_STRATEGY,
            _EXECUTION_PERSISTENCE_SIGNAL_ONLY_STRATEGY,
        ),
        switchable=True,
        reason="返回 stats.claimed，能稳定判断是否真的处理了业务信号；空轮询不应写成功日志",
    ),
    "notice_scheduler.cb_subscribe_today": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="成功与否取决于发行列表和通知发送链路，当前没有结构化业务信号可供安全收口",
    ),
    "notice_scheduler.cb_subscribe_tomorrow": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="成功与否取决于发行列表和通知发送链路，当前没有结构化业务信号可供安全收口",
    ),
    "notice_scheduler.daily_report": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="日报任务是聚合型输出，当前只具备日志语义，不具备可稳定判定的业务信号",
    ),
    "DataboxTestScheduler.test_databox_get_rt": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="成功只记日志、失败才发通知，但当前还没有足够证据把它安全收口为 error_only",
    ),
    "analysis_scheduler.to_analysis_all_transaction": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="分析任务只写入过程日志，当前没有返回可测试的成功信号",
    ),
    "analysis_scheduler.analysis_all_the_time": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="一次性全量分析更适合保留完整执行轨迹，当前没有收口依据",
    ),
    "AssetScheduler.update_asset_holding": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="任务内部有处理数量，但没有稳定返回值供 listener 判断业务信号",
    ),
    "AssetScheduler.update_fund_daily_data": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="任务内部有新增记录数日志，但没有稳定返回值供 listener 判断业务信号",
    ),
    "AssetScheduler.update_stock_asset": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="任务内部有新增股票代码数日志，但没有稳定返回值供 listener 判断业务信号",
    ),
    "AssetScheduler.monitor_grid_type_detail": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="监控任务会产生命中/未命中变化，但当前不返回可测试的结构化业务结果",
    ),
    "GridTypeScheduler.grid_type_trade_analysis": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="分析任务只写日志，没有结构化成功信号",
    ),
    "GridStrategyScheduler.grid_strategy_trade_analysis": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="分析任务只写日志，没有结构化成功信号",
    ),
    "AssetScheduler.complement_asset_data": _build_execution_persistence_profile(
        default_policy=_EXECUTION_PERSISTENCE_FULL_STRATEGY,
        supported_policies=(_EXECUTION_PERSISTENCE_FULL_STRATEGY,),
        switchable=False,
        reason="补全任务只写日志，没有结构化成功信号",
    ),
}


def _mysql_operational_errors():
    errors = [sqlalchemy.exc.OperationalError]
    if pymysql is not None:
        errors.append(pymysql.err.OperationalError)
    return tuple(errors)

# 运行级日志缓冲：零线程实现（方案1）
class _RunLogBufferHandler(logging.Handler):
    """一次任务运行的内存日志缓冲处理器。

    - 仅在本次运行期间挂载到 web logger 上；结束后卸载并聚合入库。
    - 通过 max_records 和 max_bytes 控制资源占用；超过则丢弃最旧记录。
    """

    def __init__(self, run_key: str, max_records: int = 2000, max_bytes: int = 256 * 1024):
        super().__init__()
        self.run_key = run_key
        self.max_records = max_records
        self.max_bytes = max_bytes
        self._buffer: list[str] = []
        self._current_bytes = 0
        self.setFormatter(logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
            "%Y-%m-%d %H:%M:%S",
        ))

    def emit(self, record: logging.LogRecord) -> None:
        try:
            line = self.format(record)
        except Exception:
            line = f"{getattr(record, 'levelname', 'INFO')} {record.getMessage()}"
        size = len(line.encode("utf-8", "ignore"))
        if size > self.max_bytes:
            # 单行过大直接丢弃，避免撑爆缓冲
            return
        self._buffer.append(line)
        self._current_bytes += size
        # 控制条数
        if len(self._buffer) > self.max_records:
            removed = self._buffer.pop(0)
            self._current_bytes -= len(removed.encode("utf-8", "ignore"))
        # 控制字节数
        while self._current_bytes > self.max_bytes and self._buffer:
            removed = self._buffer.pop(0)
            self._current_bytes -= len(removed.encode("utf-8", "ignore"))

    def dump_text(self) -> str:
        return "\n".join(self._buffer)


class _SchedulerModuleFilter(logging.Filter):
    """过滤仅采集 scheduler 相关模块日志，降低串扰。"""

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        try:
            name = getattr(record, "name", "") or ""
            pathname = getattr(record, "pathname", "") or ""
            module = getattr(record, "module", "") or ""
            return (
                "scheduler" in name
                or "scheduler" in pathname
                or module in {
                    "notice_scheduler",
                    "asset_scheduler",
                    "analysis_scheduler",
                    "databox_test_scheduler",
                }
            )
        except Exception:
            return True


_RUN_LOG_HANDLERS: dict[str, _RunLogBufferHandler] = {}


def _make_run_key(job_id: str | None, scheduled_run_time) -> str:
    try:
        if scheduled_run_time:
            run_time_str = scheduled_run_time.replace(tzinfo=None, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S")
        else:
            run_time_str = "unknown"
        return f"{job_id}|{run_time_str}"
    except Exception:
        return f"{job_id}|unknown"


def _resolve_job_id(event: JobSubmissionEvent | JobExecutionEvent) -> str:
    """与 save_logs 保持一致的 job_id 解析（动态任务映射支持）。"""
    manual_job_id = decode_manual_job_id(getattr(event, "job_id", ""))
    if manual_job_id is not None:
        return manual_job_id

    if _is_lite_runtime(current_app if has_app_context() else None):
        return getattr(event, "job_id", "")

    mapped = None
    redis_client = _get_cache_client_or_none()
    if redis_client is not None:
        mapped = redis_client.get(
            webcons.RedisKeyPrefix.DYNAMIC_JOB + getattr(event, "job_id", "")
        )
    return mapped if mapped is not None else getattr(event, "job_id", "")


def _is_lite_runtime(app=None) -> bool:
    if app is None and has_app_context():
        app = current_app
    if app is None:
        app = getattr(scheduler, "app", None)
    if app is None:
        return False
    return app.config.get("_config_name") == "lite" or app.config.get("ENV") == "lite"


def _get_cache_client_or_none():
    try:
        return cache.get_redis_client()
    except RuntimeError:
        return None


def _get_execution_persistence_profile(job_id: str | None) -> ExecutionPersistenceProfile:
    if not job_id:
        return _EXECUTION_PERSISTENCE_DEFAULT_PROFILE
    return _EXECUTION_PERSISTENCE_PROFILE_REGISTRY.get(
        job_id,
        _EXECUTION_PERSISTENCE_DEFAULT_PROFILE,
    )


def _get_registered_execution_persistence_profiles() -> dict[str, ExecutionPersistenceProfile]:
    return dict(_EXECUTION_PERSISTENCE_PROFILE_REGISTRY)


def _get_effective_execution_persistence_profile(
    job_id: str | None,
) -> ExecutionPersistenceProfile:
    profile = _get_execution_persistence_profile(job_id)

    try:
        from web.services.scheduler.scheduler_persistence_service import (
            scheduler_persistence_service,
        )

        effective_policy = scheduler_persistence_service.get_effective_policy(job_id)
    except Exception:
        return profile

    if effective_policy == profile.default_policy:
        return profile

    return _build_execution_persistence_profile(
        default_policy=effective_policy,
        supported_policies=profile.supported_policies,
        switchable=profile.switchable,
        reason=profile.reason,
    )


def _get_execution_persistence_strategy(job_id: str | None) -> str:
    return _get_effective_execution_persistence_profile(job_id).default_policy


def _is_manual_job_id(raw_job_id: str | None) -> bool:
    return decode_manual_job_id(raw_job_id or "") is not None


def _has_business_signal(execution_event: JobExecutionEvent) -> bool:
    retval = getattr(execution_event, "retval", None)
    if retval is None:
        return False

    claimed = None
    if isinstance(retval, dict):
        claimed = retval.get("claimed")
    else:
        claimed = getattr(retval, "claimed", None)

    try:
        return int(claimed) > 0
    except (TypeError, ValueError):
        return False


def _should_persist_execution_event(
    profile: ExecutionPersistenceProfile,
    execution_event: JobExecutionEvent,
) -> bool:
    if profile.default_policy == _EXECUTION_PERSISTENCE_FULL_STRATEGY:
        return True
    if profile.default_policy == _EXECUTION_PERSISTENCE_SIGNAL_ONLY_STRATEGY:
        return _has_business_signal(execution_event)
    return False


def _should_persist_submission_event(
    profile: ExecutionPersistenceProfile,
    is_manual_job: bool,
) -> bool:
    if is_manual_job:
        return True
    return profile.default_policy == _EXECUTION_PERSISTENCE_FULL_STRATEGY


def _get_error_msg(event):
    if isinstance(event, JobExecutionEvent) and event.code == EVENT_JOB_ERROR:
        exception_msg = event.exception
        return (
            str(exception_msg) if exception_msg is not None else None,
            event.traceback,
        )
    return None, None


def _get_scheduler_run_time(event):
    if isinstance(event, JobSubmissionEvent):
        if event.scheduled_run_times and event.scheduled_run_times[0] is not None:
            return event.scheduled_run_times[0].replace(tzinfo=None, microsecond=0)
    elif isinstance(event, JobExecutionEvent):
        return event.scheduled_run_time.replace(tzinfo=None, microsecond=0)
    return None


def _get_event_type(event):
    if hasattr(event, "code"):
        if event.code == EVENT_JOB_SUBMITTED:
            return SchedulerLog.get_scheduler_state_enum().SUBMITTED.value
        elif event.code == EVENT_JOB_ERROR:
            return SchedulerLog.get_scheduler_state_enum().ERROR.value
        elif event.code == EVENT_JOB_MISSED:
            return SchedulerLog.get_scheduler_state_enum().MISSED.value
        elif event.code == EVENT_JOB_EXECUTED:
            return SchedulerLog.get_scheduler_state_enum().EXECUTED.value
    raise Exception(f"Unexpected event code: {getattr(event, 'code', None)}")


def _should_mark_signal_run(
    profile: ExecutionPersistenceProfile,
    execution_event: JobSubmissionEvent | JobExecutionEvent,
) -> bool:
    if getattr(execution_event, "code", None) != EVENT_JOB_EXECUTED:
        return False
    if profile.default_policy == _EXECUTION_PERSISTENCE_SIGNAL_ONLY_STRATEGY:
        return _has_business_signal(execution_event)
    return profile.default_policy == _EXECUTION_PERSISTENCE_FULL_STRATEGY


def _sync_job_state(
    *,
    job_id: str,
    execution_event: JobSubmissionEvent | JobExecutionEvent,
    profile: ExecutionPersistenceProfile,
) -> None:
    event_type = _get_event_type(execution_event)
    scheduler_run_time = _get_scheduler_run_time(execution_event)
    exception_msg, _ = _get_error_msg(execution_event)
    event_time = datetime.now()

    job_state = (
        db.session.query(SchedulerJobState)
        .filter(SchedulerJobState.job_id == job_id)
        .first()
    )
    if job_state is None:
        job_state = SchedulerJobState(
            job_id=job_id,
            last_execution_state=event_type,
        )

    job_state.last_execution_state = event_type
    if scheduler_run_time is not None:
        job_state.last_scheduler_run_time = scheduler_run_time

    if event_type == SchedulerLog.get_scheduler_state_enum().SUBMITTED.value:
        job_state.last_submitted_time = event_time
    elif event_type == SchedulerLog.get_scheduler_state_enum().EXECUTED.value:
        job_state.last_finished_time = event_time
        if _should_mark_signal_run(profile, execution_event):
            job_state.last_signal_run_time = event_time
        job_state.last_error = None
        job_state.last_error_time = None
    elif event_type == SchedulerLog.get_scheduler_state_enum().ERROR.value:
        job_state.last_finished_time = event_time
        job_state.last_error_time = event_time
        job_state.last_error = exception_msg

    db.session.add(job_state)


def _attach_run_log_buffer(job_id: str, scheduled_run_time) -> None:
    """在任务提交时挂载缓冲处理器。"""
    run_key = _make_run_key(job_id, scheduled_run_time)
    if run_key in _RUN_LOG_HANDLERS:
        return
    handler = _RunLogBufferHandler(run_key)
    handler.addFilter(_SchedulerModuleFilter())
    try:
        from web.weblogger import logger as web_logger
        web_logger.addHandler(handler)
        _RUN_LOG_HANDLERS[run_key] = handler
        debug(f"运行日志缓冲器挂载: {run_key}")
    except Exception as e:
        error(f"挂载运行日志缓冲器失败: {e}", exc_info=True)


def _detach_run_log_buffer(job_id: str, scheduled_run_time) -> str | None:
    """在任务结束/异常时卸载缓冲并返回文本。"""
    run_key = _make_run_key(job_id, scheduled_run_time)
    handler = _RUN_LOG_HANDLERS.pop(run_key, None)
    if not handler:
        return None
    try:
        from web.weblogger import logger as web_logger
        web_logger.removeHandler(handler)
        debug(f"运行日志缓冲器卸载: {run_key}")
    except Exception:
        pass
    return handler.dump_text()


def _persist_run_logs(job_id: str, scheduled_run_time, logs_text: str | None) -> None:
    """将本次运行日志写入 tb_apscheduler_log.traceback（KISS）。"""
    if not logs_text:
        return
    try:
        record = (
            db.session.query(SchedulerLog)
            .filter(SchedulerLog.job_id == job_id)
            .filter(SchedulerLog.scheduler_run_time == scheduled_run_time.replace(tzinfo=None, microsecond=0))
            .order_by(SchedulerLog.id.desc())
            .first()
        )
        if record:
            existing_tb = getattr(record, "traceback", None) or ""
            combined = (
                f"{existing_tb}\n\n--- RUN LOGS ---\n{logs_text}" if existing_tb else logs_text
            )
            # 简单长度控制，保留后 64KB
            max_len_bytes = 64 * 1024
            b = combined.encode("utf-8", "ignore")
            if len(b) > max_len_bytes:
                combined = b[-max_len_bytes:].decode("utf-8", "ignore")
            record.traceback = combined
            db.session.add(record)
            db.session.commit()
            debug("运行日志已写入 tb_apscheduler_log.traceback")
    except Exception as e:
        error(f"运行日志入库失败: {e}", exc_info=True)
        try:
            db.session.rollback()
        except Exception:
            pass


def init_app(app):
    global _scheduler_initialized

    app.logger.debug("### 加载scheduler监听模块")

    # 检查调度器是否已经初始化过，避免Flask debug模式重复初始化
    if _scheduler_initialized:
        # 检查调度器是否已经在运行
        if hasattr(scheduler, "_scheduler") and getattr(
            scheduler._scheduler, "running", False
        ):
            app.logger.info("APScheduler已经初始化并且正在运行中，跳过重复初始化")
            return True
        app.logger.warning("APScheduler已经初始化但未运行，尝试重新启动")

    # 设置时区为东八区（上海）
    app.config["SCHEDULER_TIMEZONE"] = "Asia/Shanghai"

    is_lite_runtime = _is_lite_runtime(app)
    persistent_mode = bool(app.config.get("ENABLE_PERSISTENT_JOBSTORE", False))
    lite_fail_fast = bool(is_lite_runtime and persistent_mode)
    jobstores = app.config.get("SCHEDULER_JOBSTORES") or {}
    if persistent_mode and not jobstores:
        message = "lite 持久化 scheduler 模式缺少 SCHEDULER_JOBSTORES 配置"
        if lite_fail_fast:
            error(message)
            raise RuntimeError(message)
        warning(message)

    # 在初始化APScheduler前，先检查数据库连接
    if not verify_apscheduler_database(app):
        message = (
            "APScheduler数据库连接检查失败，调度器无法启动"
            if lite_fail_fast
            else "APScheduler数据库连接检查失败，调度器可能无法正常工作"
        )
        if lite_fail_fast:
            error(message)
            raise RuntimeError(message)
        warning(message)

    # 初始化APScheduler
    try:
        debug("开始初始化APScheduler...")
        jobstores_config = app.config.pop("SCHEDULER_JOBSTORES", None)
        try:
            scheduler.init_app(app)
        finally:
            if jobstores_config is not None:
                app.config["SCHEDULER_JOBSTORES"] = jobstores_config
        debug("APScheduler初始化完成")

        # 手动设置jobstores
        debug("开始手动配置jobstores...")
        if init_jobstores(app):
            debug("jobstores配置成功")
        else:
            if lite_fail_fast:
                raise RuntimeError("lite 持久化 JobStore 配置失败，无法启动调度器")
            warning("jobstores配置失败，将使用内存存储")
    except Exception as e:
        error(f"APScheduler初始化失败: {e}")
        error(traceback.format_exc())
        if is_lite_runtime:
            raise
        return False

    # 检查scheduler状态并记录日志
    if hasattr(scheduler, "running"):
        info(f"初始化前 APScheduler 运行状态: {scheduler.running}")
    else:
        info("初始化前 APScheduler 没有 running 属性")

    # 检查scheduler是否有必要的属性和方法
    debug_scheduler_attributes()

    # 添加事件监听器
    try:
        scheduler.add_listener(
            scheduler_listener,
            EVENT_JOB_SUBMITTED
            | EVENT_JOB_EXECUTED
            | EVENT_JOB_ERROR
            | EVENT_JOB_MISSED,
        )
        debug("已成功添加事件监听器")
    except Exception as e:
        error(f"添加事件监听器失败: {e}")
        error(traceback.format_exc())

    # 启动scheduler
    try:
        debug("开始启动APScheduler...")

        # 先检查必要的配置是否都已经设置
        if hasattr(scheduler, "_scheduler"):
            if (
                hasattr(scheduler._scheduler, "jobstores")
                and not scheduler._scheduler.jobstores
            ):
                warning(
                    "警告: scheduler没有配置jobstores，这可能导致调度器无法正常工作"
                )

        # 启动调度器
        scheduler.start()
        debug(f"APScheduler 调用start()方法完成")
        info(f"APScheduler 启动成功，运行状态: {scheduler.running}")
    except Exception as e:
        error(f"APScheduler 启动失败: {e}")
        error(traceback.format_exc())
        if is_lite_runtime:
            raise
        return False

    # 再次检查scheduler状态
    if hasattr(scheduler, "running"):
        info(f"启动后 APScheduler 运行状态: {scheduler.running}")
        if not scheduler.running:
            warning("警告: APScheduler 启动后状态为 False，可能无法正常调度任务")
            debug("检查scheduler属性及配置...")
            debug(
                f"- scheduler.jobstores: {getattr(scheduler._scheduler, 'jobstores', 'Not Found') if hasattr(scheduler, '_scheduler') else 'Not Found'}"
            )
            debug(
                f"- app.config SCHEDULER_JOBSTORES: {app.config.get('SCHEDULER_JOBSTORES', 'Not Found')}"
            )
            debug(
                f"- scheduler._scheduler: {getattr(scheduler, '_scheduler', 'Not Found')}"
            )

            try:
                # 尝试直接访问内部scheduler
                if hasattr(scheduler, "_scheduler"):
                    internal_scheduler = scheduler._scheduler
                    debug(
                        f"- internal scheduler state: {getattr(internal_scheduler, 'state', 'Not Found')}"
                    )
                    debug(
                        f"- internal scheduler running: {getattr(internal_scheduler, 'running', 'Not Found')}"
                    )

                    # 尝试重新初始化jobstores并重启
                    debug("尝试重新初始化jobstores...")

                    # 获取默认jobstore
                    default_jobstore = app.config.get("SCHEDULER_JOBSTORES", {}).get(
                        "default"
                    )
                    if default_jobstore:
                        try:
                            default_jobstore = resolve_jobstore_config(default_jobstore)
                            # 为内部scheduler直接设置jobstores
                            internal_scheduler.configure(
                                jobstores={"default": default_jobstore}
                            )
                            debug("已手动设置jobstores")

                            # 尝试直接访问和启动内部调度器
                            if hasattr(internal_scheduler, "start") and callable(
                                internal_scheduler.start
                            ):
                                internal_scheduler.start()
                                debug("内部调度器直接启动完成")
                                info(
                                    f"内部调度器状态: {getattr(internal_scheduler, 'running', False)}"
                                )
                                # 标记调度器已初始化成功
                                _scheduler_initialized = True
                        except Exception as e:
                            error(f"重新初始化jobstores失败: {e}")
            except Exception as e:
                debug(f"检查内部scheduler失败: {e}")

            try:
                # 尝试重新启动
                debug("尝试重新启动APScheduler...")
                scheduler.start()
                info(f"APScheduler 重新启动尝试后状态: {scheduler.running}")
                if scheduler.running:
                    # 标记调度器已初始化成功
                    _scheduler_initialized = True
            except Exception as e:
                error(f"APScheduler 重新启动失败: {e}")
                error(traceback.format_exc())

    if not hasattr(scheduler, "running") or not scheduler.running:
        if not is_lite_runtime:
            warning("APScheduler 未进入 running 状态，当前环境继续启动但不标记 scheduler 可用")
            return False
        raise RuntimeError("APScheduler 启动失败，调度器未进入 running 状态")

    _scheduler_initialized = True
    app.logger.debug("scheduler监听模块加载完毕 ###")
    return True


def verify_apscheduler_database(app):
    """
    验证APScheduler所需的数据库连接是否正常

    Args:
        app: Flask应用实例

    Returns:
        bool: 数据库连接是否正常
    """
    try:
        # 获取jobstore配置
        jobstores = app.config.get("SCHEDULER_JOBSTORES")
        if not jobstores:
            warning("未找到SCHEDULER_JOBSTORES配置，将使用默认内存存储")
            return True

        # 检查default jobstore是否存在且类型正确
        default_jobstore = jobstores.get("default")
        if not default_jobstore:
            warning("未找到default jobstore配置，将使用默认内存存储")
            return True

        # 如果使用SQLAlchemyJobStore，检查数据库连接
        default_jobstore = resolve_jobstore_config(default_jobstore)

        if hasattr(default_jobstore, "url"):
            debug(f"APScheduler使用SQLAlchemyJobStore，URL: {default_jobstore.url}")

            # 检查数据库表是否存在
            engine = None
            try:
                engine = sqlalchemy.create_engine(default_jobstore.url)

                # 首先测试连接
                with engine.connect():
                    pass

                inspector = sqlalchemy.inspect(engine)
                if engine.url.get_backend_name() == "sqlite":
                    if not inspector.has_table("apscheduler_jobs"):
                        warning(
                            "APScheduler SQLite jobstore 任务表(apscheduler_jobs)不存在，首次启动时会自动创建"
                        )
                    debug("APScheduler SQLite jobstore 连接检查成功")
                    return True

                if not inspector.has_table("apscheduler_jobs"):
                    warning(
                        "APScheduler的任务表(apscheduler_jobs)不存在，可能需要初始化数据库"
                    )
                    return False

                debug("APScheduler数据库连接和表检查成功")
                return True

            except _mysql_operational_errors() as e:
                error(f"APScheduler数据库连接失败: {e}")
                return False
            except Exception as e:
                error(f"APScheduler数据库检查过程中发生未知错误: {e}")
                error(traceback.format_exc())
                return False
            finally:
                if engine is not None:
                    engine.dispose()

    except Exception as e:
        error(f"验证APScheduler数据库时发生错误: {e}")
        error(traceback.format_exc())
        return False

    return True


def debug_scheduler_attributes():
    """输出scheduler关键属性，用于调试"""
    try:
        debug("APScheduler关键属性:")
        debug(f"- 类型: {type(scheduler)}")
        debug(f"- running: {getattr(scheduler, 'running', 'Not Found')}")
        debug(
            f"- 方法列表: {[method for method in dir(scheduler) if not method.startswith('_') and callable(getattr(scheduler, method))]}"
        )

        # 检查内部scheduler
        if hasattr(scheduler, "_scheduler"):
            internal_scheduler = scheduler._scheduler
            debug("内部scheduler属性:")
            debug(f"- 类型: {type(internal_scheduler)}")
            debug(f"- state: {getattr(internal_scheduler, 'state', 'Not Found')}")
            debug(f"- running: {getattr(internal_scheduler, 'running', 'Not Found')}")

    except Exception as e:
        debug(f"获取scheduler属性时出错: {e}")


def scheduler_listener(callback_event: JobSubmissionEvent | JobExecutionEvent):
    # 为了避免在gevent环境下，事件监听器内部的日志IO操作可能引发的问题，
    # 尤其是在高并发或fork场景下，将日志记录操作封装在 app_context 内，
    # 并确保日志记录是非阻塞的或在gevent友好的方式下进行。
    # Flask的logger通常是线程安全的，但在gevent环境中，最好也遵循gevent的最佳实践。

    event_type_str = "未知事件"
    job_id_str = getattr(callback_event, "job_id", "N/A")
    scheduled_run_time_str = "N/A"

    if (
        hasattr(callback_event, "scheduled_run_time")
        and callback_event.scheduled_run_time
    ):
        scheduled_run_time_str = callback_event.scheduled_run_time.isoformat()
    elif (
        hasattr(callback_event, "scheduled_run_times")
        and callback_event.scheduled_run_times
        and callback_event.scheduled_run_times[0]
    ):
        scheduled_run_time_str = callback_event.scheduled_run_times[0].isoformat()

    # 供事件末尾入库使用的临时变量
    logs_to_persist: str | None = None
    job_id_for_persist: str | None = None
    run_time_for_persist = None
    job_id_resolved = _resolve_job_id(callback_event)
    execution_profile = _get_effective_execution_persistence_profile(job_id_resolved)
    is_manual_job = _is_manual_job_id(job_id_str)

    if callback_event.code == EVENT_JOB_SUBMITTED:
        event_type_str = "任务已提交 (SUBMITTED)"
        # 对于SUBMITTED事件，通常我们更关心它何时被实际添加到执行队列
        # 可以在这里添加更详细的日志，比如任务的触发器类型等
        info(
            f"APScheduler事件: {event_type_str} - 作业ID: {job_id_str}, 计划运行时间: {scheduled_run_time_str}"
        )
        # 运行日志开始：挂载缓冲处理器（零线程）
        try:
            scheduled_rt = getattr(callback_event, "scheduled_run_time", None) or getattr(callback_event, "scheduled_run_times", [None])[0]
            _attach_run_log_buffer(job_id_resolved, scheduled_rt)
        except Exception as e:
            error(f"挂载运行日志缓冲器出错: {e}", exc_info=True)
    elif callback_event.code == EVENT_JOB_EXECUTED:
        event_type_str = "任务已执行 (EXECUTED)"
        # 对于EXECUTED事件，可以记录返回值（如果适用且不大）和执行时长（如果APScheduler提供）
        # retval = getattr(callback_event, 'retval', 'N/A') # 注意：retval可能很大
        info(
            f"APScheduler事件: {event_type_str} - 作业ID: {job_id_str}, 计划运行时间: {scheduled_run_time_str}"
        )
        # 运行日志结束：卸载缓冲并入库
        try:
            scheduled_rt = getattr(callback_event, "scheduled_run_time", None) or getattr(callback_event, "scheduled_run_times", [None])[0]
            logs_to_persist = _detach_run_log_buffer(job_id_resolved, scheduled_rt)
            job_id_for_persist = job_id_resolved
            run_time_for_persist = scheduled_rt
        except Exception as e:
            error(f"卸载运行日志缓冲器失败: {e}", exc_info=True)
    elif callback_event.code == EVENT_JOB_ERROR:
        event_type_str = "任务执行错误 (ERROR)"
        exception_str = str(getattr(callback_event, "exception", "N/A"))
        traceback_str = str(getattr(callback_event, "traceback", "N/A"))
        error(
            f"APScheduler事件: {event_type_str} - 作业ID: {job_id_str}, 计划运行时间: {scheduled_run_time_str}"
        )
        error(f"  异常: {exception_str}")
        error(
            f"  堆栈跟踪: {traceback_str}"
        )  # 对于生产环境，可能需要更精简的错误日志或发送到专门的错误跟踪系统
        # 运行日志结束：卸载缓冲并入库（包含错误信息）
        try:
            scheduled_rt = getattr(callback_event, "scheduled_run_time", None) or getattr(callback_event, "scheduled_run_times", [None])[0]
            logs_to_persist = _detach_run_log_buffer(job_id_resolved, scheduled_rt)
            job_id_for_persist = job_id_resolved
            run_time_for_persist = scheduled_rt
        except Exception as e:
            error(f"卸载运行日志缓冲器失败: {e}", exc_info=True)
    elif callback_event.code == EVENT_JOB_MISSED:
        event_type_str = "任务错过执行 (MISSED)"
        warning(
            f"APScheduler事件: {event_type_str} - 作业ID: {job_id_str}, 计划运行时间: {scheduled_run_time_str}"
        )
        # 运行日志结束：卸载缓冲并入库（错过执行也记录时间窗内日志）
        try:
            scheduled_rt = getattr(callback_event, "scheduled_run_time", None) or getattr(callback_event, "scheduled_run_times", [None])[0]
            logs_to_persist = _detach_run_log_buffer(job_id_resolved, scheduled_rt)
            job_id_for_persist = job_id_resolved
            run_time_for_persist = scheduled_rt
        except Exception as e:
            error(f"卸载运行日志缓冲器失败: {e}", exc_info=True)
    else:
        warning(
            f"APScheduler接收到未知事件代码: {callback_event.code} - 作业ID: {job_id_str}"
        )

    def save_logs(execution_event: JobSubmissionEvent | JobExecutionEvent):
        job_id = job_id_resolved
        should_persist_event = True
        if (
            execution_event.code == EVENT_JOB_SUBMITTED
            and not _should_persist_submission_event(execution_profile, is_manual_job)
        ):
            debug(
                "APScheduler事件: SUBMITTED 命中非 full 策略且不是手动触发，跳过落库"
            )
            should_persist_event = False
        if (
            execution_event.code == EVENT_JOB_EXECUTED
            and not _should_persist_execution_event(execution_profile, execution_event)
        ):
            debug(
                "APScheduler事件: EXECUTED 命中 signal_only 策略且未发现业务信号，跳过落库"
            )
            should_persist_event = False

        try:
            if should_persist_event:
                scheduler_log: SchedulerLog = SchedulerLog()
                scheduler_log.job_id = job_id
                scheduler_log.execution_state = _get_event_type(execution_event)
                scheduler_log.scheduler_run_time = _get_scheduler_run_time(execution_event)
                scheduler_log.exception, scheduler_log.traceback = _get_error_msg(
                    execution_event
                )
                db.session.add(scheduler_log)

            _sync_job_state(
                job_id=job_id,
                execution_event=execution_event,
                profile=execution_profile,
            )
            db.session.commit()
        except Exception as e:
            error(f"scheduler_log save error: {e}", exc_info=True)
            db.session.rollback()

    with scheduler.app.app_context():
        save_logs(callback_event)
        # 在事件记录入库后，追加运行日志正文
        try:
            if logs_to_persist and job_id_for_persist and run_time_for_persist:
                _persist_run_logs(job_id_for_persist, run_time_for_persist, logs_to_persist)
        except Exception as e:
            error(f"运行日志入库失败: {e}", exc_info=True)
