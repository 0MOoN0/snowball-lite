"""
Flask-RESTX API工厂模块
提供统一的API对象创建和管理功能，避免循环依赖

@Author: System
@Date: 2025/1/XX
"""

from flask import Flask, Blueprint, jsonify
from flask_restx import Api, ValidationError
from typing import Optional, Tuple

from werkzeug.exceptions import BadRequest

from web.common.utils import R


class ApiFactory:
    """
    Flask-RESTX API工厂类
    
    负责创建和管理API实例，提供统一的配置管理
    避免在各个路由模块中重复创建API实例导致的循环依赖问题
    """
    
    _instance: Optional['ApiFactory'] = None
    _api_instance: Optional[Api] = None
    _api_blueprint: Optional[Blueprint] = None
    
    def __new__(cls) -> 'ApiFactory':
        """单例模式，确保全局只有一个API工厂实例"""
        if cls._instance is None:
            cls._instance = super(ApiFactory, cls).__new__(cls)
        return cls._instance
    
    def create_api_blueprint(self, app: Flask, **kwargs) -> Tuple[Api, Blueprint]:
        """
        创建API蓝图和Flask-RESTX API实例
        
        Args:
            app: Flask应用实例
            **kwargs: 额外的API配置参数
            
        Returns:
            tuple: (Api实例, Blueprint实例)
        """
        if self._api_instance is not None and self._api_blueprint is not None:
            return self._api_instance, self._api_blueprint
            
        # 创建API蓝图
        self._api_blueprint = Blueprint(
            'api', 
            __name__, 
            url_prefix='/'
        )
        
        # 从Flask配置中获取API文档配置
        doc_config = app.config.get('RESTX_DOC', '/docs')
        
        # 基础API配置
        api_config = {
            'version': '1.0',
            'title': 'Snowball API',
            'description': 'Snowball Web应用API文档',
            'doc': doc_config,  # 根据环境配置决定是否启用文档
            'validate': app.config.get('RESTX_VALIDATE', True),
            'mask_swagger': app.config.get('RESTX_MASK_SWAGGER', False),
            'error_404_help': app.config.get('RESTX_ERROR_404_HELP', False),
        }
        
        # 合并用户提供的额外配置
        api_config.update(kwargs)
        
        # 创建API实例并绑定到蓝图
        self._api_instance = Api(self._api_blueprint, **api_config)

        self._setup_error_handlers()
        
        app.logger.info(f"Flask-RESTX API蓝图创建成功，文档路径: {doc_config or '已禁用'}")
        
        return self._api_instance, self._api_blueprint
    
    def get_api(self) -> Optional[Api]:
        """
        获取已创建的API实例
        
        Returns:
            Api: 已创建的API实例，如果未创建则返回None
        """
        return self._api_instance
    
    def get_api_blueprint(self) -> Optional[Blueprint]:
        """
        获取已创建的API蓝图
        
        Returns:
            Blueprint: 已创建的API蓝图，如果未创建则返回None
        """
        return self._api_blueprint
    
    def reset(self):
        """
        重置工厂实例（主要用于测试）
        """
        self._api_instance = None
        self._api_blueprint = None

    def _setup_error_handlers(self):
        
        @self._api_instance.errorhandler(ValidationError)
        def handle_validation_error(error):
            raise error
        
        @self._api_instance.errorhandler(BadRequest)
        def handle_bad_request(error):
            raise error

# 提供便捷的工厂函数
def create_api_blueprint(app: Flask, **kwargs) -> Tuple[Api, Blueprint]:
    """
    便捷的API蓝图创建函数
    
    Args:
        app: Flask应用实例
        **kwargs: 额外的API配置参数
        
    Returns:
        tuple: (Api实例, Blueprint实例)
    """
    factory = ApiFactory()
    return factory.create_api_blueprint(app, **kwargs)


def get_api() -> Optional[Api]:
    """
    获取已创建的API实例
    
    Returns:
        Api: 已创建的API实例，如果未创建则返回None
    """
    factory = ApiFactory()
    return factory.get_api()


def get_api_blueprint() -> Optional[Blueprint]:
    """
    获取已创建的API蓝图
    
    Returns:
        Blueprint: 已创建的API蓝图，如果未创建则返回None
    """
    factory = ApiFactory()
    return factory.get_api_blueprint()