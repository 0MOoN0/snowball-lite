from gevent import monkey

monkey.patch_all()

import os
import sys

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, app_root)

from web.common.utils.gunicorn_log_util import get_gunicorn_logger_config
from web.common.utils.timezone_util import set_timezone


workers = 1
worker_class = "gevent"
bind = f"0.0.0.0:{os.environ.get('LITE_FLASK_PORT', '5002')}"
raw_env = ["SNOW_APP_STATUS=lite"]

max_requests_jitter = 50
timeout = 300
keepalive = 2
daemon = False

log_dir = os.path.join(app_root, "weblogs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

loglevel = "warning"
capture_output = True
logconfig_dict = get_gunicorn_logger_config(log_dir)
preload_app = False

set_timezone("Asia/Shanghai")


def on_starting(server):
    pass


def worker_exit(server, worker):
    import logging

    logging.shutdown()
