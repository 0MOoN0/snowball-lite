#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    ：__init__.py
@IDE     ：PyCharm
@Author  ：Assistant
@Date    ：2025-01-14
@Description: Actors模块初始化文件
导出所有的Dramatiq actors
"""

from .NotificationActors import send_notification
from .AssetActors import init_fund_asset

# 创建一个包装类来保持向后兼容性
class NotificationActors:
    """NotificationActors包装类，用于保持向后兼容性"""
    send_notification = send_notification

# 导出所有actors
__all__ = [
    'send_notification',
    'init_fund_asset',
    'NotificationActors',
]