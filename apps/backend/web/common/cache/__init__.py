# -*- coding: UTF-8 -*-
"""
@File    ：__init__.py.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/10/8 19:36
"""

from web.common.cache.base import cache


def init_app(app):
    app.logger.debug('### 加载cache模块')
    cache.init_app(app)
    app.logger.debug('cache模块加载完毕 ###')
