from flask_dramatiq import Dramatiq
import dramatiq
from dramatiq.middleware import Retries, CurrentMessage

# 配置中间件
retries_middleware = Retries(
    max_retries=3,  # 最大重试次数
    min_backoff=1000,  # 最小重试间隔（毫秒）
    max_backoff=30000,  # 最大重试间隔（毫秒）
    retry_when=lambda retries, exc: True,  # 任何异常都重试
)

# 创建 Dramatiq 实例时添加重试中间件和当前消息中间件
dramatiq = Dramatiq(
    middleware=[
        retries_middleware,
        CurrentMessage(),  # 增加当前消息中间件，方便访问消息状态
    ]
)
