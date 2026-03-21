import os
from contextlib import contextmanager
from threading import RLock

from flask import current_app, has_app_context

GridNoticeTitle = "触发网格：{}:{}，请确认是否成交"
GridNoticeMsg = "触发网格：{} : {} ，方向：{}，价格：{}， 份额:{}，"


class HttpStatus:
    """HTTP 错误代码"""

    DATA_ERROR = 20002
    """ 数据错误"""


class DataFormatStr:
    """项目datetime格式集"""

    Y_m_d_H_M_S = "%Y-%m-%d %H:%M:%S"
    """datetime年月日时分秒格式格式：2020-01-01 00:00:00"""

    Y_m_d = "%Y-%m-%d"
    """datetime年月日格式：2020-01-01"""

    FORMAT_2 = "%Y%m%d%H%M%S"
    """datetime年月日时分秒格式：20200101000000"""


TRAND_LOCK_TIME_OUT = 300
"""
交易分析锁持有时间，5分钟
"""

NOTIFICATION_QUEUE_NAME = "notification_queue"
NORMAL_QUEUE_NAME = "normal_queue"


class QueueNames:
    """队列名称"""

    notification_queue = NOTIFICATION_QUEUE_NAME
    normal_queue = NORMAL_QUEUE_NAME


class RedisKeyPrefix:
    DYNAMIC_JOB = "DYNAMIC_JOB:"
    """动态任务"""


class RedisKey:
    """redis key"""

    XQ_TOKEN = "XQ_TOKEN"
    """雪球token"""
    """Server酱 sendkey"""
    SERVERCHAN_SENDKEY = "SERVERCHAN_SENDKEY"


class DataBoxTokenKey:
    XQ_TOKEN = "XQ_TOKEN"


# scheduler
class SchedulerConstants:
    """
    定时任务常量
    """

    JOB_RESUBMIT_DELAY = 15 * 60
    """重新提交任务的延迟 单位：秒"""


# xalpha 相关常量
class XAFundSummaryColumns:
    """
    常量内容：
    "基金名称","基金代码","当日净值","单位成本","持有份额","基金现值","基金总申购",
    "历史最大占用","基金持有成本","基金分红与赎回","换手率","基金收益总额","投资收益率","内部收益率"
    """

    FUND_NAME = "基金名称"
    FUND_CODE = "基金代码"
    NET_VALUE = "当日净值"
    UNIT_COST = "单位成本"
    ATTRIBUTABLE_SHARE = "持有份额"
    PRESENT_VALUE = "基金现值"
    PURCHASE_AMOUNT = "基金总申购"
    MAXIMUM_OCCUPANCY = "历史最大占用"
    HOLDING_COST = "基金持有成本"
    DIVIDEND = "基金分红与赎回"
    TURNOVER_RATE = "换手率"
    PROFIT = "基金收益总额"
    INVESTMENT_YIELD = "投资收益率"
    ANNUALIZED_RETURN = "年化收益率"
    IRR = "内部收益率"

    @classmethod
    def get_dict(cls):
        # 获取常量对应的小写字符串字典
        return {
            str(value): str(key).lower()
            for key, value in XAFundSummaryColumns.__dict__.items()
            if not callable(value) and not key.startswith("__")
        }


class XAIRRDelayDate:
    """
    IRR计算延迟日期
    """

    DELAY_DATE = 30


class XaFundInfoSetting:
    DB_SETTING = {}


class XaCacheBackend:
    SQL = "sql"
    CSV = "csv"
    MEMORY = "memory"


class XaCacheConfig:
    DAILY_KEY_PREFIX = "xq_"
    FUNDINFO_PREFIX = "INFO-"
    DEFAULT_CACHE_DIR = os.path.join("data", "xalpha_cache")


_XALPHA_DAILY_BACKEND_LOCK = RLock()


def _ensure_cache_dir(path: str) -> str:
    abs_path = os.path.abspath(path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path


def _normalize_optional_path(path: str | None) -> str | None:
    if path is None:
        return None

    normalized = str(path).strip()
    if not normalized:
        return None

    return os.path.abspath(normalized)


def _get_sqlite_cache_engine(sqlite_path: str):
    from sqlalchemy import create_engine

    from web.models import configure_sqlite_engine

    abs_path = os.path.abspath(sqlite_path)
    parent = os.path.dirname(abs_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    cache_uri = f"sqlite:///{abs_path}"
    app = current_app._get_current_object() if has_app_context() else None
    if app is not None:
        cache_engines = app.extensions.setdefault("xalpha_cache_engines", {})
        engine = cache_engines.get(cache_uri)
        if engine is not None:
            return engine
    else:
        cache_engines = None

    engine = create_engine(
        cache_uri,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,
        },
    )
    configure_sqlite_engine(engine)
    if cache_engines is not None:
        cache_engines[cache_uri] = engine
    return engine


def resolve_xalpha_cache_settings(default_engine=None):
    backend_name = XaCacheBackend.SQL
    cache_dir = None
    cache_sqlite_path = None
    enable_xalpha_sql_cache = True
    lite_db_path = None
    is_lite = False

    if has_app_context():
        config = current_app.config
        backend_name = str(
            config.get("XALPHA_CACHE_BACKEND", backend_name)
        ).lower()
        cache_dir = config.get("XALPHA_CACHE_DIR")
        cache_sqlite_path = config.get("XALPHA_CACHE_SQLITE_PATH")
        enable_xalpha_sql_cache = bool(
            config.get("ENABLE_XALPHA_SQL_CACHE", True)
        )
        lite_db_path = config.get("LITE_DB_PATH")
        env_name = str(config.get("_config_name") or config.get("ENV") or "").lower()
        is_lite = env_name == "lite"

    # 兼容旧配置语义：关闭 SQL cache 时回退到内存缓存，但保留显式 CSV backend。
    if not enable_xalpha_sql_cache and backend_name == XaCacheBackend.SQL:
        if is_lite:
            raise ValueError(
                "lite 模式下 backend=sql 时必须启用 LITE_ENABLE_XALPHA_SQL_CACHE"
            )
        backend_name = XaCacheBackend.MEMORY

    if backend_name == XaCacheBackend.CSV:
        cache_dir = _ensure_cache_dir(cache_dir or XaCacheConfig.DEFAULT_CACHE_DIR)
        return {
            "backend_name": backend_name,
            "backend": {
                "backend": XaCacheBackend.CSV,
                "path": cache_dir,
            },
            "fundinfo": {
                "save": True,
                "fetch": True,
                "form": XaCacheBackend.CSV,
                "path": os.path.join(cache_dir, XaCacheConfig.FUNDINFO_PREFIX),
            },
        }

    if backend_name == XaCacheBackend.MEMORY:
        return {
            "backend_name": backend_name,
            "backend": {
                "backend": XaCacheBackend.MEMORY,
            },
            "fundinfo": {
                "save": False,
                "fetch": False,
            },
        }

    if backend_name != XaCacheBackend.SQL:
        raise ValueError(f"Unsupported xalpha cache backend: {backend_name}")

    cache_sqlite_path = _normalize_optional_path(cache_sqlite_path)
    lite_db_path = _normalize_optional_path(lite_db_path)

    if is_lite:
        if not cache_sqlite_path:
            raise ValueError(
                "lite 模式下 backend=sql 时必须提供 LITE_XALPHA_CACHE_SQLITE_PATH"
            )
        if lite_db_path and cache_sqlite_path == lite_db_path:
            raise ValueError(
                "LITE_XALPHA_CACHE_SQLITE_PATH 不能与 LITE_DB_PATH 指向同一个文件"
            )

        cache_engine = _get_sqlite_cache_engine(cache_sqlite_path)
    else:
        cache_engine = default_engine
        if cache_sqlite_path:
            cache_engine = _get_sqlite_cache_engine(cache_sqlite_path)

    return {
        "backend_name": backend_name,
        "backend": {
            "backend": XaCacheBackend.SQL,
            "path": cache_engine,
        },
        "fundinfo": {
            "save": True,
            "fetch": True,
            "form": XaCacheBackend.SQL,
            "path": cache_engine,
        },
    }


def _apply_xalpha_cache_settings_unlocked(xa_module, default_engine=None):
    cache_settings = resolve_xalpha_cache_settings(default_engine=default_engine)
    xa_module.set_backend(
        **cache_settings["backend"],
        key_func=lambda key: XaCacheConfig.DAILY_KEY_PREFIX + str(key).lower(),
    )
    XaFundInfoSetting.DB_SETTING = dict(cache_settings["fundinfo"])
    return cache_settings


def apply_xalpha_cache_settings(xa_module, default_engine=None):
    with _XALPHA_DAILY_BACKEND_LOCK:
        return _apply_xalpha_cache_settings_unlocked(
            xa_module,
            default_engine=default_engine,
        )


@contextmanager
def xalpha_daily_backend_scope(xa_module, default_engine=None):
    with _XALPHA_DAILY_BACKEND_LOCK:
        cache_settings = _apply_xalpha_cache_settings_unlocked(
            xa_module,
            default_engine=default_engine,
        )
        yield cache_settings


# 通知消息重试延迟，一小时，单位毫秒
NOTIFICATION_RETRY_DELAY = 1 * 60 * 1000

# 通知消息全局重试次数
NOTIFICATION_GLOBAL_MAX_RETRY = 9
