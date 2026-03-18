# -*- coding: UTF-8 -*-
"""
@File    ：xa_service_adapter_test.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/11/10 11:46
"""
from pprint import pprint

from test_base import TestBase
from web.databox.adapter.data.xa_service import XaService, XaServiceAdapter


class TestXaServiceAdapter(TestBase):

    def test_get_rt(self):
        """
        测试获取响应时间的功能。

        Args:
            无。

        Returns:
            无。

        Raises:
            无。
        """
        adapter: XaService = XaServiceAdapter()
        rt = adapter.get_rt('SZ162411')
        pprint(rt)

    def test_fundinfo(self):
        """
        测试获取基金信息的功能。

        Args:
            无。

        Returns:
            无。

        Raises:
            无。
        """
        adapter: XaService = XaServiceAdapter()
        fundinfo = adapter.fundinfo('162411')
        pprint(fundinfo)

    def test_get_daily(self):
        """
        测试获取每日数据的功能。

        Args:
            无。

        Returns:
            无。

        Raises:
            无。
        """
        adapter: XaService = XaServiceAdapter()
        daily = adapter.get_daily('SZ162411', '2023-01-01', '2023-01-31')
        pprint(daily)
