import datetime

from web.common.utils.WebUtils import web_utils
from web.webtest.TestModelsClass import TestBasicModels


class UtilsTestBasicModels(TestBasicModels):

    def test_get_quarter(self):
        date1 = datetime.date(2022, 1, 15)  # Q1 of 2022
        print(web_utils.get_previous_quarter(date1))  # output: (2021, 4)

        date2 = datetime.date(2022, 6, 30)  # Q2 of 2022
        print(web_utils.get_previous_quarter(date2))  # output: (2022, 1)

        date3 = datetime.date(2022, 12, 31)  # Q4 of 2022
        print(web_utils.get_previous_quarter(date3))  # output: (2022, 3)
