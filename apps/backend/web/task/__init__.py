from dramatiq import Worker
import time
import redis

from web.common.cons import webcons
from web.task.Base import dramatiq
from web.weblogger import info, error


def init_app(app):
    """
    初始化RQ异步任务队列，并启动通知队列和普通队列的Worker。

    Args:
        app (Flask): Flask应用实例。

    Returns:
        无返回值。

    Raises:
        redis.ConnectionError: 当无法连接到Redis服务器时抛出
    """
    info("### 加载task模块")
    
    # 首先检查Redis连接是否可用
    try:
        # 从配置中获取Redis连接信息
        redis_host = app.config['REDIS_CLIENT']['REDIS_HOST']
        redis_port = app.config['REDIS_CLIENT']['REDIS_PORT']
        redis_db = app.config['REDIS_CLIENT']['REDIS_DB']
        redis_password = app.config['REDIS_CLIENT']['REDIS_PASSWORD']
        
        # 尝试建立连接
        client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            db=redis_db,
            password=redis_password,
            socket_timeout=5,
            socket_connect_timeout=3,
            health_check_interval=30,
            retry_on_timeout=True
        )
        
        # 测试连接
        client.ping()
        info(f"Redis连接检查成功: {redis_host}:{redis_port}/{redis_db}")
        client.close()
    except redis.ConnectionError as e:
        error(f"Redis连接检查失败: {e}")
        # 向上抛出异常，让应用层决定如何处理
        raise redis.ConnectionError(f"无法连接到Redis服务器: {e}")
    except Exception as e:
        error(f"Redis连接检查中发生未知错误: {e}", exc_info=True)
        # 向上抛出异常，让应用层决定如何处理
        raise
        
    # 初始化Dramatiq
    dramatiq.init_app(app)

    # 设置 Redis Broker 的重连参数
    try:
        if hasattr(dramatiq.broker, "_client"):
            # 为 Redis 客户端设置重试策略
            dramatiq.broker._client.connection_pool.connection_kwargs.update(
                {
                    "socket_timeout": 5,  # 套接字超时时间
                    "socket_connect_timeout": 5,  # 连接超时时间
                    "retry_on_timeout": True,  # 超时时自动重试
                    "health_check_interval": 30,  # 每30秒检查连接健康状态
                }
            )
            info("Redis Broker参数配置成功")
    except Exception as e:
        error(f"配置Redis Broker参数失败: {str(e)}")

    # 启动带重试机制的Worker
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        try:
            info(f"尝试启动Dramatiq Worker (尝试 {attempt + 1}/{max_attempts})")

            # 内存优化：使用单个 Worker 处理多个队列，减少内存占用
            combined_worker = Worker(
                broker=dramatiq.broker,
                worker_threads=1,  # 限制线程数
                queues=[
                    webcons.QueueNames.notification_queue,
                    webcons.QueueNames.normal_queue,
                ],
            )
            combined_worker.start()
            info("Dramatiq Worker 启动成功")
            break
        except (redis.ConnectionError, redis.TimeoutError) as e:
            attempt += 1
            error(f"Worker 启动失败 (尝试 {attempt}/{max_attempts}): {str(e)}")
            if attempt < max_attempts:
                time.sleep(2)  # 等待2秒再重试
            else:
                error("在多次尝试后，Worker 启动失败")
                # 在最后一次尝试失败后将异常向上抛出
                raise redis.ConnectionError(f"无法启动Dramatiq Worker，Redis连接失败: {e}")
        except Exception as e:
            error(f"Worker 启动失败，未知错误: {str(e)}")
            # 将异常向上抛出
            raise

    info("task模块加载完毕 ###")
