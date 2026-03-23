class WebBaseException(Exception):
    code = 20001
    message = '服务器异常'
    name = 'web基础异常'

    def __init__(self, code=None, msg=None):
        if code:
            self.code = code
        if msg:
            self.message = msg
        super(WebBaseException, self).__init__(self.message)

    def __str__(self):
        return self.message


class WebDataException(WebBaseException):
    """
    数据异常，一般用于远程获取数据时发生的异常
    """
    code = 20002
    message = '获取数据异常'
    name = 'WebDataException'

    def __init__(self, code=None, msg=None):
        if code:
            self.code = code
        if msg:
            self.message = msg
        super(WebDataException, self).__init__(code=code, msg=msg)


class WebTaskException(WebBaseException):
    code = 20003
    message = 'Web端任务异常'
    name = 'Web端任务异常'

    def __init__(self, code=None, msg=None):
        if code:
            self.code = code
        if msg:
            self.message = msg
        super(WebTaskException, self).__init__(code=code, msg=msg)


class WebAnalyzerException(WebBaseException):
    code = 20004
    message = '交易分析异常'
    name = '交易分析异常'

    def __init__(self, code=None, msg=None):
        if code:
            self.code = code
        if msg:
            self.message = msg
        super(WebAnalyzerException, self).__init__(code=code, msg=msg)


class NotificationRenderException(WebBaseException):
    code = 20005
    message = '通知渲染异常'
    name = '通知渲染异常'

    def __init__(self, code=None, msg=None):
        if code:
            self.code = code
        if msg:
            self.message = msg
        super(NotificationRenderException, self).__init__(code=code, msg=msg)
