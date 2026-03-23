import os
import platform
import sys

IS_DARWIN = platform.system() == "Darwin"

if IS_DARWIN:
    os.environ.setdefault("OBJC_DISABLE_INITIALIZE_FORK_SAFETY", "YES")

if not IS_DARWIN:
    from gevent import monkey

    monkey.patch_all()

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, app_root)

from web.common.utils.timezone_util import set_timezone

if not IS_DARWIN:
    from web.common.utils.gunicorn_log_util import get_gunicorn_logger_config


workers = 1
worker_class = "sync" if IS_DARWIN else "gevent"
bind = f"0.0.0.0:{os.environ.get('LITE_FLASK_PORT', '5002')}"
raw_env = ["SNOW_APP_STATUS=lite"]

if IS_DARWIN:
    raw_env.append("OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES")

max_requests_jitter = 50
timeout = 300
keepalive = 2
daemon = False

log_dir = os.path.join(app_root, "weblogs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

loglevel = "warning"
capture_output = True
if IS_DARWIN:
    accesslog = "-"
    errorlog = "-"
else:
    logconfig_dict = get_gunicorn_logger_config(log_dir)
preload_app = False

set_timezone("Asia/Shanghai")


def on_starting(server):
    pass


def worker_exit(server, worker):
    import logging

    logging.shutdown()
