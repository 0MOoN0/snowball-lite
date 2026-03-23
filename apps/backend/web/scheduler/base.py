from flask_apscheduler import APScheduler
from apscheduler.executors.gevent import GeventExecutor
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.gevent import GeventScheduler
import platform
import pytz


def resolve_jobstore_config(jobstore_config):
    if not isinstance(jobstore_config, dict):
        return jobstore_config
    if jobstore_config.get("backend") != "sqlalchemy":
        return jobstore_config
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

    return SQLAlchemyJobStore(url=jobstore_config.get("url"))

def _use_thread_scheduler_runtime():
    return platform.system() == "Darwin"


def get_scheduler_runtime_backend() -> str:
    return "background_threadpool" if _use_thread_scheduler_runtime() else "gevent"


def _build_scheduler_executors():
    if _use_thread_scheduler_runtime():
        return {
            "default": ThreadPoolExecutor(max_workers=4),
        }
    return {
        "default": GeventExecutor(),
    }


def _build_internal_scheduler(scheduler_config):
    if _use_thread_scheduler_runtime():
        return BackgroundScheduler(**scheduler_config)
    return GeventScheduler(**scheduler_config)


def create_apscheduler():
    """创建一个预配置的APScheduler实例，确保在所有环境中一致工作"""

    executors = _build_scheduler_executors()

    # 基本配置
    scheduler_config = {
        "timezone": pytz.timezone("Asia/Shanghai"),
        "executors": executors,
        "job_defaults": {
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": 60,
        },
    }

    internal_scheduler = _build_internal_scheduler(scheduler_config)
    scheduler_instance = APScheduler(scheduler=internal_scheduler)
    scheduler_instance.runtime_backend = get_scheduler_runtime_backend()

    return scheduler_instance


scheduler = create_apscheduler()


def init_jobstores(app):
    """
    为scheduler手动设置jobstores
    这个函数需要在scheduler.init_app(app)之后、scheduler.start()之前调用
    """
    if not app:
        return False
        
    # 检查是否有MySQL配置
    if 'SCHEDULER_JOBSTORES' not in app.config:
        app.logger.warning("未找到SCHEDULER_JOBSTORES配置，APScheduler将使用默认的MemoryJobStore")
        return False # 明确返回False，因为无法配置DB jobstore
        
    # 获取默认jobstore
    default_jobstore_config = app.config['SCHEDULER_JOBSTORES'].get('default')
    if not default_jobstore_config:
        app.logger.warning("未找到default jobstore配置，APScheduler将使用默认的MemoryJobStore")
        return False # 明确返回False
    default_jobstore_config = resolve_jobstore_config(default_jobstore_config)

    if hasattr(scheduler, "_scheduler") and scheduler._scheduler:
        try:
            if platform.system() == "Windows":
                try:
                    scheduler._scheduler.configure(jobstores={"default": default_jobstore_config})
                    app.logger.debug("Windows系统成功配置SQLAlchemy jobstores")
                    return True
                except Exception as e:
                    if ("Timezone offset does not match system offset" in str(e) or
                        "Selected backend doesn't support timezone-aware datetimes" in str(e)):
                        app.logger.warning(f"Windows时区相关问题导致SQLAlchemyJobStore配置失败: {e}")
                        app.logger.info("APScheduler在Windows上将回退到默认的MemoryJobStore。")
                        return False
                    else:
                        app.logger.error(f"Windows系统配置jobstores时发生非预期错误: {e}", exc_info=True)
                        raise
            else:
                scheduler._scheduler.configure(jobstores={"default": default_jobstore_config})
                app.logger.debug("成功配置SQLAlchemy jobstores")
                return True
        except Exception as e:
            app.logger.error(f"设置jobstores时出错: {e}", exc_info=True)
            print(f"设置jobstores时出错: {e}")

    return False
