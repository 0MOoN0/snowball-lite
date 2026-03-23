from os import environ

from web import create_app
from web.common.utils.timezone_util import set_timezone
from web.lite_bootstrap import bootstrap_lite_database
from web.weblogger import info


def _safe_print(message: str) -> None:
    try:
        print(message)
    except OSError:
        # Gunicorn worker under detached/devtools launch may not have a writable stdout.
        pass


set_timezone("Asia/Shanghai")
environ["SNOW_APP_STATUS"] = "lite"

_safe_print("应用启动环境: lite")
info("应用启动环境: lite")
info("日志时区: Asia/Shanghai")
info("应用日志保留天数: 30")
info("Gunicorn 日志已整合到应用日志系统")

app = create_app("lite")

with app.app_context():
    bootstrap_lite_database(app)
    from web.databox import databox as lite_databox

    lite_databox.init_app(app)

_safe_print(f"配置类型: {app.config.get('ENV', '未知')}")
info(f"配置类型: {app.config.get('ENV', '未知')}")
_safe_print(f"Lite SQLite 路径: {app.config['LITE_DB_PATH']}")
info(f"Lite SQLite 路径: {app.config['LITE_DB_PATH']}")


if __name__ == "__main__":
    port = int(environ.get("LITE_FLASK_PORT", environ.get("FLASK_RUN_PORT", "5001")))

    _safe_print(f"Flask应用端口: {port}")
    info(f"Flask应用端口: {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
