# gunicorn.config.py
import os
import sys
import platform

IS_DARWIN = platform.system() == "Darwin"

if IS_DARWIN:
    os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")

if not IS_DARWIN:
    from gevent import monkey

    monkey.patch_all()  # 必须在导入其他可能被 patch 的库之前调用

# 添加项目根目录到 Python 路径
app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, app_root)

from web.common.utils.timezone_util import set_timezone

if not IS_DARWIN:
    from web.common.utils.gunicorn_log_util import get_gunicorn_logger_config

# 性能和内存优化设置
workers = 1  # 在内存有限的情况下使用单进程 (单核心服务器推荐为1)
#threads = 4  # gevent模式下此参数作用不大，可以移除或设为1
#worker_class = "sync"
worker_class = "sync" if IS_DARWIN else "gevent"  # Darwin 本地调试避免 gevent + requests/ssl 递归问题
bind = "0.0.0.0:5001"  # 绑定IP和端口

# 内存优化
# max_requests = 1000  # 处理1000个请求后重启worker，防止内存泄漏
max_requests_jitter = 50  # 添加随机抖动，避免所有worker同时重启
timeout = 300  # 减少超时时间
keepalive = 2  # 在关闭连接前，等待keepalive_seconds秒的keep-alive请求
#worker_tmp_dir = "/dev/shm"  # 使用内存文件系统存储临时文件 # 注释掉此行，macOS上可能导致问题
daemon = False  # 不使用守护进程，减少资源消耗

# 确保日志目录存在
log_dir = os.path.join(app_root, "weblogs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# 日志配置
loglevel = "warning"  # 日志级别
capture_output = True  # 捕获标准输出和标准错误
raw_env = []
if IS_DARWIN:
    accesslog = "-"
    errorlog = "-"
    raw_env.append("OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES")
else:
    logconfig_dict = get_gunicorn_logger_config(log_dir)  # 使用自定义日志配置

# 关闭预加载，减少内存占用
preload_app = False

# 设置时区为东八区
set_timezone("Asia/Shanghai")


# 工作进程启动与结束时的钩子
def on_starting(server):
    """服务启动时初始化日志配置"""
    pass


def worker_exit(server, worker):
    """工作进程退出时确保日志刷新"""
    import logging

    logging.shutdown()
