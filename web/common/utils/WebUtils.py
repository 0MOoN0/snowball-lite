from __future__ import annotations

import datetime
import web.weblogger as logger

import pandas as pd
from babel.numbers import format_currency

from xalpha.cons import opendate_set


class WebUtils:
    @staticmethod
    def to_currency(amount) -> str:
        # locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
        # return locale.currency(amount, symbol=True, grouping=True)
        return format_currency(amount, 'CNY', locale='zh_CN', decimal_quantization=False)

    @staticmethod
    def get_previous_quarter(date: datetime.datetime):
        # date is a datetime object
        year = date.year
        month = date.month
        # use integer division and modulo to calculate the last quarter
        quarter = (month - 1) // 3
        if quarter == 0:
            # last quarter is Q4 of previous year
            year -= 1
            quarter = 4
        return year, quarter

    @staticmethod
    def is_trading_day(date: datetime.datetime) -> bool:
        """
        根据datetime判断该天是否为交易日， opendate_set为交易日
        Args:
            date (datetime.datetime): 要判断的日期

        Returns:
            bool: True为交易日，False为非交易日
        """
        return date.date().strftime('%Y-%m-%d') in opendate_set

    @staticmethod
    def get_last_trading_day(date: datetime.datetime) -> datetime:
        """
        根据datetime获取上一个交易日
        Args:
            date (datetime): 要判断的日期

        Returns:
            datetime: 上一个交易日
        """
        if WebUtils.is_trading_day(date):
            return date
        else:
            while not WebUtils.is_trading_day(date):
                date = date - datetime.timedelta(days=1)
            return date

    @staticmethod
    def is_A_sahres(name: str) -> bool:
        """
        方法内容：根据名称判断是否为A股
        方法实现：如果名称以ETF、ETF基金、B股、ETF港股、B结尾，返回False，否则返回True
        Args:
            name (str): 证券名称

        Returns:
            bool: True为A股，False为非A股
        """
        name = name.upper()
        return not (name.endswith('ETF') or name.endswith('ETF基金') or \
                    name.endswith('B股') or name.endswith('ETF港股') or name.endswith('B'))

    @staticmethod
    def to_date(date) -> datetime:
        """
        方法内容：根据输入数据类型，返回datetime类型的日期
        Args:
            date (date like):   str类型的日期，格式为'%Y-%m-%d'，或者datetime类型的日期

        Returns:

        """
        if isinstance(date, str):
            return datetime.strptime(date, '%Y-%m-%d')
        elif isinstance(date, datetime.datetime):
            return date
        else:
            logger.error(f'date should be a str or datetime object, but got {type(date)}')
            raise TypeError('date should be a str or datetime object')

    @staticmethod
    def underscore_to_camelcase(word: str) -> str:
        # 这是一个简单的函数，用于将下划线转换为驼峰
        return ''.join(x.capitalize() or '_' for x in word.split('_'))

    @staticmethod
    def convert_date(date: str | datetime.date | datetime.datetime | None) -> pd.Timestamp | None:
        """
        将日期或符合日期格式的数据转换成pandas的timestamp类型
        Args:
            date:

        Returns:

        """
        if None is date:
            return date
        elif isinstance(date, str) or isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
            return pd.to_datetime(date)
        else:
            raise TypeError('date should be a str or datetime object')


web_utils = WebUtils
webutils = WebUtils
web_util = WebUtils
utils = WebUtils
