from flask import request
from werkzeug.exceptions import BadRequest

from web.common.utils import R
from web.web_exception.WebException import WebBaseException


def init_app(app):
    """
    初始化Flask应用并注册错误处理函数。

    Args:
        app (Flask): Flask应用实例。

    Returns:
        None

    """
    @app.errorhandler(404)
    def database_not_found_error_handler(e):
        app.logger.error(f"404 error: URL {request.url}", exc_info=True)
        return R.fail(code=e.code, msg='Page not found')

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        """处理HTTP 400 Bad Request错误，特别是来自flask-restx的验证错误。"""
        error_message = e.description or "请求无效"
        # 检查是否有flask-restx提供的更详细的错误信息
        if hasattr(e, 'data') and isinstance(e.data, dict):
            messages = []
            if 'message' in e.data:
                messages.append(e.data['message'])
            if 'errors' in e.data and isinstance(e.data['errors'], dict):
                for field, error in e.data['errors'].items():
                    messages.append(f"{field}: {error}")
            if messages:
                error_message = "; ".join(messages)

        app.logger.error(f"Bad Request: {error_message}", exc_info=True)
        return R.fail(msg=error_message)

    @app.errorhandler(500)
    def internal_server_error_handler(e):
        app.logger.error(f"500 error: URL {request.url}", exc_info=True)
        return R.fail(code=e.code, msg='Internal server error')

    @app.errorhandler(WebBaseException)
    def handle_web_exception(e):
        app.logger.error(f"Web error: {e.message}", exc_info=True)
        # 打印异常堆栈信息
        return R.fail(code=e.code, msg=e.message)

    @app.errorhandler(Exception)
    def default_error_handler(e):
        message = f'Unhandled exception: {str(e)}'
        app.logger.error(message, exc_info=True)
        return R.fail(code=20001, msg=message)