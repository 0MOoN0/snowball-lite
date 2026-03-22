"""
Gunicorn 日志工具类
提供 Gunicorn 日志轮转和自定义处理功能
"""

import os
from logging.handlers import TimedRotatingFileHandler
from web.common.utils.timezone_util import format_current_month, format_current_date


class GunicornMonthlyFileHandler(TimedRotatingFileHandler):
    """
    按月组织的日志处理器，与应用日志相同的结构
    logs/
        gunicorn/
            YYYY-MM/
                YYYY-MM-DD-access.log
                YYYY-MM-DD-error.log
    """

    def __init__(
        self,
        log_type,
        log_dir="weblogs",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    ):
        """
        初始化处理器

        Args:
            log_type: 日志类型，"access" 或 "error"
            log_dir: 日志根目录
            when: 轮转周期 ('S', 'M', 'H', 'D', 'W', 'midnight')
            interval: 轮转间隔
            backupCount: 保留文件数量
            encoding: 文件编码
        """
        self.log_type = log_type
        self.base_dir = log_dir
        self.gunicorn_dir = os.path.join(self.base_dir, "gunicorn")

        # 确保目录存在
        if not os.path.exists(self.gunicorn_dir):
            os.makedirs(self.gunicorn_dir, exist_ok=True)

        # 创建月份目录
        current_month = format_current_month()
        self.month_dir = os.path.join(self.gunicorn_dir, current_month)
        if not os.path.exists(self.month_dir):
            os.makedirs(self.month_dir, exist_ok=True)

        # 确定日志文件名
        current_date = format_current_date()
        filename = os.path.join(self.month_dir, f"{current_date}-{log_type}.log")

        # 初始化父类
        super().__init__(
            filename=filename,
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
            delay=False,
            utc=False,
        )

    def doRollover(self):
        """
        执行日志轮转，创建新的日志文件
        """
        # 关闭旧文件
        if self.stream:
            self.stream.close()
            self.stream = None

        # 创建月份目录
        current_month = format_current_month()
        self.month_dir = os.path.join(self.gunicorn_dir, current_month)
        if not os.path.exists(self.month_dir):
            os.makedirs(self.month_dir, exist_ok=True)

        # 创建新的日志文件
        current_date = format_current_date()
        self.baseFilename = os.path.join(
            self.month_dir, f"{current_date}-{self.log_type}.log"
        )

        # 调用父类方法完成轮转
        super(GunicornMonthlyFileHandler, self).doRollover()

        # 重新打开新文件
        if not self.delay:
            self.stream = self._open()


def get_gunicorn_logger_config(log_dir="weblogs"):
    """
    获取 Gunicorn 日志配置

    Args:
        log_dir: 日志根目录

    Returns:
        字典格式的日志配置
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %z",
            },
            "access": {
                "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %z",
            },
        },
        "handlers": {
            "console": {
                "level": "WARNING",
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
            "error_file": {
                "level": "WARNING",
                "class": "web.common.utils.gunicorn_log_util.GunicornMonthlyFileHandler",
                "formatter": "standard",
                "log_type": "error",
                "log_dir": log_dir,
                "when": "midnight",
                "interval": 1,
                "backupCount": 30,
            },
            "access_file": {
                "class": "web.common.utils.gunicorn_log_util.GunicornMonthlyFileHandler",
                "formatter": "access",
                "log_type": "access",
                "log_dir": log_dir,
                "when": "midnight",
                "interval": 1,
                "backupCount": 30,
            },
        },
        "loggers": {
            "gunicorn.error": {
                "handlers": ["console", "error_file"],
                "level": "WARNING",
                "propagate": True,
            },
            "gunicorn.access": {
                "handlers": ["console", "access_file"],
                "level": "INFO",
                "propagate": True,
            },
        },
    }
