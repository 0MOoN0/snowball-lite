from flask import Blueprint, current_app
from flask_restful import Resource, Api

from web.common.utils import R
from web.models.scheduler.scheduler_info import SchedulerInfo, SchedulerInfoSchema
from web.scheduler import scheduler
from web.weblogger import info, warning, error

scheduler_bp = Blueprint("scheduler", __name__, url_prefix="/scheduler")
scheduler_api = Api(scheduler_bp)


class SchedulerRouter(Resource):

    def get(self):
        """
        @@@
        获取调度器信息
        Returns:
        @@@
        """
        # 创建调度器信息对象
        scheduler_info = SchedulerInfo()
        
        # 检查scheduler是否有running属性
        if hasattr(scheduler, 'running'):
            scheduler_info.running = scheduler.running
        else:
            warning("APScheduler没有running属性，这可能表明它没有正确初始化")
            scheduler_info.running = False
            
        # 获取主机名
        scheduler_info.current_host = getattr(scheduler, 'host_name', '')
        
        # 添加诊断信息
        diagnostic_info = self.get_scheduler_diagnostic_info()
        
        # 返回结果
        result = SchedulerInfoSchema().dump(scheduler_info)
        result['diagnostic_info'] = diagnostic_info
        
        return R.ok(data=result)
    
    def get_scheduler_diagnostic_info(self):
        """获取调度器的诊断信息"""
        diagnostic_info = {}
        
        try:
            # 基本信息
            diagnostic_info['scheduler_type'] = str(type(scheduler))
            
            # 检查关键属性
            if hasattr(scheduler, '_scheduler'):
                internal_scheduler = scheduler._scheduler
                diagnostic_info['internal_scheduler'] = {
                    'type': str(type(internal_scheduler)),
                    'state': getattr(internal_scheduler, 'state', 'Not Found'),
                    'running': getattr(internal_scheduler, 'running', False)
                }
            
            # 检查jobstores
            if hasattr(scheduler, 'jobstores'):
                diagnostic_info['jobstores'] = str(scheduler.jobstores)
            
            # 从配置获取信息
            diagnostic_info['config'] = {
                'SCHEDULER_API_ENABLED': current_app.config.get('SCHEDULER_API_ENABLED', False),
                'SCHEDULER_TIMEZONE': current_app.config.get('SCHEDULER_TIMEZONE', 'Not Found'),
                'has_jobstores_config': 'SCHEDULER_JOBSTORES' in current_app.config
            }
            
            # 获取所有任务
            try:
                if hasattr(scheduler, 'get_jobs'):
                    jobs = scheduler.get_jobs()
                    diagnostic_info['jobs_count'] = len(jobs) if jobs else 0
            except Exception as e:
                diagnostic_info['jobs_error'] = str(e)
                
        except Exception as e:
            diagnostic_info['error'] = str(e)
            
        return diagnostic_info


scheduler_api.add_resource(SchedulerRouter, '')
