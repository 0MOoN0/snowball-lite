"""
跨平台时区工具类
提供在不同操作系统上统一的时区处理方法
"""

import os
import time
import platform
import datetime
import pytz
from typing import Union


def set_timezone(timezone_str="Asia/Shanghai"):
    """
    设置系统时区，在不同平台上使用不同实现

    Args:
        timezone_str: 时区字符串，默认为'Asia/Shanghai'
    """
    # 设置环境变量
    os.environ["TZ"] = timezone_str

    # 在类Unix系统上使用tzset()
    if platform.system() != "Windows":
        time.tzset()


def get_current_time():
    """
    获取当前时间（含时区信息）

    Returns:
        datetime: 当前时间，带有时区信息
    """
    tz = pytz.timezone("Asia/Shanghai")
    return datetime.datetime.now(tz)


def format_datetime(dt=None, fmt="%Y-%m-%d %H:%M:%S"):
    """
    格式化日期时间

    Args:
        dt: 要格式化的日期时间，默认为当前时间
        fmt: 格式化字符串

    Returns:
        str: 格式化后的日期时间字符串
    """
    if dt is None:
        dt = get_current_time()
    return dt.strftime(fmt)


def format_date(dt=None, fmt="%Y-%m-%d"):
    """
    格式化日期

    Args:
        dt: 要格式化的日期时间，默认为当前时间
        fmt: 格式化字符串

    Returns:
        str: 格式化后的日期字符串
    """
    return format_datetime(dt, fmt)


def format_current_month():
    """
    获取当前月份字符串（YYYY-MM格式）

    Returns:
        str: 当前月份字符串
    """
    return format_date(fmt="%Y-%m")


def format_current_date():
    """
    获取当前日期字符串（YYYY-MM-DD格式）

    Returns:
        str: 当前日期字符串
    """
    return format_date()


def parse_to_date(value: Union[str, datetime.date, datetime.datetime, None], default: datetime.date) -> datetime.date:
    """
    将输入值解析为 `datetime.date`，解析失败或为None时返回默认值。

    Args:
        value: 支持 `YYYY-MM-DD` 字符串、`datetime.date`、`datetime.datetime` 或 `None`
        default: 解析失败时返回的默认日期

    Returns:
        date: 解析后的日期
    """
    if value is None:
        return default
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return default
    return default
