import logging
import os
import sys
import errno # 确保导入 errno
from logging.handlers import TimedRotatingFileHandler

from flask.logging import default_handler
from web.common.utils.timezone_util import format_current_month, format_current_date

logger = logging.getLogger("web")
# 定义日志相关的变量
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error

# ANSI颜色代码常量
class Colors:
    """ANSI颜色转义码"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 高亮前景色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class LoggerInitialize:
    def init_logger(self, app, logging_level=logging.DEBUG):  # 设置默认日志级别为DEBUG
        log_path = app.root_path + "logs/"
        xa_logger = logging.getLogger("xalpha")

        # 设置logger不向上传播日志
        logger.propagate = False
        xa_logger.propagate = False

        # 创建月份文件夹的日志处理器
        # 设置日志保留30天
        file_handler_debug = MyTimedRotatingFileHandler(
            log_path + "debug/",
            level="debug",
            when="midnight",
            interval=1,
            backupCount_user_intent=30,
        )  # 保留30天日志
        file_handler_debug.setLevel(logging.DEBUG)

        # 输出错误日志
        file_handler_error = MyTimedRotatingFileHandler(
            log_path + "error/",
            level="error",
            when="midnight",
            interval=1,
            backupCount_user_intent=30,
        )  # 保留30天日志
        file_handler_error.setLevel(logging.ERROR)

        # 控制台输出的handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging_level)

        # 为不同级别的日志定义不同的格式 - 用于文件日志（无颜色）
        class ColorlessFormatter(logging.Formatter):
            """定义不同级别日志的格式但不使用emoji和颜色代码，确保兼容性"""
            formats = {
                logging.DEBUG: "[%(asctime)s] [DEBUG] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
                logging.INFO: "[%(asctime)s] [INFO] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
                logging.WARNING: "[%(asctime)s] [WARNING] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
                logging.ERROR: "[%(asctime)s] [ERROR] [%(name)s] [%(filename)s:%(lineno)d] [%(funcName)s] - %(message)s",
                logging.CRITICAL: "[%(asctime)s] [CRITICAL] [%(name)s] [%(filename)s:%(lineno)d] [%(funcName)s] - %(message)s"
            }

            def format(self, record):
                log_fmt = self.formats.get(record.levelno)
                formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
                return formatter.format(record)
        
        # 为控制台日志创建彩色格式化器
        class ColoredFormatter(logging.Formatter):
            """为控制台日志添加ANSI颜色"""
            
            # 根据日志级别定义不同的颜色和格式
            formats = {
                logging.DEBUG: Colors.BRIGHT_BLACK + "[%(asctime)s] " + Colors.CYAN + "[DEBUG] " + 
                              Colors.BRIGHT_BLACK + "[%(name)s] " + Colors.CYAN + "[%(filename)s:%(lineno)d] " +
                              Colors.RESET + "- %(message)s",
                
                logging.INFO: Colors.BRIGHT_BLACK + "[%(asctime)s] " + Colors.GREEN + "[INFO] " + 
                             Colors.BRIGHT_BLACK + "[%(name)s] " + Colors.GREEN + "[%(filename)s:%(lineno)d] " +
                             Colors.RESET + "- %(message)s",
                
                logging.WARNING: Colors.BRIGHT_BLACK + "[%(asctime)s] " + Colors.YELLOW + "[WARNING] " + 
                                Colors.BRIGHT_BLACK + "[%(name)s] " + Colors.YELLOW + "[%(filename)s:%(lineno)d] " +
                                Colors.RESET + "- %(message)s",
                
                logging.ERROR: Colors.BRIGHT_BLACK + "[%(asctime)s] " + Colors.RED + "[ERROR] " + 
                              Colors.BRIGHT_BLACK + "[%(name)s] " + Colors.RED + "[%(filename)s:%(lineno)d] " +
                              Colors.RED + "[%(funcName)s] " + Colors.RESET + "- %(message)s",
                
                logging.CRITICAL: Colors.BRIGHT_BLACK + "[%(asctime)s] " + Colors.BOLD + Colors.RED + 
                                 "[CRITICAL] " + Colors.BRIGHT_BLACK + "[%(name)s] " + 
                                 Colors.BOLD + Colors.RED + "[%(filename)s:%(lineno)d] [%(funcName)s] " + 
                                 Colors.RESET + "- %(message)s",
            }
            
            def format(self, record):
                # 判断输出是否支持颜色
                is_tty = hasattr(sys.stderr, 'isatty') and sys.stderr.isatty()
                
                # 如果不支持颜色（比如重定向到文件），使用无颜色格式
                if not is_tty:
                    log_fmt = ColorlessFormatter.formats.get(record.levelno)
                else:
                    log_fmt = self.formats.get(record.levelno)
                
                formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
                return formatter.format(record)

        # 使用定制的格式化器
        file_formatter = ColorlessFormatter()
        console_formatter = ColoredFormatter()

        # 将Formatter对象添加到handlers
        file_handler_debug.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        file_handler_error.setFormatter(file_formatter)

        # 设置flask的handler
        app.logger.setLevel(logging_level)
        app.logger.addHandler(console_handler)
        app.logger.addHandler(file_handler_debug)  # 恢复debug日志记录
        app.logger.addHandler(file_handler_error)
        app.logger.removeHandler(default_handler)
        app.logger.propagate = False

        # 清除xa_logger现有的handlers，避免重复添加
        for handler in xa_logger.handlers[:]:
            xa_logger.removeHandler(handler)

        # 设置xa_logger的level
        xa_logger.setLevel(logging_level)
        xa_logger.addHandler(console_handler)
        xa_logger.addHandler(file_handler_debug)  # 恢复debug日志记录
        xa_logger.addHandler(file_handler_error)

        # 设置web logger
        logger.setLevel(logging_level)
        # 清除现有的handlers，避免重复添加
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler_debug)  # 恢复debug日志记录
        logger.addHandler(file_handler_error)

        # 配置APScheduler相关的logger
        apscheduler_loggers = [
            'apscheduler',
            'apscheduler.scheduler',
            'apscheduler.executors',
            'apscheduler.jobstores',
            'apscheduler.executors.default'
        ]
        
        # 从配置中获取APScheduler的日志级别
        scheduler_log_level_str = app.config.get("SCHEDULER_LOG_LEVEL", "INFO")
        apscheduler_log_level = getattr(logging, scheduler_log_level_str.upper(), logging.INFO)
        
        for logger_name in apscheduler_loggers:
            apscheduler_logger = logging.getLogger(logger_name)
            apscheduler_logger.setLevel(apscheduler_log_level)  # 根据配置设置APScheduler日志级别
            apscheduler_logger.propagate = False
            
            # 清除现有的handlers，避免重复添加
            for handler in apscheduler_logger.handlers[:]:
                apscheduler_logger.removeHandler(handler)
            
            # 添加相同的handlers
            apscheduler_logger.addHandler(console_handler)
            apscheduler_logger.addHandler(file_handler_debug)
            apscheduler_logger.addHandler(file_handler_error)

        # 生产环境中禁用DEBUG日志只在PROD环境中启用
        if app.config.get("ENV") == "production":
            app.logger.debug = lambda *args, **kwargs: None
            logger.debug = lambda *args, **kwargs: None
            xa_logger.debug = lambda *args, **kwargs: None
            # 在生产环境中也禁用APScheduler的DEBUG日志（如果配置为DEBUG级别）
            if scheduler_log_level_str.upper() == "DEBUG":
                for logger_name in apscheduler_loggers:
                    apscheduler_logger = logging.getLogger(logger_name)
                    apscheduler_logger.debug = lambda *args, **kwargs: None


# 定义一个继承自TimedRotatingFileHandler的子类
class MyTimedRotatingFileHandler(TimedRotatingFileHandler):
    # 重写__init__()方法
    def __init__(
        self,
        filename_base_dir, # 例如: "logs/debug/"
        level,
        when="midnight",
        interval=1,
        backupCount_user_intent=0, # 用户期望的保留天数，但不由本handler直接处理删除
        encoding=None,
        delay=False,
        utc=False,
    ):
        self.base_dir = filename_base_dir  # 例如 "logs/debug/"
        self.my_level = level # 例如 "debug"
        self.user_backup_count_intent = backupCount_user_intent # 保存用户意图

        # 计算初始的完整日志文件路径
        current_time_str = format_current_date() # "YYYY-MM-DD"
        current_month_str = format_current_month() # "YYYY-MM"

        month_dir = os.path.join(self.base_dir, current_month_str)
        if not os.path.exists(month_dir):
            try:
                os.makedirs(month_dir)
            except OSError as e:
                if e.errno != errno.EEXIST: # 如果不是"目录已存在"的错误，则抛出
                    raise
        
        initial_full_path = os.path.join(month_dir, f"{current_time_str}-{self.my_level}.log")

        # 调用父类的__init__()方法，使用计算好的初始文件路径
        # 将 backupCount 传给父类时设为0，因为我们不使用父类的备份机制
        super().__init__(
            initial_full_path, when, interval, 0, encoding, delay, utc
        )

    # 重写doRollover()方法
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None # 明确流已关闭

        # 计算新一天的日期和月份，用于新文件名和路径
        current_time_for_new_file = format_current_date() # "YYYY-MM-DD"
        current_month_for_new_file = format_current_month() # "YYYY-MM"

        month_dir = os.path.join(self.base_dir, current_month_for_new_file)
        if not os.path.exists(month_dir):
            try:
                os.makedirs(month_dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        new_base_filename = os.path.join(month_dir, f"{current_time_for_new_file}-{self.my_level}.log")
        
        # 更新 baseFilename，TimedRotatingFileHandler 的 _open() 会使用它
        self.baseFilename = new_base_filename 

        # 打开新的日志文件流
        if not self.delay:
            self.stream = self._open()
        
        # 注意：我们不调用 super().doRollover()，因为它的备份和重命名逻辑
        # 与我们"每天新文件"的策略不兼容。旧文件的清理需要外部机制。

logger_initialize = LoggerInitialize()
