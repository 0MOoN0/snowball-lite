# -*- coding: UTF-8 -*-
"""
@File    ：__init__.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2025/1/27 15:30
@Description: 指数路由模块初始化文件
"""

# 导入指数相关路由
from .index_list_routers import api_ns as index_list_ns

__all__ = ["index_list_ns"]