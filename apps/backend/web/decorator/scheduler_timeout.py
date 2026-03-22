import functools
from typing import Callable, Any
import gevent
from web.weblogger import error, info


def scheduler_timeout(
    seconds: float, error_message: str = "Scheduler task execution timed out"
) -> Callable:
    """
    一个装饰器，用于监控函数执行时间，如果超过指定秒数，则引发TimeoutError。
    使用gevent.spawn和join实现守护者模式，以兼容gevent的协作式调度。

    Args:
        seconds: 超时时间（秒），支持浮点数，必须大于0
        error_message: 超时时的错误信息

    Returns:
        装饰器函数

    Raises:
        ValueError: 当seconds参数无效时抛出
        TimeoutError: 当函数执行时间超过指定秒数时抛出

    注意：
        - 此装饰器仅对协作式代码有效，如果函数不让出控制权，可能无法超时
        - 被装饰的函数应该包含gevent协作点（如gevent.sleep、数据库操作等）
        - 超时后会强制杀死greenlet，可能导致资源未正确释放

    示例:
        @scheduler_timeout(30, "数据处理超时")
        def process_data():
            # 一些可能耗时的操作
            pass
    """
    # 参数验证
    if not isinstance(seconds, (int, float)) or seconds <= 0:
        raise ValueError(f"timeout seconds must be a positive number, got: {seconds}")

    if not isinstance(error_message, str):
        raise ValueError(f"error_message must be a string, got: {type(error_message)}")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            g = None
            try:
                info(f"Starting task {func.__module__}.{func.__name__} with timeout {seconds}s")
                g = gevent.spawn(func, *args, **kwargs)
                g.join(timeout=seconds)
                if not g.ready():
                    # 超时处理
                    g.kill()
                    # 输出完整参数信息以便排查问题
                    error(
                        f"Task {func.__module__}.{func.__name__} timed out after {seconds} seconds. "
                        f"Args: {args}, Kwargs: {kwargs}. Error: {error_message}",
                        exc_info=True,
                    )
                    raise TimeoutError(error_message)
                else:
                    info(f"Task {func.__module__}.{func.__name__} completed successfully within {seconds}s timeout")
                    result = g.value  # 获取函数的实际返回值
                return result
            except Exception as e:
                # 处理函数执行中的异常
                if g:
                    g.kill()
                if isinstance(e, TimeoutError):
                    raise  # 重新抛出超时异常
                else:
                    # 记录其他异常并重新抛出
                    error(
                        f"Exception in {func.__module__}.{func.__name__}: {str(e)}",
                        exc_info=True,
                    )
                    raise
            finally:
                # 确保清理greenlet资源
                if g and not g.ready():
                    try:
                        g.unlink()
                    except Exception as cleanup_error:
                        error(
                            f"Failed to unlink greenlet for {func.__name__}: {cleanup_error}",
                            exc_info=True,
                        )

        return wrapper

    return decorator
