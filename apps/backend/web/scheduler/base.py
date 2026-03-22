from flask_apscheduler import APScheduler
# from apscheduler.schedulers.background import BackgroundScheduler # 不再使用 BackgroundScheduler
from apscheduler.schedulers.gevent import GeventScheduler # 引入 GeventScheduler
from apscheduler.executors.gevent import GeventExecutor # 引入 GeventExecutor
import platform
import pytz


def resolve_jobstore_config(jobstore_config):
    if not isinstance(jobstore_config, dict):
        return jobstore_config
    if jobstore_config.get("backend") != "sqlalchemy":
        return jobstore_config
    from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

    return SQLAlchemyJobStore(url=jobstore_config.get("url"))

# Windows与其他系统通用的初始化方法
def create_apscheduler():
    """创建一个预配置的APScheduler实例，确保在所有环境中一致工作"""
    
    # 配置执行器
    executors = {
        'default': GeventExecutor()
    }
    
    # 基本配置
    scheduler_config = {
        'timezone': pytz.timezone("Asia/Shanghai"),
        'executors': executors, # 设置执行器
        'job_defaults': {
            'coalesce': True,           # 合并延迟的任务
            'max_instances': 1,         # 同一个任务最大实例数
            'misfire_grace_time': 60    # 错过执行时间的宽限期（秒）
        }
    }
    
    # 创建内部调度器实例为 GeventScheduler
    internal_scheduler = GeventScheduler(**scheduler_config)
    
    # 创建Flask-APScheduler实例，并传入我们自定义的 internal_scheduler
    scheduler_instance = APScheduler(scheduler=internal_scheduler)
    
    # 返回配置好的scheduler实例
    return scheduler_instance

# 创建调度器实例
scheduler = create_apscheduler()

# 后续初始化将在init_app中完成
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

    # 设置jobstores
    # scheduler._scheduler 引用的是我们传入的 GeventScheduler 实例
    if hasattr(scheduler, '_scheduler') and scheduler._scheduler:
        try:
            # Windows系统上的特殊处理逻辑保持不变
            if platform.system() == 'Windows':
                try:
                    scheduler._scheduler.configure(jobstores={'default': default_jobstore_config})
                    app.logger.debug("Windows系统成功配置SQLAlchemy jobstores")
                    return True
                except Exception as e:
                    # 增加了对 gevent 可能抛出的 "Selected backend doesn't support timezone-aware datetimes" 的检查
                    if ("Timezone offset does not match system offset" in str(e) or 
                        "Selected backend doesn't support timezone-aware datetimes" in str(e)):
                        app.logger.warning(f"Windows时区相关问题导致SQLAlchemyJobStore配置失败: {e}")
                        app.logger.info("APScheduler在Windows上将回退到默认的MemoryJobStore。")
                        return False 
                    else:
                        app.logger.error(f"Windows系统配置jobstores时发生非预期错误: {e}", exc_info=True)
                        raise 
            else:
                # 非Windows系统，正常设置
                scheduler._scheduler.configure(jobstores={'default': default_jobstore_config})
                app.logger.debug("成功配置SQLAlchemy jobstores")
                return True
        except Exception as e:
            app.logger.error(f"设置jobstores时出错: {e}", exc_info=True)
            print(f"设置jobstores时出错: {e}") # 保持原有打印
            
    return False
