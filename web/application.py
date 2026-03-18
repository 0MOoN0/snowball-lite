from os import environ
from web import create_app
from web.common.utils.timezone_util import set_timezone
from web.weblogger import info

# 设置时区为东八区
set_timezone("Asia/Shanghai")

# 获取当前应用环境
env = environ.get("SNOW_APP_STATUS", "dev")

# 打印当前使用的配置
config_name = env
print(f"应用启动环境: {config_name}")
info(f"应用启动环境: {config_name}")
info(f"日志时区: Asia/Shanghai")
info(f"应用日志保留天数: 30")
info(f"Gunicorn 日志已整合到应用日志系统")

# 创建应用
app = create_app(env)

# 打印配置类型
config_class = app.config.get("ENV", "未知")
print(f"配置类型: {config_class}")
info(f"配置类型: {config_class}")

if __name__ == "__main__":
    # 获取端口配置，如果配置中没有FLASK_PORT则使用默认值5001
    port = 5001  # 默认端口
    
    # 通过环境名称获取配置类
    from web.settings import config
    current_config = config.get(env)
    if current_config and hasattr(current_config, 'FLASK_PORT'):
        port = current_config.FLASK_PORT
    
    print(f"Flask应用端口: {port}")
    info(f"Flask应用端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
