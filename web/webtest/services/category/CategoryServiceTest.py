import unittest
from pprint import pprint

from web.services import categoryService
from web.webtest.BasicRouterTestClass import BasicRouterTestClass


class CategoryServiceTest(BasicRouterTestClass):
    def test_getCategory(self):
        result_list = categoryService.get_category_list()
        pprint(len(result_list))


if __name__ == '__main':
    unittest.main()
