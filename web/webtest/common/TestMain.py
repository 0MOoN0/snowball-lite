# -*- coding: UTF-8 -*-
"""
@File    ：TestMain.py
@IDE     ：PyCharm
@Author  ：Leon
@Date    ：2024/9/12 22:06
"""
import sys
import traceback
from test_base import TestBase
from web.common.cons.webcons import XAFundSummaryColumns
from web.common.enum.databox.databox_enum import CodeTypeEnum


class TestMain(TestBase):

    def test_main(self):
        print(CodeTypeEnum.XQ)
        print(CodeTypeEnum.XQ.value)

    def test_traceback(self):
        try:
            1 / 0
        except ZeroDivisionError as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(f"Exception Type: {exc_type}")
            print(f"Exception Value: {exc_value}")
            print("Traceback Info:")
            traceback.print_tb(exc_traceback)


