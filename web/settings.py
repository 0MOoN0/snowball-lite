"""
本项目配置了多个数据源，主要分为两个（默认），一个是业务相关数据源：snowball / snowball2，一个是数据存放数据源：snowball_data
启动FLASK应用时，通过指定的配置文件来动态变化配置
配置结构：
Config ：基础配置，所有配置的基础类
    -DevConfig：继承了Config，开发环境配置
    -StgConfig：继承了Config，线上测试环境配置
    -ProdConfig：继承了Config，生产环境配置
    -TestingConfig：继承了Config，测试环境配置
"""

import os
from urllib.parse import quote_plus


def build_sqlalchemy_jobstore_config(url):
    return {"backend": "sqlalchemy", "url": url}


class Config:
    # 从环境变量中获取数据库连接信息，如果未设置则使用默认值
    DIALCT = os.environ.get("DB_DIALECT", "mysql")
    DRIVER = os.environ.get("DB_DRIVER", "pymysql")
    USERNAME = os.environ.get("DEV_DB_USERNAME", "root")
    PASSWORD = quote_plus(os.environ.get("DEV_DB_PASSWORD", "root"))  # URL编码处理密码
    HOST = os.environ.get("DEV_DB_HOST", "127.0.0.1")
    PORT = os.environ.get("DEV_DB_PORT", "3306")
    DATABASE = os.environ.get("DB_DATABASE", "snowball_data_dev")
    # 默认数据源，数据存放库
    SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8mb4".format(
        DIALCT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE
    )
    UPLOAD_DIR_GRID = "static/data/grid"
    UPLOAD_DIR_IRECORD = "static/data/irecord"
    # 显示sqlalchemy的SQL追踪
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 设置通过REST-API与APScheduler进行交互
    SCHEDULER_API_ENABLED = True
    SCHEDULER_API_PREFIX = "/apscheduler"
    # 设置 APScheduler 时区为东八区（上海）
    SCHEDULER_TIMEZONE = "Asia/Shanghai"
    # APScheduler 日志级别配置
    SCHEDULER_LOG_LEVEL = "INFO"  # 默认使用INFO级别

    # 数据库引擎日志配置
    ENABLE_ENGINE_LOG = True  # 是否启用数据库引擎日志
    SLOW_QUERY_THRESHOLD = 1.0  # 慢查询阈值（秒）
    
    # 轻量模式/可选基础设施开关
    ENABLE_REDIS = True
    ENABLE_TASK_QUEUE = True
    ENABLE_SCHEDULER = True
    ENABLE_PERSISTENT_JOBSTORE = True
    ENABLE_PROFILER = True
    ENABLE_XALPHA_SQL_CACHE = True
    XALPHA_CACHE_BACKEND = os.environ.get("XALPHA_CACHE_BACKEND", "sql").lower()
    XALPHA_CACHE_DIR = os.path.abspath(
        os.environ.get("XALPHA_CACHE_DIR", os.path.join(os.getcwd(), "data", "xalpha_cache"))
    )
    XALPHA_CACHE_SQLITE_PATH = os.environ.get("XALPHA_CACHE_SQLITE_PATH")

    # 添加默认的数据库连接池配置，所有环境都会继承这些配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,  # 连接池大小
        "max_overflow": 15,  # 最大溢出连接数
        "pool_timeout": 60,  # 获取连接的超时时间（秒）
        "pool_recycle": 1200,  # 连接回收时间（秒），低于MySQL默认连接超时时间
        "pool_pre_ping": True,  # 每次连接前ping一下数据库，确保连接有效
        "connect_args": {
            "connect_timeout": 30,  # MySQL连接超时时间（秒）
            "read_timeout": 60,  # 读取超时时间（秒）
            "write_timeout": 60,  # 写入超时时间（秒）
        },
    }
    # Flask-RESTX API文档配置
    RESTX_DOC = "/docs"  # API文档路径，默认为/docs
    RESTX_VALIDATE = True  # 启用请求验证
    RESTX_MASK_SWAGGER = False  # 不隐藏swagger字段
    RESTX_ERROR_404_HELP = True  # 关闭404帮助信息


# 开发环境
class DevConfig(Config):
    """
    开发环境配置
    """

    # 从环境变量获取开发环境用的数据库连接信息
    DEV_DB_USERNAME = os.environ.get("DEV_DB_USERNAME", "root")
    DEV_DB_PASSWORD = quote_plus(
        os.environ.get("DEV_DB_PASSWORD", "root")
    )  # URL编码处理密码
    DEV_DB_HOST = os.environ.get("DEV_DB_HOST", "localhost")
    DEV_DB_PORT = os.environ.get("DEV_DB_PORT", "3306")
    DEV_DB_DATABASE = os.environ.get("DEV_DB_DATABASE", "snowball_dev")
    DEV_DB_PROFILER = os.environ.get("DEV_DB_PROFILER", "snowball_profiler_dev")

    SQLALCHEMY_BINDS = {
        "snowball": f"mysql+pymysql://{DEV_DB_USERNAME}:{DEV_DB_PASSWORD}@{DEV_DB_HOST}:{DEV_DB_PORT}/{DEV_DB_DATABASE}?charset=utf8mb4",
        "profiler": f"mysql+pymysql://{DEV_DB_USERNAME}:{DEV_DB_PASSWORD}@{DEV_DB_HOST}:{DEV_DB_PORT}/{DEV_DB_PROFILER}?charset=utf8mb4",
    }
    # 显示sqlalchemy的SQL追踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True  # 开启 DevConfig 的查询记录
    # 设置APSchedular数据库存储方式，default为默认的存储方式
    SCHEDULER_JOBSTORES = {
        "default": build_sqlalchemy_jobstore_config(SQLALCHEMY_BINDS.get("snowball"))
    }
    # 开发环境特定的连接池配置，只覆盖必要的参数
    SQLALCHEMY_ENGINE_OPTIONS = Config.SQLALCHEMY_ENGINE_OPTIONS.copy()
    SQLALCHEMY_ENGINE_OPTIONS.update(
        {
            "pool_recycle": 1800,  # 开发环境特有的连接回收时间
        }
    )
    # 性能报告
    # flask-profiler配置选项
    FLASK_PROFILER = {
        "enabled": False,
        "storage": {
            "engine": "sqlalchemy",
            "db_url": SQLALCHEMY_BINDS.get("profiler", "sqlite:///:memory:"),
        },
        "basicAuth": {"enabled": True, "username": "admin", "password": "admin"},
        "ignore": ["^/static/.*"],
    }

    # Redis配置
    DEV_REDIS_HOST = os.environ.get("DEV_REDIS_HOST", "localhost")
    DEV_REDIS_PORT = int(os.environ.get("DEV_REDIS_PORT", "6379"))
    DEV_REDIS_DB = int(os.environ.get("DEV_REDIS_DB", "1"))
    DEV_REDIS_PASSWORD = os.environ.get("DEV_REDIS_PASSWORD", None)

    REDIS_CLIENT = {
        "REDIS_HOST": DEV_REDIS_HOST,
        "REDIS_PORT": DEV_REDIS_PORT,
        "REDIS_DB": DEV_REDIS_DB,
        "REDIS_PASSWORD": DEV_REDIS_PASSWORD,
    }
    # DRAMATIQ
    DRAMATIQ_BROKER = "dramatiq.brokers.redis:RedisBroker"
    # 开发环境，使用1号数据库
    DRAMATIQ_BROKER_URL = f"redis://{':' + DEV_REDIS_PASSWORD + '@' if DEV_REDIS_PASSWORD else ''}{DEV_REDIS_HOST}:{DEV_REDIS_PORT}/{DEV_REDIS_DB}"
    ENV = "dev"
    SQLALCHEMY_ECHO = False
    # SQLALCHEMY_RECORD_QUERIES = True
    DEBUG = False
    # 检测代码改变的时间间隔为10秒
    # RELOADER_INTERVAL = 10
    
    # APScheduler 日志级别配置 - 开发环境使用DEBUG级别
    SCHEDULER_LOG_LEVEL = "DEBUG"
    
    # 开发环境引擎日志配置
    ENABLE_ENGINE_LOG = True  # 开发环境启用引擎日志
    SLOW_QUERY_THRESHOLD = 2.0  # 开发环境使用更低的阈值
    
    # Flask应用端口配置
    FLASK_PORT = int(os.environ.get("DEV_FLASK_PORT", "15000"))  # 开发环境Flask端口


# 线上测试环境
class StgConfig(Config):
    """
    线上测试环境配置
    """

    # 从环境变量获取线上测试环境用的数据库连接信息
    STG_DB_USERNAME = os.environ.get("STG_DB_USERNAME", "root")
    STG_DB_PASSWORD = quote_plus(
        os.environ.get("STG_DB_PASSWORD", "root")
    )  # URL编码处理密码
    STG_DB_HOST = os.environ.get("STG_DB_HOST", "mysql")
    STG_DB_PORT = os.environ.get("STG_DB_PORT", "3307")
    STG_DB_DATABASE = os.environ.get("STG_DB_DATABASE", "snowball_stg")
    STG_DB_PROFILER = os.environ.get("STG_DB_PROFILER", "snowball_profiler_stg")
    STG_DB_DATA = os.environ.get("STG_DB_DATA", "snowball_data_stg")

    SQLALCHEMY_BINDS = {
        "snowball": f"mysql+pymysql://{STG_DB_USERNAME}:{STG_DB_PASSWORD}@{STG_DB_HOST}:{STG_DB_PORT}/{STG_DB_DATABASE}?charset=utf8mb4",
        "profiler": f"mysql+pymysql://{STG_DB_USERNAME}:{STG_DB_PASSWORD}@{STG_DB_HOST}:{STG_DB_PORT}/{STG_DB_PROFILER}?charset=utf8mb4",
    }
    # 默认数据源
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{STG_DB_USERNAME}:{STG_DB_PASSWORD}@{STG_DB_HOST}:{STG_DB_PORT}/{STG_DB_DATA}?charset=utf8mb4"
    # 显示sqlalchemy的SQL追踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True  # 开启 StgConfig 的查询记录

    # 线上测试环境特定的连接池配置，只覆盖必要的参数
    SQLALCHEMY_ENGINE_OPTIONS = Config.SQLALCHEMY_ENGINE_OPTIONS.copy()
    SQLALCHEMY_ENGINE_OPTIONS.update(
        {
            "pool_recycle": 1800,  # 线上测试环境特有的连接回收时间
        }
    )

    # Redis配置
    STG_REDIS_HOST = os.environ.get("STG_REDIS_HOST", "redis")
    STG_REDIS_PORT = int(os.environ.get("STG_REDIS_PORT", "6379"))
    STG_REDIS_DB = int(os.environ.get("STG_REDIS_DB", "0"))
    STG_REDIS_PASSWORD = os.environ.get("STG_REDIS_PASSWORD", None)

    # DRAMATIQ
    DRAMATIQ_BROKER = "dramatiq.brokers.redis:RedisBroker"
    DRAMATIQ_BROKER_URL = f"redis://{':' + STG_REDIS_PASSWORD + '@' if STG_REDIS_PASSWORD else ''}{STG_REDIS_HOST}:{STG_REDIS_PORT}"
    # 设置APSchedular数据库存储方式，default为默认的存储方式
    SCHEDULER_JOBSTORES = {
        "default": build_sqlalchemy_jobstore_config(SQLALCHEMY_BINDS.get("snowball"))
    }
    
    # 线上测试环境引擎日志配置
    ENABLE_ENGINE_LOG = True  # 线上测试环境启用引擎日志
    SLOW_QUERY_THRESHOLD = 2.0  # 线上测试环境使用更高的阈值
    # 性能报告
    # flask-profiler配置选项
    FLASK_PROFILER = {
        "enabled": False,  # 连接处理有问题，会一直占用会话不会结束事务
        "storage": {
            "engine": "sqlalchemy",
            "db_url": SQLALCHEMY_BINDS.get("profiler", "sqlite:///:memory:"),
        },
        "basicAuth": {"enabled": True, "username": "admin", "password": "admin"},
        "ignore": ["^/static/.*"],
    }
    REDIS_CLIENT = {
        "REDIS_HOST": STG_REDIS_HOST,
        "REDIS_PORT": STG_REDIS_PORT,
        "REDIS_DB": STG_REDIS_DB,
        "REDIS_PASSWORD": STG_REDIS_PASSWORD,
    }
    # DRAMATIQ
    DRAMATIQ_BROKER = "dramatiq.brokers.redis:RedisBroker"
    # 线上测试库，使用0号数据库
    DRAMATIQ_BROKER_URL = f"redis://{':' + STG_REDIS_PASSWORD + '@' if STG_REDIS_PASSWORD else ''}{STG_REDIS_HOST}:{STG_REDIS_PORT}"
    ENV = "stg"
    # SQLALCHEMY_ECHO = True
    # SQLALCHEMY_RECORD_QUERIES = True
    DEBUG = False
    
    # APScheduler 日志级别配置 - 测试环境使用DEBUG级别
    SCHEDULER_LOG_LEVEL = "DEBUG"


# 用于本地连接在线测试服务
class LocalDevTest(Config):
    """
    开发环境配置
    """

    # 从环境变量获取本地开发测试用的数据库连接信息
    LOCAL_DEV_DB_USERNAME = os.environ.get("LOCAL_DEV_DB_USERNAME", "root")
    LOCAL_DEV_DB_PASSWORD = quote_plus(
        os.environ.get("LOCAL_DEV_DB_PASSWORD", "root")
    )  # URL编码处理密码
    LOCAL_DEV_DB_HOST = os.environ.get("LOCAL_DEV_DB_HOST", "localhost")
    LOCAL_DEV_DB_PORT = os.environ.get("LOCAL_DEV_DB_PORT", "3307")
    LOCAL_DEV_DB_DATABASE = os.environ.get("LOCAL_DEV_DB_DATABASE", "snowball")
    LOCAL_DEV_DB_PROFILER = os.environ.get("LOCAL_DEV_DB_PROFILER", "snowball_profiler")
    LOCAL_DEV_DB_DATA = os.environ.get("LOCAL_DEV_DB_DATA", "snowball_data")

    SQLALCHEMY_BINDS = {
        "snowball": f"mysql+pymysql://{LOCAL_DEV_DB_USERNAME}:{LOCAL_DEV_DB_PASSWORD}@{LOCAL_DEV_DB_HOST}:{LOCAL_DEV_DB_PORT}/{LOCAL_DEV_DB_DATABASE}?charset=utf8mb4",
        "profiler": f"mysql+pymysql://{LOCAL_DEV_DB_USERNAME}:{LOCAL_DEV_DB_PASSWORD}@{LOCAL_DEV_DB_HOST}:{LOCAL_DEV_DB_PORT}/{LOCAL_DEV_DB_PROFILER}?charset=utf8mb4",
    }
    # 默认数据源
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{LOCAL_DEV_DB_USERNAME}:{LOCAL_DEV_DB_PASSWORD}@{LOCAL_DEV_DB_HOST}:{LOCAL_DEV_DB_PORT}/{LOCAL_DEV_DB_DATA}?charset=utf8mb4"
    # 显示sqlalchemy的SQL追踪
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Redis配置
    LOCAL_REDIS_HOST = os.environ.get("LOCAL_DEV_REDIS_HOST", "localhost")
    LOCAL_REDIS_PORT = int(os.environ.get("LOCAL_DEV_REDIS_PORT", "6379"))
    LOCAL_REDIS_DB = int(os.environ.get("LOCAL_DEV_REDIS_DB", "0"))
    LOCAL_REDIS_PASSWORD = os.environ.get("LOCAL_DEV_REDIS_PASSWORD", None)

    # DRAMATIQ
    DRAMATIQ_BROKER = "dramatiq.brokers.redis:RedisBroker"
    DRAMATIQ_BROKER_URL = f"redis://{':' + LOCAL_REDIS_PASSWORD + '@' if LOCAL_REDIS_PASSWORD else ''}{LOCAL_REDIS_HOST}:{LOCAL_REDIS_PORT}"
    # 设置APSchedular数据库存储方式，default为默认的存储方式
    SCHEDULER_JOBSTORES = {
        "default": build_sqlalchemy_jobstore_config(SQLALCHEMY_BINDS.get("snowball"))
    }
    # 性能报告
    # flask-profiler配置选项
    FLASK_PROFILER = {
        "enabled": False,
        "storage": {
            "engine": "sqlalchemy",
            "db_url": SQLALCHEMY_BINDS.get("profiler", "sqlite:///:memory:"),
        },
        "basicAuth": {"enabled": True, "username": "admin", "password": "admin"},
        "ignore": ["^/static/.*"],
    }
    REDIS_CLIENT = {
        "REDIS_HOST": LOCAL_REDIS_HOST,
        "REDIS_PORT": LOCAL_REDIS_PORT,
        "REDIS_DB": LOCAL_REDIS_DB,
        "REDIS_PASSWORD": LOCAL_REDIS_PASSWORD,
    }
    # DRAMATIQ
    DRAMATIQ_BROKER = "dramatiq.brokers.redis:RedisBroker"
    # 线上测试库，使用0号数据库
    DRAMATIQ_BROKER_URL = f"redis://{':' + LOCAL_REDIS_PASSWORD + '@' if LOCAL_REDIS_PASSWORD else ''}{LOCAL_REDIS_HOST}:{LOCAL_REDIS_PORT}"
    ENV = "development"
    # SQLALCHEMY_ECHO = True
    # SQLALCHEMY_RECORD_QUERIES = True
    DEBUG = False
    
    # 本地开发测试环境引擎日志配置
    ENABLE_ENGINE_LOG = True  # 本地开发测试环境启用引擎日志
    SLOW_QUERY_THRESHOLD = 1.0  # 本地开发测试环境使用标准阈值


class ProdConfig(Config):
    # 生产环境禁用API文档
    RESTX_DOC = False  # 生产环境不提供API文档
    # 从环境变量获取生产环境用的数据库连接信息
    PROD_DB_USERNAME = os.environ.get("PROD_DB_USERNAME", "root")
    PROD_DB_PASSWORD = quote_plus(
        os.environ.get("PROD_DB_PASSWORD", "root")
    )  # URL编码处理密码
    PROD_DB_HOST = os.environ.get("PROD_DB_HOST", "127.0.0.1")
    PROD_DB_PORT = os.environ.get("PROD_DB_PORT", "3306")
    PROD_DB_DATABASE = os.environ.get("PROD_DB_DATABASE", "snowball")

    SQLALCHEMY_BINDS = {
        "snowball": f"mysql+pymysql://{PROD_DB_USERNAME}:{PROD_DB_PASSWORD}@{PROD_DB_HOST}:{PROD_DB_PORT}/{PROD_DB_DATABASE}?charset=utf8mb4"
    }
    # 生产环境特定的连接池配置，只覆盖必要的参数
    SQLALCHEMY_ENGINE_OPTIONS = Config.SQLALCHEMY_ENGINE_OPTIONS.copy()
    SQLALCHEMY_ENGINE_OPTIONS.update(
        {
            "pool_recycle": 1800,  # 生产环境特有的连接回收时间
            "pool_timeout": 30,  # 生产环境特有的连接超时时间
        }
    )

    ENV = "production"
    DEBUG = False
    SQLALCHEMY_ECHO = False

    # 生产环境 Redis 配置
    PROD_REDIS_HOST = os.environ.get("PROD_REDIS_HOST", "redis")
    PROD_REDIS_PORT = int(os.environ.get("PROD_REDIS_PORT", "6379"))
    PROD_REDIS_DB = int(os.environ.get("PROD_REDIS_DB", "0"))
    PROD_REDIS_PASSWORD = os.environ.get("PROD_REDIS_PASSWORD", None)

    # 添加 Redis 客户端配置
    REDIS_CLIENT = {
        "REDIS_HOST": PROD_REDIS_HOST,
        "REDIS_PORT": PROD_REDIS_PORT,
        "REDIS_DB": PROD_REDIS_DB,
        "REDIS_PASSWORD": PROD_REDIS_PASSWORD,
    }

    # 添加 DRAMATIQ 配置
    DRAMATIQ_BROKER = "dramatiq.brokers.redis:RedisBroker"
    DRAMATIQ_BROKER_URL = f"redis://{':' + PROD_REDIS_PASSWORD + '@' if PROD_REDIS_PASSWORD else ''}{PROD_REDIS_HOST}:{PROD_REDIS_PORT}/{PROD_REDIS_DB}"
    
    # 生产环境引擎日志配置
    ENABLE_ENGINE_LOG = False  # 生产环境默认关闭
    SLOW_QUERY_THRESHOLD = 5.0  # 生产环境使用更高的阈值


class TestingConfig(Config):
    ENV = "testing"
    # 数据存放测试库
    DATABASE = os.environ.get("TEST_DB_DATABASE", "snowball_data_test")

    # 从环境变量获取测试环境用的数据库连接信息
    TEST_DB_USERNAME = os.environ.get("TEST_DB_USERNAME", Config.USERNAME)
    TEST_DB_PASSWORD = quote_plus(
        os.environ.get("TEST_DB_PASSWORD", Config.PASSWORD)
    )  # URL编码处理密码
    TEST_DB_HOST = os.environ.get("TEST_DB_HOST", Config.HOST)
    TEST_DB_PORT = os.environ.get("TEST_DB_PORT", Config.PORT)
    TEST_DB_TESTDB = os.environ.get("TEST_DB_TESTDB", "snowball_test")
    TEST_DB_PROFILER = os.environ.get("TEST_DB_PROFILER", "snowball_profiler_test")

    # 连接测试库
    SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}?charset=utf8mb4".format(
        Config.DIALCT,
        "pymysql",
        TEST_DB_USERNAME,
        TEST_DB_PASSWORD,
        TEST_DB_HOST,
        TEST_DB_PORT,
        DATABASE,
    )
    SQLALCHEMY_BINDS = {
        "snowball": f"mysql+pymysql://{TEST_DB_USERNAME}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_TESTDB}?charset=utf8mb4",
        # "profiler": f"mysql+pymysql://{TEST_DB_USERNAME}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_PROFILER}?charset=utf8mb4"
    }
    TESTING = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = True

    # 测试环境特定的连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = Config.SQLALCHEMY_ENGINE_OPTIONS.copy()
    SQLALCHEMY_ENGINE_OPTIONS.update(
        {
            "pool_size": 2,  # 测试环境使用较小的连接池
            "max_overflow": 5,  # 测试环境使用较小的溢出连接数
            "pool_recycle": 300,  # 测试环境连接回收更频繁
            "pool_timeout": 10,  # 测试环境连接超时更短
        }
    )

    # 设置APSchedular数据库存储方式
    SCHEDULER_JOBSTORES = {
        "default": build_sqlalchemy_jobstore_config(SQLALCHEMY_BINDS.get("snowball"))
    }

    # Redis配置
    TEST_REDIS_HOST = os.environ.get("TEST_REDIS_HOST", "localhost")
    TEST_REDIS_PORT = int(os.environ.get("TEST_REDIS_PORT", "6379"))
    TEST_REDIS_DB = int(
        os.environ.get("TEST_REDIS_DB", "1")
    )  # 使用2号数据库避免与开发环境冲突
    TEST_REDIS_PASSWORD = os.environ.get("TEST_REDIS_PASSWORD", None)

    REDIS_CLIENT = {
        "REDIS_HOST": TEST_REDIS_HOST,
        "REDIS_PORT": TEST_REDIS_PORT,
        "REDIS_DB": TEST_REDIS_DB,
        "REDIS_PASSWORD": TEST_REDIS_PASSWORD,
    }

    # DRAMATIQ配置
    DRAMATIQ_BROKER = "dramatiq.brokers.redis:RedisBroker"
    DRAMATIQ_BROKER_URL = f"redis://{':' + TEST_REDIS_PASSWORD + '@' if TEST_REDIS_PASSWORD else ''}{TEST_REDIS_HOST}:{TEST_REDIS_PORT}/{TEST_REDIS_DB}"

    # 性能报告配置
    FLASK_PROFILER = {
        "enabled": False,  # 测试环境默认关闭
        "storage": {"engine": "memory"},  # 测试环境使用内存存储，不依赖数据库
        "basicAuth": {"enabled": True, "username": "admin", "password": "admin"},
        "ignore": ["^/static/.*"],
    }

    DEBUG = True  # 测试环境开启调试以便查看详细错误信息
    
    # 测试环境引擎日志配置
    ENABLE_ENGINE_LOG = True  # 测试环境默认关闭，避免干扰测试
    SLOW_QUERY_THRESHOLD = 1.0  # 测试环境使用标准阈值


class LiteConfig(Config):
    """
    轻量模式配置：
    - 默认使用 SQLite
    - 关闭 Redis / Dramatiq / APScheduler / profiler 等可选基础设施
    - 保留最小数据库与 API 启动能力，用于 spike 验证
    """

    ENV = "lite"
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_ECHO = False

    LITE_DB_PATH = os.path.abspath(
        os.environ.get("LITE_DB_PATH", os.path.join(os.getcwd(), "snowball_lite.db"))
    )
    LITE_DB_URI = f"sqlite:///{LITE_DB_PATH}"

    SQLALCHEMY_DATABASE_URI = LITE_DB_URI
    # 将默认库和业务 bind 指向同一 SQLite 文件，先跑通最小启动链路
    SQLALCHEMY_BINDS = {
        "snowball": LITE_DB_URI,
    }
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "check_same_thread": False,
            "timeout": 30,
        }
    }

    ENABLE_REDIS = False
    ENABLE_TASK_QUEUE = False
    ENABLE_SCHEDULER = False
    ENABLE_PERSISTENT_JOBSTORE = False
    ENABLE_PROFILER = False
    ENABLE_XALPHA_SQL_CACHE = False
    ENABLE_ENGINE_LOG = False
    XALPHA_CACHE_BACKEND = os.environ.get("LITE_XALPHA_CACHE_BACKEND", "csv").lower()
    XALPHA_CACHE_DIR = os.path.abspath(
        os.environ.get(
            "LITE_XALPHA_CACHE_DIR",
            os.path.join(os.getcwd(), "data", "lite_xalpha_cache"),
        )
    )
    XALPHA_CACHE_SQLITE_PATH = os.environ.get("LITE_XALPHA_CACHE_SQLITE_PATH")

    REDIS_CLIENT = {}
    SCHEDULER_JOBSTORES = {}
    FLASK_PROFILER = {
        "enabled": False,
        "storage": {"engine": "memory"},
        "basicAuth": {"enabled": False, "username": "admin", "password": "admin"},
        "ignore": ["^/static/.*"],
    }
    DRAMATIQ_BROKER = None
    DRAMATIQ_BROKER_URL = None


config = {
    "dev": DevConfig,
    "prod": ProdConfig, # 目前未使用
    "stg": StgConfig,
    "test": TestingConfig,
    "local_dev_test": LocalDevTest, # 目前未使用
    "lite": LiteConfig,
}


def apply_runtime_overrides(app, config_name: str) -> None:
    if config_name != "lite":
        return

    lite_db_path = os.path.abspath(
        os.environ.get("LITE_DB_PATH", os.path.join(os.getcwd(), "snowball_lite.db"))
    )
    lite_db_uri = f"sqlite:///{lite_db_path}"

    app.config["LITE_DB_PATH"] = lite_db_path
    app.config["LITE_DB_URI"] = lite_db_uri
    app.config["SQLALCHEMY_DATABASE_URI"] = lite_db_uri
    app.config["SQLALCHEMY_BINDS"] = {
        "snowball": lite_db_uri,
    }
    app.config["XALPHA_CACHE_BACKEND"] = os.environ.get(
        "LITE_XALPHA_CACHE_BACKEND",
        app.config.get("XALPHA_CACHE_BACKEND", "csv"),
    ).lower()
    app.config["XALPHA_CACHE_DIR"] = os.path.abspath(
        os.environ.get(
            "LITE_XALPHA_CACHE_DIR",
            app.config.get(
                "XALPHA_CACHE_DIR",
                os.path.join(os.getcwd(), "data", "lite_xalpha_cache"),
            ),
        )
    )
    app.config["XALPHA_CACHE_SQLITE_PATH"] = os.environ.get(
        "LITE_XALPHA_CACHE_SQLITE_PATH"
    )
