# -*- coding: UTF-8 -*-
"""
@File    ：fund.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/11/15 15:41
"""
from dataclasses import dataclass
from numbers import Number

from pandas import DataFrame


@dataclass
class DataBoxFundInfo:
    price: DataFrame
    rate: Number
    fee_info: dict
