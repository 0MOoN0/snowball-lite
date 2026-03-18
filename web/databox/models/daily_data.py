# -*- coding: UTF-8 -*-
"""
@File    ：daily_data.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/11/15 20:13
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class DataBoxDailyData:
    date: str = None
    open: Decimal = 0
    close: Decimal = 0
    high: Decimal = 0
    low: Decimal = 0
    volume: Decimal = 0
    percent: Decimal = 0