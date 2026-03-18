import os
import json
import time
from importlib import import_module

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_docs import ApiDoc

from web.common.api_factory import create_api_blueprint
from web.weblogger import logger_initialize, info, error, warning
from web import settings, models, web_exception, weblogger
from web.common.cache import cache
from web.common.cons import webcons
from web.common.utils import R
from web.common.utils.enum_utils import record_enum_version

# 全局变量，标记任务队列是否可用
task_queue_available = False


def _import_web_module(module_name):
    return import_module(f"web.{module_name}")


def _is_redis_connection_error(exc):
    module_name = getattr(exc.__class__, "__module__", "")
    class_name = getattr(exc.__class__, "__name__", "")
    return module_name.startswith("redis") and class_name in {
        "ConnectionError",
        "TimeoutError",
    }


def register_interceptor(app):
    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )


def teardown_appcontext(app, db):
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        app.logger.info("teardown_appcontext")
        db.session.remove()


def create_app(config_name="dev"):
    """创建并初始化Flask应用"""
    global task_queue_available

    task_queue_available = False
    app = Flask(__name__)
    app.config.from_object(settings.config[config_name])
    settings.apply_runtime_overrides(app, config_name)

    # 保存配置名称到app.config中，供后续使用
    app.config["_config_name"] = config_name
    app.config["_config_class_name"] = settings.config[config_name].__name__

    logger_initialize.init_logger(app)
    cache.reset()

    app.config["CACHE_AVAILABLE"] = False
    app.config["SCHEDULER_AVAILABLE"] = False
    app.config["TASK_QUEUE_AVAILABLE"] = False

    with app.app_context():
        # 初始化关键组件 - 这些组件对系统一致性至关重要，失败时应用不应继续启动

        # 1. 初始化数据库模型（包括连接检查）
        app.logger.info("正在初始化数据库连接...")
        db_connected = models.ini_app(app)
        if not db_connected:
            raise Exception("数据库连接失败，应用无法正常工作，终止启动")

        # 2. 初始化缓存（Lite 模式下可跳过）
        if app.config.get("ENABLE_REDIS", True):
            app.logger.info("正在初始化缓存系统...")
            cache.init_app(app)
            app.config["CACHE_AVAILABLE"] = True
        else:
            app.logger.info("根据配置跳过缓存系统初始化")

        # 3. 初始化调度器（Lite 模式下可跳过）
        if app.config.get("ENABLE_SCHEDULER", True):
            if not app.config.get("ENABLE_PERSISTENT_JOBSTORE", True):
                app.config.pop("SCHEDULER_JOBSTORES", None)
                app.logger.info("根据配置禁用持久化 JobStore，调度器将使用内存模式")
            app.logger.info("正在初始化调度器...")
            scheduler_module = _import_web_module("scheduler")
            scheduler_module.init_app(app)
            app.config["SCHEDULER_AVAILABLE"] = True
        else:
            app.logger.info("根据配置跳过调度器初始化")

        # 在create_app函数中修改API初始化部分
        
        # 4. 初始化Flask-RESTX API蓝图（在路由初始化之前）
        try:
            app.logger.info("正在初始化Flask-RESTX API蓝图...")
            api, api_blueprint = create_api_blueprint(app)
            app.config["API_INSTANCE"] = api
            app.config["API_BLUEPRINT"] = api_blueprint
            app.logger.info("Flask-RESTX API蓝图初始化成功")
        except Exception as e:
            app.logger.error(f"Flask-RESTX API蓝图初始化失败: {e}", exc_info=True)
            raise Exception("Flask-RESTX API蓝图初始化失败，应用无法正常工作，终止启动")
        
        # 5. 初始化路由 - 确保API实例已创建
        app.logger.info("正在初始化路由...")
        routers = _import_web_module("routers")
        routers.init_app(app)
        
        # 6. 注册API蓝图（在所有namespace注册完成后）
        try:
            app.logger.info("正在注册API蓝图...")
            app.register_blueprint(api_blueprint)
            app.logger.info("API蓝图注册成功")
        except Exception as e:
            app.logger.error(f"API蓝图注册失败: {e}", exc_info=True)
            raise Exception("API蓝图注册失败，应用无法正常工作，终止启动")
        
        # 5. 设置Web异常处理器 - 保证API异常的正确处理
        app.logger.info("正在设置异常处理...")
        web_exception.init_app(app)

        # 6. xalpha设置 - 依赖数据库连接
        app.logger.info("正在配置xalpha设置...")
        import xalpha as xa

        engine = models.db.engine
        cache_settings = webcons.apply_xalpha_cache_settings(
            xa,
            default_engine=engine,
        )
        app.logger.info(f"xalpha缓存后端已设置为: {cache_settings['backend_name']}")
        info("xalpha设置初始化成功")

        # 7. 配置session自动关闭 - 确保数据库连接正确管理
        app.logger.info("正在配置session管理...")
        # teardown_appcontext(app, models.db)

        # 以下是非关键组件，失败时不影响系统核心功能

        # 8. 初始化databox
        try:
            if app.config.get("CACHE_AVAILABLE", False):
                app.logger.info("正在初始化databox...")
                databox = _import_web_module("databox")
                databox.init_app(app)
            else:
                app.logger.info("由于缓存系统未启用，跳过 databox 初始化")
        except Exception as e:
            app.logger.error(f"databox初始化失败: {e}", exc_info=True)

        # 9. 定义拦截器
        try:
            app.logger.info("正在注册拦截器...")
            register_interceptor(app)
        except Exception as e:
            app.logger.error(f"拦截器注册失败: {e}", exc_info=True)

        # 10. 跨域设置
        try:
            app.logger.info("正在配置CORS跨域...")
            CORS(app)
        except Exception as e:
            app.logger.error(f"CORS设置失败: {e}", exc_info=True)

        # 11. 自动生成API文档 /docs/api
        try:
            app.logger.info("正在初始化API文档...")
            ApiDoc(app)
        except Exception as e:
            app.logger.error(f"API文档初始化失败: {e}", exc_info=True)

        # 12. 初始化flask-profiler
        try:
            if app.config.get("ENABLE_PROFILER", True):
                app.logger.info("正在初始化性能分析工具...")
                flask_profiler = import_module("flask_profiler")
                # 检查是否为测试环境，测试环境中不初始化profiler或使用内存存储
                if app.config.get("ENV") == "testing":
                    app.logger.info("测试环境中，使用内存存储或跳过flask-profiler初始化")
                    # 确保配置正确设置为内存存储
                    if "FLASK_PROFILER" in app.config and app.config["FLASK_PROFILER"].get(
                        "enabled"
                    ):
                        app.config["FLASK_PROFILER"]["storage"] = {"engine": "memory"}
                else:
                    # 正常环境初始化
                    flask_profiler.init_app(app)
                    app.logger.info("flask-profiler初始化成功")
            else:
                app.logger.info("根据配置跳过性能分析工具初始化")
        except Exception as e:
            app.logger.error(f"flask-profiler初始化失败: {e}", exc_info=True)

        # 13. 最后初始化异步任务队列（可选功能）
        if app.config.get("ENABLE_TASK_QUEUE", True):
            if app.config.get("ENABLE_REDIS", True):
                try:
                    app.logger.info("正在初始化异步任务队列...")
                    task = _import_web_module("task")
                    task.init_app(app)
                    task_queue_available = True
                    app.logger.info("任务队列初始化成功，异步功能可用")
                except Exception as e:
                    task_queue_available = False
                    if _is_redis_connection_error(e):
                        app.logger.warning(f"Redis连接失败，Dramatiq任务队列将不可用: {e}")
                    else:
                        app.logger.error(f"异步任务队列初始化失败: {e}", exc_info=True)
            else:
                app.logger.info("由于 Redis 已禁用，跳过异步任务队列初始化")
        else:
            app.logger.info("根据配置跳过异步任务队列初始化")

    # 推送appcontext，测试环境中需要依赖上下文环境
    app.app_context().push()

    # 设置任务队列状态到app配置中，方便其他模块检查
    app.config["TASK_QUEUE_AVAILABLE"] = task_queue_available

    # 记录当前枚举版本信息到 Redis（key=version:enum，value={"global": 当前时间戳}）
    if app.config.get("CACHE_AVAILABLE", False):
        record_enum_version(
            redis_client=cache.get_redis_client(),
            key="version:enum",
            scope="global",
            logger=app.logger,
            merge=False,
        )
    else:
        app.logger.info("由于缓存系统未启用，跳过枚举版本写入")
    app.logger.info("应用初始化完成，所有关键组件正常工作")
    return app
